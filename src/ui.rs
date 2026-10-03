use dioxus::prelude::*;
use molip_quest::{
    ai::AiConnection,
    client::Api,
    drafts,
    runner::{assemble, check_unit, run_python, Artifact},
    Course, Unit,
};
use serde_json::{json, Value};
use std::collections::HashMap;

#[component]
pub fn ClassDetails(
    api: Api,
    classroom: String,
    courses: Vec<Value>,
    staff: bool,
    oncourse: EventHandler<String>,
) -> Element {
    let mut pick = use_signal(String::new);
    let mut message = use_signal(String::new);
    let mut refresh = use_signal(|| 0u64);
    let fetch_api = api.clone();
    let fetch_class = classroom.clone();
    let data = use_resource(move || {
        let _ = refresh();
        let api = fetch_api.clone();
        let id = fetch_class.clone();
        async move {
            let assigned = api
                .get::<Vec<Value>>(&format!("/api/classrooms/{id}/courses"))
                .await?;
            let progress = api
                .get::<Vec<Value>>(&format!("/api/classrooms/{id}/progress"))
                .await?;
            let submissions = api
                .get::<Vec<Value>>(&format!("/api/classrooms/{id}/submissions"))
                .await?;
            let students = if staff {
                api.get::<Vec<Value>>(&format!("/api/classrooms/{id}/students"))
                    .await?
            } else {
                Vec::new()
            };
            Ok::<_, String>((assigned, progress, submissions, students))
        }
    });
    let (assigned, progress, submissions, students) = data
        .read()
        .as_ref()
        .and_then(|r| r.as_ref().ok())
        .cloned()
        .unwrap_or_default();
    let error = data
        .read()
        .as_ref()
        .and_then(|r| r.as_ref().err())
        .cloned()
        .unwrap_or_default();
    rsx! {p{class:"error",role:"alert","{error}"}
        if staff{section{class:"card",h2{"수업 배정"}select{value:pick(),onchange:move|e|pick.set(e.value()),option{value:"","수업 선택"}
            for course in courses{option{value:course["id"].as_str().unwrap_or_default(),{course["title"].as_str().unwrap_or_default()}}}
        }button{class:"primary",onclick:{let api=api.clone();let id=classroom.clone();move |_|{let api=api.clone();let id=id.clone();async move{match api.post::<Value>(&format!("/api/classrooms/{id}/assign"),json!({"course_id":pick()})).await{Ok(_)=>{message.set("배정했습니다.".into());refresh+=1;},Err(e)=>message.set(e)}}}},"배정하기"}p{role:"status","{message}"}}}
        h2{"배정된 수업"}if assigned.is_empty(){p{class:"muted","아직 배정된 수업이 없습니다."}}
        for course in assigned{button{class:"course-open",onclick:{let id=course["id"].as_str().unwrap_or_default().to_string();move |_|oncourse.call(id.clone())},{format!("{} · {} 단원 →",course["title"].as_str().unwrap_or_default(),course["total_units"])}}}
        if staff {h2{"참여 학생 ({students.len()})"}for student in students {p{{student["email"].as_str().unwrap_or_default()}}}}
        h2{if staff{"학생별 진도"}else{"나의 진도"}}
        for row in progress{div{class:"card student-row",span{{format!("{} · {}",row["email"].as_str().unwrap_or_default(),row["course_title"].as_str().unwrap_or_default())}}strong{{format!("{} / {} 단원",row["completed_units"],row["total_units"])}}}}
        h2{"제출 기록"}p{class:"muted","학생 컴퓨터에서 실행한 검사 결과입니다. 최근 제출 100개를 표시합니다."}
        for row in submissions{details{class:"card",summary{{format!("{} · {} · 통과 {}",row["email"].as_str().unwrap_or_default(),row["unit_id"].as_str().unwrap_or_default(),row["report"]["passed"])}}pre{{row["code"].as_str().unwrap_or_default()}}pre{{serde_json::to_string_pretty(&row["report"]).unwrap_or_default()}}}}
    }
}

