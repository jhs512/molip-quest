# 1차 조사 결과 · stock-b

조사자가 찾은 이상한 곳이에요. 예시 fix는 참고용이고, 같은 목소리로 더 낫게 써도 돼요. 미션마다 severity(0~3).


## d3_p3_stock_split.py (7 missions)


### temporal-boundary · concept · severity 2
- 메모: 내용은 좋고 문단 흐름도 맞음. 손볼 곳은 '~것은/~것이라' 명사절과 45자 넘는 문장 셋. 마지막 문단이 기준 모델과 MAE 두 생각을 한 문단에 담고 있어 둘로 나누면 읽기 편함(anchor '나눴으면 기준 모델입니다'는 앞 문단 첫 문장으로 남김). 만화 둘('섞으면 점쟁이가 된다', '시간은 섞지 않는다')이 같은 6월/3월 이야기를 반복하지만 만화는 대상 아님, 참고만. check 해설은 합니다체만 바꾸면 됨.
- [stiff] 전: 분류의 "전원 사망"에 해당하는 가장 단순한 예측은 **"내일 종가는 오늘 종가와 같다"**입니다.
  후: 분류의 "전원 사망" 자리에 오는 가장 단순한 예측이 뭘까요? **"내일 종가는 오늘 종가와 같다"**예요.
- [long] 전: 입력 날짜는 테스트 전이니 훈련에 들어가도 될 것 같지만, 그 행의 **정답**은 `test_start` 당일의 종가입니다.
  후: 입력 날짜는 테스트 전이라 훈련에 넣어도 될 것 같죠? 그런데 그 행의 **정답**은 `test_start` 당일 종가예요.
- [long] 전: 예측과 정답의 차이를 부호 없이 평균 낸 것이라 단위가 원이고, "평균적으로 몇 원 빗나갔나"로 읽으면 됩니다.
  후: 예측과 정답의 차이를 부호 없이 평균 낸 거예요. 그래서 단위가 원이에요. "평균 몇 원 빗나갔나"로 읽으면 돼요.
- [stiff] 전: 앞 단원에서 `target_date`를 남겨 둔 이유가 이것입니다.
  후: 앞 단원에서 `target_date`를 남겨 둔 이유가 바로 이거예요.
- [stiff] 전: 미래를 보고 과거를 맞히는 것은 시험이 아닙니다.
  후: 미래를 보고 과거를 맞히면 그건 시험이 아니죠.
- [stiff] 전: 테스트가 시작되는 날을 `test_start`라고 합시다.
  후: 테스트가 시작되는 날을 `test_start`라고 할게요.
- [long] 전: "내일 종가는 오늘 종가와 같다"처럼 가장 단순한 예측을 두고 모델과 비교하는 것을 무엇이라고 하나요?
  후: "내일 종가는 오늘 종가와 같다"처럼 가장 단순한 예측을 두고 모델과 비교해요. 이걸 뭐라고 하나요?

### test-start · coding · severity 1
- 메모: 목표는 짧고 분명함. 힌트 둘째 문장만 세 절로 길다.
- [long] 전: `frame.index >= test_start`는 행마다 참·거짓이고 `.sum()`이 참의 개수, `int()`로 감싸 정수로 저장하세요.
  후: `frame.index >= test_start`는 행마다 참·거짓이에요. `.sum()`이 참의 개수죠. `int()`로 감싸 정수로 저장하세요.
- [stiff] 전: `n_test`가 80이면 맞게 정한 것입니다.
  후: `n_test`가 80이면 맞게 정한 거예요.

### time-boundary · coding · severity 2
- 메모: 목표 둘째 문장이 127자에 변수 일곱 개를 한 호흡에 나열해 이 그룹에서 가장 긴 문장. 지시문 안에 '출력합니다'가 섞여 지시인지 설명인지 흐림. 백틱 안 쉼표(`X_train`, `X_test`...)는 그대로 두고 백틱 바깥에서만 자를 것.
- [long] 전: `test_start`를 정하고, 입력 날짜와 `target_date`가 **모두** `test_start` 전인 행을 `train_mask`, 입력 날짜가 `test_start` 이상인 행을 `test_mask`로 만든 뒤 `X_train`, `X_test`, `y_train`, `y_test`를 만드세요.
  후: `test_start`를 정하세요. 입력 날짜와 `target_date`가 **모두** `test_start` 전인 행이 `train_mask`예요. 입력 날짜가 `test_start` 이상인 행이 `test_mask`고요. 그걸로 `X_train`, `X_test`, `y_train`, `y_test`를 만드세요.
