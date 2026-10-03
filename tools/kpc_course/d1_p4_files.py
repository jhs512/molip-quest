"""1일차 · 4교시 — CSV·Excel과 행·열 선택"""
from kpc_course.dsl import *

UNIT = unit('files', '1일차 · 4교시 — CSV·Excel과 행·열 선택', [
    concept('file-table', '표를 파일로 저장하고 다시 열기',
        body="""
        3교시의 표는 코드 안에 직접 적은 종목 세 개였습니다. 그런데 진짜 분석은 남이 만들어 둔 파일에서 시작합니다. 거래 내역은 Excel로 오고, 주가는 CSV로 내려받고, 설문 결과는 또 다른 CSV입니다. 오늘 오후부터 쓸 타이타닉 승객 기록도 1,309줄짜리 CSV 파일입니다. 그러니 "파일을 표로 읽어 오는 법"과 "표를 파일로 저장하는 법"이 먼저입니다.

        ```comic-gen
        제목: 어디서 왔든 읽고 나면 같은 표
        등장인물:
          강사:
            그림: 사람
            이름표: 강사
            외형: {옷: 재킷, 옷색: "#5379a7", 안경: true}
        컷:
          - 인물: [강사]
            대사: [{화자: 강사, 내용: "파일 형식이 달라도 DataFrame이 된 뒤에는 똑같이 다룹니다."}]
            다이어그램:
              종류: 머메이드
              제목: 파일 → DataFrame
              높이: 420
              원문: |
                flowchart TB
                  A["CSV 파일"] -->|read_csv| D["DataFrame"]
                  B["Excel 파일"] -->|read_excel| D
                  D --> E["다루는 법은 같다"]
        ```

        CSV는 값을 쉼표로 구분해 한 줄에 한 행씩 적은 **글자 파일**입니다. 메모장으로 열어도 읽힙니다. Excel 파일(.xlsx)은 시트와 서식이 있는 문서라서 더 복잡하지만, `pandas`로 읽으면 둘 다 똑같은 `DataFrame`이 됩니다. 어디서 왔든 표가 된 다음부터는 다루는 법이 같다는 것이 핵심입니다.

        ```python
        import pandas as pd
        orders.to_csv('orders.csv', index=False)   # 저장
        saved = pd.read_csv('orders.csv')          # 다시 읽기
        titanic = pd.read_csv('data/titanic.csv')  # 남이 만든 파일 읽기
        ```

        저장할 때 `index=False`를 붙이는 이유가 있습니다. `DataFrame`은 행마다 0, 1, 2… 번호(인덱스)를 달고 있는데, 이 번호를 파일에 함께 적으면 다시 읽을 때 "이름 없는 열"이 하나 더 생겨 버립니다. 번호는 데이터가 아니니 빼고 저장하는 것이 보통입니다.

        읽어 온 표가 어떻게 생겼는지 확인하는 세 가지는 늘 같습니다. `df.head()`로 앞 5행을 훑어보고, `df.shape`로 몇 행 몇 열인지 세고, `df.columns`로 열 이름을 확인합니다. 그다음에 원하는 열과 행을 고릅니다. 열은 `df['price']`처럼 이름으로, 행은 `df.iloc[:2]`처럼 자리 번호로, 또는 `df.loc[조건]`처럼 조건으로 고릅니다. 이번 시간의 미션은 이 동작들을 하나씩 해 보는 것입니다.
        """,
        check=short('`to_csv`로 저장할 때 행 번호(인덱스)를 파일에 넣지 않으려고 붙이는 옵션은 무엇인가요?', ['index=False', 'index = False'],
                    '`index=False`는 행 번호를 데이터 열로 저장하지 않게 합니다. 빼먹으면 다시 읽을 때 `Unnamed: 0`이라는 열이 생깁니다.')),
    coding('inspect-frame', '표의 크기와 열 이름 확인',
        goal="""
        네 건의 거래가 든 `orders` 표가 준비돼 있습니다. 가격 하나가 비어 있다는 점도 눈여겨보세요. 행 수를 `n_rows`, 열 수를 `n_columns`, 열 이름 리스트를 `column_names`에 저장하고 세 값을 출력하세요.

        4행 3열이고 열 이름은 `product`, `price`, `quantity`입니다.
        """,
        hint="""
        `orders.shape`는 `(4, 3)` 같은 쌍이라 `n_rows, n_columns = orders.shape`로 한 번에 두 변수에 나눠 담을 수 있습니다. 열 이름은 `list(orders.columns)`로 리스트로 만드세요.
        """,
        starter=ORDERS + "# n_rows, n_columns, column_names를 만들고 출력하세요\n",
        solution=ORDERS + "n_rows, n_columns = orders.shape\ncolumn_names = list(orders.columns)\nprint(n_rows, n_columns, column_names)\n",
        check="assert s['n_rows']==4 and s['n_columns']==3\nassert list(s['column_names'])==['product','price','quantity']"),
    coding('to-csv', '표를 CSV로 저장하고 다시 읽기',
        goal="""
        `orders`를 `orders.csv`라는 파일로 저장한 뒤, 그 파일을 다시 읽어 `saved`에 저장하세요. 저장할 때 `index=False`를 꼭 붙입니다. 마지막 줄에 `saved`를 적어 표를 확인하세요.

        다시 읽은 표가 원래처럼 4행 3열이고 열 이름이 같으면 맞게 한 것입니다.
        """,
        hint="""
        저장은 `orders.to_csv('orders.csv', index=False)`, 읽기는 `saved = pd.read_csv('orders.csv')`입니다. `index=False`를 빼면 `Unnamed: 0`이라는 열이 하나 더 생겨 열 수가 4가 됩니다.
        """,
        starter=ORDERS + "# orders.csv로 저장하고 다시 읽어 saved에 담으세요\n",
        solution=ORDERS + "orders.to_csv('orders.csv', index=False)\nsaved = pd.read_csv('orders.csv')\nsaved\n",
        check="import os\nassert os.path.exists('orders.csv')\nassert s['saved'].shape==(4,3) and list(s['saved'].columns)==['product','price','quantity']"),
    coding('csv-excel', 'CSV와 Excel, 읽고 나면 같은 표',
        goal="""
        같은 표를 CSV와 Excel 두 형식으로 저장하고 각각 다시 읽어 `csv_df`, `excel_df`에 저장하세요. 저장할 때는 둘 다 `index=False`입니다.

        두 표의 크기가 같고 `product` 열의 값도 같으면 맞게 한 것입니다. 파일 형식이 달라도 읽고 나면 같은 `DataFrame`이라는 것을 확인하는 미션입니다.
        """,
        hint="""
        저장은 `orders.to_csv('orders.csv', index=False)`와 `orders.to_excel('orders.xlsx', index=False)`, 읽기는 `pd.read_csv('orders.csv')`와 `pd.read_excel('orders.xlsx')`입니다. 파일 이름의 확장자만 다르고 쓰는 법은 같습니다.
        """,
        starter=ORDERS + "# 저장하고 다시 읽어 csv_df, excel_df를 만드세요\n",
        solution=ORDERS + "orders.to_csv('orders.csv',index=False)\norders.to_excel('orders.xlsx',index=False)\ncsv_df=pd.read_csv('orders.csv')\nexcel_df=pd.read_excel('orders.xlsx')\nprint(csv_df.shape, excel_df.shape)\ncsv_df\n",
        check="assert s['csv_df'].shape==(4,3) and s['excel_df'].shape==(4,3)\nassert s['csv_df']['product'].tolist()==['A','B','A','C']\nassert list(s['csv_df'].columns)==list(s['excel_df'].columns)"),
    coding('series-vs-frame', '대괄호 한 겹과 두 겹의 차이',
        goal="""
        `orders['price']`를 `price_series`에, `orders[['price']]`를 `price_frame`에 저장하고 각각 `type()`을 출력해 보세요. 하나는 `Series`, 하나는 `DataFrame`이 나옵니다.

        대괄호 한 겹은 **열 하나**를 세로줄 하나로 꺼내는 것이고, 두 겹은 "이 이름들의 열로 된 **표**를 달라"는 뜻입니다. 앞으로 `.sum()`, `.mean()`처럼 열 하나에 계산할 때는 한 겹, 열 여러 개를 골라 표로 쓸 때는 두 겹을 씁니다.
        """,
        hint="""
        `orders['price']`는 한 열인 `Series`, `orders[['price']]`는 열 이름 리스트를 넣은 것이라 `DataFrame`입니다. `print(type(price_series))`처럼 쓰면 자료구조 이름이 출력됩니다.
        """,
        starter=ORDERS + "# price_series, price_frame을 만들고 type을 출력하세요\n",
        solution=ORDERS + "price_series = orders['price']\nprice_frame = orders[['price']]\nprint(type(price_series))\nprint(type(price_frame))\n",
        check="import pandas as pd\nassert isinstance(s['price_series'],pd.Series) and isinstance(s['price_frame'],pd.DataFrame)"),
    coding('selection', '원하는 열과 첫 두 행',
        goal="""
        표에서 필요한 부분만 잘라 냅니다. `product`와 `price` 두 열만 고른 표를 `selected`에, 자리 번호로 첫 두 행만 고른 표를 `first_two`에 저장하세요.

        `selected`는 4행 2열, `first_two`의 제품은 A와 B면 맞게 한 것입니다.
        """,
        hint="""
        열 여러 개는 `orders[['product', 'price']]`처럼 이름 리스트로 고릅니다. 행을 자리 번호로 고를 때는 `orders.iloc[:2]`입니다. 리스트와 같은 규칙이라 끝 번호 2는 포함되지 않아 0번과 1번 행만 남습니다.
        """,
        starter=ORDERS + "# selected, first_two를 만드세요\n",
        solution=ORDERS + "selected=orders[['product','price']]\nfirst_two=orders.iloc[:2]\nprint(selected.shape,first_two.shape)\nselected\n",
        check="assert list(s['selected'].columns)==['product','price'] and s['selected'].shape==(4,2)\nassert s['first_two']['product'].tolist()==['A','B']"),
    coding('loc-condition', '조건으로 행 고르기',
        goal="""
        자리 번호가 아니라 **조건**으로 행을 고릅니다. 수량이 3 이상인 거래만 골라 `many`에 저장하고 마지막 줄에 `many`를 적어 표를 확인하세요.

        제품 A 두 건(수량 3과 4)만 남으면 맞게 한 것입니다.
        """,
        hint="""
        `orders['quantity'] >= 3`은 행마다 참·거짓을 매긴 결과입니다. 이걸 `orders.loc[...]` 안에 넣으면 참인 행만 남습니다. 3교시의 `if`가 표 전체에 한꺼번에 적용되는 셈입니다.
        """,
        starter=ORDERS + "# many를 만들고 표를 표시하세요\n",
        solution=ORDERS + "many = orders.loc[orders['quantity'] >= 3]\nmany\n",
        check="assert s['many']['product'].tolist()==['A','A'] and s['many']['quantity'].tolist()==[3,4]"),
    coding('read-csv-titanic', '남이 만든 파일 열어 보기',
        goal="""
        이제 진짜 파일입니다. 앱이 준비해 둔 `data/titanic.csv`를 읽어 `titanic`에 저장하고, `titanic.shape`를 출력한 뒤 마지막 줄에 `titanic.head()`를 적어 앞 5행을 보세요.

        1309행 14열이 나옵니다. 이 표가 내일까지 우리의 주인공입니다. 열 이름들을 한 번 훑어 두세요.
        """,
        hint="""
        `pd.read_csv('data/titanic.csv')`처럼 파일 경로를 따옴표로 감싸 넘기고 결과를 `titanic`에 저장하세요. 자료는 `data/` 폴더 안에 있어서 경로의 `data/`를 빼면 파일을 찾지 못합니다.
        """,
        starter='import pandas as pd\n# titanic을 읽고 shape와 head()를 확인하세요\n',
        solution="import pandas as pd\ntitanic = pd.read_csv('data/titanic.csv')\nprint(titanic.shape)\ntitanic.head()\n",
        check="assert s['titanic'].shape==(1309,14)"),
    quiz('files-check', '4교시 점검',
        choice("`orders.to_csv('orders.csv')`처럼 `index=False`를 빼고 저장한 파일을 다시 읽으면 어떻게 되나요?",
               ['`Unnamed: 0`이라는 열이 하나 더 생긴다', '아무 차이가 없다', '파일이 저장되지 않는다'], 0,
               '행 번호가 데이터처럼 저장돼서 다시 읽을 때 이름 없는 열이 하나 늘어납니다. 그래서 저장할 때 `index=False`를 붙입니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「저장되지 않는다」: 저장은 되지만 열이 하나 늘어난다.\n- 「아무 차이가 없다」: 다시 읽으면 Unnamed: 0 열이 생겨 4열이 된다."),
        choice("`orders[['price']]`의 자료구조는 무엇인가요?",
               ['`DataFrame`. 대괄호 두 겹은 열 이름 리스트로 표를 고르는 것', '`Series`. 열이 하나뿐이니까', '리스트'], 0,
               '열이 하나뿐이어도 대괄호 두 겹이면 "이 열들로 된 표"라서 `DataFrame`입니다. 세로줄 하나인 `Series`를 원하면 `orders[\'price\']`처럼 한 겹을 씁니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「Series」: 한 겹 `orders['price']`일 때 이야기다.\n- 「리스트」: pandas는 리스트가 아니라 Series/DataFrame을 돌려준다."),
        choice('`orders.iloc[:2]`에 포함되는 행은 어느 것인가요?',
               ['0번과 1번 행', '0번, 1번, 2번 행', '1번과 2번 행'], 0,
               '자리 번호 범위는 리스트처럼 끝 번호를 포함하지 않습니다. `:2`는 0번과 1번까지입니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「0, 1, 2번」: 끝 번호 2는 포함되지 않는다.\n- 「1번과 2번」: 범위는 0부터 시작한다."),
        choice("`pd.read_csv('titanic.csv')`가 `FileNotFoundError`를 냈습니다. 가장 먼저 확인할 것은 무엇인가요?",
               ['파일 경로. 이 앱의 자료는 `data/` 폴더 안에 있다', '`pandas`가 설치됐는지', '파일이 Excel인지'], 0,
               '오류 이름 그대로 "파일을 못 찾았다"는 뜻입니다. 자료는 `data/titanic.csv`에 있으니 경로에 `data/`를 넣어야 합니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「Excel인지」: 형식이 달라도 이 오류는 나지 않는다. 경로 문제다.\n- 「pandas 설치」: 설치가 안 됐으면 ImportError가 난다."),
        short('표의 앞 5행만 보여 주는 메서드는 무엇인가요? (`df.____()`)', ['head', 'head()'],
              '`head()`는 기본으로 앞 5행을 보여 줍니다. `head(10)`처럼 숫자를 넣으면 그만큼 보여 줍니다.'),
        choice('수량이 2 이상인 행만 고르는 코드는 어느 것인가요?',
               ["`orders.loc[orders['quantity'] >= 2]`", "`orders.iloc[orders['quantity'] >= 2]`", "`orders['quantity' >= 2]`"], 0,
               "조건으로 고를 때는 `loc`입니다. `iloc`은 자리 번호 전용이고, 마지막 보기는 문법 자체가 틀렸습니다." "\n\n**다른 보기는 왜 아닌가**\n\n- 「iloc[조건]」: iloc은 자리 번호만 받아 조건을 넣으면 오류가 난다.\n- 「orders['quantity' >= 2]」: 글자와 숫자를 비교하는 문법 오류다."),
        choice("""**프롬프트 고르기** · 표를 CSV로 저장했다가 다시 읽었더니 열이 하나 늘었습니다. AI에게 고쳐 달라고 할 때 가장 정확한 프롬프트는 무엇인가요?""",
               ["""pandas. orders.to_csv('orders.csv')로 저장하고 read_csv로 읽으니 Unnamed: 0 열이 생겨. index=False로 저장하는 코드로 고쳐 줘. 코드만""", """csv 저장이 이상해""", """열이 하나 더 생겼어. 지워 줘""", """pandas 저장 방법 알려 줘"""], 0,
               """정답은 증상(열 이름까지)과 원인 추정, 원하는 수정(index=False)을 적었습니다. 증상을 구체적으로 적으면 AI는 바로 그 옵션을 짚습니다.

**다른 보기는 왜 아닌가**

- 「저장이 이상해」: 무엇이 이상한지 없다.
- 「지워 줘」: 읽은 뒤 열을 지우는 땜질 코드를 받는다. 원인은 그대로다.
- 「저장 방법 알려 줘」: 일반 설명이 오고 내 문제는 안 풀린다."""),
        choice("""**프롬프트 고르기** · `orders`에서 `product`, `price` 두 열만 고르고, 첫 두 행만 따로 떼어야 합니다. 두 결과의 변수 이름이 검사 조건입니다. 어떤 프롬프트가 맞을까요?""",
               ["""pandas. orders에서 product, price 두 열만 고른 표를 selected에, iloc으로 첫 두 행만 고른 표를 first_two에 담아. 코드만""", """orders에서 필요한 부분만 잘라 줘""", """pandas로 열이랑 행 고르는 법 알려 줘""", """orders.head(2) 보여 줘"""], 0,
               """정답은 열 이름 목록, 자리 번호 선택 방법(iloc), 두 결과 변수 이름을 모두 적었습니다. 검사기는 변수 이름으로 읽습니다.

**다른 보기는 왜 아닌가**

- 「필요한 부분만」: 어느 열, 어느 행인지 없다.
- 「고르는 법 알려 줘」: 설명만 오고 내 변수는 안 생긴다.
- 「head(2)」: 열 고르기가 빠졌고 변수 이름도 없다."""),
    ),
])
