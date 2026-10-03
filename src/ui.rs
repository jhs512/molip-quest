use dioxus::prelude::*;
use molip_quest::{
    ai::AiConnection,
    drafts,
    runner::{assemble, check_unit, run_python, Artifact},
    Course, Unit,
};
use std::collections::HashMap;

#[component]
pub fn Learning(course: Course) -> Element {
    let mut selected = use_signal(String::new);
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
    let active = course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .find(|u| u.id == selected())
        .unwrap_or(&course.chapters[0].units[0])
        .clone();
    rsx! {header {class:"practice-header", h1 {"{course.title}"} span {{format!("완료 {} / {} 단원",completed.len(),course.total_units())}} DoctorPanel {}}
        div {class:"learning", details {class:"curriculum-menu", summary {"수업 목차 ▾"} nav {class:"curriculum", h2 {"수업 목차"}
            for chapter in &course.chapters {h3 {{format!("{} · {}/{}",chapter.title,chapter.units.iter().filter(|u|completed.contains(&u.id)).count(),chapter.units.len())}}
                for unit in &chapter.units {button {class:"unit",onclick:{let id=unit.id.clone();move |_|selected.set(id.clone())}, {format!("{} {}",if completed.contains(&unit.id) {"✓"} else {"○"},unit.title)}}}
            }
        }}
        for active in [active] {UnitWorkspace {key:"{active.id}-{active.revision}", course_id:course.id.clone(), unit:active, oncompleted:move |_|refresh+=1}}
        }
    }
}

#[component]
fn UnitWorkspace(course_id: String, unit: Unit, oncompleted: EventHandler<()>) -> Element {
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
        section{class:"problem-pane",h2{"{unit.title}"}h3{"문제 설명"}p{class:"content","{unit.content}"}
            if !unit.blanks.is_empty(){p{class:"blank-note","코드의 빈칸만 채워보세요. 나머지 코드는 수정하지 않습니다."}}
            div{class:"lesson-ai",h3{"AI와 함께 풀기"}AiPanel{unit:unit.clone(),code,answers,input,output,artifacts,busy,draft_key:key.clone()}}
        }
        section{class:"coding-pane",div{class:"pane-heading",strong{"main.py"}span{"Python"}}
        div{class:"editor-pane",
        if unit.blanks.is_empty(){textarea{class:"code-editor", "data-code-editor":"python", "data-editor-value":code(),aria_label:"Python 코드",spellcheck:false,value:code(),oninput:{let key=key.clone();move|e|{code.set(e.value());if let Err(error)=drafts::save(&key,&code(),&answers()){message.set(error)}}}}}
        else{div{class:"inline-code",for (number,parts) in lines.iter().enumerate(){div{class:"code-line",span{class:"line-number","{number+1}"}div{class:"line-source",for (text,blank) in parts {if let Some(blank)=blank {input{class:"code-blank",aria_label:"빈칸 {blank}",spellcheck:false,value:answers.read().get(blank).cloned().unwrap_or_default(),oninput:{let blank=blank.clone();let unit=unit.clone();let key=key.clone();move|e|{answers.write().insert(blank.clone(),e.value());if let Ok(assembled)=assemble(&unit,&answers()){code.set(assembled);if let Err(error)=drafts::save(&key,&code(),&answers()){message.set(error)}}}}}}else{span{"{text}"}}}}}}}}
        }
        section{class:"result-pane",h3{"실행 결과"}details{summary{"실행 입력"}textarea{aria_label:"실행 입력",value:input(),oninput:move|e|input.set(e.value())}}
            p{class:"execution-status",role:"status","{message}"}
            pre{class:"output",if output().is_empty(){"실행 결과가 여기에 표시됩니다."}else{"{output}"}}
            RichResults { artifacts: artifacts() }
        }}
        footer{class:"actions practice-actions",button{disabled:busy(),onclick:{let unit=unit.clone();let key=key.clone();move |_|{code.set(unit.starter_code.clone());answers.set(HashMap::new());output.set(String::new());artifacts.set(vec![]);message.set(String::new());let _=drafts::save(&key,&code(),&answers());}},"초기화"}
        button{disabled:busy(),onclick:move |_|async move{busy.set(true);message.set(String::new());artifacts.set(vec![]);match run_python(&code(),&input()).await{Ok(result)=>{artifacts.set(result.artifacts);output.set(format!("{}\n{}\n{}",result.stdout,result.stderr,if result.success {"실행 완료"} else {"실행 실패"}));},Err(e)=>message.set(e)}busy.set(false);},"코드 실행"}
            button{class:"primary",disabled:busy(),onclick:{let unit=unit.clone();let course_id=course_id.clone();move |_|{let unit=unit.clone();let course_id=course_id.clone();async move{
                busy.set(true);message.set(String::new());artifacts.set(vec![]);let source=code();let blank_answers=answers();
                if !unit.blanks.is_empty()&&assemble(&unit,&blank_answers).as_deref()!=Ok(source.as_str()){message.set("지정된 빈칸을 모두 채워주세요.".into());busy.set(false);return;}
                match check_unit(&unit,&source).await{Err(e)=>message.set(e),Ok(report)=>{output.set(report.cases.iter().enumerate().map(|(i,c)|format!("테스트 {} · {}\n입력: {}\n예상: {}\n결과: {}\n{}",i+1,if c.passed {"통과"} else {"실패"},c.input.trim(),c.expected.trim(),c.stdout.trim(),c.stderr.trim())).collect::<Vec<_>>().join("\n\n"));let passed=report.passed;
                    match molip_quest::learning_store::LearningStore::user_store().and_then(|mut store|store.save(&course_id,&unit,&source,&report)) {
                        Ok(())=>{message.set(if passed {"통과했습니다. 완료 기록을 이 컴퓨터에 저장했습니다."} else {"검사를 통과하지 못했습니다. 결과를 이 컴퓨터에 저장했습니다."}.into());oncompleted.call(());},
                        Err(e)=>message.set(e)
                    }
                }}busy.set(false);
            }}},"테스트 · 완료"}
        }
    }}
}

