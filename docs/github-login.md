# GitHub 학생 로그인

로그인 화면의 **GitHub로 로그인하기**를 누르면 인증 코드가 표시됩니다. **GitHub에서 승인하기**를 열어 코드를 입력하면 앱이 자동으로 로그인합니다. 취소하거나 인증 시간이 지나면 새로 시작할 수 있습니다.

서버에서 GitHub OAuth 앱의 Client ID를 `MOLIP_GITHUB_CLIENT_ID`로 설정하고 서버를 재시작해야 합니다. GitHub 앱 설정에서 **Enable Device Flow**를 켜세요. 서버는 실행 디렉터리의 `.env`도 읽습니다. `.env.example`을 복사해 설정할 수 있으며 실제 `.env`는 Git에 포함하지 않습니다. 데모 실행 디렉터리는 `target/demo`입니다.

2026-10-03에 jhs512 소유의 **몰입 퀘스트** OAuth 앱을 등록하고 Device Flow를 활성화했습니다. [등록 설정](https://github.com/settings/applications/3900520). 로컬 서버와 데모 서버에 Client ID를 연결했으며 브라우저 승인 후 데스크톱 앱에서 GitHub 학생 계정으로 로그인되는 것까지 확인했습니다.

이 방식에는 Client Secret이 필요하지 않습니다. 저장소 접근 권한이나 비공개 이메일 권한도 요청하지 않습니다. GitHub 토큰과 device code는 데스크톱에 전달하지 않습니다. 로그인 요청을 추적하는 임시 코드만 클라이언트에 전달합니다. 운영 서버는 HTTPS를 사용해야 합니다.

GitHub의 숫자 계정 ID로 학생 계정을 구분합니다. 표시되는 `숫자@github.local`은 내부 식별용이고 실제 이메일 주소가 아닙니다. 기존 이메일 계정과 자동으로 합치지 않으며 강사·관리자 권한도 자동 부여하지 않습니다. 기존 이메일 계정으로 참여한 클래스룸은 별도 계정 연결 기능이 없으므로 GitHub 계정으로 다시 참여해야 합니다.

서버가 인증 요청의 만료 시간과 폴링 간격을 관리하고, 로그인 완료 시 요청을 한 번만 소비합니다. GitHub 인증 대기 상태와 slow_down 응답에 따라 폴링 간격을 조정합니다. 계정 확인 이후 앱 자체의 일주일 세션을 발급합니다. GitHub 토큰은 DB에 저장하지 않습니다.

검증: 계정 ID 유지, 학생 권한, 임시 요청 재사용 차단, 만료 요청 차단의 자동 테스트 통과. 실제 앱 버튼 → 인증 코드 발급 → GitHub 승인 → 앱 학생 로그인 흐름도 확인했습니다. 기존 이메일 계정의 클래스룸 접근이 자동 부여되지 않는 것도 확인했습니다.

[GitHub 공식 Device flow 문서](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#device-flow)
