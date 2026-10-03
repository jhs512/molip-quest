# 한글 답안 조합 중복 수정

Status: completed

사용자 증상: 개념 단답형에 파이썬을 입력하면 파이이써썬으로 중복된다.

Dioxus HTML의 value는 volatile 속성이다. 답안 input 이벤트마다 화면을 렌더링하면서 현재 값을 입력창에 다시 적용해 네이티브 IME 조합을 방해할 수 있다. 초기 답안은 initial_value로 한 번 전달하고 편집 중 값은 브라우저가 유지한다. input 이벤트로 답안 저장과 채점 상태를 계속 갱신한다. 같은 방식의 실행 입력에도 적용했다. 기존 빈칸 코딩의 초기화 동작은 이 변경에 포함하지 않았다.

## 검증

- tools/verify-ime.py: 실제 WebView2 앱에 합성 조합 입력 이벤트 전달. 기존 value 처리에서는 framework value rewrite during composition으로 실패했고, initial_value 변경 후 파이썬 유지·프레임워크 값 재쓰기 0회·화면 재진입 답안 복원·한글 답안 채점 통과.
- 네이티브 Input.imeSetComposition 자동화로 사용자의 정확한 중복 문자열은 안정적으로 재현하지 못했다. 합성 이벤트 검증은 Windows 하드웨어 IME 타이핑과 같지 않다.
- cargo test --locked --test kpc_learning concept_requires_one_answer 통과.
- cargo fmt --check 및 Windows 앱 빌드 확인.

검증용 course id ime-regression-check를 사용했다. 검증 후 원래 수업 앱으로 재실행했다.
