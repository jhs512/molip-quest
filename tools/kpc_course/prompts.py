"""The answer prompt for every coding problem, written the way a person actually types it.

Each entry is (prompt, why). `prompt` is what the "정답 구하는 프롬프트 복사" button copies:
two to five short lines a student would type into an AI, ending with "코드만 줘". The
professional vocabulary a working analyst uses is placed where it changes the answer
(temporal split, 누수, stratify, baseline, ...). `why` is shown in the prompt guide and
explains which words in this prompt carry the expertise and what happens without them.
"""

TAIL = "\n\n---\n코드만 줘"


def p(body, why):
    return (body.strip() + TAIL, why.strip())


PROMPTS = {
    # ---- 1일차 1교시 ----
    "hello": p("""
파이썬에서 "Hello, KPC!" 출력하는 코드
""", """
가장 짧은 프롬프트입니다. 그래도 두 가지는 들어 있습니다. **언어**(파이썬)와 **정확한 출력 문자열**(따옴표 안 그대로). "인사말 출력해 줘"라고 하면 AI는 Hello, World!를 줍니다. 검사기는 글자 단위로 비교하므로 출력할 글자를 따옴표로 묶어 그대로 주는 습관이 첫 번째 전문성입니다. "코드만 줘"는 설명 없이 붙여 넣을 수 있는 답을 받기 위한 말입니다.
"""),
    "print-calc": p("""
파이썬. 10000 * 3을 계산해서 결과 30000만 출력. 따옴표로 감싼 글자 말고 실제 계산.
""", """
"계산해서"와 "따옴표 말고 실제 계산"이 핵심입니다. 이 말이 없으면 AI가 `print("30000")`처럼 결과를 글자로 박아 줄 수 있고, 그러면 숫자가 바뀔 때 틀립니다. 기대 출력(30000)을 적어 주면 AI가 스스로 검산합니다.
"""),
    "variable-print": p("""
파이썬. price = 10000, quantity = 3 이 있어. 둘을 곱한 값을 amount 변수에 저장하고 print(amount).
변수 이름 그대로 써.
""", """
**변수 이름을 지정**하는 것이 이 프롬프트의 전문성입니다. 검사기는 `amount`라는 이름으로 값을 읽기 때문에 `total`이나 `result`로 받으면 정답이어도 실패합니다. "변수 이름 그대로"는 AI가 이름을 멋대로 바꾸는 흔한 버릇을 막는 한 줄입니다.
"""),
    "single-input": p("""
파이썬. 표준 입력 한 줄로 수량(정수)이 들어와. int로 받아서 가격 10000과 곱한 금액을 출력.
입력 3이면 30000.
""", """
"표준 입력"과 "int로 받아서"가 전문 용어입니다. `input()`은 글자를 돌려주므로 정수로 **형 변환**해야 곱셈이 됩니다. 이 말이 없으면 AI가 `input("수량: ")`처럼 안내 문구를 출력해 테스트가 깨지기도 합니다. 입력→출력 예시 한 쌍을 적으면 형식 오해가 사라집니다.
"""),
    "amount-input": p("""
파이썬. 표준 입력 한 줄에 "가격 수량"이 공백으로 들어와. 둘 다 int로 받아 곱한 금액만 출력.
입력 "10000 3" → 출력 30000
""", """
입력 **형식**("한 줄에 공백으로")을 적는 것이 핵심입니다. 형식을 안 적으면 AI는 두 줄로 받거나 쉼표로 자릅니다. "금액만 출력"은 `금액: 30000`처럼 꾸며서 출력하는 것을 막습니다. 예시 한 쌍이 명세를 대신합니다.
"""),
    "fstring-report": p("""
파이썬. 표준 입력 한 줄 "가격 수량"(공백, 정수). 곱한 금액을 f-string으로 "금액: 30000원" 형식 그대로 출력.
콜론 뒤 공백 하나, 숫자 뒤에 바로 "원".
""", """
출력 **형식을 글자 단위로** 지정했습니다. "콜론 뒤 공백 하나, 숫자 뒤에 바로 원"처럼 띄어쓰기까지 적어야 테스트를 통과합니다. "f-string"이라는 용어는 글자와 값을 섞는 표준 방법을 AI에게 지정하는 말입니다.
"""),
    # ---- 1일차 2교시 ----
    "list-index": p("""
파이썬. prices = [10000, 10200, 10100] 에서 첫 값을 first, 마지막 값을 last에 담고 둘 다 출력.
인덱스로 꺼내.
""", """
"인덱스로 꺼내"가 전문 용어입니다. 리스트의 자리 번호(0부터, 마지막은 -1)로 값을 꺼내라는 뜻이고, 이 말이 없으면 AI가 `min`/`max`나 정렬로 '우연히' 같은 값을 주기도 합니다. 변수 이름 두 개를 지정한 이유는 앞 문제와 같습니다.
"""),
    "list-len-sum": p("""
파이썬. prices = [10000, 10200, 10100]. 개수를 count, 합계를 total에 담고 출력. len과 sum 써.
""", """
`len`과 `sum`을 **지정**했습니다. 함수 이름을 아는 사람의 프롬프트입니다. 지정하지 않으면 AI가 반복문으로 길게 짜 주고, 그것도 답이지만 이 미션은 내장 함수를 쓰는 연습입니다. 원하는 도구를 이름으로 부르는 것이 전문성입니다.
"""),
    "dict-read": p("""
파이썬. holding = {'name':'연습A', 'price':10000, 'quantity':3} 딕셔너리에서 price와 quantity를 키로 꺼내 곱한 값을 amount에 저장하고 출력.
딕셔너리는 수정하지 마.
""", """
"키로 꺼내"는 딕셔너리 접근 방식(`holding['price']`)을 가리키는 용어입니다. "수정하지 마"는 검사기가 원본 딕셔너리를 그대로 확인하기 때문에 넣은 **제약**입니다. 하지 말아야 할 것을 적는 것도 프롬프트의 일부입니다.
"""),
    "holdings-access": p("""
파이썬. holdings 는 종목 딕셔너리 3개가 든 리스트야 (키: name, price, quantity).
두 번째 종목의 name을 second_name, 세 번째 종목의 price를 third_price에 담고 출력.
""", """
자료 **구조**를 한 줄로 설명했습니다("딕셔너리 3개가 든 리스트, 키는 …"). 구조를 말해 주면 AI는 `holdings[1]['name']`처럼 정확한 접근 코드를 짭니다. "두 번째"가 인덱스 1이라는 것은 AI가 알지만, 변수 이름은 알 수 없으니 지정했습니다.
"""),
    "holding": p("""
파이썬. holding = {'name':'연습A', 'price':10000, 'quantity':3}. quantity를 5로 바꾸고, price * quantity를 새 키 amount에 저장. holding['amount']가 50000이어야 해.
""", """
"새 키에 저장"이 딕셔너리를 **수정**하라는 전문 표현입니다. 앞 문제와 반대로 이번에는 원본을 바꿔야 하므로 그 점을 분명히 했습니다. 기대 결과(50000)를 적으면 AI가 바뀐 수량으로 계산했는지 스스로 확인합니다.
"""),
    "price-average": p("""
파이썬. prices = [10000, 10200, 10100]에 10300을 append하고, 개수를 count, 평균을 average에 담아 출력.
평균은 sum/len으로.
""", """
"append"와 "sum/len"을 지정했습니다. 파이썬 기본에는 `average()`가 없어서 AI가 `statistics`나 `numpy`를 끌어오기도 하는데, 이 미션은 기본 도구만 쓰는 연습이라 **방법을 못 박았습니다**. 쓰지 말아야 할 라이브러리를 막는 가장 쉬운 방법은 쓸 방법을 지정하는 것입니다.
"""),
    # ---- 1일차 3교시 ----
    "simple-if": p("""
파이썬. 표준 입력으로 가격(정수) 한 줄. 10000 이상이면 "기준 이상", 아니면 "기준 미만" 출력. if/else로.
10000은 "기준 이상".
""", """
"이상"의 경계를 **예시로 못 박았습니다**(10000은 기준 이상). 경계값은 사람끼리도 자주 틀리는 부분이라 AI에게도 적어 줘야 `>`와 `>=`를 혼동하지 않습니다. 출력 문자열은 따옴표로 그대로 줬습니다.
"""),
    "for-sum": p("""
파이썬. prices = [10000,10200,9900,10100]. sum() 쓰지 말고 for 반복문으로 total에 누적해서 출력.
""", """
"sum() 쓰지 말고 for로"가 이 프롬프트의 전부입니다. **금지와 지정**을 한 줄에 담았습니다. 연습 목적이 있을 때는 더 쉬운 방법을 막아야 원하는 코드를 받습니다. 이런 제약은 실무에서도 "이 라이브러리는 못 써"처럼 자주 등장합니다.
"""),
    "above-count": p("""
파이썬. prices = [10000,10200,9900,10100]. for 한 번 돌면서 합계는 total, 10000 이상인 값의 개수는 above_count에 누적. 둘 다 출력.
""", """
"for 한 번 돌면서" 두 가지를 같이 하라고 했습니다. 지정하지 않으면 AI는 `sum()`과 리스트 컴프리헨션으로 따로 계산합니다. 반복 안에 `if`를 넣는 구조를 원한다면 **구조를 말로** 적어야 합니다.
"""),
    "max-price": p("""
파이썬. prices = [10000,10200,9900,10100]. max() 쓰지 말고, highest = prices[0]에서 시작해 for와 if로 더 큰 값 만나면 갱신. 결과 highest 출력.
""", """
알고리즘을 **한 문장으로** 적었습니다("첫 값에서 시작해 더 큰 값을 만나면 갱신"). 방법을 알고 있으면 이렇게 적는 것이 가장 정확한 프롬프트이고, AI는 그 설명을 코드로 옮기는 역할만 합니다. `max()` 금지도 함께 적었습니다.
"""),
    "croissant-plan": p("""
파이썬. 지난 사흘 크루아상 판매량 sold = [412, 388, 455].
for로 합계를 total에 누적(sum 금지), 평균을 average에, 평균의 1.1배를 round한 정수를 plan에 담아 "오늘 생산 계획: 460개" 형식으로 출력.
""", """
현장 규칙("평균의 1.1배를 반올림")을 **숫자와 함수 이름(round)**으로 바꿔 적었습니다. "조금 여유 있게"라고 하면 AI마다 다른 답을 줍니다. 비즈니스 규칙을 계산식으로 번역하는 것이 분석가의 일이고, 그 번역이 프롬프트에 들어가야 합니다.
"""),
    "holdings-amounts": p("""
파이썬. holdings 는 {'name','price','quantity'} 딕셔너리 3개가 든 리스트. for로 돌면서 각 딕셔너리에 price*quantity를 amount 키로 추가. holdings 자체를 수정.
""", """
"각 딕셔너리에 … 키로 추가"와 "holdings 자체를 수정"이 핵심입니다. 검사기는 리스트 안 딕셔너리들이 **제자리에서(in place)** 바뀌었는지 보므로, 새 리스트를 만들어 돌려주는 코드는 실패합니다. 결과를 어디에 남길지 적는 것이 전문성입니다.
"""),
    "holdings-total": p("""
파이썬. holdings 리스트의 각 딕셔너리에 amount 키가 있어. 세 amount를 더해 total_amount에 담고 출력. 결과 130000.
""", """
짧지만 자료 구조와 결과 변수, 기대값이 다 있습니다. 기대값을 적으면 AI가 `quantity`를 더하는 식의 실수를 스스로 걸러 냅니다. 답을 알고 있을 때는 **답도 적어 주는 것**이 좋은 프롬프트입니다.
"""),
    "holdings-frame": p("""
pandas. holdings(딕셔너리 리스트, 키 name·price·quantity·amount)를 DataFrame으로 만들어 df에 담고 마지막 줄에 df.
열 순서 name, price, quantity, amount.
""", """
"pandas"와 "DataFrame"이라는 **도구 이름**이 들어갔습니다. 이제부터는 파이썬이 아니라 pandas로 일한다고 선언하는 셈입니다. "열 순서"를 적은 이유는 검사기가 열 이름 순서를 확인하기 때문이고, "마지막 줄에 df"는 이 앱이 마지막 표현식을 표로 보여 주기 때문입니다.
"""),
    "frame-column-sum": p("""
pandas. df(열 name·price·quantity·amount)에서 amount 열의 합을 .sum()으로 구해 total_amount에 담고 출력.
""", """
"amount 열의 합을 .sum()으로"는 반복문 대신 **열 연산**을 쓰라는 pandas식 표현입니다. 열 이름과 메서드를 함께 적으면 AI는 `df['amount'].sum()` 한 줄을 줍니다. 같은 일을 반복문으로 하던 앞 미션과 비교해 보라는 것이 이 미션의 요점입니다.
"""),
    # ---- 1일차 4교시 ----
    "inspect-frame": p("""
pandas. orders DataFrame(열 product, price, quantity, 4행)이 있어. 행 수 n_rows, 열 수 n_columns, 열 이름 리스트 column_names에 담고 출력.
shape와 columns 써.
""", """
"shape와 columns"는 표의 **뼈대를 보는 속성 이름**입니다. 이름을 알면 AI에게 바로 지정할 수 있고, 모르면 "행 수 세어 줘"로 돌려 말해야 합니다. 열 이름은 리스트로 달라고 했는데, `columns`는 Index 객체라 `list()`로 바꿔야 검사가 통과합니다.
"""),
    "to-csv": p("""
pandas. orders DataFrame을 orders.csv로 저장(index=False)하고 다시 read_csv로 읽어 saved에 담아. 마지막 줄에 saved.
""", """
"index=False"가 전문성입니다. 이 옵션이 없으면 저장할 때 행 번호가 열로 끼어들어 다시 읽은 표가 4열이 됩니다. pandas를 써 본 사람은 반드시 적는 옵션이고, AI도 적어 주면 빠뜨리지 않습니다.
"""),
    "csv-excel": p("""
pandas. orders DataFrame을 CSV와 Excel(xlsx) 두 형식으로 저장(둘 다 index=False)하고 각각 다시 읽어 csv_df, excel_df에 담아.
Excel은 openpyxl 엔진.
""", """
"openpyxl 엔진"은 Excel 파일을 다루는 **라이브러리 이름**입니다. 이 환경에 설치된 것을 지정해야 AI가 다른 엔진을 가정하지 않습니다. 두 결과 변수 이름과 `index=False`는 앞 문제와 같은 이유입니다.
"""),
    "series-vs-frame": p("""
pandas. orders DataFrame에서 orders['price']를 price_series, orders[['price']]를 price_frame에 담고 각각 type() 출력.
""", """
대괄호 한 겹과 두 겹을 **코드로 그대로** 적었습니다. 말로 "열 하나를 시리즈로, 표로"라고 해도 되지만, 코드로 적으면 오해가 없습니다. 프롬프트에 코드 조각을 섞는 것은 흔하고 좋은 방법입니다.
"""),
    "selection": p("""
pandas. orders DataFrame에서 product, price 두 열만 고른 표를 selected에, iloc으로 첫 두 행만 고른 표를 first_two에 담아.
""", """
"iloc으로"가 핵심 용어입니다. 자리 번호로 행을 고르는 pandas 방법이고, 이 말이 없으면 AI가 `head(2)`를 쓰기도 합니다. 결과는 같지만 이 미션은 `iloc`을 익히는 것이 목적입니다. 열 고르기는 열 이름 리스트로 지정했습니다.
"""),
    "loc-condition": p("""
pandas. orders DataFrame에서 quantity가 3 이상인 행만 불리언 마스크로 골라 many에 담고 마지막 줄에 many.
""", """
"불리언 마스크(boolean mask)"는 조건으로 행을 고르는 pandas의 표준 용어입니다(`orders[orders['quantity'] >= 3]`). 이 말을 쓰면 AI가 `query()`나 반복문 대신 가장 기본적인 형태를 줍니다. 조건의 경계(3 이상)도 적었습니다.
"""),
    "read-csv-titanic": p("""
pandas. data/titanic.csv를 read_csv로 읽어 titanic에 담고, titanic.shape 출력, 마지막 줄에 titanic.head().
""", """
**파일 경로를 상대 경로 그대로** 적었습니다. AI는 파일이 어디 있는지 모르므로 경로를 주지 않으면 `titanic.csv`나 인터넷 URL을 가정합니다. `shape`와 `head()`는 새 자료를 받으면 가장 먼저 보는 두 가지라 그대로 지정했습니다.
"""),
    # ---- 1일차 5교시 ----
    "count-missing": p("""
pandas. orders DataFrame(price 열에 결측 1개). isna().sum()으로 열별 결측 개수를 missing_counts에 담고, price 열 결측 개수를 int로 n_missing_price에 담아 출력.
""", """
"결측"과 "isna().sum()"이 전문 용어입니다. 빈칸을 결측(missing, NaN)이라 부르고 세는 표준 방법을 이름으로 지정했습니다. "int로"는 pandas 숫자형을 파이썬 정수로 바꾸라는 뜻으로, 검사기가 자료형을 확인하기 때문에 넣었습니다.
"""),
    "fill-median": p("""
pandas. orders['price']에 결측 1개. 중앙값을 median_price에, 결측을 중앙값으로 채운 열을 filled_price에 담아 둘 다 출력.
원본 orders는 바꾸지 마 (fillna 결과를 새 변수에).
""", """
"중앙값(median)으로 채운다"는 결측 처리의 표준 선택 중 하나이고, "원본은 바꾸지 마"는 **부작용 없는 처리**를 요구하는 말입니다. 이 한 줄이 없으면 AI가 `inplace=True`로 원본을 바꿔 검사가 실패합니다.
"""),
    "drop-missing": p("""
pandas. orders DataFrame에서 price가 결측인 행을 dropna로 빼서 dropped에 담고, 남은 행 수를 int로 n_left에. 둘 다 출력, 마지막 줄에 dropped.
""", """
"dropna로 빼서"가 결측 처리의 두 번째 길을 가리키는 용어입니다. 앞 문제의 채우기와 짝을 이룹니다. `subset=['price']`까지는 적지 않았지만, 결측이 price에만 있다는 걸 AI가 알도록 "price가 결측인 행"이라고 했습니다.
"""),
    "filter-orders": p("""
pandas. orders에서 price >= 12000 이고 quantity >= 2 인 행만 골라 selected에 담아. 두 조건은 & 로 묶고 각각 괄호. 결과에 .copy().
열은 product, price, quantity 유지.
""", """
"& 로 묶고 각각 괄호"는 pandas에서 두 조건을 합칠 때 가장 흔한 실수(`and` 사용, 괄호 누락)를 막는 지시입니다. ".copy()"는 뒤에서 수정해도 원본이 안 바뀌게 하는 **방어 코드**이고, 검사기가 확인합니다. 아는 함정은 프롬프트에 미리 적습니다.
"""),
    "or-filter": p("""
pandas. orders에서 product == 'A' 이거나 quantity == 1 인 행을 | 로 골라 either에 담고 마지막 줄에 either.
""", """
"| 로"가 pandas의 **또는** 연산자입니다. 파이썬의 `or`를 쓰면 오류가 나므로 연산자를 지정했습니다. 조건을 코드 형태(`product == 'A'`)로 적으면 글자 비교인지 숫자 비교인지도 분명해집니다.
"""),
    "missing-totals": p("""
pandas. orders(price 결측 1개). 결측을 중앙값으로 채운 표를 filled, 결측 행을 뺀 표를 dropped에 만들고, 각 표에 price*quantity 열 amount를 추가해 합계를 filled_total, dropped_total에 담아 둘 다 출력.
둘 다 원본은 건드리지 말고 .copy().
""", """
두 처리 방법을 **나란히 비교**하는 설계를 프롬프트에 담았습니다. 분석가는 "결측을 어떻게 다뤘는지에 따라 합계가 달라진다"는 것을 보고서에 적어야 하고, 그러려면 두 길을 모두 계산해야 합니다. 변수 네 개와 `.copy()`가 그 비교를 가능하게 합니다.
"""),
    # ---- 1일차 6교시 ----
    "string-to-int": p("""
파이썬. price_text = '10,000'. 쉼표를 지우고 int로 바꿔 price에 담은 뒤 price * 3 출력.
""", """
"쉼표를 지우고 int로"는 웹에서 긁어 온 숫자 글자를 정리하는 전형적인 단계입니다. 글자 `'10,000'`은 그대로 `int()`에 넣으면 오류가 나므로 **전처리 순서**(지우고 → 바꾸고)를 적었습니다.
"""),
    "select-one": p("""
파이썬 BeautifulSoup. soup 객체가 있어(data/prices.html). CSS 선택자 "#prices li"에 해당하는 요소 개수를 n_items에, 첫 요소 안 ".name"의 텍스트를 first_name에 담고 출력.
select와 select_one 써.
""", """
"CSS 선택자"와 "select / select_one"이 BeautifulSoup의 핵심 용어입니다. 선택자 문자열(`#prices li`, `.name`)을 그대로 주면 AI는 그걸 코드에 옮기기만 하면 됩니다. 웹 수집 프롬프트는 **선택자를 주는 것**이 절반입니다.
"""),
    "select-prices": p("""
파이썬 BeautifulSoup. soup 객체가 있어. "#prices li b" 요소들의 텍스트를 꺼내 쉼표 제거 후 int로 바꿔 prices 리스트에 모아 출력. 결과 [10000, 20000].
""", """
선택자, 정리 규칙(쉼표 제거, int), 결과 형태(리스트)와 기대값을 한 줄에 적었습니다. 수집 코드는 **선택 → 추출 → 변환 → 저장** 네 단계이고, 네 단계가 모두 프롬프트에 있어야 빠지는 단계 없이 받습니다.
"""),
    "parse-html": p("""
파이썬 BeautifulSoup + pandas. data/prices.html을 읽어 soup를 만들고, "#prices li"를 돌면서 data-code 속성, .name 텍스트, b 텍스트(쉼표 제거 후 int)를 딕셔너리로 rows 리스트에 모은 뒤 pd.DataFrame(rows)를 df에. 열 이름 code, name, price.
""", """
수집 전체 흐름을 한 번에 적은 프롬프트입니다. "data-code 속성"처럼 **속성과 텍스트를 구분**하고, 딕셔너리 리스트를 DataFrame으로 만드는 표준 패턴을 지정했습니다. 열 이름을 적은 이유는 검사기가 `price` 열을 보기 때문입니다.
"""),
    # ---- 1일차 7교시 ----
    "titanic-shape": p("""
pandas. titanic = pd.read_csv('data/titanic.csv'). 행 수 n_rows, 열 수 n_columns, 열 이름 리스트 columns에 담고 출력.
""", """
준비 코드를 **그대로 보여 주는** 방식입니다. 읽는 코드 한 줄을 주면 AI는 파일 경로와 변수 이름을 틀리지 않습니다. 나머지는 4교시의 `shape`/`columns` 패턴입니다.
"""),
    "survived-counts": p("""
pandas. titanic DataFrame. survived 열을 value_counts()해서 counts에 담고, 0(사망) 인원을 n_dead, 1(생존) 인원을 n_alive에 int로 담아 출력.
""", """
"value_counts()"가 범주형 열을 세는 표준 메서드입니다. 값의 **의미**(0 사망, 1 생존)를 적으면 AI가 두 변수를 바꿔 담지 않습니다. 타깃 열을 먼저 세는 것은 분류 문제의 첫 습관입니다.
"""),
    "missing-per-column": p("""
pandas. titanic DataFrame. isna().sum()을 missing에 담고, age와 fare의 결측 수를 int로 age_missing, fare_missing에 담아 출력.
""", """
5교시의 결측 세기를 실제 자료에 적용한 프롬프트입니다. 열 이름과 결과 변수를 짝지어 적었고, "int로"는 검사기 때문입니다. 자료를 받으면 **열별 결측부터 센다**는 순서가 프롬프트에 담겨 있습니다.
"""),
    "titanic-counts": p("""
pandas. titanic DataFrame. 전체 인원 n_total, age가 기록된 인원 n_known, age가 결측인 인원 n_unknown을 int로, survived의 평균을 survival_rate에 담아 전부 출력.
n_known + n_unknown == n_total 이어야 해.
""", """
"survived의 평균이 생존율"이라는 것은 0/1 타깃의 **평균이 비율**이라는 분석가의 상식입니다. 그리고 검산 조건(`n_known + n_unknown == n_total`)을 적었습니다. 검산식을 프롬프트에 넣으면 AI가 스스로 확인하고, 사람이 읽을 때도 의도가 분명합니다.
"""),
    # ---- 1일차 8교시 ----
    "sex-counts": p("""
pandas. titanic DataFrame. sex 열 value_counts()를 sex_counts에 담고 출력.
""", """
비율을 구하기 전에 **분모(그룹 인원)부터** 세는 순서를 프롬프트가 보여 줍니다. 짧지만 메서드 이름과 결과 변수가 있어 AI가 다른 것을 줄 여지가 없습니다.
"""),
    "sex-mean": p("""
pandas. titanic DataFrame. groupby('sex')['survived'].mean()을 rates에 담고 출력.
""", """
"groupby('sex')['survived'].mean()"을 코드로 그대로 적었습니다. 그룹별 비율은 **groupby + 타깃 평균**이라는 공식이고, 코드로 적을 수 있으면 그게 가장 정확한 프롬프트입니다.
"""),
    "sex-summary": p("""
pandas. titanic DataFrame. sex로 groupby한 survived에 agg(['count','sum','mean'])을 적용한 표를 sex_summary에 담고 마지막 줄에 sex_summary.
""", """
"agg(['count','sum','mean'])"이 핵심입니다. 인원·생존자·생존율을 **한 표에서** 보는 집계 방법이고, 이 세 개를 같이 보는 습관이 "비율 뒤에는 몇 명 중"을 붙이는 전문성입니다.
"""),
    "pclass-summary": p("""
pandas. titanic DataFrame. pclass로 groupby한 survived에 agg(['count','sum','mean'])을 적용해 pclass_summary에.
""", """
앞 프롬프트에서 묶는 열만 바꿨습니다. 같은 집계를 다른 열에 반복하는 것이 탐색의 기본 동작이고, 프롬프트도 **열 이름만 바꿔 재사용**합니다.
"""),
    "age-groups": p("""
pandas. titanic DataFrame. pd.cut으로 age를 bins=[0, 20, 40, 60, float('inf')], labels=['0~19','20~39','40~59','60+'], right=False 로 나눈 열 age_group을 titanic에 추가하고, age_group으로 groupby한 survived의 agg(['count','sum','mean'])을 age_summary에.
""", """
구간 나누기의 **모든 매개변수**(bins, labels, right=False)를 적었습니다. "20대, 30대로 나눠 줘"라고 하면 AI마다 경계가 달라지고 20살이 어느 구간인지 흔들립니다. `right=False`는 왼쪽 경계를 포함하라는 뜻으로, 구간 문제에서 가장 자주 틀리는 부분입니다.
"""),
    # ---- 2일차 1교시 ----
    "simple-bar": p("""
matplotlib. names = ['A','B','C'], amounts = [30000,40000,60000]. fig, ax = plt.subplots()로 만들고 ax.bar로 막대그래프. ax.set(title='Amount by stock', ylabel='Amount'). plt.show().
""", """
"fig, ax = plt.subplots()"와 "ax.bar"로 **Axes 방식**을 지정했습니다. `plt.bar()`로 그려도 그림은 같지만, 검사기는 `ax` 객체를 읽으므로 방식이 중요합니다. 제목과 축 이름 문자열을 그대로 준 것도 검사 때문입니다.
"""),
    "sex-bar": p("""
pandas + matplotlib. titanic DataFrame. groupby('sex')['survived'].mean()을 rates에 담고, rates*100을 ax.bar로 그려. ylim=(0,100), xlabel 'Sex', ylabel 'Survival rate (%)'. fig, ax = plt.subplots() 방식, plt.show().
""", """
집계(`groupby`)와 그리기(`ax.bar`)를 한 프롬프트에 묶었습니다. "rates*100"과 "ylim=(0,100)"은 **퍼센트 축**을 만드는 두 가지 지시이고, 하나만 적으면 축과 값이 안 맞습니다. 축 이름은 검사기가 보는 문자열이라 그대로 적었습니다.
"""),
    "pclass-bar": p("""
pandas + matplotlib. titanic DataFrame. groupby('pclass')['survived'].mean()을 rates에 담고 rates*100을 ax.bar로. ylim=(0,100), xlabel 'Pclass', ylabel 'Survival rate (%)'. fig, ax 방식, plt.show().
""", """
앞 프롬프트에서 열 이름과 축 이름만 바꿨습니다. 같은 그림을 다른 변수로 반복할 때는 **프롬프트도 복사해서 바꾸는 것**이 가장 빠르고 정확합니다.
"""),
    # ---- 2일차 2교시 ----
    "age-hist": p("""
pandas + seaborn. titanic DataFrame. age가 결측이 아닌 행만 known_age에 담고, fig, ax = plt.subplots() 뒤 sns.histplot(data=known_age, x='age', bins=20, ax=ax). 축 이름과 제목은 영어로. plt.show().
""", """
"결측이 아닌 행만"을 먼저 적은 것이 분석가의 순서입니다. 그리고 "bins=20"과 "ax=ax"가 중요합니다. 구간 수는 검사 조건이고, `ax=ax`는 seaborn 그림을 우리가 만든 Axes에 그리게 하는 **연결 고리**라 빠지면 검사기가 그림을 못 찾습니다.
"""),
    "fare-scatter": p("""
pandas + matplotlib. titanic DataFrame. age와 fare 둘 다 결측이 아닌 행만 known에 담고, fig, ax 만든 뒤 ax.scatter(known['age'], known['fare']). xlabel 'Age', ylabel 'Fare'. plt.show().
""", """
"둘 다 결측이 아닌 행만"은 산점도의 전제 조건입니다. 한쪽이 비면 점이 안 찍히거나 경고가 납니다. 그림 종류(산점도=`scatter`)와 두 축의 열을 **x, y 순서대로** 적었습니다.
"""),
    "correlation": p("""
pandas + seaborn. titanic DataFrame. columns=['pclass','age','sibsp','parch','fare','survived'] 열의 상관계수 표를 corr에 담고(titanic[columns].corr()), sns.heatmap(corr, annot=True, vmin=-1, vmax=1, ax=ax)로 그려. fig, ax 방식, plt.show().
""", """
"상관계수"와 `.corr()`, 히트맵 옵션 `annot=True, vmin=-1, vmax=1`을 적었습니다. `vmin/vmax`는 **색 범위를 −1~1로 고정**해 다른 자료와 비교 가능하게 하는 전문가의 기본 설정입니다. 옵션 이름을 아는 만큼 프롬프트가 정확해집니다.
"""),
    # ---- 2일차 3교시 ----
    "embarked-rate": p("""
pandas. titanic DataFrame. embarked로 groupby한 survived의 agg(['count','mean'])을 by_port에 담고 마지막 줄에 by_port.
""", """
8교시 집계 프롬프트의 재사용입니다. `count`를 빼지 않은 이유는 항구별 **인원이 다르면 비율의 신뢰도도 다르기** 때문입니다. 집계 프롬프트에는 늘 `count`를 넣는 습관을 보여 줍니다.
"""),
    "sex-pclass-table": p("""
pandas. titanic DataFrame. ['sex','pclass']로 groupby한 survived의 agg(['count','mean'])을 grouped에, grouped['mean'].unstack('pclass')를 wide에 담고 마지막 줄에 wide.
""", """
"두 열로 groupby"와 "unstack('pclass')"가 핵심 용어입니다. 두 조건으로 묶으면 긴 표가 되고, `unstack`은 그걸 **행×열 교차표**로 펼칩니다. 이 변환 이름을 알면 "성별 × 등급 표 만들어 줘"보다 훨씬 정확하게 받습니다.
"""),
    "combined-groups": p("""
pandas + matplotlib. titanic DataFrame. ['sex','pclass'] groupby survived agg(['count','mean'])을 grouped에, grouped['mean'].unstack('pclass')*100을 wide에. ax = wide.plot.bar(ylim=(0,100), rot=0)로 그리고 ylabel과 title 붙여 plt.show().
""", """
표를 바로 그리는 "wide.plot.bar"를 지정했습니다. pandas 표에서 **묶음 막대**를 그리는 가장 짧은 길이고, `rot=0`은 x축 글자를 눕히지 않는 옵션입니다. 결과 변수 `ax`에 그 반환값을 담아야 검사기가 그림을 읽습니다.
"""),
    # ---- 2일차 4교시 ----
    "drop-columns": p("""
pandas. titanic DataFrame. drop(columns=[...])으로 survived, name, ticket, cabin, boat, body, home.dest 를 빼서 candidates에 담고 열 이름 출력. 7열 남아야 해.
""", """
뺄 열을 **전부 이름으로** 적었습니다. 특히 `boat`, `body`는 사고 뒤에 적히는 열이라 입력에 넣으면 누수가 되는데, 그 판단은 AI가 아니라 자료를 아는 사람이 합니다. 프롬프트는 그 판단의 결과를 전달합니다.
"""),
    "xy-separation": p("""
pandas. titanic DataFrame. features = ['pclass','sex','age','sibsp','parch','fare','embarked'] 리스트를 만들고, X = titanic[features].copy(), y = titanic['survived'].astype(int).
""", """
입력 `X`와 정답 `y`를 나누는 **머신러닝의 첫 줄**을 코드로 적었습니다. `.copy()`와 `.astype(int)`는 뒤에서 생기는 경고와 자료형 문제를 미리 막는 전문가의 습관이고, 검사기도 확인합니다.
"""),
    "column-types": p("""
pandas. X DataFrame(열 pclass, sex, age, sibsp, parch, fare, embarked). 숫자형 열 이름 리스트를 numeric_columns, 문자(범주형) 열 이름 리스트를 category_columns에 담고 출력. select_dtypes 써.
""", """
"숫자형"과 "범주형"이라는 **자료형 구분**과 그걸 자동으로 가르는 `select_dtypes`를 지정했습니다. 다음 시간에 두 종류를 다르게 손질하므로, 이 구분을 코드로 남겨 두는 것이 전처리의 시작입니다.
"""),
    "get-dummies": p("""
pandas. titanic DataFrame. pd.get_dummies(titanic[['sex']])로 sex 열을 One-hot 인코딩해 encoded에 담고 마지막 줄에 encoded.head(). sex_female, sex_male 두 열이 나와야 해.
""", """
"One-hot 인코딩"이 글자 열을 숫자 열로 바꾸는 표준 용어입니다. 이 말을 쓰면 AI는 `map({'male':0})` 같은 임의 코드 대신 표준 변환을 줍니다. 기대 열 이름을 적어 결과를 검산할 수 있게 했습니다.
"""),
    # ---- 2일차 5교시 ----
    "stratified-split": p("""
scikit-learn. X, y가 있어. train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)로 X_train, X_test, y_train, y_test 만들고 두 쪽 행 수와 y 평균(생존 비율) 출력.
""", """
"stratify=y"와 "random_state=42"가 전문성입니다. **층화 분할**은 두 쪽의 생존 비율을 같게 유지하고, 고정 난수는 누가 실행해도 같은 분할을 만듭니다. 이 두 매개변수를 안 적으면 AI가 빼먹기 쉽고, 빼먹으면 결과를 재현할 수 없습니다.
"""),
    "first-model": p("""
scikit-learn. X_train, X_test, y_train, y_test가 있어. simple = ['pclass','sibsp','parch'] 세 열만 써서 LogisticRegression(max_iter=1000)을 model에 만들고 fit. X_test[simple] 예측의 accuracy_score를 accuracy에 담고 출력.
""", """
모델 이름(`LogisticRegression`)과 매개변수(`max_iter=1000`), 쓸 열을 지정했습니다. "빈칸 없는 숫자 열 세 개만"이라는 선택은 전처리 없이 돌리기 위한 **의도적 제한**이고, 그 의도가 열 목록으로 프롬프트에 들어갔습니다. fit → predict → 점수가 모델 프롬프트의 기본 골격입니다.
"""),
    "train-imputer": p("""
scikit-learn. X_train, X_test가 있어. SimpleImputer(strategy='median')를 imputer에 만들고, X_train[['age','fare']]에 fit_transform한 결과를 train_values, X_test[['age','fare']]에 transform한 결과를 test_values에. 둘의 shape 출력.
""", """
"훈련에는 fit_transform, 테스트에는 transform"이 이 프롬프트의 전문성입니다. 중앙값 같은 **기준은 훈련 자료에서만 정하고** 테스트에는 적용만 해야 누수가 없습니다. AI는 둘 다 `fit_transform`하는 실수를 자주 하므로 메서드 이름을 나눠 적었습니다.
"""),
    "onehot-fit": p("""
scikit-learn. X_train, X_test가 있어. OneHotEncoder(handle_unknown='ignore', sparse_output=False)를 encoder에 만들고 X_train[['sex']]에 fit_transform → train_encoded, X_test[['sex']]에 transform → test_encoded. shape 출력.
""", """
"handle_unknown='ignore'"는 테스트에 훈련 때 못 본 값이 나와도 오류 대신 0으로 처리하는 **운영용 옵션**이고, "sparse_output=False"는 결과를 일반 배열로 받는 옵션입니다. 둘 다 아는 사람만 적는 매개변수이며, fit/transform 구분은 앞 문제와 같습니다.
"""),
    "pipeline-build": p("""
scikit-learn. X_train, X_test가 있고 numeric = ['pclass','age','sibsp','parch','fare']. Pipeline([('fill', SimpleImputer(strategy='median')), ('scale', StandardScaler())])를 numeric_pipeline에 만들고, X_train[numeric]에 fit_transform → train_values, X_test[numeric]에 transform → test_values. shape 출력.
""", """
"Pipeline"으로 채우기와 표준화를 **한 객체로 묶으라**고 했습니다. 단계 이름('fill', 'scale')까지 적은 이유는 뒤 미션에서 그 이름으로 단계를 꺼내기 때문입니다. 손질 단계가 늘수록 Pipeline 없이는 순서가 꼬이고, 그걸 아는 사람의 프롬프트에는 Pipeline이 들어갑니다.
"""),
    # ---- 2일차 6교시 ----
    "dummy-only": p("""
scikit-learn. X_train, X_test, y_train, y_test가 있어. DummyClassifier(strategy='most_frequent')를 dummy에 만들어 fit하고 X_test 예측의 accuracy_score를 dummy_accuracy에 담아 출력.
""", """
"DummyClassifier(strategy='most_frequent')"가 **기준선(baseline)**을 만드는 표준 도구입니다. 모델을 돌리기 전에 "아무것도 안 배운 점수"를 먼저 재는 것이 전문가의 순서이고, 이 프롬프트는 그 순서의 첫 줄입니다.
"""),
    "model-comparison": p("""
scikit-learn. X_train, X_test, y_train, y_test와 make_preprocessor()가 있어. models = {'Dummy': DummyClassifier(strategy='most_frequent'), 'Logistic': LogisticRegression(max_iter=2000), 'Tree': DecisionTreeClassifier(max_depth=5, random_state=42), 'Forest': RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)}.
각각 Pipeline([('prepare', make_preprocessor()), ('model', m)])로 fit/predict해서 accuracy_score와 f1_score를 구하고, 모델 이름을 인덱스로 accuracy, f1 두 열인 DataFrame results를 만들어.
""", """
비교 실험의 설계를 통째로 적었습니다. **같은 전처리, 같은 분할, 같은 지표**로 네 모델을 돌리고 표 하나로 모으는 것이 공정한 비교이고, 기준 모델(Dummy)이 그 표의 첫 행입니다. 매개변수(`max_depth`, `random_state`)를 적은 이유는 재현성입니다.
"""),
    "train-vs-test": p("""
scikit-learn. X_train, X_test, y_train, y_test, make_preprocessor()가 있어. Pipeline([('prepare', make_preprocessor()), ('model', DecisionTreeClassifier(random_state=42))])를 model에 fit하고, 훈련 자료 정확도를 train_accuracy, 테스트 자료 정확도를 test_accuracy에 담아 둘 다 출력.
""", """
"훈련 정확도와 테스트 정확도를 둘 다"가 **과적합**을 잡아내는 방법입니다. 깊이 제한 없는 트리를 일부러 지정해 두 점수가 벌어지는 걸 보여 주는 실험이고, 그 의도(제한 없음)가 매개변수 생략으로 프롬프트에 들어 있습니다.
"""),
    # ---- 2일차 7교시 ----
    "credit-shape": p("""
pandas. credit = pd.read_csv('data/credit.csv'), target = 'default payment next month'. 행 수 n_rows, 열 수 n_columns에 담고, credit[target].value_counts()를 target_counts에 담아 출력.
""", """
타깃 열 이름에 **공백이 있어** 변수 `target`에 담아 둔 준비 코드를 그대로 보여 줬습니다. 열 이름을 말로 풀면 AI가 밑줄로 바꾸는 경우가 있어 코드로 적는 편이 안전합니다. 새 자료의 뼈대와 타깃 분포를 먼저 보는 순서는 타이타닉과 같습니다.
"""),
    "default-summary": p("""
pandas. credit DataFrame, target = 'default payment next month'. 부도(1) 인원을 default_count, 부도율(타깃 평균)을 default_rate에 담고, ID와 target 열을 drop한 입력 표를 X에 만들어. 셋 다 출력.
""", """
"ID를 입력에서 뺀다"가 전문적 판단입니다. 고객 번호는 규칙을 찾을 재료가 아니라 **식별자**이고, 넣으면 모델이 번호를 외웁니다. 부도율을 "타깃 평균"이라고 적은 것은 0/1 평균이 비율이라는 상식을 코드로 옮긴 것입니다.
"""),
    "limit-by-default": p("""
pandas. credit DataFrame, target 변수에 타깃 열 이름. target으로 groupby한 LIMIT_BAL의 mean을 limit_by_default에 담고 출력.
""", """
`groupby(target)['LIMIT_BAL'].mean()`을 말로 적었습니다. **타깃으로 묶어 입력 열의 평균을 비교**하는 것은 어떤 열이 타깃과 관련 있는지 보는 가장 빠른 방법이고, 열 이름(`LIMIT_BAL`)을 정확히 적어야 합니다.
"""),
    "delay-groups": p("""
pandas. credit DataFrame, target, pay_columns = ['PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6']. (credit[pay_columns] >= 1).any(axis=1)을 credit['has_delay']에 넣고, has_delay로 groupby한 target의 agg(['count','sum','mean'])을 summary에.
""", """
새 특징(feature)을 만드는 규칙을 **코드 한 줄로** 적었습니다. `.any(axis=1)`은 "여섯 열 중 하나라도 참"을 행마다 계산하는 표현이고, 말로 풀면 AI가 반복문으로 길게 짭니다. 특징을 만든 뒤 바로 `count/sum/mean`으로 효과를 보는 순서도 들어 있습니다.
"""),
    "pay0-rate": p("""
pandas. credit DataFrame, target. PAY_0로 groupby한 target의 agg(['count','mean'])을 pay0_summary에 담고, 상태 0의 부도율을 rate_0, 상태 2의 부도율을 rate_2에 담아 출력.
""", """
집계표에서 **특정 행의 값을 꺼내는** 단계까지 적었습니다(`pay0_summary.loc[0, 'mean']`). `count`를 함께 구하는 이유는 인원이 적은 상태의 비율은 믿을 수 없기 때문이고, 그 판단 재료를 프롬프트가 요구합니다.
"""),
    # ---- 2일차 8교시 ----
    "manual-metrics": p("""
파이썬. tp, fp, fn, tn = 2, 1, 1, 2. precision = tp/(tp+fp), recall = tp/(tp+fn), accuracy = (tp+tn)/(tp+fp+fn+tn) 계산해서 세 변수에 담고 출력.
""", """
공식을 **그대로** 적었습니다. precision·recall·accuracy의 정의를 아는 사람의 프롬프트이고, AI는 계산만 합니다. 혼동 행렬 네 칸(TP, FP, FN, TN)의 이름을 쓰는 것 자체가 분류 지표를 다루는 공통 언어입니다.
"""),
    "metrics-matrix": p("""
scikit-learn. y_true=[0,0,1,1,1,0], y_pred=[0,1,1,0,1,0]. accuracy_score, precision_score, recall_score, f1_score를 같은 이름 키('accuracy','precision','recall','f1')로 metrics 딕셔너리에 담고, confusion_matrix(y_true, y_pred, labels=[0,1])를 matrix에. 둘 다 출력.
""", """
함수 네 개의 이름과 **인자 순서(정답, 예측)**, 딕셔너리 키 이름, `labels=[0,1]`을 적었습니다. `labels`를 고정하면 혼동 행렬의 칸 위치가 항상 같아 TN/FP/FN/TP를 읽을 때 헷갈리지 않습니다. 지표 함수는 순서를 바꾸면 값이 달라지므로 순서를 적는 것이 중요합니다.
"""),
    "credit-model": p("""
scikit-learn. X_train, X_test, y_train, y_test가 있어(입력 PAY_0, LIMIT_BAL, AGE). models = {'Dummy': DummyClassifier(strategy='most_frequent'), 'Logistic': LogisticRegression(max_iter=1000)}. 각각 Pipeline([('scale', StandardScaler()), ('model', m)])로 fit/predict해서 accuracy, precision, recall, f1 네 지표를 구하고 모델 이름을 인덱스로 한 DataFrame results를 만들어. precision은 zero_division=0.
""", """
불균형 자료의 비교 실험입니다. **네 지표를 함께** 요구한 것과 "zero_division=0"이 전문성입니다. 기준 모델은 부도를 하나도 안 찍으므로 precision 계산에서 0으로 나누기가 생기는데, 그 경고를 어떻게 처리할지 미리 정해 주는 것이 아는 사람의 프롬프트입니다.
"""),
    "predict-proba": p("""
scikit-learn. 학습된 Pipeline model과 X_test가 있어. model.predict_proba(X_test)[:, 1]을 probabilities에 담고, 0.5 이상인 개수를 n_positive_05, 0.3 이상인 개수를 n_positive_03에 int로 담아 출력.
""", """
"predict_proba(...)[:, 1]"이 **부도일 확률**을 꺼내는 정확한 표현입니다. `[:, 1]`을 빼면 두 열이 나와 세는 코드가 틀립니다. 임계값 0.5와 0.3을 비교하게 한 것은 "모델은 확률을 주고, 기준은 사람이 정한다"는 다음 미션의 요점을 미리 보여 주기 위해서입니다.
"""),
    "thresholds": p("""
numpy. probabilities = np.array([0.1,0.35,0.49,0.51,0.8]). 0.5 이상이면 1 아니면 0인 정수 배열을 pred_05, 0.3 이상이면 1인 배열을 pred_03에 담고 각각 1의 개수 출력. (probabilities >= 0.5).astype(int) 식으로.
""", """
임계값(threshold)을 적용하는 코드를 **벡터 연산**(`(p >= 0.5).astype(int)`)으로 지정했습니다. 반복문으로도 되지만 numpy에서는 이 한 줄이 표준이고, 자료형을 `int`로 맞추는 것까지 적어야 검사가 통과합니다.
"""),
    # ---- 3일차 1교시 ----
    "stock-load": p("""
pandas. data/stock.csv를 parse_dates=['Date']로 읽고 set_index('Date').sort_index()해서 prices에. 행·열 수를 n_rows, n_columns에 담고, 첫 날짜와 마지막 날짜 출력.
""", """
시계열을 읽는 **세 가지 필수 처리**(날짜 파싱, 날짜 인덱스, 정렬)를 메서드 이름으로 적었습니다. 하나라도 빠지면 뒤의 `shift`/`rolling`이 엉뚱한 순서로 계산됩니다. 주가 파일 프롬프트는 늘 이 한 줄로 시작합니다.
"""),
    "close-plot": p("""
pandas + matplotlib. prices(Date 인덱스, Close 열)가 있어. fig, ax = plt.subplots() 뒤 ax.plot(prices.index, prices['Close']). xlabel 'Date', ylabel 'Close'. plt.show().
""", """
시간 자료는 **선그래프**(`ax.plot`)라는 선택과, x축에 날짜 인덱스를 쓴다는 것을 적었습니다. 축 이름은 검사 조건입니다. 2일차 그림 프롬프트와 구조가 같고 그림 종류만 다릅니다.
"""),
    "price-range": p("""
pandas. prices(Date 인덱스, Close 열). 첫 날짜 first_date, 마지막 날짜 last_date, 최고 종가 max_close, 그 날짜 max_date에 담고 전부 출력. 날짜는 index.min()/max(), 최고 종가 날짜는 idxmax().
""", """
"idxmax()"가 핵심입니다. 최댓값이 **언제** 있었는지를 돌려주는 메서드이고, 모르면 정렬해서 첫 행을 꺼내는 긴 코드를 받게 됩니다. 메서드 이름 하나가 코드 길이를 바꿉니다.
"""),
    # ---- 3일차 2교시 ----
    "daily-return": p("""
pandas. prices(Date 인덱스, Close 열). prices['Close'].pct_change()를 return_1 열로 추가하고 prices.head() 출력.
""", """
"pct_change()"가 **일별 수익률**을 만드는 표준 메서드입니다. "어제보다 몇 % 올랐나"를 말로 설명하면 AI가 `diff()/shift()`로 길게 짜는데, 이름을 알면 한 줄입니다.
"""),
    "moving-average": p("""
pandas. prices(Date 인덱스, Close 열). prices['Close'].rolling(5).mean()을 ma5 열로 추가하고 prices.head(6) 출력.
""", """
"rolling(5).mean()"이 **5거래일 이동평균**입니다. 창 크기(5)를 숫자로 적고, 처음 네 행이 비는 것이 정상이라는 걸 알기에 `head(6)`으로 확인합니다. 시계열 특징의 기본 어휘입니다.
"""),
    "lag-next": p("""
pandas. prices(Date 인덱스, Close 열). prices['Close'].shift(1)을 lag_close_1 열로, shift(-1)을 target_next_close 열로 추가.
""", """
"shift(1)은 어제, shift(-1)은 내일"이라는 **lag 개념**을 코드로 적었습니다. 부호를 틀리면 과거와 미래가 바뀌어 누수가 생기므로, 두 열의 이름과 shift 방향을 짝지어 명시했습니다.
"""),
    "stock-frame": p("""
pandas. prices(Date 인덱스, Close 열)와 빈 frame=pd.DataFrame(index=prices.index)가 있어. frame에 close(Close), return_1(pct_change), ma5(rolling(5).mean()), lag_close_1(shift(1)), target_next_close(shift(-1)), target_date(pd.Series(prices.index, index=prices.index).shift(-1)) 여섯 열을 만들고 frame = frame.dropna().copy(). 396행이어야 해.
""", """
입력 네 열과 정답, 그리고 **정답 날짜**(`target_date`)까지 한 표에 모으는 설계입니다. `target_date`를 남겨 두는 이유는 다음 교시에서 훈련/테스트 경계의 누수를 막기 위해서이고, 그 의도가 열 목록에 들어 있습니다. `dropna()`로 불완전한 행을 빼는 것까지 적었습니다.
"""),
    # ---- 3일차 3교시 ----
    "test-start": p("""
pandas. frame(Date 인덱스, 396행)이 있어. 마지막 80행의 첫 날짜를 test_start에 담고, 인덱스가 test_start 이상인 행 수를 int로 n_test에 담아 출력. frame.index[-80] 써.
""", """
시간 분할의 **경계 날짜**를 정하는 프롬프트입니다. "마지막 80거래일을 테스트로"라는 설계를 `frame.index[-80]`이라는 코드로 옮겼고, 검산(`n_test == 80`)까지 적었습니다.
"""),
    "time-boundary": p("""
pandas. frame(Date 인덱스, 열 close, return_1, ma5, lag_close_1, target_next_close, target_date). test_start = frame.index[-80]. 입력 날짜와 target_date가 둘 다 test_start 전인 행을 train_mask, 입력 날짜가 test_start 이상인 행을 test_mask로 만들고, feature_columns=['close','return_1','ma5','lag_close_1']로 X_train, X_test, y_train(target_next_close), y_test 만들어. 두 쪽 행 수 출력(훈련 315, 테스트 80).
""", """
"target_date도 test_start 전"이 이 프롬프트의 전문성입니다. 입력 날짜만 보고 나누면 테스트 첫날의 정답을 훈련에서 보게 되는 **경계 누수**가 생깁니다. 이 조건을 모르면 적을 수 없고, 적지 않으면 AI는 거의 항상 빠뜨립니다. 기대 행 수(315/80)로 검산합니다.
"""),
    "manual-mae": p("""
pandas. X_test(close 열)와 y_test가 있어. "내일 종가 = 오늘 종가" 기준 예측의 오차 (y_test - X_test['close']).abs()를 errors에, 그 평균을 manual_mae에 담아 출력.
""", """
MAE의 정의(**차이의 절댓값 평균**)를 코드로 적었습니다. 함수를 쓰기 전에 손으로 계산해 보는 단계이고, "기준 예측 = 오늘 종가"라는 naive forecast를 말로 설명했습니다. 정의를 아는 사람은 지표를 설명할 수 있습니다.
"""),
    "close-baseline": p("""
scikit-learn. X_test(close 열), y_test. 기준 예측 X_test['close'].to_numpy()를 baseline_pred에, mean_absolute_error(y_test, baseline_pred)를 baseline_mae에 담아 출력.
""", """
"mean_absolute_error(정답, 예측)" 함수와 **인자 순서**를 적었습니다. 그리고 기준 예측을 배열로 바꾸는 `.to_numpy()`까지. 이 값이 이후 모든 모델이 넘어야 할 선이라는 설계는 프롬프트 밖의 지식이지만, 변수 이름 `baseline_mae`가 그 역할을 말해 줍니다.
"""),
    "callcenter-baseline": p("""
pandas + scikit-learn. calls DataFrame(열 week 1/2, weekday 월~일, calls). 1주차 calls를 배열 last_week, 2주차 calls를 this_week에 담고, mean_absolute_error(this_week, last_week)를 baseline_mae에, 월요일 오차 abs(this_week[0]-last_week[0])를 monday_error에 담아 출력.
""", """
"지난주 같은 요일 = 이번 주 예측"이라는 **naive 기준 모델**을 콜센터에 옮긴 프롬프트입니다. 정답(this_week)과 예측(last_week)의 순서를 함수 인자에 맞춰 적었고, 월요일 하나를 따로 보게 했습니다. 기준 모델은 자료가 바뀌어도 같은 말로 요구할 수 있다는 것을 보여 줍니다.
"""),
    # ---- 3일차 4교시 ----
    "linear-only": p("""
scikit-learn. X_train, X_test, y_train, y_test가 있어(temporal split 완료). Pipeline([('scale', StandardScaler()), ('model', LinearRegression())])를 model에 fit. 테스트 예측을 prediction, mean_absolute_error를 linear_mae에 담아 출력하고 model.named_steps['model'].coef_도 출력.
""", """
"StandardScaler와 묶은 Pipeline"과 "named_steps로 계수 꺼내기"가 핵심입니다. 입력 크기가 제각각이면 계수를 비교할 수 없으므로 **표준화 뒤 회귀**가 표준이고, 단계 이름을 적어 두면 학습된 모델의 계수를 꺼낼 수 있습니다. "temporal split 완료"라는 한마디는 AI가 다시 섞지 않게 합니다.
"""),
    "regression-table": p("""
scikit-learn. X_train, X_test, y_train, y_test(temporal split). models = {'Linear': LinearRegression(), 'Ridge': Ridge(alpha=1), 'Lasso': Lasso(alpha=10, max_iter=20000, tol=0.001)}. 각각 StandardScaler와 Pipeline으로 fit해서 fitted 딕셔너리에 보관하고 테스트 예측을 predictions 딕셔너리에 모아. predictions['Baseline']은 X_test['close'] 값. 네 예측 각각 MAE, RMSE, R2를 구해 인덱스가 모델 이름이고 열이 MAE, RMSE, R2인 DataFrame results를 만들어. RMSE는 mean_squared_error의 제곱근.
""", """
회귀 비교 실험의 전체 설계입니다. **기준 예측을 표의 한 행으로** 넣는 것, 세 지표를 같은 테스트 기간에서 재는 것, 그리고 "RMSE는 MSE의 제곱근"이라는 정의까지 적었습니다. 정규화 매개변수(`alpha`)를 적은 것은 재현성 때문이고, 열 이름은 검사 조건입니다.
"""),
    "beat-baseline": p("""
scikit-learn. X_train, X_test, y_train, y_test(temporal split). 기준 예측 X_test['close']의 MAE를 baseline_mae, Pipeline(StandardScaler, Ridge(alpha=1))의 테스트 MAE를 ridge_mae에 담고, improved = ridge_mae < baseline_mae. 셋 다 출력. improved가 False여도 그대로 둬.
""", """
"False여도 그대로 둬"가 이 프롬프트의 윤리이자 전문성입니다. AI는 "개선"을 요구받으면 테스트 기간을 바꾸거나 매개변수를 뒤져 이기는 결과를 만들려 합니다. **같은 조건에서 정직하게 비교한 결과를 그대로 보고**하라는 말이 없으면 결과를 믿을 수 없습니다.
"""),
    "forecast-plot": p("""
scikit-learn + matplotlib. frame, X_train, X_test, y_train, y_test, test_mask(temporal split). Pipeline(StandardScaler, Ridge(alpha=1))을 fit해 prediction을 구하고, frame.loc[test_mask, 'target_date']를 인덱스로 actual(y_test 값)과 prediction 두 열인 comparison DataFrame을 만들어. fig, ax에 두 선을 그리고 xlabel 'Target date', 범례 표시, plt.show().
""", """
"x축을 **정답 날짜**(target_date)로"가 핵심입니다. 입력 날짜로 그리면 예측이 하루 앞당겨 보여 실제와 어긋납니다. 비교표(`comparison`)를 먼저 만들고 그리는 순서, 범례 표시까지 적어 그림을 읽을 수 있게 했습니다.
"""),
    "final-report": p("""
scikit-learn. X_train, X_test, y_train, y_test(temporal split, 테스트 80거래일), models = {'Linear': ..., 'Ridge': ...}가 있어. 각 모델을 StandardScaler Pipeline으로 fit해 테스트 MAE를 maes 딕셔너리에 모으고, 기준(X_test['close']) MAE와 비교해 report 딕셔너리를 만들어. 키: test_days, baseline_mae, best_model(MAE 최소 모델 이름), best_mae, improved(best_mae < baseline_mae). 결론 세 줄 출력: ① 무엇을 언제 예측했고 어떻게 나눴는지 ② 기준 MAE와 최선 MAE ③ 개선 여부. improved가 False면 그대로 적어.
""", """
보고서의 **구조**(숫자 다섯 개, 결론 세 줄)를 프롬프트에 그대로 넣었습니다. 분석 결과는 "무엇을, 언제, 어떻게 나눠, 기준 대비 얼마나, 그래서 개선했는지"로 보고하고, 개선 못 했으면 못 했다고 적습니다. 이 다섯 칸을 채우는 것이 3일 과정에서 가져가는 마지막 프롬프트입니다.
"""),
}
