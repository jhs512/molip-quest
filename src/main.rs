mod ui;
use dioxus::prelude::*;
use molip_quest::Course;
use ui::Learning;

fn main() {
    use dioxus::desktop::muda::{Menu, MenuItem, PredefinedMenuItem, Submenu};
    let menu = Menu::new();
    let window_menu = Submenu::new("Window", true);
    window_menu
        .append_items(&[
            &MenuItem::with_id("quest-fullscreen", "전체 화면 전환", true, None),
            &PredefinedMenuItem::maximize(None),
            &PredefinedMenuItem::minimize(None),
            &PredefinedMenuItem::close_window(None),
            &PredefinedMenuItem::quit(None),
        ])
        .expect("window menu");
    let edit_menu = Submenu::new("Edit", true);
    edit_menu
        .append_items(&[
            &PredefinedMenuItem::undo(None),
            &PredefinedMenuItem::redo(None),
            &PredefinedMenuItem::cut(None),
            &PredefinedMenuItem::copy(None),
            &PredefinedMenuItem::paste(None),
            &PredefinedMenuItem::select_all(None),
        ])
        .expect("edit menu");
    menu.append_items(&[&window_menu, &edit_menu])
        .expect("menu bar");
    dioxus::LaunchBuilder::new()
        .with_cfg(
            dioxus::desktop::Config::new()
                .with_menu(menu)
                .with_window(dioxus::desktop::WindowBuilder::new().with_title("몰입 퀘스트")),
        )
        .launch(App);
}
#[component]
fn App() -> Element {
    let window = dioxus::desktop::use_window();
    dioxus::desktop::use_muda_event_handler(move |event| {
        if event.id.0 == "quest-fullscreen" {
            window.set_fullscreen(window.window.fullscreen().is_none());
        }
    });
    use_effect(|| {
        document::eval(include_str!("../assets/editor/editor.bundle.js"));
    });
    rsx! {
        if cfg!(debug_assertions) && std::env::var_os("MOLIP_DEV_LIVE").is_some() {
            document::Stylesheet { href: asset!("/assets/app.css") }
        } else {
            style {{include_str!("../assets/app.css")}}
        }
        Workspace {}
    }
}
#[component]
fn Workspace() -> Element {
    let mut opened = use_signal(|| false);
    let mut ai_refresh = use_signal(|| 0u64);
    let ai_checks = use_resource(move || {
        let _ = ai_refresh();
        async move { molip_quest::doctor::inspect_ai().await }
    });
    let ai_ready = ai_checks
        .read()
        .as_ref()
        .is_some_and(|checks| !checks.is_empty() && checks.iter().all(|check| check.ready));

    let course = use_hook(|| {
        let source = if let Ok(path) = std::env::var("MOLIP_COURSE_PATH") {
            std::fs::read_to_string(path).map_err(|e| e.to_string())?
        } else {
            include_str!("../courses/getting-started.json").to_string()
        };
        Course::parse(&source)
    });
    match course {
        Err(error) => {
            rsx! { main { h1 {"수업을 불러올 수 없습니다."} p {"{error}"} ui::DoctorPanel {} } }
        }
        Ok(course) => rsx! { div { class:if opened() {"shell practice-shell"} else {"shell"},
            aside { class:"sidebar", div {class:"brand", "몰입 퀘스트"} h3 {"클래스룸"} p {"Python 학습"} ui::DoctorPanel {} }
            main {
                if opened() {
                    button {class:"classroom-back", onclick:move |_|opened.set(false), "← 클래스룸"}
                    Learning { course:course.clone() }
                } else {
                    h1 {"Python 학습 클래스룸"} p {"수업을 선택하고 바로 문제를 풀어보세요."}
                    section {class:"card course-row", h2 {"{course.title}"} p {"{course.description}"}
                        p {{format!("{} 단원",course.total_units())}}
                        section {class:"ai-requirement", h3 {"AI 연결이 필요합니다"}
                            p {"설치하고 로그인한 Claude Code로 AI와 함께 학습합니다."}
                            if let Some(checks)=ai_checks.read().as_ref() {
                                for check in checks {p {{format!("{} {} · {}",if check.ready {"✓"}else{"!"},check.name,check.detail)}}}
                            } else {p {"AI 환경을 확인하고 있습니다…"}}
                            button {onclick:move |_|ai_refresh+=1, "AI 준비 다시 확인"}
                        }
                        button {class:"primary",disabled:!ai_ready,onclick:move |_|opened.set(true),"AI와 수업 시작"}
                    }
                }
            }
        } },
    }
}
