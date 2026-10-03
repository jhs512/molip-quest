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

/// Markdown for the prompt guide: the human prompt, which of its words carry the expertise,
/// what this chapter always needs said, and how the machine version differs.
pub fn prompt_guide(unit: &Unit) -> String {
    let human = answer_prompt(unit, "");
    let why = unit
        .prompt_why
        .as_deref()
        .map(str::trim)
        .unwrap_or("이 문제에는 별도 해설이 없습니다. 입출력 조건이 곧 명세입니다.");
    let chapter = unit
        .expertise
        .as_ref()
        .map(|e| {
            format!(
                "## 이 단원에서 AI에게 꼭 말해야 하는 것\n\n{}\n\n{}",
                e.principles
                    .iter()
                    .map(|p| format!("- {p}"))
                    .collect::<Vec<_>>()
                    .join("\n"),
                e.why.trim()
            )
        })
        .unwrap_or_default();
    format!(
        "## 인간 버전 프롬프트\n\n```text\n{human}\n```\n\n\
## 이 프롬프트의 단어들\n\n{why}\n\n\
{chapter}\n\n\
## 짧게 쓰는 요령\n\n\
- **도구 이름**을 먼저 부릅니다. \"파이썬\", \"pandas\", \"scikit-learn\"이 한 단어로 어휘와 기본값을 정합니다.\n\
- **들어오는 것과 나가는 것**을 적습니다. 입력 형식, 결과 변수 이름, 출력 형식. 검사기는 이름과 글자로 읽습니다.\n\
- **방법을 알면 이름으로** 지정합니다. `groupby`, `stratify`, `temporal split`처럼 한 단어가 긴 설명을 대신하고 흔한 실수를 막습니다.\n\
- **하지 말 것**도 적습니다. \"sum() 쓰지 말고\", \"원본은 바꾸지 마\", \"False여도 그대로 둬\".\n\
- 마지막은 **\"코드만 줘\"**. 설명이 섞이면 붙여 넣을 때 깨집니다. 막혔으면 지금 코드를 그 아래에 붙여 넣으세요.\n\n\
## 기계 버전은 무엇이 다른가\n\n\
오른쪽의 기계 버전은 같은 요청을 **명세서 형식**으로 쓴 것입니다. 역할, 산출물 형식, 실행 환경, 단원 원칙, 기본·현재 코드, 입출력 예시, 검사 코드가 빠짐없이 들어가 있어 AI가 환경을 모를 때도 그대로 돌아가는 코드를 돌려줍니다. 사람이 손으로 치는 글은 아니지만, 도구가 도구에게 일을 넘길 때(자동화, 에이전트, 재현 가능한 실험)는 이 형식이 표준입니다. 인간 버전으로 원하는 답이 안 나올 때 기계 버전을 붙여 넣어 보고, 두 결과를 비교해 보세요.",
    )
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
