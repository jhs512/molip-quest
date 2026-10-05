use base64::{engine::general_purpose::STANDARD, Engine};
use dioxus::prelude::*;
use molip_quest::{learning_store::LearningStore, Course};
use ring::{aead, pbkdf2};
use serde::Deserialize;
use std::{collections::HashMap, num::NonZeroU32};

pub(crate) const COURSE_ID: &str = "kpc-morning-practice-v1";

#[derive(Clone, Deserialize)]
pub(crate) struct Material {
    code: String,
    explanation: Vec<String>,
    narration: Vec<serde_json::Value>,
}
pub(crate) type Materials = HashMap<String, Material>;

#[derive(Deserialize)]
struct Encrypted {
    iterations: u32,
    salt: String,
    iv: String,
    ciphertext: String,
}

pub(crate) fn decrypt(password: &str) -> Result<Materials, String> {
    let data: Encrypted = serde_json::from_str(include_str!("../site/data/instructor.json"))
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?;
    let salt = STANDARD
        .decode(data.salt)
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?;
    let iv: [u8; 12] = STANDARD
        .decode(data.iv)
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?
        .try_into()
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?;
    let mut ciphertext = STANDARD
        .decode(data.ciphertext)
        .map_err(|_| "강사용 자료를 읽지 못했습니다.")?;
    let mut key = [0u8; 32];
    pbkdf2::derive(
        pbkdf2::PBKDF2_HMAC_SHA256,
        NonZeroU32::new(data.iterations).ok_or("강사용 자료를 읽지 못했습니다.")?,
        &salt,
        password.as_bytes(),
        &mut key,
    );
    let key = aead::LessSafeKey::new(
        aead::UnboundKey::new(&aead::AES_256_GCM, &key)
            .map_err(|_| "강사용 자료를 읽지 못했습니다.")?,
    );
    let plaintext = key
        .open_in_place(
            aead::Nonce::assume_unique_for_key(iv),
            aead::Aad::empty(),
            &mut ciphertext,
        )
        .map_err(|_| "비밀번호가 맞지 않습니다. 다시 입력하세요.")?;
    serde_json::from_slice(plaintext).map_err(|_| "강사용 자료를 읽지 못했습니다.".into())
}

fn numbered_units(course: &Course) -> Vec<molip_quest::Unit> {
    course
        .chapters
        .iter()
        .enumerate()
        .flat_map(|(chapter, group)| {
            group.units.iter().enumerate().map(move |(ordinal, unit)| {
                let mut unit = unit.clone();
                let title = unit
                    .title
                    .split_once(". ")
                    .filter(|(prefix, _)| prefix.chars().all(|c| c.is_ascii_digit()))
                    .map(|(_, title)| title)
                    .unwrap_or(&unit.title);
                if !unit.title.starts_with("C-") {
                    unit.title = format!("C-{}-{} · {}", chapter + 1, ordinal + 1, title);
                }
                unit
            })
        })
        .collect()
}