- [tone] 전: 두 쪽의 행 수를 출력합니다.
  후: 두 쪽의 행 수를 출력하세요.
- [long] 전: `X.loc[train_mask]`, `y.loc[train_mask]`처럼 같은 마스크로 입력과 정답을 함께 골라야 행이 어긋나지 않습니다.
  후: `X.loc[train_mask]`, `y.loc[train_mask]`처럼 같은 마스크로 입력과 정답을 함께 고르세요. 그래야 행이 안 어긋나요.
- [stiff] 전: 두 조건을 괄호로 감싸 `&`로 잇는 것은 앞서 배운 것과 같습니다.
  후: 두 조건을 괄호로 감싸 `&`로 이어요. 앞에서 배운 그대로예요.
- [stiff] 전: 396행이 훈련 315, 경계 하루 제외 1, 테스트 80으로 나뉘면 맞게 한 것입니다.
  후: 396행이 훈련 315, 경계 하루 제외 1, 테스트 80으로 나뉘면 맞게 한 거예요.

### manual-mae · coding · severity 1
- 메모: 위젯과 만화가 앞에 있어 흐름이 좋음. 목표 한 문장이 길고 힌트 끝 문장이 '~뿐입니다'로 딱딱한 정도.
- [long] 전: 정답 `y_test`와의 차이에 `.abs()`를 붙인 것을 `errors`에, 그 평균을 `manual_mae`에 저장하고 출력하세요.
  후: 정답 `y_test`와의 차이에 `.abs()`를 붙여 `errors`에 담으세요. 그 평균을 `manual_mae`에 저장하고 출력하세요.
- [stiff] 전: MAE라는 이름이 붙어 있지만 하는 일은 "차이의 절댓값을 평균 낸다" 두 단계뿐입니다.
  후: MAE라는 이름은 거창한데, 하는 일은 "차이의 절댓값을 평균 낸다" 두 단계뿐이에요.

### close-baseline · coding · severity 1
- 메모: 목표 둘째 문장이 107자(대부분 코드). 백틱 바깥 쉼표에서 둘로 자르면 끝. 나머지는 합니다체만.
- [long] 전: 기준 예측 `X_test['close']`를 배열로 바꿔 `baseline_pred`에 저장하고, `mean_absolute_error(y_test, baseline_pred)`를 `baseline_mae`에 담아 출력하세요.
  후: 기준 예측 `X_test['close']`를 배열로 바꿔 `baseline_pred`에 저장하세요. 그리고 `mean_absolute_error(y_test, baseline_pred)`를 `baseline_mae`에 담아 출력하세요.

### callcenter-baseline · coding · severity 2
- 메모: intro가 왜 푸는지를 잘 말해 주는 좋은 예. 다만 '준비되어 있습니다', '~이므로', 85자 문장이 각각 intro·goal·hint에 하나씩. 마지막 '월요일만 보면 어떤가요?'는 좋은 질문형이라 그대로.
- [long] 전: 1주차 값을 2주차 예측으로 쓰는 것이 기준 모델이니, `mean_absolute_error(this_week, last_week)`를 `baseline_mae`에 담아 출력하세요.
  후: 1주차 값을 2주차 예측으로 쓰는 게 기준 모델이에요. 그러니 `mean_absolute_error(this_week, last_week)`를 `baseline_mae`에 담아 출력하세요.
- [stiff] 전: 어느 카드사 콜센터의 2주치 일별 통화량이 준비되어 있습니다.
  후: 어느 카드사 콜센터의 2주치 일별 통화량이 준비돼 있어요.
- [stiff] 전: 지표 함수는 `(정답, 예측)` 순서이므로 정답은 `this_week`, 예측은 `last_week`입니다.
  후: 지표 함수는 `(정답, 예측)` 순서예요. 그러니 정답은 `this_week`, 예측은 `last_week`.
- [stiff] 전: 이 방법이 얼마나 빗나가는지가, 통화량 예측 모델이 넘어야 할 선입니다.
  후: 이 방법이 얼마나 빗나가는지가 통화량 예측 모델이 넘어야 할 선이에요.

