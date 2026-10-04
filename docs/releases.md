# 릴리즈 설치 파일

`Release installers` 워크플로가 main의 모든 커밋(및 수동 실행)마다 세 플랫폼 설치 파일을 빌드하고, 셋 다 준비됐을 때만 `v<Cargo 버전>-build.<실행 번호>` 태그의 GitHub Release를 최신(latest)으로 발행합니다. 하나라도 빌드나 형식 검사에 실패하면 릴리즈를 만들지 않습니다.

| 플랫폼 | 파일 | 빌드 방식 | 현재 상태 |
| --- | --- | --- | --- |
| Windows x64 | molip-quest-windows-x64-setup.exe | Inno Setup. `build.rs`가 아이콘을 실행 파일에 내장. CI에서 무인 설치·제거까지 검증 | 자동 발행. 인증서 서명 없음 (SmartScreen 경고 가능) |
| macOS Apple Silicon | molip-quest-macos-arm64.dmg | `packaging/macos/bundle.sh`가 .app 번들을 만들고 ad-hoc 서명 후 DMG로 묶음. CI에서 DMG 마운트·arm64·서명 검증 | 자동 발행. Apple 공증 없음 (아래 첫 실행 안내 필요). 실기기 수동 검증은 아직 없음 |
| Android (열람 모드) | molip-quest-android.apk | `dx build --android --release`(Cargo `mobile` 기능). 저장소 비밀 `ANDROID_KEYSTORE_BASE64`·`ANDROID_KEYSTORE_PASSWORD`의 키스토어로 서명하고 `apksigner verify`로 확인 | 자동 발행. Play 스토어 외 설치(APK 직접 설치 허용 필요). 실기기 수동 검증은 아직 없음 |

형식 검사(`tools/verify-release-assets.py`)는 EXE 헤더·DMG 트레일러·APK 매니페스트와 arm64 라이브러리만 확인하며 앱 동작·서명을 보증하지 않습니다. Python·수업 패키지는 데스크톱 두 플랫폼 모두 README에 따라 사전 설치하며 설치 파일에 포함하지 않습니다.

## Android 열람 모드

Android 빌드는 `target_os = "android"`에서 Python을 실행하지 않습니다. 개념 확인과 퀴즈는 데스크톱과 같이 채점·저장하고, 코딩 미션은 문제·힌트·준비 코드·입출력 예제를 보여준 뒤 "읽었어요 · 다음 미션"으로 완료 처리합니다. 환경 진단·프롬프트 복사·코드 편집기는 숨겨지며, 순차 해금 없이 모든 단원과 미션이 처음부터 열려 있습니다. `packaging/android/MainActivity.kt`가 화면을 시스템 바 아래까지 그리고(edge-to-edge) 상태 표시줄·내비게이션 바 여백을 CSS 변수 `--inset-top`·`--inset-bottom`으로 넘깁니다. 진도는 앱 내부 저장 공간(`/data/data/dev.molipquest.app/files`)에 저장됩니다.

서명 키스토어는 한 번 만들어 저장소 비밀로 보관합니다. 키스토어를 바꾸면 기존 설치 위에 업데이트할 수 없으므로 원본 파일(`android-release.jks`)과 비밀번호를 안전한 곳에 백업하세요.

## macOS 첫 실행

DMG를 열어 `몰입 퀘스트.app`을 Applications로 끌어 넣습니다. 지금 배포본은 Apple 공증을 받지 않은 ad-hoc 서명이라, 처음 열면 Gatekeeper가 "'몰입 퀘스트'을(를) 열지 않음 … 악성 코드가 없음을 확인할 수 없습니다"라고 막습니다(macOS 15 Sequoia부터는 우클릭 → 열기도 통하지 않습니다). 한 번만 다음 순서로 허용하면 됩니다. 같은 안내가 DMG 안의 `먼저 읽어 주세요.txt`에도 있습니다.

1. 경고 창에서 **완료**를 누릅니다(휴지통으로 이동 아님).
2. **시스템 설정 → 개인정보 보호 및 보안 → 보안** 항목의 "'몰입 퀘스트'이(가) 차단되었습니다" 옆 **그래도 열기**를 누르고 암호로 확인합니다.
3. 다음부터는 더블클릭으로 열립니다.

터미널이 편하면 2번 대신 격리 속성을 지우면 됩니다.

```bash
xattr -dr com.apple.quarantine "/Applications/몰입 퀘스트.app"
```

이 경고를 없애려면 Apple Developer Program(연 99달러)의 **Developer ID Application** 인증서로 서명하고 공증해야 합니다. 워크플로는 준비돼 있어서 저장소 비밀 다섯 개만 넣으면 자동으로 서명·공증·스테이플까지 합니다: `APPLE_CERTIFICATE_P12_BASE64`(인증서 .p12를 base64로), `APPLE_CERTIFICATE_PASSWORD`, `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_APP_PASSWORD`(appleid.apple.com에서 만든 앱 암호). 비밀이 없으면 지금처럼 ad-hoc 서명으로 빌드합니다.

학습용 Python은 `MOLIP_PYTHON` 환경 변수로 지정하거나, 지정하지 않으면 PATH의 `python3`를 사용합니다.

## 모바일에 대한 판단

현재 앱은 로컬 Python 프로세스를 띄워 pandas·scikit-learn을 실행하는 데스크톱 구조입니다. 모바일에서 같은 학습 기능을 제공하려면 Python과 수업 패키지를 앱 안에 임베딩해야 하며 이는 별도의 대형 작업입니다. iOS는 Apple 인증서·프로비저닝이 필요해 범위에서 제외했습니다. Android는 위의 열람 모드로 제공합니다.

공식 참고: [Dioxus 배포](https://dioxuslabs.com/learn/0.7/tutorial/bundle/), [Python Android 임베딩](https://docs.python.org/3/using/android.html).

## 앱 아이콘

`tools/make-icon.py`가 `assets/icon/`에 Q 글자 아이콘(1024px 원본, Windows `.ico`, Android 밀도별 PNG와 적응형 전경)을 생성합니다. Windows는 `build.rs`(winresource)로 실행 파일에 내장하고 Inno Setup 설치 프로그램에도 씁니다. macOS는 `bundle.sh`가 `sips`·`iconutil`로 `.icns`를 만듭니다. Android는 dx가 기본 아이콘을 항상 덮어쓰므로 CI가 `tools/apply-android-icon.py`로 생성된 프로젝트의 리소스를 바꾼 뒤 Gradle로 다시 조립합니다.
