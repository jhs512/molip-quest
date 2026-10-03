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

/// The prompt students paste into an external AI. It is written the way a working analyst
/// briefs a tool: role, task, output contract, environment constraints, the chapter's
/// professional principles, then the exact code and acceptance criteria.
pub fn answer_prompt(unit: &Unit, code: &str) -> String {
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

/// Markdown shown in the full-screen prompt guide: why each section of the answer prompt exists.
pub fn prompt_guide(unit: &Unit) -> String {
    let chapter_why = unit
        .expertise
        .as_ref()
        .map(|e| {
            format!(
                "{}\n\n이 단원의 프롬프트에 들어가는 원칙은 다음과 같습니다.\n\n{}",
                e.why.trim(),
                e.principles
                    .iter()
                    .map(|p| format!("- {p}"))
                    .collect::<Vec<_>>()
                    .join("\n")
            )
        })
        .unwrap_or_else(|| {
            "이 문제에는 단원별 원칙이 없습니다. 입출력 조건이 곧 명세입니다.".into()
        });
    format!(
        "이 수업이 끝나면 여러분은 코드를 직접 짜기보다 AI에게 맡기는 일이 더 많을 겁니다. 그때 결과의 질을 정하는 것은 **프롬프트에 담긴 전문성**입니다. 「정답 구하는 프롬프트 복사」가 만드는 글은 분석가가 도구에게 일을 맡길 때 쓰는 틀을 그대로 따릅니다. 각 칸이 왜 있는지 알면, 수업이 끝난 뒤 자기 문제에도 같은 틀을 쓸 수 있습니다.\n\n\
## 1. 역할\n\
\"당신은 pandas·scikit-learn에 능숙한 금융 데이터 분석가입니다.\" AI는 역할에 따라 어휘와 기본값을 고릅니다. 역할을 적지 않으면 초보용 설명 코드나 다른 도구(Excel, R)의 방식이 섞여 나옵니다. 역할 지정(role prompting)은 가장 싼 품질 장치입니다.\n\n\
## 2. 과제\n\
문제 제목과 설명을 그대로 넣습니다. 요약해서 넣으면 조건이 빠집니다. 전문가는 명세를 줄이지 않고 통째로 전달합니다.\n\n\
## 3. 산출물 형식\n\
이 앱의 검사기는 `main.py` 파일 하나를 실행합니다. 설명 문장이나 Markdown 코드 펜스가 섞이면 붙여넣을 때 깨지고, 파일이 여러 개면 검사가 되지 않습니다. 산출물의 **형태를 못 박는 것**이 프롬프트의 두 번째 축입니다.\n\n\
## 4. 실행 환경과 제약\n\
AI는 환경을 모릅니다. 적지 않으면 인터넷에서 자료를 내려받거나 설치되지 않은 패키지를 가져옵니다. 패키지 목록, `data/` 폴더, 인터넷 금지, 독립 실행, `random_state=42`는 모두 \"이 앱 안에서 그대로 돌아가는 코드\"를 받기 위한 조건입니다. 재현성(reproducibility)은 실무에서도 첫 번째 요구 사항입니다.\n\n\
## 5. 이 단원의 전문 원칙\n\
{chapter_why}\n\n\
## 6. 기본 코드와 현재 코드\n\
준비 코드를 보여 주어야 AI가 자료 읽는 방식과 변수 이름을 바꾸지 않습니다. 현재 코드를 함께 주면 처음부터 다시 짜지 않고 지금 상태에서 이어 갑니다. 막힌 코드를 그대로 보여 주는 것이 가장 좋은 질문입니다.\n\n\
## 7. 입출력 예시와 검사 조건\n\
예시 몇 개와 통과 조건이 곧 **테스트 가능한 명세**입니다. 검사 코드에는 결과 변수의 이름과 자료형, 허용 오차가 적혀 있으니 AI는 그 이름을 그대로 써야 합니다. 명세 없이 \"잘 만들어 줘\"라고 하면 AI는 자기 기준으로 잘 만든 다른 것을 줍니다.\n\n\
## 받은 코드를 쓰기 전에\n\
붙여 넣고 실행한 뒤, 왜 그렇게 짰는지 한 번은 읽으세요. 특히 5번 원칙을 어긴 코드(누수, 섞인 시간, 기준 없는 점수)는 점수가 높아도 틀린 답입니다. 수업이 끝난 뒤에는 역할·과제·형식·제약·원칙·명세 여섯 칸을 자기 문제로 채워 보세요. 그것이 이 수업에서 가져가는 프롬프트입니다.",
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
