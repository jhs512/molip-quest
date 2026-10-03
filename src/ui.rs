use dioxus::prelude::*;
use molip_quest::{
    curriculum::{Activity, ActivityKind, Question, QuestionKind},
    drafts,
    runner::{assemble, check_unit, run_python, Artifact},
    Course, Unit,
};
use std::collections::{HashMap, HashSet};

/// The Android build cannot spawn Python, so coding missions are read and acknowledged instead.
pub const VIEW_ONLY: bool = cfg!(target_os = "android");

#[cfg(not(target_os = "android"))]
fn copy_to_clipboard(text: String) -> Result<(), String> {
    arboard::Clipboard::new()
        .and_then(|mut clipboard| clipboard.set_text(text))
        .map_err(|e| e.to_string())
}
#[cfg(target_os = "android")]
fn copy_to_clipboard(_text: String) -> Result<(), String> {
    Err("Android 열람 모드에서는 클립보드 복사를 지원하지 않습니다.".into())
}

/// Every unit and mission can be opened at any time so students can look ahead; clearing
/// still requires passing the mission, and progress still decides where a unit resumes.
fn unlocked_units(course: &Course, _completed: &HashSet<String>) -> HashSet<String> {
    course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .map(|u| u.id.clone())
        .collect()
}
fn unlocked_activities(unit: &Unit, _completed: &HashSet<String>) -> usize {
    unit.activities.len()
}

/// Brief feedback that floats over the page (assets/layout/toast.js) instead of taking up layout.
fn toast(message: &str, kind: &str) {
    document::eval(&format!(
        "window.molipToast && molipToast({}, {})",
        serde_json::to_string(message).expect("toast text"),
        serde_json::to_string(kind).expect("toast kind")
    ));
}

fn mission_progress<'a>(
    units: impl Iterator<Item = &'a Unit>,
    completed: &HashSet<String>,
) -> String {
    let mut total = 0;
    let mut done = 0;
    for unit in units {
        for activity in &unit.activities {
            total += 1;
            done += usize::from(completed.contains(&activity.progress_unit(unit).id));
        }
    }
    let percent = if total == 0 { 0 } else { done * 100 / total };
    format!("{done} / {total} 미션 · {percent}%")
}