### temporal-check · quiz · severity 2
- 메모: 7문항. 해설은 대체로 짧고 좋음. 영어 'temporal split'이 수업 말 '시간 분리'(단원 제목·해설)와 어긋나고, 마지막 프롬프트 문항의 '값이 달라지는 습관이다'는 한 번 읽어서 뜻이 안 잡힘. '다른 보기는 왜 아닌가'의 '~다'는 해요체로만.
- [jargon] 전: 정답은 temporal split에 더해 "target_date도 test_start 전"이라는 경계 조건을 적었습니다.
  후: 정답은 시간 분리에 더해 "target_date도 test_start 전"이라는 경계 조건을 적었어요.
- [unclear] 전: MAE는 같아도 다른 지표에서는 값이 달라지는 습관이다.
  후: MAE는 값이 같지만, 이 버릇은 다른 지표에서 값을 바꿔요.
- [stiff] 전: 미래 가격으로 훈련해 과거를 맞히게 되어 점수를 믿을 수 없다
  후: 미래 가격으로 훈련해 과거를 맞히게 돼서 점수를 믿을 수 없다
- [stiff] 전: MAE가 1500이라는 것은 무슨 뜻인가요?
  후: MAE가 1500이면 무슨 뜻인가요?
- [stiff] 전: 모델이 이 오차보다 작아야 무언가 배운 것이라는 선
  후: 모델이 이 오차보다 작아야 뭔가 배운 거라는 선

## d3_p4_regression_project.py (9 missions)


### regression-metrics · concept · severity 3
- 메모: 내용은 정확하고 비유도 수업 것(빵 공장·콜센터·모의고사)이라 그대로 살림. 그러나 45자 넘는 문장이 9개로 다섯 문단 모두에 걸쳐 있고, '~것이고/~것입니다/~라는 것입니다' 명사절이 문단마다 나와 문장 단위로 전부 다시 써야 함. 8개 밖의 손볼 곳: '입력 크기가 제각각이면 브레이크가 공평하지 않으니 분류에서처럼 `StandardScaler`와 묶어 씁니다.'(49자), '가중치가 너무 커지면 벌점을 매겨, 훈련 자료의 우연한 흔들림까지 외우는 것을 막습니다.'(것을), check 프롬프트 '...큰 실수에 더 민감한 것의 약어는 무엇인가요?'(것의), check 해설 '큰 오차가 더 크게 반영됩니다'(피동). 둘째 문단은 선형 회귀 → 릿지·라쏘 → 스케일러 세 생각 일곱 문장이라 두 문단으로 나눌 후보(anchor '선형 회귀(LinearRegression)는 입력마다 가중치를 곱해'는 첫 문단에 남김). 크루아상 MAE 30개 설명이 만화1·본문·만화2에서 세 번 나옴(만화는 그대로, 본문 첫 문장만 줄일 여지). anchor 8개 중 본문 앞머리 anchor 5개가 전부 바뀌니 narration_stock_b.py를 같이.
- [long] 전: 입력 네 열(오늘 종가, 수익률, 5일 평균, 어제 종가)로 내일 종가를 맞히는 회귀 모델을 세 개 돌리고, 앞 단원의 기준과 비교해서 결론을 씁니다.
  후: 입력은 네 열이에요. 오늘 종가, 수익률, 5일 평균, 어제 종가. 이걸로 내일 종가를 맞히는 회귀 모델을 세 개 돌려요. 그리고 앞 단원의 기준과 비교해서 결론을 써요.
- [unclear] 전: 월요일 통화량 예측이 100통 빗나가면 자리가 비어 통화가 밀리거나, 반대로 고객이 대기음을 10분씩 듣습니다.
  후: '반대로' 앞뒤가 반대가 아니에요(둘 다 상담원이 모자란 상황). 앞 단원 intro의 '밀리거나 비는지'에 맞춰: 월요일 통화량 예측이 100통 빗나가면요? 상담원이 모자라 고객이 대기음을 10분씩 듣거나, 반대로 상담원이 남아 자리가 비어요.
- [long] 전: 주의할 점은 R²의 비교 대상이 "평균으로 찍기"이지 우리의 기준 "오늘 종가 그대로"가 아니라는 것입니다.
  후: 주의하세요. R²의 비교 대상은 "평균으로 찍기"예요. 우리 기준 "오늘 종가 그대로"가 아니에요.
