use crate::runner::TestReport;
use crate::Course;
use argon2::{
    password_hash::{PasswordHash, PasswordHasher, PasswordVerifier, SaltString},
    Argon2,
};
use axum::{
    extract::{Path, State},
    http::{HeaderMap, StatusCode},
    response::{IntoResponse, Response},
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use sqlx::{any::AnyPoolOptions, AnyPool, Row};
use std::time::{SystemTime, UNIX_EPOCH};
use uuid::Uuid;

#[derive(Clone)]
pub struct AppState {
    pub(crate) pool: AnyPool,
}

#[derive(Clone, Serialize, Deserialize, PartialEq)]
pub struct User {
    pub id: String,
    pub email: String,
    pub role: String,
}

#[derive(Debug)]
pub struct ApiError(StatusCode, String);
impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        (self.0, Json(json!({"error": self.1}))).into_response()
    }
}
impl From<sqlx::Error> for ApiError {
    fn from(error: sqlx::Error) -> Self {
        eprintln!("Database operation failed: {error}");
        Self(
            StatusCode::INTERNAL_SERVER_ERROR,
            "서버 저장 작업에 실패했습니다.".into(),
        )
    }
}
type ApiResult<T> = Result<Json<T>, ApiError>;
pub(crate) fn reject(status: StatusCode, message: &str) -> ApiError {
    ApiError(status, message.into())
}
pub(crate) fn now() -> i64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs() as i64
}
pub(crate) fn token_hash(token: &str) -> String {
    format!("{:x}", Sha256::digest(token.as_bytes()))
}
fn identifier() -> String {
    Uuid::new_v4().to_string()
}

impl AppState {
    pub async fn connect(url: &str) -> Result<Self, sqlx::Error> {
        sqlx::any::install_default_drivers();
        let pool = AnyPoolOptions::new()
            .max_connections(if url.starts_with("sqlite:") { 1 } else { 8 })
            .connect(url)
            .await?;
        for statement in [
            "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL, role TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id), expires_at BIGINT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS classrooms (id TEXT PRIMARY KEY, title TEXT NOT NULL, instructor_id TEXT NOT NULL REFERENCES users(id), invite TEXT NOT NULL UNIQUE)",
            "CREATE TABLE IF NOT EXISTS memberships (classroom_id TEXT NOT NULL REFERENCES classrooms(id), student_id TEXT NOT NULL REFERENCES users(id), PRIMARY KEY(classroom_id,student_id))",
            "CREATE TABLE IF NOT EXISTS courses (id TEXT PRIMARY KEY, author_id TEXT NOT NULL REFERENCES users(id), document TEXT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS assignments (classroom_id TEXT NOT NULL REFERENCES classrooms(id), course_id TEXT NOT NULL REFERENCES courses(id), PRIMARY KEY(classroom_id,course_id))",
            "CREATE TABLE IF NOT EXISTS submissions (id TEXT PRIMARY KEY, classroom_id TEXT NOT NULL, student_id TEXT NOT NULL, course_id TEXT NOT NULL, unit_id TEXT NOT NULL, revision BIGINT NOT NULL, code TEXT NOT NULL, report TEXT NOT NULL, created_at BIGINT NOT NULL)",
            "CREATE TABLE IF NOT EXISTS completions (classroom_id TEXT NOT NULL, student_id TEXT NOT NULL, course_id TEXT NOT NULL, unit_id TEXT NOT NULL, revision BIGINT NOT NULL, PRIMARY KEY(classroom_id,student_id,course_id,unit_id))",
            "CREATE TABLE IF NOT EXISTS unit_revisions (course_id TEXT NOT NULL, unit_id TEXT NOT NULL, revision BIGINT NOT NULL, PRIMARY KEY(course_id,unit_id))",
        ] { sqlx::query(statement).execute(&pool).await?; }
        // Retire pending GitHub authorization and its sessions; keep historical submissions.
        sqlx::query("DROP TABLE IF EXISTS github_logins")
            .execute(&pool)
            .await?;
        sqlx::query("DELETE FROM sessions WHERE user_id LIKE 'github:%'")
            .execute(&pool)
            .await?;
        Ok(Self { pool })
    }

