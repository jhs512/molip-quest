mod ui;
use dioxus::prelude::*;
use molip_quest::client::{Api, Auth};
use serde_json::{json, Value};
use ui::{ClassDetails, CourseAuthor, Learning};

fn main() {
    dioxus::LaunchBuilder::new()
        .with_cfg(
            dioxus::desktop::Config::new()
                .with_window(dioxus::desktop::WindowBuilder::new().with_title("몰입 퀘스트")),
        )
        .launch(App);
}
#[component]
fn App() -> Element {
    let mut auth = use_signal(|| None::<Auth>);
    use_future(move || async move {
        if let (Ok(email), Ok(password)) = (
            std::env::var("MOLIP_DEMO_EMAIL"),
            std::env::var("MOLIP_DEMO_PASSWORD"),
        ) {
            let api = Api::new(String::new());
            if api.base == "http://127.0.0.1:3010" {
                if let Ok(session) = api
                    .post::<Auth>("/api/login", json!({"email":email,"password":password}))
                    .await
                {
                    auth.set(Some(session));
                }
            }
        }
    });
    rsx! {style{{include_str!("../assets/app.css")}}
        if let Some(session)=auth(){Workspace{auth:session,onlogout:move |_|auth.set(None)}}
        else{Login{onlogin:move |session|auth.set(Some(session))}}
    }
}
#[component]
fn Login(onlogin: EventHandler<Auth>) -> Element {
    let mut email = use_signal(String::new);
    let mut password = use_signal(String::new);
    let mut message = use_signal(String::new);
    let mut busy = use_signal(|| false);
    rsx! {main{class:"login card",p{class:"eyebrow","내 컴퓨터에서 배우는 프로그래밍"}h1{"몰입 퀘스트"}
        p{class:"muted","로그인하고 클래스룸의 수업을 시작하세요. 인터넷 연결이 필요합니다."}
        label{"이메일" input{r#type:"email",value:email(),oninput:move|e|email.set(e.value())}}
        label{"비밀번호" input{r#type:"password",value:password(),oninput:move|e|password.set(e.value())}}
        div{class:"actions",
            button{class:"primary",disabled:busy(),onclick:move |_|async move{
                busy.set(true);message.set(String::new());
                match Api::new(String::new()).post::<Auth>("/api/login",json!({"email":email(),"password":password()})).await{Ok(session)=>onlogin.call(session),Err(e)=>message.set(e)}busy.set(false);
            },"로그인"}
            button{disabled:busy(),onclick:move |_|async move{busy.set(true);
                match Api::new(String::new()).post::<Value>("/api/register",json!({"email":email(),"password":password()})).await{Ok(_)=>message.set("학생 계정을 만들었습니다. 로그인해 주세요.".into()),Err(e)=>message.set(e)}busy.set(false);
            },"학생 가입"}
        }
        p{class:"muted","비밀번호는 12자 이상입니다. 가입 링크로 참여한 클래스룸도 같은 계정으로 로그인하면 표시됩니다."}
        p{role:"status",class:"error","{message}"}
    }}
}
#[component]
fn Workspace(auth: Auth, onlogout: EventHandler<()>) -> Element {
    let api = use_hook(|| Api::new(auth.token.clone()));
    let mut refresh = use_signal(|| 0u64);
    let mut selected_class =
        use_signal(|| std::env::var("MOLIP_DEMO_CLASSROOM").unwrap_or_default());
    let mut selected_course = use_signal(|| std::env::var("MOLIP_DEMO_COURSE").unwrap_or_default());
    let mut author = use_signal(|| None::<String>);
    let mut title = use_signal(String::new);
    let mut invite = use_signal(String::new);
    let mut message = use_signal(String::new);
    let data_api = api.clone();
    let data = use_resource(move || {
        let _ = refresh();
        let api = data_api.clone();
        async move {
            let classes = api.get::<Vec<Value>>("/api/classrooms").await?;
            let courses = api.get::<Vec<Value>>("/api/courses").await?;
            Ok::<_, String>((classes, courses))
        }
    });
    let (classes, courses) = data
        .read()
        .as_ref()
        .and_then(|r| r.as_ref().ok())
        .cloned()
        .unwrap_or_default();
    let load_error = data
        .read()
        .as_ref()
        .and_then(|r| r.as_ref().err())
        .cloned()
        .unwrap_or_default();
    let staff = auth.user.role == "instructor" || auth.user.role == "admin";
    let class_id = selected_class();
    let class_title = classes
        .iter()
        .find(|c| c["id"].as_str() == Some(&class_id))
        .and_then(|c| c["title"].as_str())
        .unwrap_or("클래스룸")
        .to_string();
    rsx! {div{class:"shell",
        aside{class:"sidebar",div{class:"brand","몰입 퀘스트"}p{class:"muted","{auth.user.email}"}span{class:"badge",if staff{"강사·관리자"}else{"학생"}}
            h3{"나의 클래스룸"}
            for classroom in &classes{button{class:"class-button",key:"{classroom}",onclick:{let id=classroom["id"].as_str().unwrap_or_default().to_string();move |_|{selected_class.set(id.clone());selected_course.set(String::new());author.set(None);}},{classroom["title"].as_str().unwrap_or_default()}}}
            div{class:"roles",
                button{onclick:move |_|{selected_class.set(String::new());selected_course.set(String::new());author.set(None);},"수업 은행"}
                if staff{button{onclick:move |_|author.set(Some(String::new())),"수업 작성"}}
                button{onclick:move |_|refresh+=1,"새로고침"}
                button{onclick:{let api=api.clone();move |_|{let api=api.clone();async move{let _=api.post::<Value>("/api/logout",json!({})).await;onlogout.call(());}}},"로그아웃"}
            }
        }
        main{
            if !load_error.is_empty(){p{role:"alert",class:"error","{load_error}"}}
            if let Some(id)=author(){CourseAuthor{key:"author-{id}",api:api.clone(),course_id:id,onsaved:move |_|{author.set(None);refresh+=1;}}}
            else if !selected_course().is_empty()&&!class_id.is_empty(){
                button{onclick:move |_|selected_course.set(String::new()),"← 클래스룸"}
                for instance in [format!("{class_id}-{}",selected_course())]{Learning{key:"{instance}",api:api.clone(),classroom:class_id.clone(),course_id:selected_course(),student_id:auth.user.id.clone(),can_submit:!staff,oncompleted:move |_|refresh+=1}}
            }else if !class_id.is_empty(){
                h1{"{class_title}"}
                if staff{if let Some(classroom)=classes.iter().find(|c|c["id"].as_str()==Some(&class_id)){label{"학생 가입 링크" input{readonly:true,value:format!("{}/join/{}",api.base,classroom["invite"].as_str().unwrap_or_default())}}}}
                for instance in [format!("{class_id}-{}",refresh())]{ClassDetails{key:"{instance}",api:api.clone(),classroom:class_id.clone(),courses:courses.clone(),staff,oncourse:move|id|selected_course.set(id)}}
            }else{
                p{class:"eyebrow","Python으로 시작하는 학습"}h1{"나의 학습 공간"}
                if auth.user.role=="instructor"{section{class:"card",h2{"클래스룸 만들기"}input{placeholder:"클래스룸 이름",value:title(),oninput:move|e|title.set(e.value())}
                    button{class:"primary",onclick:{let api=api.clone();move |_|{let api=api.clone();async move{match api.post::<Value>("/api/classrooms",json!({"title":title()})).await{Ok(c)=>{selected_class.set(c["id"].as_str().unwrap_or_default().into());refresh+=1;},Err(e)=>message.set(e)}}}},"만들기"}
                }}else if !staff{section{class:"card",h2{"클래스룸 참여"}input{placeholder:"가입 링크 또는 초대 코드",value:invite(),oninput:move|e|invite.set(e.value())}
                    button{class:"primary",onclick:{let api=api.clone();move |_|{let api=api.clone();async move{let value=invite();let code=value.trim().trim_end_matches('/').rsplit('/').next().unwrap_or_default();match api.post::<Value>("/api/join",json!({"invite":code})).await{Ok(c)=>{selected_class.set(c["classroom_id"].as_str().unwrap_or_default().into());refresh+=1;},Err(e)=>message.set(e)}}}},"참여하기"}
                }}
                p{class:"error",role:"status","{message}"}h2{"공개 수업 은행"}
                if courses.is_empty(){p{class:"muted","등록된 수업이 없습니다."}}
                for course in courses{section{class:"card course-row",key:"{course}",h3{{course["title"].as_str().unwrap_or_default()}}p{{course["description"].as_str().unwrap_or_default()}}p{class:"muted",{format!("{} 단원 · 클래스룸에 배정하여 학습합니다.",course["total_units"])}}
                    if course["author_id"].as_str()==Some(&auth.user.id){button{onclick:{let id=course["id"].as_str().unwrap_or_default().to_string();move |_|author.set(Some(id.clone()))},"내 수업 수정"}}
                }}
            }
        }
    }}
}
