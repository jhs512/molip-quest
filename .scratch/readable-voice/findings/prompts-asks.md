# 1차 조사 결과 · prompts-asks

조사자가 찾은 이상한 곳이에요. 예시 fix는 참고용이고, 같은 목소리로 더 낫게 써도 돼요. 미션마다 severity(0~3).


## prompts.py (99 missions)


### hello · prompt · severity 0

### print-calc · prompt · severity 0

### variable-print · prompt · severity 0

### single-input · prompt · severity 0

### amount-input · prompt · severity 0

### fstring-report · prompt · severity 0

### list-index · prompt · severity 0

### list-len-sum · prompt · severity 0

### dict-read · prompt · severity 0

### holdings-access · prompt · severity 0

### holding · prompt · severity 0

### price-average · prompt · severity 0

### simple-if · prompt · severity 0

### for-sum · prompt · severity 0

### above-count · prompt · severity 0

### max-price · prompt · severity 0

### croissant-plan · prompt · severity 1
- [long] 전: for로 합계를 total에 누적(sum 금지), 평균을 average에, 평균의 1.1배를 round한 정수를 plan에 담아 "오늘 생산 계획: 460개" 형식으로 출력.
  후: for로 합계를 total에 누적(sum 금지), 평균을 average에.
평균의 1.1배를 round한 정수를 plan에 담아 "오늘 생산 계획: 460개" 형식으로 출력.

### holdings-amounts · prompt · severity 0

### holdings-total · prompt · severity 0

### holdings-frame · prompt · severity 0

### frame-column-sum · prompt · severity 0

### numpy-race · prompt · severity 1
- [long] 전: - `time.perf_counter()` → 시간 재는 함수를 지정해야 `time.time()`처럼 거친 시계를 안 쓴다.
  후: - `time.perf_counter()` → 시간 재는 함수를 지정. 안 적으면 `time.time()`처럼 거친 시계를 써요.

### inspect-frame · prompt · severity 0

### to-csv · prompt · severity 0

### csv-excel · prompt · severity 0

### series-vs-frame · prompt · severity 0

### selection · prompt · severity 0

### loc-condition · prompt · severity 1
- [jargon] 전: - `불리언 마스크` → `orders[orders['quantity'] >= 3]`. 조건으로 행을 고르는 표준 용어.
  후: - `불리언 마스크` → 행마다 참·거짓을 매겨 참인 행만 남기기. `orders[orders['quantity'] >= 3]`. 수업에서 "참·거짓 표"라고 부른 그거예요.

### read-csv-titanic · prompt · severity 0

### count-missing · prompt · severity 0

### fill-median · prompt · severity 0

### drop-missing · prompt · severity 0

### filter-orders · prompt · severity 0

### or-filter · prompt · severity 0

### missing-totals · prompt · severity 1
- [long] 전: 결측을 중앙값으로 채운 표를 filled, 결측 행을 뺀 표를 dropped에 만들고, 각 표에 price*quantity 열 amount를 추가해 합계를 filled_total, dropped_total에 담아 둘 다 출력.
  후: pandas. orders(price 결측 1개).
결측을 중앙값으로 채운 표를 filled, 결측 행을 뺀 표를 dropped에.
각 표에 price*quantity 열 amount를 추가해 합계를 filled_total, dropped_total에 담아 둘 다 출력.
둘 다 원본은 건드리지 말고 .copy().

### string-to-int · prompt · severity 0

### select-one · prompt · severity 0

### select-prices · prompt · severity 0

### parse-html · prompt · severity 1
- [long] 전: 파이썬 BeautifulSoup + pandas. data/prices.html을 읽어 soup를 만들고, "#prices li"를 돌면서 data-code 속성, .name 텍스트, b 텍스트(쉼표 제거 후 int)를 딕셔너리로 rows 리스트에 모은 뒤 pd.DataFrame(rows)를 df에. 열 이름 code, name, price.
  후: 파이썬 BeautifulSoup + pandas. data/prices.html을 읽어 soup를 만들어.
"#prices li"를 돌면서 data-code 속성, .name 텍스트, b 텍스트(쉼표 제거 후 int)를 딕셔너리로 rows 리스트에 모아.
pd.DataFrame(rows)를 df에. 열 이름 code, name, price.

### titanic-shape · prompt · severity 0

### survived-counts · prompt · severity 0

### missing-per-column · prompt · severity 0

### titanic-counts · prompt · severity 0

### sex-counts · prompt · severity 0

### sex-mean · prompt · severity 0

