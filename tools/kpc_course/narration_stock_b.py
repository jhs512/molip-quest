"""해설 모드 scripts for the stock chapter, second half (d3_p3 시간 분리와 기준 모델, d3_p4 회귀 비교와
최종 결과, and the chapter's ★ 도전 과제): what the tutor says and types for each concept and coding
problem, keyed by activity id. Format and rules: narration.py. The first half (d3_p1, d3_p2) lives in
narration_stock_a.py.

Voice: the instructor's (see .scratch/presenter-decks/spec.md): 해요체 구어, "자," opens a scene,
one or two short sentences per line, says what the student should look at right now.

Numbers spoken in the output lines come from running each solution on courses/data/stock.csv:
baseline MAE 13637.5, Linear 13521, Ridge 13601, Lasso 13630 (ma5); Ridge 13859 with ma10.
"""

NARRATION = {
    # ---- 3일차 3교시 — 시간 분리와 기준 모델 ----
    "temporal-boundary": [
        ("title", "자, 3교시예요. 나누는 방법이 타이타닉하고 달라져요. 시간 자료는 섞으면 안 되거든요."),
        ("타이타닉에서는 train_test_split이 승객을 무작위로 섞어", "타이타닉은 승객을 무작위로 섞어도 됐어요. 승객끼리는 순서가 없으니까요. 주가는 날짜를 섞으면 6월 가격으로 배워서 3월을 맞히는 꼴이 돼요. 그래서 앞 기간으로 훈련, 뒤 기간으로 테스트예요."),
        ("제목: 섞으면 점쟁이가 된다", "만화 보세요. 5월 종가를 거의 다 맞혔다고 기뻐하는데, 훈련 자료에 6월 가격이 들어 있었던 거예요. 실제 내일은 그렇게 안 보이죠."),
        ("제목: 시간은 섞지 않는다", "준호 씨 질문도 같아요. 앞 기간으로 배우고 뒤 기간으로 채점한다, 그게 전부예요. 여기서는 마지막 80거래일을 테스트로 떼요."),
        ("위젯: temporal", "위젯을 단계마다 넘겨 보세요. 거래일 30일을 날짜순으로 세우고 뒤쪽 8일을 테스트로 떼요. 셋째 단계의 경계 바로 앞 하루, 그 칸이 지금부터 볼 문제예요."),
        ("그런데 경계를 하루 잘못 그으면 작은 누수가 숨어듭니다", "경계를 하루 잘못 그으면 작은 누수가 숨어들어요. 테스트 첫날을 test_start라고 하고 그 바로 전날 행을 보세요. 입력 날짜는 테스트 전인데, 정답은 test_start 당일 종가거든요."),
        ("안 된다. 정답이 테스트 기간", "표의 둘째 줄이에요. test_start 하루 전 행은 입력은 훈련처럼 보여도 정답이 테스트 기간이라 안 돼요. 테스트 첫날의 답을 훈련에서 미리 보는 셈이죠."),
        ("그래서 훈련 조건은 둘입니다", "그래서 훈련 조건이 둘이에요. 입력 날짜도 test_start 전, target_date도 test_start 전. 아래 코드의 train_mask가 두 조건을 &로 이은 거예요. 2교시에 target_date를 남겨 둔 이유가 이거죠."),
        ("나눴으면 기준 모델입니다", "나눴으면 기준 모델이에요. 내일 종가는 오늘 종가와 같다, 분류의 전원 사망에 해당해요. 점수는 MAE, 예측과 정답의 차이를 부호 없이 평균 낸 거라 단위가 원이에요. 작을수록 좋아요."),
        ("check", "확인 문항이요. 가장 단순한 예측을 두고 모델과 비교하는 것, 분류에서도 썼던 그 이름이에요."),
    ],
    "test-start": [
        ("problem", "자, 첫 코딩이에요. 준비된 frame에서 마지막 80행의 첫 날짜를 test_start에 넣고, 그 날짜 이상인 행 수를 n_test에 담아 출력해요. 80이 나와야 맞아요."),
        ("starter", "준비 코드가 2교시에 만든 frame을 그대로 만들어 둬요. 여섯 열에 dropna까지요. 그대로 둘게요."),
        ("code", "test_start = frame.index[-80]\n", "frame.index[-80], 뒤에서 80번째 날짜예요. 거기가 테스트 첫날이에요."),
        ("code", "n_test = int((frame.index >= test_start).sum())\nprint(test_start, n_test)\n", "frame.index >= test_start는 행마다 참·거짓이고, sum()이 참의 개수예요. int로 감싸 정수로 저장하고 출력해요."),
        ("output", "2026년 5월 11일, 그리고 80이 나왔죠? 그 날짜부터 끝까지가 테스트 자료예요."),
    ],
    "time-boundary": [
        ("problem", "자, 이제 진짜로 나눠요. 입력 날짜와 target_date가 모두 test_start 전인 행이 train_mask, 입력 날짜가 test_start 이상이면 test_mask예요. 그걸로 X_train, X_test, y_train, y_test를 만들어요."),
        ("hint", "개념의 네 줄 그대로예요. 같은 마스크로 입력과 정답을 함께 골라야 행이 어긋나지 않아요."),
        ("starter", "준비 코드가 frame에 이어 feature_columns 네 열로 입력 X, target_next_close로 정답 y까지 만들어 뒀어요."),
        ("code", "test_start=frame.index[-80]\n", "앞 미션 그대로, test_start부터요."),
        ("code", "train_mask=(frame.index<test_start)&(frame['target_date']<test_start)\ntest_mask=frame.index>=test_start\n", "train_mask는 조건 둘을 괄호로 감싸 &로 이어요. 입력 날짜도, target_date도 test_start 전. test_mask는 입력 날짜가 test_start 이상이면 돼요."),
        ("code", "X_train,X_test=X.loc[train_mask],X.loc[test_mask]\ny_train,y_test=y.loc[train_mask],y.loc[test_mask]\n", "같은 마스크로 X와 y를 같이 골라요. 그래야 입력과 정답의 행이 어긋나지 않거든요."),
        ("code", "print(len(X_train),len(X_test))\nprint(frame.loc[train_mask,'target_date'].max(),X_test.index.min())\n", "행 수를 찍고, 훈련 정답의 마지막 날짜와 테스트 첫 날짜도 나란히 찍어 봐요."),
        ("output", "315하고 80이에요. 396에서 경계 하루가 빠진 거죠. 둘째 줄은 5월 8일과 5월 11일, 훈련 정답이 테스트 시작보다 앞이에요."),
    ],
    "manual-mae": [
        ("problem", "자, 기준 예측의 오차를 손으로 계산해요. 테스트 기간에서 내일 종가는 오늘 종가라고 하면 예측값이 X_test의 close예요. 정답 y_test와의 차이에 abs()를 붙여 errors에, 그 평균을 manual_mae에 담아요."),
        ("hint", "위젯과 만화 보셨죠? 플러스 500, 마이너스 500을 그냥 평균 내면 0이에요. 부호를 떼고 평균 내는 게 MAE예요."),
        ("starter", "준비 코드가 frame 만들기와 시간 분리까지 다 해 뒀어요. X_test, y_test가 준비돼 있어요."),
        ("code", "errors = (y_test - X_test['close']).abs()\n", "y_test에서 X_test의 close를 빼고 abs()로 부호를 떼요. 80일치 오차가 전부 0 이상이 되죠."),
        ("code", "manual_mae = errors.mean()\nprint(manual_mae)\n", "그 평균이 MAE예요. 이름은 거창한데 하는 일은 차이의 절댓값을 평균 낸다, 두 단계뿐이죠."),
        ("output", "13637.5가 나왔어요. 오늘 종가 그대로 찍으면 하루 평균 만 삼천육백 원쯤 빗나간다는 뜻이에요."),
    ],
    "close-baseline": [
        ("problem", "자, 같은 값을 이번엔 scikit-learn 함수로 구해요. X_test의 close를 배열로 바꿔 baseline_pred에, mean_absolute_error(y_test, baseline_pred)를 baseline_mae에 담아 출력해요."),
        ("starter", "준비 코드 끝에 mean_absolute_error를 불러오는 줄이 있어요. 그대로 둘게요."),
        ("code", "baseline_pred=X_test['close'].to_numpy()\n", "to_numpy()로 배열로 바꿔요. 기준 예측은 오늘 종가 그대로니까 close 열이 곧 예측이에요."),
        ("code", "baseline_mae=mean_absolute_error(y_test,baseline_pred)\nprint(baseline_mae)\n", "지표 함수는 정답, 예측 순서예요. 분류 때 accuracy_score와 같죠."),
        ("output", "13637.5, 앞 미션의 manual_mae와 똑같아요. 이 숫자가 이 챕터의 모든 모델이 넘어야 할 선이에요."),
    ],
    "callcenter-baseline": [
        ("problem", "자, 잠깐 콜센터로 가요. 2주치 일별 통화량이 있고, 팀장은 지난주 같은 요일과 같다고 보고 상담원을 배치해 왔어요. 이 방법이 얼마나 빗나가는지가 통화량 모델이 넘어야 할 선이에요."),
        ("starter", "준비 코드가 calls 표를 만들어요. week, weekday, calls 세 열에 14행이에요. mean_absolute_error도 불러왔어요."),
        ("code", "last_week = calls[calls['week'] == 1]['calls'].to_numpy()\nthis_week = calls[calls['week'] == 2]['calls'].to_numpy()\n", "week가 1인 행의 calls가 last_week, 2인 행이 this_week예요. 조건으로 행을 고르고 열 하나를 배열로 꺼내요."),
        ("code", "baseline_mae = mean_absolute_error(this_week, last_week)\n", "정답은 이번 주, 예측은 지난주예요. 순서 조심하세요. 정답, 예측."),
        ("code", "monday_error = abs(this_week[0] - last_week[0])\nprint(baseline_mae, monday_error)\n", "월요일은 두 배열의 첫 값이라 인덱스 0이에요. 그 하루의 차이만 절댓값으로 따로 봐요."),
        ("output", "37.14쯤, 그리고 90이에요. 하루 평균 37통, 한 통 5분이면 세 시간 넘게 밀리거나 비는 거죠. 월요일만 보면 90통이라 더 커요."),
    ],

    # ---- 3일차 4교시 — 회귀 비교와 최종 결과 ----
    "regression-metrics": [
        ("title", "자, 마지막 단원이에요. 회귀 모델 세 개를 돌려서 3교시 기준과 비교하고 결론을 써요."),
        ("마지막 단원입니다", "입력 X는 네 열이에요. 오늘 종가, 수익률, 5일 평균, 어제 종가. 정답 y는 내일 종가고요."),
        ("선형 회귀(LinearRegression)는 입력마다 가중치를 곱해", "선형 회귀는 입력마다 가중치를 곱해 더해요. 입력이 넷이면 기울어진 판을 맞추는 거죠. 릿지와 라쏘는 같은 직선 맞추기에 브레이크를 단 거예요. 가중치가 너무 커지면 벌점을 줘서 우연한 흔들림까지 외우는 걸 막아요. 그래서 StandardScaler와 묶어 써요."),
        ("model = Pipeline([('scale', StandardScaler()), ('model', Ridge(alpha=1))])", "코드는 분류 때랑 똑같은 모양이에요. Pipeline에 scale과 model, fit, predict, 그리고 지표 함수에 정답, 예측 순서."),
        ("점수는 셋을 함께 적습니다", "점수는 셋을 같이 적어요. MAE는 하루 평균 몇 원. RMSE는 제곱해서 평균 내니까 큰 실수에 민감해요. R²는 평균으로 찍었을 때보다 얼마나 나은가, 1이 만점이에요. 주의할 건 R²의 비교 대상이 우리 기준인 오늘 종가가 아니라는 거예요."),
        ("제목: 평균 30개와 큰 실수", "만화 보세요. 빵 공장 MAE 30개는 하루 평균 30개를 더 굽거나 덜 굽는다는 뜻이고, 200개 빗나간 날이 있으면 RMSE가 벌어져요."),
        ("숫자가 현장에서 무슨 뜻인지 한 번 옮겨 봅니다", "현장으로 옮기면요. 더 구우면 저녁에 폐기, 덜 구우면 빈 진열대예요. 콜센터는 자리가 비어 통화가 밀리거나 고객이 대기음을 듣죠. 가끔 크게 틀리는 게 비싸면 RMSE를 더 무겁게 봐요."),
        ("제목: 30개와 300개", "명절 전날 300개 틀린 날, 그런 날이 RMSE를 크게 띄워요. 어느 숫자를 볼지는 현장에서 어느 실수가 더 비싼지에 달려 있어요."),
        ("결론을 쓰는 순서는 셋입니다", "결론은 세 줄이에요. 무엇을 언제 예측해 어떻게 나눴나, 기준 MAE와 모델 MAE, 그리고 한계. 기준보다 나쁘면 나쁘다고 적어요. 테스트 기간을 바꿔 가며 다시 돌리는 건 모의고사 문제를 고르는 거예요."),
        ("check", "확인 문항이요. 제곱해서 평균 내고 제곱근을 씌운 지표, 큰 실수에 민감한 그 약어예요."),
    ],
    "linear-only": [
        ("problem", "자, 선형 회귀 하나만 먼저 돌려요. StandardScaler와 LinearRegression을 Pipeline으로 묶어 model에 학습하고, 예측을 prediction, MAE를 linear_mae에 담아 출력해요. 가중치 네 개도 찍어 봐요."),
        ("starter", "준비 코드가 frame, 시간 분리, 그리고 회귀 모델과 지표 함수 불러오기까지 해 뒀어요. 그대로 둘게요."),
        ("code", "model = Pipeline([('scale', StandardScaler()), ('model', LinearRegression())])\nmodel.fit(X_train, y_train)\n", "분류와 같은 흐름이에요. scale 다음 model, fit은 훈련 자료로만."),
        ("code", "prediction = model.predict(X_test)\nlinear_mae = mean_absolute_error(y_test, prediction)\n", "테스트 자료로 예측하고, 정답 y_test, 예측 순서로 MAE를 구해요."),
        ("code", "print(linear_mae)\nprint(model.named_steps['model'].coef_)\n", "named_steps로 파이프라인 안의 모델을 꺼내면 coef_에 가중치 네 개가 있어요."),
        ("output", "13521 정도예요. 기준 13637.5보다 백 원쯤 작죠. 가중치는 첫 번째 close가 53196으로 압도적이에요. 오늘 종가가 거의 다 한 거예요."),
    ],
    "regression-table": [
        ("problem", "자, 분류 비교표를 회귀로 다시 만들어요. Linear, Ridge, Lasso 세 모델을 StandardScaler와 묶어 학습하고, 기준 예측 Baseline까지 네 예측의 MAE, RMSE, R2를 results 표에 모아요."),
        ("starter", "준비 코드는 앞 미션과 같아요. 분리된 네 자료와 회귀 도구들이 준비돼 있어요."),
        ("code", "models={'Linear':LinearRegression(),'Ridge':Ridge(alpha=1),'Lasso':Lasso(alpha=10,max_iter=20000,tol=0.001)}\n", "models 딕셔너리에 세 모델을 이름표 붙여 넣어요. 라쏘는 계산이 끝까지 가라고 max_iter와 tol을 넉넉히 줬어요."),
        ("code", "predictions={'Baseline':X_test['close'].to_numpy()}\nfitted={}\n", "predictions는 기준 예측 Baseline으로 시작해요. 오늘 종가 그대로죠. fitted는 학습한 모델을 보관할 빈 딕셔너리예요."),
        ("code", "for name,estimator in models.items():\n    model=Pipeline([('scale',StandardScaler()),('model',estimator)])\n    model.fit(X_train,y_train)\n    predictions[name]=model.predict(X_test)\n    fitted[name]=model\n", "첫 반복이에요. 모델마다 파이프라인을 만들어 fit하고, 테스트 예측을 predictions에, 모델은 fitted에 넣어요."),
        ("code", "rows=[]\nfor name,pred in predictions.items():\n    rows.append({'model':name,'MAE':mean_absolute_error(y_test,pred),'RMSE':mean_squared_error(y_test,pred)**0.5,'R2':r2_score(y_test,pred)})\n", "둘째 반복은 네 예측을 채점해요. RMSE는 mean_squared_error에 0.5 제곱, 그게 제곱근이에요. 전부 정답, 예측 순서죠."),
        ("code", "results=pd.DataFrame(rows).set_index('model')\nresults\n", "rows를 DataFrame으로 만들고 model을 인덱스로 세워요. 마지막 줄에 results만 두면 표로 보여 줘요."),
        ("output", "네 행 세 열이죠? MAE는 Linear 13521, Ridge 13601, Lasso 13630, 셋 다 기준 13637.5를 아슬아슬하게 넘어요. 그런데 RMSE는 기준이 17408로 가장 작아요. 큰 실수는 모델 쪽이 더 한 거죠."),
    ],
    "beat-baseline": [
        ("problem", "자, 비교를 참·거짓 하나로 정리해요. 기준 MAE를 baseline_mae, Ridge(alpha=1) 파이프라인의 MAE를 ridge_mae에 담고, ridge_mae < baseline_mae를 improved에 넣어 세 값을 출력해요. False여도 틀린 게 아니에요."),
        ("starter", "준비 코드는 그대로예요. 분리된 자료와 회귀 도구가 있어요."),
        ("code", "baseline_mae = mean_absolute_error(y_test, X_test['close'])\n", "기준부터요. 정답 y_test, 예측은 오늘 종가 close."),
        ("code", "ridge = Pipeline([('scale', StandardScaler()), ('model', Ridge(alpha=1))])\nridge.fit(X_train, y_train)\nridge_mae = mean_absolute_error(y_test, ridge.predict(X_test))\n", "릿지 파이프라인을 학습하고 테스트 예측으로 MAE를 구해요. 비교는 같은 y_test로요."),
        ("code", "improved = bool(ridge_mae < baseline_mae)\nprint(baseline_mae, ridge_mae, improved)\n", "작으면 True, 아니면 False. bool로 감싸 파이썬 참·거짓으로 만들어요."),
        ("output", "13637.5, 13601, True예요. 이 기간에서 릿지가 36원쯤 줄였어요. 만화처럼 False가 나오는 기간도 있어요. 그때는 그대로 적는 거예요."),
    ],
    "forecast-plot": [
        ("problem", "자, 마지막 그림이에요. 릿지로 예측을 구하고, target_date를 인덱스로 actual과 prediction 두 열을 가진 comparison 표를 만들어요. 두 선을 같은 날짜 축에 그리고 x축 이름은 정답 날짜예요."),
        ("starter", "준비 코드가 모델 재료에 matplotlib, seaborn까지 불러 뒀어요. 그대로 둘게요."),
        ("code", "model=Pipeline([('scale',StandardScaler()),('model',Ridge(alpha=1))])\nmodel.fit(X_train,y_train)\nprediction=model.predict(X_test)\n", "릿지 파이프라인, 앞 미션과 같아요. 학습하고 테스트 예측을 prediction에 담아요."),
        ("code", "comparison=pd.DataFrame({'actual':y_test.to_numpy(),'prediction':prediction},index=pd.DatetimeIndex(frame.loc[test_mask,'target_date']))\n", "comparison 표의 인덱스가 핵심이에요. 입력 날짜가 아니라 target_date. 실제값도 예측값도 다음 거래일의 값이니까 그 날짜 위에 놓는 거죠."),
        ("code", "fig,ax=plt.subplots()\nax.plot(comparison.index,comparison['actual'],label='Actual next close')\nax.plot(comparison.index,comparison['prediction'],label='Ridge')\n", "subplots로 종이와 영역을 만들고, 같은 날짜 축에 실제 선과 예측 선을 하나씩 그려요. label이 범례에 들어가요."),
        ("code", "ax.set(xlabel='정답 날짜',ylabel='Price',title='Held-out next trading day')\nax.legend()\nplt.show()\ncomparison.head()\n", "set으로 축 이름과 제목을 붙이고 legend로 범례를 켜요. plt.show() 뒤에 comparison.head()로 표 앞 다섯 줄도 봐요."),
        ("output", "그림이 나왔죠? 두 선이 거의 붙어 다니다 5월 15일처럼 급락한 날에 벌어져요. 표 첫 줄은 5월 12일, 실제 279000에 예측 282582예요."),
    ],
    "final-report": [
        ("problem", "자, 수업의 결론을 코드로 써요. models의 Linear와 Ridge를 학습해 MAE를 maes에 모으고, 기준과 비교해 report 딕셔너리 다섯 키를 채워요. 그리고 결론 세 줄을 출력해요."),
        ("starter", "준비 코드 끝에 models 딕셔너리가 있어요. Linear와 Ridge 둘이에요. 그대로 둘게요."),
        ("code", "baseline_mae=mean_absolute_error(y_test,X_test['close'])\nmaes={}\n", "기준 MAE를 먼저 구하고, 모델 점수를 모을 빈 딕셔너리 maes를 둬요."),
        ("code", "for name,estimator in models.items():\n    model=Pipeline([('scale',StandardScaler()),('model',estimator)])\n    model.fit(X_train,y_train)\n    maes[name]=mean_absolute_error(y_test,model.predict(X_test))\n", "비교표 때와 같은 반복이에요. 모델마다 파이프라인으로 학습해 테스트 MAE를 maes에 넣어요."),
        ("code", "best_model=min(maes,key=maes.get)\nreport={'test_days':len(X_test),'baseline_mae':baseline_mae,'best_model':best_model,'best_mae':maes[best_model],'improved':bool(maes[best_model]<baseline_mae)}\n", "min에 key=maes.get을 주면 값이 가장 작은 키, 즉 MAE가 가장 작은 모델 이름이 나와요. report에 다섯 값을 담아요."),
        ("code", "print(f\"다음 거래일 종가를 예측했고, 마지막 {report['test_days']}거래일을 테스트로 두었으며 훈련 정답은 모두 테스트 시작 전이다.\")\nprint(f\"기준 예측(오늘 종가 그대로) MAE {baseline_mae:.0f}원, 최선 모델 {best_model} MAE {maes[best_model]:.0f}원.\")\nprint('최선 모델이 기준보다 오차를 줄였다.' if report['improved'] else '최선 모델도 기준보다 오차를 줄이지 못했다. 이 파일, 이 기간의 결과다.')\n", "결론 세 줄이에요. 무엇을 언제 예측해 어떻게 나눴나, 기준과 최선 모델 MAE, 그리고 개선 여부. improved가 False면 못 줄였다고 그대로 찍어요."),
        ("output", "마지막 80거래일, 기준 13638원, 최선 모델 Linear 13521원, 기준보다 오차를 줄였다. 백 원 남짓이지만 정직하게 적은 숫자예요."),
    ],

    # ---- ★ 도전 과제 (stock) ----
    "window-rematch": [
        ("problem", "자, 도전 과제예요. 주가 챕터를 한 번에 복습하는데 이동평균 창을 5일에서 10일로 바꿔요. 특징 만들기, 경계 하루까지 챙긴 시간 분리, 기준 모델, 릿지 비교, report까지 직접 써요."),
        ("hint", "2교시 여섯 열에서 rolling(5)만 rolling(10)으로 바꾸면 처음 아홉 행이 비어 391행이 남아요. train_mask는 3교시 그대로예요."),
        ("starter", "준비 코드가 prices를 읽고 Pipeline, StandardScaler, Ridge, mean_absolute_error를 불러 뒀어요. frame은 이번엔 직접 만들어요."),
        ("code", "frame = pd.DataFrame(index=prices.index)\nframe['close'] = prices['종가']\nframe['return_1'] = prices['종가'].pct_change()\nframe['ma10'] = prices['종가'].rolling(10).mean()\nframe['lag_close_1'] = prices['종가'].shift(1)\n", "날짜 인덱스만 가진 빈 frame에 열을 하나씩 붙여요. close, pct_change의 return_1, 이번엔 rolling(10)으로 ma10, shift(1)로 어제 종가."),
        ("code", "frame['target_next_close'] = prices['종가'].shift(-1)\nframe['target_date'] = pd.Series(prices.index, index=prices.index).shift(-1)\nframe = frame.dropna().copy()\n", "정답은 shift(-1), 내일 종가예요. 부호를 틀리면 누수죠. target_date도 날짜를 하루 밀어 같이 두고, dropna로 빈 행을 떨어내요. 391행이 남아요."),
        ("code", "feature_columns = ['close', 'return_1', 'ma10', 'lag_close_1']\nX = frame[feature_columns]\ny = frame['target_next_close']\ntest_start = frame.index[-80]\ntrain_mask = (frame.index < test_start) & (frame['target_date'] < test_start)\ntest_mask = frame.index >= test_start\n", "입력 X 네 열, 정답 y. test_start는 뒤에서 80번째 날짜고, train_mask는 입력 날짜와 target_date 둘 다 test_start 전이에요. 경계 하루를 빼는 조건이죠."),
        ("code", "X_train, X_test = X.loc[train_mask], X.loc[test_mask]\ny_train, y_test = y.loc[train_mask], y.loc[test_mask]\nbaseline_mae = mean_absolute_error(y_test, X_test['close'].to_numpy())\n", "같은 마스크로 X와 y를 갈라요. 훈련 310, 테스트 80. 기준 MAE는 오늘 종가 그대로예요."),
        ("code", "model = Pipeline([('scale', StandardScaler()), ('model', Ridge(alpha=1))]).fit(X_train, y_train)\nridge_mae = mean_absolute_error(y_test, model.predict(X_test))\nreport = {'window': 10, 'rows': len(frame), 'baseline_mae': baseline_mae, 'ridge_mae': ridge_mae, 'improved': ridge_mae < baseline_mae}\nprint(report)\n", "릿지 파이프라인을 학습해 ridge_mae를 구하고, report 딕셔너리에 window 10, 행 수, 두 MAE, improved를 담아 출력해요."),
        ("output", "rows 391, 기준 13637.5, 릿지 13859, improved False예요. 창을 10일로 바꾸니 릿지가 기준을 못 넘었어요. 그래도 그대로 적는 거예요. 이 파일, 이 기간의 결과거든요."),
    ],
}