- [long] 전: 테스트 점수가 마음에 안 든다고 테스트 기간을 바꿔 가며 다시 돌리는 것은, 모의고사 문제를 바꿔 가며 점수 좋은 것만 고르는 일입니다.
  후: 테스트 점수가 마음에 안 든다고 기간을 바꿔 가며 다시 돌리면요? 모의고사 문제를 바꿔 가며 좋은 점수만 고르는 거예요.
- [long] 전: 어느 지표를 더 무겁게 볼지는 "가끔 크게 틀리는 것"과 "늘 조금씩 틀리는 것" 중 어느 쪽이 현장에서 더 비싼지에 달려 있습니다.
  후: 어느 지표를 더 무겁게 볼까요? "가끔 크게 틀리기"와 "늘 조금씩 틀리기" 중 현장에서 더 비싼 쪽을 보면 돼요.
- [stiff] 전: 입력이 하나면 점들 사이에 가장 잘 맞는 직선을 긋는 것이고, 넷이면 네 방향으로 기울어진 판을 맞추는 것입니다.
  후: 입력이 하나면 점들 사이에 가장 잘 맞는 직선을 그어요. 넷이면 네 방향으로 기울어진 판을 맞추는 거예요.
- [long] 전: 평소에는 20개쯤 빗나가다가 명절 전날 하루만 300개 틀리는 모델은 MAE는 그럭저럭이지만 RMSE가 크게 뜁니다.
  후: 평소엔 20개쯤 빗나가다가 명절 전날 하루만 300개 틀리는 모델이 있다고 해요. MAE는 그럭저럭인데 RMSE가 크게 뛰어요.
- [jargon] 전: **RMSE**는 차이를 제곱해 평균 낸 뒤 제곱근을 씌운 것이라 단위는 같은 원이지만 **큰 실수에 더 민감**합니다.
  후: **RMSE**(평균 제곱근 오차)는 차이를 제곱해 평균 낸 뒤 제곱근을 씌워요. 단위는 같은 원인데 **큰 실수에 더 민감**해요. (R²도 덱처럼 '결정계수'를 괄호에)

### linear-only · coding · severity 1
- 메모: 힌트의 '→' 흐름은 짧고 좋음. 목표 첫 문장의 '`model`에 학습하세요'가 어색하고 둘째 문장이 85자.
- [long] 전: 테스트 예측을 `prediction`, MAE를 `linear_mae`에 저장해 출력하고, `model.named_steps['model'].coef_`로 가중치 네 개도 출력하세요.
  후: 테스트 예측을 `prediction`, MAE를 `linear_mae`에 저장해 출력하세요. `model.named_steps['model'].coef_`로 가중치 네 개도 출력하세요.
- [unclear] 전: `StandardScaler`와 `LinearRegression`을 `Pipeline`으로 묶어 `model`에 학습하세요.
  후: `StandardScaler`와 `LinearRegression`을 `Pipeline`으로 묶어 `model`에 담고 학습하세요.

### regression-table · coding · severity 2
- 메모: 목표 둘째 문장 123자, 힌트는 167자·177자짜리 코드 사슬 두 문장. 지시문에 '넣습니다/보관합니다'가 섞임. `Lasso(alpha=10, max_iter=20000, tol=0.001)`의 숫자가 왜 그런지 본문엔 없고 해설만 말함('계산이 끝까지 가라고 넉넉히'). 힌트의 `rows.append({...})`와 `Lasso(...)` 백틱 안 쉼표는 절대 자르지 말 것.
- [long] 전: `models`에 `Linear`, `Ridge(alpha=1)`, `Lasso(alpha=10, max_iter=20000, tol=0.001)`를 넣고 각각 `StandardScaler`와 묶어 학습한 뒤, 테스트 예측을 `predictions` 딕셔너리에 모으세요.
  후: `models`에 `Linear`, `Ridge(alpha=1)`, `Lasso(alpha=10, max_iter=20000, tol=0.001)`를 넣으세요. 각각 `StandardScaler`와 묶어 학습하세요. 테스트 예측은 `predictions` 딕셔너리에 모으세요.
