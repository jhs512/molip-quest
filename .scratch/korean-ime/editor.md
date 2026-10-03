# CodeMirror 한글 조합과 코드 동기화

Status: completed

사용자가 CodeMirror에 안녕하세요.를 입력했을 때 음절이 중복되는 화면을 제공했다. 답안 입력창 수정만으로는 코드 편집기의 별도 동기화 문제가 해결되지 않았다.

## 재현과 원인

실제 CodeMirror 문서에 한글을 추가하고 Rust 응답 전에 sync를 호출하면 data-editor-value의 이전 코드가 문서를 다시 덮어쓴다. 기존 코드에서 신규 한글이 사라지는 실패를 재현했다. IME가 조합 중인 DOM과 전체 문서 교체가 충돌할 수 있는 경로다.

## 수정

일반 타이핑은 CodeMirror가 소유하고 Dioxus에는 저장·실행용으로 전달한다. 지연된 값 응답으로 편집 문서를 다시 쓰지 않는다. 명시적 초기화만 data-editor-reset 버전을 변경하여 문서를 교체한다. 숨겨진 textarea도 매 입력마다 value를 다시 쓰는 대신 초기값만 제공한다.

## 검증

tools/verify-editor-ime.py로 단계별 한글 문서 변경과 오래된 값 응답을 함께 전달해 입력 유지, 정확한 한글 Python 실행, 초안 복원, 초기화 통과를 확인했다. Windows 하드웨어 IME 입력 그 자체를 자동화했다고 주장하지 않는다.

tools/verify-learning-flow.py는 실제 CodeMirror 문서 변경으로 코딩 답안을 입력하도록 갱신했다. Markdown 색상, 정답 팝업, CodeMirror, 미션·단원 왕복 이동 검증을 유지한다. Windows 빌드와 cargo fmt --check도 확인했다.
