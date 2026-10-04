//! "AI에게 물어보기": a tutor chat that knows the mission on screen, answered by the Gemini API.
//!
//! The current mission (every slide of a deck, a concept's text, a problem with its hint and the
//! student's code, or a quiz's questions) is sent as the system context with the chat history.
//! The API key lives in `assistant.json` next to the progress database, or in `GEMINI_API_KEY`.
use crate::curriculum::{Activity, ActivityKind, QuestionKind};
use crate::Unit;
use serde::{Deserialize, Serialize};

pub const DEFAULT_MODEL: &str = "gemini-3.8-flash";
/// Earlier defaults Google has since closed to new users; a saved settings file still naming
/// one of them is moved to the current default.
const RETIRED_MODELS: &[&str] = &["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"];

const SYSTEM: &str = "당신은 KPC 「머신러닝을 활용한 금융데이터 분석」 수업의 조교입니다. 아래 '현재 미션 내용'을 기준으로, \
코딩이 처음인 직장인 수강생의 질문에 한국어로 짧고 친절하게 답하세요.\n\
규칙:\n\
1. 미션 내용 범위 안에서 답하고, 범위를 벗어나면 그렇다고 말한 뒤 짧게만 답합니다.\n\
2. 코딩 미션의 정답 코드를 통째로 주지 말고 막힌 줄만 짚어 주거나 힌트를 줍니다. 학생이 '코드만 줘'라고 분명히 말하면 코드를 줍니다.\n\
3. 퀴즈는 정답을 바로 말하지 말고 생각할 거리를 줍니다.\n\
4. 용어는 수업에서 쓰는 말(입력 X, 정답 y, 훈련 자료/테스트 자료, 기준 모델, 누수, 하이퍼파라미터)을 그대로 씁니다.\n\
5. 답은 다섯 문장 이내로 하고, 코드는 코드 블록으로 보여 줍니다.";

/// Who answers: the Gemini API, or a CLI assistant installed on this computer.
#[derive(Clone, Copy, Debug, Default, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum Provider {
    #[default]
    Gemini,
    ClaudeCode,
    Codex,
}

impl Provider {
    pub const ALL: [Provider; 3] = [Provider::Gemini, Provider::ClaudeCode, Provider::Codex];
    pub fn id(self) -> &'static str {
        match self {
            Provider::Gemini => "gemini",
            Provider::ClaudeCode => "claude_code",
            Provider::Codex => "codex",
        }
    }
    pub fn from_id(id: &str) -> Provider {
        Provider::ALL
            .into_iter()
            .find(|p| p.id() == id)
            .unwrap_or_default()
    }
    pub fn label(self) -> &'static str {
        match self {
            Provider::Gemini => "Gemini API",
            Provider::ClaudeCode => "Claude Code (이 컴퓨터의 claude 명령)",
            Provider::Codex => "Codex CLI (이 컴퓨터의 codex 명령)",
        }
    }
}

fn default_claude_command() -> String {
    "claude".into()
}
fn default_codex_command() -> String {
    "codex".into()
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Settings {
    #[serde(default)]
    pub provider: Provider,
    #[serde(default)]
    pub api_key: String,
    #[serde(default)]
    pub model: String,
    #[serde(default = "default_claude_command")]
    pub claude_command: String,
    #[serde(default = "default_codex_command")]
    pub codex_command: String,
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            provider: Provider::Gemini,
            api_key: String::new(),
            model: String::new(),
            claude_command: default_claude_command(),
            codex_command: default_codex_command(),
        }
    }
}

impl Settings {
    fn path() -> Result<std::path::PathBuf, String> {
        Ok(crate::data_dir()?.join("assistant.json"))
    }

    /// Saved settings, with `GEMINI_API_KEY` taking precedence over the saved key.
    pub fn load() -> Settings {
        let mut settings: Settings = Self::path()
            .ok()
            .and_then(|path| std::fs::read_to_string(path).ok())
            .and_then(|text| serde_json::from_str(&text).ok())
            .unwrap_or_default();
        if let Ok(key) = std::env::var("GEMINI_API_KEY") {
            if !key.trim().is_empty() {
                settings.api_key = key.trim().to_string();
            }
        }
        if settings.model.trim().is_empty() || RETIRED_MODELS.contains(&settings.model.trim()) {
            settings.model = DEFAULT_MODEL.to_string();
        }
        if settings.claude_command.trim().is_empty() {
            settings.claude_command = default_claude_command();
        }
        if settings.codex_command.trim().is_empty() {
            settings.codex_command = default_codex_command();
        }
        settings
    }

    pub fn save(&self) -> Result<(), String> {
        let path = Self::path()?;
        if let Some(dir) = path.parent() {
            std::fs::create_dir_all(dir).map_err(|e| e.to_string())?;
        }
        let text = serde_json::to_string_pretty(self).map_err(|e| e.to_string())?;
        std::fs::write(path, text).map_err(|e| e.to_string())
    }
}

