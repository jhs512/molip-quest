use dioxus::prelude::*;
use molip_quest::curriculum::{Activity, ActivityKind, Question, QuestionKind};

#[derive(Clone, Copy)]
pub(crate) struct InstructorSession(pub Signal<Option<crate::practice::Materials>>);

#[component]
pub(crate) fn InstructorLogin() -> Element {
    let mut session = use_context::<InstructorSession>().0;
    let mut open = use_signal(|| false);
    let mut password = use_signal(String::new);
    let mut error = use_signal(String::new);
    let mut busy = use_signal(|| false);
    rsx! {
        button {class:"instructor-login",onclick:move |_|{if session().is_some(){document::eval("window.molipAgent?.stop()");session.set(None);}else{open.set(true);error.set(String::new());}}, {if session().is_some(){"강사모드 종료"}else{"강사모드 접속"}}}
        if open() {
            div {class:"doctor-backdrop",onclick:move |_|{if !busy(){open.set(false);password.set(String::new());}},
                form {class:"doctor-panel practice-password",role:"dialog",aria_modal:"true",aria_label:"강사모드 접속",onclick:move |e|e.stop_propagation(),onkeydown:move |e|{if e.key()==Key::Escape&&!busy(){open.set(false);password.set(String::new());}},
                    onsubmit:move |e|{e.prevent_default();if busy(){return;}let supplied=password();password.set(String::new());busy.set(true);error.set(String::new());spawn(async move {match tokio::task::spawn_blocking(move ||crate::practice::decrypt(&supplied)).await {Ok(Ok(materials))=>{session.set(Some(materials));open.set(false);},Ok(Err(message))=>error.set(message),Err(_)=>error.set("확인하지 못했습니다. 다시 시도하세요.".into())}busy.set(false);});},
                    h2 {"강사모드 접속"}label {r#for:"instructor-password","비밀번호"}
                    input {id:"instructor-password",r#type:"password",autofocus:true,autocomplete:"off",value:password(),oninput:move |e|password.set(e.value())}
                    p {class:"error",role:"status","{error}"}
                    div {class:"actions",button {class:"primary",r#type:"submit",disabled:busy()||password().is_empty(),{if busy(){"확인 중…"}else{"접속"}}}button {r#type:"button",disabled:busy(),onclick:move |_|{open.set(false);password.set(String::new());},"취소"}}
                }
            }
        }
    }
}

fn question_answer(question: &Question) -> String {
    let answer = match &question.kind {
        QuestionKind::Choice { options, correct } => format!(
            "{}. {}",
            correct + 1,
            options.get(*correct).map(String::as_str).unwrap_or("")
        ),
        QuestionKind::ShortAnswer { accepted } => accepted.join(" / "),
        QuestionKind::TableSelect { expected, .. } => expected.clone(),
    };
    format!(
        "{}\n정답: {}\n{}",
        question.prompt, answer, question.explanation
    )
}
fn answer(activity: &Activity) -> String {
    match &activity.kind {
        ActivityKind::Coding { .. } => {
            let solutions: std::collections::HashMap<String, String> =
                serde_json::from_str(include_str!("../courses/kpc-solutions.json"))
                    .unwrap_or_default();
            if let Some(code) = solutions.get(&activity.id) {
                return code.clone();
            }
            let mut code = String::new();
            for action in &activity.narration {
                if action["action"] == "type_code" || action["action"] == "set_code" {
                    if action["replace"] == true || action["action"] == "set_code" {
                        code.clear();
                    }
                    if let Some(chunk) = action["code"].as_str() {
                        code.push_str(chunk);
                    }
                }
            }
            if code.is_empty() {
                "이 미션의 준비된 정답 코드가 없습니다.".into()
            } else {
                code
            }
        }
        ActivityKind::Concept { check, .. } => question_answer(check),
        ActivityKind::Quiz { questions } => questions
            .iter()
            .map(question_answer)
            .collect::<Vec<_>>()
            .join("\n\n"),
        ActivityKind::Slides { .. } => "슬라이드를 읽고 다음 장으로 진행하세요.".into(),
    }
}

/// What "정답 보기" runs through the tutor agent: the answers go in and grading is pressed, with
/// no answer card. Coding puts the solution in the editor and submits; concept and quiz replay the
/// answer_quiz steps of the compiled narration (the same answers the 해설 ticks) without speech.
fn solve_actions(activity: &Activity) -> serde_json::Value {
    use serde_json::json;
    match &activity.kind {
        ActivityKind::Coding { .. } => json!([
            {"action": "set_code", "code": answer(activity)},
            {"action": "submit"}
        ]),
        ActivityKind::Concept { .. } | ActivityKind::Quiz { .. } => {
            let mut steps: Vec<serde_json::Value> = activity
                .narration
                .iter()
                .filter(|a| a["action"] == "answer_quiz")
                .cloned()
                .map(|mut a| {
                    a.as_object_mut().map(|o| o.remove("say"));
                    a
                })
                .collect();
            if steps.is_empty() {
                let questions: Vec<&Question> = match &activity.kind {
                    ActivityKind::Concept { check, .. } => vec![check],
                    ActivityKind::Quiz { questions } => questions.iter().collect(),
                    _ => vec![],
                };
                let answers: serde_json::Map<String, serde_json::Value> = questions
                    .iter()
                    .enumerate()
                    .filter_map(|(i, q)| match &q.kind {
                        QuestionKind::Choice { correct, .. } => Some((correct + 1).to_string()),
                        QuestionKind::ShortAnswer { accepted } => accepted.first().cloned(),
                        QuestionKind::TableSelect { .. } => None,
                    }
                    .map(|a| ((i + 1).to_string(), serde_json::Value::String(a))))
                    .collect();
                steps.push(json!({"action": "answer_quiz", "answers": answers}));
            }
            serde_json::Value::Array(steps)
        }
        ActivityKind::Slides { .. } => json!([]),
    }
}

#[component]
pub(crate) fn InstructorControls(activity: Activity) -> Element {
    let session = use_context::<InstructorSession>().0;
    let mut running = use_signal(|| false);
    let mut paused = use_signal(|| false);
    let mut report = use_signal(String::new);
    use_drop(|| {
        document::eval("window.molipAgent?.stop()");
    });
    if session().is_none() {
        return rsx! {};
    }
    // A deck has nothing to fill in: "정답 보기" marks it watched, the same as "다 봤어요 · 미션 완료".
    let slides = matches!(activity.kind, ActivityKind::Slides { .. });
    let solve = serde_json::to_string(&solve_actions(&activity)).unwrap_or_else(|_| "[]".into());
    let actions = serde_json::to_string(&activity.narration).unwrap_or_else(|_| "[]".into());
    rsx! {
        div {class:"instructor-controls",
            button {class:"instructor-answer",disabled:running(),onclick:move |_|{document::eval("window.molipAgent?.stop()");if slides {document::eval("document.querySelector('.slides-finish')?.click()");return;}running.set(true);paused.set(false);report.set(String::new());let solve=solve.clone();spawn(async move {let script=format!("(async()=>{{const a=window.molipAgent,voice=a.voice;a.setVoice(false);try{{dioxus.send(await a.run({solve}));}}catch(e){{dioxus.send(String(e));}}finally{{a.setVoice(voice);}}}})()");let mut eval=document::eval(&script);let result=eval.recv::<String>().await.unwrap_or_else(|_|"정답을 넣지 못했습니다.".into());running.set(false);report.set(result);});},"정답 보기"}
            button {class:"instructor-explain",disabled:running()||actions=="[]",onclick:move |_|{running.set(true);paused.set(false);report.set(String::new());let actions=actions.clone();spawn(async move {let script=format!("(async()=>{{const a=window.molipAgent,voice=a.voice,name=a.voiceName;a.setVoiceName('system');a.setVoice(true);try{{dioxus.send(await a.run({actions}));}}catch(e){{dioxus.send(String(e));}}finally{{a.setVoice(voice);a.setVoiceName(name);}}}})()");let mut eval=document::eval(&script);let result=eval.recv::<String>().await.unwrap_or_else(|_|"해설을 종료했습니다.".into());running.set(false);paused.set(false);report.set(result);});},"해설 보기"}
            if running() {
                button {onclick:move |_|{if paused(){document::eval("window.molipAgent?.resume()");}else{document::eval("window.molipAgent?.pause()");}paused.set(!paused());},{if paused(){"계속"}else{"일시정지"}}}
                button {onclick:move |_|{document::eval("window.molipAgent?.stop()");},"해설 멈춤"}
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn every_coding_answer_matches_compiled_narration_and_challenge_reference() {
        let course =
            molip_quest::Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        for activity in course
            .chapters
            .iter()
            .flat_map(|c| &c.units)
            .flat_map(|u| &u.activities)
        {
            if matches!(activity.kind, ActivityKind::Coding { .. }) {
                assert!(
                    !answer(activity).contains("정답 코드가 없습니다"),
                    "{}",
                    activity.id
                );
            }
        }
        let hello = course.chapters[0].units[0]
            .activities
            .iter()
            .find(|a| a.id == "hello")
            .unwrap();
        assert!(answer(hello).contains("print("));
        let concept = course.chapters[0].units[0]
            .activities
            .iter()
            .find(|a| a.id == "runtime")
            .unwrap();
        assert!(answer(concept).contains("정답:"));
    }
}
