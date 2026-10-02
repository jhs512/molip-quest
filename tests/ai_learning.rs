use axum::{routing::post, Json, Router};
use molip_quest::{ai::AiConnection, runner::run_python, Course};
use serde_json::{json, Value};

#[tokio::test]
async fn learner_can_get_hint_apply_ai_code_and_execute_it_locally() {
    let app=Router::new().route("/v1/chat/completions",post(|Json(body):Json<Value>|async move {
        assert!(body["messages"][1]["content"].as_str().unwrap().contains("print(0)"));
        Json(json!({"choices":[{"message":{"content":"{\"message\":\"두 수를 더합니다.\",\"code\":\"print(2+3)\\n\"}"}}]}))
    }));
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
    let address = listener.local_addr().unwrap();
    let server = tokio::spawn(async move { axum::serve(listener, app).await.unwrap() });
    let course = Course::parse(include_str!("../courses/getting-started.json")).unwrap();
    let unit = &course.chapters[0].units[0];
    let connection = AiConnection {
        base: format!("http://{address}/v1"),
        model: "test-model".into(),
        key: String::new(),
    };
    let response = connection
        .ask(unit, "print(0)", "2와 3의 합을 출력하도록 고쳐줘", true)
        .await
        .unwrap();
    assert_eq!(response.message, "두 수를 더합니다.");
    let output = run_python(response.code.as_deref().unwrap(), "")
        .await
        .unwrap();
    assert!(output.success);
    assert_eq!(output.stdout, "5\n");
    server.abort();
}

#[tokio::test]
#[ignore = "사용자 Claude Code 로그인과 실제 연결이 필요함"]
async fn claude_cli_returns_code_that_runs_locally() {
    let course = Course::parse(include_str!("../courses/getting-started.json")).unwrap();
    let connection = AiConnection {
        base: "claude-cli".into(),
        model: "auto".into(),
        key: String::new(),
    };
    let reply = connection
        .ask(
            &course.chapters[0].units[0],
            "print(0)",
            "외부 도구를 사용하지 말고 코드만 수정해서 2와 3의 합을 출력해 주세요.",
            true,
        )
        .await
        .unwrap();
    let result = run_python(reply.code.as_deref().unwrap(), "")
        .await
        .unwrap();
    assert!(result.success);
    assert_eq!(result.stdout, "5\n");
}
