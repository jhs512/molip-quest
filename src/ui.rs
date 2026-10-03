use dioxus::prelude::*;
use molip_quest::{
    curriculum::{Activity, ActivityKind, Question, QuestionKind},
    drafts,
    runner::{assemble, check_unit, run_python, Artifact},
    Course, Unit,
};
use std::collections::HashMap;

#[component]
pub fn Learning(course: Course) -> Element {
    let mut selected = use_signal(String::new);
    let mut clear_popup = use_signal(|| false);
    let mut refresh = use_signal(|| 0u64);
    let progress_course = course.clone();
    let completed = use_memo(move || {
        let _ = refresh();
        molip_quest::learning_store::LearningStore::user_store()?.completed(&progress_course)
    });
    let completed = match completed() {
        Ok(completed) => completed,
        Err(error) => return rsx! {p {class:"error", "{error}"}},
    };
    let unlocked = molip_quest::curriculum::unlocked_units(&course, &completed);
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
    rsx! {header {class:"practice-header", h1 {"{course.title}"} span {{format!("완료 {} / {} 단원",completed.len(),course.total_units())}} DoctorPanel {}}
        div {class:"learning", details {class:"curriculum-menu", summary {"수업 목차 ▾"} nav {class:"curriculum", h2 {"수업 목차"}
            for chapter in &course.chapters {h3 {{format!("{} · {}/{}",chapter.title,chapter.units.iter().filter(|u|completed.contains(&u.id)).count(),chapter.units.len())}}
                for unit in &chapter.units {button {class:"unit",disabled:!unlocked.contains(&unit.id),onclick:{let id=unit.id.clone();move |_|selected.set(id.clone())}, {format!("{} {}",if completed.contains(&unit.id) {"✓"} else if unlocked.contains(&unit.id) {"○"} else {"🔒"},unit.title)}}}
            }
        }}
        for active in [active] {UnitFlow {key:"{active.id}-{active.revision}", course_id:course.id.clone(), unit:active, has_previous_unit:previous.is_some(),has_next_unit:next.is_some(),
            onpreviousunit:{let previous=previous.clone();move |_|{if let Some(id)=&previous {selected.set(id.clone());}}},
            onnextunit:{let next=next.clone();move |_|{if let Some(id)=&next {selected.set(id.clone());}}},
            oncompleted:{let active_id=active_id.clone();move |passed|{selected.set(active_id.clone());refresh+=1;if passed {clear_popup.set(true);}}}}}
        }
        if clear_popup() {div {class:"doctor-backdrop",section {class:"doctor-panel",role:"dialog",aria_label:"정답 확인",aria_modal:"true",
            h2 {"정답입니다!"} p {"미션을 클리어했습니다. 다음 버튼으로 계속 학습하세요."}
            button {class:"primary",autofocus:true,onclick:move |_|clear_popup.set(false),"확인"}
        }}}
    }
}

