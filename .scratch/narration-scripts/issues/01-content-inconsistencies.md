# 해설을 쓰며 발견한 본문 불일치

Status: needs-triage

해설 집필 중 본문과 실제 실행 결과가 어긋나는 곳. 고치면 같은 커밋에서 `narration_*.py`의 해당 항목(구절·출력 문장)도 고친다.

- `beat-baseline` (stock): 만화와 목표 글은 Ridge가 기준에 진다는 이야기인데, 번들 자료(ma5)에서는 Ridge MAE 13601 < 기준 13637.5라 `improved`가 True. 지는 경우는 도전 과제 `window-rematch`(ma10, 13859)에서 나온다. 본문을 "True일 수도 False일 수도" 쪽으로 손보거나 자료 창을 바꿀지 결정.
- `regression-metrics` (stock): "기준을 이기기 어렵다"고 하지만 MAE에서는 세 모델이 모두 기준을 이긴다(8~117원). RMSE에서는 기준이 가장 낮다(17408 vs 17581~17766). 본문에 이 대비를 넣으면 학생이 보는 숫자와 맞는다.
- `get-dummies` (modeling): 목표는 "둘 중 하나만 1"인데 현재 pandas는 True/False를 보여 준다. 검사기는 `astype(int)`로 처리. 본문을 True/False로 고치거나 `dtype=int`를 쓸지 결정.
- `model-comparison` (modeling): 목표에 Tree의 `max_depth=4`가 없는데 정답은 4를 쓴다(도전 과제는 5). 목표 글에 적어 주기.
- `age-hist`, `pclass-bar`, `fare-scatter` (visualization): 힌트는 한글 제목·축 이름인데 정답은 영어(`'Passenger count'`, `'Survival by class'`, `'Age vs fare'`). 한쪽으로 맞추기.
- `string-to-int` (pandas): 목표는 "수집의 네 단계 중 세 번째"인데 만화는 변환을 4단계로 그린다.
- `saved-prices` (stock): 같은 이야기의 만화 두 편("결정하는 시각에 아는 것만", "새벽 3시의 결정"). 하나 줄이기.
- `sex-summary`·`pclass-summary`·`age-groups` (eda): 힌트는 `['count', 'sum', 'mean']`, 정답은 띄어쓰기 없음. 표기만 다름.
- `threshold-cost` (credit): `max_iter=1000`, 8교시 미션들은 2000. 결과는 같음.

고친 것(2026-10-05): `lag-target` 만화 제목 방향 반대 → "아래로 밀면 어제, 위로 밀면 내일"; `distribution-types` 코드 주석 4번 중복; `leakage` "넷은 숫자" → "다섯은 숫자"; `tune-depth` 출력의 `np.float64(...)` → `float()`.
