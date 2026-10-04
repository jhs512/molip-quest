#![cfg_attr(all(windows, not(debug_assertions)), windows_subsystem = "windows")]

mod ui;
use dioxus::prelude::*;
use molip_quest::Course;
use ui::Learning;

#[cfg(feature = "desktop")]
fn main() {
    // No menu bar: the app is driven from its own screens, slides have their own fullscreen button.
    dioxus::LaunchBuilder::new()
        .with_cfg(
            dioxus::desktop::Config::new()
                .with_menu(None)
                .with_window(dioxus::desktop::WindowBuilder::new().with_title("몰입 퀘스트")),
        )
        .launch(App);
}

// Mobile builds (Android view-only).
#[cfg(not(feature = "desktop"))]
fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    #[cfg(feature = "desktop")]
    {
        let window = dioxus::desktop::use_window();
        use_effect(move || place_on_screen(&window.window));
    }
    use_effect(|| {
        document::eval(include_str!("../assets/editor/editor.bundle.js"));
        // The comic SDK is an ES module, so the loader imports it from a Blob URL built from this string.
        document::eval(&format!(
            "window.__molipComicGenSource={};window.__molipMermaidSource={};{}",
            serde_json::to_string(include_str!("../assets/comics/comic-gen.js"))
                .expect("comic sdk"),
            serde_json::to_string(include_str!("../assets/comics/mermaid.min.js"))
                .expect("mermaid"),
            include_str!("../assets/comics/comics.js")
        ));
        document::eval(include_str!("../assets/speech/speech.js"));
        document::eval(include_str!("../assets/layout/split.js"));
        document::eval(include_str!("../assets/layout/toast.js"));
        document::eval(include_str!("../assets/layout/diagrams.js"));
        document::eval(include_str!("../assets/layout/interactive.js"));
        document::eval(include_str!("../assets/slides/slides.bundle.js"));
    });
    rsx! {
        if cfg!(debug_assertions) && std::env::var_os("MOLIP_DEV_LIVE").is_some() {
            style {{include_str!("../assets/fonts/fonts.css")}}
            document::Stylesheet { href: asset!("/assets/app.css") }
        } else {
            style {{include_str!("../assets/fonts/fonts.css")}}
            style {{include_str!("../assets/app.css")}}
        }
        Workspace {}
    }
}
/// Some Windows sessions hand a new window the off-screen placeholder position (-32000, -32000)
/// with a tiny size, so the app seems to start minimized and only appears after maximizing.
/// When that happens, size the window to most of the primary screen and center it.
#[cfg(feature = "desktop")]
fn place_on_screen(window: &dioxus::desktop::tao::window::Window) {
    use dioxus::desktop::tao::dpi::{PhysicalPosition, PhysicalSize};
    let off_screen = window
        .outer_position()
        .map(|p| p.x <= -30000 || p.y <= -30000)
        .unwrap_or(false);
    if !off_screen {
        return;
    }
    let Some(monitor) = window
        .primary_monitor()
        .or_else(|| window.current_monitor())
    else {
        return;
    };
    let screen = monitor.size();
    let origin = monitor.position();
    let width = screen.width * 85 / 100;
    let height = screen.height * 85 / 100;
    window.set_minimized(false);
    window.set_inner_size(PhysicalSize::new(width, height));
    window.set_outer_position(PhysicalPosition::new(
        origin.x + ((screen.width - width) / 2) as i32,
        origin.y + ((screen.height - height) / 2) as i32,
    ));
}

/// Which screen fills the window: the classroom home, the learning flow, or one gallery page.
#[derive(Clone, Copy, PartialEq)]
enum View {
    Home,
    Learning,
    Gallery(ui::GalleryKind),
}

#[component]
fn Workspace() -> Element {
    let mut view = use_signal(|| View::Home);
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
        Ok(course) => {
            rsx! { div { class: match view() { View::Home => "shell", View::Learning => "shell practice-shell", View::Gallery(_) => "shell practice-shell gallery-shell" },
                aside { class:"sidebar", div {class:"brand", "몰입 퀘스트"} h3 {"KPC 금융 데이터 분석"} p {"3일 · 20시간 · 7챕터"}
                    if ui::VIEW_ONLY { p {class:"view-only-note","Android 열람 모드 · 모든 단원과 미션이 열려 있습니다. 개념과 퀴즈를 풀고, 코딩 미션은 읽고 넘어갑니다. 코드 실행·채점은 데스크톱 앱에서 하세요."} }
                    ui::DoctorPanel {} }
                main {
                    match view() {
                        View::Learning => rsx! {
                            button {class:"classroom-back", onclick:move |_|view.set(View::Home), "← 클래스룸"}
                            Learning { course:course.clone() }
                        },
                        View::Gallery(kind) => rsx! {
                            button {class:"classroom-back", onclick:move |_|view.set(View::Home), "← 클래스룸"}
                            ui::Gallery { course:course.clone(), kind }
                        },
                        View::Home => rsx! {
                            h1 {"KPC 학습 여정"} p {"개념을 확인하고 코딩 미션과 퀴즈를 클리어하며 성장하세요."}
                            section {class:"card course-row", h2 {"{course.title}"} p {"{course.description}"}
                                p {{format!("{} 단원",course.total_units())}}
                                div {class:"course-actions",
                                    button {class:"primary",onclick:move |_|view.set(View::Learning),"학습 시작 · 이어하기"}
                                    for kind in ui::GalleryKind::ALL {
                                        button {class:"gallery-link",onclick:move |_|view.set(View::Gallery(kind)),{kind.label()}}
                                    }
                                    ui::ResetProgress {course_id:course.id.clone(),onreset:move |_|{}}
                                }
                            }
                        },
                    }
                }
            } }
        }
    }
}