/// One chat message; `role` is "user" or "model" as the Gemini API names them.
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct Turn {
    pub role: String,
    pub text: String,
}

/// Everything the tutor should know about the mission on screen.
pub fn page_context(
    course_title: &str,
    chapter_title: &str,
    unit: &Unit,
    activity: &Activity,
    draft_code: Option<&str>,
) -> String {
    let mut out = format!(
        "수업: {course_title}\n챕터: {chapter_title}\n단원: {}\n미션({}): {}\n\n---\n\n",
        unit.title,
        activity.label(),
        activity.title
    );
    match &activity.kind {
        ActivityKind::Slides { markdown } => {
            out.push_str("(강사용 슬라이드 전체. `---`가 장 구분입니다.)\n\n");
            out.push_str(markdown);
        }
        ActivityKind::Concept { body, check } => {
            out.push_str(body);
            out.push_str("\n\n### 확인 문항\n\n");
            out.push_str(&check.prompt);
        }
        ActivityKind::Coding { problem } => {
            out.push_str(&problem.content);
            out.push_str("\n\n### 기본 코드\n\n```python\n");
            out.push_str(&problem.starter_code);
            out.push_str("\n```\n");
            if let Some(code) = draft_code
                .filter(|c| !c.trim().is_empty() && c.trim() != problem.starter_code.trim())
            {
                out.push_str("\n### 학생이 지금 쓴 코드\n\n```python\n");
                out.push_str(code);
                out.push_str("\n```\n");
            }
        }
        ActivityKind::Quiz { questions } => {
            out.push_str("(퀴즈. 정답은 알려 주지 않습니다.)\n\n");
            for (n, q) in questions.iter().enumerate() {
                out.push_str(&format!("Q{}. {}\n", n + 1, q.prompt));
                if let QuestionKind::Choice { options, .. } = &q.kind {
                    for option in options {
                        out.push_str(&format!("- {option}\n"));
                    }
                }
                out.push('\n');
            }
        }
    }
    out
}

/// Answer the latest question with the mission as context and the conversation so far.
pub async fn ask(settings: &Settings, context: &str, history: &[Turn]) -> Result<String, String> {
    match settings.provider {
        Provider::Gemini => ask_gemini(settings, context, history).await,
        Provider::ClaudeCode => {
            ask_cli(
                &settings.claude_command,
                &["-p", "--output-format", "text"],
                &transcript(context, history),
                true,
                None,
            )
            .await
        }
        Provider::Codex => {
            let out = std::env::temp_dir().join(format!("molip-codex-{}.txt", std::process::id()));
            let out_arg = out.to_string_lossy().to_string();
            ask_cli(
                &settings.codex_command,
                &["exec", "--skip-git-repo-check", "-o", &out_arg],
                &transcript(context, history),
                false,
                Some(out),
            )
            .await
        }
    }
}

/// Gemini models this key can use with generateContent, newest-looking first.
pub async fn list_models(settings: &Settings) -> Result<Vec<String>, String> {
    let key = settings.api_key.trim();
    if key.is_empty() {
        return Err("Gemini API 키가 없습니다.".into());
    }
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(30))
        .build()
        .map_err(|e| e.to_string())?;
    let value: serde_json::Value = client
        .get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200")
        .header("x-goog-api-key", key)
        .send()
        .await
        .map_err(|e| format!("모델 목록을 받지 못했습니다: {e}"))?
        .json()
        .await
        .map_err(|e| format!("모델 목록을 읽지 못했습니다: {e}"))?;
    if let Some(message) = value.pointer("/error/message").and_then(|v| v.as_str()) {
        return Err(format!("Gemini 오류: {message}"));
    }
    let names: Vec<String> = value
        .get("models")
        .and_then(|m| m.as_array())
        .map(|models| {
            models
                .iter()
                .filter(|m| {
                    m.get("supportedGenerationMethods")
                        .and_then(|v| v.as_array())
                        .is_some_and(|v| v.iter().any(|x| x.as_str() == Some("generateContent")))
                })
                .filter_map(|m| m.get("name").and_then(|n| n.as_str()))
                .map(|n| n.trim_start_matches("models/").to_string())
                .collect()
        })
        .unwrap_or_default();
    let names = chat_models(&names);
    if names.is_empty() {
        return Err("쓸 수 있는 모델이 없습니다.".into());
    }
    Ok(names)
}

