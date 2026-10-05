"""해설 모드 scripts for chapter 3 (eda): what the tutor says and types for each concept and
coding problem of 두 단원(실제 자료와 타깃, 그룹별 생존율), plus the chapter's
challenge. Keyed by activity id. Format and rules: narration.py.

Voice: the instructor's (see .scratch/presenter-decks/spec.md): 해요체 구어, "자," opens a scene,
one or two short sentences per line, says what the student should look at right now.
"""

NARRATION = {
    # ---- 실제 자료와 타깃 ----
    "target": [
        ("title", "자, 이 단원은 진짜 자료예요. 열이 열넷인데 뭐부터 볼지, 그걸 정해요."),
        ("앞 단원 끝에 잠깐 열어 봤던", "앞 단원에 잠깐 열어 본 타이타닉 표로 돌아가요. 승객 1309명, 한 사람이 한 행이에요. 객실등급, 성별, 나이, 요금 같은 열이 있고, 생존 열은 0이면 사망, 1이면 생존이에요."),
        ("제목: 먼저 정할 것", "만화를 보세요. 열이 많을 땐 맞히고 싶은 칸부터 정해요. 그 칸을 타깃이라고 불러요."),
        ("다음 챕터에서 이 표로", "다음 챕터에서 어떤 승객이 살아남았을까를 맞히는 모델을 만들어요. 그러니 타깃은 생존이고, 나머지 열은 맞히는 데 쓸 재료예요."),
        ("그런데 재료라고 다 쓸 수 있는 건 아니에요", "그런데 재료라고 다 쓰면 안 돼요. 구명보트 번호와 시신번호는 사고가 끝난 뒤에 적힌 거거든요. 그걸로 생존을 맞히면 답안지 보고 시험 치는 거예요. 맞히는 시점에 알 수 있는 것만 써요."),
        ("titanic['생존'].mean()", "코드 네 줄을 보세요. shape는 행과 열 수, value_counts는 0과 1이 몇 명씩인지, mean은 생존율, isna().sum()은 열마다 빈 칸 개수예요."),
        ("타깃이 0과 1뿐이면 평균이 곧 비율이에요", "0과 1만 있는 열은 평균이 곧 비율이에요. 1이 셋, 0이 일곱이면 평균 0.3, 생존율 30%죠. 그리고 빈 나이는 0살이 아니라 모름이에요. 앞 단원에서 봤죠?"),
        ("check", "확인 문항이요. 모델이 맞히려는 칸, 여기서는 생존 열을 부르는 영어 용어예요. 만화에 나왔어요."),
    ],
    "titanic-shape": [
        ("problem", "자, 표의 뼈대부터 봐요. 행 수를 n_rows, 열 수를 n_columns, 열 이름 리스트를 columns에 담아서 출력하면 돼요. 앞 단원에 한 것과 같아요."),
        ("starter", "준비 코드가 pandas를 불러오고 titanic.csv를 읽어 뒀어요. 그대로 두고 아래에 이어 써요."),
        ("code", "n_rows, n_columns = titanic.shape\ncolumns = list(titanic.columns)\n", "shape는 행 수와 열 수 두 개를 주니까 두 이름에 나눠 담아요. titanic.columns는 열 이름 묶음이고, list로 감싸면 리스트가 돼요."),
        ("code", "print(n_rows, n_columns)\nprint(columns)\n", "숫자 둘을 한 줄에, 열 이름 리스트를 다음 줄에 출력해요."),
        ("output", "1309 14가 나왔죠? 1309명, 열 14개예요. 아래 리스트에 생존, 나이가 보이고, 구명보트와 시신번호도 있어요. 이 둘은 아까 말한 답안지예요."),
        ("submit", "제출할게요. 검사는 1309, 14와 열 이름에 생존이 있는지를 봐요."),
    ],
    "survived-counts": [
        ("problem", "자, 타깃 열을 세요. 생존 열의 value_counts()를 counts에 담고, 사망 0 인원을 n_dead, 생존 1 인원을 n_alive에 정수로 담아 출력해요. 둘을 더하면 1309가 되어야 해요."),
        ("starter", "준비 코드는 그대로 둘게요. titanic이 이미 읽혀 있어요."),
        ("code", "counts = titanic['생존'].value_counts()\n", "생존 열을 꺼내서 value_counts()를 붙여요. 값마다 몇 번 나오는지 세 주거든요. 여기선 0과 1 두 줄이에요."),
        ("code", "n_dead = int(counts[0])\nn_alive = int(counts[1])\n", "counts[0]이 0의 개수, counts[1]이 1의 개수예요. int로 감싸서 보통 정수로 만들어 둬요."),
        ("code", "print(counts)\nprint(n_dead, n_alive)\n", "표 자체와 두 숫자를 같이 출력해서 눈으로 맞춰 봐요."),
        ("output", "0이 809, 1이 500이에요. 더하면 1309, 전체 인원과 맞죠? 사망이 생존보다 훨씬 많아요."),
        ("submit", "제출할게요. 809와 500, 그리고 합이 1309인지 검사해요."),
    ],
    "missing-per-column": [
        ("problem", "자, 어느 열이 얼마나 비어 있는지 봐요. isna().sum()을 missing에 담고, 나이의 빈 칸 수를 age_missing, 요금의 빈 칸 수를 fare_missing에 정수로 담아 출력해요."),
        ("starter", "준비 코드는 그대로 둬요."),
        ("code", "missing = titanic.isna().sum()\n", "isna()가 빈 칸을 True로 바꾸고, sum()이 열마다 True를 세요. 결과는 열 이름으로 꺼내는 Series예요."),
        ("code", "age_missing = int(missing['나이'])\nfare_missing = int(missing['요금'])\n", "missing에서 나이와 요금을 열 이름으로 꺼내요. int로 감싸서 정수로 담아요."),
        ("code", "print(missing)\nprint(age_missing, fare_missing)\n", "전체 표와 두 숫자를 출력해요."),
        ("output", "나이가 263, 요금은 1이에요. 생존은 0이죠? 타깃은 하나도 안 비었어요. 선실 1014, 시신번호 1188처럼 거의 다 빈 열도 있어요."),
        ("submit", "제출할게요. 263과 1, 그리고 생존이 0인지를 봐요."),
    ],
    "titanic-counts": [
        ("problem", "자, 평균 나이를 말하려면 몇 명으로 나눈 평균인지부터 알아야 해요. 전체 n_total, 나이를 아는 사람 n_known, 모르는 사람 n_unknown, 그리고 생존율 survival_rate를 구해 출력해요."),
        ("starter", "준비 코드는 그대로 두고 아래에 써요."),
        ("code", "n_total=len(titanic)\n", "전체 인원은 len(titanic)이에요. 행 수죠."),
        ("code", "n_known=int(titanic['나이'].notna().sum())\nn_unknown=int(titanic['나이'].isna().sum())\n", "notna()는 값이 있는 칸이 True, isna()는 빈 칸이 True예요. 각각 sum()으로 세고 int로 감싸요. 둘을 더하면 전체가 되어야 해요."),
        ("code", "survival_rate=titanic['생존'].mean()\n", "생존 열의 mean()이 생존율이에요. 0과 1의 평균이 1의 비율이거든요."),
        ("code", "print(n_total,n_known,n_unknown)\nprint(f'{survival_rate:.2%}')\n", "인원 셋을 한 줄에 찍고, 생존율은 f 문자열에 .2%를 붙여 퍼센트로 보여요."),
        ("output", "1309 1046 263, 그리고 38.20%예요. 1046 더하기 263이 1309죠? 평균 나이는 1309명이 아니라 1046명의 평균이라는 뜻이에요."),
        ("submit", "제출할게요. 인원 셋과 생존율 500 나누기 1309를 검사해요."),
    ],

    # ---- 그룹별 생존율 ----
    "denominator": [
        ("title", "자, 비율을 말할 때마다 몇 명 중을 붙이는 습관, 이 단원 주제예요."),
        ("앞 단원에서 전체 생존율을 구했죠", "앞 단원에 전체 생존율 38%를 구했죠? 그런데 그 숫자 하나로는 여성과 남성이 달랐나, 1등실과 3등실은, 이런 질문에 답을 못 해요. 표를 그룹으로 나눠야 하고, 그 도구가 groupby예요."),
        ("제목: 몇 명 중에?", "만화를 보세요. 여성 생존율이 높아요, 하면 강사가 몇 명 중 몇 명이냐고 묻죠. 3명 중 2명도 67%거든요."),
        ("titanic.groupby('성별')['생존'].agg(['count', 'sum', 'mean'])", "코드 두 줄이에요. 첫 줄은 성별로 묶고 생존의 평균을 그룹마다 구해요. 둘째 줄의 agg는 집계를 여러 개 한 번에 달라는 거예요."),
        ("첫 줄은 \"성별로 묶은 뒤", "count는 그룹 인원, sum은 생존자 수, mean은 생존율이에요. 1의 합이 생존자 수라는 게 포인트죠. 이 셋을 같이 보는 습관이 중요해요."),
        ("비율은 분모를 숨기거든요", "비율은 분모를 숨겨요. 그래서 count가 분모 역할이에요. 다만 count는 빈 칸을 빼고 세니까, 나이처럼 빈 칸 많은 열의 count는 그룹 인원이 아니에요. 인원은 빈 칸 없는 생존 열로 세요."),
        ("제목: 생존율 100%의 정체", "두 번째 만화요. 생존율 100%가 알고 보니 1명 중 1명이에요. 그래서 비율 옆에 인원을 꼭 적어요."),
        ("마지막으로 해석의 선을 하나 긋고 가요", "마지막으로 선 하나 긋고 가요. 여성 생존율이 높다는 표는 이 자료에서 그렇게 관찰됐다는 거예요. 여성이라서 살았다는 원인 설명이 아니에요. 1등실 비율이나 구조 순서 같은 다른 요인이 있을 수 있거든요."),
        ("check", "확인 문항이요. 그룹별 생존율을 보고할 때 비율 옆에 꼭 적어야 하는 것, 비율의 무엇이냐. 만화에서 두 번 나왔죠."),
    ],
    "sex-counts": [
        ("problem", "자, 비율 전에 분모부터 세요. 성별 열의 value_counts()를 gender_counts에 담아 출력하면 돼요. 이 숫자가 다음 미션의 분모예요."),
        ("starter", "준비 코드는 그대로 둘게요."),
        ("code", "gender_counts = titanic['성별'].value_counts()\nprint(gender_counts)\n", "앞 단원 value_counts와 같아요. 열만 성별로 바꿨어요. 바로 출력해요."),
        ("output", "남성 843, 여성 466이에요. 인원이 거의 두 배 차이죠? 이 둘이 다음 생존율의 분모예요."),
        ("submit", "제출할게요. 466과 843을 검사해요."),
    ],
    "sex-mean": [
        ("problem", "자, 첫 groupby예요. 성별로 묶은 생존의 mean()을 rates에 담아 출력해요. 바로 앞에서 센 인원과 함께 읽어요."),
        ("starter", "준비 코드는 그대로 둬요."),
        ("code", "rates = titanic.groupby('성별')['생존'].mean()\nprint(rates)\n", "groupby('성별')로 묶고, ['생존']으로 열을 고르고, mean()을 붙여요. 그룹마다 0과 1의 평균, 즉 생존율이 나와요."),
        ("output", "남성 0.19, 여성 0.73이에요. 여성 466명 중 73%, 남성 843명 중 19%. 차이가 크죠? 분모를 같이 말하는 거 잊지 마세요."),
        ("submit", "제출할게요. 여성 339 나누기 466, 남성 161 나누기 843을 검사해요."),
    ],
    "sex-summary": [
        ("problem", "자, 인원과 비율을 따로 구하지 말고 한 표로 봐요. 성별로 묶은 생존에 agg로 count, sum, mean을 한 번에 구해 gender_summary에 담고, 마지막 줄에 이름만 적어요."),
        ("starter", "준비 코드는 그대로 둘게요."),
        ("code", "gender_summary=titanic.groupby('성별')['생존'].agg(['count','sum','mean'])\n", "mean() 자리에 agg를 쓰고 리스트로 count, sum, mean 셋을 넘겨요. 인원, 생존자 수, 생존율이 열 세 개로 나와요."),
        ("code", "gender_summary\n", "마지막 줄에 이름만 적으면 앱이 표로 보여 줘요."),
        ("output", "남성 843명 중 161명 19%, 여성 466명 중 339명 73%. count 합이 1309, sum 합이 500이죠? 이 표 한 장이 몇 명 중 몇 명을 다 담아요."),
        ("submit", "제출할게요. 열 이름 셋과 인원, 생존자 합을 검사해요."),
    ],
    "pclass-summary": [
        ("problem", "자, 같은 질문을 객실 등급에 던져요. 객실등급으로 묶어서 count, sum, mean 표를 pclass_summary에 담아요. 등급이 내려갈수록 생존율이 어떻게 변하는지 보는 거예요."),
        ("starter", "준비 코드는 그대로 둬요."),
        ("code", "pclass_summary = titanic.groupby('객실등급')['생존'].agg(['count','sum','mean'])\n", "앞 미션 코드에서 묶는 열만 성별에서 객실등급으로 바꿨어요. 나머지는 그대로예요."),
        ("code", "pclass_summary\n", "마지막 줄에 이름을 적어 표로 봐요."),
        ("output", "1등실 323명 중 62%, 2등실 277명 중 43%, 3등실 709명 중 26%예요. 등급이 내려갈수록 생존율이 떨어지죠? 3등실이 인원은 제일 많아요."),
        ("submit", "제출할게요. 등급 1, 2, 3과 count 합 1309, 1등실 323을 검사해요."),
    ],
    "age-groups": [
        ("problem", "자, 나이는 값이 수십 가지라 그대로 묶으면 그룹이 너무 많아요. pd.cut으로 네 구간으로 나눈 age_group 열을 만들고, 구간별 count, sum, mean을 age_summary에 담아요."),
        ("hint", "경계는 0, 20, 40, 60, 무한대고 right=False를 주면 왼쪽 경계를 포함해요. 20살은 20~39에 들어가요."),
        ("starter", "준비 코드는 그대로 둘게요."),
        ("code", "titanic['age_group']=pd.cut(titanic['나이'],bins=[0,20,40,60,float('inf')],labels=['0~19','20~39','40~59','60+'],right=False)\n", "pd.cut에 나이 열, 경계 bins, 이름표 labels, right=False를 줘요. 결과를 titanic의 새 열 age_group에 넣어요. 나이가 빈 사람은 구간도 비어요."),
        ("code", "age_summary=titanic.groupby('age_group',observed=True)['생존'].agg(['count','sum','mean'])\n", "이제 age_group으로 묶어요. observed=True는 아무도 없는 구간을 표에서 빼 달라는 옵션이에요. 집계는 아까와 같은 agg 셋이에요."),
        ("code", "age_summary\n", "마지막 줄에 이름을 적어 표로 봐요."),
        ("output", "0~19가 225명 중 47%, 20~39가 576명 중 39%, 40~59가 205명 중 41%, 60 이상은 40명 중 30%예요. count 합은 1046이에요. 나이 모르는 263명이 빠졌거든요."),
        ("submit", "제출할게요. count 합 1046, 빈 구간 263명, 20살이 20~39에 들어가는지를 검사해요."),
    ],

    # ---- 3장 도전 과제 ----
    "family-survival": [
        ("problem", "자, 도전 과제예요. 표에 없는 열을 직접 만들어 집계해요. 형제배우자와 부모자녀를 더해 가족동반 열을 만들고, 그걸로 count, sum, mean 표를, 그리고 등급과 가족동반으로 묶은 생존율을 3행 2열로 펼쳐요."),
        ("hint", "새 열은 두 열을 더한 값이 1 이상인지 비교한 True, False예요. 두 열로 묶기는 groupby에 리스트를 주고, 뒤에 unstack을 붙이면 펼쳐져요."),
        ("starter", "준비 코드는 그대로 둬요."),
        ("code", "titanic['가족동반'] = (titanic['형제배우자'] + titanic['부모자녀']) >= 1\n", "두 열을 더하고 1 이상인지 비교해요. 결과가 True, False 열이 되고, 그걸 titanic의 새 열 가족동반에 넣어요."),
        ("code", "family_summary = titanic.groupby('가족동반')['생존'].agg(['count', 'sum', 'mean'])\n", "앞 단원과 같은 표예요. 묶는 열만 방금 만든 가족동반이에요. 인원, 생존자, 생존율 셋을 같이 봐요."),
        ("code", "by_class = titanic.groupby(['객실등급', '가족동반'])['생존'].mean().unstack('가족동반')\n", "groupby에 열 두 개를 리스트로 주면 등급과 가족동반 조합마다 생존율이 나와요. unstack('가족동반')이 그걸 옆으로 펼쳐서 3행 2열 표로 만들어요."),
        ("code", "print(family_summary)\nby_class\n", "첫 표는 print로, 둘째 표는 마지막 줄에 이름만 적어 표로 봐요."),
        ("output", "혼자 탄 790명 중 30%, 가족과 탄 519명 중 50%예요. 아래 표를 보면 1등실은 51%와 72%, 2등실은 30%와 60%, 3등실은 23%와 30%. 모든 등급에서 가족과 탄 쪽이 높죠? 다만 이건 관찰이에요. 원인은 아직 몰라요."),
        ("submit", "제출할게요. 가족동반이 bool인지, count 합 1309, by_class가 3행 2열인지를 검사해요."),
    ],
}
