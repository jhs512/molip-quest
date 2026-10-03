"""2일차 · 5교시 — 분리와 전처리 Pipeline"""
from kpc_course.dsl import *

UNIT = unit('preprocessing', '2일차 · 5교시 — 분리와 전처리 Pipeline', [
    concept('fit-train', '기준은 훈련 자료에서만 정한다',
        body="""
        4교시에서 입력 `X`와 정답 `y`를 만들었습니다. 이제 둘을 훈련 자료와 테스트 자료로 나눕니다. 손으로 자르지 않고 `train_test_split`에 맡기는데, 인자 세 개의 뜻만 알면 됩니다. `test_size=0.2`는 20%를 테스트로 떼어 두라는 것, `stratify=y`는 두 쪽의 생존 비율이 비슷하게 섞으라는 것, `random_state=42`는 누가 실행해도 똑같이 나뉘게 하는 고정 번호입니다. 돌려주는 순서는 훈련 입력, 테스트 입력, 훈련 정답, 테스트 정답입니다.

        ```python
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
        ```

        나눈 다음에 손질을 시작합니다. 나이의 빈칸을 중앙값으로 채우려면 "중앙값이 얼마인가"를 먼저 알아야 하고, `성별`을 One-hot으로 바꾸려면 "어떤 값들이 있는가"를 알아야 합니다. 이렇게 손질의 **기준을 정하는 일** 자체가 자료를 들여다보는 학습입니다. 그래서 기준은 **훈련 자료에서만** 정하고, 테스트 자료에는 정해진 기준을 **적용만** 합니다. 테스트의 나이까지 넣어 중앙값을 구하면 모의고사 문제를 미리 본 셈이 됩니다. 작은 누수입니다.

        `scikit-learn`의 손질 도구들은 이 구분을 메서드 이름으로 드러냅니다. `fit`은 기준 정하기, `transform`은 적용하기, `fit_transform`은 둘을 한 번에. 그러니 훈련에는 `fit_transform`, 테스트에는 `transform`입니다.

        ```python
        from sklearn.impute import SimpleImputer
        imputer = SimpleImputer(strategy='median')
        train_values = imputer.fit_transform(X_train[['나이', '요금']])  # 훈련에서 중앙값을 정하고 채움
        test_values = imputer.transform(X_test[['나이', '요금']])        # 같은 중앙값으로 채우기만
        ```

        이 규칙은 빈칸 채우기뿐 아니라 One-hot 인코딩, 숫자 크기 맞추기(표준화) 전부에 똑같이 적용됩니다. 한 번 더 요약하면, **훈련에서 정하고 테스트에는 적용만.**
        """,
        check=short('빈칸을 채울 중앙값이나 One-hot의 값 목록 같은 손질 기준은 훈련 자료와 테스트 자료 중 어느 쪽에서만 정해야 하나요?', ['훈련 자료', '훈련자료', '훈련', '훈련 데이터', '훈련데이터', 'train', 'X_train'],
                    '기준을 정하는 것은 자료를 들여다보는 학습입니다. 테스트까지 넣으면 모의고사를 미리 본 셈이라 훈련에서만 `fit`하고 테스트에는 `transform`만 합니다.')),
    coding('stratified-split', '훈련 자료와 테스트 자료로 나누기',
        goal="""
        `X`, `y`를 `train_test_split`으로 나눠 `X_train`, `X_test`, `y_train`, `y_test`를 만드세요. `test_size=0.2`, `stratify=y`, `random_state=42`입니다. 두 쪽의 행 수와 생존 비율을 출력하세요.

        훈련 1047명, 테스트 262명으로 나뉘고 두 쪽의 생존 비율이 거의 같으면 맞게 한 것입니다.
        """,
        hint="""
        `train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)`가 네 개를 순서대로 돌려줍니다. 행 수는 `len()`, 생존 비율은 `y_train.mean()`과 `y_test.mean()`입니다.
        """,
        starter=TI + FEATURES + "from sklearn.model_selection import train_test_split\n# 네 변수를 만드세요\n",
        solution=TI + FEATURES + SPLIT + "print(len(X_train),len(X_test))\nprint(y_train.mean(),y_test.mean())\n",
        check="assert len(s['X_train'])==1047 and len(s['X_test'])==262\nassert set(s['X_train'].index).isdisjoint(s['X_test'].index)\nassert len(s['y_train'])==1047 and len(s['y_test'])==262\nassert abs(s['y_train'].mean()-s['y_test'].mean())<0.01"),
    coding('first-model', '손질 없이 첫 모델 돌려 보기',
        goal="""
        손질을 배우기 전에 모델이 실제로 어떻게 돌아가는지 한 번 봅니다. 빈칸이 없고 이미 숫자인 열 `객실등급`, `형제배우자`, `부모자녀` 세 개만 씁니다. `LogisticRegression(max_iter=1000)`을 `model`에 만들고 `X_train[simple]`, `y_train`으로 학습한 뒤, `X_test[simple]`을 예측해 정확도를 `accuracy`에 저장하고 출력하세요.

        정확도는 0과 1 사이의 어떤 값이 나옵니다. 재료가 셋뿐이니 높지 않습니다. 이 숫자를 기억해 두세요. 오늘 남은 시간은 이 숫자를 올리는 일입니다.
        """,
        hint="""
        모델은 늘 세 단계입니다. 만들기 `model = LogisticRegression(max_iter=1000)`, 학습 `model.fit(X_train[simple], y_train)`, 예측 `pred = model.predict(X_test[simple])`. 그다음 `accuracy = accuracy_score(y_test, pred)`가 테스트 정답과 예측이 일치한 비율입니다.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\nsimple = ['객실등급','형제배우자','부모자녀']\n# model을 학습하고 accuracy를 구하세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import accuracy_score\nsimple = ['객실등급','형제배우자','부모자녀']\nmodel = LogisticRegression(max_iter=1000)\nmodel.fit(X_train[simple], y_train)\npred = model.predict(X_test[simple])\naccuracy = accuracy_score(y_test, pred)\nprint(accuracy)\n",
        check="assert 0<=s['accuracy']<=1\nassert s['model'].n_features_in_==3\nassert abs(s['accuracy']-(s['model'].predict(s['X_test'][['객실등급','형제배우자','부모자녀']])==s['y_test']).mean())<1e-12"),
    coding('train-imputer', '빈 나이와 요금을 훈련 기준으로 채우기',
        goal="""
        나이와 요금의 빈칸을 채웁니다. `SimpleImputer(strategy='median')`를 `imputer`에 만들고, 훈련 표의 `['나이', '요금']`에 `fit_transform`한 결과를 `train_values`, 테스트 표의 같은 열에 `transform`한 결과를 `test_values`에 저장하세요. 두 결과의 `shape`를 출력합니다.

        훈련 1047행, 테스트 262행에 열 두 개씩이고 빈 값이 하나도 없으면 맞게 한 것입니다.
        """,
        hint="""
        `imputer.fit_transform(X_train[['나이', '요금']])`는 훈련 자료에서 중앙값을 정하고 바로 채웁니다. 테스트에는 같은 `imputer`로 `imputer.transform(X_test[['나이', '요금']])`만 호출하세요. 테스트에 `fit`을 다시 하면 기준이 바뀝니다.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.impute import SimpleImputer\n# imputer와 두 변환 결과를 만드세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.impute import SimpleImputer\nimputer=SimpleImputer(strategy='median')\ntrain_values=imputer.fit_transform(X_train[['나이','요금']])\ntest_values=imputer.transform(X_test[['나이','요금']])\nprint(train_values.shape,test_values.shape)\n",
        check="import numpy as np\nassert s['train_values'].shape==(1047,2) and s['test_values'].shape==(262,2)\nassert np.isfinite(s['train_values']).all() and np.isfinite(s['test_values']).all()\nassert np.allclose(s['imputer'].statistics_,s['X_train'][['나이','요금']].median().to_numpy())"),
    coding('onehot-fit', '글자 열을 훈련 기준으로 One-hot',
        goal="""
        4교시의 `get_dummies`를 모델 흐름에 맞는 도구로 바꿉니다. `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`를 `encoder`에 만들고, `X_train[['성별']]`에 `fit_transform`한 결과를 `train_encoded`, `X_test[['성별']]`에 `transform`한 결과를 `test_encoded`에 저장해 `shape`를 출력하세요.

        두 결과 모두 열이 2개(여성, 남성)이면 맞게 한 것입니다.
        """,
        hint="""
        빈칸 채우기와 똑같은 모양입니다. 훈련에는 `fit_transform`, 테스트에는 `transform`. `handle_unknown='ignore'`는 테스트에 처음 보는 값이 나와도 오류 대신 0으로 두라는 뜻이고, `sparse_output=False`는 결과를 보통 배열로 달라는 뜻입니다.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.preprocessing import OneHotEncoder\n# encoder, train_encoded, test_encoded를 만드세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.preprocessing import OneHotEncoder\nencoder = OneHotEncoder(handle_unknown='ignore', sparse_output=False)\ntrain_encoded = encoder.fit_transform(X_train[['성별']])\ntest_encoded = encoder.transform(X_test[['성별']])\nprint(train_encoded.shape, test_encoded.shape)\n",
        check="assert s['train_encoded'].shape==(1047,2) and s['test_encoded'].shape==(262,2)\nassert sorted(s['encoder'].categories_[0])==['남성','여성']\nassert (s['train_encoded'].sum(axis=1)==1).all()"),
    concept('why-pipeline', '손질이 늘어나면 순서가 꼬인다, 그래서 한 줄로 묶는다',
        body="""
        지금까지 손질 도구를 둘 썼습니다. 빈칸 채우기, One-hot. 실제로는 하나 더 필요합니다. 나이는 0~80, 요금은 0~500, `형제배우자`는 0~8처럼 열마다 숫자 크기가 제각각이라 어떤 모델은 큰 숫자 열에 끌려갑니다. 그래서 각 열을 "평균 0, 퍼짐 1"로 맞추는 **표준화**(`StandardScaler`)를 합니다. 이것도 기준(평균과 퍼짐)을 훈련에서 정하고 테스트에 적용하는 도구입니다.

        손질이 셋이 되면 코드가 길어지고, 무엇보다 **순서와 짝을 틀리기 쉬워집니다.** 훈련에는 `fit_transform`, 테스트에는 `transform`을 셋 다 정확히 맞춰야 하고, 모델에 넣기 전에 결과를 다시 합쳐야 합니다. 한 군데라도 테스트에 `fit`을 하면 조용히 누수가 생기는데, 오류가 나지 않아서 알아차리기 어렵습니다.

        `Pipeline`은 이 단계들을 **순서대로 한 줄에 묶어** 주는 도구입니다. 묶고 나면 `fit`을 한 번만 부르면 안쪽 단계들이 차례로 훈련 자료에서 기준을 정하고, `transform`이나 `predict`를 부르면 같은 순서로 적용만 합니다. 짝을 틀릴 자리가 없어집니다.

        ```python
        from sklearn.pipeline import Pipeline
        numeric_pipeline = Pipeline([
            ('fill', SimpleImputer(strategy='median')),   # 1단계: 빈칸 채우기
            ('scale', StandardScaler()),                  # 2단계: 크기 맞추기
        ])
        train_values = numeric_pipeline.fit_transform(X_train[numeric])  # 두 단계 모두 훈련에서 fit
        test_values = numeric_pipeline.transform(X_test[numeric])        # 두 단계 모두 적용만
        ```

        `(이름, 도구)` 쌍을 리스트에 순서대로 넣는 것이 전부입니다. 다음 시간에는 숫자 열용 묶음과 글자 열용 묶음을 합치고 그 끝에 모델까지 붙여서, `fit` 한 번으로 손질과 학습이 끝나는 완성형을 씁니다.
        """,
        check=short('빈칸 채우기, 표준화 같은 손질 단계들을 순서대로 묶어 `fit` 한 번에 처리하게 해 주는 `scikit-learn` 도구의 이름은 무엇인가요?', ['Pipeline', 'pipeline', '파이프라인'],
                    '`Pipeline`에 `(이름, 도구)` 쌍을 순서대로 넣으면 훈련에서는 차례로 `fit`, 테스트에서는 차례로 `transform`만 합니다.')),
    coding('pipeline-build', '빈칸 채우기와 표준화를 한 줄로 묶기',
        goal="""
        `Pipeline([('fill', SimpleImputer(strategy='median')), ('scale', StandardScaler())])`를 `numeric_pipeline`에 만드세요. 숫자 열 `numeric`에 대해 훈련은 `fit_transform`, 테스트는 `transform`해 `train_values`, `test_values`에 저장하고 `shape`를 출력합니다.

        훈련 1047행 5열, 테스트 262행 5열이면 맞게 한 것입니다. 표준화를 거친 훈련 자료는 열마다 평균이 0에 가깝습니다.
        """,
        hint="""
        `Pipeline`의 괄호 안에 리스트, 리스트 안에 `(이름, 도구)` 튜플 두 개입니다. 만든 뒤에는 도구 하나처럼 `numeric_pipeline.fit_transform(X_train[numeric])`, `numeric_pipeline.transform(X_test[numeric])`로 씁니다.
        """,
        starter=TI + FEATURES + SPLIT + "from sklearn.impute import SimpleImputer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nnumeric = ['객실등급','나이','형제배우자','부모자녀','요금']\n# numeric_pipeline, train_values, test_values를 만드세요\n",
        solution=TI + FEATURES + SPLIT + "from sklearn.impute import SimpleImputer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nnumeric = ['객실등급','나이','형제배우자','부모자녀','요금']\nnumeric_pipeline = Pipeline([('fill', SimpleImputer(strategy='median')), ('scale', StandardScaler())])\ntrain_values = numeric_pipeline.fit_transform(X_train[numeric])\ntest_values = numeric_pipeline.transform(X_test[numeric])\nprint(train_values.shape, test_values.shape)\n",
        check="import numpy as np\nassert s['train_values'].shape==(1047,5) and s['test_values'].shape==(262,5)\nassert np.isfinite(s['train_values']).all() and np.isfinite(s['test_values']).all()\nassert np.allclose(s['train_values'].mean(axis=0),0,atol=1e-8)\nassert list(s['numeric_pipeline'].named_steps)==['fill','scale']"),
    quiz('pipeline-check', '2일차 5교시 점검',
        choice('올바른 손질 순서는 어느 것인가요?',
               ['훈련·테스트를 먼저 나누고, 훈련에서 `fit`, 테스트에는 `transform`', '전체 자료에서 `fit`한 뒤 나눈다', '테스트에서 `fit`하고 훈련에 `transform`'], 0,
               '기준을 정하는 `fit`에 테스트가 섞이면 모의고사를 미리 본 셈입니다. 나누는 것이 먼저입니다.'),
        short('누가 실행해도 똑같이 나뉘도록 `train_test_split`에 넣는 고정 번호 인자의 이름은 무엇인가요?', ['random_state'],
              '`random_state=42`처럼 같은 번호를 쓰면 같은 분리가 재현됩니다. 결과를 비교하려면 분리가 같아야 합니다.'),
        choice('`stratify=y`는 무엇을 맞추려는 것인가요?',
               ['훈련과 테스트의 생존 비율이 비슷하도록', '행 수가 같도록', '나이 순서대로 나뉘도록'], 0,
               '무작위로 나누다 보면 한쪽에 생존자가 몰릴 수 있습니다. `stratify`는 정답 비율을 양쪽에 비슷하게 유지합니다.'),
        choice("`encoder.fit_transform(X_test[['성별']])`처럼 테스트에 `fit`을 하면 무슨 문제가 생기나요?",
               ['테스트 자료로 기준을 정하는 누수가 된다', '더 정확해진다', '열 수가 바뀐다'], 0,
               '값 목록·중앙값·평균 같은 기준은 훈련에서만 정합니다. 테스트에는 정해진 기준을 적용만 해야 합니다.'),
        choice('`Pipeline`을 쓰는 가장 큰 이유는 무엇인가요?',
               ['손질 단계마다 `fit`과 `transform` 짝을 틀릴 자리를 없애려고', '코드가 더 길어져서', '정확도가 자동으로 오르기 때문에'], 0,
               '단계를 묶으면 `fit` 한 번에 전부 훈련에서 기준을 정하고, 적용할 때는 전부 적용만 합니다. 조용한 누수를 막습니다.'),
        choice('1309명을 `test_size=0.2`로 나누면 테스트 자료는 약 몇 명인가요?',
               ['약 262명', '약 1047명', '약 20명'], 0,
               '20%가 테스트입니다. 1309의 20%는 약 262명이고 나머지 1047명이 훈련입니다.'),
    ),
])