#[component]
fn AiPanel(
    unit: Unit,
    mut code: Signal<String>,
    mut answers: Signal<HashMap<String, String>>,
    input: Signal<String>,
    mut output: Signal<String>,
    mut artifacts: Signal<Vec<Artifact>>,
    mut busy: Signal<bool>,
    draft_key: String,
) -> Element {
    let mut connection = use_signal(AiConnection::default);
    let mut question = use_signal(String::new);
    let mut reply = use_signal(String::new);
    rsx! {section{class:"ai-panel",h3{"나의 AI 도구"}details{summary{"연결 설정과 준비 안내"}
        p{class:"muted","기본 연결은 설치·로그인한 Claude Code입니다. claude-cli를 그대로 사용하세요. 필요하면 OmniRoute 등의 OpenAI 호환 주소로 바꿀 수 있습니다. 비용과 한도는 연결 계정의 조건을 따릅니다."}
        label{"연결 방식 또는 주소" input{value:connection.read().base.clone(),oninput:move|e|connection.write().base=e.value()}}
        label{"모델" input{value:connection.read().model.clone(),oninput:move|e|connection.write().model=e.value()}}
        label{"연결 키 (필요한 경우)" input{r#type:"password",value:connection.read().key.clone(),oninput:move|e|connection.write().key=e.value()}}
    }textarea{placeholder:"AI에게 질문하거나 수정할 내용을 입력하세요",value:question(),oninput:move|e|question.set(e.value())}
        div{class:"actions",
            button{disabled:busy(),onclick:{let unit=unit.clone();move |_|{let unit=unit.clone();async move{busy.set(true);match connection().ask(&unit,&code(),&question(),false).await{Ok(answer)=>reply.set(answer.message),Err(e)=>reply.set(e)}busy.set(false);}}},"설명 · 힌트"}
            button{disabled:busy(),onclick:{let unit=unit.clone();let key=draft_key.clone();move |_|{let unit=unit.clone();let key=key.clone();async move{busy.set(true);
                match connection().ask(&unit,&code(),&question(),true).await{Err(e)=>reply.set(e),Ok(answer)=>{reply.set(answer.message);if let Some(source)=answer.code{code.set(source.clone());if !unit.blanks.is_empty(){answers.set(answer.answers);}if let Err(e)=drafts::save(&key,&source,&answers()){reply.set(e);}artifacts.set(vec![]);match run_python(&source,&input()).await{Ok(result)=>{artifacts.set(result.artifacts);output.set(format!("{}\n{}\n{}",result.stdout,result.stderr,if result.success {"실행 완료"} else {"실행 실패"}));},Err(e)=>output.set(e)}}}}busy.set(false);
            }}},"AI 수정 · 실행"}
        }p{class:"content","{reply}"}
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
        p { "Python과 실습 패키지, Claude 설치·로그인 상태를 확인합니다." }
        if busy() { p { role:"status", "검사 중입니다…" } }
        for check in checks() { div { class:if check.ready {"doctor-check ready"} else {"doctor-check missing"},
            strong { if check.ready {"✓ "} else {"! "} "{check.name}" } p { "{check.detail}" }
        } }
        button { onclick:move |_|open.set(false), "닫기" }
    } } }
    }
}