    pub async fn provision_instructor(&self, email: &str, password: &str) -> Result<(), ApiError> {
        self.provision_staff(email, password, "instructor").await
    }

    pub async fn provision_admin(&self, email: &str, password: &str) -> Result<(), ApiError> {
        self.provision_staff(email, password, "admin").await
    }

    async fn provision_staff(
        &self,
        email: &str,
        password: &str,
        role: &str,
    ) -> Result<(), ApiError> {
        let credentials = Credentials {
            email: email.into(),
            password: password.into(),
        };
        let email = credentials.validate()?;
        if sqlx::query("SELECT id FROM users WHERE email=$1")
            .bind(&email)
            .fetch_optional(&self.pool)
            .await?
            .is_some()
        {
            return Err(reject(
                StatusCode::CONFLICT,
                "이미 존재하는 계정입니다. 기존 계정의 역할을 자동 변경하지 않습니다.",
            ));
        }
        let hash = hash_password(credentials.password).await?;
        sqlx::query("INSERT INTO users (id,email,password_hash,role) VALUES ($1,$2,$3,$4)")
            .bind(identifier())
            .bind(email)
            .bind(hash)
            .bind(role)
            .execute(&self.pool)
            .await?;
        Ok(())
    }
}

pub fn router(state: AppState) -> Router {
    Router::new()
        .route(
            "/join/{invite}",
            get(|| async { axum::response::Html(include_str!("../assets/join.html")) }),
        )
        .route(
            "/api/health",
            get(|| async { Json(json!({"online":true})) }),
        )
        .route("/api/register", post(register))
        .route("/api/login", post(login))
        .route("/api/logout", post(logout))
        .route("/api/me", get(me))
        .route(
            "/api/classrooms",
            post(create_classroom).get(list_classrooms),
        )
        .route("/api/join", post(join_classroom))
        .route("/api/classrooms/{id}/students", get(classroom_students))
        .route("/api/courses", post(create_course).get(list_courses))
        .route("/api/courses/{id}", get(get_course).post(update_course))
        .route("/api/classrooms/{id}/assign", post(assign_course))
        .route("/api/classrooms/{id}/courses", get(assigned_courses))
        .route("/api/submissions", post(submit))
        .route("/api/classrooms/{id}/submissions", get(submissions))
        .route("/api/classrooms/{id}/progress", get(progress))
        .with_state(state)
}

