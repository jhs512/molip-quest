use axum::{
    body::{to_bytes, Body},
    http::{Request, StatusCode},
};
use molip_quest::server::{router, AppState};
use molip_quest::{runner::check_unit, Course};
use serde_json::{json, Value};
use std::collections::HashMap;
use tower::ServiceExt;

#[tokio::test]
async fn provisioned_admin_can_publish_but_student_cannot_be_promoted_by_provisioning() {
    let state = AppState::connect("sqlite::memory:").await.unwrap();
    state
        .provision_admin("admin@example.test", "admin-password-123")
        .await
        .unwrap();
    let app = router(state.clone());
    let (_, login) = request(
        &app,
        "/api/login",
        json!({"email":"admin@example.test","password":"admin-password-123"}),
        None,
    )
    .await;
    assert_eq!(login["user"]["role"], "admin");
    let course: Value =
        serde_json::from_str(include_str!("../courses/getting-started.json")).unwrap();
    assert_eq!(
        request(&app, "/api/courses", course, login["token"].as_str())
            .await
            .0,
        StatusCode::OK
    );
    request(
        &app,
        "/api/register",
        json!({"email":"student@example.test","password":"student-password-123"}),
        None,
    )
    .await;
    assert!(state
        .provision_admin("student@example.test", "another-password-123")
        .await
        .is_err());
    let (_, login) = request(
        &app,
        "/api/login",
        json!({"email":"student@example.test","password":"student-password-123"}),
        None,
    )
    .await;
    assert_eq!(login["user"]["role"], "student");
}

async fn request(
    app: &axum::Router,
    path: &str,
    body: Value,
    token: Option<&str>,
) -> (StatusCode, Value) {
    let mut request = Request::builder()
        .method("POST")
        .uri(path)
        .header("Content-Type", "application/json");
    if let Some(token) = token {
        request = request.header("Authorization", format!("Bearer {token}"));
    }
    let response = app
        .clone()
        .oneshot(request.body(Body::from(body.to_string())).unwrap())
        .await
        .unwrap();
    let status = response.status();
    let bytes = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    (status, serde_json::from_slice(&bytes).unwrap())
}

