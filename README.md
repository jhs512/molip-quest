# 몰입 퀘스트

Rust + Dioxus로 만든 계정 없이 사용하는 설치형 프로그래밍 학습 앱입니다. 앱을 열면 클래스룸의 수업을 선택하고 문제를 풀 수 있습니다. AI 연결과 인터넷 연결 없이 로컬 수업 파일, Python 실행 환경과 SQLite 저장소로 동작합니다.

## 학습 기능

- Python 코드 작성과 실행, 고정 템플릿의 빈칸 문제
- 입출력 검사와 작성자 정의 Python 검사
- 수업 → 챕터 → 단원 목차, 로컬 완료 진도
- 코드 초안·검사 결과·제출 코드를 사용자 컴퓨터의 SQLite에 저장
- 표·그래프 출력, 코드 편집기와 환경 진단

GitHub 및 이메일 로그인·회원가입·계정 인증을 제거했습니다. 학생용 앱에 중앙 서버가 필요하지 않습니다. 현재는 단독 학습 프로그램이며 강사와의 기록 공유나 P2P 동기화는 아직 구현하지 않았습니다. 이전 서버 기반 티켓과 명세는 과거 결정 기록입니다.

## 설치 및 실행

현재 GitHub Releases에 macOS·Windows 설치 패키지를 배포하지 않았으므로 아래는 **소스에서 빌드하는 설치 방법**입니다. 비공개 저장소라 복제하려면 GitHub 접근 권한이 필요합니다. 최초 도구·패키지 다운로드와 빌드에는 인터넷이 필요하지만, 준비가 끝난 앱의 학습 기능은 인터넷 없이 동작합니다. uv는 Python 환경을 준비하기 위한 도구이며 앱 실행 자체의 필수 구성요소는 아닙니다.

### macOS (터미널)

먼저 Xcode 명령줄 도구와 Rust, uv를 설치합니다. 이미 설치된 도구는 건너뜁니다. Xcode 설치 창이 열리면 설치를 완료한 뒤 나머지 명령을 실행합니다.

```bash
xcode-select --install
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
curl -LsSf https://astral.sh/uv/install.sh | sh
```

터미널을 다시 연 뒤 저장소와 Python 실습 환경을 준비하고 앱을 빌드합니다.

```bash
git clone https://github.com/jhs512/molip-quest.git
cd molip-quest
uv python install 3.13
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python -r requirements-learning.txt
cargo build --release --locked --bin molip-quest
export MOLIP_PYTHON="$PWD/.venv/bin/python"
./target/release/molip-quest
```

다음 실행부터는 저장소 폴더에서 마지막 두 명령만 실행하면 됩니다. macOS 실제 빌드·실행은 아직 검증하지 않았습니다.

### Windows (PowerShell)

Git, Rust 빌드 도구, Rust, uv를 준비합니다. 설치 중 관리자 권한 요청이나 재시작 안내가 나오면 완료한 뒤 이어서 진행합니다. `winget`이 없다면 Microsoft의 [앱 설치 관리자](https://learn.microsoft.com/windows/package-manager/winget/)를 먼저 설치합니다.

```powershell
winget install --id Git.Git --exact
winget install --id Microsoft.VisualStudio.2022.BuildTools --exact --override "--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended"
winget install --id Rustlang.Rustup --exact
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

WebView2가 없는 PC에서는 다음 명령도 실행합니다.

```powershell
winget install --id Microsoft.EdgeWebView2Runtime --exact
```

PowerShell을 다시 연 뒤 저장소와 Python 실습 환경을 준비하고 앱을 빌드합니다.

```powershell
rustup default stable
git clone https://github.com/jhs512/molip-quest.git
cd molip-quest
uv python install 3.13
uv venv .venv --python 3.13
uv pip install --python .venv/Scripts/python.exe -r requirements-learning.txt
cargo build --release --locked --bin molip-quest
$env:MOLIP_PYTHON = Join-Path (Get-Location) '.venv/Scripts/python.exe'
./target/release/molip-quest.exe
```

다음 실행부터는 저장소 폴더에서 마지막 두 명령만 실행하면 됩니다. Python 경로 설정은 현재 터미널에 적용되므로 새 터미널에서는 다시 설정합니다.

Python이 이미 준비돼 있다면 `MOLIP_PYTHON`을 해당 실행 파일의 경로로 설정하여 사용할 수 있습니다. 기본 입출력 문제는 Python만으로 풀 수 있고, 표·그래프·ML 수업은 `requirements-learning.txt`의 실습 패키지를 사용합니다. 환경 진단 버튼으로 준비 상태를 확인합니다.

설치 명령 참고: [Rust 설치](https://www.rust-lang.org/tools/install), [Windows Rust 빌드 도구](https://learn.microsoft.com/windows/dev-environment/rust/setup), [uv 설치](https://docs.astral.sh/uv/getting-started/installation/), [Dioxus 데스크톱 준비](https://dioxuslabs.com/learn/0.7/getting_started/).

### 개발 실행

```powershell
cargo run --bin molip-quest
```

Windows 데모 실행은 `cargo build --bin molip-quest` 이후 `./scripts/start-demo.ps1`로도 가능합니다.

## 수업과 저장

기본 수업은 `courses/getting-started.json`입니다. `MOLIP_COURSE_PATH`로 다른 JSON 수업 파일을 선택할 수 있습니다. 파일을 불러오지 못하면 오류를 표시합니다. 저장 위치는 OS별 사용자 앱 데이터 폴더의 MolipQuest이며 코드 초안은 drafts.sqlite3, 실행 검사·완료 기록은 learning.sqlite3에 보관합니다.

단원의 `tests`는 input·expected 배열입니다. `blanks`는 starter_code의 {{name}} 자리만 수정하도록 지정합니다. `checker`는 학생 파일 경로를 첫 번째 인자로 받는 Python 코드입니다. 성공 종료는 통과, AssertionError 또는 종료 상태 1은 오답, 다른 예외나 종료 상태는 검사 오류입니다. 본질적으로 변경한 단원의 revision을 올리면 이전 완료가 현재 진도로 집계되지 않고 기존 검사 기록은 보존됩니다.

## 환경 진단

환경 진단 버튼은 Python 실행, pandas·matplotlib·seaborn·scikit-learn·openpyxl 설치를 확인합니다. 모든 수업이 모든 패키지를 필요로 하는 것은 아닙니다.

- `MOLIP_PYTHON`: Python 실행 파일 경로

## 검증

```powershell
cargo fmt --check
cargo test
```

실제 Python 실행·입출력·사용자 정의 검사·표와 그래프·계정과 서버 없는 로컬 완료 저장을 검사합니다.

현재 Windows 11에서 개발 실행을 확인했습니다. Windows 10은 Rust 및 WebView2 지원 대상이지만 이 앱의 실기기 검증은 남아 있습니다. macOS 실행·설치 패키지 검증도 아직 완료하지 않았습니다.
