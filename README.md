# 몰입 퀘스트 — KPC 금융 데이터 분석

KPC 「머신러닝을 활용한 금융데이터 분석」 3일(8+8+4시간) 수업 전용 Rust + Dioxus 설치형 앱입니다. 7개 챕터·20개 단원·148개 미션을 순서대로 클리어합니다. 로그인·AI 연결 없이 로컬 Python과 SQLite로 학습하며, 필요한 데이터와 HTML은 앱에 포함되어 있습니다. 환경 준비 후 학습에는 인터넷이 필요하지 않습니다.

## 학습 기능

main에 커밋이 올라갈 때마다 GitHub Releases에 **Windows x64 설치 EXE·macOS Apple Silicon DMG·Android APK** 세 파일이 자동으로 첨부됩니다. Android는 코드 실행 없이 개념·퀴즈를 풀고 코딩 미션은 읽고 넘어가는 열람 모드입니다. 설치 방법과 서명·검증 상태는 [릴리즈 문서](docs/releases.md)를 확인하세요.

- 단원마다 개념·코딩 미션·퀴즈의 수와 순서를 다르게 배치 (개념 반복, 문제 중심, 중간 퀴즈 등)
- 개념마다 단답형 확인 문제 정확히 한 개, 정답이면 클리어
- 객관식·단답형 혼합 퀴즈, 맞힌 문항 유지 및 오답만 재도전
- 한글·영문·약어 복수 인정 답안, 공백·영문 대소문자 처리
- 모든 단원과 미션으로 자유롭게 이동해 미리 보기. 클리어는 제출 통과·퀴즈 정답으로만 기록되고, 단원은 아직 클리어하지 않은 첫 미션에서 이어짐
- 단원 진도 막대는 미션별 칸: 클리어한 칸은 채워지고 지금 보는 칸은 테두리로 구분되며, 칸을 누르면 그 미션으로 이동
- 자료 보기: 문제가 쓰는 data/ 파일마다 버튼이 생기고, CSV·Excel은 앞 100행 표로, HTML은 원문으로 전체 화면에서 확인
- 단계적 시각화(explorable explanation): 빈 그림에서 "다음 단계"마다 요소가 하나씩 더해지고 슬라이더로 직접 움직여 보는 위젯. 트리 깊이와 과적합(훈련·테스트 오차), 임계값(정밀도·재현율·비용), 시간 분리(테스트 구간과 경계 하루), 층화 분할(다시 나누기·stratify 토글), 누수(구명보트 열 토글과 시점), MAE(오차 막대 쌓기), 이동평균(창 크기), 히스토그램(구간 수)
- 자료의 열 이름과 범주 값은 한글(객실등급·생존·성별·나이·요금 …, 신용한도·상환_9월·다음달 부도, 날짜·종가·거래량). 변수 이름과 함수는 영어 그대로이고, 그래프의 한글은 실행 환경이 글꼴을 골라 줌
- main.py 하나로 푸는 독립 코딩 문제 104개, 실행과 자동 검사
- 챕터마다 마지막에 ★ 도전 과제 1개: 그 챕터의 기술을 전부 써야 풀리는 독립 문제(빵 공장 생산 계획표, 크루아상 판매 기록 정리, 가족 동반 생존, 한 장에 두 그림, 네 모델 비교, 임계값과 비용, 창을 바꾼 재실험)
- 개념·문제·슬라이드 안의 1~3컷 만화 50편 (Comic Gen YAML, 내장 SDK로 오프라인 렌더링). 흐름·순서가 핵심인 곳은 컷 안에 머메이드 다이어그램(내장 Mermaid)
- 퀴즈 166문항 중 40문항은 "프롬프트 고르기": 상황과 후보 프롬프트 4개, 해설은 보기마다 왜 아닌지를 적음. 모든 객관식 해설에 "다른 보기는 왜 아닌가"
- 강사용 슬라이드 미션 5벌 (Marp Markdown, 내장 Marp Core로 오프라인 렌더링): 왜 3일을 배우나(AI 시대의 데이터 분석과 비용 절감 사례), 표는 왜 pandas로(2차원 리스트와의 차이, NumPy가 빠른 이유, 콘다가 필요했던 시절), 머신러닝은 표에서 규칙 찾기, 기준·과적합·모델 저장, 시간은 섞지 않는다. 이전·다음·전체 화면, 마지막 장까지 보면 미션 완료. 슬라이드 안에도 만화·머메이드·그림이 들어감
- 한 번 만든 모델을 `joblib`으로 저장하고 불러와 다시 쓰는 개념과 미션 (2일차 6교시)
- 클래스룸 첫 화면의 모아보기 4종: PPT·만화·발전적 시각화·개념(문제·퀴즈 제외). 각각 제목 목록이 먼저 나오고, 제목을 누르면 그 내용이 열리며 이전·다음으로 넘어감. PPT는 덱 뷰어 그대로(이전·다음 장, 전체 화면)
- 글꼴 내장: 본문 Pretendard, 코드 JetBrains Mono (`assets/fonts/`, base64로 앱에 포함). 창 메뉴 막대 없음
- 본문을 더블 클릭하면 그 문단부터 미션 끝까지 읽어 주는 한국어 음성 (기기의 ko-KR 음성 사용, 속도 조절·일시정지)
- 표·그래프 출력과 오류 피드백, 코드·답안·결과·진도 로컬 저장
- 프롬프트 복사 · 인간 버전: 문제마다 손으로 쓴, 사람이 실제로 치는 2~5줄 프롬프트(`tools/kpc_course/prompts.py`). 분석가의 용어(stratify, temporal split, 누수, 기준선 …)가 답을 바꾸는 자리에만 들어가고 "코드만 줘"로 끝남
- 프롬프트 복사 · 기계 버전: 같은 요청을 최소 명세로 쓴 것. 과제, 출력 형식, (실제 코드가 있을 때만) 기본 코드, 지금 쓴 코드, 예시, 채점 조건만
- 프롬프트 해설: 전체 화면 레이어. 인간 버전의 어떤 단어가 왜 들어갔는지, 이 단원에서 AI에게 꼭 말해야 하는 것, 짧게 쓰는 요령, 기계 버전과의 차이. 앱은 AI를 호출하지 않음
- 코딩 화면의 문제/코드, 편집기/실행 결과 사이 드래그 핸들 (더블 클릭으로 초기화, 크기는 기기에 저장)
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

