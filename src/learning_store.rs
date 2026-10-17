use crate::{runner::TestReport, Unit};
use rusqlite::OptionalExtension;
use rusqlite::{params, Connection};
use std::{collections::HashSet, path::Path};

pub struct LearningStore(Connection);
impl LearningStore {
    pub fn quiz_passed(
        &self,
        course: &str,
        unit: &Unit,
        questions: &[crate::curriculum::Question],
    ) -> Result<HashSet<String>, String> {
        let mut passed = HashSet::new();
        for q in questions {
            let key = format!("{}/question/{}", unit.id, q.id);
            let exists:bool = self.0.query_row("SELECT EXISTS(SELECT 1 FROM completed WHERE course=?1 AND unit=?2 AND revision=?3)",params![course,key,unit.revision],|r|r.get(0)).map_err(|e|e.to_string())?;
            if exists {
                passed.insert(q.id.clone());
            }
        }
        Ok(passed)
    }
    pub fn save_quiz(
        &mut self,
        course: &str,
        unit: &Unit,
        questions: &[crate::curriculum::Question],
        answers: &std::collections::HashMap<String, String>,
    ) -> Result<TestReport, String> {
        let passed = self.quiz_passed(course, unit, questions)?;
        let mut report = crate::curriculum::grade_quiz(questions, answers);
        for (q, case) in questions.iter().zip(&mut report.cases) {
            if passed.contains(&q.id) {
                case.passed = true;
                case.state = "previously_passed".into();
            }
        }
        report.passed = !report.cases.is_empty() && report.cases.iter().all(|c| c.passed);
        if report.cases.is_empty() {
            return Err("퀴즈 문항이 없습니다.".into());
        }
        let source = serde_json::to_string(answers).map_err(|e| e.to_string())?;
        let report_json = serde_json::to_string(&report).map_err(|e| e.to_string())?;
        let tx = self.0.transaction().map_err(|e| e.to_string())?;
        tx.execute(
            "INSERT INTO attempts(course,unit,revision,code,report) VALUES (?1,?2,?3,?4,?5)",
            params![course, unit.id, unit.revision, source, report_json],
        )
        .map_err(|e| e.to_string())?;
        for (q, case) in questions.iter().zip(&report.cases) {
            if case.passed {
                tx.execute("INSERT INTO completed VALUES (?1,?2,?3) ON CONFLICT(course,unit) DO UPDATE SET revision=excluded.revision",params![course,format!("{}/question/{}",unit.id,q.id),unit.revision]).map_err(|e|e.to_string())?;
            }
        }
        if report.passed {
            tx.execute("INSERT INTO completed VALUES (?1,?2,?3) ON CONFLICT(course,unit) DO UPDATE SET revision=excluded.revision",params![course,unit.id,unit.revision]).map_err(|e|e.to_string())?;
        }
        tx.commit().map_err(|e| e.to_string())?;
        Ok(report)
    }
    pub fn open(path: &Path) -> Result<Self, String> {
        let db = Connection::open(path).map_err(|e| e.to_string())?;
        db.execute_batch("CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, course TEXT NOT NULL, unit TEXT NOT NULL, revision INTEGER NOT NULL, code TEXT NOT NULL, report TEXT NOT NULL); CREATE TABLE IF NOT EXISTS completed (course TEXT NOT NULL, unit TEXT NOT NULL, revision INTEGER NOT NULL, PRIMARY KEY(course,unit));").map_err(|e| e.to_string())?;
        db.execute_batch("CREATE TABLE IF NOT EXISTS study_positions (course TEXT PRIMARY KEY, unit TEXT NOT NULL, activity TEXT NOT NULL)")
            .map_err(|e| e.to_string())?;
        Ok(Self(db))
    }
    pub fn user_store() -> Result<Self, String> {
        Self::open(&crate::data_dir()?.join("learning.sqlite3"))
    }
    /// Last viewed mission, independent of completion. IDs survive insertions and reordering.
    pub fn save_position(&self, course: &str, unit: &str, activity: &str) -> Result<(), String> {
        self.0.execute("INSERT INTO study_positions(course,unit,activity) VALUES (?1,?2,?3) ON CONFLICT(course) DO UPDATE SET unit=excluded.unit,activity=excluded.activity", params![course,unit,activity])
            .map(|_| ()).map_err(|e| e.to_string())
    }
    pub fn resume_position(&self, course: &crate::Course) -> Result<Option<(String, usize)>, String> {
        let saved: Option<(String, String)> = self.0.query_row(
            "SELECT unit,activity FROM study_positions WHERE course=?1", [&course.id],
            |row| Ok((row.get(0)?, row.get(1)?)),
        ).optional().map_err(|e| e.to_string())?;
        Ok(saved.and_then(|(unit_id, activity_id)| {
            let unit = course.chapters.iter().flat_map(|c| &c.units).find(|u| u.id == unit_id)?;
            let index = if unit.activities.is_empty() { Some(0) } else { unit.activities.iter().position(|a| a.id == activity_id) }?;
            Some((unit_id, index))
        }))
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
    /// Record a mission the student finished by reading it to the end (slide decks).
    pub fn mark_viewed(&mut self, course: &str, unit: &Unit) -> Result<(), String> {
        self.0
            .execute(
                "INSERT INTO completed VALUES (?1,?2,?3) ON CONFLICT(course,unit) DO UPDATE SET revision=excluded.revision",
                params![course, unit.id, unit.revision],
            )
            .map(|_| ())
            .map_err(|e| e.to_string())
    }
    /// Forget every attempt and completion for one course so the student starts over.
    pub fn reset(&mut self, course: &str) -> Result<(), String> {
        let tx = self.0.transaction().map_err(|e| e.to_string())?;
        tx.execute("DELETE FROM attempts WHERE course=?1", [course])
            .map_err(|e| e.to_string())?;
        tx.execute("DELETE FROM completed WHERE course=?1", [course])
            .map_err(|e| e.to_string())?;
        tx.execute("DELETE FROM study_positions WHERE course=?1", [course])
            .map_err(|e| e.to_string())?;
        tx.commit().map_err(|e| e.to_string())
    }
    pub fn completed(&self, course: &crate::Course) -> Result<HashSet<String>, String> {
        let items = self.completed_items(course)?;
        Ok(course
            .chapters
            .iter()
            .flat_map(|c| &c.units)
            .filter(|unit| {
                if unit.activities.is_empty() {
                    items.contains(&unit.id)
                } else {
                    unit.activities
                        .iter()
                        .all(|a| items.contains(&a.progress_unit(unit).id))
                }
            })
            .map(|u| u.id.clone())
            .collect())
    }
    /// Whether this unit (a coding problem, or a mission's progress unit) has been passed at
    /// its current revision: what the 제출 button turns into 다시 제출 on.
    pub fn unit_completed(&self, course: &str, unit: &Unit) -> Result<bool, String> {
        let revision: Option<i64> = self
            .0
            .query_row(
                "SELECT revision FROM completed WHERE course=?1 AND unit=?2",
                params![course, unit.id],
                |r| r.get(0),
            )
            .optional()
            .map_err(|e| e.to_string())?;
        Ok(revision == Some(unit.revision))
    }
    pub fn completed_items(&self, course: &crate::Course) -> Result<HashSet<String>, String> {
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
            if course.chapters.iter().flat_map(|c| &c.units).any(|u| {
                u.revision == revision
                    && ((u.activities.is_empty() && u.id == id)
                        || u.activities.iter().any(|a| a.progress_unit(u).id == id))
            }) {
                units.insert(id);
            }
        }
        Ok(units)
    }
}

