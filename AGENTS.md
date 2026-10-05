## Agent skills

### Issue tracker

Before creating or reading issues and specs, read `docs/agents/issue-tracker.md`. Work is tracked in local Markdown files under `.scratch/`.

### Triage labels

Before triaging an issue, read `docs/agents/triage-labels.md` for the default role labels.

### Domain docs

Before exploring the codebase, read `docs/agents/domain.md` for the single-context layout and domain documentation rules.

### 해설 모드 스크립트

개념 본문, 코딩 문제의 정답, 퀴즈 해설, 덱의 강사 스크립트를 바꾸기 전에 `docs/agents/narration.md`를 읽는다. 내용을 바꾸면 같은 커밋에서 `python tools/narrate.py`로 그 미션의 해설을 다시 만들고(바뀐 미션만 다시 쓴다) `python tools/build-kpc-course.py`로 확인한다.