단원의 `activities`는 순서가 있는 미션 배열입니다. `concept`는 설명과 단답형 `check` 한 개, `coding`은 독립된 `problem`, `quiz`는 `questions` 배열, `slides`는 Marp `markdown`을 담습니다. 단답형은 `accepted` 배열로 여러 인정 답안을 등록합니다.

코딩 문제의 `tests`는 input·expected 배열입니다. `blanks`는 starter_code의 {{name}} 자리만 수정하도록 지정합니다. `checker`는 학생 파일 경로를 첫 번째 인자로 받는 Python 코드입니다. 성공 종료는 통과, AssertionError 또는 종료 상태 1은 오답, 다른 예외나 종료 상태는 검사 오류입니다. 본질적으로 변경한 단원의 revision을 올리면 이전 완료가 현재 진도로 집계되지 않고 기존 검사 기록은 보존됩니다.

## 환경 진단

환경 진단 버튼은 Python 실행, pandas·matplotlib·seaborn·scikit-learn·openpyxl·BeautifulSoup 설치를 확인합니다. 모든 수업이 모든 패키지를 필요로 하는 것은 아닙니다.

- `MOLIP_PYTHON`: Python 실행 파일 경로

## 검증

```powershell
cargo fmt --check
cargo test
```

실제 Python 실행·입출력·사용자 정의 검사·표와 그래프·로컬 저장과 함께 개념 확인, 20문항 혼합 퀴즈 누적 정답·재시작·프롬프트를 검사합니다. 제공 코딩 문제 102개는 각각 참조 답안으로 독립 실행·검사합니다. 읽어주기의 문장 분할·발음 변환·재생 제어는 `node --test assets/speech/speech.test.mjs`로 검사합니다.

콘텐츠를 수정할 때는 `python tools/build-kpc-course.py`로 과정 및 참조 답안을 재생성합니다. 학생용 화면은 참조 답안을 자동으로 표시하지 않습니다.

현재 Windows 11에서 개발 실행을 확인했습니다. Windows 10은 Rust 및 WebView2 지원 대상이지만 이 앱의 실기기 검증은 남아 있습니다. macOS 실행·설치 패키지 검증도 아직 완료하지 않았습니다.
