"""3일차 · 1교시 — 주가 파일과 시점"""
from kpc_course.dsl import *

UNIT = unit('stock-data', '3일차 · 1교시 — 주가 파일과 시점', [
    concept('saved-prices', '오늘 저녁에 아는 것으로 내일을 맞힌다',
        body="""
        마지막 날입니다. 이틀 동안 익힌 흐름, 즉 자료를 읽고, 입력과 정답을 나누고, 훈련과 테스트를 나누고, 기준 모델과 비교하는 흐름을 주가에 그대로 적용합니다. 다른 점은 하나뿐입니다. 타이타닉의 정답은 "생존/사망" 중 하나를 **고르는** 분류였고, 오늘의 정답은 "다음 거래일 종가"라는 **숫자**입니다. 숫자를 맞히는 것을 회귀라고 하며, 점수를 재는 방법이 달라집니다.

        자료는 `data/stock.csv`, 삼성전자의 하루치 주가 기록 401일분입니다. 날짜(`Date`), 시가(`Open`), 고가(`High`), 저가(`Low`), 종가(`Close`), 거래량(`Volume`), 전일 대비 변화율(`Change`)이 있습니다. 날짜가 있는 표는 날짜를 행 이름(인덱스)으로 올려 두면 다루기 편해서, 준비 코드가 늘 이렇게 읽습니다.

        ```python
        prices = pd.read_csv('data/stock.csv', parse_dates=['Date']).set_index('Date').sort_index()
        ```

        `parse_dates`는 글자를 날짜로 바꾸고, `set_index`는 날짜를 행 이름으로 올리고, `sort_index`는 날짜순으로 정렬합니다. 정렬이 중요한 이유는 곧 나옵니다.

        예측하는 상황을 정확히 정해 둡니다. **오늘 장이 끝난 저녁**, 오늘까지의 가격을 전부 알고 있는 상태에서, **다음 거래일의 종가**를 맞힙니다. "다음 날"이 아니라 "다음 거래일"인 이유는 주말과 휴장일에는 가격이 없기 때문입니다. 금요일 저녁의 정답은 토요일이 아니라 월요일 종가입니다. 이 시점을 흐리면 어제 배운 누수가 바로 생깁니다. 내일 가격이 입력에 섞이는 순간, 모델은 답을 보고 답을 맞히게 됩니다.

        빵 공장에 옮겨 보면 같은 그림입니다. 파리바게뜨 공장은 **새벽 3시**에 오늘 크루아상을 몇 개 구울지 정해야 합니다. 그 시점에 아는 것은 요일, 어제와 지난주 같은 요일의 판매량, 날씨 예보, 근처 학교의 개학 여부 정도이고, 모르는 것은 **오늘 실제로 팔릴 개수**입니다. 그 개수가 정답이고, 정답은 저녁에야 적힙니다. "오늘 판매량"을 입력에 넣고 오늘 생산량을 맞히면 점수는 완벽하지만 새벽 3시에는 쓸 수 없는 모델입니다. 주가에서 내일 종가를 입력에 넣는 것과 똑같은 누수입니다.

        한 가지 더. 이 수업은 **예측이 얼마나 빗나가는지를 재는 연습**이지 돈을 버는 방법이 아닙니다. 모델이 기준보다 조금 낫게 나와도 그것이 수익을 뜻하지는 않습니다. 결과를 투자 판단에 쓰지 마세요.
        """,
        check=short('오늘 저녁에 알고 있는 가격으로 맞히려는 정답, 즉 다음 거래일의 종가에 해당하는 열 이름은 무엇인가요?', ['Close', '종가', 'close'],
                    '종가 `Close`의 다음 거래일 값이 정답입니다. 다음 날이 아니라 다음 거래일이라는 점, 그리고 그 값은 입력에 넣으면 안 된다는 점을 기억하세요.')),
    coding('stock-load', '날짜 순서와 크기 확인',
        goal="""
        주가 파일을 읽어 `prices`에 저장하세요. `Date`를 날짜로 읽어 인덱스로 올리고 `sort_index()`로 정렬합니다. 행 수와 열 수를 `n_rows`, `n_columns`에 담고, 첫 날짜와 마지막 날짜도 출력하세요.

        401행 6열이고 날짜가 오름차순이면 맞게 읽은 것입니다.
        """,
        hint="""
        개념의 한 줄을 그대로 쓰면 됩니다. `pd.read_csv('data/stock.csv', parse_dates=['Date']).set_index('Date').sort_index()`. 날짜 범위는 `prices.index.min()`과 `prices.index.max()`입니다.
        """,
        starter='import pandas as pd\n# prices, n_rows, n_columns를 만드세요\n',
        solution=ST + "n_rows,n_columns=prices.shape\nprint(n_rows,n_columns)\nprint(prices.index.min(),prices.index.max())\nprices.head()\n",
        check="assert s['prices'].shape==(401,6) and s['n_rows']==401 and s['n_columns']==6\nassert s['prices'].index.is_monotonic_increasing and not s['prices'].index.has_duplicates\nassert s['prices']['Close'].iloc[0]==54100"),
    coding('close-plot', '종가를 선으로 그리기',
        goal="""
        날짜순 자료는 선그래프가 어울립니다. `fig, ax`를 만들고 `ax.plot(prices.index, prices['Close'])`로 종가를 선으로 그린 뒤 x축 이름 `Date`, y축 이름 `Close`를 붙여 띄우세요.

        401개 점을 이은 선 하나가 보이면 맞게 그린 것입니다. 1년 반 동안 가격이 어떻게 움직였는지 보세요.
        """,
        hint="""
        어제의 뼈대에서 `ax.bar`를 `ax.plot`으로 바꾸면 됩니다. x에는 날짜 인덱스 `prices.index`, y에는 `prices['Close']`.
        """,
        starter=ST + "import matplotlib.pyplot as plt\n# fig, ax를 만들고 종가를 그리세요\n",
        solution=ST + "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot(prices.index, prices['Close'])\nax.set(xlabel='Date', ylabel='Close', title='Close price')\nplt.show()\n",
        check="assert len(s['ax'].lines)==1 and len(s['ax'].lines[0].get_ydata())==401\nassert s['ax'].get_ylabel()=='Close'"),
    coding('price-range', '기간과 최고 종가',
        goal="""
        자료의 양 끝 날짜를 `first_date`, `last_date`에, 가장 높았던 종가를 `max_close`에, 그 날짜를 `max_date`에 저장하고 모두 출력하세요.

        최고 종가가 언제였는지 그래프와 맞춰 보세요.
        """,
        hint="""
        날짜 인덱스의 `.min()`과 `.max()`가 양 끝입니다. 종가 열의 `.max()`는 값이고, `.idxmax()`는 그 값이 있는 행 이름, 즉 날짜입니다.
        """,
        starter=ST + "# first_date, last_date, max_close, max_date를 만들고 출력하세요\n",
        solution=ST + "first_date = prices.index.min()\nlast_date = prices.index.max()\nmax_close = prices['Close'].max()\nmax_date = prices['Close'].idxmax()\nprint(first_date, last_date)\nprint(max_close, max_date)\n",
        check="import pandas as pd\nassert s['first_date']==pd.Timestamp('2025-01-13') and s['last_date']==pd.Timestamp('2026-09-04')\nassert s['max_close']==362500 and s['max_date']==pd.Timestamp('2026-06-18')"),
    quiz('stock-data-check', '3일차 1교시 점검',
        choice('금요일 저녁에 예측하는 "다음 거래일 종가"는 언제의 종가인가요?',
               ['월요일(다음 거래일)', '토요일(다음 날)', '금요일 당일'], 0,
               '주말과 휴장일에는 가격이 없습니다. 정답은 다음 달력 날짜가 아니라 다음 거래일의 종가입니다.'),
        choice('타이타닉 생존 예측과 오늘의 주가 예측은 무엇이 다른가요?',
               ['고르는 분류와 숫자를 맞히는 회귀', '둘 다 분류', '주가는 머신러닝이 아니다'], 0,
               '정답이 "생존/사망" 중 하나면 분류, 종가 같은 숫자면 회귀입니다. 흐름은 같고 점수 재는 법이 다릅니다.'),
        short('날짜를 행 이름으로 올린 뒤 날짜순으로 정렬하는 메서드는 무엇인가요? (`.set_index(\'Date\').________()`)', ['sort_index', 'sort_index()'],
              '`sort_index()`가 행 이름(날짜) 순으로 정렬합니다. 날짜가 뒤섞여 있으면 "이전 날", "다음 날"이 전부 틀어집니다.'),
        short('가장 높은 종가가 있는 날짜를 돌려주는 메서드는 무엇인가요? (`prices[\'Close\'].________()`)', ['idxmax', 'idxmax()'],
              '`max()`는 값, `idxmax()`는 그 값의 행 이름입니다. 날짜 인덱스에서는 날짜가 나옵니다.'),
        choice('모델이 기준 예측보다 오차가 작게 나왔습니다. 이것은 무엇을 뜻하나요?',
               ['이 기간에서 예측 오차가 더 작았다는 것뿐, 수익과는 별개다', '이 모델로 투자하면 돈을 번다', '예측이 항상 맞는다'], 0,
               '이 수업은 예측이 얼마나 빗나가는지를 재는 연습입니다. 오차가 작다는 것과 수익은 다른 이야기입니다.'),
    ),
])