/// Only text chat models (gemini-*, gemma-*), gemini first, newer versions on top.
fn chat_models(names: &[String]) -> Vec<String> {
    const NOT_CHAT: [&str; 7] = [
        "robotics",
        "tts",
        "image",
        "live",
        "audio",
        "computer-use",
        "embedding",
    ];
    let mut keep: Vec<String> = names
        .iter()
        .filter(|n| {
            (n.starts_with("gemini-") || n.starts_with("gemma-"))
                && !NOT_CHAT.iter().any(|w| n.contains(w))
        })
        .cloned()
        .collect();
    keep.sort_by(|a, b| {
        let family = |n: &str| if n.starts_with("gemini-") { 0 } else { 1 };
        family(a).cmp(&family(b)).then_with(|| b.cmp(a))
    });
    keep.dedup();
    keep
}

/// The whole exchange as one prompt for a CLI assistant.
fn transcript(context: &str, history: &[Turn]) -> String {
    let mut text = format!("{SYSTEM}\n\n## 현재 미션 내용\n\n{context}\n\n## 지금까지의 대화\n\n");
    for turn in history {
        let who = if turn.role == "user" {
            "학생"
        } else {
            "조교"
        };
        text.push_str(&format!("{who}: {}\n\n", turn.text.trim()));
    }
    text.push_str(
        "위 대화의 마지막 학생 질문에 조교로서 답하세요. 인사말이나 머리말 없이 답만 쓰세요.",
    );
    text
}

/// Run a local CLI assistant (claude or codex) with the prompt and return its answer.
async fn ask_cli(
    command: &str,
    args: &[&str],
    prompt: &str,
    via_stdin: bool,
    output_file: Option<std::path::PathBuf>,
) -> Result<String, String> {
    use std::process::Stdio;
    use tokio::io::AsyncWriteExt;
    let command = command.trim();
    if command.is_empty() {
        return Err("명령 이름이 비어 있습니다. 설정에서 적어 주세요.".into());
    }
    // npm shims on Windows are .cmd files, which only a shell resolves.
    let mut cmd = if cfg!(windows) {
        let mut c = tokio::process::Command::new("cmd");
        c.arg("/C").arg(command);
        c
    } else {
        tokio::process::Command::new(command)
    };
    cmd.args(args);
    // Windows command lines are capped near 32K characters; keep a positional prompt under it.
    let prompt_arg: String = if via_stdin {
        String::new()
    } else {
        prompt.chars().take(30_000).collect()
    };
    if !via_stdin {
        cmd.arg(&prompt_arg);
    }
    cmd.current_dir(std::env::temp_dir())
        .stdin(if via_stdin {
            Stdio::piped()
        } else {
            Stdio::null()
        })
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    #[cfg(windows)]
    cmd.creation_flags(0x0800_0000); // CREATE_NO_WINDOW
    let mut child = cmd.spawn().map_err(|e| {
        format!("'{command}' 명령을 실행하지 못했습니다: {e}. 설치되어 있고 PATH에 있는지, 설정의 명령 이름이 맞는지 확인하세요.")
    })?;
    if via_stdin {
        if let Some(mut stdin) = child.stdin.take() {
            stdin
                .write_all(prompt.as_bytes())
                .await
                .map_err(|e| format!("프롬프트를 넘기지 못했습니다: {e}"))?;
        }
    }
    let output = tokio::time::timeout(
        std::time::Duration::from_secs(240),
        child.wait_with_output(),
    )
    .await
    .map_err(|_| "4분 안에 답이 오지 않았습니다. 다시 시도해 보세요.".to_string())?
    .map_err(|e| e.to_string())?;
    let stdout = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let stderr = String::from_utf8_lossy(&output.stderr).trim().to_string();
    if !output.status.success() {
        let detail: String = if stderr.is_empty() {
            stdout.clone()
        } else {
            stderr
        }
        .chars()
        .take(500)
        .collect();
        return Err(format!("{command} 오류 ({}): {detail}", output.status));
    }
    let text = match output_file {
        Some(path) => {
            let saved = std::fs::read_to_string(&path).ok();
            let _ = std::fs::remove_file(&path);
            saved
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .unwrap_or(stdout)
        }
        None => stdout,
    };
    if text.trim().is_empty() {
        return Err(format!(
            "{command}가 빈 답을 돌려줬습니다. 터미널에서 로그인되어 있는지 확인하세요."
        ));
    }
    Ok(text)
}

