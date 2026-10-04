//! "AI에게 물어보기": a tutor chat that knows the mission on screen, answered by the Gemini API.
//!
//! The current mission (every slide of a deck, a concept's text, a problem with its hint and the
//! student's code, or a quiz's questions) is sent as the system context with the chat history.
//! The API key lives in `assistant.json` next to the progress database, or in `GEMINI_API_KEY`.
use crate::curriculum::{Activity, ActivityKind, QuestionKind};
use crate::Unit;
use serde::{Deserialize, Serialize};

pub const DEFAULT_MODEL: &str = "gemini-2.5-flash";

const SYSTEM: &str = "당신은 KPC 「머신러닝을 활용한 금융데이터 분석」 수업의 조교입니다. 아래 '현재 미션 내용'을 기준으로, \
코딩이 처음인 직장인 수강생의 질문에 한국어로 짧고 친절하게 답하세요.\n\
규칙:\n\
1. 미션 내용 범위 안에서 답하고, 범위를 벗어나면 그렇다고 말한 뒤 짧게만 답합니다.\n\
2. 코딩 미션의 정답 코드를 통째로 주지 말고 막힌 줄만 짚어 주거나 힌트를 줍니다. 학생이 '코드만 줘'라고 분명히 말하면 코드를 줍니다.\n\
3. 퀴즈는 정답을 바로 말하지 말고 생각할 거리를 줍니다.\n\
4. 용어는 수업에서 쓰는 말(입력 X, 정답 y, 훈련 자료/테스트 자료, 기준 모델, 누수, 하이퍼파라미터)을 그대로 씁니다.\n\
5. 답은 다섯 문장 이내로 하고, 코드는 코드 블록으로 보여 줍니다.";

#[derive(Clone, Debug, Default, Deserialize, Serialize, PartialEq)]
pub struct Settings {
    #[serde(default)]
    pub api_key: String,
    #[serde(default)]
    pub model: String,
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
        if settings.model.trim().is_empty() {
            settings.model = DEFAULT_MODEL.to_string();
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

/// Ask Gemini with the mission as system context and the whole conversation so far.
pub async fn ask(settings: &Settings, context: &str, history: &[Turn]) -> Result<String, String> {
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
    if !status.is_success() {
        let message = value
            .pointer("/error/message")
            .and_then(|v| v.as_str())
            .unwrap_or("알 수 없는 오류");
        return Err(format!("Gemini 오류 ({status}): {message}"));
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