#[component]
pub fn CourseAuthor(api: Api, course_id: String, onsaved: EventHandler<()>) -> Element {
    let mut document = use_signal(|| include_str!("../courses/getting-started.json").to_string());
    let mut message = use_signal(String::new);
    let mut busy = use_signal(|| false);
    let fetch_api = api.clone();
    let fetch_id = course_id.clone();
    use_future(move || {
        let api = fetch_api.clone();
        let id = fetch_id.clone();
        async move {
            if !id.is_empty() {
                match api.get::<Course>(&format!("/api/courses/{id}")).await {
                    Ok(c) => document.set(serde_json::to_string_pretty(&c).unwrap()),
                    Err(e) => message.set(e),
                }
            }
        }
    });
    let editing = !course_id.is_empty();
    rsx! {section{class:"card",h1{if editing{"내 수업 수정"}else{"공개 수업 작성"}}
        p{"수업 파일에서 챕터·단원·기본 코드·입력과 예상 출력 테스트를 작성하세요. 저장하면 수업 은행에 공개됩니다."}
        p{class:"muted","빈칸은 starter_code에 중괄호 두 개로 둘러싼 이름을 표시하고 blanks 목록에 이름을 넣습니다. checker는 학생 코드 파일 경로를 첫 번째 인자로 받는 Python 검사 코드이며 종료 상태 0이면 통과입니다."}
        if editing{p{class:"ai-note","다시 풀어야 하는 단원은 reset_completion을 true로 표시하세요. 문구 수정은 false로 둡니다. 수업 ID는 유지합니다."}}
        textarea{class:"code-editor author-editor",spellcheck:false,value:document(),oninput:move|e|document.set(e.value())}
        button{class:"primary",disabled:busy(),onclick:{let api=api.clone();let id=course_id.clone();move |_|{let api=api.clone();let id=id.clone();async move{
            busy.set(true);match Course::parse(&document()){Err(e)=>message.set(e),Ok(course)=>{let path=if id.is_empty(){"/api/courses".into()}else{format!("/api/courses/{id}")};match api.post::<Value>(&path,serde_json::to_value(course).unwrap()).await{Ok(_)=>onsaved.call(()),Err(e)=>message.set(e)}}}busy.set(false);
        }}},"저장하기"}p{class:"error",role:"status","{message}"}
    }}
}

#[component]
pub fn Learning(
    api: Api,
    classroom: String,
    course_id: String,
    student_id: String,
    can_submit: bool,
    oncompleted: EventHandler<()>,
) -> Element {
    let mut selected = use_signal(String::new);
    let mut refresh = use_signal(|| 0u64);
    let fetch_api = api.clone();
    let fetch_id = course_id.clone();
    let fetch_classroom = classroom.clone();
    let course = use_resource(move || {
        let _ = refresh();
        let api = fetch_api.clone();
        let id = fetch_id.clone();
        let classroom = fetch_classroom.clone();
        async move {
            let course = api.get::<Course>(&format!("/api/courses/{id}")).await?;
            let progress = api
                .get::<Vec<Value>>(&format!("/api/classrooms/{classroom}/progress"))
                .await?;
            Ok::<_, String>((course, progress))
        }
    });
    let result = course.read().as_ref().cloned();
    match result {
        None => rsx! {p{"수업을 불러오는 중입니다."}},
        Some(Err(e)) => rsx! {p{class:"error","{e}"}},
        Some(Ok((course, progress))) => {
            let completed: Vec<String> = progress
                .iter()
                .find(|p| {
                    p["student_id"].as_str() == Some(student_id.as_str())
                        && p["course_id"].as_str() == Some(course_id.as_str())
                })
                .and_then(|p| p["units"].as_array())
                .map(|units| {
                    units
                        .iter()
                        .filter_map(|u| u.as_str().map(str::to_string))
                        .collect()
                })
                .unwrap_or_default();
            let active = course
                .chapters
                .iter()
                .flat_map(|c| &c.units)
                .find(|u| u.id == selected())
                .unwrap_or(&course.chapters[0].units[0])
                .clone();
            rsx! {header{class:"practice-header",h1{"{course.title}"}span{{format!("완료 {} / {} 단원",completed.len(),course.total_units())}}DoctorPanel {} button{onclick:move |_|refresh+=1,"최신 수업 불러오기"}}
                div{class:"learning",details{class:"curriculum-menu",summary{"수업 목차 ▾"}nav{class:"curriculum",h2{"수업 목차"}
                    for chapter in &course.chapters{h3{{format!("{} · {}/{}",chapter.title,chapter.units.iter().filter(|u| completed.contains(&u.id)).count(),chapter.units.len())}}for unit in &chapter.units{button{class:"unit",onclick:{let id=unit.id.clone();move |_|selected.set(id.clone())},{format!("{} {}",if completed.contains(&unit.id) {"✓"}else{"○"},unit.title)}}}}
                }}for active in [active]{UnitWorkspace{key:"{active.id}-{active.revision}",api:api.clone(),classroom:classroom.clone(),course_id:course_id.clone(),student_id:student_id.clone(),unit:active,can_submit,oncompleted:move |_|{refresh+=1;oncompleted.call(());}}}}
            }
        }
    }
}