/// Ask Gemini with the mission as system context and the whole conversation so far.
async fn ask_gemini(
    settings: &Settings,
    context: &str,
    history: &[Turn],
) -> Result<String, String> {
    let key = settings.api_key.trim();
    if key.is_empty() {
        return Err("Gemini API 키가 없습니다. 설정에서 키를 넣어 주세요.".into());
    }
    let model = match settings.model.trim() {
        "" => DEFAULT_MODEL,
        m => m,
    };
    let url =
        format!("https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent");
    let contents: Vec<serde_json::Value> = history
        .iter()
        .map(|turn| serde_json::json!({"role": turn.role, "parts": [{"text": turn.text}]}))
        .collect();
    let body = serde_json::json!({
        "systemInstruction": {"parts": [{"text": format!("{SYSTEM}\n\n## 현재 미션 내용\n\n{context}")}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.4}
    });
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(90))
        .build()
        .map_err(|e| e.to_string())?;
    // Google answers 503/429 when the model is busy; those usually clear within seconds,
    // so retry a few times with a growing pause before giving up.
    let mut attempt = 0;
    let (status, value) = loop {
        let response = client
            .post(&url)
            .header("x-goog-api-key", key)
            .json(&body)
            .send()
            .await
            .map_err(|e| format!("요청을 보내지 못했습니다: {e}"))?;
        let status = response.status();
        let value: serde_json::Value = response
            .json()
            .await
            .map_err(|e| format!("응답을 읽지 못했습니다: {e}"))?;
        let transient = matches!(status.as_u16(), 429 | 500 | 502 | 503 | 504);
        if transient && attempt < 3 {
            attempt += 1;
            tokio::time::sleep(std::time::Duration::from_millis(1500 * attempt)).await;
            continue;
        }
        break (status, value);
    };
    if !status.is_success() {
        let message = value
            .pointer("/error/message")
            .and_then(|v| v.as_str())
            .unwrap_or("알 수 없는 오류");
        return Err(match status.as_u16() {
            503 | 429 => "지금 Gemini가 붐빕니다. 몇 번 다시 시도했지만 답을 못 받았어요. 잠시 뒤 「다시 시도」를 눌러 주세요.".to_string(),
            404 => format!("Gemini 오류 ({status}): {message} 설정에서 모델 이름을 최신 모델로 바꿔 보세요."),
            _ => format!("Gemini 오류 ({status}): {message}"),
        });
    }
    let text = value
        .pointer("/candidates/0/content/parts")
        .and_then(|parts| parts.as_array())
        .map(|parts| {
            parts
                .iter()
                .filter_map(|part| part.get("text").and_then(|t| t.as_str()))
                .collect::<Vec<_>>()
                .join("")
        })
        .unwrap_or_default();
    if text.trim().is_empty() {
        return Err("빈 답이 왔습니다. 다시 물어보세요.".into());
    }
    Ok(text)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn model_list_keeps_only_chat_models() {
        let raw: Vec<String> = [
            "lyria-3.5",
            "nano-banana-pro-preview",
            "gemini-robotics-er-2-preview",
            "gemini-3.8-flash",
            "gemini-3.8-flash-lite",
            "gemma-4-31b-it",
            "gemini-3.5-flash-tts",
            "gemini-pro-latest",
        ]
        .iter()
        .map(|s| s.to_string())
        .collect();
        let kept = chat_models(&raw);
        assert_eq!(
            kept,
            vec![
                "gemini-pro-latest",
                "gemini-3.8-flash-lite",
                "gemini-3.8-flash",
                "gemma-4-31b-it"
            ]
        );
    }

    /// Needs a logged-in `claude` CLI on this machine: `cargo test -- --ignored claude_cli`.
    #[tokio::test]
    #[ignore]
    async fn claude_cli_answers_a_question() {
        let settings = Settings {
            provider: Provider::ClaudeCode,
            ..Settings::default()
        };
        let history = vec![Turn {
            role: "user".into(),
            text: "기준 모델이 뭐야? 한 문장으로.".into(),
        }];
        let answer = ask(
            &settings,
            "미션: 기준 모델 소개. 기준 모델은 가장 많은 답만 찍는 DummyClassifier다.",
            &history,
        )
        .await
        .unwrap();
        assert!(
            answer.contains("기준") || answer.contains("Dummy"),
            "{answer}"
        );
    }

    #[test]
    fn context_carries_every_slide_and_the_student_code() {
        let course = crate::Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        let chapter = &course.chapters[0];
        let unit = &chapter.units[0];
        let deck = &unit.activities[0];
        let text = page_context(&course.title, &chapter.title, unit, deck, None);
        assert!(text.contains("슬라이드") && text.contains("안 배워도 됩니다"));
        let problem = unit
            .activities
            .iter()
            .find(|a| matches!(a.kind, ActivityKind::Coding { .. }))
            .unwrap();
        let text = page_context(
            &course.title,
            &chapter.title,
            unit,
            problem,
            Some("print('hi')"),
        );
        assert!(text.contains("학생이 지금 쓴 코드") && text.contains("print('hi')"));
        let same = page_context(
            &course.title,
            &chapter.title,
            unit,
            problem,
            Some("# 첫 문장을 출력하세요\n"),
        );
        assert!(!same.contains("학생이 지금 쓴 코드"));
    }
}
