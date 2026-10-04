"""1일차 · 2교시 — 변수와 자료구조"""
from kpc_course.dsl import *

HOLDINGS = "holdings = [{'name':'A','price':10000,'quantity':3},{'name':'B','price':20000,'quantity':2},{'name':'C','price':15000,'quantity':4}]\n"

UNIT = unit('structures', '1일차 · 2교시 — 변수와 자료구조', [
    concept('values', '값이 여러 개면 리스트, 이름표가 있으면 딕셔너리',
        body="""
        1교시에서는 값 하나에 이름 하나를 붙였습니다. 그런데 어떤 주식의 사흘치 가격을 다루려면 `price1`, `price2`, `price3`을 따로 만들어야 할까요? 백 일치라면요? 그래서 값 여러 개를 **한 줄로 세워 한 이름에** 담는 방법이 있습니다. 바로 리스트입니다.

        ```comic-gen
        제목: 값 백 개에 이름 백 개?
        등장인물:
          민지:
            그림: 사람
            이름표: 민지
            외형: {머리모양: 단발, 머리색: "#573d36", 옷: 후드, 옷색: "#609b87"}
          파이썬: {그림: 서버, 이름표: Python}
        컷:
          - 인물: [{식별자: 민지, 표정: 어리둥절}, 파이썬]
            대사:
              - {화자: 민지, 상대: 파이썬, 내용: "백 일치 가격이면 변수가 백 개야?"}
              - {화자: 파이썬, 상대: 민지, 내용: "값들을 한 줄로 세워서 이름 하나에 담아. 그게 리스트야."}
          - 구성: 이전
            인물: [{식별자: 민지, 표정: 보통}, {식별자: 파이썬, 손모양: 가리키는손}]
            대사:
              - {화자: 민지, 상대: 파이썬, 내용: "첫 값은 어떻게 꺼내?"}
              - 화자: 파이썬
                상대: 민지
                내용: |-
                  prices[0]. 자리는 0부터 세고
                  마지막은 prices[-1].
        ```

        ```python
        prices = [10000, 10200, 10100]
        print(prices[0])      # 첫 값 10000
        print(prices[-1])     # 마지막 값 10100
        print(len(prices))    # 개수 3
        print(sum(prices))    # 합계 30300
        prices.append(10300)  # 맨 뒤에 값 추가
        ```

        리스트의 자리는 **0부터** 셉니다. 첫 값이 `prices[0]`, 둘째가 `prices[1]`입니다. 뒤에서부터 세고 싶으면 음수를 씁니다. `prices[-1]`은 마지막 값입니다. 없는 자리를 부르면 Python은 `IndexError`라는 오류로 알려 줍니다. `len`은 몇 개인지, `sum`은 다 더하면 얼마인지를 돌려주고, `append`는 맨 뒤에 값을 하나 붙입니다.

        리스트는 "몇 번째"로 값을 찾습니다. 그런데 어떤 종목 하나를 설명하려면 이름, 가격, 수량처럼 **종류가 다른 값**이 한 묶음입니다. 이때는 자리 번호보다 "가격", "수량" 같은 이름표로 찾는 쪽이 자연스럽습니다. 그런 묶음이 딕셔너리입니다.

        ```python
        holding = {'name': '연습A', 'price': 10000, 'quantity': 3}
        print(holding['price'])     # 10000
        holding['quantity'] = 5     # 값 바꾸기
        holding['amount'] = 50000   # 새 이름표 추가
        ```

        딕셔너리는 중괄호 안에 `'이름표': 값` 쌍을 쉼표로 늘어놓습니다. 이름표를 **키**(key)라고 부르며 꺼낼 때는 `holding['price']`처럼 대괄호 안에 키를 따옴표째 적습니다. 키는 글자가 정확히 같아야 합니다. `'Price'`와 `'price'`는 다른 키라서 없는 키를 부르면 `KeyError`가 납니다. 리스트는 **위치**로, 딕셔너리는 **키**로 찾는다는 것만 기억하면 뒤가 편해집니다.
        """,
        check=short('값마다 이름표(키)를 붙여 두고 그 이름표로 값을 찾는 자료구조는 무엇인가요?', ['dict', 'dictionary', '딕셔너리', '사전'],
                    '딕셔너리(dict)는 키로 값을 찾습니다. 리스트는 0부터 세는 위치로 값을 찾습니다.')),
    coding('list-index', '리스트에서 위치로 값 꺼내기',
        goal="""
        사흘치 가격이 `prices` 리스트에 들어 있습니다. 첫날 가격을 `first`, 마지막 날 가격을 `last`에 저장하고 둘을 출력하세요.

        첫 값은 10000, 마지막 값은 10100이 나와야 합니다.
        """,
        hint="""
        리스트의 자리는 0부터 시작합니다. 첫 값은 `prices[0]`, 마지막 값은 `prices[-1]`입니다. `prices[3]`은 없는 자리라서 `IndexError`가 납니다.
        """,
        starter='prices = [10000, 10200, 10100]\n# first, last를 만들고 출력하세요\n',
        solution='prices = [10000, 10200, 10100]\nfirst = prices[0]\nlast = prices[-1]\nprint(first, last)\n',
        check="assert s['first']==10000 and s['last']==10100"),
    coding('list-len-sum', '개수와 합계 구하기',
        goal="""
        같은 리스트로 "며칠치인가"와 "다 더하면 얼마인가"를 구합니다. 개수를 `count`, 합계를 `total`에 저장하고 출력하세요.

        개수 3, 합계 30300이 나와야 합니다.
        """,
        hint="""
        `len(prices)`가 개수, `sum(prices)`가 합계입니다. 각각 변수에 담은 뒤 `print(count, total)`로 한 줄에 출력하세요.
        """,
        starter='prices = [10000, 10200, 10100]\n# count, total을 만들고 출력하세요\n',
        solution='prices = [10000, 10200, 10100]\ncount = len(prices)\ntotal = sum(prices)\nprint(count, total)\n',
        check="assert s['count']==3 and s['total']==30300"),
    coding('dict-read', '딕셔너리에서 키로 값 읽기',
        goal="""
        종목 하나가 `holding` 딕셔너리에 들어 있습니다. 가격과 수량을 키로 꺼내 곱한 금액을 `amount`에 저장하고 출력하세요. 딕셔너리 자체는 바꾸지 않습니다.

        결과는 30000입니다.
        """,
        hint="""
        값은 `holding['price']`처럼 대괄호 안에 키를 따옴표째 적어 꺼냅니다. 따옴표를 빼고 `holding[price]`라고 쓰면 Python은 `price`라는 변수를 찾다가 `NameError`를 냅니다.
        """,
        starter="holding = {'name':'연습A', 'price':10000, 'quantity':3}\n# amount를 계산하고 출력하세요\n",
        solution="holding = {'name':'연습A', 'price':10000, 'quantity':3}\namount = holding['price'] * holding['quantity']\nprint(amount)\n",
        check="assert s['amount']==30000"),
    coding('holdings-access', '리스트 안의 딕셔너리',
        goal="""
        이제 두 가지를 합칩니다. `holdings`는 종목 딕셔너리 세 개를 순서대로 담은 리스트입니다. 두 번째 종목의 이름을 `second_name`, 세 번째 종목의 가격을 `third_price`에 저장하고 출력하세요.

        각각 `B`, 15000이 나와야 합니다.
        """,
        hint="""
        두 단계입니다. 먼저 리스트에서 위치로 딕셔너리 하나를 꺼내고, 이어서 키로 값을 꺼냅니다. `holdings[1]['name']`처럼 대괄호를 두 번 붙이면 됩니다. 두 번째 종목의 위치는 1, 세 번째는 2입니다.
        """,
        starter=HOLDINGS + "# second_name, third_price를 만들고 출력하세요\n",
        solution=HOLDINGS + "second_name = holdings[1]['name']\nthird_price = holdings[2]['price']\nprint(second_name, third_price)\n",
        check="assert s['second_name']=='B' and s['third_price']==15000"),
    coding('holding', '값을 바꾸고 다시 계산하기',
        goal="""
        읽기만 했으니 이번에는 고쳐 봅니다. `holding`의 수량을 5로 바꾸고, 바뀐 수량으로 가격 × 수량을 계산해 `amount`라는 **새 키**에 저장하세요.

        `holding['amount']`가 50000이면 맞게 한 것입니다.
        """,
        hint="""
        `holding['quantity'] = 5`처럼 키에 새 값을 넣으면 바뀌고, 없던 키에 넣으면 추가됩니다. 수량을 바꾼 **다음에** 곱해야 50000이 나옵니다. 순서가 바뀌면 30000이 저장됩니다.
        """,
        starter="holding = {'name':'연습A', 'price':10000, 'quantity':3}\n# 수량을 수정하고 금액을 계산하세요\n",
        solution="holding = {'name':'연습A', 'price':10000, 'quantity':3}\nholding['quantity'] = 5\nholding['amount'] = holding['price'] * holding['quantity']\nprint(holding)\n",
        check="assert s['holding']['quantity']==5 and s['holding']['amount']==50000"),
    coding('price-average', '값을 추가하고 평균 내기',
        goal="""
        넷째 날 가격 10300이 들어왔습니다. `prices` 맨 뒤에 추가한 뒤 개수를 `count`, 평균을 `average`에 저장하고 둘 다 출력하세요.

        개수 4, 평균 10150이 나와야 합니다.
        """,
        hint="""
        1. `prices.append(10300)`으로 맨 뒤에 값을 붙입니다.
        2. 평균은 **합계 ÷ 개수**입니다. Python 기본 함수에 `average()`는 없으니 `sum(prices) / count`로 직접 계산하세요.
        3. 나눗셈 `/`의 결과는 소수가 될 수 있어서 10150.0으로 보여도 괜찮습니다.
        """,
        starter='prices = [10000, 10200, 10100]\n# 값을 추가하고 count, average를 계산하세요\n',
        solution='prices = [10000, 10200, 10100]\nprices.append(10300)\ncount = len(prices)\naverage = sum(prices)/count\nprint(count, average)\n',
        check="assert s['prices']==[10000,10200,10100,10300] and s['count']==4 and s['average']==10150"),
    quiz('structure-check', '2교시 점검',
        short('리스트에서 첫 번째 값의 자리 번호(인덱스)는 몇인가요?', ['0'],
              'Python의 자리 번호는 0부터 시작합니다. 세 값이 든 리스트의 마지막 자리는 2입니다.'),
        choice("""
               아래 코드를 위에서부터 실행했습니다. 마지막 줄 `print(amount)`는 무엇을 출력할까요?

               ```python
               price = 10000
               quantity = 3
               amount = price * quantity
               quantity = 5
               print(amount)
               ```
               """,
               ['`30000`. 계산한 순간의 값이 그대로 남아 있다', '`50000`. 수량이 바뀌면 금액도 따라 바뀐다', '오류. 수량을 두 번 정할 수 없다'], 0,
               '`amount = price * quantity`는 그 순간 계산한 30000을 넣어 두는 것이지, "앞으로 계속 곱해라"는 약속이 아닙니다. 수량을 바꾼 뒤 금액도 바꾸려면 곱셈 줄을 다시 실행해야 합니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「50000」: 변수는 공식이 아니라 값이라 나중에 수량을 바꿔도 따라 바뀌지 않는다.\n- 「오류」: 같은 변수에 다시 넣는 것은 자유다."),
        short("""
              두 종목의 가격이 같은지 **비교**하려 합니다. 결과가 `True`가 되도록 빈칸 `____`에 들어갈 연산자를 입력하세요.

              ```python
              price_a = 10000
              price_b = 10000
              print(price_a ____ price_b)
              ```
              """, ['=='],
              '`==`는 양쪽이 같은지 묻는 비교입니다. `=` 하나는 "오른쪽 값을 왼쪽 공간(변수)에 넣어라"는 뜻이라 비교가 아닙니다.'),
        choice('`prices = [10000, 10200, 10100]`에서 `prices[3]`을 실행하면 어떻게 될까요?',
               ['`IndexError`. 자리 3은 없다', '`10100`이 나온다', '`None`이 나온다'], 0,
               '자리 번호는 0, 1, 2까지입니다. 세 번째 값이 필요하면 `prices[2]`, 마지막 값이면 `prices[-1]`입니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「None」: 없는 자리는 조용히 비는 게 아니라 오류로 알려 준다.\n- 「10100」: 그 값은 자리 2(또는 -1)에 있다."),
        choice("`holding = {'price': 10000}`에서 `holding['Price']`를 실행하면 어떻게 될까요?",
               ['`KeyError`. 키는 대소문자까지 똑같아야 한다', '`10000`이 나온다. 대소문자는 구분하지 않는다', '빈 값이 나온다'], 0,
               "딕셔너리의 키는 글자가 완전히 같아야 찾습니다. `'price'`와 `'Price'`는 서로 다른 키입니다." "\n\n**다른 보기는 왜 아닌가**\n\n- 「10000이 나온다」: 대소문자가 다르면 다른 키다.\n- 「빈 값」: 없는 키는 빈 값 대신 KeyError를 낸다."),
        short('리스트 `prices`의 마지막 값을 뒤에서부터 세어 꺼내려면 대괄호 안에 무엇을 넣나요? (`prices[__]`)', ['-1'],
              '`-1`은 뒤에서 첫 번째, 즉 마지막 값입니다. `-2`는 뒤에서 두 번째입니다.'),
        choice("""**프롬프트 고르기** · `prices` 리스트에 값을 하나 추가하고 평균을 구해 `average` 변수에 담아야 합니다. 기본 함수만 쓰는 연습입니다. 어떤 프롬프트가 맞을까요?""",
               ["""파이썬. prices = [10000, 10200, 10100]에 10300을 append하고 평균을 average에 담아 출력. 평균은 sum/len으로, 다른 라이브러리 없이. 코드만 줘""", """리스트 평균 구해 줘""", """numpy로 prices 평균 내는 코드 줘""", """prices에 값 넣고 평균 내 줘. 변수 이름은 알아서"""], 0,
               """정답은 자료, 추가할 값, 결과 변수 이름, 그리고 "sum/len으로, 다른 라이브러리 없이"라는 제약까지 적었습니다. 연습 목적이 있을 때는 방법을 지정해야 원하는 코드를 받습니다.

**다른 보기는 왜 아닌가**

- 「리스트 평균 구해 줘」: 어느 리스트인지, 결과를 어디 담는지 없다.
- 「numpy로」: 이 미션은 기본 함수 연습이라 numpy는 어긋난다.
- 「변수 이름은 알아서」: 검사기는 average라는 이름으로 읽는다. 이름을 맡기면 실패한다."""),
        choice("""**프롬프트 고르기** · `holdings[1]['name']`이 왜 두 번째 종목의 이름인지 헷갈립니다. AI에게 어떻게 물어야 개념이 정리될까요?""",
               ["""holdings = [{'name':'A',...},{'name':'B',...}] 에서 holdings[1]['name']이 'B'인 이유를 리스트 자리 번호와 딕셔너리 키로 나눠서 두 줄로 설명해 줘""", """이 코드 설명해 줘""", """holdings 두 번째 이름 뽑는 코드 줘""", """파이썬 리스트랑 딕셔너리 차이 알려 줘"""], 0,
               """정답은 실제 자료 모양과 코드를 보여 주고, 설명을 "자리 번호"와 "키" 두 단계로 나눠 달라고 했습니다. 답의 구조를 지정하면 이해가 빨라집니다.

**다른 보기는 왜 아닌가**

- 「이 코드 설명해 줘」: 코드가 없다. AI는 짐작으로 답한다.
- 「코드 줘」: 코드는 이미 있고 궁금한 건 이유다.
- 「리스트랑 딕셔너리 차이」: 일반론만 돌아오고 내 코드의 [1]['name']은 설명되지 않는다."""),
    ),
])