#[component]
pub(crate) fn PracticeView() -> Element {
    let course = use_hook(|| Course::parse(include_str!("../courses/morning-practice.json")));
    let Ok(course) = course else {
        return rsx! {p {class:"error","실습을 불러올 수 없습니다."}};
    };
    let mut selected = use_signal(|| 0usize);
    let mut refresh = use_signal(|| 0u64);
    let materials = use_context::<crate::instructor_mode::InstructorSession>().0;
    let mut shown = use_signal(|| None::<bool>);
    let mut demo_round = use_signal(|| 0u64);
    let mut demo_running = use_signal(|| false);
    let mut demo_paused = use_signal(|| false);
    let mut demo_report = use_signal(String::new);
    let demo_units = numbered_units(&course);
    use_drop(|| {
        document::eval("window.molipAgent?.stop()");
    });
    use_effect(move || {
        let round = demo_round();
        if round == 0 {
            return;
        }
        let id = &demo_units[*selected.peek()].id;
        let Some(material) = materials.peek().as_ref().and_then(|m| m.get(id)).cloned() else {
            return;
        };
        let mut actions = material.narration;
        for action in &mut actions {
            if let Some(code) = action.get_mut("code") {
                if let Some(text) = code.as_str() {
                    *code = text
                        .replace("\"cafe-sales.xlsx\"", "\"data/cafe-sales.xlsx\"")
                        .into();
                }
            }
        }
        demo_running.set(true);
        demo_paused.set(false);
        demo_report.set(String::new());
        let actions = serde_json::to_string(&actions).unwrap_or_else(|_| "[]".into());
        spawn(async move {
            let script = format!("(async()=>{{const a=window.molipAgent;if(!a){{dioxus.send('해설 엔진을 불러오지 못했습니다.');return;}}const voice=a.voice,name=a.voiceName;a.setVoiceName('system');a.setVoice(true);try{{dioxus.send(await a.run({actions}));}}catch(e){{dioxus.send(String(e));}}finally{{a.setVoice(voice);a.setVoiceName(name);}}}})()");
            let mut eval = document::eval(&script);
            let report = eval
                .recv::<String>()
                .await
                .unwrap_or_else(|_| "해설 재생이 종료되었습니다.".into());
            if *demo_round.peek() == round {
                demo_running.set(false);
                demo_paused.set(false);
                demo_report.set(report);
            }
        });
    });
    let units = numbered_units(&course);
    let unit = units[selected()].clone();
    let _ = refresh();
    let completed = LearningStore::user_store()
        .and_then(|store| store.completed(&course))
        .unwrap_or_default();
    rsx! {
        header {class:"practice-header",h1 {"도전 과제"}
        nav {class:"header-course-actions",aria_label:"실습 문제",
            button {class:"curriculum-toggle",onclick:move |_|{document::eval(r#"const dialog = document.querySelector('.practice-list');
                if (!dialog.dataset.dismissBound) {dialog.addEventListener('click', event => {if(event.target === dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});dialog.dataset.dismissBound='true';}
                dialog.showModal();"#);},"도전 과제 목록"}
                    if materials().is_some() {
                button {class:"instructor-answer",onclick:move |_|{document::eval("window.molipAgent?.stop()");shown.set(Some(true));},"정답 보기"}
                button {class:"instructor-explain",disabled:demo_running(),onclick:move |_|{shown.set(Some(false));demo_round+=1;},"해설 보기"}
            }
        }
        span {class:"practice-current-title","{unit.title}"}
        }
        dialog {class:"curriculum-menu practice-list",aria_label:"도전 과제 목록",
            div {class:"curriculum-modal-header",h2 {"도전 과제 목록"}
                button {class:"curriculum-close",aria_label:"도전 과제 목록 닫기",autofocus:true,onclick:move |_|{document::eval("document.querySelector('.practice-list').close()");},"닫기 ×"}
            }
            div {class:"curriculum-gauge",role:"progressbar",aria_valuemin:"0",aria_valuemax:"100",aria_valuenow:format!("{}",completed.len()*100/units.len()),
                div {class:"curriculum-gauge-head",span {class:"curriculum-gauge-label","클리어"}span {class:"curriculum-gauge-percent",{format!("{}%",completed.len()*100/units.len())}}span {class:"curriculum-gauge-count",{format!("{} / {} 과제",completed.len(),units.len())}}}
                div {class:"curriculum-gauge-track",div {class:"curriculum-gauge-fill",style:format!("width:{}%",completed.len()*100/units.len())}}
            }
            nav {class:"curriculum",
                for chapter in &course.chapters {
                    details {class:"curriculum-chapter",open:chapter.units.iter().any(|problem|problem.id==unit.id),
                        summary {h3 {span {class:"curriculum-kind","📚 챕터"}{format!(" {} · {} / {} · {}%",chapter.title,chapter.units.iter().filter(|problem|completed.contains(&problem.id)).count(),chapter.units.len(),if chapter.units.is_empty(){0}else{chapter.units.iter().filter(|problem|completed.contains(&problem.id)).count()*100/chapter.units.len()})}}
                        }
                        for problem in &chapter.units {
                            {
                                let index=units.iter().position(|candidate|candidate.id==problem.id).unwrap();
                                let title=units[index].title.clone();
                                rsx! {
                                    div {class:"curriculum-unit",button {class:format!("unit{}{}",if selected()==index{" selected"}else{""},if completed.contains(&problem.id){" done"}else{""}),aria_current:if selected()==index {"step"}else{"false"},onclick:move |_|{document::eval("window.molipAgent?.stop();document.querySelector('.practice-list').close()");selected.set(index);shown.set(None);},
                                        span {class:"unit-title",{format!("{} {}",if completed.contains(&problem.id){"✓"}else if selected()==index{"▶"}else{"○"},title)}}
                                        if selected()==index {span {class:"unit-current","학습 중"}}
                                    }}
                                }
                            }
                        }
                    }
                }
            }
        }
        if materials().is_some() { if let Some(code_view) = shown() {
            if let Some(material)=materials().and_then(|m|m.get(&unit.id).cloned()) {
                section {class:"practice-instructor-result",h2 {{if code_view{"정답"}else{"해설"}}}
                    if code_view {pre {code {{material.code.replace("\"cafe-sales.xlsx\"", "\"data/cafe-sales.xlsx\"")}}}}
                    else {
                        p {"코드를 한 단계씩 작성하며 설명하고, 실행 결과와 제출까지 보여 드립니다."}
                        div {class:"actions",
                            button {disabled:!demo_running(),onclick:move |_|{if demo_paused(){document::eval("window.molipAgent?.resume()");}else{document::eval("window.molipAgent?.pause()");}demo_paused.set(!demo_paused());},{if demo_paused(){"계속"}else{"일시정지"}}}
                            button {id:"autopilot-stop",disabled:!demo_running(),onclick:move |_|{document::eval("window.molipAgent?.stop()");},"해설 멈춤"}
                            button {disabled:demo_running(),onclick:move |_|demo_round+=1,"다시 보기"}
                        }
                        if !demo_running() && !demo_report().is_empty() {p {role:"status","해설 재생이 종료되었습니다."}}
                        details {summary {"풀이 요약"}ol {for text in material.explanation {li {"{text}"}}}}
                    }
                    button {onclick:move |_|{document::eval("window.molipAgent?.stop()");shown.set(None);},"닫기"}
                }
            }
        }
        }
        div {class:"separate-practice-workspace", {rsx! {
            crate::ui::UnitWorkspace {key:"{unit.id}",course_id:COURSE_ID.to_string(),unit,
                oncompleted:move |passed|{if passed {refresh+=1;crate::ui::toast("정답입니다! 실습 완료를 저장했습니다.","success");}}
            }
        }}}
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn practice_is_separate_and_all_problems_have_tests() {
        let course = Course::parse(include_str!("../courses/morning-practice.json")).unwrap();
        assert_eq!(course.id, COURSE_ID);
        assert!(course.total_units() >= 3);
        let numbered = numbered_units(&course);
        assert_eq!(numbered.len(), course.total_units());
        assert!(numbered[0].title.starts_with("C-1-1"));
        assert_eq!(numbered[0].id, "sales");
        assert_eq!(numbered[1].id, "total");
        assert_eq!(numbered[2].id, "best");
        for unit in &course.chapters[0].units {
            assert_eq!(unit.tests.len(), 1);
            assert!(unit.starter_code.contains("data/cafe-sales.xlsx"));
        }
        assert!(decrypt("incorrect-password").is_err());
    }
    #[test]
    fn numbering_flattens_chapters_without_changing_progress_ids() {
        let mut course = Course::parse(include_str!("../courses/morning-practice.json")).unwrap();
        let mut second = course.chapters[0].clone();
        second.id = "second-numbering-test".into();
        for problem in &mut second.units {
            problem.id = format!("second-{}", problem.id);
        }
        let first_count = course.total_units();
        course.chapters.push(second);
        let numbered = numbered_units(&course);
        assert!(numbered[first_count]
            .title
            .starts_with(&format!("C-{}-1", course.chapters.len())));
        assert_eq!(numbered[first_count].id, "second-sales");
        assert_eq!(numbered[0].id, "sales");
    }
    #[tokio::test]
    #[ignore = "requires local instructor password file"]
    async fn private_instructor_material_and_bundled_excel_run() {
        let path = std::env::var("MOLIP_PRACTICE_TEST_PASSWORD_FILE").unwrap();
        let password = std::fs::read_to_string(path).unwrap();
        let materials = decrypt(password.trim()).unwrap();
        let course = Course::parse(include_str!("../courses/morning-practice.json")).unwrap();
        for unit in course.chapters.iter().flat_map(|chapter| &chapter.units) {
            let code = materials[&unit.id]
                .code
                .replace("\"cafe-sales.xlsx\"", "\"data/cafe-sales.xlsx\"");
            let assembled: String = materials[&unit.id]
                .narration
                .iter()
                .filter(|a| a["action"] == "type_code")
                .map(|a| a["code"].as_str().unwrap())
                .collect();
            assert_eq!(assembled, materials[&unit.id].code);
            let report = molip_quest::runner::check_unit(unit, &code).await.unwrap();
            assert!(
                report.passed,
                "{}: {:?}",
                unit.id,
                report.cases.iter().map(|c| &c.stderr).collect::<Vec<_>>()
            );
        }
    }
}
