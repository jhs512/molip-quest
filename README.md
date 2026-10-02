# 몰입 퀘스트

Rust + Dioxus 설치형 학습 앱입니다. 코드 작성·Python 실행·검사·AI 작업은 사용자 컴퓨터에서 하고, 로그인·클래스룸·공개 수업·제출 코드·진도는 Rust 서버에서 관리합니다.

## 구현된 흐름

- 학생 가입·로그인, 강사 전용 클래스룸 생성, 가입 링크, 공개 수업 배정
- 수업 → 챕터 → 단원 목차, Python 코드 편집·실행, 빈칸 문제
- 입출력 검사와 작성자 정의 Python 검사, 중앙 제출·완료 기록
- 강사의 학생별 진도·제출 코드·검사 결과 확인
- 작성자만 같은 수업 수정, 본질 변경 시 완료 무효화·제출 이력 유지
- 설치·로그인한 Claude Code CLI로 설명·힌트, 코드 수정·실행

수업 작성 화면은 현재 JSON 편집 방식입니다. 오프라인 동기화는 제공하지 않습니다. 학생 컴퓨터의 검사 결과를 중앙 저장하는 방식이며 서버 재채점은 하지 않습니다.

## Windows 데모 실행

Rust MSVC 도구 체인과 WebView2, Python이 필요합니다. AI 사용에는 Claude Code 설치·로그인이 필요합니다.

```powershell
cargo build --bins
./scripts/start-demo.ps1
```

로컬 서버와 샘플 학생 계정으로 Python 학습 화면을 엽니다. 강사 화면은 앱을 닫고 다음과 같이 실행합니다.

```powershell
./scripts/start-demo.ps1 -Instructor
```

데모 전용 계정은 `teacher@molip.local`, `student@molip.local`이며 비밀번호는 `MolipQuest-Demo-2026!`입니다. 실제 서비스에서 사용하지 마세요. DB와 로그는 무시되는 `target/demo` 안에 저장됩니다. 실행 파일은 빌드를 방해하지 않도록 `target/demo/bin`에 복사합니다. 새 빌드를 데모에 반영하려면 데모 프로세스를 종료하고 이 폴더의 실행 파일을 새 빌드로 교체하세요.

## 서버와 앱 별도 실행

```powershell
$env:DATABASE_URL = 'sqlite://server.sqlite3?mode=rwc'
$env:MOLIP_INSTRUCTOR_EMAIL = 'your-email@example.com'
$env:MOLIP_INSTRUCTOR_PASSWORD = 'your-own-long-password'
cargo run --bin molip-server
```

다른 터미널에서:

```powershell
$env:MOLIP_SERVER_URL = 'http://127.0.0.1:3010'
cargo run --bin molip-quest
```

강사 계정은 서버에서 최초 생성하며 일반 가입은 학생 계정만 만듭니다. 기존 계정의 권한이나 비밀번호를 환경 변수로 변경하지 않습니다. 서버 바인딩은 `MOLIP_SERVER_BIND`로 지정합니다. 배포 시 HTTPS 연결을 제공해야 합니다.

서버 DB에는 SQLx를 사용합니다. 배포 시 `DATABASE_URL`을 PostgreSQL 접속 문자열로 지정할 수 있습니다. Supabase는 PostgreSQL 호스팅으로만 사용할 계획이며 접속 비밀은 서버에서 관리합니다. 학생 앱의 SQLite는 로컬 코드 초안만 저장합니다. 실제 Supabase 연결은 아직 검증하지 않았습니다.

## AI와 Python

기본 AI 연결은 `claude-cli`입니다. 별도 API 키 없이 설치된 Claude Code 로그인 환경으로 호출하며, 응답을 앱에서 표시하거나 코드에 적용해 로컬 실행합니다. CLI의 파일 편집·명령 실행 도구는 이 호출에서 비활성화합니다. 모델 기본값 `auto`는 Claude 설정을 따릅니다.

- `MOLIP_CLAUDE_PATH`: Claude 실행 파일 경로 (기본 `claude`)
- `MOLIP_PYTHON`: Python 실행 파일 경로 (Windows `python`, macOS `python3`)
- 앱 연결 설정에서 OpenAI 호환 주소·모델·키를 지정할 수도 있습니다.

AI 비용과 사용 한도는 사용자 계정에 따릅니다. 검사와 학생 코드는 실제 로컬 프로세스로 실행되며 실행 시간·출력 크기를 제한합니다.

## 수업 작성

[courses/getting-started.json](courses/getting-started.json)에 코드 작성·빈칸·입출력·사용자 정의 검사 예제가 있습니다. 강사 또는 관리자가 수업 작성 화면에 JSON을 입력해 공개합니다. 다른 작성자의 수업은 수정하거나 복사할 수 없습니다.

`tests`는 `input`·`expected` 배열이며 줄바꿈을 정규화하고 마지막 줄바꿈을 제외해 출력을 비교합니다. `blanks`는 `starter_code`의 `{{name}}` 자리만 편집합니다. `checker`는 학생 코드 파일 경로를 첫 번째 인자로 받는 Python 코드로, 종료 상태 0이 통과입니다. 본질적으로 바꾼 단원에 `reset_completion: true`를 지정하면 이전 완료가 무효화되고 제출은 보존됩니다.

## 검증 상태

```powershell
cargo fmt --check
cargo test
cargo test --test ai_learning claude_cli_returns_code_that_runs_locally -- --ignored
```

일반 테스트는 서버 권한·초대·배정·제출·진도·수업 수정, 실제 Python 검사와 AI 응답 적용을 검증합니다. 마지막 명령은 로그인한 Claude Code를 실제 호출하여 사용자 계정의 사용량을 소비합니다.

Windows에서 빌드·창 실행과 실제 Claude Code 연결을 확인했습니다. macOS 실행·설치 패키지와 실제 Supabase 배포 검증은 남아 있습니다. 현재 개발용 실행 파일이며 배포 완료 상태는 아닙니다.

## 개발 문서

- [프로젝트 지침](AGENTS.md)
- [도메인 용어](CONTEXT.md)
- [구현 명세](.scratch/molip-quest/spec.md)
- [구현 티켓](.scratch/molip-quest/issues)
