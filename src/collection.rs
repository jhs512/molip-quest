//! The collection is a projection of mission progress: it has no second reward ledger.
use dioxus::prelude::*;
use molip_quest::{curriculum::ActivityKind, Course};
use std::collections::HashSet;

#[derive(Clone, PartialEq)]
pub struct Card {
    pub id: String,
    pub title: String,
    pub category: String,
    pub body: String,
    pub unit: String,
    pub mission: usize,
    pub chapter: usize,
    pub acquired: bool,
    pub cover: bool,
}

pub fn cards(course: &Course, done: &HashSet<String>) -> Vec<Card> {
    let mut cards = Vec::new();
    for (chapter, c) in course.chapters.iter().enumerate() {
        let start = cards.len();
        for u in &c.units {
            for (mission, a) in u.activities.iter().enumerate() {
                let (category, body) = match &a.kind {
                    ActivityKind::Concept { body, .. } => ("개념", body.clone()),
                    ActivityKind::Coding { problem } => (
                        if a.challenge { "발견" } else { "도구" },
                        format!(
                            "{}\n\n### 코드 예제 · 시작 코드\n\n```python\n{}\n```",
                            problem.content, problem.starter_code
                        ),
                    ),
                    ActivityKind::Quiz { questions } => (
                        "발견",
                        questions
                            .iter()
                            .map(|q| format!("### {}\n\n{}", q.prompt, q.explanation))
                            .collect::<Vec<_>>()
                            .join("\n\n"),
                    ),
                    ActivityKind::Slides { .. } => continue,
                };
                let id = a.progress_unit(u).id;
                cards.push(Card {
                    acquired: done.contains(&id),
                    id,
                    title: a.title.clone(),
                    category: category.into(),
                    body,
                    unit: u.id.clone(),
                    mission,
                    chapter,
                    cover: false,
                });
            }
        }
        let acquired = cards.len() > start && cards[start..].iter().all(|c| c.acquired);
        cards.push(Card { id: format!("cover/{}",c.id), title: c.title.clone(), category: "챕터 표지".into(), body: "이 챕터의 개념·도구·발견 카드를 모두 모았습니다. 배운 내용을 다시 꺼내 볼 수 있는 나만의 분석 기록입니다.".into(), unit: c.units.first().map(|u|u.id.clone()).unwrap_or_default(), mission: 0, chapter, acquired, cover: true });
    }
    let acquired = !cards.is_empty() && cards.iter().all(|c| c.acquired);
    cards.push(Card {id:"collection-complete".into(),title:"KPC 분석가".into(),category:"완성 카드".into(),body:"모든 챕터 도감을 완성했습니다. 숫자를 읽고, 표를 만들고, 데이터로 질문하는 분석가의 여정을 완주했어요.".into(),unit:String::new(),mission:0,chapter:course.chapters.len(),acquired,cover:true});
    cards
}