async fn get(app: &axum::Router, path: &str, token: &str) -> (StatusCode, Value) {
    let response = app
        .clone()
        .oneshot(
            Request::builder()
                .uri(path)
                .header("Authorization", format!("Bearer {token}"))
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    let status = response.status();
    let bytes = to_bytes(response.into_body(), 1024 * 1024).await.unwrap();
    (
        status,
        serde_json::from_slice(&bytes).unwrap_or(Value::Null),
    )
}

#[tokio::test]
async fn instructor_publishes_course_and_assigns_it_to_classroom() {
    let state = AppState::connect("sqlite::memory:").await.unwrap();
    state
        .provision_instructor("author@example.test", "author-password-123")
        .await
        .unwrap();
    let app = router(state);
    let (_, login) = request(
        &app,
        "/api/login",
        json!({"email":"author@example.test","password":"author-password-123"}),
        None,
    )
    .await;
    let token = login["token"].as_str().unwrap();
    let course: Value =
        serde_json::from_str(include_str!("../courses/getting-started.json")).unwrap();
    let (status, _) = request(&app, "/api/courses", course.clone(), Some(token)).await;
    assert_eq!(status, StatusCode::OK);
    let (_, classroom) = request(
        &app,
        "/api/classrooms",
        json!({"title":"Python 수업"}),
        Some(token),
    )
    .await;
    let path = format!(
        "/api/classrooms/{}/assign",
        classroom["id"].as_str().unwrap()
    );
    let (status, _) = request(&app, &path, json!({"course_id":course["id"]}), Some(token)).await;
    assert_eq!(status, StatusCode::OK);
    let (status, assigned) = get(
        &app,
        &format!(
            "/api/classrooms/{}/courses",
            classroom["id"].as_str().unwrap()
        ),
        token,
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(assigned[0]["id"], course["id"]);
    let (_, public) = get(&app, "/api/courses", token).await;
    assert_eq!(public[0]["id"], course["id"]);
}

#[tokio::test]
async fn student_tests_python_and_instructor_reads_saved_submission() {
    let state = AppState::connect("sqlite::memory:").await.unwrap();
    state
        .provision_instructor("teacher@example.test", "teacher-password-123")
        .await
        .unwrap();
    let app = router(state);
    let (_, teacher) = request(
        &app,
        "/api/login",
        json!({"email":"teacher@example.test","password":"teacher-password-123"}),
        None,
    )
    .await;
    let teacher_token = teacher["token"].as_str().unwrap();
    let course = json!({"id":"python-sum","title":"덧셈","description":"","chapters":[{"id":"basics","title":"기초","units":[{"id":"sum","title":"합","content":"두 정수의 합을 출력하세요.","tests":[{"input":"2 3\n","expected":"5\n"}]}]}]});
    let parsed = Course::parse(&course.to_string()).unwrap();
    let code = "a,b=map(int,input().split())\nprint(a+b)\n";
    let report = check_unit(&parsed.chapters[0].units[0], code)
        .await
        .unwrap();
    assert!(report.passed);
    assert_eq!(report.cases[0].stdout, "5\n");
    request(&app, "/api/courses", course, Some(teacher_token)).await;
    let (_, classroom) = request(
        &app,
        "/api/classrooms",
        json!({"title":"학습"}),
        Some(teacher_token),
    )
    .await;
    let id = classroom["id"].as_str().unwrap();
    request(
        &app,
        &format!("/api/classrooms/{id}/assign"),
        json!({"course_id":"python-sum"}),
        Some(teacher_token),
    )
    .await;
    request(
        &app,
        "/api/register",
        json!({"email":"student@example.test","password":"student-password-123"}),
        None,
    )
    .await;
    let (_, student) = request(
        &app,
        "/api/login",
        json!({"email":"student@example.test","password":"student-password-123"}),
        None,
    )
    .await;
    let token = student["token"].as_str().unwrap();
    request(
        &app,
        "/api/join",
        json!({"invite":classroom["invite"]}),
        Some(token),
    )
    .await;
    let body = json!({"id":"submission-one","classroom_id":id,"course_id":"python-sum","unit_id":"sum","revision":1,"code":code,"report":report});
    let (status, _) = request(&app, "/api/submissions", body.clone(), Some(token)).await;
    assert_eq!(status, StatusCode::OK);
    let (status, records) = get(
        &app,
        &format!("/api/classrooms/{id}/submissions"),
        teacher_token,
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(records[0]["code"], code);
    assert_eq!(records[0]["report"]["passed"], true);
    let (_, progress) = get(
        &app,
        &format!("/api/classrooms/{id}/progress"),
        teacher_token,
    )
    .await;
    assert_eq!(progress[0]["completed_units"], 1);
    assert_eq!(progress[0]["total_units"], 1);
    let mut edited = serde_json::to_value(&parsed).unwrap();
    edited["chapters"][0]["units"][0]["content"] = json!("설명 문구 정리");
    let (status, _) = request(
        &app,
        "/api/courses/python-sum",
        edited.clone(),
        Some(teacher_token),
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    let (_, progress) = get(
        &app,
        &format!("/api/classrooms/{id}/progress"),
        teacher_token,
    )
    .await;
    assert_eq!(progress[0]["completed_units"], 1);
    edited["chapters"][0]["units"][0]["reset_completion"] = json!(true);
    let (status, _) = request(&app, "/api/courses/python-sum", edited, Some(teacher_token)).await;
    assert_eq!(status, StatusCode::OK);
    let (_, progress) = get(
        &app,
        &format!("/api/classrooms/{id}/progress"),
        teacher_token,
    )
    .await;
    assert_eq!(progress[0]["completed_units"], 0);
    let (_, records) = get(
        &app,
        &format!("/api/classrooms/{id}/submissions"),
        teacher_token,
    )
    .await;
    assert_eq!(records.as_array().unwrap().len(), 1);
    let mut stale = body;
    stale["id"] = json!("stale-submission");
    let (status, _) = request(&app, "/api/submissions", stale, Some(token)).await;
    assert_eq!(status, StatusCode::CONFLICT);
}

#[tokio::test]
async fn blank_answers_are_composed_into_fixed_code_before_testing() {
    let course=Course::parse(&json!({"id":"blank","title":"빈칸","description":"","chapters":[{"id":"c","title":"c","units":[{"id":"u","title":"u","content":"","starter_code":"print({{answer}})\n","blanks":["answer"],"tests":[{"input":"","expected":"5"}]}]}]}).to_string()).unwrap();
    let unit = &course.chapters[0].units[0];
    let code =
        molip_quest::runner::assemble(unit, &HashMap::from([("answer".into(), "2 + 3".into())]))
            .unwrap();
    assert_eq!(code, "print(2 + 3)\n");
    assert!(check_unit(unit, &code).await.unwrap().passed);
    assert!(molip_quest::runner::assemble(
        unit,
        &HashMap::from([("other".into(), "2 + 3".into())])
    )
    .is_err());
}

#[tokio::test]
async fn student_can_register_login_but_cannot_create_a_classroom() {
    let state = AppState::connect("sqlite::memory:").await.unwrap();
    let app = router(state);
    let (status, _) = request(
        &app,
        "/api/register",
        json!({"email":"student@example.test","password":"student-password-123"}),
        None,
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    let (status, login) = request(
        &app,
        "/api/login",
        json!({"email":"student@example.test","password":"student-password-123"}),
        None,
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(login["user"]["role"], "student");
    let token = login["token"].as_str().unwrap();
    let (status, _) = request(
        &app,
        "/api/classrooms",
        json!({"title":"unauthorized"}),
        Some(token),
    )
    .await;
    assert_eq!(status, StatusCode::FORBIDDEN);
    let (status, _) = request(
        &app,
        "/api/login",
        json!({"email":"student@example.test","password":"wrong-password-123"}),
        None,
    )
    .await;
    assert_eq!(status, StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn instructor_creates_classroom_and_student_joins_once() {
    let state = AppState::connect("sqlite::memory:").await.unwrap();
    state
        .provision_instructor("teacher@example.test", "teacher-password-123")
        .await
        .unwrap();
    let app = router(state);
    let (_, teacher) = request(
        &app,
        "/api/login",
        json!({"email":"teacher@example.test","password":"teacher-password-123"}),
        None,
    )
    .await;
    let (status, classroom) = request(
        &app,
        "/api/classrooms",
        json!({"title":"Python 기초"}),
        teacher["token"].as_str(),
    )
    .await;
    assert_eq!(status, StatusCode::OK);
    assert_eq!(classroom["title"], "Python 기초");
    request(
        &app,
        "/api/register",
        json!({"email":"learner@example.test","password":"learner-password-123"}),
        None,
    )
    .await;
    let (_, student) = request(
        &app,
        "/api/login",
        json!({"email":"learner@example.test","password":"learner-password-123"}),
        None,
    )
    .await;
    for _ in 0..2 {
        let (status, joined) = request(
            &app,
            "/api/join",
            json!({"invite":classroom["invite"]}),
            student["token"].as_str(),
        )
        .await;
        assert_eq!(status, StatusCode::OK);
        assert_eq!(joined["classroom_id"], classroom["id"]);
    }
}