#[derive(Deserialize)]
struct Credentials {
    email: String,
    password: String,
}
impl Credentials {
    fn validate(&self) -> Result<String, ApiError> {
        let email = self.email.trim().to_lowercase();
        if !email.contains('@')
            || email.len() > 254
            || self.password.len() < 12
            || self.password.len() > 256
        {
            return Err(reject(
                StatusCode::BAD_REQUEST,
                "이메일과 12자 이상 비밀번호가 필요합니다.",
            ));
        }
        Ok(email)
    }
}
async fn hash_password(password: String) -> Result<String, ApiError> {
    tokio::task::spawn_blocking(move || {
        let salt = SaltString::encode_b64(Uuid::new_v4().as_bytes()).map_err(|_| ())?;
        Argon2::default()
            .hash_password(password.as_bytes(), &salt)
            .map(|hash| hash.to_string())
            .map_err(|_| ())
    })
    .await
    .map_err(|_| {
        reject(
            StatusCode::INTERNAL_SERVER_ERROR,
            "인증 작업에 실패했습니다.",
        )
    })?
    .map_err(|_| {
        reject(
            StatusCode::INTERNAL_SERVER_ERROR,
            "인증 작업에 실패했습니다.",
        )
    })
}
async fn register(
    State(state): State<AppState>,
    Json(credentials): Json<Credentials>,
) -> ApiResult<Value> {
    let email = credentials.validate()?;
    let hash = hash_password(credentials.password).await?;
    let result =
        sqlx::query("INSERT INTO users (id,email,password_hash,role) VALUES ($1,$2,$3,'student')")
            .bind(identifier())
            .bind(email)
            .bind(hash)
            .execute(&state.pool)
            .await;
    match result {
        Ok(_) => Ok(Json(json!({"registered":true}))),
        Err(sqlx::Error::Database(error)) if error.is_unique_violation() => {
            Err(reject(StatusCode::CONFLICT, "이미 가입된 이메일입니다."))
        }
        Err(error) => Err(error.into()),
    }
}
async fn login(
    State(state): State<AppState>,
    Json(credentials): Json<Credentials>,
) -> ApiResult<Value> {
    let email = credentials.validate()?;
    let row = sqlx::query("SELECT id,email,role,password_hash FROM users WHERE email=$1")
        .bind(email)
        .fetch_optional(&state.pool)
        .await?
        .ok_or_else(|| {
            reject(
                StatusCode::UNAUTHORIZED,
                "이메일 또는 비밀번호가 맞지 않습니다.",
            )
        })?;
    let hash: String = row.try_get("password_hash")?;
    let valid = tokio::task::spawn_blocking(move || {
        PasswordHash::new(&hash)
            .map(|parsed| {
                Argon2::default()
                    .verify_password(credentials.password.as_bytes(), &parsed)
                    .is_ok()
            })
            .unwrap_or(false)
    })
    .await
    .unwrap_or(false);
    if !valid {
        return Err(reject(
            StatusCode::UNAUTHORIZED,
            "이메일 또는 비밀번호가 맞지 않습니다.",
        ));
    }
    let user = User {
        id: row.try_get("id")?,
        email: row.try_get("email")?,
        role: row.try_get("role")?,
    };
    let token = format!("{}{}", identifier(), identifier());
    sqlx::query("INSERT INTO sessions (token_hash,user_id,expires_at) VALUES ($1,$2,$3)")
        .bind(token_hash(&token))
        .bind(&user.id)
        .bind(now() + 7 * 86400)
        .execute(&state.pool)
        .await?;
    Ok(Json(json!({"token":token,"user":user})))
}
async fn authenticated(state: &AppState, headers: &HeaderMap) -> Result<User, ApiError> {
    let token = bearer(headers)?;
    let row = sqlx::query("SELECT u.id,u.email,u.role FROM users u JOIN sessions s ON s.user_id=u.id WHERE s.token_hash=$1 AND s.expires_at>$2")
        .bind(token_hash(token)).bind(now()).fetch_optional(&state.pool).await?
        .ok_or_else(|| reject(StatusCode::UNAUTHORIZED, "다시 로그인해 주세요."))?;
    Ok(User {
        id: row.try_get("id")?,
        email: row.try_get("email")?,
        role: row.try_get("role")?,
    })
}
fn bearer(headers: &HeaderMap) -> Result<&str, ApiError> {
    headers
        .get("Authorization")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.strip_prefix("Bearer "))
        .ok_or_else(|| reject(StatusCode::UNAUTHORIZED, "로그인이 필요합니다."))
}
async fn me(State(state): State<AppState>, headers: HeaderMap) -> ApiResult<User> {
    Ok(Json(authenticated(&state, &headers).await?))
}
async fn logout(State(state): State<AppState>, headers: HeaderMap) -> ApiResult<Value> {
    let token = bearer(&headers)?;
    sqlx::query("DELETE FROM sessions WHERE token_hash=$1")
        .bind(token_hash(token))
        .execute(&state.pool)
        .await?;
    Ok(Json(json!({"logged_out":true})))
}
#[derive(Deserialize)]
struct Title {
    title: String,
}
async fn create_classroom(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(body): Json<Title>,
) -> ApiResult<Value> {
    let user = authenticated(&state, &headers).await?;
    if user.role != "instructor" {
        return Err(reject(
            StatusCode::FORBIDDEN,
            "강사만 클래스룸을 만들 수 있습니다.",
        ));
    }
    if body.title.trim().is_empty() || body.title.len() > 200 {
        return Err(reject(
            StatusCode::BAD_REQUEST,
            "클래스룸 제목이 필요합니다.",
        ));
    }
    let id = identifier();
    let invite = identifier();
    let title = body.title.trim();
    sqlx::query("INSERT INTO classrooms (id,title,instructor_id,invite) VALUES ($1,$2,$3,$4)")
        .bind(&id)
        .bind(title)
        .bind(user.id)
        .bind(&invite)
        .execute(&state.pool)
        .await?;
    Ok(Json(json!({"id":id,"title":title,"invite":invite})))
}

