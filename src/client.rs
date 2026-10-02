use crate::server::User;
use serde::{de::DeserializeOwned, Deserialize, Serialize};
use serde_json::Value;
use std::time::Duration;

#[derive(Clone, PartialEq, Serialize, Deserialize)]
pub struct Auth {
    pub token: String,
    pub user: User,
}

#[derive(Clone)]
pub struct Api {
    pub base: String,
    pub token: String,
    client: reqwest::Client,
}
impl PartialEq for Api {
    fn eq(&self, other: &Self) -> bool {
        self.base == other.base && self.token == other.token
    }
}
impl Api {
    pub fn new(token: String) -> Self {
        Self {
            base: std::env::var("MOLIP_SERVER_URL")
                .unwrap_or_else(|_| "http://127.0.0.1:3010".into())
                .trim_end_matches('/')
                .into(),
            token,
            client: reqwest::Client::builder()
                .timeout(Duration::from_secs(20))
                .build()
                .expect("HTTP client"),
        }
    }
    pub async fn get<T: DeserializeOwned>(&self, path: &str) -> Result<T, String> {
        self.send(reqwest::Method::GET, path, None).await
    }
    pub async fn post<T: DeserializeOwned>(&self, path: &str, body: Value) -> Result<T, String> {
        self.send(reqwest::Method::POST, path, Some(body)).await
    }
    async fn send<T: DeserializeOwned>(
        &self,
        method: reqwest::Method,
        path: &str,
        body: Option<Value>,
    ) -> Result<T, String> {
        let mut request = self.client.request(method, format!("{}{path}", self.base));
        if !self.token.is_empty() {
            request = request.bearer_auth(&self.token);
        }
        if let Some(body) = body {
            request = request.json(&body);
        }
        let response = request.send().await.map_err(|_| {
            "서버에 연결할 수 없습니다. 인터넷과 서버 주소를 확인해 주세요.".to_string()
        })?;
        let status = response.status();
        let value: Value = response
            .json()
            .await
            .map_err(|_| "서버 응답을 읽을 수 없습니다.".to_string())?;
        if !status.is_success() {
            return Err(value["error"]
                .as_str()
                .unwrap_or("요청에 실패했습니다.")
                .into());
        }
        serde_json::from_value(value).map_err(|_| "서버 응답 형식을 확인해 주세요.".into())
    }
}
