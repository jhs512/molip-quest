# 몰입 퀘스트

Rust + Dioxus로 만든 계정 없이 사용하는 설치형 프로그래밍 학습 앱입니다. 앱을 열면 클래스룸의 수업을 선택하고 문제를 풀 수 있습니다. AI가 필수이며 Claude Code 설치·로그인 확인을 통과해야 수업을 시작할 수 있습니다.

## 학습 기능

- Python 코드 작성과 실행, 고정 템플릿의 빈칸 문제
- 입출력 검사와 작성자 정의 Python 검사
- 수업 → 챕터 → 단원 목차, 로컬 완료 진도
- 코드 초안·검사 결과·제출 코드를 사용자 컴퓨터의 SQLite에 저장
- Claude Code CLI로 설명·힌트 및 코드 수정·실행
- 표·그래프 출력, 코드 편집기와 환경 진단

GitHub 및 이메일 로그인·회원가입·계정 인증을 제거했습니다. 학생용 앱에 중앙 서버가 필요하지 않습니다. 현재는 단독 학습 프로그램이며 강사와의 기록 공유나 P2P 동기화는 아직 구현하지 않았습니다. 이전 서버 기반 티켓과 명세는 과거 결정 기록입니다.

## 실행

```powershell
cargo build --bin molip-quest
./scripts/start-demo.ps1
```

또는 `cargo run --bin molip-quest`로 실행합니다. Windows에서는 WebView2가 필요하고, Python 실습에는 Python 설치가 필요합니다. AI 기능은 설치·로그인한 Claude Code를 호출하며 사용량과 비용은 사용자 계정에 따릅니다.

## 수업과 저장

기본 수업은 `courses/getting-started.json`입니다. `MOLIP_COURSE_PATH`로 다른 JSON 수업 파일을 선택할 수 있습니다. 파일을 불러오지 못하면 오류를 표시합니다. 저장 위치는 OS별 사용자 앱 데이터 폴더의 MolipQuest이며 코드 초안은 drafts.sqlite3, 실행 검사·완료 기록은 learning.sqlite3에 보관합니다.

단원의 `tests`는 input·expected 배열입니다. `blanks`는 starter_code의 {{name}} 자리만 수정하도록 지정합니다. `checker`는 학생 파일 경로를 첫 번째 인자로 받는 Python 코드입니다. 성공 종료는 통과, AssertionError 또는 종료 상태 1은 오답, 다른 예외나 종료 상태는 검사 오류입니다. 본질적으로 변경한 단원의 revision을 올리면 이전 완료가 현재 진도로 집계되지 않고 기존 검사 기록은 보존됩니다.

## 환경 진단

환경 진단 버튼은 Python 실행, pandas·matplotlib·seaborn·scikit-learn·openpyxl 설치, Claude Code 실행과 로그인 상태를 확인합니다. 모든 수업이 모든 패키지를 필요로 하는 것은 아닙니다.

- `MOLIP_PYTHON`: Python 실행 파일 경로
- `MOLIP_CLAUDE_PATH`: Claude 실행 파일 경로

클로드 자체의 계정 로그인은 AI 제공자 사용을 위한 것이며 몰입 퀘스트 서비스 회원가입이 아닙니다.

## 검증

```powershell
cargo fmt --check
cargo test
```

실제 Python 실행·입출력·사용자 정의 검사·표와 그래프·AI 응답 적용·계정과 서버 없는 로컬 완료 저장을 검사합니다. 실제 Claude Code 연동 검사는 별도 ignored 테스트로 제공하며 사용자 계정의 사용량을 사용합니다.

현재 Windows 11에서 개발 실행을 확인했습니다. Windows 10은 Rust 및 WebView2 지원 대상이지만 이 앱의 실기기 검증은 남아 있습니다. macOS 실행·설치 패키지 검증도 아직 완료하지 않았습니다.
