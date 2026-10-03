"""1일차 · 7교시 — 실제 데이터와 Target"""
from kpc_course.dsl import *

UNIT = unit('titanic-structure', '1일차 · 7교시 — 실제 데이터와 Target', [
    concept('target', '우리가 맞히고 싶은 칸부터 정하기',
        body="""
        4교시 끝에 잠깐 열어 봤던 `data/titanic.csv`로 돌아갑니다. 1912년 타이타닉호에 탔던 승객 1,309명의 기록입니다. 한 사람이 한 행이고, 열에는 객실 등급(`pclass`), 성별(`gender`), 나이(`age`), 함께 탄 형제·배우자 수(`sibsp`), 부모·자녀 수(`parch`), 요금(`fare`), 탑승 항구(`embarked`) 같은 정보가 있습니다. 그리고 `survived` 열이 있습니다. 0이면 사망, 1이면 생존입니다.

        내일 우리는 이 표로 "어떤 승객이 살아남았을까"를 맞히는 모델을 만듭니다. 그러려면 먼저 **무엇을 맞힐 것인지**를 정해야 합니다. 맞히려는 칸을 타깃(target)이라고 부릅니다. 여기서는 `survived`입니다. 타깃을 정하고 나면 나머지 열은 "맞히는 데 쓸 재료"가 됩니다.

        그런데 재료라고 다 쓸 수 있는 것은 아닙니다. `boat`(탄 구명보트 번호)와 `body`(시신 번호) 열을 보세요. 둘 다 **사고가 끝난 뒤에** 적힌 정보입니다. 구명보트 번호가 있으면 살아남은 것이고 시신 번호가 있으면 사망한 것이니, 이 열로 생존을 맞히는 것은 답안지를 보고 시험을 치는 것과 같습니다. 재료는 "맞히려는 시점에 알 수 있는 것"만 써야 합니다. 이 원칙은 내일도, 주가를 다루는 모레도 계속 나옵니다.

        ```python
        titanic = pd.read_csv('data/titanic.csv')
        titanic.shape                      # (행 수, 열 수)
        titanic['survived'].value_counts() # 0과 1이 각각 몇 명
        titanic['survived'].mean()         # 0과 1의 평균 = 1의 비율 = 생존율
        titanic.isna().sum()               # 열마다 빈 칸 개수
        ```

        타깃이 0과 1뿐이면 평균이 곧 비율입니다. 1이 세 명, 0이 일곱 명이면 평균은 0.3이고 생존율 30%입니다. 이번 시간의 미션은 이 표를 숫자로 더듬어 보는 것입니다. 몇 명인지, 몇 명이 살아남았는지, 어느 칸이 얼마나 비어 있는지. 특히 나이는 꽤 많이 비어 있는데, 5교시에서 배운 대로 빈 나이는 0살이 아니라 "모름"입니다.
        """,
        check=short('모델이 맞히려는 칸, 이 자료에서는 `survived` 열을 가리키는 영어 용어는 무엇인가요?', ['target', '타깃', '타겟', '목표 변수', '목표변수'],
                    '타깃(target)은 맞히려는 정답 칸입니다. 나머지 열 중 "맞히는 시점에 알 수 있는 것"만 재료로 씁니다.')),
    coding('titanic-shape', '자료의 크기와 열 이름',
        goal="""
        표의 뼈대부터 봅니다. `titanic`의 행 수를 `n_rows`, 열 수를 `n_columns`, 열 이름 리스트를 `columns`에 저장하고 출력하세요.

        1309행 14열이고 열 이름 중에 소문자 `survived`가 있으면 맞게 한 것입니다.
        """,
        hint="""
        4교시와 같습니다. `n_rows, n_columns = titanic.shape`, `columns = list(titanic.columns)`.
        """,
        starter=TI + "# n_rows, n_columns, columns를 만들고 출력하세요\n",
        solution=TI + "n_rows, n_columns = titanic.shape\ncolumns = list(titanic.columns)\nprint(n_rows, n_columns)\nprint(columns)\n",
        check="assert s['n_rows']==1309 and s['n_columns']==14\nassert 'survived' in list(s['columns']) and 'age' in list(s['columns'])"),
    coding('survived-counts', '생존·사망 인원 세기',
        goal="""
        타깃 열을 셉니다. `titanic['survived'].value_counts()`를 `counts`에 저장하고, 사망(0) 인원을 `n_dead`, 생존(1) 인원을 `n_alive`에 정수로 담아 출력하세요.

        두 수를 더하면 전체 인원 1309가 되어야 합니다.
        """,
        hint="""
        `value_counts()`는 값마다 몇 번 나오는지 세어 줍니다. 결과에서 `counts[0]`이 0의 개수, `counts[1]`이 1의 개수입니다. `int()`로 감싸 정수로 저장하세요.
        """,
        starter=TI + "# counts, n_dead, n_alive를 만들고 출력하세요\n",
        solution=TI + "counts = titanic['survived'].value_counts()\nn_dead = int(counts[0])\nn_alive = int(counts[1])\nprint(counts)\nprint(n_dead, n_alive)\n",
        check="assert s['n_dead']==809 and s['n_alive']==500\nassert s['counts'].sum()==1309"),
    coding('missing-per-column', '열마다 빈 칸 세기',
        goal="""
        어느 열이 얼마나 비어 있는지 봅니다. `titanic.isna().sum()`을 `missing`에 저장하고, 나이의 결측 수를 `age_missing`, 요금의 결측 수를 `fare_missing`에 정수로 담아 출력하세요.

        나이가 꽤 많이 비어 있고 요금은 거의 안 비어 있을 것입니다. 타깃 `survived`는 하나도 비어 있지 않아야 합니다.
        """,
        hint="""
        `titanic.isna().sum()`은 열 이름으로 꺼내는 `Series`입니다. `missing['age']`처럼 꺼내 `int()`로 바꾸세요.
        """,
        starter=TI + "# missing, age_missing, fare_missing을 만들고 출력하세요\n",
        solution=TI + "missing = titanic.isna().sum()\nage_missing = int(missing['age'])\nfare_missing = int(missing['fare'])\nprint(missing)\nprint(age_missing, fare_missing)\n",
        check="assert s['age_missing']==263 and s['fare_missing']==1\nassert s['missing']['survived']==0"),
    coding('titanic-counts', '전체, 나이를 아는 사람, 모르는 사람',
        goal="""
        "평균 나이"를 말하려면 몇 명으로 나눈 평균인지부터 알아야 합니다. 전체 인원을 `n_total`, 나이가 기록된 인원을 `n_known`, 나이가 비어 있는 인원을 `n_unknown`에 저장하세요. 그리고 `survived`의 평균을 `survival_rate`에 저장해 전부 출력하세요.

        `n_known + n_unknown`이 `n_total`과 같아야 합니다. 생존율은 0.38 근처가 나옵니다.
        """,
        hint="""
        전체는 `len(titanic)`, 나이가 있는 사람은 `titanic['age'].notna().sum()`, 없는 사람은 `titanic['age'].isna().sum()`입니다. 생존율은 `titanic['survived'].mean()`이고 `f'{survival_rate:.2%}'`로 출력하면 퍼센트로 보입니다.
        """,
        starter=TI + "# 인원과 생존율을 계산하세요\n",
        solution=TI + "n_total=len(titanic)\nn_known=int(titanic['age'].notna().sum())\nn_unknown=int(titanic['age'].isna().sum())\nsurvival_rate=titanic['survived'].mean()\nprint(n_total,n_known,n_unknown)\nprint(f'{survival_rate:.2%}')\n",
        check="assert (s['n_total'],s['n_known'],s['n_unknown'])==(1309,1046,263)\nassert abs(s['survival_rate']-500/1309)<1e-10"),
    quiz('target-check', '7교시 점검',
        short('이 자료는 몇 명(몇 행)의 기록인가요?', ['1309', '1,309', '1309명'],
              '`titanic.shape`의 첫 값이 1309입니다. 모든 비율은 이 분모를 기준으로 읽습니다.'),
        choice("`survived`의 평균이 0.38이라는 것은 무슨 뜻인가요?",
               ['전체의 38%가 생존(1)했다', '평균 생존 연령이 38세다', '38명이 생존했다'], 0,
               '0과 1만 있는 열의 평균은 1의 비율입니다. 1309명 중 38%, 약 500명이 살아남았다는 뜻입니다.'),
        choice('나이 칸이 비어 있는 승객을 어떻게 봐야 하나요?',
               ['나이를 모르는 사람', '0살인 아기', '기록 오류라서 지워야 하는 행'], 0,
               '빈 칸은 "모른다"입니다. 0살로 보면 평균 나이가 틀어지고, 지울지 채울지는 분석 목적에 따라 따로 정합니다.'),
        choice('`boat`(구명보트 번호) 열을 생존을 맞히는 재료로 쓰면 안 되는 이유는 무엇인가요?',
               ['사고가 끝난 뒤에 적힌 정보라 맞히려는 시점에는 알 수 없다', '글자라서 계산이 안 된다', '빈 칸이 많아서'], 0,
               '보트 번호가 있다는 것은 이미 살아남았다는 뜻입니다. 답을 보고 답을 맞히는 셈이라 모델의 실력을 알 수 없게 됩니다.'),
        short('열마다 빈 칸의 개수를 세는 코드는 `titanic.______().sum()`입니다. 빈칸은?', ['isna', 'isnull', 'isna()', 'isnull()'],
              '`isna()`가 빈 칸을 `True`로 표시하고 `.sum()`이 열마다 그 개수를 셉니다.'),
        choice("`titanic['survived'].value_counts()`는 무엇을 보여 주나요?",
               ['0인 사람과 1인 사람이 각각 몇 명인지', '생존율', '생존자의 평균 나이'], 0,
               '`value_counts()`는 값별 개수입니다. 비율이 필요하면 `.mean()`을 쓰거나 개수를 전체로 나눕니다.'),
    ),
])