#[component]
pub fn Learning(course: Course) -> Element {
    let mut selected = use_signal(String::new);
    let mut mission_index = use_signal(|| usize::MAX);
    let mut clear_popup = use_signal(|| false);
    let mut refresh = use_signal(|| 0u64);
    // Bumped on reset so the mounted mission re-reads drafts and quiz state from scratch.
    let mut epoch = use_signal(|| 0u64);
    let progress_course = course.clone();
    let completed = use_memo(move || {
        let _ = refresh();
        let store = molip_quest::learning_store::LearningStore::user_store()?;
        Ok::<_, String>((
            store.completed(&progress_course)?,
            store.completed_items(&progress_course)?,
        ))
    });
    let (completed, completed_items) = match completed() {
        Ok(completed) => completed,
        Err(error) => return rsx! {p {class:"error", "{error}"}},
    };
    let unlocked = unlocked_units(&course, &completed);
    let active = course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .find(|u| u.id == selected() && unlocked.contains(&u.id))
        .or_else(|| {
            course
                .chapters
                .iter()
                .flat_map(|c| &c.units)
                .find(|u| unlocked.contains(&u.id) && !completed.contains(&u.id))
        })
        .unwrap_or(&course.chapters[0].units[0])
        .clone();
    let units: Vec<_> = course.chapters.iter().flat_map(|c| &c.units).collect();
    let position = units.iter().position(|u| u.id == active.id).unwrap();
    let previous = position.checked_sub(1).map(|i| units[i].id.clone());
    let next = units
        .get(position + 1)
        .filter(|u| unlocked.contains(&u.id))
        .map(|u| u.id.clone());
    let active_id = active.id.clone();
    let following_id = units.get(position + 1).map(|u| u.id.clone());
    let active_unlocked = unlocked_activities(&active, &completed_items);
    let active_total = active.activities.len();
    // A unit resumes at its first mission that is not cleared yet.
    let active_mission = if mission_index() == usize::MAX {
        molip_quest::curriculum::unlocked_activities(&active, &completed_items)
            .saturating_sub(1)
            .min(active_unlocked.saturating_sub(1))
    } else {
        mission_index().min(active_unlocked.saturating_sub(1))
    };
    let can_prev = !(active_mission == 0 && previous.is_none());
    let can_next = !(active_mission + 1 >= active_unlocked
        && !(active_mission + 1 == active_total && next.is_some()));
    // Shared by the header buttons and the buttons at the bottom of concept and quiz missions.
    let navigate = Callback::new(move |delta: i32| {
        if delta < 0 {
            if active_mission > 0 {
                mission_index.set(active_mission - 1);
            } else if let Some(id) = &previous {
                mission_index.set(usize::MAX);
                selected.set(id.clone());
            }
        } else if active_mission + 1 < active_unlocked {
            mission_index.set(active_mission + 1);
        } else if let Some(id) = &next {
            mission_index.set(usize::MAX);
            selected.set(id.clone());
        }
    });
    rsx! {header {class:"practice-header", h1 {"{course.title}"}
        div {class:"header-navigation",aria_label:"학습 이동",
            button {disabled:!can_prev,onclick:move |_|navigate.call(-1),"← 이전"}
            button {disabled:!can_next,onclick:move |_|navigate.call(1),"다음 →"}
        }
        span {{format!("완료 {} / {} 단원",completed.len(),course.total_units())}}
        ResetProgress {course_id:course.id.clone(),onreset:move |_|{selected.set(String::new());mission_index.set(usize::MAX);clear_popup.set(false);refresh+=1;epoch+=1;}}}
        div {class:"learning",
        button {class:"curriculum-toggle",onclick:move |_|{document::eval(r#"const dialog = document.querySelector('.curriculum-menu');
            if (!dialog.dataset.dismissBound) {
                dialog.addEventListener('click', event => { if (event.target === dialog) {
                    const rect = dialog.getBoundingClientRect();
                    if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
                }});
                dialog.dataset.dismissBound = 'true';
            }
            dialog.showModal();"#);},"수업 목차"}
        dialog {class:"curriculum-menu",aria_label:"수업 목차",
            div {class:"curriculum-modal-header",h2 {"수업 목차"}
                button {class:"curriculum-close",aria_label:"수업 목차 닫기",autofocus:true,onclick:move |_|{document::eval("document.querySelector('.curriculum-menu').close();");},"닫기 ×"}
            }
            p {class:"curriculum-overall",{format!("전체 진도 {}",mission_progress(course.chapters.iter().flat_map(|c|c.units.iter()),&completed_items))}}
            nav {class:"curriculum",
            for chapter in &course.chapters {h3 {{format!("{} · {}",chapter.title,mission_progress(chapter.units.iter(),&completed_items))}}
                for unit in &chapter.units {div {class:"curriculum-unit",button {class:if unit.id==active_id {"unit selected"}else{"unit"},aria_current:if unit.id==active_id {"step"}else{"false"},disabled:!unlocked.contains(&unit.id),onclick:{let id=unit.id.clone();let active_id=active_id.clone();move |_|{if id!=active_id {mission_index.set(usize::MAX);}selected.set(id.clone());document::eval("document.querySelector('.curriculum-menu').close();");}},
                    span {class:"unit-summary",span {class:"unit-title",{format!("{} {}",if unit.id==active_id {"▶"}else if completed.contains(&unit.id) {"✓"} else if unlocked.contains(&unit.id) {"○"} else {"🔒"},unit.title)}}span {class:"unit-progress",{mission_progress(std::iter::once(unit),&completed_items)}}}
                    if unit.id==active_id {span {class:"unit-current","학습 중"}}
                }
                if unit.id==active_id {
                    nav {class:"curriculum-missions",aria_label:"단원 미션",
                        for (n,activity) in unit.activities.iter().enumerate() {
                            button {class:if n==active_mission {"curriculum-mission selected"}else{"curriculum-mission"},
                                aria_current:if n==active_mission {"step"}else{"false"},disabled:n>=active_unlocked,
                                onclick:move |_|{mission_index.set(n);document::eval("document.querySelector('.curriculum-menu').close();");},
                                span {class:"mission-kind",{format!("{} {} · {}",if n==active_mission {"▶"}else if completed_items.contains(&activity.progress_unit(unit).id){"✓"}else if n<active_unlocked {"○"}else{"🔒"},n+1,activity.label())}}
                                span {class:"mission-title","{activity.title}"}
                            }
                        }
                    }
                }
                }}
            }
        }}
        for active in [active] {UnitFlow {key:"{active.id}-{active.revision}-{epoch}", course_id:course.id.clone(), unit:active,index:mission_index,nav_prev:can_prev,nav_next:can_next,onnavigate:navigate,
            oncompleted:{let active_id=active_id.clone();let following_id=following_id.clone();let course=course.clone();move |passed|{
                let unit_finished=passed&&molip_quest::learning_store::LearningStore::user_store().and_then(|store|store.completed(&course)).is_ok_and(|done|done.contains(&active_id));
                if unit_finished {mission_index.set(usize::MAX);}
                selected.set(if unit_finished {following_id.clone().unwrap_or_else(||active_id.clone())}else{active_id.clone()});refresh+=1;if passed {clear_popup.set(true);}
            }}}}
        }
        if clear_popup() {div {class:"doctor-backdrop",section {class:"doctor-panel",role:"dialog",aria_label:"정답 확인",aria_modal:"true",
            if VIEW_ONLY {h2 {"미션 클리어!"} p {"진도를 저장하고 다음 미션을 준비했습니다."}}
            else {h2 {"정답입니다!"} p {"제출한 답안이 정답입니다. 진도를 저장하고 다음 미션을 준비했습니다."}}
            button {class:"primary",autofocus:true,onclick:move |_|clear_popup.set(false),"확인"}
        }}}
    }
}

#[component]
fn UnitFlow(
    course_id: String,
    unit: Unit,
    mut index: Signal<usize>,
    nav_prev: bool,
    nav_next: bool,
    onnavigate: EventHandler<i32>,
    oncompleted: EventHandler<bool>,
) -> Element {
    let mut refresh = use_signal(|| 0u64);
    let progress_course = course_id.clone();
    let progress_unit = unit.clone();
    let completed = use_memo(move || {
        let _ = refresh();
        let course = Course {
            id: progress_course.clone(),
            title: "KPC".into(),
            description: String::new(),
            chapters: vec![molip_quest::Chapter {
                id: "unit".into(),
                title: "unit".into(),
                units: vec![progress_unit.clone()],
            }],
        };
        molip_quest::learning_store::LearningStore::user_store()?.completed_items(&course)
    });
    if unit.activities.is_empty() {
        return rsx! { UnitWorkspace {course_id,unit,oncompleted} };
    }
    let completed = match completed() {
        Ok(items) => items,
        Err(e) => return rsx! {p {class:"error","{e}"}},
    };
    let unlocked_count = unlocked_activities(&unit, &completed);
    // A unit resumes at its first mission that is not cleared yet (the same rule as Learning).
    let active_index = if index() == usize::MAX {
        molip_quest::curriculum::unlocked_activities(&unit, &completed)
            .saturating_sub(1)
            .min(unlocked_count.saturating_sub(1))
    } else {
        index().min(unlocked_count.saturating_sub(1))
    };
    let active = unit.activities[active_index].clone();
    let progress = active.progress_unit(&unit);
    let count = unit
        .activities
        .iter()
        .filter(|a| completed.contains(&a.progress_unit(&unit).id))
        .count();
    let total = unit.activities.len();
    rsx! {
        section {class:"mission-strip",
            div {class:"mission-heading",strong {"{unit.title}"} span {"클리어 {count} / {total} · 현재 {active_index + 1}번째"}}
            // One cell per mission: cleared cells fill, the current one is outlined, and any cell jumps there.
            div {class:"mission-bar",role:"list",aria_label:"단원 진도",
                for (n, activity) in unit.activities.iter().enumerate() {
                    button {key:"{activity.id}",role:"listitem",
                        class:format!("mission-cell{}{}", if completed.contains(&activity.progress_unit(&unit).id) {" cleared"} else {""}, if n == active_index {" current"} else {""}),
                        title:format!("{} · {}{}", n + 1, activity.title, if completed.contains(&activity.progress_unit(&unit).id) {" (클리어)"} else {""}),
                        aria_current:if n == active_index {"step"} else {"false"},
                        onclick:move |_| index.set(n)}
                }
            }

        }
        for active in [active] {ActivityView {key:"{progress.id}-{progress.revision}",course_id:course_id.clone(),activity:active,progress:progress.clone(),nav_prev,nav_next,onnavigate,oncompleted:move |passed|{index.set(if passed {(active_index+1).min(total-1)}else{active_index});refresh+=1;oncompleted.call(passed);}}}
    }
}

#[component]
fn ActivityView(
    course_id: String,
    activity: Activity,
    progress: Unit,
    nav_prev: bool,
    nav_next: bool,
    onnavigate: EventHandler<i32>,
    oncompleted: EventHandler<bool>,
) -> Element {
    match activity.kind {
        ActivityKind::Coding { .. } if VIEW_ONLY => {
            rsx! {ReadOnlyMission {course_id,unit:progress,oncompleted}}
        }
        ActivityKind::Coding { .. } => rsx! {UnitWorkspace {course_id,unit:progress,oncompleted}},
        ActivityKind::Concept { body, check } => rsx! {
            div {class:"concept-flow",
                article {class:"reading-mission",span {class:"badge","개념"} h2 {"{activity.title}"}Markdown {text:body}}
                QuizView {course_id,unit:progress,questions:vec![check],nav_prev,nav_next,onnavigate,oncompleted}
            }
        },
        ActivityKind::Quiz { questions } => {
            rsx! {QuizView {course_id,unit:progress,questions,nav_prev,nav_next,onnavigate,oncompleted}}
        }
    }
}

#[component]
fn QuizView(
    course_id: String,
    unit: Unit,
    questions: Vec<Question>,
    nav_prev: bool,
    nav_next: bool,
    onnavigate: EventHandler<i32>,
    oncompleted: EventHandler<bool>,
) -> Element {
    let key = format!("quiz:{course_id}:{}:{}", unit.id, unit.revision);
    let initial = use_hook(|| -> Result<_, String> {
        let answers = drafts::load(&key)?.map(|d| d.answers).unwrap_or_default();
        let passed = molip_quest::learning_store::LearningStore::user_store()?
            .quiz_passed(&course_id, &unit, &questions)?;
        Ok((answers, passed))
    });
    let (initial_answers, initial_passed) = match initial {
        Ok(v) => v,
        Err(e) => return rsx! {p {class:"error","{e}"}},
    };
    // Keep the DOM value independent of answer updates: writing a controlled value
    // on every input interrupts native Korean IME composition in WebView2.
    let input_defaults = initial_answers.clone();
    let mut answers = use_signal(|| initial_answers);
    let mut passed = use_signal(|| initial_passed);
    let mut report = use_signal(|| None::<molip_quest::runner::TestReport>);
    let mut message = use_signal(String::new);
    let all_passed = passed.read().len() == questions.len();
    rsx! {article {class:"reading-mission quiz-mission",span {class:"badge",if questions.len()==1 {"개념 확인"}else{"퀴즈"}} h2 {"{unit.title}"}
        p {{format!("정답 완료 {} / {} 문항",passed.read().len(),questions.len())}}
        if all_passed {p {class:"clear-banner",role:"status","미션 클리어! 다음 미션으로 이동할 수 있어요."}}
        else {p {"맞힌 문항은 저장됩니다. 아직 맞히지 못한 문항만 다시 도전하세요."}}
        for (n,q) in questions.iter().enumerate().filter(|(_,q)|!passed.read().contains(&q.id)) {
            section {key:"{q.id}",class:"quiz-question",div {class:"question-heading",Markdown {text:format!("{}. {}",n+1,q.prompt)}}
                match &q.kind {
                    QuestionKind::Choice {options,..}=>rsx! {
                        for (option,text) in options.iter().enumerate() {
                            label {class:"quiz-option",input {r#type:"radio",name:q.id.clone(),value:option.to_string(),checked:answers.read().get(&q.id)==Some(&option.to_string()),onchange:{let id=q.id.clone();let key=key.clone();move |_|{answers.write().insert(id.clone(),option.to_string());report.set(None);if let Err(e)=drafts::save(&key,"",&answers()){message.set(e);}}}}Markdown {text:text.clone()}}
                        }
                    },
                    QuestionKind::ShortAnswer {..}=>rsx! {input {aria_label:q.prompt.clone(),placeholder:"답을 입력하세요",initial_value:input_defaults.get(&q.id).cloned().unwrap_or_default(),oninput:{let id=q.id.clone();let key=key.clone();move |e|{answers.write().insert(id.clone(),e.value());report.set(None);if let Err(e)=drafts::save(&key,"",&answers()){message.set(e);}}}}},
                }
                if let Some(result)=report.read().as_ref().and_then(|r|r.cases.get(n)) {
                    p {class:"error","다시 생각해보세요."}
                    Markdown {text:result.stderr.clone()}
                    p {"인정 답안: {result.expected}"}
                }
            }
        }
        if !passed.read().is_empty() {details {summary {"맞힌 문항과 해설 복습"}
            for q in questions.iter().filter(|q|passed.read().contains(&q.id)) {p {strong {"✓ {q.prompt}"}}Markdown {text:q.explanation.clone()}}
        }}
        p {class:"execution-status",role:"status","{message}"}
        div {class:"quiz-actions",
        button {class:"primary",disabled:all_passed,onclick:move |_|{
            let result=molip_quest::learning_store::LearningStore::user_store().and_then(|mut store|{
                let graded=store.save_quiz(&course_id,&unit,&questions,&answers())?;
                let completed=store.quiz_passed(&course_id,&unit,&questions)?;
                Ok((graded,completed))
            });
            match result {
                Ok((graded,completed))=>{message.set(format!("{} / {} 정답 · {}",completed.len(),questions.len(),if graded.passed {"미션 클리어!"}else{"오답 문항만 다시 풀어보세요."}));let cleared=graded.passed;passed.set(completed);report.set(Some(graded));oncompleted.call(cleared);},Err(e)=>message.set(e)
            }
        },"제출"}
        MissionNav {nav_prev,nav_next,onnavigate}
        }
    }}
}

/// `data/...csv|xlsx|html` paths mentioned by a problem's starter code or text, in order, once each.
fn data_files(text: &str) -> Vec<String> {
    let mut files = Vec::new();
    for (start, _) in text.match_indices("data/") {
        let end = text[start..]
            .find(|c: char| !(c.is_ascii_alphanumeric() || matches!(c, '/' | '.' | '_' | '-')))
            .map(|n| start + n)
            .unwrap_or(text.len());
        let path = text[start..end].trim_end_matches('.');
        if (path.ends_with(".csv") || path.ends_with(".xlsx") || path.ends_with(".html"))
            && !files.iter().any(|f| f == path)
        {
            files.push(path.to_string());
        }
    }
    files
}

/// Full-screen preview of a data file: tables through pandas (first 100 rows), HTML as source text.
#[component]
fn DataViewer(path: String, onclose: EventHandler<()>) -> Element {
    let code = if path.ends_with(".html") {
        format!("from pathlib import Path\nprint(Path({path:?}).read_text(encoding='utf-8'))")
    } else {
        let reader = if path.ends_with(".xlsx") {
            "read_excel"
        } else {
            "read_csv"
        };
        format!("import pandas as pd\ndf = pd.{reader}({path:?})\nprint(f'{{len(df)}}행 × {{len(df.columns)}}열')\ndf")
    };
    let result = use_resource(move || {
        let code = code.clone();
        async move { run_python(&code, "").await }
    });
    rsx! { div { class:"prompt-guide-layer data-viewer", role:"dialog", aria_modal:"true", aria_label:"자료 보기",
        onkeydown: move |e| { if e.key() == Key::Escape { onclose.call(()); } },
        header { class:"prompt-guide-header",
            h2 { "자료 보기" }
            span { class:"prompt-guide-unit", "{path}" }
            button { class:"prompt-guide-close", autofocus:true, onclick: move |_| onclose.call(()), "닫기 ×" }
        }
        div { class:"data-viewer-body",
            match &*result.read() {
                None => rsx! { p { class:"data-viewer-note", "읽는 중…" } },
                Some(Err(error)) => rsx! { p { class:"error", "{error}" } },
                Some(Ok(run)) => rsx! {
                    if !run.success { p { class:"error", "{run.stderr}" } }
                    if path.ends_with(".html") { pre { class:"data-viewer-source", "{run.stdout}" } }
                    else {
                        p { class:"data-viewer-note", "{run.stdout.trim()} · 앞 100행만 보여 줍니다." }
                        RichResults { artifacts: run.artifacts.clone() }
                    }
                },
            }
        }
    } }
}

/// Previous/next mission buttons for the bottom of a concept or quiz card.
#[component]
fn MissionNav(nav_prev: bool, nav_next: bool, onnavigate: EventHandler<i32>) -> Element {
    rsx! { div {class:"mission-nav",aria_label:"학습 이동",
        button {disabled:!nav_prev,onclick:move |_|onnavigate.call(-1),"← 이전"}
        button {disabled:!nav_next,onclick:move |_|onnavigate.call(1),"다음 →"}
    } }
}

#[component]
fn UnitWorkspace(course_id: String, unit: Unit, oncompleted: EventHandler<bool>) -> Element {
    let key = format!("local:{course_id}:{}:{}", unit.id, unit.revision);
    let initial = use_hook(|| {
        drafts::load(&key)
            .ok()
            .flatten()
            .unwrap_or_else(|| drafts::Draft {
                code: unit.starter_code.clone(),
                answers: HashMap::new(),
            })
    });
    let mut code = use_signal(|| initial.code.clone());
    let mut editor_reset = use_signal(|| 0u64);
    let mut answers = use_signal(|| initial.answers.clone());
    let sample_input = use_hook(|| {
        unit.tests
            .first()
            .map(|test| test.input.clone())
            .unwrap_or_default()
    });
    let mut input = use_signal(|| sample_input.clone());
    let mut output = use_signal(String::new);
    let mut artifacts = use_signal(Vec::<Artifact>::new);
    let mut message = use_signal(String::new);
    let mut busy = use_signal(|| false);
    let lines: Vec<Vec<(String, Option<String>)>> = unit
        .starter_code
        .lines()
        .map(|line| {
            let mut rest = line;
            let mut parts = Vec::new();
            while let Some(start) = rest.find("{{") {
                let Some(end) = rest[start + 2..].find("}}") else {
                    break;
                };
                let name = &rest[start + 2..start + 2 + end];
                parts.push((rest[..start].to_string(), None));
                if unit.blanks.iter().any(|b| b == name) {
                    parts.push((String::new(), Some(name.to_string())));
                } else {
                    parts.push((rest[start..start + end + 4].to_string(), None));
                }
                rest = &rest[start + end + 4..];
            }
            parts.push((rest.to_string(), None));
            parts
        })
        .collect();
    let mut guide_open = use_signal(|| false);
    let mut viewer = use_signal(|| None::<String>);
    let data_files = data_files(&format!("{}\n{}", unit.starter_code, unit.content));
    rsx! {article{class:"lesson",
        if guide_open() {PromptGuide {unit:unit.clone(),code:code(),onclose:move |_|guide_open.set(false)}}
        if let Some(path)=viewer() {DataViewer {path,onclose:move |_|viewer.set(None)}}
        section{class:"problem-pane",h2{"{unit.title}"}h3{"문제 설명"}Markdown {text:unit.content.clone()}
            if !VIEW_ONLY && !data_files.is_empty() {div {class:"data-files",
                for file in data_files.iter().cloned() {button {class:"data-file-open",onclick:move |_|viewer.set(Some(file.clone())),"자료 보기 · {file}"}}
            }}
            div {class:"prompt-buttons",
                button {class:"prompt-copy",onclick:{let unit=unit.clone();move |_|{
                    let prompt=molip_quest::curriculum::answer_prompt(&unit,&code());
                    match copy_to_clipboard(prompt) {
                        Ok(())=>toast("인간 버전을 복사했습니다. AI에 붙여넣고, 받은 코드를 편집기에 넣으세요.", "success"),
                        Err(e)=>toast(&format!("클립보드 복사에 실패했습니다: {e}"), "error")
                    }
                }},"프롬프트 복사 · 인간 버전"}
                button {class:"prompt-copy",onclick:{let unit=unit.clone();move |_|{
                    let prompt=molip_quest::curriculum::machine_prompt(&unit,&code());
                    match copy_to_clipboard(prompt) {
                        Ok(())=>toast("기계 버전을 복사했습니다. AI에 붙여넣고, 받은 코드를 편집기에 넣으세요.", "success"),
                        Err(e)=>toast(&format!("클립보드 복사에 실패했습니다: {e}"), "error")
                    }
                }},"프롬프트 복사 · 기계 버전"}
                button {class:"prompt-guide-open",onclick:move |_|guide_open.set(true),"프롬프트 해설"}
            }

            if !unit.blanks.is_empty(){p{class:"blank-note","코드의 빈칸만 채워보세요. 나머지 코드는 수정하지 않습니다."}}
        }
        div{class:"split-handle split-col",role:"separator",aria_orientation:"vertical",aria_label:"문제와 코드 영역 너비 조절",tabindex:"0",title:"드래그로 너비 조절, 더블 클릭으로 되돌리기"}
        section{class:"coding-pane",div{class:"pane-heading",strong{"main.py"}
        div{class:"pane-actions",button{disabled:busy(),onclick:{let unit=unit.clone();let key=key.clone();move |_|{code.set(unit.starter_code.clone());editor_reset+=1;answers.set(HashMap::new());output.set(String::new());artifacts.set(vec![]);message.set(String::new());let _=drafts::save(&key,&code(),&answers());}},"초기화"}
        button{disabled:busy(),onclick:move |_|async move{busy.set(true);message.set(String::new());artifacts.set(vec![]);match run_python(&code(),&input()).await{Ok(result)=>{artifacts.set(result.artifacts);if result.stderr.contains("EOFError: EOF when reading a line") {message.set("실행 입력이 부족합니다. 실행 입력 칸에 문제에서 요구한 값을 넣어주세요.".into());}else if result.success {message.set("실행 완료. 제출하면 전체 테스트로 정답을 확인합니다.".into());}output.set(format!("{}\n{}\n{}",result.stdout,result.stderr,if result.success {"실행 완료"} else {"실행 실패"}));},Err(e)=>message.set(e)}busy.set(false);},"코드 실행"}
            button{class:"primary",disabled:busy(),onclick:{let unit=unit.clone();let course_id=course_id.clone();move |_|{let unit=unit.clone();let course_id=course_id.clone();async move{
                busy.set(true);message.set(String::new());artifacts.set(vec![]);let source=code();let blank_answers=answers();
                if !unit.blanks.is_empty()&&assemble(&unit,&blank_answers).as_deref()!=Ok(source.as_str()){message.set("지정된 빈칸을 모두 채워주세요.".into());busy.set(false);return;}
                match check_unit(&unit,&source).await{Err(e)=>message.set(e),Ok(report)=>{output.set(report.cases.iter().enumerate().map(|(i,c)|format!("테스트 {} · {}\n입력: {}\n예상: {}\n결과: {}\n{}",i+1,if c.passed {"통과"} else {"실패"},c.input.trim(),c.expected.trim(),c.stdout.trim(),c.stderr.trim())).collect::<Vec<_>>().join("\n\n"));let passed=report.passed;
                    match molip_quest::learning_store::LearningStore::user_store().and_then(|mut store|store.save(&course_id,&unit,&source,&report)) {
                        Ok(())=>{message.set(if passed {"통과했습니다. 완료 기록을 이 컴퓨터에 저장했습니다."} else {"검사를 통과하지 못했습니다. 결과를 이 컴퓨터에 저장했습니다."}.into());oncompleted.call(passed);},
                        Err(e)=>message.set(e)
                    }
                }}busy.set(false);
            }}},"제출"}
        }
        }
        div{class:"editor-pane",
        if unit.blanks.is_empty(){textarea{class:"code-editor", "data-code-editor":"python", "data-editor-value":code(),"data-editor-reset":editor_reset().to_string(),aria_label:"Python 코드",spellcheck:false,initial_value:initial.code.clone(),oninput:{let key=key.clone();move|e|{code.set(e.value());if let Err(error)=drafts::save(&key,&code(),&answers()){message.set(error)}}}}}
        else{div{class:"inline-code",for (number,parts) in lines.iter().enumerate(){div{class:"code-line",span{class:"line-number","{number+1}"}div{class:"line-source",for (text,blank) in parts {if let Some(blank)=blank {input{class:"code-blank",aria_label:"빈칸 {blank}",spellcheck:false,value:answers.read().get(blank).cloned().unwrap_or_default(),oninput:{let blank=blank.clone();let unit=unit.clone();let key=key.clone();move|e|{answers.write().insert(blank.clone(),e.value());if let Ok(assembled)=assemble(&unit,&answers()){code.set(assembled);if let Err(error)=drafts::save(&key,&code(),&answers()){message.set(error)}}}}}}else{span{"{text}"}}}}}}}}
        }
        div{class:"split-handle split-row",role:"separator",aria_orientation:"horizontal",aria_label:"편집기와 실행 결과 높이 조절",tabindex:"0",title:"드래그로 높이 조절, 더블 클릭으로 되돌리기"}
        section{class:"result-pane",h3{"실행 결과"}details{open:!unit.tests.is_empty(),summary{"실행 입력"}p{"아래 입력값으로 실행합니다. 예제 입력을 바꾸며 연습할 수 있어요."}textarea{aria_label:"실행 입력",initial_value:sample_input.clone(),oninput:move|e|input.set(e.value())}}
            p{class:"execution-status",role:"status","{message}"}
            pre{class:"output",if output().is_empty(){"실행 결과가 여기에 표시됩니다."}else{"{output}"}}
            RichResults { artifacts: artifacts() }
        }}
    }}
}

/// View-only coding mission for the Android build: read the problem, acknowledge, move on.
#[component]
fn ReadOnlyMission(course_id: String, unit: Unit, oncompleted: EventHandler<bool>) -> Element {
    let mut message = use_signal(String::new);
    rsx! {article {class:"reading-mission view-only-mission",span {class:"badge","코딩 미션 · 열람"} h2 {"{unit.title}"}
        p {class:"muted","Android에서는 코드를 실행·채점하지 않습니다. 문제와 준비 코드를 읽고 데스크톱 앱에서 직접 풀어보세요. 아래 버튼을 누르면 다음 미션이 열립니다."}
        Markdown {text:unit.content.clone()}
        h3 {"준비 코드 · main.py"} pre {class:"output","{unit.starter_code}"}
        if !unit.tests.is_empty() {details {summary {"입출력 예제"}
            for (n,test) in unit.tests.iter().enumerate() {pre {class:"output",{format!("예제 {}\n입력:\n{}\n예상 출력:\n{}",n+1,test.input.trim_end(),test.expected.trim_end())}}}
        }}
        p {class:"execution-status",role:"status","{message}"}
        button {class:"primary",onclick:{let unit=unit.clone();move |_|{
            let report=molip_quest::runner::TestReport{passed:true,cases:vec![molip_quest::runner::TestCaseResult{input:String::new(),expected:"열람 확인".into(),stdout:"열람 확인".into(),stderr:String::new(),passed:true,state:"viewed".into()}]};
            match molip_quest::learning_store::LearningStore::user_store().and_then(|mut store|store.save(&course_id,&unit,&unit.starter_code,&report)) {
                Ok(())=>oncompleted.call(true),
                Err(e)=>message.set(e)
            }
        }},"읽었어요 · 다음 미션"}
    }}
}

#[component]
fn RichResults(artifacts: Vec<Artifact>) -> Element {
    rsx! { div { class: "rich-results",
        for artifact in artifacts { match artifact {
            Artifact::Image { title, data_url } => rsx! { figure { class:"plot-result", figcaption { "{title}" } img { src: data_url, alt: title } } },
            Artifact::Table { title, columns, rows, total_rows, total_columns } => rsx! { section { class:"table-result",
                h4 { "{title} · {total_rows}행 × {total_columns}열" }
                if total_rows > 100 || total_columns > 30 { p { class:"muted", "앞 100행·30열까지만 미리보기로 표시합니다." } }
                div { class:"data-grid", table { thead { tr { for column in columns { th { "{column}" } } } }
                    tbody { for row in rows { tr { for cell in row { td { "{cell}" } } } } }
                } }
            } },
        } }
    } }
}

/// "Start over" button with a confirmation step; wipes completions, attempts and drafts for the course.
/// Full-screen explanation of the human prompt (which words carry the expertise and why),
/// with the machine version of the same request beside it.
#[component]
fn PromptGuide(unit: Unit, code: String, onclose: EventHandler<()>) -> Element {
    let guide = molip_quest::curriculum::prompt_guide(&unit);
    let prompt = molip_quest::curriculum::machine_prompt(&unit, &code);
    rsx! { div { class:"prompt-guide-layer", role:"dialog", aria_modal:"true", aria_label:"정답 구하는 프롬프트 해설",
        onkeydown: move |e| { if e.key() == Key::Escape { onclose.call(()); } },
        header { class:"prompt-guide-header",
            h2 { "프롬프트 해설 · 인간 버전" }
            span { class:"prompt-guide-unit", "{unit.title}" }
            button { class:"prompt-guide-close", autofocus:true, onclick: move |_| onclose.call(()), "닫기 ×" }
        }
        div { class:"prompt-guide-body",
            section { class:"prompt-guide-text", Markdown { text: guide } }
            section { class:"prompt-guide-prompt",
                h3 { "기계 버전" }
                p { class:"prompt-guide-note", "같은 요청을 명세서로 쓴 것. 자동화할 때 쓴다." }
                button { class:"prompt-copy", onclick: {let prompt=prompt.clone(); move |_| {
                    match copy_to_clipboard(prompt.clone()) {
                        Ok(()) => toast("기계 버전을 복사했습니다.", "success"),
                        Err(e) => toast(&format!("클립보드 복사에 실패했습니다: {e}"), "error"),
                    }
                }}, "기계 버전 복사" }
                pre { class:"prompt-guide-source", "{prompt}" }
            }
        }
    } }
}

#[component]
pub fn ResetProgress(course_id: String, onreset: EventHandler<()>) -> Element {
    let mut confirming = use_signal(|| false);
    let mut message = use_signal(String::new);
    rsx! {
        button { class:"reset-progress", onclick: move |_| { message.set(String::new()); confirming.set(true); }, "진도 초기화" }
        if confirming() { div { class:"doctor-backdrop", section { class:"doctor-panel", role:"dialog", aria_label:"진도 초기화", aria_modal:"true",
            h2 { "처음부터 다시 시작할까요?" }
            p { "이 컴퓨터에 저장된 클리어 기록, 제출 기록, 작성 중인 코드와 퀴즈 답안을 모두 지웁니다. 되돌릴 수 없습니다." }
            if !message().is_empty() { p { class:"error", "{message}" } }
            div { class:"actions",
                button { onclick: move |_| confirming.set(false), "취소" }
                button { class:"danger", autofocus:true, onclick: {let course_id=course_id.clone(); move |_| {
                    match molip_quest::reset_progress(&course_id) {
                        Ok(()) => { confirming.set(false); onreset.call(()); }
                        Err(e) => message.set(e),
                    }
                }}, "모두 지우고 처음부터" }
            }
        } } }
    }
}

#[component]
pub fn DoctorPanel() -> Element {
    if VIEW_ONLY {
        return rsx! { span { class:"muted", "열람 모드 · Python 실행 없음" } };
    }
    let mut open = use_signal(|| false);
    let mut busy = use_signal(|| false);
    let mut checks = use_signal(Vec::<molip_quest::doctor::Check>::new);
    rsx! { button { onclick: move |_| async move {
        open.set(true); busy.set(true); checks.set(vec![]);
        checks.set(molip_quest::doctor::inspect().await); busy.set(false);
    }, "환경 진단" }
    if open() { div { class:"doctor-backdrop", section { class:"doctor-panel", role:"dialog", aria_label:"학습 환경 진단",
        h2 { "학습 환경 진단" }
        p { "Python과 실습 패키지 설치 상태를 확인합니다." }
        if busy() { p { role:"status", "검사 중입니다…" } }
        for check in checks() { div { class:if check.ready {"doctor-check ready"} else {"doctor-check missing"},
            strong { if check.ready {"✓ "} else {"! "} "{check.name}" } p { "{check.detail}" }
        } }
        button { onclick:move |_|open.set(false), "닫기" }
    } } }
    }
}

#[component]
fn Markdown(text: String) -> Element {
    rsx! {div {class:"markdown",dangerous_inner_html:molip_quest::markdown::render(&text)}}
}