async fn list_classrooms(
    State(state): State<AppState>,
    headers: HeaderMap,
) -> ApiResult<Vec<Value>> {
    let user = authenticated(&state, &headers).await?;
    let rows = sqlx::query("SELECT c.id,c.title,c.instructor_id,c.invite FROM classrooms c WHERE c.instructor_id=$1 OR EXISTS (SELECT 1 FROM memberships m WHERE m.classroom_id=c.id AND m.student_id=$1) ORDER BY c.title")
        .bind(&user.id).fetch_all(&state.pool).await?;
    let mut result = Vec::new();
    for row in rows {
        let owner: String = row.try_get("instructor_id")?;
        result.push(json!({"id":row.try_get::<String,_>("id")?,"title":row.try_get::<String,_>("title")?,"invite":if owner==user.id { row.try_get::<String,_>("invite")? } else { String::new() }}));
    }
    Ok(Json(result))
}

#[derive(Deserialize)]
struct Join {
    invite: String,
}
async fn join_classroom(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(body): Json<Join>,
) -> ApiResult<Value> {
    let user = authenticated(&state, &headers).await?;
    if user.role != "student" {
        return Err(reject(
            StatusCode::FORBIDDEN,
            "학생 계정으로 참여해 주세요.",
        ));
    }
    let row = sqlx::query("SELECT id FROM classrooms WHERE invite=$1")
        .bind(body.invite.trim())
        .fetch_optional(&state.pool)
        .await?
        .ok_or_else(|| reject(StatusCode::NOT_FOUND, "가입 링크를 확인해 주세요."))?;
    let id: String = row.try_get("id")?;
    sqlx::query(
        "INSERT INTO memberships (classroom_id,student_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
    )
    .bind(&id)
    .bind(user.id)
    .execute(&state.pool)
    .await?;
    Ok(Json(json!({"classroom_id":id})))
}

async fn classroom_access(
    state: &AppState,
    user: &User,
    id: &str,
    instructor_only: bool,
) -> Result<(), ApiError> {
    let row = sqlx::query("SELECT instructor_id FROM classrooms WHERE id=$1")
        .bind(id)
        .fetch_optional(&state.pool)
        .await?
        .ok_or_else(|| reject(StatusCode::NOT_FOUND, "클래스룸을 찾을 수 없습니다."))?;
    if row.try_get::<String, _>("instructor_id")? == user.id {
        return Ok(());
    }
    if !instructor_only
        && sqlx::query("SELECT student_id FROM memberships WHERE classroom_id=$1 AND student_id=$2")
            .bind(id)
            .bind(&user.id)
            .fetch_optional(&state.pool)
            .await?
            .is_some()
    {
        return Ok(());
    }
    Err(reject(
        StatusCode::FORBIDDEN,
        "이 클래스룸에 접근할 수 없습니다.",
    ))
}

async fn classroom_students(
    State(state): State<AppState>,
    headers: HeaderMap,
    Path(id): Path<String>,
) -> ApiResult<Vec<User>> {
    let user = authenticated(&state, &headers).await?;
    classroom_access(&state, &user, &id, true).await?;
    let rows=sqlx::query("SELECT u.id,u.email,u.role FROM users u JOIN memberships m ON m.student_id=u.id WHERE m.classroom_id=$1 ORDER BY u.email").bind(id).fetch_all(&state.pool).await?;
    let mut result = Vec::new();
    for row in rows {
        result.push(User {
            id: row.try_get("id")?,
            email: row.try_get("email")?,
            role: row.try_get("role")?,
        });
    }
    Ok(Json(result))
}