#[component]
fn UnitFlow(
    course_id: String,
    unit: Unit,
    oncompleted: EventHandler<bool>,
    has_previous_unit: bool,
    has_next_unit: bool,
    onpreviousunit: EventHandler<()>,
    onnextunit: EventHandler<()>,
) -> Element {
    let mut index = use_signal(|| usize::MAX);
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
    let unlocked_count = molip_quest::curriculum::unlocked_activities(&unit, &completed);
    let active_index = if index() == usize::MAX {
        unlocked_count.saturating_sub(1)
    } else {
        index().min(unlocked_count.saturating_sub(1))
    };
    let active = unit.activities[active_index].clone();
    let progress = active.progress_unit(&unit);
    let cleared = completed.contains(&progress.id);
    let count = unit
        .activities
        .iter()
        .filter(|a| completed.contains(&a.progress_unit(&unit).id))
        .count();
    let total = unit.activities.len();
    rsx! {
        section {class:"mission-strip",
            div {class:"mission-heading",strong {"{unit.title}"} span {"클리어 {count} / {total}"}}
            progress {value:count as f64,max:total as f64,aria_label:"단원 진도"}
            nav {class:"mission-tabs",aria_label:"단원 미션",
                for (n,activity) in unit.activities.iter().enumerate() {
                    button {class:if n==active_index {"selected"}else{""},disabled:n>=unlocked_count,onclick:move |_|index.set(n),
                        {format!("{} {} · {}",if completed.contains(&activity.progress_unit(&unit).id){"✓"}else if n<unlocked_count {"○"}else{"🔒"},n+1,activity.label())}}
                }
            }
            div {class:"mission-controls",
                button {disabled:active_index==0&&!has_previous_unit,onclick:move |_|{if active_index==0 {onpreviousunit.call(());}else{index.set(active_index-1);}},"← 이전"}
                span {if cleared {"미션 클리어!"}else{"내 속도로 읽고, 실행하고, 확인하세요."}}
                button {disabled:active_index+1>=unlocked_count&&!(active_index+1==total&&has_next_unit),onclick:move |_|{if active_index+1<unlocked_count {index.set(active_index+1);}else if active_index+1==total&&has_next_unit {onnextunit.call(());}},"다음 →"}
            }
        }
        for active in [active] {ActivityView {key:"{progress.id}-{progress.revision}",course_id:course_id.clone(),activity:active,progress:progress.clone(),oncompleted:move |passed|{index.set(active_index);refresh+=1;oncompleted.call(passed);}}}
    }
}

#[component]
fn ActivityView(
    course_id: String,
    activity: Activity,
    progress: Unit,
    oncompleted: EventHandler<bool>,
) -> Element {
    match activity.kind {
        ActivityKind::Coding { .. } => rsx! {UnitWorkspace {course_id,unit:progress,oncompleted}},
        ActivityKind::Concept { body, check } => rsx! {
            div {class:"concept-flow",
                article {class:"reading-mission",span {class:"badge","개념"} h2 {"{activity.title}"}Markdown {text:body}}
                QuizView {course_id,unit:progress,questions:vec![check],oncompleted}
            }
        },
        ActivityKind::Quiz { questions } => {
            rsx! {QuizView {course_id,unit:progress,questions,oncompleted}}
        }
    }
}

