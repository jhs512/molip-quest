//! Server-owned GitHub device authorization. Provider tokens never reach the desktop.
use crate::server::{now, reject, token_hash, ApiError, AppState, User};
use axum::{extract::State, http::StatusCode, Json};
use serde::Deserialize;
use serde_json::{json, Value};
use sqlx::Row;
use std::time::Duration;
use uuid::Uuid;

fn client_id() -> Result<String, ApiError> {
    std::env::var("MOLIP_GITHUB_CLIENT_ID")
        .ok()
        .filter(|v| !v.trim().is_empty())
        .ok_or_else(|| {
            reject(
                StatusCode::SERVICE_UNAVAILABLE,
                "GitHub 로그인 설정이 필요합니다. 서버에 앱 Client ID를 등록해 주세요.",
            )
        })
}
fn http() -> reqwest::Client {
    reqwest::Client::builder()
        .timeout(Duration::from_secs(15))
        .user_agent("molip-quest")
        .build()
        .expect("GitHub HTTP client")
}
async fn provider(response: Result<reqwest::Response, reqwest::Error>) -> Result<Value, ApiError> {
    let response =
        response.map_err(|_| reject(StatusCode::BAD_GATEWAY, "GitHub에 연결할 수 없습니다."))?;
    if !response.status().is_success() {
        return Err(reject(
            StatusCode::BAD_GATEWAY,
            "GitHub 인증 요청을 확인해 주세요.",
        ));
    }
    response
        .json()
        .await
        .map_err(|_| reject(StatusCode::BAD_GATEWAY, "GitHub 응답을 읽을 수 없습니다."))
}
pub async fn start(State(state): State<AppState>) -> Result<Json<Value>, ApiError> {
    let id = client_id()?;
    sqlx::query("DELETE FROM github_logins WHERE expires_at<=$1")
        .bind(now())
        .execute(&state.pool)
        .await?;
    let count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM github_logins")
        .fetch_one(&state.pool)
        .await?;
    if count >= 1000 {
        return Err(reject(
            StatusCode::TOO_MANY_REQUESTS,
            "잠시 후 다시 로그인해 주세요.",
        ));
    }
    // Public profile only: no repository or private email scope.
    let data = provider(
        http()
            .post("https://github.com/login/device/code")
            .header("Accept", "application/json")
            .form(&[("client_id", id.as_str()), ("scope", "")])
            .send()
            .await,
    )
    .await?;
    let device = data["device_code"].as_str().ok_or_else(|| {
        reject(
            StatusCode::BAD_GATEWAY,
            "GitHub 앱에서 Device flow를 활성화해 주세요.",
        )
    })?;
    let code = data["user_code"].as_str().ok_or_else(|| {
        reject(
            StatusCode::BAD_GATEWAY,
            "GitHub 인증 코드를 받지 못했습니다.",
        )
    })?;
    let interval = data["interval"].as_i64().unwrap_or(5).clamp(5, 60);
    let expires = data["expires_in"].as_i64().unwrap_or(900).clamp(1, 900);
    let ticket = format!("{}{}", Uuid::new_v4(), Uuid::new_v4());
    sqlx::query("INSERT INTO github_logins (ticket_hash,device_code,expires_at,next_poll,interval_seconds) VALUES ($1,$2,$3,$4,$5)")
        .bind(token_hash(&ticket)).bind(device).bind(now()+expires).bind(now()+interval).bind(interval).execute(&state.pool).await?;
    Ok(Json(
        json!({"ticket":ticket,"user_code":code,"interval":interval,"expires_in":expires}),
    ))
}
#[derive(Deserialize)]
pub struct Poll {
    ticket: String,
}
pub async fn poll(
    State(state): State<AppState>,
    Json(body): Json<Poll>,
) -> Result<Json<Value>, ApiError> {
    let id = client_id()?;
    if body.ticket.len() != 72 {
        return Err(reject(
            StatusCode::UNAUTHORIZED,
            "로그인을 다시 시작해 주세요.",
        ));
    }
    let key = token_hash(&body.ticket);
    let row = sqlx::query("SELECT device_code,expires_at,next_poll,interval_seconds FROM github_logins WHERE ticket_hash=$1")
        .bind(&key).fetch_optional(&state.pool).await?
        .ok_or_else(|| reject(StatusCode::UNAUTHORIZED, "로그인을 다시 시작해 주세요."))?;
    let expires: i64 = row.try_get("expires_at")?;
    if expires <= now() {
        sqlx::query("DELETE FROM github_logins WHERE ticket_hash=$1")
            .bind(&key)
            .execute(&state.pool)
            .await?;
        return Err(reject(
            StatusCode::UNAUTHORIZED,
            "인증 시간이 만료되었습니다. 다시 로그인해 주세요.",
        ));
    }
    let interval: i64 = row.try_get("interval_seconds")?;
    let next: i64 = row.try_get("next_poll")?;
    if next > now() {
        return Ok(Json(json!({"pending":true,"interval":next-now()})));
    }
    // Claim each polling slot atomically, so concurrent requests cannot bypass the interval.
    let claimed =
        sqlx::query("UPDATE github_logins SET next_poll=$1 WHERE ticket_hash=$2 AND next_poll=$3")
            .bind(now() + interval)
            .bind(&key)
            .bind(next)
            .execute(&state.pool)
            .await?;
    if claimed.rows_affected() == 0 {
        return Ok(Json(json!({"pending":true,"interval":interval})));
    }
    let device: String = row.try_get("device_code")?;
    let data = provider(
        http()
            .post("https://github.com/login/oauth/access_token")
            .header("Accept", "application/json")
            .form(&[
                ("client_id", id.as_str()),
                ("device_code", device.as_str()),
                ("grant_type", "urn:ietf:params:oauth:grant-type:device_code"),
            ])
            .send()
            .await,
    )
    .await?;
    match data["error"].as_str() {
        Some("authorization_pending") => {
            return Ok(Json(json!({"pending":true,"interval":interval})))
        }
        Some("slow_down") => {
            let interval = interval + 5;
            sqlx::query(
                "UPDATE github_logins SET interval_seconds=$1,next_poll=$2 WHERE ticket_hash=$3",
            )
            .bind(interval)
            .bind(now() + interval)
            .bind(&key)
            .execute(&state.pool)
            .await?;
            return Ok(Json(json!({"pending":true,"interval":interval})));
        }
        Some(_) => {
            sqlx::query("DELETE FROM github_logins WHERE ticket_hash=$1")
                .bind(&key)
                .execute(&state.pool)
                .await?;
            return Err(reject(
                StatusCode::UNAUTHORIZED,
                "GitHub 승인이 취소되었거나 만료되었습니다. 다시 로그인해 주세요.",
            ));
        }
        None => {}
    }
    let access = data["access_token"].as_str().ok_or_else(|| {
        reject(
            StatusCode::BAD_GATEWAY,
            "GitHub 인증을 완료하지 못했습니다.",
        )
    })?;
    let profile = provider(
        http()
            .get("https://api.github.com/user")
            .bearer_auth(access)
            .send()
            .await,
    )
    .await?;
    let github_id = profile["id"].as_u64().filter(|v| *v > 0).ok_or_else(|| {
        reject(
            StatusCode::BAD_GATEWAY,
            "GitHub 계정을 확인하지 못했습니다.",
        )
    })?;
    finish(&state, &key, github_id).await
}
async fn finish(state: &AppState, key: &str, github_id: u64) -> Result<Json<Value>, ApiError> {
    // Stable provider ID, never auto-link to an email/password account or grant staff privileges.
    let user_id = format!("github:{github_id}");
    let email = format!("{github_id}@github.local");
    let token = format!("{}{}", Uuid::new_v4(), Uuid::new_v4());
    let mut tx = state.pool.begin().await?;
    let consumed = sqlx::query("DELETE FROM github_logins WHERE ticket_hash=$1 AND expires_at>$2")
        .bind(&key)
        .bind(now())
        .execute(&mut *tx)
        .await?;
    if consumed.rows_affected() != 1 {
        return Err(reject(
            StatusCode::UNAUTHORIZED,
            "로그인을 다시 시작해 주세요.",
        ));
    }
    sqlx::query("INSERT INTO users (id,email,password_hash,role) VALUES ($1,$2,'','student') ON CONFLICT(id) DO NOTHING")
        .bind(&user_id).bind(&email).execute(&mut *tx).await?;
    let row = sqlx::query("SELECT id,email,role FROM users WHERE id=$1")
        .bind(&user_id)
        .fetch_one(&mut *tx)
        .await?;
    let user = User {
        id: row.try_get("id")?,
        email: row.try_get("email")?,
        role: row.try_get("role")?,
    };
    sqlx::query("INSERT INTO sessions (token_hash,user_id,expires_at) VALUES ($1,$2,$3)")
        .bind(token_hash(&token))
        .bind(&user_id)
        .bind(now() + 7 * 86400)
        .execute(&mut *tx)
        .await?;
    tx.commit().await?;
    Ok(Json(json!({"token":token,"user":user})))
}