- [long] 전: `predictions = {'Baseline': X_test['close'].to_numpy()}`로 시작해 `for name, estimator in models.items():`에서 `Pipeline`을 만들어 `fit`하고 `predictions[name] = model.predict(X_test)`, `fitted[name] = model`.
  후: 시작은 `predictions = {'Baseline': X_test['close'].to_numpy()}`예요. `for name, estimator in models.items():` 안에서 `Pipeline`을 만들어 `fit`하세요. 그리고 `predictions[name] = model.predict(X_test)`, `fitted[name] = model`.
- [long] 전: 두 번째 반복 `for name, pred in predictions.items():`에서 `rows.append({'model': name, 'MAE': mean_absolute_error(y_test, pred), 'RMSE': mean_squared_error(y_test, pred) ** 0.5, 'R2': r2_score(y_test, pred)})`.
  후: 둘째 반복 `for name, pred in predictions.items():` 안에서는 한 줄이에요. `rows.append({'model': name, 'MAE': mean_absolute_error(y_test, pred), 'RMSE': mean_squared_error(y_test, pred) ** 0.5, 'R2': r2_score(y_test, pred)})`.
- [tone] 전: `predictions`에는 기준 예측 `Baseline`(오늘 종가)도 함께 넣습니다.
  후: `predictions`에는 기준 예측 `Baseline`(오늘 종가)도 함께 넣으세요.
- [tone] 전: 학습한 모델은 `fitted`에 보관합니다.
  후: 학습한 모델은 `fitted`에 보관하세요.
- [unclear] 전: 분류 비교표와 같은 표를 회귀로 만듭니다.
  후: 분류 비교표와 같은 표를 회귀로 만들어요. 라쏘의 `max_iter`와 `tol`은 계산이 끝까지 가도록 넉넉히 준 값이에요. (해설이 이미 말하는 내용)

### midpoint · quiz · severity 1
- 메모: 2문항. '표가 의미를 가집니다'만 번역투. 나머지는 합니다체 전환만.
- [stiff] 전: 기준과 세 모델 모두 같은 80일, 같은 정답으로 채점했기 때문에 표가 의미를 가집니다.
  후: 기준과 세 모델 모두 같은 80일, 같은 정답으로 채점했어요. 그래서 표가 뜻이 있는 거예요.

### beat-baseline · coding · severity 1
- 메모: 만화가 앞에 있어 '왜 푸는지'가 잘 잡힘. 목표 한 문장이 107자, 마무리 두 문장이 '것이 아닙니다/그것이'.
- [long] 전: 기준 예측의 MAE를 `baseline_mae`, `Ridge(alpha=1)` 파이프라인의 MAE를 `ridge_mae`에 저장하고, `improved`에 `ridge_mae < baseline_mae`의 결과를 담아 세 값을 출력하세요.
  후: 기준 예측의 MAE를 `baseline_mae`에, `Ridge(alpha=1)` 파이프라인의 MAE를 `ridge_mae`에 저장하세요. `improved`에는 `ridge_mae < baseline_mae`의 결과를 담으세요. 세 값을 출력하세요.
- [stiff] 전: 그것이 이 기간의 사실이고, 검사는 계산이 맞는지만 봅니다.
  후: 그게 이 기간의 사실이에요. 검사는 계산이 맞는지만 봐요.

### forecast-plot · coding · severity 2
- 메모: 목표 두 문장과 힌트 한 문장이 길다(89·47·133자). 'x축이 정답 날짜인 이유를 생각해 보세요'는 좋은 질문. `ax.plot(..., label='Actual next close')`와 `ax.set(xlabel='정답 날짜', ...)` 백틱 안 쉼표 주의.
- [long] 전: 릿지 파이프라인을 학습해 `prediction`을 구하고, `target_date`를 인덱스로 `actual`(실제 다음 종가)과 `prediction` 두 열을 가진 `comparison` 표를 만드세요.
  후: 릿지 파이프라인을 학습해 `prediction`을 구하세요. 그다음 `target_date`를 인덱스로 `comparison` 표를 만드세요. 열은 `actual`(실제 다음 종가)과 `prediction` 둘이에요.
- [long] 전: `fig, ax`에 두 선을 같은 날짜 축에 그리고 x축 이름 `정답 날짜`, 범례를 표시하세요.
  후: `fig, ax`에 두 선을 같은 날짜 축에 그리세요. x축 이름은 `정답 날짜`, 범례도 켜세요.
