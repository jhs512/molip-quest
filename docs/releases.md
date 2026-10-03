# 릴리즈 설치 파일

릴리즈에는 다음 세 파일을 함께 첨부합니다. 하나라도 없으면 릴리즈 준비 워크플로가 중단됩니다.

| 플랫폼 | 필수 파일 | 현재 상태 |
| --- | --- | --- |
| Windows x64 | molip-quest-windows-x64-setup.exe | Inno Setup 설치·제거 검증과 빌드 워크플로 추가. CI 실행 결과 확인 필요 |
| Android | molip-quest-android.apk | 모바일 앱 및 내장 Python 실행 환경 구현 필요 |
| iOS | molip-quest-ios.ipa | 모바일 앱·내장 Python 실행 환경 구현, Apple 서명·프로비저닝 필요 |

현재 Cargo 설정, 윈도 메뉴, 클립보드, Python subprocess 실행 방식은 데스크톱용입니다. 확장자를 바꾸거나 빈 모바일 앱을 만드는 것으로 코딩 학습 기능을 제공할 수 없습니다.

모바일에서는 앱 내부에 Python과 pandas, matplotlib, scikit-learn 등 수업 패키지를 포함하고, 임베디드 인터프리터를 통해 실행·채점·표·그래프 출력을 지원해야 합니다. 서버나 AI를 추가하지 않으며 오프라인 학습 요구사항을 유지합니다. Android SDK/NDK 및 macOS/Xcode 빌드 환경과 실제 기기 검증이 필요합니다. iOS는 배포 방식에 맞는 Apple 인증서와 프로비저닝 프로파일이 필요하며 IPA 파일만 내려받아 모든 iPhone에 바로 설치할 수 있는 것은 아닙니다.

공식 참고: [Dioxus 배포](https://dioxuslabs.com/learn/0.7/tutorial/bundle/), [Python iOS 임베딩](https://docs.python.org/3/using/ios.html), [Python Android 임베딩](https://docs.python.org/3/using/android.html).

`Windows installer` 워크플로는 main 변경 또는 수동 실행으로 설치 파일을 `release-windows-x64` 아티팩트에 보관합니다. Python·수업 패키지와 WebView2는 README에 따라 사전 설치하며 이 설치 파일에는 포함하지 않습니다. Windows 인증서 서명은 아직 구성하지 않았습니다.

모바일 구현과 서명·기기 검증 완료 후 모바일 빌드가 각각 `release-android`, `release-ios` 아티팩트를 생성하도록 연결합니다. `Prepare three-platform release`에 기존 버전 태그와 세 빌드의 실행 ID를 넣으면 파일 존재·형식 검사 후 세 설치 파일이 첨부된 초안 릴리즈를 만듭니다. 형식 검사는 실제 앱 동작이나 서명 검증을 대체하지 않습니다. 모바일 빌드가 아직 없으므로 현재는 세 플랫폼 릴리즈를 만들 수 없습니다.
