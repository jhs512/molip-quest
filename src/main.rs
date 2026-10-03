#![cfg_attr(all(windows, not(debug_assertions)), windows_subsystem = "windows")]

mod ui;
use dioxus::prelude::*;
use molip_quest::Course;
use ui::Learning;

#[cfg(feature = "desktop")]
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

// Mobile builds (Android view-only) have no window menu.
#[cfg(not(feature = "desktop"))]
fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    #[cfg(feature = "desktop")]
    {
        let window = dioxus::desktop::use_window();
        dioxus::desktop::use_muda_event_handler(move |event| {
            if event.id.0 == "quest-fullscreen" {
                window.set_fullscreen(window.window.fullscreen().is_none());
            }
        });
    }
    use_effect(|| {
        document::eval(include_str!("../assets/editor/editor.bundle.js"));
        // The comic SDK is an ES module, so the loader imports it from a Blob URL built from this string.
        document::eval(&format!(
            "window.__molipComicGenSource={};{}",
            serde_json::to_string(include_str!("../assets/comics/comic-gen.js"))
                .expect("comic sdk"),
            include_str!("../assets/comics/comics.js")
        ));
        document::eval(include_str!("../assets/speech/speech.js"));
        document::eval(include_str!("../assets/layout/split.js"));
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
    let course = use_hook(|| {
        let source = if let Ok(path) = std::env::var("MOLIP_COURSE_PATH") {
            std::fs::read_to_string(path).map_err(|e| e.to_string())?
        } else {
            include_str!("../courses/kpc-finance.json").to_string()
        };
        Course::parse(&source)
    });
    match course {
        Err(error) => {
            rsx! { main { h1 {"수업을 불러올 수 없습니다."} p {"{error}"} ui::DoctorPanel {} } }
        }
        Ok(course) => rsx! { div { class:if opened() {"shell practice-shell"} else {"shell"},
            aside { class:"sidebar", div {class:"brand", "몰입 퀘스트"} h3 {"KPC 금융 데이터 분석"} p {"3일 · 20시간 · 7챕터"}
                if ui::VIEW_ONLY { p {class:"view-only-note","Android 열람 모드 · 모든 단원과 미션이 열려 있습니다. 개념과 퀴즈를 풀고, 코딩 미션은 읽고 넘어갑니다. 코드 실행·채점은 데스크톱 앱에서 하세요."} }
                ui::DoctorPanel {}
                ui::ResetProgress {course_id:course.id.clone(),onreset:move |_|{}} }
            main {
                if opened() {
                    button {class:"classroom-back", onclick:move |_|opened.set(false), "← 클래스룸"}
                    Learning { course:course.clone() }
                } else {
                    h1 {"KPC 학습 여정"} p {"개념을 확인하고 코딩 미션과 퀴즈를 클리어하며 성장하세요."}
                    section {class:"card course-row", h2 {"{course.title}"} p {"{course.description}"}
                        p {{format!("{} 단원",course.total_units())}}
                        button {class:"primary",onclick:move |_|opened.set(true),"학습 시작 · 이어하기"}
                    }
                }
            }
        } },
    }
}