async fn create_course(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(document): Json<Value>,
) -> ApiResult<Value> {
    let user = authenticated(&state, &headers).await?;
    if user.role != "instructor" && user.role != "admin" {
        return Err(reject(StatusCode::FORBIDDEN, "수업 작성 권한이 없습니다."));
    }
    let mut course =
        Course::parse(&document.to_string()).map_err(|e| reject(StatusCode::BAD_REQUEST, &e))?;
    for unit in course.chapters.iter_mut().flat_map(|c| &mut c.units) {
        unit.revision = 1;
        unit.reset_completion = false;
    }
    let mut tx = state.pool.begin().await?;
    let result = sqlx::query("INSERT INTO courses (id,author_id,document) VALUES ($1,$2,$3)")
        .bind(&course.id)
        .bind(user.id)
        .bind(serde_json::to_string(&course).unwrap())
        .execute(&mut *tx)
        .await;
    match result {
        Ok(_) => {
            for unit in course.chapters.iter().flat_map(|c| &c.units) {
                sqlx::query(
                    "INSERT INTO unit_revisions (course_id,unit_id,revision) VALUES ($1,$2,$3)",
                )
                .bind(&course.id)
                .bind(&unit.id)
                .bind(unit.revision)
                .execute(&mut *tx)
                .await?;
            }
            tx.commit().await?;
            Ok(Json(json!({"id":course.id})))
        }
        Err(sqlx::Error::Database(error)) if error.is_unique_violation() => {
            Err(reject(StatusCode::CONFLICT, "이미 존재하는 수업 ID입니다."))
        }
        Err(error) => Err(error.into()),
    }
}

async fn list_courses(State(state): State<AppState>, headers: HeaderMap) -> ApiResult<Vec<Value>> {
    authenticated(&state, &headers).await?;
    let rows = sqlx::query("SELECT id,author_id,document FROM courses ORDER BY id")
        .fetch_all(&state.pool)
        .await?;
    let mut result = Vec::new();
    for row in rows {
        let course = Course::parse(&row.try_get::<String, _>("document")?).map_err(|_| {
            reject(
                StatusCode::INTERNAL_SERVER_ERROR,
                "수업을 읽을 수 없습니다.",
            )
        })?;
        result.push(json!({"id":course.id,"title":course.title,"description":course.description,"author_id":row.try_get::<String,_>("author_id")?,"total_units":course.total_units()}));
    }
    Ok(Json(result))
}

async fn load_course(state: &AppState, id: &str) -> Result<Course, ApiError> {
    let row = sqlx::query("SELECT document FROM courses WHERE id=$1")
        .bind(id)
        .fetch_optional(&state.pool)
        .await?
        .ok_or_else(|| reject(StatusCode::NOT_FOUND, "수업을 찾을 수 없습니다."))?;
    Course::parse(&row.try_get::<String, _>("document")?).map_err(|_| {
        reject(
            StatusCode::INTERNAL_SERVER_ERROR,
            "수업을 읽을 수 없습니다.",
        )
    })
}
async fn get_course(
    State(state): State<AppState>,
    headers: HeaderMap,
    Path(id): Path<String>,
) -> ApiResult<Course> {
    authenticated(&state, &headers).await?;
    Ok(Json(load_course(&state, &id).await?))
}