#[component]
fn UnitWorkspace(
    api: Api,
    classroom: String,
    course_id: String,
    student_id: String,
    unit: Unit,
    can_submit: bool,
    oncompleted: EventHandler<()>,
) -> Element {
    let key = format!(
        "{student_id}:{classroom}:{course_id}:{}:{}",
        unit.id, unit.revision
    );
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
            details{class:"lesson-ai",summary{"AI에게 질문하기"}AiPanel{api:api.clone(),unit:unit.clone(),code,answers,input,output,artifacts,busy,draft_key:key.clone()}}
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
        button{disabled:busy(),onclick:{let api=api.clone();move |_|{let api=api.clone();async move{busy.set(true);message.set(String::new());artifacts.set(vec![]);if let Err(e)=api.get::<Value>("/api/me").await{message.set(e);busy.set(false);return;}match run_python(&code(),&input()).await{Ok(result)=>{artifacts.set(result.artifacts);output.set(format!("{}\n{}\n{}",result.stdout,result.stderr,if result.success {"실행 완료"} else {"실행 실패"}));},Err(e)=>message.set(e)}busy.set(false);}}},"코드 실행"}
            if can_submit{button{class:"primary",disabled:busy(),onclick:{let api=api.clone();let unit=unit.clone();let classroom=classroom.clone();let course_id=course_id.clone();move |_|{let api=api.clone();let unit=unit.clone();let classroom=classroom.clone();let course_id=course_id.clone();async move{
                busy.set(true);message.set(String::new());artifacts.set(vec![]);if let Err(e)=api.get::<Value>("/api/me").await{message.set(e);busy.set(false);return;}let source=code();let blank_answers=answers();
                if !unit.blanks.is_empty()&&assemble(&unit,&blank_answers).as_deref()!=Ok(source.as_str()){message.set("지정된 빈칸을 모두 채워주세요.".into());busy.set(false);return;}
                match check_unit(&unit,&source).await{Err(e)=>message.set(e),Ok(report)=>{output.set(report.cases.iter().enumerate().map(|(i,c)|format!("테스트 {} · {}\n입력: {}\n예상: {}\n결과: {}\n{}",i+1,if c.passed {"통과"} else {"실패"},c.input.trim(),c.expected.trim(),c.stdout.trim(),c.stderr.trim())).collect::<Vec<_>>().join("\n\n"));let passed=report.passed;
                    match api.post::<Value>("/api/submissions",json!({"id":uuid::Uuid::new_v4().to_string(),"classroom_id":classroom,"course_id":course_id,"unit_id":unit.id,"revision":unit.revision,"code":source,"answers":blank_answers,"report":report})).await{Ok(_)=>{message.set(if passed{"통과했습니다. 제출과 완료 기록을 서버에 저장했습니다."}else{"검사를 통과하지 못했습니다. 제출 기록은 저장했습니다."}.into());oncompleted.call(());},Err(e)=>message.set(e)}
                }}busy.set(false);
            }}},"테스트 · 제출"}}
        }
    }}
}

#[component]
fn AiPanel(
    api: Api,
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
            button{disabled:busy(),onclick:{let api=api.clone();let unit=unit.clone();move |_|{let api=api.clone();let unit=unit.clone();async move{busy.set(true);if let Err(e)=api.get::<Value>("/api/me").await{reply.set(e);busy.set(false);return;}match connection().ask(&unit,&code(),&question(),false).await{Ok(answer)=>reply.set(answer.message),Err(e)=>reply.set(e)}busy.set(false);}}},"설명 · 힌트"}
            button{disabled:busy(),onclick:{let api=api.clone();let unit=unit.clone();let key=draft_key.clone();move |_|{let api=api.clone();let unit=unit.clone();let key=key.clone();async move{busy.set(true);if let Err(e)=api.get::<Value>("/api/me").await{reply.set(e);busy.set(false);return;}
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