#[component]
pub fn Collection(course: Course, onstudy: EventHandler<(String, usize)>) -> Element {
    let done = match molip_quest::learning_store::LearningStore::user_store()
        .and_then(|s| s.completed_items(&course))
    {
        Ok(done) => done,
        Err(e) => return rsx! {p {class:"error","{e}"}},
    };
    let cards = cards(&course, &done);
    let acquired = cards.iter().filter(|c| c.acquired).count();
    let mut selection = use_signal(|| None::<Card>);
    let mut filter = use_signal(|| "전체".to_string());
    rsx! {section {class:"collection-page","data-collection-course":course.id.clone(),
        div {class:"collection-heading",div {p {class:"collection-eyebrow","THE ANALYST'S ARCHIVE"}h1 {"분석가 도감"}p {"배운 개념이 카드로 남습니다. 모든 카드는 수업을 끝내면 모을 수 있어요."}}
            div {class:"collection-count",strong {"{acquired}"}span {" / {cards.len()} 수집"}}
        }
        div {class:"collection-filters",for category in ["전체","개념","도구","발견","챕터 표지","완성 카드"] {
            button {class:if filter()==category {"selected"}else{""},onclick:move |_|filter.set(category.into()),"{category}"}
        }}
        for chapter in 0..=course.chapters.len() {
            {let items:Vec<_>=cards.iter().filter(|c|c.chapter==chapter&&(filter()=="전체"||filter()==c.category)).cloned().collect();let chapter_all:Vec<_>=cards.iter().filter(|c|c.chapter==chapter).collect();let owned=chapter_all.iter().filter(|c|c.acquired).count();rsx!{
                if !items.is_empty() {section {class:"collection-chapter",h2 {{if chapter<course.chapters.len(){course.chapters[chapter].title.clone()}else{"여정의 완성".into()}}}p {class:"collection-chapter-count","{owned} / {chapter_all.len()} 수집"}
                    div {class:"collection-grid",for card in items {
                        button {key:"{card.id}",class:format!("collection-card{}{}",if card.acquired {" acquired"}else{" locked"},if card.cover {" cover"}else{""}),"data-card-id":card.id.clone(),
                            onclick:{let card=card.clone();move |_|selection.set(Some(card.clone()))},
                            span {class:"collection-card-top",span {"{card.category}"}span {class:"collection-new",hidden:!card.acquired,"NEW"}}
                            div {class:"collection-art",span {{if card.acquired {match card.category.as_str(){"개념"=>"◈","도구"=>"⌘","발견"=>"✧",_=>"♛"}}else{"?"}}}}
                            strong {"{card.title}"}span {class:"collection-card-bottom",{if card.acquired {"✓ 획득 · 눌러서 복습"}else{"미획득 · 획득 방법 보기"}}}
                        }
                    }}
                }}
            }}
        }
        if let Some(card)=selection() {div {class:"doctor-backdrop collection-backdrop",onclick:move |_|selection.set(None),onkeydown:move |e|{if e.key()==Key::Escape {selection.set(None);}},
            section {class:"doctor-panel collection-detail",role:"dialog",aria_modal:"true",aria_label:card.title.clone(),onclick:move |e|e.stop_propagation(),
                button {class:"collection-close",autofocus:true,onclick:move |_|selection.set(None),"닫기 ×"}
                p {class:"collection-eyebrow","{card.category}"}h2 {"{card.title}"}
                if card.acquired {div {class:"markdown",dangerous_inner_html:molip_quest::markdown::render(&card.body)}}
                else {p {"아직 획득하지 않은 카드예요."}p {{if card.id=="collection-complete" {"모든 챕터의 카드를 모으면 획득합니다.".into()}else if card.cover {"이 챕터의 모든 개념·코딩·퀴즈 미션을 완료하면 획득합니다.".into()}else{format!("「{}」 미션을 처음 완료하면 획득합니다.",card.title)}}}}
                if !card.cover {button {class:"primary",onclick:move |_|{onstudy.call((card.unit.clone(),card.mission));selection.set(None);},{if card.acquired {"해당 미션 다시 풀기 →"}else{"획득 미션으로 이동 →"}}}}
            }
        }}
    }}
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rewards_follow_progress_and_reset_without_duplicate_cards() {
        let course = Course::parse(include_str!("../courses/kpc-finance.json")).unwrap();
        let empty = cards(&course, &HashSet::new());
        assert!(empty.iter().all(|c| !c.acquired));
        let mut done = HashSet::new();
        done.insert(empty.iter().find(|c| !c.cover).unwrap().id.clone());
        assert_eq!(
            cards(&course, &done).iter().filter(|c| c.acquired).count(),
            1
        );
        done.extend(empty.iter().filter(|c| !c.cover).map(|c| c.id.clone()));
        let full = cards(&course, &done);
        assert!(full.iter().all(|c| c.acquired));
        assert_eq!(
            full.iter().map(|c| &c.id).collect::<HashSet<_>>().len(),
            full.len()
        );
    }
}