async fn update_course(
    State(state): State<AppState>,
    headers: HeaderMap,
    Path(id): Path<String>,
    Json(document): Json<Value>,
) -> ApiResult<Value> {
    let user = authenticated(&state, &headers).await?;
    let row = sqlx::query("SELECT author_id,document FROM courses WHERE id=$1")
        .bind(&id)
        .fetch_optional(&state.pool)
        .await?
        .ok_or_else(|| reject(StatusCode::NOT_FOUND, "수업을 찾을 수 없습니다."))?;
    if row.try_get::<String, _>("author_id")? != user.id {
        return Err(reject(
            StatusCode::FORBIDDEN,
            "작성자만 수업을 수정할 수 있습니다.",
        ));
    }
    let old_document: String = row.try_get("document")?;
    let old = Course::parse(&old_document).map_err(|_| {
        reject(
            StatusCode::INTERNAL_SERVER_ERROR,
            "기존 수업을 읽을 수 없습니다.",
        )
    })?;
    let mut updated =
        Course::parse(&document.to_string()).map_err(|e| reject(StatusCode::BAD_REQUEST, &e))?;
    if updated.id != id {
        return Err(reject(
            StatusCode::BAD_REQUEST,
            "수업 ID는 변경할 수 없습니다.",
        ));
    }
    let mut tx = state.pool.begin().await?;
    let lock = sqlx::query("UPDATE courses SET document=document WHERE id=$1 AND document=$2")
        .bind(&id)
        .bind(&old_document)
        .execute(&mut *tx)
        .await?;
    if lock.rows_affected() != 1 {
        return Err(reject(
            StatusCode::CONFLICT,
            "다른 수정이 먼저 저장되었습니다. 다시 열어주세요.",
        ));
    }
    for unit in updated.chapters.iter_mut().flat_map(|c| &mut c.units) {
        let previous = old
            .chapters
            .iter()
            .flat_map(|c| &c.units)
            .find(|u| u.id == unit.id);
        let known =
            sqlx::query("SELECT revision FROM unit_revisions WHERE course_id=$1 AND unit_id=$2")
                .bind(&id)
                .bind(&unit.id)
                .fetch_optional(&mut *tx)
                .await?;
        let stored_revision = known.map(|r| r.try_get::<i64, _>("revision")).transpose()?;
        unit.revision = match previous {
            Some(previous) => previous.revision + if unit.reset_completion { 1 } else { 0 },
            None => stored_revision.map(|r| r + 1).unwrap_or(1),
        };
        unit.reset_completion = false;
        sqlx::query("INSERT INTO unit_revisions (course_id,unit_id,revision) VALUES ($1,$2,$3) ON CONFLICT(course_id,unit_id) DO UPDATE SET revision=excluded.revision")
            .bind(&id).bind(&unit.id).bind(unit.revision).execute(&mut *tx).await?;
    }
    sqlx::query("UPDATE courses SET document=$1 WHERE id=$2")
        .bind(serde_json::to_string(&updated).unwrap())
        .bind(&id)
        .execute(&mut *tx)
        .await?;
    tx.commit().await?;
    Ok(Json(json!({"saved":true,"id":id})))
}
#[derive(Deserialize)]
struct Assignment {
    course_id: String,
}
async fn assign_course(
    State(state): State<AppState>,
    headers: HeaderMap,
    Path(id): Path<String>,
    Json(body): Json<Assignment>,
) -> ApiResult<Value> {
    let user = authenticated(&state, &headers).await?;
    classroom_access(&state, &user, &id, true).await?;
    load_course(&state, &body.course_id).await?;
    sqlx::query(
        "INSERT INTO assignments (classroom_id,course_id) VALUES ($1,$2) ON CONFLICT DO NOTHING",
    )
    .bind(id)
    .bind(body.course_id)
    .execute(&state.pool)
    .await?;
    Ok(Json(json!({"assigned":true})))
}
async fn assigned_courses(
    State(state): State<AppState>,
    headers: HeaderMap,
    Path(id): Path<String>,
) -> ApiResult<Vec<Value>> {
    let user = authenticated(&state, &headers).await?;
    classroom_access(&state, &user, &id, false).await?;
    let rows=sqlx::query("SELECT c.id,c.document FROM courses c JOIN assignments a ON a.course_id=c.id WHERE a.classroom_id=$1 ORDER BY c.id").bind(id).fetch_all(&state.pool).await?;
    let mut result = Vec::new();
    for row in rows {
        let course = Course::parse(&row.try_get::<String, _>("document")?).map_err(|_| {
            reject(
                StatusCode::INTERNAL_SERVER_ERROR,
                "수업을 읽을 수 없습니다.",
            )
        })?;
        result
            .push(json!({"id":course.id,"title":course.title,"total_units":course.total_units()}));
    }
    Ok(Json(result))
}

