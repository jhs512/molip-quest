"""2일차 · 4교시 — 입력과 정답 분리"""
from kpc_course.dsl import *

UNIT = unit('features', '2일차 · 4교시 — 입력과 정답 분리', [
    concept('what-is-learning', '표에서 규칙을 찾아 빈칸을 채우는 것',
        body="""
        오전 내내 "누가 살아남았나"를 표와 그림으로 들여다봤습니다. 이제 질문을 바꿉니다. **승객 정보만 주어졌을 때 생존 여부를 맞힐 수 있을까?** 사람이 규칙을 적는 대신, 컴퓨터가 1,309명의 기록을 보고 규칙을 스스로 찾게 하는 것이 머신러닝입니다. 거창해 보이지만 하는 일은 하나입니다. 표에서 **입력과 정답의 관계**를 찾아, 정답이 비어 있는 새 행의 빈칸을 채우는 것.

        용어 네 개만 정리하면 됩니다. 맞히는 데 쓰는 재료 열들을 **입력**(`X`), 맞히려는 칸을 **정답**(`y`, 어제 배운 타깃)이라고 합니다. 규칙을 찾는 과정을 **학습**(fit), 찾은 규칙을 새 행에 적용하는 것을 **예측**(predict)이라고 합니다. 정답이 "생존/사망"처럼 몇 가지 중 하나를 고르는 것이면 **분류**, 모레 다룰 주가처럼 숫자를 맞히는 것이면 **회귀**입니다.

        그런데 규칙을 찾은 다음, 그 규칙이 쓸 만한지 어떻게 알까요? 학습에 쓴 1,309명에게 다시 물어보면 당연히 잘 맞힙니다. 문제집을 풀고 나서 같은 문제집으로 시험을 치는 셈이니까요. 실력을 재려면 **학습에 쓰지 않은 행**으로 시험을 쳐야 합니다. 그래서 표를 둘로 나눕니다. 규칙을 찾는 데 쓰는 **훈련 자료**(문제집)와, 다 배운 뒤 한 번만 채점하는 **테스트 자료**(모의고사)입니다.

        ```python
        X = titanic[['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked']]
        y = titanic['survived']
        model.fit(X_train, y_train)        # 훈련 자료로 규칙 찾기
        prediction = model.predict(X_test) # 테스트 자료의 빈칸 채우기
        ```

        이 흐름은 모레까지 변하지 않습니다. 입력과 정답을 나누고, 훈련과 테스트를 나누고, 훈련으로 배워 테스트로 채점한다. 오늘 남은 시간은 이 네 줄을 제대로 하기 위한 준비입니다.
        """,
        check=short('규칙을 찾는 데 쓰지 않고 다 배운 뒤 한 번만 채점하는 데 쓰는 자료, 비유하면 모의고사에 해당하는 자료를 무엇이라고 하나요?', ['테스트 자료', '테스트자료', '테스트 데이터', '테스트데이터', 'test', '테스트'],
                    '학습에 쓴 자료로 채점하면 외운 것인지 이해한 것인지 알 수 없습니다. 테스트 자료는 학습에 쓰지 않고 남겨 둔 몫입니다.')),
    concept('leakage', '시험지에 답이 적혀 있으면 점수는 의미가 없다',
        body="""
        입력으로 어떤 열을 쓸지 고를 때 어제의 원칙이 그대로 옵니다. **맞히려는 시점에 알 수 있는 것만.** 타이타닉에서 승객의 등급·성별·나이·요금은 배를 타기 전에 정해지지만, `boat`(구명보트 번호)와 `body`(시신 번호)는 사고가 끝난 뒤에야 적힙니다. 이 둘을 입력에 넣으면 모델은 "보트 번호가 있으면 생존"이라는 규칙을 찾아 거의 100%를 맞힙니다. 그런데 그 모델은 아무 쓸모가 없습니다. 사고 전에는 보트 번호를 모르기 때문입니다.

        이렇게 **정답을 알려 주는 정보가 입력에 새어 들어오는 것**을 누수(leakage)라고 합니다. 가장 노골적인 누수는 정답 열 `survived` 자체를 입력에 넣는 것이고, `boat`·`body`처럼 정답과 사실상 같은 열도 누수입니다. 누수가 있으면 테스트 점수가 아무리 높아도 믿을 수 없습니다. 시험지에 답이 적혀 있는데 만점을 받은 것과 같습니다.

        ```python
        features = ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked']
        X = titanic[features].copy()         # 사고 전에 알 수 있는 7개 열
        y = titanic['survived'].astype(int)  # 정답
        ```

        이름, 티켓 번호, 선실 번호, 목적지도 뺍니다. 누수는 아니지만 사람마다 거의 다 달라서 규칙을 찾을 재료가 못 됩니다. 남는 일곱 열 중 넷은 숫자, 둘은 글자(`sex`, `embarked`)이고, 나이와 요금에는 빈칸이 있습니다. 모델은 숫자만 받고 빈칸을 싫어하므로 이 상태 그대로는 학습이 안 됩니다. 글자를 숫자로 바꾸고 빈칸을 채우는 손질이 다음 시간의 주제이고, 이번 시간은 어느 열을 쓰고 어느 열을 뺄지 정하는 데서 끝납니다.
        """,
        check=short('정답을 알려 주는 정보가 입력에 섞여 들어와 점수를 믿을 수 없게 되는 현상을 무엇이라고 하나요?', ['누수', '데이터 누수', '데이터누수', 'leakage', 'data leakage'],
                    '누수(leakage)가 있으면 모델은 답을 보고 답을 맞히는 셈이라 테스트 점수가 실력을 반영하지 않습니다.')),
    coding('drop-columns', '쓰지 않을 열 빼기',
        goal="""
        입력 후보를 추립니다. `titanic.drop(columns=[...])`으로 정답 `survived`와 쓰지 않을 열 `name`, `ticket`, `cabin`, `boat`, `body`, `home.dest`를 빼서 `candidates`에 저장하고, 남은 열 이름을 출력하세요.

        일곱 열이 남으면 맞게 한 것입니다.
        """,
        hint="""
        `drop(columns=[...])`에 뺄 열 이름을 리스트로 넣습니다. 열 이름은 전부 소문자이고 `home.dest`에는 점이 들어 있습니다. 결과를 변수에 받아야 합니다.
        """,
        starter=TI + "# candidates를 만들고 열 이름을 출력하세요\n",
        solution=TI + "candidates = titanic.drop(columns=['survived','name','ticket','cabin','boat','body','home.dest'])\nprint(list(candidates.columns))\n",
        check="assert list(s['candidates'].columns)==['pclass','sex','age','sibsp','parch','fare','embarked']\nassert len(s['candidates'])==1309"),
    coding('xy-separation', '입력 X와 정답 y 만들기',
        goal="""
        이번에는 쓸 열을 직접 골라 입력과 정답을 만듭니다. 일곱 열 이름을 담은 리스트 `features`를 만들고, `X = titanic[features].copy()`로 입력을, `y`에 `survived`를 정수로 저장하세요.

        `X`가 1309행 7열이고 `y`의 합이 생존자 수 500이면 맞게 한 것입니다.
        """,
        hint="""
        `features = ['pclass', 'sex', 'age', 'sibsp', 'parch', 'fare', 'embarked']`, `X = titanic[features].copy()`, `y = titanic['survived'].astype(int)`. `.copy()`는 뒤에서 `X`를 고쳐도 원본 표가 안 바뀌게 합니다.
        """,
        starter=TI + "# features, X, y를 만드세요\n",
        solution=TI + FEATURES + "print(X.shape,y.shape)\nX.head()\n",
        check="assert list(s['X'].columns)==['pclass','sex','age','sibsp','parch','fare','embarked']\nassert s['X'].shape==(1309,7) and len(s['y'])==1309\nassert int(s['y'].sum())==500"),
    coding('column-types', '숫자 열과 글자 열 나누기',
        goal="""
        다음 시간에 숫자 열과 글자 열을 다르게 손질할 것이므로 미리 갈라 둡니다. 준비된 `X`에서 숫자 열 이름 리스트를 `numeric_columns`, 글자(범주) 열 이름 리스트를 `category_columns`에 저장하고 출력하세요.

        숫자 다섯, 글자 둘이면 맞게 나눈 것입니다.
        """,
        hint="""
        `X.select_dtypes('number')`는 숫자 열만 남긴 표, `X.select_dtypes(exclude='number')`는 나머지 열만 남긴 표입니다. 각각 `.columns`를 `list()`로 감싸세요.
        """,
        starter=TI + FEATURES + "# numeric_columns, category_columns를 만들고 출력하세요\n",
        solution=TI + FEATURES + "numeric_columns = list(X.select_dtypes('number').columns)\ncategory_columns = list(X.select_dtypes(exclude='number').columns)\nprint(numeric_columns)\nprint(category_columns)\n",
        check="assert list(s['numeric_columns'])==['pclass','age','sibsp','parch','fare']\nassert list(s['category_columns'])==['sex','embarked']"),
    coding('get-dummies', '글자 열을 숫자 열로: One-hot',
        goal="""
        모델은 `female`, `male` 같은 글자를 받지 못합니다. 흔한 해결은 값마다 열을 하나씩 만들어 해당하면 1, 아니면 0을 적는 것이고, 이를 One-hot 인코딩이라고 부릅니다. `pd.get_dummies(titanic[['sex']])`로 `sex` 열을 바꿔 `encoded`에 저장하고 마지막 줄에 `encoded.head()`를 적으세요.

        `sex_female`, `sex_male` 두 열이 생기고, 각 행에서 둘 중 하나만 1이면 맞게 된 것입니다.
        """,
        hint="""
        `pd.get_dummies(표)`가 글자 열의 값마다 새 열을 만듭니다. `titanic[['sex']]`처럼 대괄호 두 겹으로 표를 넘기세요. 다음 시간에 쓸 `OneHotEncoder`가 같은 일을 모델 흐름 안에서 합니다.
        """,
        starter=TI + "# encoded를 만들고 head()를 확인하세요\n",
        solution=TI + "encoded = pd.get_dummies(titanic[['sex']])\nprint(encoded.shape)\nencoded.head()\n",
        check="assert list(s['encoded'].columns)==['sex_female','sex_male'] and s['encoded'].shape==(1309,2)\nassert (s['encoded'].astype(int).sum(axis=1)==1).all()"),
    quiz('features-check', '2일차 4교시 점검',
        choice('생존/사망처럼 몇 가지 중 하나를 고르는 예측은 무엇이라고 하나요?',
               ['분류', '회귀', '군집'], 0,
               '고르는 것은 분류, 숫자를 맞히는 것은 회귀입니다. 모레 주가는 회귀입니다.'),
        choice('학습에 쓴 자료로 그대로 채점하면 왜 안 되나요?',
               ['외운 것인지 이해한 것인지 구분할 수 없다', '컴퓨터가 느려진다', '정확도가 항상 0이 된다'], 0,
               '문제집으로 시험을 치는 것과 같습니다. 실력은 처음 보는 테스트 자료로 재야 합니다.'),
        choice('`boat`(구명보트 번호)를 입력에 넣으면 어떤 일이 생기나요?',
               ['정답을 알려 주는 누수라 점수가 높아도 쓸모없는 모델이 된다', '점수가 낮아진다', '글자라서 오류가 난다'], 0,
               '보트 번호는 사고 뒤에 적히는 정보라 사실상 정답입니다. 맞히는 시점에 알 수 없는 열은 입력에서 뺍니다.'),
        short('입력 `X`와 정답 `y`의 관계를 찾는 과정, 코드로는 `model.____(X_train, y_train)`을 무엇이라고 하나요?', ['fit', '학습', 'fit()'],
              '`fit`이 학습입니다. 찾은 규칙을 새 행에 적용하는 것은 `predict`입니다.'),
        choice("`sex` 열을 One-hot으로 바꾸면 열이 몇 개 생기나요?",
               ['값의 종류 수만큼. female, male이니 2개', '항상 1개', '승객 수만큼'], 0,
               '값마다 "해당하면 1" 열이 하나씩 생깁니다. 탑승 항구처럼 값이 셋이면 열도 셋입니다.'),
        choice('승객 이름(`name`) 열을 입력에서 빼는 이유는 무엇인가요?',
               ['사람마다 거의 다 달라서 규칙을 찾을 재료가 못 된다', '누수라서', '글자는 절대 쓸 수 없어서'], 0,
               '누수는 아니지만 1,309개가 거의 전부 다른 값이면 공통 규칙이 나올 수 없습니다. 글자 열이라도 `sex`처럼 값이 몇 가지면 쓸 수 있습니다.'),
    ),
])
