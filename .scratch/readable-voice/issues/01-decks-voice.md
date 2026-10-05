# 01 · 덱 30개의 슬라이드 글을 강사 목소리로

Status: open
Type: task
Blocked by: (없음)

## 무엇을

`tools/kpc_course/decks.py`, `decks_python_pandas.py`, `decks_eda_viz.py`, `decks_modeling_credit.py`, `decks_stock.py`의 덱 30개. 슬라이드 본문 문단을 `../voice.md`의 목소리(해요체, 한 문장 45자 이내)로 바꾼다. 강사 script는 이미 해요체라 아래 손질만 한다. 1차에서 단원 글은 다 바꿨으니(`../spec.md`), 덱만 남았다.

## 규칙

- 덱 제목, 장 제목(`#`, `##`), 닫는 장의 구호("시간은 섞지 않는다")는 헤드라인이라 그대로. 문단과 불릿의 완결 문장만 해요체.
- 표 셀, mapping 그림, comic-gen YAML, 코드 블록은 그대로. 예외는 아래 "사실 오류"의 mapping 한 줄.
- 슬라이드 수 = script 수. `dsl.slides()`가 다르면 빌드를 막는다. 장을 나누면 같은 자리에 script 하나를 더 넣는다. 덱은 5~9장.
- `---`는 장 구분자. `<!-- _class: lead -->`는 `---` 바로 다음 줄. expert-ask 3장의 ```text 블록 안 `---`는 글이다(펜스를 건드리면 장이 합쳐진다).
- script는 파이썬 문자열. decks.py는 작은따옴표 문자열(안에 `'` 금지), 나머지 넷은 큰따옴표 문자열(안에 `"`는 `\"`). `-->`는 금지. 본문은 r"""…""" 이라 `"""` 연속 금지.
- 금지어(빌드 검사): uv, 폰트, 891행, 번째 보기, 교시, 일차. "오늘/내일/3일" 같은 진도 말도 쓰지 않는다(주가 덱의 "오늘 종가/내일 종가"는 내용어라 괜찮다).

## 손볼 것 (조사 결과, `../findings/decks-*.md`에 미션별 상세)

1. **합니다체 → 해요체**: 슬라이드 문단 전부(다섯 파일에 "~니다" 약 275곳). script와 같은 장에서 말투가 둘인 상태를 없앤다.
2. **"자," 줄이기**: script 첫머리의 "자,"가 decks_python_pandas·decks_eda_viz는 전부, decks_modeling_credit은 70줄 중 45줄. 덱마다 첫 장(과 마지막 장 정도)에만 남기고 중간 장은 "그럼", "그런데", "이번엔", 앞장을 받는 말("아까 그 표요,")로. decks_stock(8장 중 2~4장)이 기준.
3. **그림 밑 문단과 script의 중복**: 그림(만화·mapping·표) 아래 2~3문장 문단을 script가 그대로 다시 읽는 장(why-this-course 2·4·6장, why-pandas 4장, ml-basics 4장, time-split 2장, charts 7장, groups 4장, distribution 7장 등). 슬라이드 문단은 한두 문장(결론)으로 줄이고, script가 이유·예를 말하게 한다. 정보는 둘 중 하나에는 남긴다.
4. **빽빽한 장 7개는 두 장으로** (script도 하나 추가):
   - why-this-course "숫자로 바꾸면 이런 이야기입니다": (1) 표 + "가상의 숫자예요" 한 줄 (2) "한 달이면" 300만 원·기다리는 시간·"오차를 10%만 줄여도 남는 장사예요".
   - why-this-course "이 수업에서 다루는 자료 세 가지": (1) 표만 + "셋 다 같은 흐름으로 풀어요" (2) "같은 흐름 네 단계" 불릿 넷(파일 읽기 / 열로 갈라 X와 y / 행으로 갈라 훈련·테스트 / 기준 모델과 비교).
   - expert-ask "그럼 왜 배우나요": 불릿 넷 × 두 문장. (1) 말할 수 있다 · 누수를 알아챈다 (2) 기준과 비교한다 · 저장해서 다시 쓴다. 또는 둘째 문장(예시)을 script로 내리고 한 장에 네 줄.
   - why-pandas "그래서 아나콘다가 필요했었습니다": "왜 이 이야기를 하냐면" 문단은 script 7번이 이미 말하니 빼고 "지금은 파이썬과 pip만 있으면 돼요" 한 줄만.
   - deck-baseline "세 모델, 한 표": (1) 표 + "어느 하나가 늘 이기진 않아요. 기준보다 얼마나 나은지가 질문이에요." (2) "정확도만 보지 마세요" F1도 같이, 생존자가 적으면 전원 사망도 정확도가 높으니까.
   - deck-metrics "정밀도와 재현율은 분모가 다르다": (1) 두 행 표 + "분자는 둘 다 TP, 분모가 달라요" (2) "F1은 둘을 하나로" F1 한 행 + "둘 다 높아야 높아요". 8장 덱이라 한 장만 더 가능.
   - deck-naive "MAE: 부호를 떼고 평균, 단위는 원": (1) 빵 공장 표 + "그냥 평균 내면 +30과 −30이 지워져요. 부호를 떼고 평균 낸 게 MAE예요." (2) "MAE의 단위는 정답과 같다" 주가에선 원, "하루 평균 몇 원 빗나갔나".
