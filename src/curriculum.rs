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

/// The "machine" answer prompt: the same request written as a specification an analyst
/// hands to a tool. Role, task, output contract, environment constraints, the chapter's
/// professional principles, then the exact code and acceptance criteria.
pub fn machine_prompt(unit: &Unit, code: &str) -> String {
    let tests = if unit.tests.is_empty() {
        "입출력 예시 없음. 아래 검사 조건을 따르세요.".to_string()
    } else {
        unit.tests
            .iter()
            .enumerate()
            .map(|(n, t)| {
                format!(
                    "예제 {}\n입력:\n{}\n예상 출력:\n{}",
                    n + 1,
                    t.input.trim_end(),
                    t.expected.trim_end()
                )
            })
            .collect::<Vec<_>>()
            .join("\n\n")
    };
    let checker = unit.checker.as_deref().map(str::trim).unwrap_or(
        "입출력 예시의 출력을 글자 단위로 일치시키세요. 공백, 줄바꿈, 소수점 자릿수까지 비교합니다.",
    );
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
        .unwrap_or_else(|| "- 문제의 입출력 조건과 검사 조건을 그대로 따릅니다.".into());
    format!(
        "# 역할\n당신은 Python 3와 pandas·scikit-learn·matplotlib에 능숙한 금융 데이터 분석가입니다. 아래 과제를 재현 가능한 단일 스크립트로 해결하세요.\n\n\
# 과제\n{title}\n\n{content}\n\n\
# 산출물 형식 (반드시 지킬 것)\n\
- 설명 없이, 바로 실행할 수 있는 Python 파일 하나(main.py)의 전체 코드만 출력합니다. 앞뒤 설명 문장과 Markdown 코드 펜스를 넣지 않습니다.\n\
- 여러 파일, Notebook, 셸 명령, 패키지 설치를 요구하지 않습니다.\n\n\
# 실행 환경과 제약\n\
- 실행 환경: Python 3, pandas, numpy, scikit-learn, matplotlib, seaborn. 표준 입력은 `input()`으로 읽습니다.\n\
- 자료: 작업 폴더의 `data/` 아래 제공 파일만 사용합니다. 인터넷 접근, 외부 다운로드, 다른 경로의 파일은 금지합니다.\n\
- 독립 실행: 앞 문제의 변수나 파일을 가정하지 않습니다. 필요한 import와 준비 코드를 모두 포함합니다.\n\
- 재현성: 난수가 필요하면 `random_state=42`로 고정해 실행할 때마다 같은 결과를 냅니다.\n\
- 준비 코드(기본 코드)의 변수 이름과 자료 읽는 방식은 그대로 두고 그 아래를 완성합니다.\n\
- 검사기가 읽는 결과 변수의 이름과 자료형을 아래 검사 조건과 정확히 맞춥니다. 출력은 글자 단위로 비교됩니다.\n\n\
# 이 단원의 전문 원칙\n{principles}\n\n\
# 기본 코드\n{starter}\n\n\
# 현재 코드\n{code}\n\n\
# 입출력 예시\n{tests}\n\n\
# 검사 조건 (결과 변수 이름과 조건은 여기서 읽으세요)\n{checker}",
        title = unit.title,
        content = unit.content.trim(),
        starter = unit.starter_code.trim_end(),
        code = code.trim_end(),
    )
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