#[cfg(test)]
mod tests {
    use super::*;
    async fn pending(state: &AppState, ticket: &str, expires: i64) {
        sqlx::query("INSERT INTO github_logins VALUES ($1,'test-device',$2,0,5)")
            .bind(token_hash(ticket))
            .bind(expires)
            .execute(&state.pool)
            .await
            .unwrap();
    }
    #[tokio::test]
    async fn identity_is_stable_student_only_and_ticket_is_consumed() {
        let state = AppState::connect("sqlite::memory:").await.unwrap();
        pending(&state, "first", now() + 100).await;
        let first = finish(&state, &token_hash("first"), 123).await.unwrap().0;
        assert_eq!(first["user"]["role"], "student");
        assert_eq!(first["user"]["id"], "github:123");
        assert!(finish(&state, &token_hash("first"), 123).await.is_err());
        pending(&state, "second", now() + 100).await;
        let second = finish(&state, &token_hash("second"), 123).await.unwrap().0;
        assert_eq!(first["user"], second["user"]);
        assert_ne!(first["token"], second["token"]);
        let hash: String =
            sqlx::query_scalar("SELECT password_hash FROM users WHERE id='github:123'")
                .fetch_one(&state.pool)
                .await
                .unwrap();
        assert!(hash.is_empty());
        pending(&state, "expired", now() - 1).await;
        assert!(finish(&state, &token_hash("expired"), 999).await.is_err());
        let count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM users")
            .fetch_one(&state.pool)
            .await
            .unwrap();
        assert_eq!(count, 1);
    }
}
