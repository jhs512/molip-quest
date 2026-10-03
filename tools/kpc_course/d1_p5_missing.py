"""1일차 · 5교시 — 조건 필터와 결측치"""
from kpc_course.dsl import *

UNIT = unit('missing', '1일차 · 5교시 — 조건 필터와 결측치', [
    concept('missing-values', '빈칸은 0이 아니다',
        body="""
        4교시의 `orders` 표에는 가격이 비어 있는 거래가 한 건 있었습니다. 설문지를 떠올려 보세요. 어떤 사람이 나이 칸을 비워 두었다면 그 사람의 나이는 0살일까요? 아닙니다. **모른다**가 정답입니다. 표에서 비어 있는 칸을 결측(missing)이라고 부르고, `pandas`는 그 자리에 `NaN`이라고 표시합니다. 결측과 0을 혼동하면 평균이 엉뚱하게 낮아지고, 그 평균으로 한 모든 계산이 같이 틀어집니다.

        ```comic-gen
        제목: 빈칸은 0이 아니다
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
              - {화자: 준호, 상대: 강사, 내용: "나이 칸이 비었으면 0으로 채울까요?"}
              - {화자: 강사, 상대: 준호, 내용: "그러면 0살 고객이 생깁니다."}
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 어리둥절}, {식별자: 강사, 손모양: 가리키는손}]
            대사:
              - {화자: 준호, 상대: 강사, 내용: "평균 나이가 확 내려가겠네요."}
              - 화자: 강사
                상대: 준호
                내용: |-
                  빈칸은 '모른다'로 두고
                  먼저 몇 개인지 세어 보죠.
        ```

        그러니 분석을 시작하기 전에 어디가 얼마나 비어 있는지부터 셉니다. `isna()`는 빈 칸을 `True`로 표시한 표를 돌려주고, 거기에 `.sum()`을 붙이면 열마다 `True`의 개수, 즉 결측 개수가 나옵니다.

        ```python
        orders.isna().sum()                       # 열마다 빈 칸 개수
        filled = orders['price'].fillna(12000)    # 빈 칸을 12000으로 채운 새 열
        dropped = orders.dropna(subset=['price']) # 가격이 빈 행을 뺀 새 표
        ```

        비어 있는 칸을 다루는 길은 두 가지뿐입니다. 어떤 값으로 **채우거나**(`fillna`), 그 행을 **빼거나**(`dropna`). 무엇을 채울지는 사람이 정합니다. 흔한 선택은 그 열의 중앙값(값들을 크기순으로 세웠을 때 한가운데 값)입니다. 어느 쪽이 옳은지는 상황마다 다르고, 두 선택의 결과가 얼마나 달라지는지는 이번 시간 마지막 미션에서 직접 보게 됩니다. 한 가지 주의할 점은 `fillna`와 `dropna`가 **새 표를 돌려줄 뿐 원본은 그대로**라는 것입니다. 바꾼 결과를 쓰려면 변수에 받아 두어야 합니다.

        조건으로 행을 고르는 일도 한 단계 늘어납니다. 4교시에는 조건이 하나였지만, "가격이 12000 이상**이고** 수량이 2 이상"처럼 둘을 합칠 때는 각 조건을 괄호로 감싸고 `&`(그리고)로 잇습니다. "제품이 A**이거나** 수량이 1"은 `|`(또는)입니다. 괄호를 빼면 Python이 계산 순서를 다르게 읽어 오류가 납니다.

        ```python
        both = orders.loc[(orders['price'] >= 12000) & (orders['quantity'] >= 2)]
        either = orders.loc[(orders['product'] == 'A') | (orders['quantity'] == 1)]
        ```
        """,
        check=short('표에서 값이 비어 있는 칸을 가리키는 말은 무엇인가요?', ['결측', '결측치', '결측값', 'missing', 'missing value', 'NaN'],
                    '비어 있는 칸은 결측(missing)이며 `pandas`는 `NaN`으로 표시합니다. 0은 "값이 0"이라는 정보이고, 결측은 "모른다"는 뜻이라 서로 다릅니다.')),
    coding('count-missing', '비어 있는 값 세기',
        goal="""
        `orders`에서 열마다 빈 칸이 몇 개인지 `orders.isna().sum()`으로 구해 `missing_counts`에 저장하세요. 그중 `price` 열의 결측 개수를 정수로 `n_missing_price`에 담아 출력하세요.

        가격 열에만 1개가 비어 있으면 맞게 센 것입니다.
        """,
        hint="""
        `orders.isna()`는 빈 칸을 `True`로 표시하고, `.sum()`은 열마다 `True`를 셉니다. 결과는 열 이름으로 꺼내는 `Series`라서 `missing_counts['price']`로 가격 열 값을 꺼내고 `int()`로 감싸세요.
        """,
        starter=ORDERS + "# missing_counts, n_missing_price를 만들고 출력하세요\n",
        solution=ORDERS + "missing_counts = orders.isna().sum()\nn_missing_price = int(missing_counts['price'])\nprint(missing_counts)\nprint(n_missing_price)\n",
        check="assert s['missing_counts']['price']==1 and s['missing_counts']['product']==0\nassert s['n_missing_price']==1"),
    coding('fill-median', '결측을 중앙값으로 채우기',
        goal="""
        첫 번째 길, 채우기입니다. `orders['price']`의 중앙값을 `median_price`에 저장하고, 빈 칸을 그 값으로 채운 열을 `filled_price`에 저장해 둘 다 출력하세요. 원본 `orders`는 건드리지 않습니다.

        중앙값이 12000이고 채운 열이 10000, 20000, 12000, 12000이면 맞게 한 것입니다.
        """,
        hint="""
        `orders['price'].median()`은 빈 칸을 빼고 중앙값을 구합니다. `orders['price'].fillna(median_price)`는 빈 칸만 그 값으로 바꾼 **새** 열을 돌려주고 원본은 그대로 둡니다. 그래서 변수에 받아야 합니다.
        """,
        starter=ORDERS + "# median_price, filled_price를 만들고 출력하세요\n",
        solution=ORDERS + "median_price = orders['price'].median()\nfilled_price = orders['price'].fillna(median_price)\nprint(median_price)\nprint(filled_price)\n",
        check="assert s['median_price']==12000\nassert s['filled_price'].tolist()==[10000,20000,12000,12000]\nassert s['orders']['price'].isna().sum()==1"),
    coding('drop-missing', '결측 행 제외하기',
        goal="""
        두 번째 길, 빼기입니다. 가격이 비어 있는 행을 제외한 표를 `dropped`에 저장하고, 남은 행 수를 `n_left`에 담아 출력하세요. 마지막 줄에 `dropped`를 적어 표도 확인하세요.

        3행이 남으면 맞게 한 것입니다.
        """,
        hint="""
        `orders.dropna(subset=['price'])`는 `price`가 빈 행만 뺍니다. `subset`을 빼고 `orders.dropna()`라고 쓰면 어느 열이든 빈 행을 전부 빼는데, 이 표에서는 결과가 같지만 열이 많은 표에서는 크게 달라집니다.
        """,
        starter=ORDERS + "# dropped, n_left를 만들고 출력하세요\n",
        solution=ORDERS + "dropped = orders.dropna(subset=['price'])\nn_left = len(dropped)\nprint(n_left)\ndropped\n",
        check="assert len(s['dropped'])==3 and s['n_left']==3\nassert s['dropped']['product'].tolist()==['A','B','A']"),
    coding('filter-orders', '두 조건을 모두 만족하는 거래',
        goal="""
        가격이 12000 이상**이고** 수량도 2 이상인 거래만 골라 `selected`에 저장하세요. 열은 `product`, `price`, `quantity` 세 개를 유지하고, 뒤에서 수정해도 원본이 안 바뀌도록 `.copy()`를 붙입니다.

        제품 B(수량 2)와 A(수량 4) 두 건이 남으면 맞게 한 것입니다. 가격이 빈 C는 비교 자체가 안 되어 빠집니다.
        """,
        hint="""
        각 조건을 괄호로 감싸고 `&`로 이으세요. `orders.loc[조건, ['product', 'price', 'quantity']].copy()`처럼 `loc`의 쉼표 뒤에 열 이름 리스트를 넣으면 행과 열을 한 번에 고릅니다.
        """,
        starter=ORDERS + "# selected를 만드세요\n",
        solution=ORDERS + "selected=orders.loc[(orders['price']>=12000)&(orders['quantity']>=2),['product','price','quantity']].copy()\nselected\n",
        check="assert s['selected']['product'].tolist()==['B','A'] and s['selected']['quantity'].tolist()==[2,4]"),
    coding('or-filter', '둘 중 하나만 만족해도 고르기',
        goal="""
        이번에는 "또는"입니다. 제품이 A**이거나** 수량이 1인 거래를 `either`에 저장하고 마지막 줄에 `either`를 적어 확인하세요.

        A, A, C 세 건이 남으면 맞게 한 것입니다.
        """,
        hint="""
        `&`가 "그리고", `|`가 "또는"입니다. `(orders['product'] == 'A') | (orders['quantity'] == 1)`처럼 조건마다 괄호를 꼭 치세요. 괄호가 없으면 Python이 `'A' | orders['quantity']`를 먼저 계산하려다 오류를 냅니다.
        """,
        starter=ORDERS + "# either를 만들고 표를 표시하세요\n",
        solution=ORDERS + "either = orders.loc[(orders['product'] == 'A') | (orders['quantity'] == 1)]\neither\n",
        check="assert s['either']['product'].tolist()==['A','A','C']"),
    coding('missing-totals', '채우기와 빼기, 합계는 얼마나 달라질까',
        goal="""
        두 길의 결과를 나란히 놓고 비교합니다. `filled`는 가격 결측을 중앙값으로 채운 표, `dropped`는 가격이 빈 행을 뺀 표입니다. 각 표에 가격 × 수량 열 `amount`를 만들고, 합계를 `filled_total`과 `dropped_total`에 저장해 둘 다 출력하세요.

        두 합계가 서로 다르게 나옵니다. 어느 쪽도 "진짜 전체 금액"은 아닙니다. 빈 칸 하나를 어떻게 다루기로 했는지에 따라 답이 달라진다는 것, 그래서 보고서에는 그 선택을 적어야 한다는 것이 이 미션의 요점입니다.
        """,
        hint="""
        `filled = orders.copy()`를 만든 뒤 `filled['price'] = filled['price'].fillna(filled['price'].median())`로 채우고, `dropped = orders.dropna(subset=['price']).copy()`로 뺀 표를 만드세요. 두 표 각각 `['amount'] = ['price'] * ['quantity']`를 만들고 `['amount'].sum()`으로 합계를 구합니다.
        """,
        starter=ORDERS + "# 두 처리 방법과 합계를 비교하세요\n",
        solution=ORDERS + "filled=orders.copy()\nfilled['price']=filled['price'].fillna(filled['price'].median())\nfilled['amount']=filled['price']*filled['quantity']\ndropped=orders.dropna(subset=['price']).copy()\ndropped['amount']=dropped['price']*dropped['quantity']\nfilled_total=filled['amount'].sum()\ndropped_total=dropped['amount'].sum()\nprint(filled_total,dropped_total)\nfilled\n",
        check="assert s['filled_total']==130000 and s['dropped_total']==118000\nassert len(s['filled'])==4 and len(s['dropped'])==3"),
    quiz('missing-check', '5교시 점검',
        choice('가격이 비어 있는 칸을 0으로 채우면 무슨 일이 생기나요?',
               ['"모른다"는 정보가 "공짜였다"로 바뀌어 평균이 내려간다', '빈 칸이 사라져 더 정확해진다', '아무 영향이 없다'], 0,
               '결측은 모른다는 뜻이고 0은 실제 값입니다. 0으로 채우면 없던 공짜 거래가 생긴 셈이라 평균과 합계가 왜곡됩니다.'),
        short('두 조건을 **모두** 만족하는 행을 고를 때 조건 사이에 넣는 기호는 무엇인가요?', ['&'],
              '`&`가 "그리고"입니다. 조건마다 괄호로 감싸고 `&`로 잇습니다.'),
        short('두 조건 중 **하나만** 만족해도 고를 때 넣는 기호는 무엇인가요?', ['|'],
              '`|`가 "또는"입니다. 역시 조건마다 괄호가 필요합니다.'),
        choice("`orders['price'].fillna(0)`을 실행한 뒤 `orders`를 출력하면 빈 칸이 채워져 있을까요?",
               ['아니요. 새 열을 돌려줄 뿐 원본은 그대로다', '네. 원본이 바로 바뀐다', '첫 번째 빈 칸만 바뀐다'], 0,
               "`fillna`는 결과를 돌려주기만 합니다. 원본을 바꾸려면 `orders['price'] = orders['price'].fillna(0)`처럼 다시 저장해야 합니다."),
        choice("`orders.dropna()`와 `orders.dropna(subset=['price'])`의 차이는 무엇인가요?",
               ['앞은 어느 열이든 빈 행을 다 빼고, 뒤는 가격이 빈 행만 뺀다', '둘은 항상 같다', '앞은 열을 빼고 뒤는 행을 뺀다'], 0,
               '`subset`으로 기준 열을 정하지 않으면 모든 열을 검사합니다. 열이 많은 표에서는 생각보다 많은 행이 사라질 수 있습니다.'),
        choice("`orders.loc[orders['price'] >= 12000 & orders['quantity'] >= 2]`처럼 괄호를 빼면 어떻게 되나요?",
               ['계산 순서가 달라져 오류가 난다', '괄호가 있을 때와 같다', '첫 조건만 적용된다'], 0,
               'Python은 `&`를 `>=`보다 먼저 계산하려고 해서 `12000 & orders[\'quantity\']`부터 시도하다 오류를 냅니다. 조건마다 괄호를 치세요.'),
    ),
])