### sex-summary · prompt · severity 0

### pclass-summary · prompt · severity 1
- [unclear] 전: pandas. titanic DataFrame. 객실등급로 groupby한 생존에 agg(['count','sum','mean'])을 적용해 pclass_summary에.
  후: pandas. titanic DataFrame. 객실등급으로 groupby한 생존에 agg(['count','sum','mean'])을 적용해 pclass_summary에.
- [unclear] 전: - 앞 프롬프트에서 `성별`을 `객실등급`로만 바꿈. 같은 집계는 프롬프트도 복사해서 쓴다.
  후: - 앞 프롬프트에서 `성별`을 `객실등급`으로만 바꿈. 같은 집계는 프롬프트도 복사해서 써요.

### age-groups · prompt · severity 1
- [long] 전: pd.cut으로 나이를 bins=[0, 20, 40, 60, float('inf')], labels=['0~19','20~39','40~59','60+'], right=False 로 나눈 열 age_group을 titanic에 추가하고, age_group으로 groupby한 생존의 agg(['count','sum','mean'])을 age_summary에.
  후: pandas. titanic DataFrame.
pd.cut으로 나이를 bins=[0, 20, 40, 60, float('inf')], labels=['0~19','20~39','40~59','60+'], right=False 로 나눈 열 age_group을 titanic에 추가.
age_group으로 groupby한 생존의 agg(['count','sum','mean'])을 age_summary에.

### simple-bar · prompt · severity 0

### sex-bar · prompt · severity 0

### pclass-bar · prompt · severity 0

### age-hist · prompt · severity 0

### fare-scatter · prompt · severity 0

### correlation · prompt · severity 0

### embarked-rate · prompt · severity 0

### sex-pclass-table · prompt · severity 0

### combined-groups · prompt · severity 0

### drop-columns · prompt · severity 0

### xy-separation · prompt · severity 0

### column-types · prompt · severity 0

### get-dummies · prompt · severity 0

### stratified-split · prompt · severity 0

### first-model · prompt · severity 0

### train-imputer · prompt · severity 0

### onehot-fit · prompt · severity 0

### pipeline-build · prompt · severity 0

### dummy-only · prompt · severity 0

### model-comparison · prompt · severity 1
- [unclear] 전: - `max_depth`, `random_state` → 재현성.
  후: - `max_depth=5`, `random_state=42` → 조건을 못 박아야 누가 돌려도 같은 표가 나와요. 깊이는 재현성이 아니라 "같은 조건"이에요.

### train-vs-test · prompt · severity 0

### save-and-load · prompt · severity 1
- [tone] 전: 타이타닉 생존 분류. 손질기 make_preprocessor()와 LogisticRegression(max_iter=1000)을 Pipeline으로 묶어 model에 fit.
  후: scikit-learn. X_train, X_test, y_train, y_test, make_preprocessor()가 있어. make_preprocessor()와 LogisticRegression(max_iter=1000)을 Pipeline으로 묶어 model에 fit.

### tune-depth · prompt · severity 1
- [tone] 전: 타이타닉 생존 분류. depths = [2, 3, 5, 8, 12] 후보마다 make_preprocessor()와 DecisionTreeClassifier(max_depth=깊이, random_state=42)를 Pipeline으로 묶고
  후: scikit-learn. X_train, X_test, y_train, y_test, make_preprocessor()가 있어. depths = [2, 3, 5, 8, 12] 후보마다 make_preprocessor()와 DecisionTreeClassifier(max_depth=깊이, random_state=42)를 Pipeline으로 묶고

### credit-shape · prompt · severity 0

### default-summary · prompt · severity 1
- [jargon] 전: - `고객번호 … drop` → 고객 번호는 식별자. 넣으면 모델이 번호를 외운다.
  후: - `고객번호 … drop` → 고객 번호는 이름표일 뿐이에요. 넣으면 모델이 번호를 외워요.

### limit-by-default · prompt · severity 1
- [unclear] 전: pandas. credit DataFrame, target 변수에 타깃 열 이름. target으로 groupby한 신용한도의 mean을 limit_by_default에 담고 출력.
  후: pandas. credit DataFrame이 있고 target에 타깃 열 이름이 들어 있어. target으로 groupby한 신용한도의 mean을 limit_by_default에 담고 출력.

### delay-groups · prompt · severity 0

### pay0-rate · prompt · severity 0

### manual-metrics · prompt · severity 0

### metrics-matrix · prompt · severity 0

