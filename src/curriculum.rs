use crate::{
    runner::{TestCaseResult, TestReport},
    Course, Unit,
};
use serde::{Deserialize, Serialize};
use std::collections::{HashMap, HashSet};

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Activity {
    pub id: String,
    pub title: String,
    #[serde(flatten)]
    pub kind: ActivityKind,
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum ActivityKind {
    Concept { body: String, check: Question },
    Coding { problem: Unit },
    Quiz { questions: Vec<Question> },
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Question {
    pub id: String,
    pub prompt: String,
    pub explanation: String,
    #[serde(flatten)]
    pub kind: QuestionKind,
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum QuestionKind {
    Choice {
        options: Vec<String>,
        correct: usize,
    },
    ShortAnswer {
        accepted: Vec<String>,
    },
}

impl Activity {
    pub fn label(&self) -> &'static str {
        match self.kind {
            ActivityKind::Concept { .. } => "개념",
            ActivityKind::Coding { .. } => "코딩 미션",
            ActivityKind::Quiz { .. } => "퀴즈",
        }
    }
    pub fn progress_unit(&self, parent: &Unit) -> Unit {
        let mut unit = match &self.kind {
            ActivityKind::Coding { problem } => problem.clone(),
            _ => parent.clone(),
        };
        unit.id = format!("{}/{}", parent.id, self.id);
        unit.title = self.title.clone();
        unit.revision = parent.revision;
        unit.activities.clear();
        unit
    }
}

pub fn normalize(answer: &str) -> String {
    answer.split_whitespace().collect::<String>().to_lowercase()
}

pub fn unlocked_units(course: &Course, completed: &HashSet<String>) -> HashSet<String> {
    let mut unlocked = HashSet::new();
    for unit in course.chapters.iter().flat_map(|c| &c.units) {
        unlocked.insert(unit.id.clone());
        if !completed.contains(&unit.id) {
            break;
        }
    }
    unlocked
}

pub fn unlocked_activities(unit: &Unit, completed: &HashSet<String>) -> usize {
    unit.activities
        .iter()
        .position(|a| !completed.contains(&a.progress_unit(unit).id))
        .map(|n| n + 1)
        .unwrap_or(unit.activities.len())
}

/// The "human" answer prompt: the two to five lines a person actually types into an AI,
/// authored per problem in tools/kpc_course/prompts.py. Courses without one fall back to
/// the machine prompt.
pub fn answer_prompt(unit: &Unit, code: &str) -> String {
    match unit.prompt.as_deref() {
        Some(prompt) => prompt.trim().to_string(),
        None => machine_prompt(unit, code),
    }
}

/// The "machine" answer prompt: the same request as a compact specification. One line per
/// item, the chapter's principles, the starter code, the current code only when it differs,
/// then the acceptance criteria with the checker boilerplate stripped.
pub fn machine_prompt(unit: &Unit, code: &str) -> String {
    // Hints are written for people; the specification carries only the task itself.
    let content = unit
        .content
        .split("### 힌트")
        .next()
        .unwrap_or("")
        .replace("### 문제에서 필요한 설명\n\n", "")
        .replace("### 목표\n\n", "");
    let principles = unit
        .expertise
        .as_ref()
        .map(|e| {
            e.principles
                .iter()
                .map(|p| format!("- {p}"))
                .collect::<Vec<_>>()
                .join("\n")
        })
        .unwrap_or_else(|| "- 입출력 조건을 그대로 따른다.".into());
    let starter = unit.starter_code.trim_end();
    let current = code.trim_end();
    let current = if current.is_empty() || current == starter {
        String::new()
    } else {
        format!("\n\n현재 코드:\n{current}")
    };
    let examples = if unit.tests.is_empty() {
        String::new()
    } else {
        let cases = unit
            .tests
            .iter()
            .enumerate()
            .map(|(n, t)| {
                let input = t.input.trim_end();
                format!(
                    "예제 {}: 입력 {} → 출력 {}",
                    n + 1,
                    if input.is_empty() {
                        "(없음)".to_string()
                    } else {
                        format!("{input:?}")
                    },
                    format!("{:?}", t.expected.trim_end())
                )
            })
            .collect::<Vec<_>>()
            .join("\n");
        format!("\n\n입출력 예시:\n{cases}")
    };
    let check = match unit.checker.as_deref() {
        Some(checker) => checker_summary(checker),
        None => "출력을 글자 단위로 비교(공백·줄바꿈·자릿수 포함).".to_string(),
    };
    format!(
        "역할: Python 3·pandas·scikit-learn·matplotlib에 능숙한 금융 데이터 분석가.\n\
과제: {title}\n{content}\n\n\
출력: 설명 없이 Python 파일 하나(main.py)의 전체 코드만. 코드 펜스 없음.\n\
환경: Python 3, pandas, numpy, scikit-learn, matplotlib, seaborn. 자료는 data/ 아래 제공 파일만, 인터넷 금지. 앞 문제의 변수·파일 가정 금지. 난수는 random_state=42. 준비 코드의 변수 이름과 읽는 방식은 그대로.\n\
원칙:\n{principles}\n\n\
기본 코드:\n{starter}{current}{examples}\n\n\
검사: {check}",
        title = unit.title,
        content = content.trim(),
    )
}

/// Reduce the checker source to what the AI must satisfy: the result variables it reads and
/// the assertions inside its `try` block, without the runpy boilerplate.
fn checker_summary(checker: &str) -> String {
    let mut lines = Vec::new();
    if let Some(start) = checker.find("assert set([") {
        let rest = &checker[start + "assert set([".len()..];
        if let Some(end) = rest.find("])") {
            let names: Vec<_> = rest[..end]
                .split(',')
                .map(|n| n.trim().trim_matches(|c| c == '\'' || c == '"'))
                .filter(|n| !n.is_empty())
                .collect();
            if !names.is_empty() {
                lines.push(format!("결과 변수 {} 를 만든다.", names.join(", ")));
            }
        }
    }
    if let Some(start) = checker.rfind("\ntry:\n") {
        let body = &checker[start + "\ntry:\n".len()..];
        let body = body.split("\nexcept (KeyError").next().unwrap_or(body);
        let assertions: Vec<_> = body
            .lines()
            .map(|l| l.strip_prefix("    ").unwrap_or(l))
            .filter(|l| !l.trim().is_empty())
            .collect();
        if !assertions.is_empty() {
            lines.push(format!(
                "검사 코드(s는 main.py의 변수들):\n{}",
                assertions.join("\n")
            ));
        }
    }
    if lines.is_empty() {
        "검사 코드가 결과 변수와 값을 확인한다.".to_string()
    } else {
        lines.join("\n")
    }
}

/// Markdown for the prompt guide: the human prompt and, for each word that matters, why.
pub fn prompt_guide(unit: &Unit) -> String {
    let human = answer_prompt(unit, "");
    let why = unit
        .prompt_why
        .as_deref()
        .map(str::trim)
        .unwrap_or("- 입출력 조건이 곧 명세. 그대로 적는다.");
    format!("```text\n{human}\n```\n\n## 왜 이 단어들인가\n\n{why}")
}

pub fn grade_quiz(questions: &[Question], answers: &HashMap<String, String>) -> TestReport {
    let cases: Vec<_> = questions
        .iter()
        .map(|q| {
            let answer = answers.get(&q.id).cloned().unwrap_or_default();
            let (passed, expected) = match &q.kind {
                QuestionKind::Choice { options, correct } => (
                    answer.parse::<usize>().ok() == Some(*correct),
                    options[*correct].clone(),
                ),
                QuestionKind::ShortAnswer { accepted } => (
                    !answer.trim().is_empty()
                        && accepted.iter().any(|a| normalize(a) == normalize(&answer)),
                    accepted[0].clone(),
                ),
            };
            TestCaseResult {
                input: q.prompt.clone(),
                expected,
                stdout: answer,
                stderr: q.explanation.clone(),
                passed,
                state: if passed { "passed" } else { "wrong_answer" }.into(),
            }
        })
        .collect();
    TestReport {
        passed: !cases.is_empty() && cases.iter().all(|c| c.passed),
        cases,
    }
}

pub fn validate(course: &Course) -> Result<(), String> {
    for unit in course.chapters.iter().flat_map(|c| &c.units) {
        if unit.id.contains('/') {
            return Err("단원 ID에는 /를 사용할 수 없습니다.".into());
        }
        let mut ids = HashSet::new();
        for activity in &unit.activities {
            if activity.id.trim().is_empty()
                || activity.id.contains('/')
                || activity.title.trim().is_empty()
                || !ids.insert(&activity.id)
            {
                return Err("미션 ID는 단원 내에서 고유해야 하며 제목이 필요합니다.".into());
            }
            match &activity.kind {
                ActivityKind::Concept { body, .. } if body.trim().is_empty() => {
                    return Err("개념 설명이 필요합니다.".into())
                }
                ActivityKind::Concept { check, .. } => {
                    if !matches!(check.kind, QuestionKind::ShortAnswer { .. }) {
                        return Err("개념 확인은 단답형 한 문항이어야 합니다.".into());
                    }
                    validate_questions(std::slice::from_ref(check))?;
                }
                ActivityKind::Coding { problem } => {
                    if !problem.activities.is_empty()
                        || (problem.tests.is_empty() && problem.checker.is_none())
                    {
                        return Err("코딩 문제는 독립된 코드와 검사 조건이 필요합니다.".into());
                    }
                    let mut single = course.clone();
                    single.chapters.truncate(1);
                    single.chapters[0].units = vec![problem.clone()];
                    Course::parse(&serde_json::to_string(&single).map_err(|e| e.to_string())?)?;
                }
                ActivityKind::Quiz { questions } => {
                    validate_questions(questions)?;
                }
            }
        }
    }
    Ok(())
}

fn validate_questions(questions: &[Question]) -> Result<(), String> {
    let mut question_ids = HashSet::new();
    if questions.is_empty() {
        return Err("퀴즈에는 문항이 필요합니다.".into());
    }
    for q in questions {
        if q.id.trim().is_empty()
            || q.id.contains('/')
            || !question_ids.insert(&q.id)
            || q.prompt.trim().is_empty()
            || q.explanation.trim().is_empty()
        {
            return Err("퀴즈 문항 ID, 질문과 해설을 확인하세요.".into());
        }
        match &q.kind {
            QuestionKind::Choice { options, correct }
                if options.len() < 2
                    || *correct >= options.len()
                    || options.iter().any(|o| o.trim().is_empty()) =>
            {
                return Err("객관식 보기와 정답을 확인하세요.".into())
            }
            QuestionKind::ShortAnswer { accepted }
                if accepted.is_empty() || accepted.iter().any(|a| a.trim().is_empty()) =>
            {
                return Err("주관식 인정 답안이 필요합니다.".into())
            }
            _ => (),
        }
    }
    Ok(())
}
