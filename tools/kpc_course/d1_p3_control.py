"""1일차 · 3교시 — 조건·반복과 DataFrame"""
from kpc_course.dsl import *

HOLDINGS = "holdings = [{'name':'A','price':10000,'quantity':3},{'name':'B','price':20000,'quantity':2},{'name':'C','price':15000,'quantity':4}]\n"
HOLDINGS_WITH_AMOUNT = "holdings = [{'name':'A','price':10000,'quantity':3,'amount':30000},{'name':'B','price':20000,'quantity':2,'amount':40000},{'name':'C','price':15000,'quantity':4,'amount':60000}]\n"

UNIT = unit('control', '1일차 · 3교시 — 조건·반복과 DataFrame', [
    concept('flow', '조건에 따라 고르고, 여러 값에 같은 일을 반복하기',
        body="""
        지금까지의 코드는 위에서 아래로 한 번 흘러가면 끝이었습니다. 그런데 "가격이 만 원 이상일 때만 알려 줘"처럼 **경우에 따라 다르게** 하고 싶을 때가 있고, "사흘치 가격을 하나씩 다 더해 줘"처럼 **같은 일을 여러 번** 하고 싶을 때가 있습니다. 전자가 `if`, 후자가 `for`입니다.

        ```python
        price = 10200
        if price >= 10000:
            print('기준 이상')
        else:
            print('기준 미만')
        ```

        `if` 뒤에 조건을 쓰고 콜론 `:`을 찍은 다음, **그 조건이 참일 때 할 일을 공백 네 칸 들여서** 적습니다. 들여쓰기가 "이 줄은 `if`에 속한다"는 표시이기 때문에, 들여쓰기를 빼면 Python이 `IndentationError`를 냅니다. 조건이 거짓일 때 할 일은 `else:` 아래에 적습니다. 비교 기호도 정확히 봐야 합니다. `>`는 초과(10000은 포함 안 됨), `>=`는 이상(10000도 포함)입니다.

        ```python
        prices = [10000, 10200, 9900, 10100]
        total = 0
        for price in prices:
            total += price
        print(total)
        ```

        `for price in prices:`는 "리스트의 값을 하나씩 꺼내 `price`라는 이름에 넣고, 아래 들여쓴 줄을 실행해라. 값이 떨어질 때까지"라는 뜻입니다. 네 값이 있으니 들여쓴 줄이 네 번 실행됩니다. `total += price`는 `total = total + price`를 짧게 쓴 것으로, 지금까지의 합에 이번 값을 더해 다시 저장합니다. 합계를 담을 `total = 0`은 반복이 시작되기 **전에** 한 번만 만들어야 합니다. 반복 안에서 만들면 매번 0으로 돌아가서 마지막 값만 남습니다.

        `for` 안에 `if`를 넣을 수도 있습니다. 그러면 `if`에 속한 줄은 공백 여덟 칸이 됩니다. 들여쓰기 깊이가 곧 "누구에게 속한 줄인가"를 나타냅니다.
        """,
        check=short("`if price >= 10000:` 아래에 속한 줄은 공백 몇 칸을 들여써야 하나요? 숫자로 답하세요.", ['4', '네', '네칸', '4칸'],
                    'Python은 공백 네 칸 들여쓰기로 "이 줄은 위 조건문에 속한다"를 표시합니다. 들여쓰기가 빠지면 오류, 깊이가 다르면 다른 줄에 속하게 됩니다.')),
    coding('simple-if', '조건에 따라 다른 문장 출력',
        goal="""
        실행 입력에 가격이 한 줄로 들어옵니다. 가격이 10000 **이상**이면 `기준 이상`, 아니면 `기준 미만`을 출력하세요.

        예: 입력 `10200` → `기준 이상`, 입력 `9900` → `기준 미만`. 10000을 넣으면 어느 쪽이 나와야 할지 생각해 보세요.
        """,
        hint="""
        `if price >= 10000:` 뒤에 콜론을 찍고, 다음 줄은 공백 네 칸 들여서 `print('기준 이상')`을 적습니다. 그 아래 `else:`와 들여쓴 `print('기준 미만')`을 같은 모양으로 씁니다. 10000도 "이상"에 포함되므로 `>`가 아니라 `>=`입니다.
        """,
        starter='price = int(input())\n# if와 else로 출력하세요\n',
        solution="price = int(input())\nif price >= 10000:\n    print('기준 이상')\nelse:\n    print('기준 미만')\n",
        tests=[io('10200\n', '기준 이상\n'), io('9900\n', '기준 미만\n'), io('10000\n', '기준 이상\n')]),
    coding('for-sum', '반복문으로 합계 누적하기',
        goal="""
        2교시에서는 `sum()`이 합계를 구해 줬습니다. 이번에는 그 일을 직접 합니다. `prices`의 값을 `for`로 하나씩 꺼내 `total`에 더한 뒤, 반복이 끝나면 `total`을 출력하세요.

        결과는 40200입니다. `sum()`을 쓰지 않고 누적하세요.
        """,
        hint="""
        `for price in prices:`라고 쓰면 `price`에 값이 하나씩 들어오면서 아래 들여쓴 줄이 반복됩니다. 그 안에서 `total += price`로 누적하세요. `print(total)`은 들여쓰기 없이 반복문 **밖**에 두어야 마지막에 한 번만 출력됩니다.
        """,
        starter='prices = [10000,10200,9900,10100]\ntotal = 0\n# for 반복문으로 total에 누적하세요\n',
        solution='prices = [10000,10200,9900,10100]\ntotal = 0\nfor price in prices:\n    total += price\nprint(total)\n',
        check="assert s['total']==40200"),
    coding('above-count', '반복하면서 조건으로 세기',
        goal="""
        합계를 구하면서, 동시에 기준 10000 이상인 날이 며칠인지도 세어 봅니다. 합계는 `total`, 기준 이상인 값의 개수는 `above_count`에 저장하세요.

        합계 40200, 개수 3이 나와야 합니다.
        """,
        hint="""
        `for price in prices:` 안에서 매번 `total += price`를 하고, 그 아래 `if price >= 10000:`일 때만 `above_count += 1`을 합니다. `if`에 속한 줄은 공백 여덟 칸입니다.
        """,
        starter='prices = [10000,10200,9900,10100]\ntotal = 0\nabove_count = 0\n# 반복문을 작성하세요\n',
        solution='prices = [10000,10200,9900,10100]\ntotal = 0\nabove_count = 0\nfor price in prices:\n    total += price\n    if price >= 10000:\n        above_count += 1\nprint(total, above_count)\n',
        check="assert s['total']==40200 and s['above_count']==3"),
    coding('max-price', '반복문으로 최댓값 찾기',
        goal="""
        가장 비쌌던 날의 가격을 찾습니다. `max()` 함수를 쓰면 한 줄이지만, 이번에는 반복문과 `if`로 직접 찾아 `highest`에 저장하세요. 첫 값을 일단 최고로 두고, 더 큰 값을 만날 때마다 바꾸는 방식입니다.

        결과는 10200입니다.
        """,
        hint="""
        준비 코드가 `highest`를 첫 값으로 시작해 둡니다. `for price in prices:` 안에서 `if price > highest:`일 때만 `highest = price`로 갈아 끼우세요. 반복이 끝나면 가장 큰 값이 남습니다.
        """,
        starter='prices = [10000,10200,9900,10100]\nhighest = prices[0]\n# 반복문과 if로 highest를 갱신하세요\n',
        solution='prices = [10000,10200,9900,10100]\nhighest = prices[0]\nfor price in prices:\n    if price > highest:\n        highest = price\nprint(highest)\n',
        check="assert s['highest']==10200"),
    coding('croissant-plan', '오늘 크루아상 몇 개 구울까',
        intro="""
        파리바게뜨 공장의 생산 담당자는 새벽마다 오늘 크루아상을 몇 개 구울지 정합니다. 너무 많이 구우면 저녁에 버리고, 너무 적게 구우면 오후에 품절입니다. 가장 단순한 방법은 최근 판매량의 평균에서 출발하는 것입니다. 이 공장은 "품절보다 폐기가 싸다"고 보고 평균보다 10% 많이 굽기로 정했습니다.
        """,
        goal="""
        지난 사흘 판매량 `sold`가 준비되어 있습니다. `for`로 합계를 `total`에 누적하고, 평균을 `average`에, 평균의 1.1배를 반올림한 정수를 `plan`에 저장한 뒤 `오늘 생산 계획: 460개` 형식으로 출력하세요.

        합계 1255, 평균 약 418.3, 계획 460이 나와야 합니다. `sum()`을 쓰지 말고 반복문으로 누적하세요.
        """,
        hint="""
        `for count in sold:` 안에서 `total += count`, 반복이 끝난 뒤 `average = total / len(sold)`. 반올림은 `round(average * 1.1)`이고 결과는 정수입니다. 출력은 f-문자열로 `print(f'오늘 생산 계획: {plan}개')`.
        """,
        starter='sold = [412, 388, 455]\ntotal = 0\n# total, average, plan을 만들고 출력하세요\n',
        solution="sold = [412, 388, 455]\ntotal = 0\nfor count in sold:\n    total += count\naverage = total / len(sold)\nplan = round(average * 1.1)\nprint(f'오늘 생산 계획: {plan}개')\n",
        check="assert s['total']==1255 and abs(s['average']-1255/3)<1e-9\nassert s['plan']==460 and isinstance(s['plan'],int)"),
    coding('holdings-amounts', '세 종목의 금액 계산하기',
        goal="""
        리스트 안의 값이 숫자가 아니라 딕셔너리여도 `for`는 똑같이 돕니다. 세 종목이 든 `holdings`를 돌면서 각 종목의 가격 × 수량을 그 종목의 `amount` 키에 저장하세요.

        세 종목의 금액이 30000, 40000, 60000이면 맞게 한 것입니다. 합계는 다음 미션에서 구합니다.
        """,
        hint="""
        `for holding in holdings:`라고 쓰면 `holding`에 종목 딕셔너리가 하나씩 들어옵니다. 그 안에서 `holding['amount'] = holding['price'] * holding['quantity']`로 새 키를 추가하세요. 반복이 끝난 뒤 `print(holdings)`로 세 종목을 확인합니다.
        """,
        starter=HOLDINGS + "# 각 종목에 amount를 추가하세요\n",
        solution=HOLDINGS + "for holding in holdings:\n    holding['amount'] = holding['price'] * holding['quantity']\nprint(holdings)\n",
        check="assert len(s['holdings'])==3\nassert [h['amount'] for h in s['holdings']]==[30000,40000,60000]"),
    coding('holdings-total', '세 종목의 금액 합산하기',
        goal="""
        준비 코드에는 각 종목의 금액이 이미 계산돼 있습니다. 세 종목의 `amount`를 모두 더해 `total_amount`에 저장하고 출력하세요.

        결과는 130000입니다.
        """,
        hint="""
        `for-sum` 미션과 같은 모양입니다. 반복 전에 `total_amount = 0`, 반복 안에서 `total_amount += holding['amount']`, 반복이 끝난 뒤 출력.
        """,
        starter=HOLDINGS_WITH_AMOUNT + "# total_amount를 계산하고 출력하세요\n",
        solution=HOLDINGS_WITH_AMOUNT + "total_amount = 0\nfor holding in holdings:\n    total_amount += holding['amount']\nprint(total_amount)\n",
        check="assert s['total_amount']==130000"),
    concept('first-dataframe', '딕셔너리 묶음은 사실 표였다',
        body="""
        방금 다룬 `holdings`를 종이에 적어 보면 이렇게 됩니다. 종목 하나가 한 줄, 이름·가격·수량·금액이 한 칸씩.

        | name | price | quantity | amount |
        | --- | ---: | ---: | ---: |
        | A | 10000 | 3 | 30000 |
        | B | 20000 | 2 | 40000 |
        | C | 15000 | 4 | 60000 |

        딕셔너리 하나는 표의 **한 행**이고, 딕셔너리를 모은 리스트는 **표 전체**입니다. 그런데 반복문으로 열 하나를 더하고, 조건에 맞는 행을 고르는 일을 매번 손으로 짜는 건 번거롭습니다. 그래서 표를 전문으로 다루는 도구 `pandas`를 씁니다. `pandas`가 다루는 표를 `DataFrame`이라고 부르고, 리스트에 든 딕셔너리들을 넘기면 바로 표가 됩니다.

        ```python
        import pandas as pd
        df = pd.DataFrame(holdings)
        print(df.shape)   # (3, 4) → 3행 4열
        df
        ```

        첫 줄 `import pandas as pd`는 "pandas를 가져와서 짧게 `pd`라고 부르겠다"는 선언이라서 표를 쓰는 모든 코드의 맨 위에 옵니다. `df.shape`는 (행 수, 열 수)입니다. 행 번호인 인덱스는 열 수에 들어가지 않습니다. 그리고 코드 **마지막 줄에 `df`만 적으면** 이 앱이 표를 그려서 보여 줍니다. `print(df)`도 되지만 글자로만 나오니 마지막 줄 방식을 쓰세요.

        한 열 전체를 더하는 일은 반복문 없이 `df['amount'].sum()` 한 줄입니다. 오늘 오전에 반복문으로 했던 일이 어떻게 한 줄로 줄어드는지 다음 두 미션에서 직접 봅니다.
        """,
        check=short("""
                    `pandas`에서 행과 열로 이루어진 표를 나타내는 자료구조의 이름은 무엇인가요? 변수 이름 `df`가 아니라 자료구조 이름을 답하세요.

                    ```python
                    import pandas as pd
                    df = pd.____(holdings)
                    ```
                    """, ['DataFrame', '데이터프레임'],
                    '`DataFrame`이 `pandas`의 표 자료구조입니다. `df`는 그 표를 담은 변수 이름일 뿐이고, `pd`는 `pandas`를 짧게 부르는 별칭입니다.')),
    coding('holdings-frame', '세 종목을 표로 보기',
        goal="""
        금액까지 들어 있는 `holdings`를 `DataFrame`으로 만들어 `df`에 저장하세요. 마지막 줄에 `df`를 적어 표를 띄워 보세요.

        3행 4열이고 열 이름이 `name`, `price`, `quantity`, `amount` 순이면 맞게 한 것입니다.
        """,
        hint="""
        `df = pd.DataFrame(holdings)` 한 줄이면 됩니다. 그다음 줄에 `df`만 적으세요. `print()`나 합계는 필요 없습니다.
        """,
        starter="import pandas as pd\n" + HOLDINGS_WITH_AMOUNT + "# df를 만들고 표를 표시하세요\n",
        solution="import pandas as pd\n" + HOLDINGS_WITH_AMOUNT + "df = pd.DataFrame(holdings)\ndf\n",
        check="assert s['df'].shape==(3,4)\nassert list(s['df'].columns)==['name','price','quantity','amount']\nassert s['df']['name'].tolist()==['A','B','C']\nassert s['df']['amount'].tolist()==[30000,40000,60000]"),
    coding('frame-column-sum', '표의 한 열을 합산하기',
        goal="""
        조금 전 반복문으로 구했던 전체 금액을 이번에는 표로 구합니다. `df`의 `amount` 열을 골라 `.sum()`으로 합계를 내서 `total_amount`에 저장하고 출력하세요.

        결과는 역시 130000입니다. 두 방법의 코드 길이를 비교해 보세요.
        """,
        hint="""
        `df['amount']`가 한 열이고, 뒤에 `.sum()`을 붙이면 그 열의 합계입니다. 반복문도 `total_amount = 0`도 필요 없습니다.
        """,
        starter="import pandas as pd\n" + HOLDINGS_WITH_AMOUNT + "df = pd.DataFrame(holdings)\n# total_amount를 계산하고 출력하세요\n",
        solution="import pandas as pd\n" + HOLDINGS_WITH_AMOUNT + "df = pd.DataFrame(holdings)\ntotal_amount = df['amount'].sum()\nprint(total_amount)\n",
        check="assert s['total_amount']==130000"),
    quiz('control-check', '3교시 점검',
        choice('`if price >= 10000:`에서 `price`가 정확히 10000이면 어떻게 되나요?',
               ['조건이 참이라 아래 줄이 실행된다', '조건이 거짓이라 건너뛴다', '같은 값은 오류가 난다'], 0,
               '`>=`는 "이상"이라 같은 값도 포함합니다. 같은 값을 빼고 싶을 때만 `>`를 씁니다.'),
        choice('`for price in prices:` 바로 아래 줄을 들여쓰지 않으면 어떻게 되나요?',
               ['`IndentationError`가 난다', '그 줄이 한 번만 실행된다', '그 줄이 무시된다'], 0,
               '반복할 줄은 반드시 들여써야 합니다. 들여쓰기가 없으면 Python은 "반복할 내용이 없다"고 보고 오류를 냅니다.'),
        choice('합계를 담을 `total = 0`은 어디에 두어야 하나요?',
               ['반복문이 시작되기 전에 한 번', '반복문 안에 매번', '반복문이 끝난 뒤'], 0,
               '반복 안에 두면 매번 0으로 돌아가 마지막 값만 남습니다. 반복 뒤에 두면 더한 결과를 0으로 덮어씁니다.'),
        short('`total = total + price`를 짧게 쓰는 연산자는 무엇인가요? (`total __ price`)', ['+=', '+ ='],
              '`+=`는 "지금 값에 더해서 다시 저장해라"입니다. 반복문 안에서 누적할 때 늘 씁니다.'),
        short('3행 4열 표의 `df.shape`는 무엇인가요?', ['(3,4)', '3,4', '(3, 4)'],
              '`shape`는 (행 수, 열 수) 순서입니다. 행 번호인 인덱스는 열 수에 들어가지 않습니다.'),
        choice('표를 앱 화면에 그려서 보려면 코드 마지막 줄에 무엇을 적나요?',
               ['`df`', "`print('df')`", '`df.sum()`'], 0,
               "마지막 줄에 `df`만 적으면 앱이 표로 그려 줍니다. `print('df')`는 글자 df를 출력할 뿐이고, `df.sum()`은 열마다 합계만 보여 줍니다."),
    ),
])
