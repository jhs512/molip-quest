use molip_quest::{
    curriculum::{grade_quiz, ActivityKind},
    learning_store::LearningStore,
    Course,
};
use std::collections::HashMap;

fn concept_course() -> Course {
    Course::parse(r#"{"id":"kpc-test","title":"KPC","description":"","chapters":[{"id":"python","title":"Python","units":[{"id":"variables","title":"변수","activities":[{"id":"intro","title":"표 이해","kind":"concept","body":"행과 열로 된 표를 DataFrame이라고 부릅니다.","check":{"id":"term","prompt":"pandas 표 이름은?","explanation":"DataFrame은 행과 열로 된 표입니다.","type":"short_answer","accepted":["DataFrame","데이터프레임"]}}]}]}]}"#).unwrap()
}

#[test]
fn concept_requires_one_answer_and_accepts_korean_or_english() {
    let course = concept_course();
    let unit = &course.chapters[0].units[0];
    let activity = &unit.activities[0];
    let ActivityKind::Concept { check, .. } = &activity.kind else {
        panic!("concept")
    };
    let directory = tempfile::tempdir().unwrap();
    let path = directory.path().join("learning.sqlite3");
    let mut store = LearningStore::open(&path).unwrap();
    let progress = activity.progress_unit(unit);
    let wrong = grade_quiz(
        std::slice::from_ref(check),
        &HashMap::from([("term".into(), "Series".into())]),
    );
    store.save(&course.id, &progress, "Series", &wrong).unwrap();
    assert!(store.completed(&course).unwrap().is_empty());
    for accepted in [" DATA frame ", "데이터 프레임"] {
        let report = grade_quiz(
            std::slice::from_ref(check),
            &HashMap::from([("term".into(), accepted.into())]),
        );
        assert!(report.passed);
        store
            .save(&course.id, &progress, accepted, &report)
            .unwrap();
    }
    drop(store);
    assert!(LearningStore::open(&path)
        .unwrap()
        .completed(&course)
        .unwrap()
        .contains("variables"));
    let mut invalid = serde_json::to_value(&course).unwrap();
    invalid["chapters"][0]["units"][0]["activities"][0]
        .as_object_mut()
        .unwrap()
        .remove("check");
    assert!(Course::parse(&invalid.to_string()).is_err());
}

#[test]
fn mixed_twenty_question_quiz_retries_only_wrong_answers_after_restart() {
    use molip_quest::curriculum::{Question, QuestionKind};
    let course = concept_course();
    let unit = &course.chapters[0].units[0];
    let progress = unit.activities[0].progress_unit(unit);
    let questions: Vec<_> = (0..20)
        .map(|i| Question {
            id: format!("q{i}"),
            prompt: format!("문항 {i}"),
            explanation: "정답 해설".into(),
            kind: if i % 2 == 0 {
                QuestionKind::Choice {
                    options: vec!["맞음".into(), "틀림".into()],
                    correct: 0,
                }
            } else {
                QuestionKind::ShortAnswer {
                    accepted: vec!["DataFrame".into(), "데이터프레임".into()],
                }
            },
        })
        .collect();
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("quiz.sqlite3");
    let first: HashMap<_, _> = (0..20)
        .map(|i| {
            (
                format!("q{i}"),
                if i % 2 == 0 { "0" } else { "wrong" }.into(),
            )
        })
        .collect();
    let mut store = LearningStore::open(&path).unwrap();
    assert!(
        !store
            .save_quiz(&course.id, &progress, &questions, &first)
            .unwrap()
            .passed
    );
    assert_eq!(
        store
            .quiz_passed(&course.id, &progress, &questions)
            .unwrap()
            .len(),
        10
    );
    drop(store);
    let mut store = LearningStore::open(&path).unwrap();
    let second: HashMap<_, _> = (0..20)
        .filter(|i| i % 2 == 1)
        .map(|i| (format!("q{i}"), " DATA frame ".into()))
        .collect();
    assert!(
        store
            .save_quiz(&course.id, &progress, &questions, &second)
            .unwrap()
            .passed
    );
    assert_eq!(
        store
            .quiz_passed(&course.id, &progress, &questions)
            .unwrap()
            .len(),
        20
    );
    assert!(store.completed(&course).unwrap().contains("variables"));
    assert!(
        store
            .save_quiz(&course.id, &progress, &questions, &HashMap::new())
            .unwrap()
            .passed
    );
    let mut revised = progress.clone();
    revised.revision += 1;
    assert!(store
        .quiz_passed(&course.id, &revised, &questions)
        .unwrap()
        .is_empty());
}

#[test]
fn progress_unlocks_only_the_next_mission_and_prompt_requests_one_python_file() {
    use molip_quest::curriculum::{answer_prompt, unlocked_activities, unlocked_units};
    use std::collections::HashSet;
    let mut course = concept_course();
    let mut second = course.chapters[0].units[0].clone();
    second.id = "next-unit".into();
    course.chapters[0].units.push(second);
    assert_eq!(
        unlocked_units(&course, &HashSet::new()),
        HashSet::from(["variables".into()])
    );
    assert!(unlocked_units(&course, &HashSet::from(["variables".into()])).contains("next-unit"));
    let unit = &mut course.chapters[0].units[0];
    let mut second = unit.activities[0].clone();
    second.id = "next".into();
    unit.activities.push(second);
    assert_eq!(unlocked_activities(unit, &HashSet::new()), 1);
    assert_eq!(
        unlocked_activities(unit, &HashSet::from(["variables/intro".into()])),
        2
    );
    let mut problem = unit.clone();
    problem.content = "수량과 가격으로 금액을 출력하세요".into();
    problem.starter_code = "price = 10000".into();
    problem.tests = vec![molip_quest::InputOutputTest {
        input: "5".into(),
        expected: "50000".into(),
    }];
    let prompt = answer_prompt(&problem, "print(0)");
    for required in [
        "main.py",
        "설명 없이",
        "Python 파일 하나",
        "print(0)",
        "price = 10000",
        "50000",
        "수량과 가격",
    ] {
        assert!(prompt.contains(required), "missing {required}");
    }
}

#[tokio::test]
async fn every_kpc_coding_problem_passes_alone_with_its_reference_answer() {
    use molip_quest::runner::{check_unit, run_python};
    let course = Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
    assert_eq!(course.chapters.len(), 7);
    assert_eq!(course.total_units(), 20);
    let solutions: HashMap<String, String> =
        serde_json::from_str(include_str!("../courses/kpc-solutions.json")).unwrap();
    let mut checked = 0;
    for unit in course.chapters.iter().flat_map(|c| &c.units) {
        for activity in &unit.activities {
            if let ActivityKind::Coding { problem } = &activity.kind {
                let report = check_unit(problem, &solutions[&problem.id]).await.unwrap();
                assert!(
                    report.passed,
                    "{}: {}",
                    problem.id,
                    serde_json::to_string(&report).unwrap()
                );
                checked += 1;
                eprintln!("passed {}", problem.id);
            }
        }
    }
    assert_eq!(checked, 93);
    let changed=run_python("from pathlib import Path\nPath('data/titanic.csv').write_text('corrupted')\nPath('previous.txt').write_text('state')\nprint('changed')"," ").await.unwrap();
    assert!(changed.success);
    let clean=run_python("from pathlib import Path\nimport pandas as pd\nassert not Path('previous.txt').exists()\nassert pd.read_csv('data/titanic.csv').shape==(1309,14)\nprint('fresh')","").await.unwrap();
    assert!(clean.success, "{}", clean.stderr);
    assert_eq!(clean.stdout.trim(), "fresh");
}

#[test]
fn kpc_units_use_varied_sequences_including_repeated_concepts_and_problem_only_units() {
    let course = Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
    let units: Vec<_> = course.chapters.iter().flat_map(|c| &c.units).collect();
    let intro = units.iter().find(|u| u.id == "environment").unwrap();
    assert!(matches!(
        intro.activities[0].kind,
        ActivityKind::Concept { .. }
    ));
    assert!(matches!(
        intro.activities[1].kind,
        ActivityKind::Coding { .. }
    ));
    assert!(matches!(
        intro.activities[2].kind,
        ActivityKind::Concept { .. }
    ));
    let practice = units.iter().find(|u| u.id == "credit-metrics").unwrap();
    assert!(practice
        .activities
        .iter()
        .all(|a| !matches!(a.kind, ActivityKind::Concept { .. })));
    assert_eq!(
        practice
            .activities
            .iter()
            .filter(|a| matches!(a.kind, ActivityKind::Coding { .. }))
            .count(),
        5
    );
    let mut completed = std::collections::HashSet::new();
    for (index, activity) in intro.activities.iter().enumerate() {
        assert_eq!(
            molip_quest::curriculum::unlocked_activities(intro, &completed),
            index + 1
        );
        completed.insert(activity.progress_unit(intro).id);
    }
    assert_eq!(
        molip_quest::curriculum::unlocked_activities(intro, &completed),
        intro.activities.len()
    );
}

#[tokio::test]
async fn incomplete_kpc_answer_is_wrong_answer_and_does_not_clear_a_mission() {
    let course = Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
    let unit = &course.chapters[0].units[1];
    let activity = &unit.activities[1];
    let ActivityKind::Coding { problem } = &activity.kind else {
        panic!("coding")
    };
    let report = molip_quest::runner::check_unit(problem, "print('not finished')")
        .await
        .unwrap();
    assert!(!report.passed);
    assert_eq!(report.cases[0].state, "wrong_answer");
    let dir = tempfile::tempdir().unwrap();
    let mut store = LearningStore::open(&dir.path().join("learning.sqlite3")).unwrap();
    store
        .save(
            &course.id,
            &activity.progress_unit(unit),
            "print('not finished')",
            &report,
        )
        .unwrap();
    assert!(store.completed_items(&course).unwrap().is_empty());
}

#[tokio::test]
async fn sex_bar_accepts_either_group_order_but_rejects_incorrect_heights() {
    let course = Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
    let problem = course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .flat_map(|u| &u.activities)
        .find_map(|a| match &a.kind {
            ActivityKind::Coding { problem } if problem.id == "sex-bar" => Some(problem),
            _ => None,
        })
        .unwrap();
    let solutions: HashMap<String, String> =
        serde_json::from_str(include_str!("../courses/kpc-solutions.json")).unwrap();
    let reversed = solutions["sex-bar"].replace(".mean()", ".mean().sort_index(ascending=False)");
    let report = molip_quest::runner::check_unit(problem, &reversed)
        .await
        .unwrap();
    assert!(report.passed, "{}", serde_json::to_string(&report).unwrap());
    let incorrect = reversed.replace(
        "fig,ax=plt.subplots()",
        "rates.loc['male'] = 0\nfig,ax=plt.subplots()",
    );
    let report = molip_quest::runner::check_unit(problem, &incorrect)
        .await
        .unwrap();
    assert!(!report.passed);
    assert_eq!(report.cases[0].state, "wrong_answer");
}