#[derive(Deserialize)]
struct Submission {
    id: String,
    classroom_id: String,
    course_id: String,
    unit_id: String,
    revision: i64,
    code: String,
    report: TestReport,
    #[serde(default)]
    answers: std::collections::HashMap<String, String>,
}
async fn submit(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(body): Json<Submission>,
) -> ApiResult<Value> {
    let user = authenticated(&state, &headers).await?;
    if user.role != "student" {
        return Err(reject(
            StatusCode::FORBIDDEN,
            "학생 계정으로 제출해 주세요.",
        ));
    }
    classroom_access(&state, &user, &body.classroom_id, false).await?;
    if sqlx::query("SELECT course_id FROM assignments WHERE classroom_id=$1 AND course_id=$2")
        .bind(&body.classroom_id)
        .bind(&body.course_id)
        .fetch_optional(&state.pool)
        .await?
        .is_none()
    {
        return Err(reject(StatusCode::FORBIDDEN, "배정되지 않은 수업입니다."));
    }
    let course = load_course(&state, &body.course_id).await?;
    let unit = course
        .chapters
        .iter()
        .flat_map(|c| &c.units)
        .find(|u| u.id == body.unit_id)
        .ok_or_else(|| reject(StatusCode::NOT_FOUND, "단원을 찾을 수 없습니다."))?;
    if unit.revision != body.revision {
        return Err(reject(
            StatusCode::CONFLICT,
            "단원이 변경되었습니다. 최신 내용을 다시 열어 검사해 주세요.",
        ));
    }
    if !unit.blanks.is_empty()
        && crate::runner::assemble(unit, &body.answers)
            .map_err(|e| reject(StatusCode::BAD_REQUEST, &e))?
            != body.code
    {
        return Err(reject(
            StatusCode::BAD_REQUEST,
            "빈칸 밖의 고정 코드는 변경할 수 없습니다.",
        ));
    }
    if body.code.len() > 65536
        || body.id.is_empty()
        || body.report.cases.is_empty()
        || body.report.cases.len() > 30
        || body.report.passed != body.report.cases.iter().all(|c| c.passed)
    {
        return Err(reject(
            StatusCode::BAD_REQUEST,
            "제출 기록을 확인해 주세요.",
        ));
    }
    let document = serde_json::to_string(&course).unwrap();
    let mut tx = state.pool.begin().await?;
    let locked = sqlx::query("UPDATE courses SET document=document WHERE id=$1 AND document=$2")
        .bind(&course.id)
        .bind(document)
        .execute(&mut *tx)
        .await?;
    if locked.rows_affected() != 1 {
        return Err(reject(
            StatusCode::CONFLICT,
            "수업이 변경되었습니다. 다시 열어주세요.",
        ));
    }
    sqlx::query("INSERT INTO submissions (id,classroom_id,student_id,course_id,unit_id,revision,code,report,created_at) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)")
        .bind(&body.id).bind(&body.classroom_id).bind(&user.id).bind(&course.id).bind(&unit.id).bind(unit.revision).bind(&body.code).bind(serde_json::to_string(&body.report).unwrap()).bind(now()).execute(&mut *tx).await?;
    if body.report.passed {
        sqlx::query("INSERT INTO completions (classroom_id,student_id,course_id,unit_id,revision) VALUES ($1,$2,$3,$4,$5) ON CONFLICT(classroom_id,student_id,course_id,unit_id) DO UPDATE SET revision=excluded.revision")
        .bind(&body.classroom_id).bind(&user.id).bind(&course.id).bind(&unit.id).bind(unit.revision).execute(&mut *tx).await?;
    }
    tx.commit().await?;
    Ok(Json(json!({"saved":true,"passed":body.report.passed})))
}

