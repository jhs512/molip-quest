# 해설 모드 스크립트 미리 컴파일

Status: done (2026-10-05)

## 목표

1. `/auto`와 `/auto-all`이 CLI를 기다리지 않고 바로 시작한다. 미션마다 해설 대본이 빌드 때 컴파일되어 `courses/kpc-finance.json`의 `narration`에 들어가고, 패널이 대본을 먼저 보여 준 뒤 동작한다.
2. 개념을 설명할 때 설명하는 문단·코드·만화가 화면 아래에 있으면 그 자리로 천천히 내려가며 비춘다 (`text:<구절>` 타깃, `assets/layout/agent.js`의 glide).
3. 규칙: 내용을 바꾸면 그 미션의 해설도 같이 바꾼다. 빌드가 강제한다 (`docs/agents/narration.md`).

## 구조

- 컴파일러·검사: `tools/kpc_course/narration.py`. 슬라이드는 강사 스크립트에서, 퀴즈는 문항 해설에서 자동. 개념·코딩은 `tools/kpc_course/narration_*.py`에 손으로 쓴다.
- 앱: `Activity.narration`(`src/curriculum.rs`), `AssistantPanel`의 `narrate`(`src/ui.rs`), `assistant::narration_lines`. 대본이 없는 미션만 CLI가 즉석에서 만든다.
- 검증: `python tools/build-kpc-course.py`, `cargo test`(모든 미션에 해설이 있고 끝 동작이 맞는지).