5. **사실 오류 4건** (확인됨):
   - deck-charts "y축 60부터" 장: 62%와 70%를 60부터 자르면 막대가 2와 10, 다섯 배. mapping의 "두 배 차이로 보인다"와 script 6번의 "두 배"를 "몇 배"로.
   - deck-credit script 4번 "마이너스는 잘 갚은 거": 표는 -2를 "쓴 돈이 없음"으로 적는다. "-2는 안 쓴 거, -1은 제때 갚은 거, 0은 최소만, 1부터는 연체 개월 수예요."
   - deck-missing 마지막 조건 장(414행 근처) "조건마다 괄호를 칩니다": 슬라이드 코드는 `expensive`, `many` 변수에 담아 괄호가 없다. "한 줄에 바로 쓸 땐 조건마다 괄호를 쳐요. 위처럼 변수에 담으면 괄호가 필요 없어요." script 6번도 같이.
   - why-pandas: 2장 "값이 세 개면", 5장 "네 개면", 닫는 장 "네 개면", script 2번 "세 개면". holdings 예시 개수 하나로 통일.
6. **영어만 나온 용어**는 첫 등장에 괄호 한국어 한 번: F1, Logistic/Tree/Forest, AutoML, %p, 병렬, 양성, 조화평균, 속성(HTML).
7. **덱 안 ask 버튼** 어긋남: why-this-course의 '왜 "해 줘"만으로는 부족하다는 거야?'는 다음 덱(expert-ask) 내용. 이 덱 내용으로 바꾼다(`decks.py`의 ask=와 `asks.py`의 "why-this-course" 둘 다; asks.py가 우선한다).
8. 자잘한 것(`../findings/decks-*.md`): "가장 전의 달"(deck-credit), "보나는"(deck-metrics 7장 제목 비문), "위/아래"가 표의 가로 식과 안 맞음(deck-metrics 4장), 강사의 "내가"→"제가"(deck-insight), "날짜라서 날짜로"(deck-stock-data 3장), deck-wrap 5·6장 같은 마무리 문장, deck-stock-data 7장의 "401개"(다음 미션에서 학생이 셀 숫자라 뺀다).

## 검증

```bash
python tools/verify-kpc-module.py decks decks_python_pandas decks_eda_viz decks_modeling_credit decks_stock
python tools/build-kpc-course.py
node assets/slides/slides.test.mjs
cargo test --locked
python tools/kpc-prose-stats.py
```

앱에서 덱을 열어 장 수, 겹침, 우클릭 script 패널을 확인한다. 끝나면 커밋하고 `readable-voice-pass-2` 태그.
