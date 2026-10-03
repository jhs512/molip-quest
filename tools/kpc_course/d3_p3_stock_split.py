"""3일차 · 3교시 — 시간 분리와 기준 모델"""
from kpc_course.dsl import *

CALLS = PD + "calls = pd.DataFrame({'week': [1]*7 + [2]*7, 'weekday': ['월','화','수','목','금','토','일']*2, 'calls': [1320,980,940,910,1010,420,380, 1410,1020,960,890,1050,450,360]})\n"

UNIT = unit('stock-split', '3일차 · 3교시 — 시간 분리와 기준 모델', [
    concept('temporal-boundary', '시간은 섞으면 안 되고, 경계의 하루도 조심해야 한다',
        body="""
        어제는 `train_test_split`이 승객을 무작위로 섞어 훈련과 테스트를 나눴습니다. 승객끼리는 순서가 없으니 괜찮았습니다. 주가는 다릅니다. 날짜를 무작위로 섞으면 6월 가격으로 훈련한 모델이 3월 가격을 맞히는 꼴이 됩니다. 미래를 보고 과거를 맞히는 것은 시험이 아닙니다. 그래서 시간 자료는 **앞쪽 기간으로 훈련하고 뒤쪽 기간으로 테스트**합니다. 여기서는 마지막 80거래일을 테스트로 떼어 둡니다.

        ```comic-gen
        제목: 시간은 섞지 않는다
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [준호, 강사]
            대사:
              - 화자: 준호
                상대: 강사
                내용: |-
                  어제처럼 train_test_split으로
                  섞으면 안 돼요?
              - {화자: 강사, 상대: 준호, 내용: "6월 가격으로 배워서 3월을 맞히게 돼요."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 기쁨}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "미래를 보고 과거를 맞히는 거네요."}
              - 화자: 강사
                상대: 준호
                내용: |-
                  앞 기간으로 훈련, 뒤 기간으로 테스트.
                  그게 전부예요.
        ```

        그런데 경계를 하루 잘못 그으면 작은 누수가 숨어듭니다. 테스트가 시작되는 날을 `test_start`라고 합시다. 그 바로 전날 행을 보세요. 입력 날짜는 테스트 전이니 훈련에 들어가도 될 것 같지만, 그 행의 **정답**은 `test_start` 당일의 종가입니다. 테스트 첫날의 답을 훈련에서 이미 본 셈입니다.

        | 행의 날짜 | 정답 날짜 | 훈련에 넣어도 되나 |
        | --- | --- | --- |
        | test_start 이틀 전 | test_start 하루 전 | 된다 |
        | test_start 하루 전 | **test_start** | 안 된다. 정답이 테스트 기간 |
        | test_start | test_start 다음 거래일 | 테스트 |

        그래서 훈련 조건은 둘입니다. 입력 날짜도 `test_start` 전, 그리고 `target_date`도 `test_start` 전. 2교시에서 `target_date`를 남겨 둔 이유가 이것입니다.

        ```python
        test_start = frame.index[-80]
        train_mask = (frame.index < test_start) & (frame['target_date'] < test_start)
        test_mask = frame.index >= test_start
        X_train, X_test = X.loc[train_mask], X.loc[test_mask]
        ```

        나눴으면 기준 모델입니다. 어제의 "전원 사망"에 해당하는 가장 단순한 예측은 **"내일 종가는 오늘 종가와 같다"**입니다. 우습게 들리지만 주가에서는 이 기준을 이기기가 생각보다 어렵습니다. 점수는 정확도 대신 **MAE**(평균 절대 오차)로 잽니다. 예측과 정답의 차이를 부호 없이 평균 낸 것이라 단위가 원이고, "평균적으로 몇 원 빗나갔나"로 읽으면 됩니다. 작을수록 좋습니다.
        """,
        check=short('"내일 종가는 오늘 종가와 같다"처럼 가장 단순한 예측을 두고 모델과 비교하는 것을 무엇이라고 하나요?', ['기준 모델', '기준모델', '기준 예측', '기준예측', 'baseline', '베이스라인'],
                    '기준(baseline)이 있어야 모델이 실제로 무엇을 배웠는지 알 수 있습니다. 주가에서는 "오늘 종가 그대로"가 생각보다 강한 기준입니다.')),
    coding('test-start', '테스트 시작일 정하기',
        goal="""
        준비된 `frame`에서 마지막 80행의 첫 날짜를 `test_start`에 저장하세요. 그리고 날짜가 `test_start` 이상인 행 수를 `n_test`에 담아 출력하세요.

        `n_test`가 80이면 맞게 정한 것입니다.
        """,
        hint="""
        `frame.index[-80]`이 뒤에서 80번째 날짜입니다. `frame.index >= test_start`는 행마다 참·거짓이고 `.sum()`이 참의 개수, `int()`로 감싸 정수로 저장하세요.
        """,
        starter=ST_FRAME + "# test_start, n_test를 만들고 출력하세요\n",
        solution=ST_FRAME + "test_start = frame.index[-80]\nn_test = int((frame.index >= test_start).sum())\nprint(test_start, n_test)\n",
        check="assert s['test_start']==s['frame'].index[-80] and s['n_test']==80"),
    coding('time-boundary', '정답 날짜까지 보고 나누기',
        goal="""
        훈련·테스트를 나눕니다. `test_start`를 정하고, 입력 날짜와 `target_date`가 **모두** `test_start` 전인 행을 `train_mask`, 입력 날짜가 `test_start` 이상인 행을 `test_mask`로 만든 뒤 `X_train`, `X_test`, `y_train`, `y_test`를 만드세요. 두 쪽의 행 수를 출력합니다.

        396행이 훈련 315, 경계 하루 제외 1, 테스트 80으로 나뉘면 맞게 한 것입니다. 훈련 정답의 마지막 날짜가 테스트 첫 날짜보다 앞인지도 출력해 보세요.
        """,
        hint="""
        개념의 네 줄 그대로입니다. 두 조건을 괄호로 감싸 `&`로 잇는 것은 1일차와 같습니다. `X.loc[train_mask]`, `y.loc[train_mask]`처럼 같은 마스크로 입력과 정답을 함께 골라야 행이 어긋나지 않습니다.
        """,
        starter=ST_FRAME + "feature_columns=['close','return_1','ma5','lag_close_1']\nX=frame[feature_columns]\ny=frame['target_next_close']\n# test_start, 마스크와 네 자료를 만드세요\n",
        solution=ST_FRAME + TIME_SPLIT + "print(len(X_train),len(X_test))\nprint(frame.loc[train_mask,'target_date'].max(),X_test.index.min())\n",
        check="assert len(s['X_train'])==315 and len(s['X_test'])==80\nassert s['frame'].loc[s['train_mask'],'target_date'].max()<s['X_test'].index.min()\nassert set(s['X_train'].index).isdisjoint(s['X_test'].index)\nassert 'target_next_close' not in s['X_train']"),
    coding('manual-mae', 'MAE를 손으로 계산하기',
        goal="""
        기준 예측의 오차를 직접 계산합니다. 테스트 기간에서 "내일 종가 = 오늘 종가"로 예측하면 예측값은 `X_test['close']`입니다. 정답 `y_test`와의 차이에 `.abs()`를 붙인 것을 `errors`에, 그 평균을 `manual_mae`에 저장하고 출력하세요.

        결과는 원 단위입니다. "하루에 평균 이 정도 빗나간다"로 읽으세요. 다음 미션에서 함수로 구한 값과 같은지 비교합니다.
        """,
        hint="""
        `errors = (y_test - X_test['close']).abs()`, `manual_mae = errors.mean()`. MAE라는 이름이 붙어 있지만 하는 일은 "차이의 절댓값을 평균 낸다" 두 단계뿐입니다.
        """,
        starter=ST_FRAME + TIME_SPLIT + "# errors, manual_mae를 만들고 출력하세요\n",
        solution=ST_FRAME + TIME_SPLIT + "errors = (y_test - X_test['close']).abs()\nmanual_mae = errors.mean()\nprint(manual_mae)\n",
        check="import numpy as np\nassert len(s['errors'])==80 and (s['errors']>=0).all()\nassert abs(s['manual_mae']-float(np.abs(s['y_test'].to_numpy()-s['X_test']['close'].to_numpy()).mean()))<1e-8"),
    coding('close-baseline', '같은 계산을 함수로',
        goal="""
        `scikit-learn`의 `mean_absolute_error`로 같은 값을 구합니다. 기준 예측 `X_test['close']`를 배열로 바꿔 `baseline_pred`에 저장하고, `mean_absolute_error(y_test, baseline_pred)`를 `baseline_mae`에 담아 출력하세요.

        앞 미션의 `manual_mae`와 같은 숫자가 나와야 합니다. 이 값이 오늘 남은 시간 동안 모든 모델이 넘어야 할 선입니다.
        """,
        hint="""
        `baseline_pred = X_test['close'].to_numpy()`, `baseline_mae = mean_absolute_error(y_test, baseline_pred)`. 지표 함수는 어제처럼 `(정답, 예측)` 순서입니다.
        """,
        starter=ST_FRAME + TIME_SPLIT + "from sklearn.metrics import mean_absolute_error\n# baseline_pred와 baseline_mae를 만드세요\n",
        solution=ST_FRAME + TIME_SPLIT + "from sklearn.metrics import mean_absolute_error\nbaseline_pred=X_test['close'].to_numpy()\nbaseline_mae=mean_absolute_error(y_test,baseline_pred)\nprint(baseline_mae)\n",
        check="import numpy as np\nassert np.array_equal(s['baseline_pred'],s['X_test']['close'].to_numpy())\nassert abs(s['baseline_mae']-float(np.abs(s['y_test'].to_numpy()-s['X_test']['close'].to_numpy()).mean()))<1e-8"),
    coding('callcenter-baseline', '콜센터 월요일, 지난주와 같다고 보면',
        intro="""
        주가에서 잠깐 벗어나 같은 기준 모델을 콜센터에 적용합니다. 어느 카드사 콜센터의 2주치 일별 통화량이 준비되어 있습니다. 주말에 쌓인 전화가 몰려 월요일이 가장 많습니다. 팀장은 매주 "지난주 같은 요일과 같다"고 보고 상담원을 배치해 왔습니다. 이 방법이 얼마나 빗나가는지가, 통화량 예측 모델이 넘어야 할 선입니다.
        """,
        goal="""
        `calls`에서 1주차 통화량을 배열 `last_week`, 2주차 통화량을 배열 `this_week`에 저장하세요. 1주차 값을 2주차 예측으로 쓰는 것이 기준 모델이니, `mean_absolute_error(this_week, last_week)`를 `baseline_mae`에 담아 출력하세요. 월요일 하루의 오차는 `monday_error`에 따로 저장하세요.

        상담원 한 명이 하루 60통을 받는다면, 이 MAE는 상담원 몇 명분의 오차인지 생각해 보세요. 월요일만 보면 어떤가요?
        """,
        hint="""
        `last_week = calls[calls['week'] == 1]['calls'].to_numpy()`, 2주차도 같은 모양입니다. 지표 함수는 `(정답, 예측)` 순서이므로 정답은 `this_week`, 예측은 `last_week`입니다. 월요일은 두 배열의 첫 값이라 `monday_error = abs(this_week[0] - last_week[0])`.
        """,
        starter=CALLS + "from sklearn.metrics import mean_absolute_error\n# last_week, this_week, baseline_mae, monday_error를 만드세요\n",
        solution=CALLS + "from sklearn.metrics import mean_absolute_error\nlast_week = calls[calls['week'] == 1]['calls'].to_numpy()\nthis_week = calls[calls['week'] == 2]['calls'].to_numpy()\nbaseline_mae = mean_absolute_error(this_week, last_week)\nmonday_error = abs(this_week[0] - last_week[0])\nprint(baseline_mae, monday_error)\n",
        check="import numpy as np\nassert np.array_equal(s['last_week'],[1320,980,940,910,1010,420,380]) and np.array_equal(s['this_week'],[1410,1020,960,890,1050,450,360])\nassert abs(s['baseline_mae']-260/7)<1e-8 and int(s['monday_error'])==90"),
    quiz('temporal-check', '3일차 3교시 점검',
        choice('주가 자료를 `train_test_split`처럼 무작위로 섞어 나누면 어떤 문제가 생기나요?',
               ['미래 가격으로 훈련해 과거를 맞히게 되어 점수를 믿을 수 없다', '행 수가 줄어든다', '아무 문제 없다'], 0,
               '승객은 순서가 없지만 날짜는 순서가 있습니다. 시간 자료는 앞 기간으로 훈련하고 뒤 기간으로 테스트합니다.'),
        choice('`test_start` 하루 전 행을 훈련에서 빼야 하는 이유는 무엇인가요?',
               ['그 행의 정답이 `test_start` 당일 종가라 테스트 첫날의 답을 훈련에서 보게 된다', '입력이 비어 있어서', '가격이 너무 높아서'], 0,
               '입력 날짜만 보면 훈련 같지만 정답 날짜가 테스트 기간입니다. 그래서 `target_date`도 `test_start` 전이어야 합니다.'),
        short('396행을 나누면 테스트 80행, 경계 제외 1행, 훈련은 몇 행인가요?', ['315', '315행'],
              '396에서 80과 1을 빼면 315입니다. 두 조건을 모두 만족하는 행만 훈련에 들어갑니다.'),
        choice('MAE가 1500이라는 것은 무슨 뜻인가요?',
               ['예측이 하루 평균 약 1500원 빗나간다', '정확도가 15%다', '1500일을 예측했다'], 0,
               'MAE는 예측과 정답의 차이를 부호 없이 평균 낸 값이라 단위가 정답과 같은 원입니다. 작을수록 좋습니다.'),
        choice('"내일 종가는 오늘 종가와 같다"는 기준 예측은 어떤 역할을 하나요?',
               ['모델이 이 오차보다 작아야 무언가 배운 것이라는 선', '가장 좋은 모델', '쓸모없는 농담'], 0,
               '어제의 "전원 사망"과 같은 역할입니다. 주가에서는 이 단순한 기준을 이기기가 쉽지 않습니다.'),
    ),
])
