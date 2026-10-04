//! "AI에게 물어보기": a tutor chat that knows the mission on screen, answered by a CLI assistant
//! installed on this computer (Claude Code or Codex).
//!
//! The current mission (every slide of a deck, a concept's text, a problem with its hint and the
//! student's code, or a quiz's questions) and the conversation so far become one prompt that is
//! handed to `claude -p` or `codex exec`. No API key: the CLI's own login is used. Settings live
//! in `assistant.json` next to the progress database.
use crate::curriculum::{Activity, ActivityKind, QuestionKind};
use crate::Unit;
use serde::{Deserialize, Serialize};

const SYSTEM: &str = "당신은 KPC 「머신러닝을 활용한 금융데이터 분석」 수업의 조교입니다. 아래 '현재 미션 내용'을 기준으로, \
코딩이 처음인 직장인 수강생의 질문에 한국어로 짧고 친절하게 답하세요.\n\
규칙:\n\
1. 미션 내용 범위 안에서 답하고, 범위를 벗어나면 그렇다고 말한 뒤 짧게만 답합니다.\n\
2. 코딩 미션의 정답 코드를 통째로 주지 말고 막힌 줄만 짚어 주거나 힌트를 줍니다. 학생이 '코드만 줘'라고 분명히 말하면 코드를 줍니다.\n\
3. 퀴즈는 정답을 바로 말하지 말고 생각할 거리를 줍니다.\n\
4. 용어는 수업에서 쓰는 말(입력 X, 정답 y, 훈련 자료/테스트 자료, 기준 모델, 누수, 하이퍼파라미터)을 그대로 씁니다.\n\
5. 답은 다섯 문장 이내로 하고, 코드는 코드 블록으로 보여 줍니다.";

/// Which locally installed CLI answers.
#[derive(Clone, Copy, Debug, Default, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum Provider {
    Codex,
    /// Also the fallback for settings files that name a provider that no longer exists.
    #[default]
    #[serde(other)]
    ClaudeCode,
}

impl Provider {
    pub const ALL: [Provider; 2] = [Provider::ClaudeCode, Provider::Codex];
    pub fn id(self) -> &'static str {
        match self {
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
    #[serde(default = "default_claude_command")]
    pub claude_command: String,
    #[serde(default = "default_codex_command")]
    pub codex_command: String,
}

impl Default for Settings {
    fn default() -> Self {
        Settings {
            provider: Provider::ClaudeCode,
            claude_command: default_claude_command(),
            codex_command: default_codex_command(),
        }
    }
}

impl Settings {
    fn path() -> Result<std::path::PathBuf, String> {
        Ok(crate::data_dir()?.join("assistant.json"))
    }

    pub fn load() -> Settings {
        let mut settings: Settings = Self::path()
            .ok()
            .and_then(|path| std::fs::read_to_string(path).ok())
            .and_then(|text| serde_json::from_str(&text).ok())
            .unwrap_or_default();
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

/// One chat message; `role` is "user" or "model".
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
    let prompt = transcript(context, history);
    match settings.provider {
        Provider::ClaudeCode => {
            ask_cli(
                &settings.claude_command,
                &["-p", "--output-format", "text"],
                &prompt,
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
                &prompt,
                false,
                Some(out),
            )
            .await
        }
    }
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn old_settings_files_fall_back_to_claude_code() {
        let old: Settings =
            serde_json::from_str(r#"{"provider":"gemini","api_key":"x","model":"m"}"#).unwrap();
        assert_eq!(old.provider, Provider::ClaudeCode);
        assert_eq!(old.claude_command, "claude");
    }

    /// Needs a logged-in `claude` CLI on this machine: `cargo test -- --ignored claude_cli`.
    #[tokio::test]
    #[ignore]
    async fn claude_cli_answers_a_question() {
        let settings = Settings::default();
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
