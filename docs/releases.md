# 릴리즈 설치 파일

`Release installers` 워크플로가 main의 모든 커밋(및 수동 실행)마다 두 플랫폼 설치 파일을 빌드하고, 둘 다 준비됐을 때만 `v<Cargo 버전>-build.<실행 번호>` 태그의 GitHub Release를 최신(latest)으로 발행합니다. 하나라도 빌드나 형식 검사에 실패하면 릴리즈를 만들지 않습니다.

| 플랫폼 | 파일 | 빌드 방식 | 현재 상태 |
| --- | --- | --- | --- |
| Windows x64 | molip-quest-windows-x64-setup.exe | Inno Setup. CI에서 무인 설치·제거까지 검증 | 자동 발행. 인증서 서명 없음 (SmartScreen 경고 가능) |
| macOS Apple Silicon | molip-quest-macos-arm64.dmg | `packaging/macos/bundle.sh`가 .app 번들을 만들고 ad-hoc 서명 후 DMG로 묶음. CI에서 DMG 마운트·arm64·서명 검증 | 자동 발행. Apple 공증 없음 (아래 첫 실행 안내 필요). 실기기 수동 검증은 아직 없음 |
| Android | molip-quest-android.apk | 미구현 | 코딩 실행 없이 개념·퀴즈만 진행하는 열람 모드 APK를 검토 중 |

형식 검사(`tools/verify-release-assets.py`)는 EXE 헤더와 DMG 트레일러만 확인하며 앱 동작·서명을 보증하지 않습니다. Python·수업 패키지는 두 플랫폼 모두 README에 따라 사전 설치하며 설치 파일에 포함하지 않습니다.

## macOS 첫 실행

DMG를 열어 `몰입 퀘스트.app`을 Applications로 끌어 넣습니다. 공증되지 않은 앱이므로 처음에는 더블클릭 대신 **우클릭 → 열기**를 선택하거나, 터미널에서 다음을 실행합니다.

```bash
xattr -cr "/Applications/몰입 퀘스트.app"
```

학습용 Python은 `MOLIP_PYTHON` 환경 변수로 지정하거나, 지정하지 않으면 PATH의 `python3`를 사용합니다.

## 모바일에 대한 판단

현재 앱은 로컬 Python 프로세스를 띄워 pandas·scikit-learn을 실행하는 데스크톱 구조입니다. 모바일에서 같은 학습 기능을 제공하려면 Python과 수업 패키지를 앱 안에 임베딩해야 하며 이는 별도의 대형 작업입니다. iOS는 Apple 인증서·프로비저닝이 필요해 범위에서 제외했습니다. Android는 Python 실행 없이 개념·퀴즈를 진행하고 코딩 미션은 열람만 하는 모드로 제한적 APK를 제공하는 방안을 검토합니다.

공식 참고: [Dioxus 배포](https://dioxuslabs.com/learn/0.7/tutorial/bundle/), [Python Android 임베딩](https://docs.python.org/3/using/android.html).