#[cfg(test)]
mod position_tests {
    use super::*;

    #[test]
    fn last_viewed_mission_survives_reopening_and_is_scoped_to_the_course() {
        let root = tempfile::tempdir().unwrap();
        let path = root.path().join("learning.sqlite3");
        let course = crate::Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        let unit = &course.chapters[1].units[1];
        let store = LearningStore::open(&path).unwrap();
        assert_eq!(store.resume_position(&course).unwrap(), None);
        store.save_position(&course.id, &unit.id, &unit.activities[5].id).unwrap();
        // Going backwards must save the last view, not the furthest completed mission.
        store.save_position(&course.id, &unit.id, &unit.activities[2].id).unwrap();
        drop(store);
        let mut store = LearningStore::open(&path).unwrap();
        assert_eq!(store.resume_position(&course).unwrap(), Some((unit.id.clone(), 2)));
        let mut other = course.clone();
        other.id = "another-course".into();
        assert_eq!(store.resume_position(&other).unwrap(), None);
        store.save_position(&other.id, &unit.id, &unit.activities[1].id).unwrap();
        store.reset(&course.id).unwrap();
        assert_eq!(store.resume_position(&course).unwrap(), None);
        assert_eq!(store.resume_position(&other).unwrap(), Some((unit.id.clone(), 1)));
    }

    #[test]
    fn positions_follow_mission_ids_and_ignore_removed_missions() {
        let mut course = crate::Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        let store = LearningStore::open(Path::new(":memory:")).unwrap();
        let unit = &course.chapters[0].units[0];
        let unit_id = unit.id.clone();
        store.save_position(&course.id, &unit.id, &unit.activities[3].id).unwrap();
        course.chapters[0].units[0].activities.swap(0, 3);
        assert_eq!(store.resume_position(&course).unwrap(), Some((unit_id.clone(), 0)));
        course.chapters[0].units[0].activities.remove(0);
        assert_eq!(store.resume_position(&course).unwrap(), None);
        store.save_position(&course.id, "removed-unit", "removed-mission").unwrap();
        assert_eq!(store.resume_position(&course).unwrap(), None);
    }
}
