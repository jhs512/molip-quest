# 몰입 퀘스트 — KPC 금융 데이터 분석

KPC 「머신러닝을 활용한 금융데이터 분석」 3일(8+8+4시간) 수업 전용 Rust + Dioxus 설치형 앱입니다. 7개 챕터·20개 단원·77개 미션을 순서대로 클리어합니다. 로그인·AI 연결 없이 로컬 Python과 SQLite로 학습하며, 필요한 데이터와 HTML은 앱에 포함되어 있습니다. 환경 준비 후 학습에는 인터넷이 필요하지 않습니다.

## 학습 기능

- 단원마다 개념·코딩 미션·퀴즈의 수와 순서를 다르게 배치 (개념 반복, 문제 중심, 중간 퀴즈 등)
- 개념마다 단답형 확인 문제 정확히 한 개, 정답이면 클리어
- 객관식·단답형 혼합 퀴즈, 맞힌 문항 유지 및 오답만 재도전
- 한글·영문·약어 복수 인정 답안, 공백·영문 대소문자 처리
- 선행 미션 완료 후 다음 미션 해금, 완료한 미션 복습
- main.py 하나로 푸는 독립 코딩 문제 36개, 실행과 자동 검사
- 표·그래프 출력과 오류 피드백, 코드·답안·결과·진도 로컬 저장
- 정답 구하는 프롬프트 복사: 학생이 외부 AI에 직접 붙여넣어 도움을 받을 수 있음. 앱은 AI를 호출하지 않음
- 제출 정답 팝업과 다음 미션 자동 이동, 이전·다음 복습 (단원 간 이동 포함)
- 코드 실행에 예제 입력을 기본 제공, 입력값을 바꿔 연습 가능
- Markdown 설명·문항·해설, Python 코드 블록 색상 표시
- CodeMirror 6 코드 편집기
- Python·수업 패키지 환경 진단

각 실행은 새 프로세스와 별도 작업 폴더에서 시작합니다. data/titanic.csv, data/credit.csv, data/stock.csv, data/prices.html은 매번 원본으로 준비하므로 이전 문제의 변수·파일·수정에 의존하지 않습니다. Jupyter Notebook은 사용하지 않습니다.

범용 수업 플랫폼이나 중앙 서버를 제공하지 않습니다. 이전 서버 기반 명세·티켓은 과거 결정 기록이며 현재 KPC 설계는 `.scratch/kpc-learning/`에 있습니다.

## 설치 및 실행

현재 GitHub Releases에 macOS·Windows 설치 패키지를 배포하지 않았으므로 아래는 **소스에서 빌드하는 설치 방법**입니다. 비공개 저장소라 복제하려면 GitHub 접근 권한이 필요합니다. 최초 도구·패키지 다운로드와 빌드에는 인터넷이 필요하지만, 준비가 끝난 앱의 학습 기능은 인터넷 없이 동작합니다. uv는 Python 환경을 준비하기 위한 도구이며 앱 실행 자체의 필수 구성요소는 아닙니다.

### macOS (터미널)

이미 설치한 도구는 건너뜁니다. Homebrew가 없다면 다음 공식 설치 명령을 실행하고 안내를 따릅니다. 이 명령은 필요한 Xcode 명령줄 도구 설치도 안내합니다.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Homebrew를 PATH에 등록합니다. Apple Silicon과 Intel 설치 위치를 자동으로 구분합니다. 설치 안내에 다른 경로가 표시됐다면 그 안내를 따릅니다.

```bash
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi
brew install git uv
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

Homebrew가 지원하지 않는 구형 macOS에서는 [uv 공식 독립 설치](https://docs.astral.sh/uv/getting-started/installation/)를 사용합니다: `curl -LsSf https://astral.sh/uv/install.sh | sh`. 현재 Homebrew 지원 범위는 [공식 안내](https://brew.sh/)를 확인합니다.

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

Python이 이미 준비돼 있다면 `MOLIP_PYTHON`을 해당 실행 파일의 경로로 설정하여 사용할 수 있습니다. 기본 입출력 문제는 Python만으로 풀 수 있고, 표·그래프·ML 수업은 `requirements-learning.txt`의 실습 패키지를 사용합니다. 이 KPC 과정은 전체 패키지를 처음 한 번에 준비하며 문제별 설치는 없습니다. 환경 진단 버튼으로 준비 상태를 확인합니다.

설치 명령 참고: [Homebrew 설치](https://brew.sh/), [Rust 설치](https://www.rust-lang.org/tools/install), [Windows Rust 빌드 도구](https://learn.microsoft.com/windows/dev-environment/rust/setup), [uv 설치](https://docs.astral.sh/uv/getting-started/installation/), [Dioxus 데스크톱 준비](https://dioxuslabs.com/learn/0.7/getting_started/).

### 개발 실행

```powershell
cargo run --bin molip-quest
```

Windows 데모 실행은 `cargo build --bin molip-quest` 이후 `./scripts/start-demo.ps1`로도 가능합니다.

## 수업과 저장

기본 수업은 `courses/kpc-finance.json`입니다. `MOLIP_COURSE_PATH`로 다른 JSON 수업 파일을 선택할 수 있습니다. 파일을 불러오지 못하면 오류를 표시합니다. 저장 위치는 OS별 사용자 앱 데이터 폴더의 MolipQuest이며 코드 초안은 drafts.sqlite3, 실행 검사·완료 기록은 learning.sqlite3에 보관합니다.

단원의 `activities`는 순서가 있는 미션 배열입니다. `concept`는 설명과 단답형 `check` 한 개, `coding`은 독립된 `problem`, `quiz`는 `questions` 배열을 담습니다. 단답형은 `accepted` 배열로 여러 인정 답안을 등록합니다.

코딩 문제의 `tests`는 input·expected 배열입니다. `blanks`는 starter_code의 {{name}} 자리만 수정하도록 지정합니다. `checker`는 학생 파일 경로를 첫 번째 인자로 받는 Python 코드입니다. 성공 종료는 통과, AssertionError 또는 종료 상태 1은 오답, 다른 예외나 종료 상태는 검사 오류입니다. 본질적으로 변경한 단원의 revision을 올리면 이전 완료가 현재 진도로 집계되지 않고 기존 검사 기록은 보존됩니다.

## 환경 진단

환경 진단 버튼은 Python 실행, pandas·matplotlib·seaborn·scikit-learn·openpyxl·BeautifulSoup 설치를 확인합니다. 모든 수업이 모든 패키지를 필요로 하는 것은 아닙니다.

- `MOLIP_PYTHON`: Python 실행 파일 경로

## 검증

```powershell
cargo fmt --check
cargo test
```

실제 Python 실행·입출력·사용자 정의 검사·표와 그래프·로컬 저장과 함께 개념 확인, 20문항 혼합 퀴즈 누적 정답·재시작·순차 해금·프롬프트를 검사합니다. 제공 코딩 문제 36개는 각각 참조 답안으로 독립 실행·검사합니다.

콘텐츠를 수정할 때는 `python tools/build-kpc-course.py`로 과정 및 참조 답안을 재생성합니다. 학생용 화면은 참조 답안을 자동으로 표시하지 않습니다.

현재 Windows 11에서 개발 실행을 확인했습니다. Windows 10은 Rust 및 WebView2 지원 대상이지만 이 앱의 실기기 검증은 남아 있습니다. macOS 실행·설치 패키지 검증도 아직 완료하지 않았습니다.
