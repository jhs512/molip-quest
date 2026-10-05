"""해설 모드 scripts for chapter stock, units d3_p1 (주가 파일과 시점) and d3_p2 (수익률·이동평균·lag):
what the tutor says and types for each concept and coding problem, keyed by activity id.
Format and rules: narration.py.

Voice: the instructor's (see .scratch/presenter-decks/spec.md): 해요체 구어, "자," opens a scene,
one or two short sentences per line, says what the student should look at right now.
"""

NARRATION = {
    # ---- 주가 파일과 시점 ----
    "saved-prices": [
        ("title", "자, 마지막 챕터예요. 오늘 저녁에 아는 것으로 내일을 맞히는 거예요."),
        ("마지막 챕터입니다. 지금까지 익힌 흐름", "흐름은 타이타닉이랑 똑같아요. 읽고, 입력과 정답 나누고, 훈련과 테스트 나누고, 기준 모델과 비교해요. 다른 건 하나, 정답이 고르는 게 아니라 숫자예요. 그걸 회귀라고 해요."),
        ("자료는 data/stock.csv, 삼성전자의 하루치 주가 기록", "자료는 data/stock.csv, 삼성전자 하루치 기록 401일분이에요. 날짜, 시가, 고가, 저가, 종가, 거래량, 변화율이 있어요."),
        ("prices = pd.read_csv('data/stock.csv', parse_dates=['날짜'])", "이 한 줄을 준비 코드가 늘 써요. parse_dates가 글자를 날짜로 바꾸고, set_index가 날짜를 행 이름으로 올리고, sort_index가 날짜순으로 줄 세워요."),
        ("예측하는 상황을 정확히 정해 둡니다", "상황을 못 박아요. 오늘 장이 끝난 저녁에, 다음 거래일 종가를 맞혀요. 금요일 저녁의 정답은 토요일이 아니라 월요일이거든요. 내일 가격이 입력에 섞이면 그게 누수예요."),
        ("빵 공장에 옮겨 보면 같은 그림입니다", "빵 공장도 같아요. 새벽 3시에 오늘 몇 개 구울지 정하는데, 오늘 판매량은 저녁에야 적히죠? 그걸 입력에 넣으면 점수는 완벽한데 새벽엔 못 쓰는 모델이에요."),
        ("제목: 결정하는 시각에 아는 것만", "만화를 보세요. 결정하는 시각에 아는 것만 입력이에요. 주가도 똑같아요. 오늘 저녁에 아는 걸로 내일을 맞히는 거죠."),
        ("한 가지 더. 이 수업은 예측이 얼마나 빗나가는지를 재는 연습", "한 가지 더요. 이 수업은 예측이 얼마나 빗나가는지 재는 연습이에요. 기준보다 조금 낫다고 돈이 되는 게 아니에요. 투자 판단엔 쓰지 마세요."),
        ("check", "확인 문항이요. 우리가 맞히려는 정답, 다음 거래일의 어느 열이었죠?"),
    ],
    "stock-load": [
        ("problem", "자, 주가 파일을 읽어 prices에 담아요. 날짜를 날짜로 읽어서 인덱스로 올리고 정렬해요. 행 수와 열 수, 첫 날짜와 마지막 날짜까지 출력하면 돼요."),
        ("starter", "준비 코드는 import pandas 한 줄이에요. 그대로 두고 아래에 써요."),
        ("code", "prices = pd.read_csv('data/stock.csv', parse_dates=['날짜']).set_index('날짜').sort_index()\n", "개념에서 본 그 한 줄이에요. parse_dates로 날짜를 날짜로 읽고, set_index로 행 이름으로 올리고, sort_index로 날짜순 정렬이에요."),
        ("code", "n_rows,n_columns=prices.shape\nprint(n_rows,n_columns)\n", "shape는 행 수와 열 수 두 개를 돌려줘요. 두 이름에 나눠 담고 출력해요."),
        ("code", "print(prices.index.min(),prices.index.max())\nprices.head()\n", "인덱스가 날짜니까 min과 max가 양 끝 날짜예요. 마지막 줄 head()는 표로 보여 줘요."),
        ("output", "401 6이 나왔죠? 날짜는 2025년 1월 13일부터 2026년 9월 4일까지예요. 표의 행 이름이 날짜고, 열이 시가부터 변화율까지 여섯 개예요."),
        ("submit", "제출할게요. 검사는 401행 6열인지, 날짜가 오름차순인지 봐요."),
    ],
    "close-plot": [
        ("problem", "자, 날짜순 자료는 선그래프예요. fig, ax를 만들고 종가를 선으로 그려요. x축 이름 날짜, y축 이름 종가를 붙이면 돼요."),
        ("starter", "준비 코드가 prices를 읽고 matplotlib까지 불러 뒀어요. 그대로 둘게요."),
        ("code", "fig, ax = plt.subplots()\nax.plot(prices.index, prices['종가'])\n", "뼈대는 막대그래프 때랑 같아요. ax.bar 대신 ax.plot이에요. x에 날짜 인덱스, y에 종가 열이에요."),
        ("code", "ax.set(xlabel='날짜', ylabel='종가', title='Close price')\nplt.show()\n", "ax.set으로 축 이름과 제목을 한 번에 붙이고, plt.show()로 띄워요."),
        ("output", "401개 점을 이은 선 하나가 보이죠? 2025년엔 5만 원대였다가 2026년 중반에 36만 원 넘게 올라가요. 1년 8개월의 움직임이에요."),
        ("submit", "제출할게요. 검사는 선이 하나이고 점이 401개인지, y축 이름이 종가인지 봐요."),
    ],
    "price-range": [
        ("problem", "자, 양 끝 날짜를 first_date와 last_date에, 가장 높았던 종가를 max_close에, 그 날짜를 max_date에 담고 출력해요."),
        ("starter", "준비 코드가 prices를 읽어 뒀어요. 그대로 둘게요."),
        ("code", "first_date = prices.index.min()\nlast_date = prices.index.max()\n", "날짜 인덱스의 min과 max가 양 끝 날짜예요. 정렬돼 있으니 첫 행과 마지막 행이기도 하죠."),
        ("code", "max_close = prices['종가'].max()\nmax_date = prices['종가'].idxmax()\n", "종가 열의 max는 값이고, idxmax는 그 값이 있는 행 이름이에요. 행 이름이 날짜니까 날짜가 나와요."),
        ("code", "print(first_date, last_date)\nprint(max_close, max_date)\n", "네 개를 두 줄로 출력해요."),
        ("output", "2025년 1월 13일부터 2026년 9월 4일이죠? 최고 종가는 362500, 2026년 6월 18일이에요. 그래프의 꼭대기와 맞춰 보세요."),
        ("submit", "제출할게요."),
    ],
    # ---- 수익률·이동평균·lag ----
    "lag-target": [
        ("title", "자, 이번엔 입력과 정답을 우리 손으로 만들어요. 과거 열은 입력, 미래 열은 정답이에요."),
        ("타이타닉에서는 입력 열이 이미 표에 있었습니다", "주가 표엔 종가 하나뿐이에요. 어제보다 얼마나 올랐나, 최근 며칠 평균, 어제 종가가 입력 재료고, 내일 종가가 정답이에요. 전부 종가 열을 위아래로 밀어서 만들어요."),
        ("위젯: moving", "위젯을 만져 보세요. 열을 한 칸 밀면 각 행 옆에 어느 날 값이 오는지 보여요."),
        ("제목: 아래로 밀면 어제, 위로 밀면 내일", "만화를 보세요. shift(1)은 어제 값을 오늘 줄로, shift(-1)은 내일 값을 오늘 줄로 가져와요. 내일 값은 정답이죠? 입력에 넣으면 답을 보고 답을 맞히는 누수예요."),
        ("shift(1)은 열을 한 칸 아래로 밉니다", "표를 보세요. shift(1)은 열을 한 칸 아래로 밀어서 각 행에 어제 종가를 놓아요. 첫 행은 어제가 없어 빈칸이에요. shift(-1)은 위로 밀어 내일 종가를 놓고, 마지막 행이 비어요."),
        ("제목: 한 칸 아래로, 한 칸 위로", "같은 밀기인데 하나는 과거라 입력, 하나는 미래라 정답이에요. 이 둘을 헷갈리면 누수가 그대로 재현돼요."),
        ("prices['return_1'] = prices['종가'].pct_change()", "코드 네 줄이 재료 네 개예요. pct_change가 어제 대비 변화율, rolling(5).mean()이 최근 5거래일 평균, shift(1)이 어제 종가, shift(-1)이 내일 종가예요."),
        ("pct_change()는 어제 대비 변화율이라 첫 행이 비고", "pct_change는 첫 행이 비고, rolling(5)는 다섯 개가 모여야 해서 처음 네 행이 비어요. 네 열을 다 만든 뒤 dropna로 한 번에 정리하면 돼요."),
        ("마지막으로 정답이 어느 날짜의 값인지도 표에 적어 둡니다", "정답이 어느 날짜 값인지도 target_date 열에 적어 둬요. 하루 어긋난 정답은 숫자만 보면 모르거든요. 다음 단원에서 훈련과 테스트를 나눌 때 꼭 써요."),
        ("check", "확인 문항이요. 한 칸 위로 밀어 내일 종가를 놓는 shift의 괄호 안 숫자예요."),
    ],
    "daily-return": [
        ("problem", "자, 첫 재료예요. 종가의 pct_change()를 return_1 열로 추가하고 head()로 확인해요."),
        ("starter", "준비 코드가 prices를 읽어 뒀어요. 그대로 둘게요."),
        ("code", "prices['return_1'] = prices['종가'].pct_change()\n", "대괄호에 새 이름 return_1을 적고 넣으면 새 열이 생겨요. pct_change()가 행마다 오늘 빼기 어제, 나누기 어제를 계산해요."),
        ("code", "prices.head()\n", "마지막 줄에 head()를 두면 표로 보여 줘요."),
        ("output", "맨 오른쪽 return_1 열을 보세요. 첫 행은 어제가 없어 NaN이고, 둘째 행은 마이너스 0.0037이에요. 54100에서 53900으로 0.37% 내린 거죠."),
        ("submit", "제출할게요."),
    ],
    "moving-average": [
        ("problem", "자, 둘째 재료예요. 종가의 rolling(5).mean()을 ma5 열로 추가하고 head(6)으로 확인해요."),
        ("starter", "준비 코드가 prices를 읽어 뒀어요. 그대로 둘게요."),
        ("code", "prices['ma5'] = prices['종가'].rolling(5).mean()\n", "rolling(5)가 오늘 포함 최근 5행이라는 창을 만들고, mean()이 그 평균을 내요. 창이 한 칸씩 내려가며 계산되는 거예요."),
        ("code", "prices.head(6)\n", "앞 여섯 행을 봐요. 창이 처음 꽉 차는 다섯째 행을 보려는 거예요."),
        ("output", "ma5 열이요. 처음 네 행은 NaN이고, 다섯째 행이 53940이에요. 첫 다섯 종가의 평균이죠. 여섯째 행은 한 칸 내려간 창의 평균 53800이에요."),
        ("submit", "제출할게요. 검사는 빈칸이 정확히 네 개인지도 봐요."),
    ],
    "lag-next": [
        ("problem", "자, 밀기 두 번이에요. 종가의 shift(1)을 lag_close_1 열로, shift(-1)을 target_next_close 열로 추가해요."),
        ("starter", "준비 코드가 prices를 읽어 뒀어요. 그대로 둘게요."),
        ("code", "prices['lag_close_1']=prices['종가'].shift(1)\n", "shift(1)은 한 칸 아래로예요. 각 행에 어제 종가가 와요. 과거니까 입력이에요."),
        ("code", "prices['target_next_close']=prices['종가'].shift(-1)\n", "shift(-1)은 한 칸 위로예요. 각 행에 내일 종가가 와요. 미래니까 이게 정답이고, 입력엔 절대 안 넣어요."),
        ("code", "prices.head()\n", "head()로 앞쪽을 봐요. tail()로 바꾸면 마지막 행도 볼 수 있어요."),
        ("output", "첫 행의 lag_close_1은 NaN, target_next_close는 53900이죠? 둘째 행의 lag_close_1은 첫 행 종가 54100이에요. 마지막 행은 target_next_close가 비어요."),
        ("submit", "제출할게요."),
    ],
    "stock-frame": [
        ("problem", "자, 재료를 한 표에 모아요. 빈 표 frame에 close, return_1, ma5, lag_close_1, target_next_close, target_date 여섯 열을 만들고, 빈칸 있는 행을 빼요."),
        ("starter", "준비 코드가 prices를 읽고, 날짜 인덱스만 있는 빈 표 frame을 만들어 뒀어요. 그대로 둘게요."),
        ("code", "frame['close']=prices['종가']\nframe['return_1']=prices['종가'].pct_change()\n", "close는 오늘 종가 그대로, return_1은 앞 미션의 pct_change예요."),
        ("code", "frame['ma5']=prices['종가'].rolling(5).mean()\nframe['lag_close_1']=prices['종가'].shift(1)\n", "ma5는 최근 5거래일 평균, lag_close_1은 shift(1), 어제 종가예요. 여기까지 입력 네 열이에요."),
        ("code", "frame['target_next_close']=prices['종가'].shift(-1)\nframe['target_date']=pd.Series(prices.index,index=prices.index).shift(-1)\n", "정답은 shift(-1), 내일 종가예요. 날짜 인덱스도 pd.Series로 열로 만들어 똑같이 shift(-1)하면 정답의 날짜 target_date가 돼요."),
        ("code", "frame=frame.dropna().copy()\n", "dropna로 빈칸 있는 행을 한 번에 빼요. copy()를 붙여 독립된 표로 만들어 둬요."),
        ("code", "print(frame.shape)\nframe.head()\n", "크기를 찍고 표를 봐요."),
        ("output", "(396, 6)이죠? 401행에서 앞 네 행과 마지막 한 행이 빠졌어요. 첫 행이 1월 17일이고 target_date는 1월 20일, 다음 거래일이에요. 주말을 건너뛰었죠?"),
        ("submit", "제출할게요. 검사는 396행 6열에 빈칸이 없는지, target_date가 모두 인덱스 날짜보다 뒤인지 봐요."),
    ],
    "fetch-prices": [
        ("title", "자, stock.csv가 어디서 왔는지 볼게요. 인터넷이 되면 두 줄이면 받아요."),
        ("import yfinance as yf", "yfinance는 야후 파이낸스에서, FinanceDataReader는 거래소 자료를 받아요. 종목 코드 뒤 .KS는 코스피라는 뜻이에요."),
        ("yfinance는 야후 파이낸스에서 받습니다", "둘 다 날짜가 인덱스인 표가 와요. 열은 시가, 고가, 저가, 종가, 거래량. 우리 파일은 그 열 이름을 한글로 바꿔 저장한 거예요."),
        ("받은 표를 바로 쓰지 않고 저장해서 쓰는 이유가 있습니다", "왜 저장해서 쓰냐. 모두 같은 숫자를 봐야 하고, 네트워크가 끊겨도 돌아야 하고, 한 달 뒤에도 같은 결과가 나와야 하거든요."),
        ("prices.to_csv('stock.csv')", "회사에서도 받는 코드는 하루 한 번 돌려 저장하고, 분석 코드는 그 파일을 읽어요. 섞어 두면 사이트가 바뀔 때 분석까지 멈춰요."),
        ("check", "확인 문항이요. 야후 파이낸스에서 받는 함수 이름, 코드 첫 줄에 있었죠?"),
    ],
}