- [long] 전: 그다음 `ax.plot(comparison.index, comparison['actual'], label='Actual next close')`와 예측 선을 하나 더 그리고 `ax.set(xlabel='정답 날짜', ...)`, `ax.legend()`, `plt.show()`.
  후: 그다음 `ax.plot(comparison.index, comparison['actual'], label='Actual next close')`로 실제 선을 그리세요. 예측 선도 하나 더요. 마무리는 `ax.set(xlabel='정답 날짜', ...)`, `ax.legend()`, `plt.show()`.

### final-report · coding · severity 2
- 메모: 키 다섯 개를 한 문장(97자)에 괄호로 욱여넣어 목록으로 풀면 좋음. '다섯 숫자'는 best_model(이름)·improved(참/거짓)가 숫자가 아니라 살짝 어긋남(제목 '숫자 다섯 개'도 같지만 제목은 대상 아님). 힌트 'f-string'은 asks.py·prompts.py에서 이미 쓰는 말이라 그대로.
- [long] 전: 키는 `test_days`(테스트 거래일 수), `baseline_mae`, `best_model`(MAE가 가장 작은 모델 이름), `best_mae`, `improved`(최선 모델이 기준보다 나은지) 다섯 개입니다.
  후: 키는 다섯 개예요.\n- `test_days`: 테스트 거래일 수\n- `baseline_mae`: 기준 MAE\n- `best_model`: MAE가 가장 작은 모델 이름\n- `best_mae`: 그 모델의 MAE\n- `improved`: 최선 모델이 기준보다 나은지
- [long] 전: 준비된 `models`(`Linear`, `Ridge`)를 각각 학습해 테스트 MAE를 `maes` 딕셔너리에 모으고, 기준 MAE와 비교해 `report` 딕셔너리를 만드세요.
  후: 준비된 `models`(`Linear`, `Ridge`)를 각각 학습해 테스트 MAE를 `maes` 딕셔너리에 모으세요. 기준 MAE와 비교해 `report` 딕셔너리를 만드세요.
- [long] 전: `maes = {}`를 두고 `for name, estimator in models.items():`에서 파이프라인을 학습해 `maes[name] = mean_absolute_error(y_test, model.predict(X_test))`.
  후: `maes = {}`를 두세요. `for name, estimator in models.items():` 안에서 파이프라인을 학습하세요. 점수는 `maes[name] = mean_absolute_error(y_test, model.predict(X_test))`.
- [fact] 전: 검사는 다섯 숫자가 실제 계산과 맞는지만 봅니다.
  후: 검사는 다섯 값이 실제 계산과 맞는지만 봐요.

### final-check · quiz · severity 1
- 메모: 6문항. 해설이 짧고 '다른 보기는 왜 아닌가'도 한 줄씩이라 좋음. '~이므로'와 '반영하지 않게 된다'만.
- [stiff] 전: 실제값과 예측값은 모두 "다음 거래일"의 값이므로 그 날짜 위에 그려야 맞습니다.
  후: 실제값과 예측값은 모두 "다음 거래일"의 값이에요. 그래서 그 날짜 위에 그려야 맞아요.
- [stiff] 전: 모의고사 문제를 고르는 셈이라 점수가 실력을 반영하지 않게 된다
  후: 모의고사 문제를 고르는 셈이라 점수가 실력을 보여 주지 못한다

### course-wrap · quiz · severity 1
- 메모: 7문항. 수업 전체를 잇는 문항이라 내용은 그대로. '매개변수'가 수업 말 '하이퍼파라미터'(d2_p6 8곳, 덱 7곳, 해설 5곳)와 어긋남. 정답 보기 '기간이나 매개변수를 바꿔 다시 돌리지 마'도 같이 고칠 것.
- [jargon] 전: 테스트로 매개변수를 고르는 누수다.
  후: 테스트로 하이퍼파라미터를 고르는 누수예요.
- [stiff] 전: AI는 "개선"을 요구받으면 조건을 바꿔 이기는 결과를 만들려 합니다.
  후: AI한테 "개선"을 시키면 조건을 바꿔서라도 이기는 결과를 만들려고 해요.
- [long] 전: 숫자 하나만 보지 말고 기준과 비교하고, 무엇을 몇 개로 잰 점수인지 함께 적는다
  후: 기준과 비교하고, 무엇을 몇 개로 잰 점수인지 함께 적는다
