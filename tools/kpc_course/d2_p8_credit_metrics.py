"""2일차 · 8교시 — 네 지표와 확률 기준"""
from kpc_course.dsl import *

CREDIT_SPLIT = CR + "from sklearn.model_selection import train_test_split\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\n"

UNIT = unit('credit-metrics', '2일차 · 8교시 — 네 지표와 확률 기준', [
    coding('manual-metrics', '혼동행렬로 네 지표 손계산',
        intro="""
        이 단원은 개념 미션 없이 문제 안에서 설명합니다. 7교시의 부도율은 약 22%였습니다. 뒤집으면 **전원 "정상"이라고 찍어도 정확도 78%**라는 뜻입니다. 그런데 그 모델은 부도 고객을 한 명도 찾아내지 못합니다. 카드사가 원하는 것은 정확도가 아니라 "부도 날 사람을 미리 찾는 것"이므로, 정확도 하나로는 모델을 평가할 수 없습니다. 그래서 맞힘과 틀림을 네 칸으로 나눠 봅니다.

        부도(1)를 양성이라고 부르기로 하고, 실제와 예측을 표로 놓으면 이렇게 됩니다. 이 표가 혼동행렬입니다.

        | | 예측: 정상(0) | 예측: 부도(1) |
        | --- | --- | --- |
        | **실제: 정상(0)** | TN (맞게 정상) | FP (멀쩡한 사람을 부도로 경고) |
        | **실제: 부도(1)** | FN (부도를 놓침) | TP (맞게 부도) |

        네 칸에서 지표 네 개가 나옵니다. **정확도**(accuracy)는 전체 중 맞힌 비율 (TP+TN)/전체. **정밀도**(precision)는 부도라고 경고한 사람 중 진짜 부도였던 비율 TP/(TP+FP), 즉 경고의 신뢰도. **재현율**(recall)은 진짜 부도 중 미리 찾아낸 비율 TP/(TP+FN), 즉 놓치지 않은 정도. **F1**은 정밀도와 재현율을 하나로 합친 점수로, 둘 다 높아야 높아집니다. 전원 정상으로 찍은 모델은 TP가 0이라 정밀도·재현율·F1이 전부 0입니다. 정확도 78%의 정체가 이렇게 드러납니다.

        어느 지표가 중요한지는 실수의 비용에 달렸습니다. 부도를 놓치면(FN) 돈을 떼이고, 멀쩡한 고객에게 경고하면(FP) 고객을 잃습니다. 떼이는 쪽이 더 아프면 재현율을, 고객을 잃는 쪽이 더 아프면 정밀도를 더 봅니다.
        """,
        goal="""
        작은 예로 공식을 손에 익힙니다. `tp, fp, fn, tn`이 준비돼 있습니다. 위 표의 공식대로 `precision`, `recall`, `accuracy`를 계산해 저장하고 출력하세요.

        세 값이 모두 약 0.667이면 맞게 계산한 것입니다.
        """,
        hint="""
        정밀도의 분모는 "부도라고 예측한 수" `tp + fp`, 재현율의 분모는 "진짜 부도 수" `tp + fn`, 정확도는 `(tp + tn) / (tp + fp + fn + tn)`입니다.
        """,
        starter='tp, fp, fn, tn = 2, 1, 1, 2\n# precision, recall, accuracy를 계산하고 출력하세요\n',
        solution='tp, fp, fn, tn = 2, 1, 1, 2\nprecision = tp / (tp + fp)\nrecall = tp / (tp + fn)\naccuracy = (tp + tn) / (tp + fp + fn + tn)\nprint(precision, recall, accuracy)\n',
        check="assert abs(s['precision']-2/3)<1e-12 and abs(s['recall']-2/3)<1e-12 and abs(s['accuracy']-2/3)<1e-12"),
    coding('metrics-matrix', '같은 계산을 함수로',
        goal="""
        손으로 한 계산을 `scikit-learn` 함수로 합니다. 정답 `y_true`와 예측 `y_pred` 여섯 개가 준비돼 있습니다. `accuracy_score`, `precision_score`, `recall_score`, `f1_score`로 네 값을 구해 같은 이름의 키로 `metrics` 딕셔너리에 담고, `confusion_matrix(y_true, y_pred, labels=[0, 1])`를 `matrix`에 저장해 둘 다 출력하세요.

        `matrix`가 `[[2, 1], [1, 2]]`, 즉 TN 2, FP 1, FN 1, TP 2이면 앞 미션과 같은 상황입니다. 네 지표도 같은 값이 나와야 합니다.
        """,
        hint="""
        지표 함수는 전부 `(정답, 예측)` 순서로 넣습니다. `metrics = {'accuracy': accuracy_score(y_true, y_pred), 'precision': precision_score(y_true, y_pred), ...}`. 혼동행렬의 `labels=[0, 1]`은 행·열 순서를 0, 1로 고정합니다.
        """,
        starter='from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix\ny_true=[0,0,1,1,1,0]\ny_pred=[0,1,1,0,1,0]\n# metrics와 matrix를 만드세요\n',
        solution="from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,confusion_matrix\ny_true=[0,0,1,1,1,0]\ny_pred=[0,1,1,0,1,0]\nmetrics={'accuracy':accuracy_score(y_true,y_pred),'precision':precision_score(y_true,y_pred),'recall':recall_score(y_true,y_pred),'f1':f1_score(y_true,y_pred)}\nmatrix=confusion_matrix(y_true,y_pred,labels=[0,1])\nprint(metrics)\nprint(matrix)\n",
        check="assert set(s['metrics'])=={'accuracy','precision','recall','f1'}\nassert all(abs(v-2/3)<1e-10 for v in s['metrics'].values())\nassert s['matrix'].tolist()==[[2,1],[1,2]]"),
    coding('credit-model', '부도 모델과 기준 모델을 네 지표로 비교',
        goal="""
        진짜 자료입니다. 준비 코드가 `상환_9월`, `신용한도`, `나이` 세 열을 입력으로 훈련·테스트를 나눠 두었습니다. `models`에 `Dummy`와 `Logistic`을 넣고, 각각 `StandardScaler`와 묶은 `Pipeline`으로 학습·예측한 뒤 `accuracy`, `precision`, `recall`, `f1`을 구해 `results` 표를 만드세요.

        기준 모델의 정확도는 78% 근처인데 재현율은 0입니다. 로지스틱 회귀가 재현율을 얼마나 끌어올리는지, 그 대가로 정확도는 어떻게 되는지 보세요.
        """,
        hint="""
        6교시의 표 만들기 패턴 그대로입니다. `for name, estimator in models.items():` 안에서 `Pipeline([('scale', StandardScaler()), ('model', estimator)])`를 만들어 `fit`, `predict`하고 네 지표를 딕셔너리로 `rows`에 모읍니다. 정밀도·재현율·F1에는 `zero_division=0`을 주면 기준 모델처럼 TP가 0일 때 경고 없이 0이 나옵니다.
        """,
        starter=CREDIT_SPLIT + "from sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score\nX=credit[['상환_9월','신용한도','나이']]\ny=credit[target]\nX_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)\n# models와 results를 만드세요\n",
        solution=CREDIT_SPLIT + "from sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score\nX=credit[['상환_9월','신용한도','나이']]\ny=credit[target]\nX_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)\nmodels={'Dummy':DummyClassifier(strategy='most_frequent'),'Logistic':LogisticRegression(max_iter=2000)}\nrows=[]\nfor name,estimator in models.items():\n    model=Pipeline([('scale',StandardScaler()),('model',estimator)])\n    model.fit(X_train,y_train)\n    pred=model.predict(X_test)\n    rows.append({'model':name,'accuracy':accuracy_score(y_test,pred),'precision':precision_score(y_test,pred,zero_division=0),'recall':recall_score(y_test,pred,zero_division=0),'f1':f1_score(y_test,pred,zero_division=0)})\nresults=pd.DataFrame(rows).set_index('model')\nresults\n",
        check="assert set(s['results'].index)=={'Dummy','Logistic'}\nassert set(s['results'].columns)=={'accuracy','precision','recall','f1'}\nassert s['results'].loc['Dummy','recall']==0\nassert ((s['results']>=0)&(s['results']<=1)).all().all()\nassert len(s['X_test'])==6000"),
    coding('predict-proba', '모델은 사실 확률을 내놓는다',
        goal="""
        로지스틱 회귀는 "부도/정상"을 바로 고르는 것이 아니라 **부도일 확률**을 먼저 계산하고, 0.5를 넘으면 부도라고 답합니다. 준비된 학습 완료 `model`에서 `model.predict_proba(X_test)[:, 1]`로 부도 확률을 `probabilities`에 저장하세요. 그리고 확률이 0.5 이상인 고객 수를 `n_positive_05`, 0.3 이상인 고객 수를 `n_positive_03`에 담아 출력하세요.

        기준을 0.5에서 0.3으로 낮추면 부도라고 경고하는 고객이 늘어납니다. 얼마나 늘어나는지 보세요.
        """,
        hint="""
        `predict_proba`는 행마다 `[정상 확률, 부도 확률]` 두 열을 돌려주므로 `[:, 1]`로 부도 확률만 고릅니다. `(probabilities >= 0.5)`는 참·거짓 배열이고 `.sum()`이 참의 개수입니다. `int()`로 감싸 정수로 저장하세요.
        """,
        starter=CREDIT_SPLIT + "from sklearn.linear_model import LogisticRegression\nX=credit[['상환_9월','신용한도','나이']]\ny=credit[target]\nX_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)\nmodel=Pipeline([('scale',StandardScaler()),('model',LogisticRegression(max_iter=2000))])\nmodel.fit(X_train,y_train)\n# probabilities, n_positive_05, n_positive_03을 만들고 출력하세요\n",
        solution=CREDIT_SPLIT + "from sklearn.linear_model import LogisticRegression\nX=credit[['상환_9월','신용한도','나이']]\ny=credit[target]\nX_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)\nmodel=Pipeline([('scale',StandardScaler()),('model',LogisticRegression(max_iter=2000))])\nmodel.fit(X_train,y_train)\nprobabilities = model.predict_proba(X_test)[:, 1]\nn_positive_05 = int((probabilities >= 0.5).sum())\nn_positive_03 = int((probabilities >= 0.3).sum())\nprint(n_positive_05, n_positive_03)\n",
        check="import numpy as np\nassert len(s['probabilities'])==6000 and ((s['probabilities']>=0)&(s['probabilities']<=1)).all()\nassert np.allclose(s['probabilities'],s['model'].predict_proba(s['X_test'])[:,1])\nassert s['n_positive_05']==int((s['probabilities']>=0.5).sum()) and s['n_positive_03']==int((s['probabilities']>=0.3).sum())\nassert s['n_positive_03']>s['n_positive_05']"),
    coding('thresholds', '기준값을 바꿔 0과 1로',
        goal="""
        확률을 0과 1로 바꾸는 규칙 자체를 손으로 써 봅니다. 확률 다섯 개가 `probabilities`에 있습니다. 0.5 이상이면 1인 배열을 `pred_05`, 0.3 이상이면 1인 배열을 `pred_03`에 저장하고 각각 1의 개수를 출력하세요.

        같은 확률인데 기준을 낮추니 부도 경고가 둘에서 넷으로 늘어납니다. 경고를 늘리면 놓치는 부도(FN)는 줄지만 멀쩡한 고객 경고(FP)는 늘어납니다. 기준값은 모델이 아니라 **비용을 아는 사람**이 정하는 숫자입니다.
        """,
        hint="""
        `(probabilities >= 0.5)`는 참·거짓 배열입니다. 뒤에 `.astype(int)`를 붙이면 참이 1, 거짓이 0이 됩니다. 개수는 `.sum()`.
        """,
        starter='import numpy as np\nprobabilities=np.array([0.1,0.35,0.49,0.51,0.8])\n# pred_05, pred_03을 만드세요\n',
        solution='import numpy as np\nprobabilities=np.array([0.1,0.35,0.49,0.51,0.8])\npred_05=(probabilities>=0.5).astype(int)\npred_03=(probabilities>=0.3).astype(int)\nprint(pred_05.sum(),pred_03.sum())\n',
        check="assert s['pred_05'].tolist()==[0,0,0,1,1]\nassert s['pred_03'].tolist()==[0,1,1,1,1]"),
    quiz('metrics-check', '2일차 8교시 점검',
        choice('부도율 22%인 자료에서 전원 "정상"으로 찍은 모델의 정확도와 재현율은 각각 얼마인가요?',
               ['정확도 약 78%, 재현율 0', '정확도 0, 재현율 약 78%', '둘 다 약 78%'], 0,
               '정상이 78%라 정확도는 78%지만, 부도를 한 명도 못 찾으니 재현율은 0입니다. 정확도만 보면 속습니다.'),
        short('부도라고 경고한 사람 중 진짜 부도였던 비율, TP/(TP+FP)를 무엇이라고 하나요?', ['정밀도', 'precision', '프리시전'],
              '정밀도(precision)는 경고의 신뢰도입니다. 멀쩡한 고객에게 경고하는 FP가 많으면 떨어집니다.'),
        short('진짜 부도 중 미리 찾아낸 비율, TP/(TP+FN)를 무엇이라고 하나요?', ['재현율', 'recall', '리콜'],
              '재현율(recall)은 놓치지 않은 정도입니다. 부도를 놓치는 FN이 많으면 떨어집니다.'),
        choice('혼동행렬에서 "진짜 부도인데 정상이라고 예측한" 칸은 어느 것인가요?',
               ['FN', 'FP', 'TN'], 0,
               'F는 틀림, N은 "정상"이라고 예측했다는 뜻입니다. 부도를 놓친 칸이라 돈을 떼이는 실수입니다.'),
        choice('부도를 놓쳐서 떼이는 손해가 멀쩡한 고객에게 경고하는 손해보다 훨씬 크다면, 어느 지표를 더 봐야 하나요?',
               ['재현율', '정밀도', '정확도'], 0,
               '놓치는 실수 FN을 줄이려는 것이므로 재현율입니다. 반대 상황이면 정밀도입니다.'),
        choice('부도 확률 기준값을 0.5에서 0.3으로 낮추면 일반적으로 어떻게 되나요?',
               ['경고가 늘어 재현율은 오르고 정밀도는 내려간다', '모든 지표가 함께 오른다', '아무 변화가 없다'], 0,
               '낮은 확률도 부도로 보니 놓치는 사람은 줄지만 멀쩡한 사람 경고가 늘어납니다. 기준값은 실수의 비용을 아는 사람이 정합니다.'),
    ),
])