async fn submissions(
    State(state): State<AppState>,
    headers: HeaderMap,
    Path(id): Path<String>,
) -> ApiResult<Vec<Value>> {
    let user = authenticated(&state, &headers).await?;
    classroom_access(&state, &user, &id, false).await?;
    let owner = sqlx::query("SELECT instructor_id FROM classrooms WHERE id=$1")
        .bind(&id)
        .fetch_one(&state.pool)
        .await?
        .try_get::<String, _>("instructor_id")?
        == user.id;
    let rows=sqlx::query("SELECT s.*,u.email FROM submissions s JOIN users u ON u.id=s.student_id WHERE s.classroom_id=$1 AND ($2='all' OR s.student_id=$2) ORDER BY s.created_at DESC,s.id DESC LIMIT 100")
        .bind(id).bind(if owner {"all".into()} else {user.id}).fetch_all(&state.pool).await?;
    let mut result = Vec::new();
    for row in rows {
        let report: Value =
            serde_json::from_str(&row.try_get::<String, _>("report")?).map_err(|_| {
                reject(
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "결과를 읽을 수 없습니다.",
                )
            })?;
        result.push(json!({"id":row.try_get::<String,_>("id")?,"student_id":row.try_get::<String,_>("student_id")?,"email":row.try_get::<String,_>("email")?,"course_id":row.try_get::<String,_>("course_id")?,"unit_id":row.try_get::<String,_>("unit_id")?,"revision":row.try_get::<i64,_>("revision")?,"code":row.try_get::<String,_>("code")?,"report":report}));
    }
    Ok(Json(result))
}

async fn progress(
    State(state): State<AppState>,
    headers: HeaderMap,
    Path(id): Path<String>,
) -> ApiResult<Vec<Value>> {
    let user = authenticated(&state, &headers).await?;
    classroom_access(&state, &user, &id, false).await?;
    let owner = sqlx::query("SELECT instructor_id FROM classrooms WHERE id=$1")
        .bind(&id)
        .fetch_one(&state.pool)
        .await?
        .try_get::<String, _>("instructor_id")?
        == user.id;
    let students=sqlx::query("SELECT u.id,u.email FROM users u JOIN memberships m ON m.student_id=u.id WHERE m.classroom_id=$1 AND ($2='all' OR u.id=$2) ORDER BY u.email").bind(&id).bind(if owner {"all".into()}else{user.id}).fetch_all(&state.pool).await?;
    let courses=sqlx::query("SELECT c.document FROM courses c JOIN assignments a ON a.course_id=c.id WHERE a.classroom_id=$1 ORDER BY c.id").bind(&id).fetch_all(&state.pool).await?;
    let mut result = Vec::new();
    for student in students {
        let student_id: String = student.try_get("id")?;
        let email: String = student.try_get("email")?;
        for row in &courses {
            let course = Course::parse(&row.try_get::<String, _>("document")?).map_err(|_| {
                reject(
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "수업을 읽을 수 없습니다.",
                )
            })?;
            let rows=sqlx::query("SELECT unit_id,revision FROM completions WHERE classroom_id=$1 AND student_id=$2 AND course_id=$3").bind(&id).bind(&student_id).bind(&course.id).fetch_all(&state.pool).await?;
            let mut completed = Vec::new();
            for row in rows {
                let unit_id: String = row.try_get("unit_id")?;
                let revision: i64 = row.try_get("revision")?;
                if course
                    .chapters
                    .iter()
                    .flat_map(|c| &c.units)
                    .any(|u| u.id == unit_id && u.revision == revision)
                {
                    completed.push(unit_id);
                }
            }
            result.push(json!({"student_id":student_id,"email":email,"course_id":course.id,"course_title":course.title,"completed_units":completed.len(),"total_units":course.total_units(),"units":completed}));
        }
    }
    Ok(Json(result))
}
