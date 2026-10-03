use crate::{runner::TestReport, Unit};
use rusqlite::{params, Connection};
use std::{collections::HashSet, path::Path};

pub struct LearningStore(Connection);
impl LearningStore {
    pub fn open(path: &Path) -> Result<Self, String> {
        let db = Connection::open(path).map_err(|e| e.to_string())?;
        db.execute_batch("CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, course TEXT NOT NULL, unit TEXT NOT NULL, revision INTEGER NOT NULL, code TEXT NOT NULL, report TEXT NOT NULL); CREATE TABLE IF NOT EXISTS completed (course TEXT NOT NULL, unit TEXT NOT NULL, revision INTEGER NOT NULL, PRIMARY KEY(course,unit));").map_err(|e| e.to_string())?;
        Ok(Self(db))
    }
    pub fn user_store() -> Result<Self, String> {
        let dirs = directories::ProjectDirs::from("", "MolipQuest", "MolipQuest")
            .ok_or("저장 위치를 찾을 수 없습니다.")?;
        std::fs::create_dir_all(dirs.data_local_dir()).map_err(|e| e.to_string())?;
        Self::open(&dirs.data_local_dir().join("learning.sqlite3"))
    }
    pub fn save(
        &mut self,
        course: &str,
        unit: &Unit,
        code: &str,
        report: &TestReport,
    ) -> Result<(), String> {
        if report.cases.is_empty() || report.passed != report.cases.iter().all(|case| case.passed) {
            return Err("검사 결과를 확인해 주세요.".into());
        }
        let report_json = serde_json::to_string(report).map_err(|e| e.to_string())?;
        let tx = self.0.transaction().map_err(|e| e.to_string())?;
        tx.execute(
            "INSERT INTO attempts(course,unit,revision,code,report) VALUES (?1,?2,?3,?4,?5)",
            params![course, unit.id, unit.revision, code, report_json],
        )
        .map_err(|e| e.to_string())?;
        if report.passed {
            tx.execute("INSERT INTO completed VALUES (?1,?2,?3) ON CONFLICT(course,unit) DO UPDATE SET revision=excluded.revision",params![course,unit.id,unit.revision]).map_err(|e|e.to_string())?;
        }
        tx.commit().map_err(|e| e.to_string())
    }
    pub fn completed(&self, course: &crate::Course) -> Result<HashSet<String>, String> {
        let mut statement = self
            .0
            .prepare("SELECT unit,revision FROM completed WHERE course=?1")
            .map_err(|e| e.to_string())?;
        let rows = statement
            .query_map([&course.id], |r| {
                Ok((r.get::<_, String>(0)?, r.get::<_, i64>(1)?))
            })
            .map_err(|e| e.to_string())?;
        let mut units = HashSet::new();
        for row in rows {
            let (id, revision) = row.map_err(|e| e.to_string())?;
            if course
                .chapters
                .iter()
                .flat_map(|c| &c.units)
                .any(|u| u.id == id && u.revision == revision)
            {
                units.insert(id);
            }
        }
        Ok(units)
    }
}