### credit-model · prompt · severity 1
- [long] 전: 각각 Pipeline([('scale', StandardScaler()), ('model', m)])로 fit/predict해서 accuracy, precision, recall, f1 네 지표를 구하고 모델 이름을 인덱스로 한 DataFrame results를 만들어.
  후: scikit-learn. X_train, X_test, y_train, y_test가 있어(입력 상환_9월, 신용한도, 나이).
models = {'Dummy': DummyClassifier(strategy='most_frequent'), 'Logistic': LogisticRegression(max_iter=1000)}.
각각 Pipeline([('scale', StandardScaler()), ('model', m)])로 fit/predict해서 accuracy, precision, recall, f1 네 지표를 구해.
모델 이름을 인덱스로 한 DataFrame results를 만들어. precision은 zero_division=0.

### predict-proba · prompt · severity 0

### thresholds · prompt · severity 1
- [jargon] 전: - `(p >= 0.5).astype(int)` → 임계값 적용을 벡터 연산 한 줄로. `int`까지 맞춰야 채점 통과.
  후: - `(probabilities >= 0.5).astype(int)` → 임계값을 배열 전체에 한 번에 적용. `int`까지 맞춰야 채점을 통과해요.

### stock-load · prompt · severity 0

### close-plot · prompt · severity 0

### price-range · prompt · severity 0

### daily-return · prompt · severity 0

### moving-average · prompt · severity 0

### lag-next · prompt · severity 0

### stock-frame · prompt · severity 1
- [long] 전: frame에 close(종가), return_1(pct_change), ma5(rolling(5).mean()), lag_close_1(shift(1)), target_next_close(shift(-1)), target_date(pd.Series(prices.index, index=prices.index).shift(-1)) 여섯 열을 만들고 frame = frame.dropna().copy().
  후: pandas. prices(날짜 인덱스, 종가 열)와 빈 frame=pd.DataFrame(index=prices.index)가 있어.
frame에 여섯 열: close(종가), return_1(pct_change), ma5(rolling(5).mean()), lag_close_1(shift(1)), target_next_close(shift(-1)), target_date(pd.Series(prices.index, index=prices.index).shift(-1)).
frame = frame.dropna().copy(). 396행이어야 해.

### test-start · prompt · severity 0

### time-boundary · prompt · severity 1
- [long] 전: 입력 날짜와 target_date가 둘 다 test_start 전인 행을 train_mask, 입력 날짜가 test_start 이상인 행을 test_mask로 만들고, feature_columns=['close','return_1','ma5','lag_close_1']로 X_train, X_test, y_train(target_next_close), y_test 만들어.
  후: pandas. frame(날짜 인덱스, 열 close, return_1, ma5, lag_close_1, target_next_close, target_date). test_start = frame.index[-80].
입력 날짜와 target_date가 둘 다 test_start 전인 행을 train_mask, 입력 날짜가 test_start 이상인 행을 test_mask로.
feature_columns=['close','return_1','ma5','lag_close_1']로 X_train, X_test, y_train(target_next_close), y_test 만들어.
두 쪽 행 수 출력(훈련 315, 테스트 80).
- [long] 전: - `target_date도 test_start 전` → 이 조건이 없으면 테스트 첫날 정답을 훈련에서 본다(경계 누수). AI는 거의 항상 빼먹는다.
  후: - `target_date도 test_start 전` → 없으면 테스트 첫날 정답을 훈련에서 봐요(경계 누수). AI가 거의 항상 빼먹어요.

### manual-mae · prompt · severity 1
- [jargon] 전: - `내일 종가 = 오늘 종가` → naive 기준 예측.
  후: - `내일 종가 = 오늘 종가` → 가장 단순한 기준 모델("내일은 오늘과 같다").

### close-baseline · prompt · severity 0

### callcenter-baseline · prompt · severity 0

### linear-only · prompt · severity 1
- [jargon] 전: - `temporal split 완료` → 다시 섞지 말라는 뜻.
  후: - `temporal split 완료` → 시간 순서로 이미 나눴으니 다시 섞지 말라는 뜻.

### regression-table · prompt · severity 2
- [long] 전: 각각 StandardScaler와 Pipeline으로 fit해서 fitted 딕셔너리에 보관하고 테스트 예측을 predictions 딕셔너리에 모아.
  후: scikit-learn. X_train, X_test, y_train, y_test(temporal split).
