use rusqlite::{params, Connection, OptionalExtension};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Clone, Default, Deserialize, Serialize)]
pub struct Draft {
    pub code: String,
    pub answers: HashMap<String, String>,
}
fn connection() -> Result<Connection, String> {
    let connection =
        Connection::open(crate::data_dir()?.join("drafts.sqlite3")).map_err(|e| e.to_string())?;
    connection
        .execute_batch(
            "CREATE TABLE IF NOT EXISTS drafts (scope TEXT PRIMARY KEY, document TEXT NOT NULL)",
        )
        .map_err(|e| e.to_string())?;
    Ok(connection)
}
pub fn load(scope: &str) -> Result<Option<Draft>, String> {
    let document: Option<String> = connection()?
        .query_row("SELECT document FROM drafts WHERE scope=?1", [scope], |r| {
            r.get(0)
        })
        .optional()
        .map_err(|e| e.to_string())?;
    document
        .map(|d| serde_json::from_str(&d).map_err(|e| e.to_string()))
        .transpose()
}
pub fn save(scope: &str, code: &str, answers: &HashMap<String, String>) -> Result<(), String> {
    let document = serde_json::to_string(&Draft {
        code: code.into(),
        answers: answers.clone(),
    })
    .map_err(|e| e.to_string())?;
    connection()?.execute("INSERT INTO drafts(scope,document) VALUES (?1,?2) ON CONFLICT(scope) DO UPDATE SET document=excluded.document",params![scope,document]).map_err(|e|e.to_string())?;
    Ok(())
}
