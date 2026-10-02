use rusqlite::{params, Connection};
use serde::{Deserialize, Serialize};
use std::{collections::HashSet, path::Path};
pub mod ai;
pub mod client;
pub mod drafts;
pub mod runner;
pub mod server;

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Course {
    pub id: String,
    pub title: String,
    pub description: String,
    pub chapters: Vec<Chapter>,
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Chapter {
    pub id: String,
    pub title: String,
    pub units: Vec<Unit>,
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct Unit {
    pub id: String,
    pub title: String,
    pub content: String,
    #[serde(default)]
    pub starter_code: String,
    #[serde(default)]
    pub tests: Vec<InputOutputTest>,
    #[serde(default)]
    pub checker: Option<String>,
    #[serde(default)]
    pub blanks: Vec<String>,
    #[serde(default = "initial_revision")]
    pub revision: i64,
    #[serde(default)]
    pub reset_completion: bool,
}

fn initial_revision() -> i64 {
    1
}

#[derive(Clone, Deserialize, Serialize, PartialEq)]
pub struct InputOutputTest {
    pub input: String,
    pub expected: String,
}

impl Course {
    pub fn parse(source: &str) -> Result<Self, String> {
        let course: Self = serde_json::from_str(source).map_err(|e| e.to_string())?;
        if course.id.trim().is_empty()
            || course.title.trim().is_empty()
            || course.chapters.is_empty()
        {
            return Err("수업 ID, 제목과 챕터가 필요합니다.".into());
        }
        let mut chapters = HashSet::new();
        let mut units = HashSet::new();
        for chapter in &course.chapters {
            if chapter.id.trim().is_empty()
                || chapter.title.trim().is_empty()
                || !chapters.insert(&chapter.id)
                || chapter.units.is_empty()
            {
                return Err("챕터 ID는 고유해야 하며 제목과 단원이 필요합니다.".into());
            }
            for unit in &chapter.units {
                if unit.id.trim().is_empty()
                    || unit.title.trim().is_empty()
                    || !units.insert(&unit.id)
                {
                    return Err("단원 ID는 수업 내에서 고유해야 하며 제목이 필요합니다.".into());
                }
                let mut blanks = HashSet::new();
                for blank in &unit.blanks {
                    if blank.trim().is_empty()
                        || blank.contains('{')
                        || blank.contains('}')
                        || !blanks.insert(blank)
                        || !unit.starter_code.contains(&format!("{{{{{blank}}}}}"))
                    {
                        return Err("빈칸 ID와 코드 템플릿을 확인해 주세요.".into());
                    }
                }
                if unit.tests.len() > 30
                    || unit
                        .tests
                        .iter()
                        .any(|t| t.input.len() > 65536 || t.expected.len() > 65536)
                    || unit.starter_code.len() > 65536
                    || unit.checker.as_ref().is_some_and(|c| c.len() > 65536)
                {
                    return Err(
                        "코드·입출력은 64KB 이하, 테스트는 30개 이하로 작성해 주세요.".into(),
                    );
                }
            }
        }
        Ok(course)
    }

    pub fn total_units(&self) -> usize {
        self.chapters.iter().map(|c| c.units.len()).sum()
    }

    pub fn completed_units(&self, completed: &HashSet<String>) -> usize {
        self.chapters
            .iter()
            .flat_map(|c| &c.units)
            .filter(|u| completed.contains(&u.id))
            .count()
    }
}

pub struct ProgressStore(Connection);

impl ProgressStore {
    pub fn open(path: &Path) -> rusqlite::Result<Self> {
        let connection = Connection::open(path)?;
        connection.execute_batch(
            "CREATE TABLE IF NOT EXISTS unit_progress (
             classroom_id TEXT NOT NULL, student_id TEXT NOT NULL,
             course_id TEXT NOT NULL, unit_id TEXT NOT NULL,
             PRIMARY KEY(classroom_id, student_id, course_id, unit_id));",
        )?;
        Ok(Self(connection))
    }

    pub fn completed(
        &self,
        classroom: &str,
        student: &str,
        course: &str,
    ) -> rusqlite::Result<HashSet<String>> {
        let mut statement = self.0.prepare(
            "SELECT unit_id FROM unit_progress WHERE classroom_id=?1 AND student_id=?2 AND course_id=?3"
        )?;
        let rows = statement.query_map(params![classroom, student, course], |row| row.get(0))?;
        rows.collect()
    }

    pub fn set_completed(
        &self,
        classroom: &str,
        student: &str,
        course: &Course,
        unit: &str,
        completed: bool,
    ) -> Result<(), String> {
        if !course
            .chapters
            .iter()
            .flat_map(|c| &c.units)
            .any(|u| u.id == unit)
        {
            return Err("수업에 없는 단원입니다.".into());
        }
        let sql = if completed {
            "INSERT OR IGNORE INTO unit_progress VALUES (?1, ?2, ?3, ?4)"
        } else {
            "DELETE FROM unit_progress WHERE classroom_id=?1 AND student_id=?2 AND course_id=?3 AND unit_id=?4"
        };
        self.0
            .execute(sql, params![classroom, student, course.id, unit])
            .map_err(|e| e.to_string())?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn course() -> Course {
        Course::parse(include_str!("../courses/getting-started.json")).unwrap()
    }

    #[test]
    fn progress_persists_and_is_scoped_to_classroom_student_and_course() {
        let directory = tempfile::tempdir().unwrap();
        let path = directory.path().join("progress.sqlite3");
        let course = course();
        {
            let store = ProgressStore::open(&path).unwrap();
            store
                .set_completed("a", "student", &course, "choose-tool", true)
                .unwrap();
            store
                .set_completed("a", "student", &course, "choose-tool", true)
                .unwrap();
        }
        let store = ProgressStore::open(&path).unwrap();
        assert_eq!(
            store.completed("a", "student", &course.id).unwrap().len(),
            1
        );
        assert!(store
            .completed("b", "student", &course.id)
            .unwrap()
            .is_empty());
        assert!(store
            .completed("a", "other", &course.id)
            .unwrap()
            .is_empty());
        assert!(store
            .completed("a", "student", "other-course")
            .unwrap()
            .is_empty());
        assert!(store
            .set_completed("a", "student", &course, "missing", true)
            .is_err());
        store
            .set_completed("a", "student", &course, "choose-tool", false)
            .unwrap();
        assert!(store
            .completed("a", "student", &course.id)
            .unwrap()
            .is_empty());
    }

    #[test]
    fn duplicate_units_are_rejected_and_removed_units_do_not_count() {
        let source = include_str!("../courses/getting-started.json");
        assert!(Course::parse(&source.replace("\"review\"", "\"try\"")).is_err());
        let completed = HashSet::from(["try".into(), "removed-unit".into()]);
        assert_eq!(course().completed_units(&completed), 1);
        assert_eq!(course().total_units(), 4);
    }
}