#[component]
fn QuizView(
    course_id: String,
    unit: Unit,
    questions: Vec<Question>,
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
        button {class:"primary",disabled:all_passed,onclick:move |_|{
            let result=molip_quest::learning_store::LearningStore::user_store().and_then(|mut store|{
                let graded=store.save_quiz(&course_id,&unit,&questions,&answers())?;
                let completed=store.quiz_passed(&course_id,&unit,&questions)?;
                Ok((graded,completed))
            });
            match result {
                Ok((graded,completed))=>{message.set(format!("{} / {} 정답 · {}",completed.len(),questions.len(),if graded.passed {"미션 클리어!"}else{"오답 문항만 다시 풀어보세요."}));let cleared=graded.passed;passed.set(completed);report.set(Some(graded));oncompleted.call(cleared);},Err(e)=>message.set(e)
            }
        },"채점 · 클리어 확인"}
    }}
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
    let mut input = use_signal(String::new);
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
    rsx! {article{class:"lesson",
        section{class:"problem-pane",h2{"{unit.title}"}h3{"문제 설명"}Markdown {text:unit.content.clone()}
            button {class:"prompt-copy",onclick:{let unit=unit.clone();move |_|{
                let prompt=molip_quest::curriculum::answer_prompt(&unit,&code());
                match arboard::Clipboard::new().and_then(|mut clipboard|clipboard.set_text(prompt)) {
                    Ok(())=>message.set("정답 요청 프롬프트를 복사했습니다. 원하는 AI에 붙여넣고, 받은 main.py 코드를 편집기에 넣으세요.".into()),
                    Err(e)=>message.set(format!("클립보드 복사에 실패했습니다: {e}"))
                }
            }},"정답 프롬프트 복사"}

            if !unit.blanks.is_empty(){p{class:"blank-note","코드의 빈칸만 채워보세요. 나머지 코드는 수정하지 않습니다."}}
        }
        section{class:"coding-pane",div{class:"pane-heading",strong{"main.py"}span{"Python"}}
        div{class:"editor-pane",
        if unit.blanks.is_empty(){textarea{class:"code-editor", "data-code-editor":"python", "data-editor-value":code(),"data-editor-reset":editor_reset().to_string(),aria_label:"Python 코드",spellcheck:false,initial_value:initial.code.clone(),oninput:{let key=key.clone();move|e|{code.set(e.value());if let Err(error)=drafts::save(&key,&code(),&answers()){message.set(error)}}}}}
        else{div{class:"inline-code",for (number,parts) in lines.iter().enumerate(){div{class:"code-line",span{class:"line-number","{number+1}"}div{class:"line-source",for (text,blank) in parts {if let Some(blank)=blank {input{class:"code-blank",aria_label:"빈칸 {blank}",spellcheck:false,value:answers.read().get(blank).cloned().unwrap_or_default(),oninput:{let blank=blank.clone();let unit=unit.clone();let key=key.clone();move|e|{answers.write().insert(blank.clone(),e.value());if let Ok(assembled)=assemble(&unit,&answers()){code.set(assembled);if let Err(error)=drafts::save(&key,&code(),&answers()){message.set(error)}}}}}}else{span{"{text}"}}}}}}}}
        }
        section{class:"result-pane",h3{"실행 결과"}details{summary{"실행 입력"}textarea{aria_label:"실행 입력",initial_value:"",oninput:move|e|input.set(e.value())}}
            p{class:"execution-status",role:"status","{message}"}
            pre{class:"output",if output().is_empty(){"실행 결과가 여기에 표시됩니다."}else{"{output}"}}
            RichResults { artifacts: artifacts() }
        }}
        footer{class:"actions practice-actions",button{disabled:busy(),onclick:{let unit=unit.clone();let key=key.clone();move |_|{code.set(unit.starter_code.clone());editor_reset+=1;answers.set(HashMap::new());output.set(String::new());artifacts.set(vec![]);message.set(String::new());let _=drafts::save(&key,&code(),&answers());}},"초기화"}
        button{disabled:busy(),onclick:move |_|async move{busy.set(true);message.set(String::new());artifacts.set(vec![]);match run_python(&code(),&input()).await{Ok(result)=>{artifacts.set(result.artifacts);output.set(format!("{}\n{}\n{}",result.stdout,result.stderr,if result.success {"실행 완료"} else {"실행 실패"}));},Err(e)=>message.set(e)}busy.set(false);},"코드 실행"}
            button{class:"primary",disabled:busy(),onclick:{let unit=unit.clone();let course_id=course_id.clone();move |_|{let unit=unit.clone();let course_id=course_id.clone();async move{
                busy.set(true);message.set(String::new());artifacts.set(vec![]);let source=code();let blank_answers=answers();
                if !unit.blanks.is_empty()&&assemble(&unit,&blank_answers).as_deref()!=Ok(source.as_str()){message.set("지정된 빈칸을 모두 채워주세요.".into());busy.set(false);return;}
                match check_unit(&unit,&source).await{Err(e)=>message.set(e),Ok(report)=>{output.set(report.cases.iter().enumerate().map(|(i,c)|format!("테스트 {} · {}\n입력: {}\n예상: {}\n결과: {}\n{}",i+1,if c.passed {"통과"} else {"실패"},c.input.trim(),c.expected.trim(),c.stdout.trim(),c.stderr.trim())).collect::<Vec<_>>().join("\n\n"));let passed=report.passed;
                    match molip_quest::learning_store::LearningStore::user_store().and_then(|mut store|store.save(&course_id,&unit,&source,&report)) {
                        Ok(())=>{message.set(if passed {"통과했습니다. 완료 기록을 이 컴퓨터에 저장했습니다."} else {"검사를 통과하지 못했습니다. 결과를 이 컴퓨터에 저장했습니다."}.into());oncompleted.call(passed);},
                        Err(e)=>message.set(e)
                    }
                }}busy.set(false);
            }}},"테스트 · 완료"}
        }
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

#[component]
pub fn DoctorPanel() -> Element {
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
