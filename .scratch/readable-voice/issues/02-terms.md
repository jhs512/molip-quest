# 02 · 용어 통일 (전체 파일)

Status: open
Type: task
Blocked by: 01

## 무엇을

`../spec.md`의 "용어 결정" 표를 `tools/kpc_course/` 전체(단원 파일, 덱, 도전 과제, 표 퀴즈, 해설, 프롬프트 해설)에 적용한다. 1차에서 단원 파일은 대부분 맞췄지만 덱·해설·프롬프트에 남아 있을 수 있다. 01이 끝난 뒤에 한 번에 grep으로 잡는다.

## 방법

파일을 읽지 말고 먼저 센다. 코드 블록·백틱·열 이름·코드 식별자 안은 바꾸지 않는다.

```bash
cd tools/kpc_course
grep -n "Python" *.py | grep -v "^\s*#" | grep -v '`' | head        # → 파이썬 (코드·패키지 이름 제외)
grep -n "빈 칸" *.py                                                 # → 빈칸
grep -n "결측치" *.py                                                # → 결측
grep -n "임계값" *.py                                                # → 기준값
grep -n "혼동 행렬" *.py                                             # → 혼동행렬
grep -n "변화율" *.py                                                # → 수익률 (d3_p1 첫 언급만 "수익률(어제 대비 변화율)")
grep -n "기준선" *.py                                                # → 모델이면 기준 모델, 점수면 기준 모델의 점수
grep -n "매개변수" *.py                                              # → stratify·random_state는 인자, alpha는 하이퍼파라미터
grep -nE "훈련(해|한|하고|하면|할)" *.py                               # fit 동사 자리 → 학습 (훈련 자료는 그대로)
grep -nE "나무|랜덤포레스트" *.py                                     # → 트리, 랜덤 포레스트
grep -n "정답 열" *.py                                               # → 타깃 열 (정답 y는 그대로)
grep -n "DataFrame" *.py | grep -v '`' | grep -v "pd\." | head       # 보통명사 → 표
grep -n "데이터" *.py | grep -v "데이터 사이언티스트\|데이터 분석\|금융데이터" # 본문 4곳 → 자료
grep -nE "accuracy|R2" *.py | grep -v '`'                           # → 정확도, R²
grep -n "특징 만들기\|불리언 마스크" *.py                              # → 입력 열 만들기, 참·거짓 마스크
```

`narration_*.py`의 anchor는 본문 글자와 부분 일치해야 하므로, 본문 용어를 바꾸면 anchor도 같이 바꾼다(빌드가 막아 준다).

## 프롬프트 해설(prompts.py)도 같이

프롬프트 본문은 사람이 치는 글이라 해요체로 바꾸지 않는다. why("단어 → 이유") 줄은 메모체 그대로 두되 뜻이 틀린 곳만:

- "재현성" 남용: max_depth(model-comparison), alpha(regression-table)는 재현성이 아니라 "같은 조건"·"브레이크 세기". random_state만 재현성.
- 풀이 없는 용어: naive(manual-mae) → "순진한 기준(naive)", 불리언 마스크(loc-condition) → "참·거짓 마스크", 식별자(default-summary) → "번호 열", 벡터 연산(thresholds) → "열 전체 한 번에 계산".
- save-and-load, tune-depth 두 프롬프트만 'scikit-learn.' 대신 '타이타닉 생존 분류.'로 시작하고 쓸 수 있는 변수 목록이 없다. 이웃 프롬프트 모양에 맞춘다.
- `객실등급로` 같은 조사 오류는 백틱 밖에 조사를 둔다.

## 검증

```bash
python tools/build-kpc-course.py
cargo test --locked
```
