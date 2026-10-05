"""저장 HTML에서 데이터 수집"""
from kpc_course.dsl import *

SOUP = PD + "from pathlib import Path\nfrom bs4 import BeautifulSoup\nhtml=Path('data/prices.html').read_text(encoding='utf-8')\nsoup=BeautifulSoup(html,'html.parser')\n"

UNIT = unit('html', '저장 HTML에서 데이터 수집', [
    concept('html-selectors', '웹 페이지는 글자 덩어리, 우리가 원하는 건 그중 두 칸',
        body="""
        지금까지의 표는 파일로 받았습니다. 그런데 어떤 숫자는 파일이 아니라 **웹 페이지에만** 있습니다. 포털의 시세 화면이 그렇습니다. 브라우저가 보여 주는 화면의 정체는 HTML이라는 글자 파일이고, 그 안에 가격이 적혀 있습니다. 문제는 가격 말고도 광고, 메뉴, 제목 같은 글자가 수천 줄 섞여 있다는 것입니다. 거기서 원하는 칸만 집어내는 것이 이 단원의 일입니다.

        ```comic-gen
        제목: 수집은 네 단계
        등장인물:
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [{식별자: 강사, 손모양: 가리키는손}]
            대사: [{화자: 강사, 내용: "선택자로 찾고, 글자를 꺼내고, 숫자로 바꾸고, 표에 모읍니다."}]
            다이어그램:
              종류: 머메이드
              제목: HTML에서 표까지
              높이: 600
              원문: |
                flowchart TB
                  A["1. 읽기: BeautifulSoup"] --> B["2. 선택: select(#prices li)"]
                  B --> C["3. 추출: 글자와 속성"]
                  C --> D["4. 변환: 쉼표 지우고 int()"]
                  D --> E["표: rows → DataFrame"]
        ```

        HTML은 `<li>`, `<span>`처럼 꺾쇠로 감싼 **태그**로 내용을 묶습니다. 앱이 준비한 `data/prices.html`은 아래처럼 생겼습니다. 종목 하나가 `li` 하나이고, 그 안에 이름을 담은 `span`과 가격을 담은 `b`가 있습니다.

        ```html
        <ul id="prices">
          <li data-code="A"><span class="name">가상A</span><b>10,000</b></li>
          <li data-code="B"><span class="name">가상B</span><b>20,000</b></li>
        </ul>
        ```

        원하는 태그를 집어내는 주소 표기법이 **선택자**(selector)입니다. `#prices`는 `id`가 prices인 요소, `.name`은 `class`가 name인 요소, `#prices li`는 "prices 안에 있는 모든 `li`"입니다. `BeautifulSoup`이라는 도구가 HTML을 읽어 두면 `select(선택자)`로 해당 요소를 전부, `select_one(선택자)`으로 첫 하나를 꺼낼 수 있습니다. 꺼낸 요소에서 글자만 뽑을 때는 `get_text(strip=True)`를 씁니다.

        ```python
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select('#prices li')                      # li 두 개
        name = items[0].select_one('.name').get_text(strip=True)  # '가상A'
        price = int(items[0].select_one('b').get_text(strip=True).replace(',', ''))
        ```

        마지막 줄에 함정이 하나 있습니다. 뽑아낸 가격은 `'10,000'`이라는 **글자**이고 쉼표까지 들어 있어서 `int()`로 바로 바꾸면 오류가 납니다. `replace(',', '')`로 쉼표를 지운 뒤에 `int()`를 거쳐야 계산할 수 있는 숫자가 됩니다. 수집은 늘 이렇게 "찾기 → 글자 뽑기 → 숫자로 고치기 → 표로 모으기" 네 단계입니다.

        실제 포털 사이트에 접속하는 대신 저장해 둔 문서로 연습하는 이유는 하나입니다. 사이트는 구조가 자주 바뀌고, 그러면 어제 되던 선택자가 오늘 빈 결과를 냅니다. 원리는 같으니 저장된 문서로 네 단계를 몸에 익히는 것이 먼저입니다.
        """,
        check=short('HTML에서 원하는 태그를 집어낼 때 쓰는 `#prices li` 같은 주소 표기법을 무엇이라고 하나요?', ['선택자', 'selector', 'CSS 선택자', 'css selector', 'CSS selector'],
                    '선택자(selector)는 "어떤 요소를 고를지"를 적는 표기법입니다. `#`은 id, `.`은 class, 공백은 "그 안의"를 뜻합니다.')),
    coding('string-to-int', '쉼표 있는 가격 글자를 숫자로',
        goal="""
        수집의 네 단계 중 세 번째, 글자를 숫자로 고치는 단계만 따로 연습합니다. `price_text`에 `'10,000'`이 들어 있습니다. 쉼표를 지우고 `int()`로 바꿔 `price`에 저장한 뒤 `price * 3`을 출력하세요.

        30000이 나오면 숫자로 바뀐 것입니다.
        """,
        hint="""
        `price_text.replace(',', '')`가 쉼표를 빈 글자로 바꿔 `'10000'`을 만듭니다. 그다음 `int()`로 감싸세요. 순서를 바꿔 `int('10,000')`을 먼저 하면 `ValueError`가 납니다.
        """,
        starter="price_text = '10,000'\n# price를 만들고 price * 3을 출력하세요\n",
        solution="price_text = '10,000'\nprice = int(price_text.replace(',', ''))\nprint(price * 3)\n",
        check="assert s['price']==10000 and isinstance(s['price'],int)"),
    coding('select-one', '선택자로 요소 찾기',
        goal="""
        준비 코드가 HTML을 읽어 `soup`를 만들어 두었습니다. `#prices li`에 해당하는 요소가 몇 개인지 `n_items`에, 첫 번째 종목의 이름(`.name` 요소의 글자)을 `first_name`에 저장하고 출력하세요.

        2와 `가상A`가 나오면 맞게 찾은 것입니다.
        """,
        hint="""
        `soup.select('#prices li')`는 맞는 요소를 리스트로 돌려주니 `len()`으로 셉니다. 첫 요소 `[0]`에서 `.select_one('.name')`으로 이름 요소를 찾고 `.get_text(strip=True)`로 글자만 꺼내세요.
        """,
        starter=SOUP + "# n_items, first_name을 만들고 출력하세요\n",
        solution=SOUP + "items = soup.select('#prices li')\nn_items = len(items)\nfirst_name = items[0].select_one('.name').get_text(strip=True)\nprint(n_items, first_name)\n",
        check="assert s['n_items']==2 and s['first_name']=='가상A'"),
    coding('select-prices', '가격만 모두 뽑아 숫자 리스트로',
        goal="""
        이번에는 두 종목의 가격을 전부 뽑아 숫자 리스트로 만듭니다. `#prices li b`로 가격 요소를 모두 찾고, 하나씩 글자를 꺼내 쉼표를 지우고 `int()`로 바꾼 값을 `prices` 리스트에 모으세요.

        `prices`가 `[10000, 20000]`이면 맞게 한 것입니다. 앞 단원의 `for`와 `append`가 그대로 쓰입니다.
        """,
        hint="""
        `prices = []`로 빈 리스트를 만들고 `for tag in soup.select('#prices li b'):`로 돌면서 `prices.append(int(tag.get_text(strip=True).replace(',', '')))`를 하세요.
        """,
        starter=SOUP + "# prices 리스트를 만들고 출력하세요\n",
        solution=SOUP + "prices = []\nfor tag in soup.select('#prices li b'):\n    prices.append(int(tag.get_text(strip=True).replace(',', '')))\nprint(prices)\n",
        check="assert s['prices']==[10000,20000]"),
    coding('parse-html', '종목 코드·이름·가격을 표로 모으기',
        goal="""
        네 단계를 한 번에 합니다. `data/prices.html`을 읽어 `soup`를 만들고, `#prices li`를 하나씩 돌면서 종목 코드(`data-code` 속성), 이름(`.name`), 가격(`b`, 쉼표 없는 정수)을 담은 딕셔너리를 `rows` 리스트에 모은 뒤, `rows`로 `df`를 만드세요.

        `df`가 2행이고 `price` 열이 10000, 20000이면 맞게 한 것입니다. 딕셔너리 리스트가 표가 되는 것은 앞 단원에서 본 그대로입니다.
        """,
        hint="""
        `soup = BeautifulSoup(html, 'html.parser')`로 시작합니다. `for item in soup.select('#prices li'):` 안에서 코드는 `item['data-code']`, 이름은 `item.select_one('.name').get_text(strip=True)`, 가격은 `int(item.select_one('b').get_text(strip=True).replace(',', ''))`로 꺼내 `{'code': ..., 'name': ..., 'price': ...}` 딕셔너리를 `rows`에 `append`하세요. 마지막에 `df = pd.DataFrame(rows)`.
        """,
        starter=PD + "from pathlib import Path\nfrom bs4 import BeautifulSoup\nhtml=Path('data/prices.html').read_text(encoding='utf-8')\n# soup, rows, df를 만드세요\n",
        solution=PD + "from pathlib import Path\nfrom bs4 import BeautifulSoup\nhtml=Path('data/prices.html').read_text(encoding='utf-8')\nsoup=BeautifulSoup(html,'html.parser')\nrows=[]\nfor item in soup.select('#prices li'):\n    rows.append({'code':item['data-code'],'name':item.select_one('.name').get_text(strip=True),'price':int(item.select_one('b').get_text(strip=True).replace(',',''))})\ndf=pd.DataFrame(rows)\ndf\n",
        check="assert s['df']['code'].tolist()==['A','B']\nassert s['df']['price'].tolist()==[10000,20000]\nassert s['df']['name'].tolist()==['가상A','가상B']"),
    quiz('html-check', '단원 점검',
        short('`id`가 `prices`인 요소를 고르는 선택자를 기호까지 포함해 쓰면 무엇인가요?', ['#prices'],
              '`#`은 id를 뜻합니다. class를 고를 때는 `.name`처럼 점을 씁니다.'),
        choice("`int('10,000')`을 실행하면 어떻게 되나요?",
               ['`ValueError`. 쉼표 때문에 숫자로 바꿀 수 없다', '`10000`이 된다', '`10`이 된다'], 0,
               "`int()`는 숫자 글자만 받습니다. 쉼표를 먼저 `replace(',', '')`로 지워야 합니다." "\n\n**다른 보기는 왜 아닌가**\n\n- 「10이 된다」: 쉼표 앞에서 끊어 읽지 않는다.\n- 「10000이 된다」: int()는 쉼표를 알아서 지워 주지 않는다."),
        choice('`soup.select(...)`와 `soup.select_one(...)`의 차이는 무엇인가요?',
               ['앞은 맞는 요소를 전부 리스트로, 뒤는 첫 하나만 돌려준다', '앞은 id로, 뒤는 class로 찾는다', '둘은 같다'], 0,
               '`select`는 리스트라 `for`로 돌거나 `[0]`으로 꺼내야 하고, `select_one`은 요소 하나를 바로 돌려줍니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「id로, class로」: 둘 다 같은 CSS 선택자를 받는다.\n- 「둘은 같다」: 돌려주는 것이 리스트냐 요소 하나냐가 다르다."),
        choice('수집 코드가 어제는 됐는데 오늘은 빈 결과를 냅니다. 가장 가능성이 높은 원인은 무엇인가요?',
               ['사이트 구조가 바뀌어 선택자가 더 이상 맞지 않는다', 'Python 문법이 바뀌었다', '`int()`가 고장 났다'], 0,
               '선택자는 문서 구조에 기대어 있습니다. 태그나 class 이름이 바뀌면 같은 선택자가 아무것도 찾지 못합니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「Python 문법이 바뀌었다」: 하루 사이에 바뀌지 않는다.\n- 「int()가 고장」: 내장 함수는 고장 나지 않는다. 입력이 비었을 뿐이다."),
        choice("`item['data-code']`는 무엇을 꺼내나요?",
               ['`<li data-code="A">`처럼 태그에 붙은 속성 값', '`li` 안의 글자', '종목 가격'], 0,
               '꺾쇠 안에 `이름="값"` 꼴로 붙은 것이 속성입니다. 태그 사이의 글자는 `get_text()`로 꺼냅니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「종목 가격」: 가격은 b 태그 안의 글자다.\n- 「li 안의 글자」: 글자는 get_text()로 꺼낸다. 속성과 다르다."),
        short('수집한 딕셔너리 리스트 `rows`를 표로 만드는 코드는 `pd.________(rows)`입니다. 빈칸은?', ['DataFrame'],
              '앞 단원과 같습니다. 딕셔너리 하나가 한 행이 되어 `DataFrame`이 만들어집니다.'),
        choice("""**프롬프트 고르기** · 저장된 HTML에서 `#prices li` 안의 가격을 숫자 리스트로 모아야 합니다. 어떤 프롬프트가 한 번에 맞는 코드를 줄까요?""",
               ["""파이썬 BeautifulSoup. soup 객체가 있어. "#prices li b" 요소들의 텍스트를 쉼표 제거 후 int로 바꿔 prices 리스트에 모아 출력. 결과 [10000, 20000]. 코드만""", """웹에서 가격 긁어 줘""", """HTML 파싱하는 법 알려 줘""", """가격 뽑아서 리스트로 만들어 줘"""], 0,
               """정답은 선택자, 추출 → 정리 → 변환 → 저장 네 단계, 결과 변수와 기대값이 다 있습니다. 수집 프롬프트는 선택자를 주는 것이 절반입니다.

**다른 보기는 왜 아닌가**

- 「웹에서 가격 긁어 줘」: 어느 페이지, 어느 요소인지 없고 인터넷 접근 코드가 온다.
- 「파싱하는 법」: 설명만 온다.
- 「가격 뽑아서 리스트로」: 선택자가 없어 AI가 구조를 추측한다."""),
        choice("""**프롬프트 고르기** · 어제 되던 수집 코드가 오늘 빈 결과를 냅니다. AI에게 원인을 찾아 달라고 할 때 가장 좋은 질문은 무엇인가요?""",
               ["""BeautifulSoup으로 soup.select('#prices li')가 어제는 2개였는데 오늘은 빈 리스트야. HTML 구조가 바뀌었는지 확인하는 코드와, 선택자를 점검하는 순서를 알려 줘""", """코드가 안 돼""", """빈 리스트 나오는데 고쳐 줘""", """파이썬 버전 문제야?"""], 0,
               """정답은 어제와 오늘의 결과 차이, 쓴 선택자, 그리고 원하는 답의 종류(확인 코드 + 점검 순서)를 적었습니다. 증상의 변화를 적으면 원인이 좁혀집니다.

**다른 보기는 왜 아닌가**

- 「코드가 안 돼」: 아무 정보가 없다.
- 「고쳐 줘」: 코드를 보여 주지 않아 고칠 수 없다.
- 「파이썬 버전 문제야?」: 하루 사이 버전은 안 바뀐다. 잘못된 가설로 유도한다."""),
    ),
])