models = {'Linear': LinearRegression(), 'Ridge': Ridge(alpha=1), 'Lasso': Lasso(alpha=10, max_iter=20000, tol=0.001)}.
각각 StandardScaler와 Pipeline으로 fit해서 fitted 딕셔너리에 보관하고 테스트 예측을 predictions 딕셔너리에 모아.
predictions['Baseline']은 X_test['close'] 값.
네 예측 각각 MAE, RMSE, R2를 구해 인덱스가 모델 이름, 열이 MAE, RMSE, R2인 DataFrame results를 만들어. RMSE는 mean_squared_error의 제곱근.
- [unclear] 전: - `alpha=…` → 재현성.
  후: - `alpha=…` → 브레이크 세기. 숫자를 정해 줘야 누가 돌려도 같은 표가 나와요.

### beat-baseline · prompt · severity 1
- [long] 전: - `False여도 그대로 둬` → "개선"을 요구하면 AI는 기간이나 매개변수를 바꿔 이기는 결과를 만든다. 정직한 비교.
  후: - `False여도 그대로 둬` → "개선"을 요구하면 AI는 기간이나 매개변수를 바꿔서라도 이기는 결과를 만들어요. 정직한 비교가 먼저예요.

### forecast-plot · prompt · severity 0

### final-report · prompt · severity 1
- [long] 전: 각 모델을 StandardScaler Pipeline으로 fit해 테스트 MAE를 maes 딕셔너리에 모으고, 기준(X_test['close']) MAE와 비교해 report 딕셔너리를 만들어.
  후: scikit-learn. X_train, X_test, y_train, y_test(temporal split, 테스트 80거래일), models = {'Linear': ..., 'Ridge': ...}가 있어.
각 모델을 StandardScaler Pipeline으로 fit해 테스트 MAE를 maes 딕셔너리에 모아.
기준(X_test['close']) MAE와 비교해 report 딕셔너리를 만들어. 키: test_days, baseline_mae, best_model(MAE 최소 모델 이름), best_mae, improved(best_mae < baseline_mae).
결론 세 줄 출력: ① 무엇을 언제 예측했고 어떻게 나눴는지 ② 기준 MAE와 최선 MAE ③ 개선 여부. improved가 False면 그대로 적어.

### rate-by-attribute · prompt · severity 1
- [long] 전: - `bins, right=False, labels` → 구간의 경계와 이름을 지정하지 않으면 AI가 임의로 자른다.
  후: - `bins, right=False, labels` → 구간 경계와 이름을 안 정해 주면 AI가 멋대로 잘라요.

## asks.py (162 missions)


### why-this-course · ask · severity 0

### runtime · ask · severity 0

### hello · ask · severity 0

### numbers-text · ask · severity 0

### print-calc · ask · severity 0

### variable-print · ask · severity 0

### single-input · ask · severity 0

### read-input · ask · severity 0

### amount-input · ask · severity 0

### fstring-report · ask · severity 0

### tools · ask · severity 0

### values · ask · severity 0

### list-index · ask · severity 0

### list-len-sum · ask · severity 0

### dict-read · ask · severity 0

### holdings-access · ask · severity 0

### holding · ask · severity 0

### price-average · ask · severity 0

### structure-check · ask · severity 0

### flow · ask · severity 0

### simple-if · ask · severity 0

### for-sum · ask · severity 0

### above-count · ask · severity 0

### max-price · ask · severity 0

### croissant-plan · ask · severity 0

### holdings-amounts · ask · severity 0

### holdings-total · ask · severity 1
- [unclear] 전: for-sum 미션과 뭐가 같고 뭐가 달라?
  후: 앞의 '반복문으로 합계 누적하기'와 뭐가 같고 뭐가 달라?

### first-dataframe · ask · severity 0

### holdings-frame · ask · severity 0

### frame-column-sum · ask · severity 0

### why-pandas · ask · severity 0

### why-fast · ask · severity 0

### numpy-race · ask · severity 0

### control-check · ask · severity 0

### week-plan · ask · severity 0

### file-table · ask · severity 0

### inspect-frame · ask · severity 1
- [unclear] 전: n_rows, n_columns = orders.shape가 어떻게 돼?
  후: n_rows, n_columns = orders.shape 한 줄로 어떻게 둘 다 들어가?

### to-csv · ask · severity 0

### csv-excel · ask · severity 0

### series-vs-frame · ask · severity 0

### selection · ask · severity 0

### loc-condition · ask · severity 0

### read-csv-titanic · ask · severity 0

### files-check · ask · severity 0

### missing-values · ask · severity 0

### count-missing · ask · severity 0

### fill-median · ask · severity 0

### drop-missing · ask · severity 0

