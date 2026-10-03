"""2일차 · 6교시 — 세 분류 모델과 기준 비교"""
from kpc_course.dsl import *

MODEL_PREP = TI + FEATURES + SPLIT + PREP

UNIT = unit('classifiers', '2일차 · 6교시 — 세 분류 모델과 기준 비교', [
    concept('baselines', '"좋다"고 말하려면 비교할 기준이 있어야 한다',
        body="""
        손질이 끝났으니 모델을 고를 차례입니다. 이 수업에서는 세 가지를 씁니다. 수식 없이 각각이 무엇을 하는지만 잡아 두면 됩니다.

        **로지스틱 회귀**(`LogisticRegression`)는 입력마다 점수를 매겨 더한 뒤, 합이 어떤 선을 넘으면 생존, 못 넘으면 사망으로 가릅니다. 어느 열이 얼마나 중요한지가 점수로 남아 설명하기 쉽습니다. **결정 트리**(`DecisionTreeClassifier`)는 스무고개입니다. "여성인가? → 3등실인가? → 나이가 15세 이하인가?" 같은 질문을 가지처럼 뻗어 가며 가릅니다. 질문을 끝없이 늘리면 훈련 자료를 통째로 외워 버릴 수 있어서 `max_depth`로 질문 깊이를 제한합니다. **랜덤 포레스트**(`RandomForestClassifier`)는 서로 조금씩 다른 트리를 수십 개 만들어 다수결로 정합니다. 한 트리의 실수를 다른 트리들이 덮어 주어 보통 트리 하나보다 안정적입니다.

        모델이 몇 개든 비교 방식은 하나입니다. **같은 훈련 자료로 배우고, 같은 테스트 자료로 채점한다.** 그런데 그 전에 물어야 할 것이 있습니다. 정확도 78%는 좋은 걸까요? 테스트 262명 중 사망이 162명이므로 **아무것도 보지 않고 전원 사망이라고 찍어도 62%**가 나옵니다. 모델의 실력은 이 "찍기 점수"와 비교해야 보입니다. 그래서 가장 많은 답만 찍는 `DummyClassifier`를 기준 모델로 먼저 돌립니다. 기준보다 못한 모델은 아무것도 배우지 못한 것입니다. 현장도 마찬가지입니다. 콜센터 팀장이 월요일 인력을 짤 때 가장 단순한 방법은 "지난주 월요일과 같게"입니다. 통화량 예측 모델을 들여왔는데 이 방법보다 더 빗나간다면, 그 모델은 팀장의 감보다 못한 것입니다.

        ```python
        model = Pipeline([('prepare', make_preprocessor()), ('model', LogisticRegression(max_iter=2000))])
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        accuracy_score(y_test, pred)
        ```

        준비 코드의 `make_preprocessor()`는 5교시에서 만든 숫자용 묶음(채우기+표준화)과 글자용 묶음(채우기+One-hot)을 하나로 합친 손질기입니다. 그 뒤에 모델을 붙인 `Pipeline`을 쓰면 `fit` 한 번으로 손질과 학습이 끝나고, `predict` 한 번으로 손질과 예측이 끝납니다. 모델을 바꿀 때는 `('model', ...)` 자리만 바꿉니다.

        점수는 정확도(accuracy, 전체 중 맞힌 비율) 하나만 보지 않습니다. 생존자가 적은 자료에서는 생존자를 얼마나 잘 찾아냈는지를 따로 보는 F1 점수도 함께 적습니다. 자세한 뜻은 8교시에서 다룹니다. 지금은 "두 점수를 표로 나란히 적는다"까지만.
        """,
        check=short('입력을 보지 않고 가장 많은 답만 찍는 기준 모델의 `scikit-learn` 이름은 무엇인가요?', ['DummyClassifier', 'Dummy', '더미 분류기', '더미분류기'],
                    '`DummyClassifier(strategy="most_frequent")`가 기준입니다. 이 점수를 넘지 못하는 모델은 아무것도 배우지 못한 것입니다.')),
    coding('dummy-only', '찍기 점수부터 재기',
        goal="""
        기준 모델만 먼저 돌립니다. `DummyClassifier(strategy='most_frequent')`를 `dummy`에 만들고 `X_train`, `y_train`으로 학습한 뒤 `X_test`를 예측해 정확도를 `dummy_accuracy`에 저장하고 출력하세요.

        입력을 보지 않으니 손질이 필요 없습니다. 테스트 262명 중 사망 162명이므로 162/262가 나옵니다. 이 숫자가 오늘의 기준선입니다.
        """,
        hint="""
        `dummy.fit(X_train, y_train)` 뒤에 `accuracy_score(y_test, dummy.predict(X_test))`입니다. 예측값을 출력해 보면 전부 0입니다.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.dummy import DummyClassifier\nfrom sklearn.metrics import accuracy_score\n# dummy를 학습하고 dummy_accuracy를 구하세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.dummy import DummyClassifier\nfrom sklearn.metrics import accuracy_score\ndummy = DummyClassifier(strategy='most_frequent')\ndummy.fit(X_train, y_train)\ndummy_accuracy = accuracy_score(y_test, dummy.predict(X_test))\nprint(dummy_accuracy)\n",
        check="assert abs(s['dummy_accuracy']-162/262)<1e-10\nassert set(s['dummy'].predict(s['X_test']))=={0}"),
    coding('model-comparison', '네 모델을 한 표에서 비교하기',
        goal="""
        기준 모델과 세 모델을 같은 조건에서 비교합니다. `models` 딕셔너리에 `Dummy`, `Logistic`, `Tree`, `Forest` 이름으로 모델을 넣고, 각각을 `Pipeline([('prepare', make_preprocessor()), ('model', ...)])`로 묶어 학습·예측한 뒤 `accuracy`와 `f1`을 구해 `results` 표를 만드세요. `Forest`는 `n_estimators=50, max_depth=5, random_state=42`입니다.

        `results`는 모델 이름이 인덱스이고 `accuracy`, `f1` 두 열입니다. 기준 모델의 정확도가 앞 미션의 162/262와 같고 F1이 0이면 표가 맞게 만들어진 것입니다. 어느 모델이 기준을 얼마나 넘는지 보세요.
        """,
        hint="""
        표 만들기 패턴입니다. 빈 리스트 `rows = []`를 두고 `for name, estimator in models.items():` 안에서 (1) `Pipeline`을 새로 만들고 (2) `fit` (3) `predict` (4) `rows.append({'model': name, 'accuracy': ..., 'f1': f1_score(y_test, pred, zero_division=0)})`. 반복이 끝나면 `results = pd.DataFrame(rows).set_index('model')`. 모델 자체도 `fitted[name] = model`로 보관해 두세요.
        """,
        starter=MODEL_PREP + "from sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score,f1_score\n# models 딕셔너리와 results를 만드세요\n",
        solution=MODEL_PREP + "from sklearn.dummy import DummyClassifier\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.tree import DecisionTreeClassifier\nfrom sklearn.ensemble import RandomForestClassifier\nfrom sklearn.metrics import accuracy_score,f1_score\nmodels={'Dummy':DummyClassifier(strategy='most_frequent'),'Logistic':LogisticRegression(max_iter=2000),'Tree':DecisionTreeClassifier(max_depth=4,random_state=42),'Forest':RandomForestClassifier(n_estimators=50,max_depth=5,random_state=42)}\nrows=[]\nfitted={}\nfor name,estimator in models.items():\n    model=Pipeline([('prepare',make_preprocessor()),('model',estimator)])\n    model.fit(X_train,y_train)\n    pred=model.predict(X_test)\n    fitted[name]=model\n    rows.append({'model':name,'accuracy':accuracy_score(y_test,pred),'f1':f1_score(y_test,pred,zero_division=0)})\nresults=pd.DataFrame(rows).set_index('model')\nresults\n",
        check="assert set(s['results'].index)=={'Dummy','Logistic','Tree','Forest'}\nassert set(s['results'].columns)=={'accuracy','f1'}\nassert ((s['results']>=0)&(s['results']<=1)).all().all()\nassert abs(s['results'].loc['Dummy','accuracy']-162/262)<1e-10\nassert s['results'].loc['Dummy','f1']==0"),
    coding('train-vs-test', '외운 모델 잡아내기',
        goal="""
        질문 깊이를 제한하지 않은 `DecisionTreeClassifier(random_state=42)`를 손질기와 묶어 `model`에 학습하세요. 그리고 정확도를 두 번 잽니다. 훈련 자료로 잰 `train_accuracy`와 테스트 자료로 잰 `test_accuracy`. 둘을 출력하세요.

        훈련 점수는 90%를 훌쩍 넘지만 테스트 점수는 한참 낮습니다. 문제집은 거의 다 맞히는데 모의고사는 못 보는, **외운 모델**입니다. 이 현상을 과적합이라고 합니다.
        """,
        hint="""
        `model = Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(random_state=42))])` → `fit(X_train, y_train)`. 그다음 `accuracy_score(y_train, model.predict(X_train))`과 `accuracy_score(y_test, model.predict(X_test))`를 각각 저장하세요.
        """,
        starter=MODEL_PREP + "from sklearn.tree import DecisionTreeClassifier\nfrom sklearn.metrics import accuracy_score\n# model, train_accuracy, test_accuracy를 만드세요\n",
        solution=MODEL_PREP + "from sklearn.tree import DecisionTreeClassifier\nfrom sklearn.metrics import accuracy_score\nmodel = Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(random_state=42))])\nmodel.fit(X_train, y_train)\ntrain_accuracy = accuracy_score(y_train, model.predict(X_train))\ntest_accuracy = accuracy_score(y_test, model.predict(X_test))\nprint(train_accuracy, test_accuracy)\n",
        check="assert 0<=s['test_accuracy']<=1 and 0<=s['train_accuracy']<=1\nassert s['train_accuracy']>s['test_accuracy']\nassert s['train_accuracy']>0.9\nassert abs(s['train_accuracy']-(s['model'].predict(s['X_train'])==s['y_train']).mean())<1e-12"),
    quiz('model-check', '2일차 6교시 점검',
        choice('정확도 78%짜리 모델이 좋은지 판단하려면 무엇과 비교해야 하나요?',
               ['아무것도 보지 않고 가장 많은 답만 찍은 기준 모델의 점수', '훈련 자료로 잰 점수', '100%'], 0,
               '테스트 262명 중 162명이 사망이라 전원 사망으로 찍어도 62%입니다. 기준을 넘는 만큼이 모델이 배운 몫입니다.'),
        choice('훈련 정확도 98%, 테스트 정확도 76%인 모델은 어떤 상태인가요?',
               ['훈련 자료를 외운 과적합', '완벽한 모델', '학습이 덜 된 모델'], 0,
               '문제집은 다 맞히고 모의고사는 못 보는 상태입니다. 실력은 테스트 점수가 더 가깝습니다.'),
        short('서로 조금씩 다른 결정 트리를 수십 개 만들어 다수결로 정하는 모델의 이름은 무엇인가요?', ['RandomForest', 'Random Forest', '랜덤 포레스트', '랜덤포레스트', 'RandomForestClassifier'],
              '랜덤 포레스트는 트리 여러 개의 다수결입니다. 한 트리의 실수를 다른 트리들이 덮어 줍니다.'),
        choice("`DecisionTreeClassifier(max_depth=4)`에서 `max_depth`는 무엇을 하나요?",
               ['스무고개 질문의 깊이를 제한해 외우는 것을 막는다', '정확도를 4%로 고정한다', '트리를 4개 만든다'], 0,
               '질문을 끝없이 늘리면 훈련 자료를 통째로 외웁니다. 깊이 제한이 과적합을 줄이는 가장 간단한 방법입니다.'),
        choice('모델 네 개를 공정하게 비교하려면 무엇이 같아야 하나요?',
               ['훈련 자료, 테스트 자료, 손질 방법, 점수 종류', '모델 이름의 길이', '학습에 걸린 시간'], 0,
               '조건이 하나라도 다르면 점수 차이가 모델 때문인지 조건 때문인지 알 수 없습니다.'),
        short('기준 모델의 테스트 정확도가 162/262인 이유는 테스트 262명 중 사망이 몇 명이기 때문인가요?', ['162', '162명'],
              '가장 많은 답(사망)만 찍으면 사망자 수만큼 맞힙니다. 162/262, 약 62%입니다.'),
    ),
])