### filter-orders · ask · severity 0

### or-filter · ask · severity 0

### missing-totals · ask · severity 0

### missing-check · ask · severity 0

### html-selectors · ask · severity 0

### string-to-int · ask · severity 0

### select-one · ask · severity 0

### select-prices · ask · severity 0

### parse-html · ask · severity 0

### html-check · ask · severity 0

### croissant-clean · ask · severity 0

### target · ask · severity 0

### titanic-shape · ask · severity 0

### survived-counts · ask · severity 0

### missing-per-column · ask · severity 0

### titanic-counts · ask · severity 0

### target-check · ask · severity 0

### denominator · ask · severity 0

### sex-counts · ask · severity 0

### sex-mean · ask · severity 0

### sex-summary · ask · severity 0

### pclass-summary · ask · severity 0

### age-groups · ask · severity 0

### groups-check · ask · severity 0

### family-survival · ask · severity 0

### axes · ask · severity 0

### simple-bar · ask · severity 0

### sex-bar · ask · severity 0

### pclass-bar · ask · severity 0

### bar-check · ask · severity 0

### distribution-types · ask · severity 0

### age-hist · ask · severity 0

### fare-scatter · ask · severity 0

### correlation · ask · severity 0

### distribution-check · ask · severity 0

### observations · ask · severity 0

### embarked-rate · ask · severity 0

### sex-pclass-table · ask · severity 0

### combined-groups · ask · severity 0

### insight-check · ask · severity 0

### two-charts · ask · severity 0

### ml-basics · ask · severity 0

### what-is-learning · ask · severity 0

### leakage · ask · severity 0

### drop-columns · ask · severity 0

### xy-separation · ask · severity 0

### column-types · ask · severity 0

### get-dummies · ask · severity 0

### features-check · ask · severity 0

### fit-train · ask · severity 0

### stratified-split · ask · severity 0

### first-model · ask · severity 0

### train-imputer · ask · severity 0

### onehot-fit · ask · severity 0

### why-pipeline · ask · severity 0

### pipeline-build · ask · severity 0

### pipeline-check · ask · severity 0

### baselines · ask · severity 0

### dummy-only · ask · severity 0

### model-comparison · ask · severity 0

### train-vs-test · ask · severity 0

### hyperparameters · ask · severity 0

### tune-depth · ask · severity 0

### save-model · ask · severity 0

### save-and-load · ask · severity 0

### model-check · ask · severity 0

### full-comparison · ask · severity 0

### credit-definition · ask · severity 0

### credit-shape · ask · severity 1
- [unclear] 전: 열 이름에 공백이 있으면 왜 변수로 꺼내?
  후: 열 이름에 공백이 있으면 왜 변수에 담아 둬?

### default-summary · ask · severity 0

### limit-by-default · ask · severity 0

### delay-groups · ask · severity 0

### pay0-rate · ask · severity 0

### credit-check · ask · severity 0

### manual-metrics · ask · severity 0

### metrics-matrix · ask · severity 0

### credit-model · ask · severity 0

### predict-proba · ask · severity 0

### thresholds · ask · severity 0

### metrics-check · ask · severity 0

### threshold-cost · ask · severity 0

### saved-prices · ask · severity 0

### stock-load · ask · severity 0

### close-plot · ask · severity 0

### price-range · ask · severity 0

### stock-data-check · ask · severity 0

### lag-target · ask · severity 0

### daily-return · ask · severity 0

### moving-average · ask · severity 0

### lag-next · ask · severity 0

### stock-frame · ask · severity 0

### feature-time-check · ask · severity 0

### time-split · ask · severity 0

### temporal-boundary · ask · severity 0

### test-start · ask · severity 0

### time-boundary · ask · severity 2
- [fact] 전: 왜 315가 아니라 316이 아니야?
  후: 왜 316이 아니라 315야?

### manual-mae · ask · severity 0

### close-baseline · ask · severity 0

### callcenter-baseline · ask · severity 0

### temporal-check · ask · severity 0

### regression-metrics · ask · severity 0

### linear-only · ask · severity 0

### regression-table · ask · severity 0

### midpoint · ask · severity 0

### beat-baseline · ask · severity 0

### forecast-plot · ask · severity 0

### final-report · ask · severity 0

### final-check · ask · severity 0

### course-wrap · ask · severity 0

### window-rematch · ask · severity 0

### environment-tools · ask · severity 0

### live-web · ask · severity 0

### fetch-prices · ask · severity 0

### rate-by-attribute · ask · severity 0
