"""표에서 고르기 quizzes: a real table on screen, the student ticks rows or columns.

They train the analyst's reflexes the course keeps coming back to: which column is the target,
which columns leak or carry no rule, which rows can be a training example, how to keep both
classes in a sample, where the time boundary falls. One quiz per unit where the idea is taught;
chapters.build() slots each one right after that unit's 단원 점검.
"""
import csv
import pathlib

from kpc_course.dsl import exact_columns, exact_rows, pick_columns, pick_rows, quiz, table, text

DATA = pathlib.Path(__file__).resolve().parents[2] / "courses" / "data"


def rows_where(tbl, column, test):
    """Indices of the table's rows whose `column` satisfies `test(cell)`."""
    at = tbl["columns"].index(column)
    return [i for i, row in enumerate(tbl["rows"]) if test(row[at])]


# ---- Titanic: the target and the columns that may not go in ----------------------------------
TITANIC_ROWS = [0, 2, 5, 7, 11, 15, 324, 327, 709, 711]
TITANIC = table("titanic.csv", rows=TITANIC_ROWS,
                columns=["객실등급", "생존", "이름", "성별", "나이", "티켓", "요금", "탑승항구", "구명보트", "시신번호"])

TARGET_TABLE = quiz('target-table', '표에서 고르기 · 맞힐 칸과 쓸 수 있는 열',
    exact_columns("""
        승객 열 명의 기록입니다. 우리가 **맞히려는 칸**, 타깃 열을 고르세요.
        """, TITANIC, """
        타깃은 `생존`입니다. 나머지 열은 그 답을 맞히는 재료(입력) 후보입니다. 이름이나 요금을 맞히는 것이 아닙니다.
        """, "생존", ["생존"]),
    exact_columns("""
        **사고가 난 뒤에야 채워지는 열**을 모두 고르세요. 이런 열을 입력에 넣으면 답을 보고 답을 맞히는 셈입니다(누수).
        """, TITANIC, """
        `구명보트`에 번호가 있으면 살아남은 사람이고, `시신번호`가 있으면 죽은 사람입니다. 둘 다 사고 뒤에 적힌 값이라 "맞히는 시점"에는 알 수 없습니다. 반면 `요금`과 `객실등급`은 배를 타기 전에 정해진 값이라 써도 됩니다.
        """, "구명보트, 시신번호", ["구명보트", "시신번호"]),
    exact_columns("""
        **사람마다 거의 다 달라서 규칙의 재료가 못 되는 열**을 모두 고르세요.
        """, TITANIC, """
        `이름`과 `티켓` 번호는 승객마다 거의 다 다릅니다. 열 명이면 열 가지 값이라 "이 값이면 살았다"는 규칙을 만들 수 없습니다. 누수는 아니지만 입력에서 뺍니다. `성별`과 `탑승항구`는 값이 몇 가지뿐이라 규칙이 생깁니다.
        """, "이름, 티켓", ["이름", "티켓"]),
    exact_rows("""
        타깃을 확인하는 눈을 길러 봅니다. **살아남은 승객의 행**을 모두 고르세요.
        """, TITANIC, """
        `생존`이 1인 행입니다. `구명보트` 번호가 있는 행과 정확히 같다는 것도 보세요. 그래서 그 열이 누수입니다.
        """, "생존이 1인 행 전부", rows_where(TITANIC, "생존", lambda v: v == "1")),
    ask=["누수 열을 입력에 넣으면 점수가 어떻게 돼?", "성별은 값이 두 가지뿐인데 왜 규칙이 돼?", "퀴즈 전부 풀어서 채점해 줘"])

# ---- Titanic: building X ---------------------------------------------------------------------
X_TABLE = table("titanic.csv", rows=TITANIC_ROWS)
FEATURES = ["객실등급", "성별", "나이", "형제배우자", "부모자녀", "요금", "탑승항구"]

XY_TABLE = quiz('xy-table', '표에서 고르기 · 입력 X 만들기',
    exact_columns("""
        열네 열 전부가 보입니다. **입력 X로 쓸 열**을 모두 고르세요. 타깃, 사고 뒤에 채워지는 열, 사람마다 다 다른 열은 뺍니다.
        """, X_TABLE, """
        남는 일곱 열이 입력입니다: `객실등급`, `성별`, `나이`, `형제배우자`, `부모자녀`, `요금`, `탑승항구`. `생존`은 타깃, `구명보트`·`시신번호`는 누수, `이름`·`티켓`·`선실`·`출신목적지`는 사람마다 달라 규칙이 안 생깁니다.
        """, "객실등급, 성별, 나이, 형제배우자, 부모자녀, 요금, 탑승항구", FEATURES),
    exact_columns("""
        위에서 고른 입력 열 가운데 **이 표에서 빈칸이 있는 열**을 고르세요. 모델에 넣기 전에 채워야 하는 열입니다.
        """, X_TABLE, """
        `나이`가 비어 있는 승객이 있습니다(Baumann). 빈칸은 0이 아니므로 훈련 자료의 중앙값 같은 값으로 채운 뒤 모델에 넣습니다. `선실`도 비어 있지만 입력에서 이미 뺀 열입니다.
        """, "나이", ["나이"]),
    exact_columns("""
        입력 열 가운데 **글자 열**을 모두 고르세요. 모델은 숫자만 받으므로 이 열들은 One-hot으로 바꿔야 합니다.
        """, X_TABLE, """
        `성별`과 `탑승항구`가 글자입니다. `객실등급`은 1·2·3이라 숫자이고, `나이`·`요금`·`형제배우자`·`부모자녀`도 숫자입니다.
        """, "성별, 탑승항구", ["성별", "탑승항구"]),
    ask=["선실은 왜 빼? 등급이랑 비슷하지 않아?", "글자 열을 그냥 넣으면 무슨 오류가 나?", "퀴즈 전부 풀어서 채점해 줘"])

# ---- Titanic: splitting with both classes ----------------------------------------------------
SPLIT = table("titanic.csv", rows=[0, 3, 11, 15, 324, 327, 329, 702, 709, 711],
              columns=["객실등급", "생존", "이름", "성별", "나이", "요금"])

SPLIT_TABLE = quiz('split-table', '표에서 고르기 · 훈련 자료와 테스트 자료',
    pick_rows("""
        승객 열 명입니다. 이 중 **모델 학습에 쓸 6명**을 고르세요. 생존과 사망이 **같은 수**가 되게 고릅니다.
        """, SPLIT, """
        생존(1) 3명, 사망(0) 3명이면 됩니다. 한쪽만 있으면 모델은 "다 산다" 또는 "다 죽는다"만 배웁니다. 누구를 고르든 두 수만 맞으면 정답입니다.
        """, "생존이 1인 행 3개와 0인 행 3개, 모두 6개", size=6, quota=[("생존", 1, 3), ("생존", 0, 3)]),
    pick_rows("""
        **테스트 자료로 남길 2명**을 고르세요. 생존과 사망을 한 명씩 넣어, 테스트가 양쪽을 다 채점하게 합니다(stratify).
        """, SPLIT, """
        생존 한 명, 사망 한 명입니다. 테스트에 생존자가 한 명도 없으면 "생존자를 얼마나 찾아냈나"를 잴 수 없습니다. `train_test_split`의 `stratify=y`가 이 비율을 자동으로 지켜 줍니다.
        """, "생존이 1인 행 1개와 0인 행 1개", size=2, quota=[("생존", 1, 1), ("생존", 0, 1)]),
    pick_rows("""
        이번에는 **8명을 훈련 자료로** 고르세요. 생존 4명, 사망 4명이어야 하고, 나이가 비어 있는 승객은 **채워서라도 넣습니다**(빼지 않습니다).
        """, SPLIT, """
        입력 열의 빈칸은 채우면 되므로 그 승객을 버릴 이유가 없습니다. 자료가 아까우니까요. 버려야 하는 것은 **타깃**이 비어 있는 행뿐입니다. 생존 4, 사망 4가 되면 정답입니다.
        """, "생존이 1인 행 4개와 0인 행 4개, 모두 8개", size=8, quota=[("생존", 1, 4), ("생존", 0, 4)]),
    ask=["stratify가 없으면 실제로 무슨 일이 생겨?", "훈련 8명, 테스트 2명이면 80:20인 거야?", "퀴즈 전부 풀어서 채점해 줘"])

# ---- Croissant: rows with a blank target --------------------------------------------------------
CROISSANT = table("croissant.csv", rows=list(range(12, 22)))
BLANK_ROWS = rows_where(CROISSANT, "판매량", lambda v: v.strip() == "")
FILLED_ROWS = rows_where(CROISSANT, "판매량", lambda v: v.strip() != "")

MISSING_TABLE = quiz('missing-table', '표에서 고르기 · 빈칸이 있는 행',
    exact_rows("""
        빵 공장의 열흘치 기록입니다. **판매량이 비어 있는 행**을 고르세요.
        """, CROISSANT, """
        한 행의 판매량이 비어 있습니다. 0이 아니라 "모른다"입니다. 세어 보지도 않고 0으로 두면 그날이 한 개도 못 판 날이 되어 평균이 내려갑니다.
        """, "판매량이 빈 행 하나", BLANK_ROWS),
    exact_rows("""
        "내일 판매량 맞히기" 모델의 **정답(판매량)으로 쓸 수 있는 행**을 모두 고르세요.
        """, CROISSANT, """
        정답이 비어 있는 행은 학습에 쓸 수 없습니다. 입력 빈칸은 채우면 되지만, 정답 빈칸은 채우는 순간 지어낸 답을 배우는 셈이라 그 행을 뺍니다. 나머지 아홉 행이 정답이 있는 행입니다.
        """, "판매량이 있는 행 아홉 개", FILLED_ROWS),
    exact_columns("""
        이 표에서 **빈칸을 중앙값으로 채울 수 있는 숫자 열**을 모두 고르세요.
        """, CROISSANT, """
        `기온`과 `판매량`이 숫자입니다. `요일`과 `날씨`는 글자라 중앙값이 없고, 가장 흔한 값으로 채우거나 그 행을 뺍니다. `날짜`는 순서를 뜻하는 열이라 채우는 대상이 아닙니다.
        """, "기온, 판매량", ["기온", "판매량"]),
    ask=["정답 빈칸은 왜 채우면 안 돼?", "날씨 빈칸은 뭘로 채워?", "퀴즈 전부 풀어서 채점해 줘"])

# ---- Credit: target and identifiers -------------------------------------------------------------
CREDIT = table("credit.csv", rows=list(range(0, 8)),
               columns=["고객번호", "신용한도", "성별", "나이", "상환_9월", "상환_8월", "청구_9월", "납부_9월", "다음달 부도"])

CREDIT_TABLE = quiz('credit-table', '표에서 고르기 · 부도를 맞히는 표',
    exact_columns("""
        고객 여덟 명의 기록입니다. **맞히려는 칸**, 타깃 열을 고르세요.
        """, CREDIT, """
        `다음달 부도`가 타깃입니다. `상환_9월`은 지난달의 연체 상태이고 입력입니다. 이름은 비슷하지만 다른 시점의 다른 칸입니다.
        """, "다음달 부도", ["다음달 부도"]),
    exact_columns("""
        **입력에서 빼야 하는 열**을 고르세요. 사람마다 다 달라서 규칙의 재료가 못 되는 열입니다.
        """, CREDIT, """
        `고객번호`는 번호표일 뿐입니다. 3번 고객이 부도였다고 해서 4번이 부도인 것과 아무 관계가 없습니다. 나머지 열은 모두 한 달 전에 알 수 있는 값이라 입력으로 씁니다.
        """, "고객번호", ["고객번호"]),
    exact_rows("""
        **다음 달에 부도가 난 고객의 행**을 모두 고르세요.
        """, CREDIT, """
        `다음달 부도`가 1인 행입니다. 여덟 명 중 두 명이니 이 표의 부도율은 25%입니다. 전체 자료에서는 약 22%입니다.
        """, "다음달 부도가 1인 행 두 개", rows_where(CREDIT, "다음달 부도", lambda v: v == "1")),
    exact_rows("""
        **9월에 연체 중이었던 고객의 행**을 모두 고르세요. `상환_9월`이 1 이상이면 그만큼 달을 밀린 것입니다.
        """, CREDIT, """
        `상환_9월`이 1 이상인 행입니다. 0은 제때 냈고, 음수는 미리 냈거나 쓴 돈이 없다는 뜻입니다. 부도가 난 두 명 중 한 명이 여기 들어 있습니다. 연체 이력이 부도의 재료가 되는 이유입니다.
        """, "상환_9월이 1 이상인 행", rows_where(CREDIT, "상환_9월", lambda v: int(v) >= 1)),
    ask=["상환 상태 -1과 -2는 뭐가 달라?", "고객번호를 넣으면 점수가 왜 안 올라?", "퀴즈 전부 풀어서 채점해 줘"])

# ---- Stock: lag features and the time boundary ------------------------------------------------
def stock_frame():
    """The six-column frame the stock units build, for every trading day, as text."""
    with (DATA / "stock.csv").open(encoding="utf-8", newline="") as handle:
        prices = list(csv.DictReader(handle))
    close = [int(float(r["종가"])) for r in prices]
    rows = []
    for i, r in enumerate(prices):
        ret = f"{(close[i] / close[i - 1] - 1):.4f}" if i >= 1 else ""
        ma5 = f"{sum(close[i - 4:i + 1]) / 5:.0f}" if i >= 4 else ""
        lag = str(close[i - 1]) if i >= 1 else ""
        nxt = str(close[i + 1]) if i + 1 < len(prices) else ""
        nxt_date = prices[i + 1]["날짜"] if i + 1 < len(prices) else ""
        rows.append([r["날짜"], str(close[i]), ret, ma5, lag, nxt, nxt_date])
    return dict(columns=["날짜", "close", "return_1", "ma5", "lag_close_1", "target_next_close", "target_date"], rows=rows)


FRAME = stock_frame()
LAG = dict(columns=FRAME["columns"], rows=FRAME["rows"][10:18])

LAG_TABLE = quiz('lag-table', '표에서 고르기 · 어제로 내일을',
    exact_columns("""
        주가에서 만든 여섯 열입니다. **맞히려는 칸**, 타깃 열을 고르세요.
        """, LAG, """
        `target_next_close`, 다음 거래일의 종가입니다. `target_date`는 그 종가가 어느 날의 것인지 적어 둔 메모일 뿐, 맞히는 대상도 입력도 아닙니다.
        """, "target_next_close", ["target_next_close"]),
    exact_columns("""
        **입력에 넣으면 누수가 되는 열**을 모두 고르세요. 오늘 저녁에 모르는 값이 든 열입니다.
        """, LAG, """
        `target_next_close`는 정답 자체이고, `target_date`는 내일 날짜라 둘 다 오늘 저녁에는 모르는 값입니다. 둘을 입력에 넣으면 점수는 완벽해지지만 실전에서는 쓸 수 없는 모델이 됩니다.
        """, "target_next_close, target_date", ["target_next_close", "target_date"]),
    exact_columns("""
        **입력 X로 쓸 네 열**을 고르세요. 오늘 저녁에 전부 알 수 있는 값이어야 합니다.
        """, LAG, """
        `close`(오늘 종가), `return_1`(어제 대비 수익률), `ma5`(최근 5거래일 평균), `lag_close_1`(어제 종가). 넷 다 오늘 장이 끝나면 계산할 수 있습니다. `날짜`는 인덱스라 입력이 아닙니다.
        """, "close, return_1, ma5, lag_close_1", ["close", "return_1", "ma5", "lag_close_1"]),
    ask=["lag_close_1은 shift(1)인데 왜 과거야?", "target_date는 왜 남겨 둬?", "퀴즈 전부 풀어서 채점해 줘"])

BOUNDARY = dict(columns=["날짜", "close", "target_next_close", "target_date"],
                rows=[[r[0], r[1], r[5], r[6]] for r in FRAME["rows"][314:324]])
TEST_START = "2026-05-11"
TRAIN_ROWS = [i for i, r in enumerate(BOUNDARY["rows"]) if r[0] < TEST_START and r[3] < TEST_START]
TEST_ROWS = [i for i, r in enumerate(BOUNDARY["rows"]) if r[0] >= TEST_START]
EDGE_ROWS = [i for i, r in enumerate(BOUNDARY["rows"]) if r[0] < TEST_START and r[3] >= TEST_START]

TIME_TABLE = quiz('time-split-table', '표에서 고르기 · 시간의 경계',
    exact_rows(f"""
        테스트 시작일이 `{TEST_START}`입니다. **훈련 자료로 쓸 수 있는 행**을 모두 고르세요. 입력 날짜도, 정답 날짜(`target_date`)도 테스트 시작 전이어야 합니다.
        """, BOUNDARY, f"""
        입력 날짜가 `{TEST_START}` 전이면서 `target_date`도 그 전인 행입니다. 경계 바로 앞 하루는 입력은 훈련 기간인데 정답이 테스트 첫날 종가라서 뺍니다. 그 행을 넣으면 테스트 첫날 답을 미리 본 셈입니다.
        """, "5월 8일 전까지의 행 다섯 개", TRAIN_ROWS),
    exact_rows(f"""
        **테스트 자료로 쓸 행**을 모두 고르세요.
        """, BOUNDARY, f"""
        입력 날짜가 `{TEST_START}` 이후인 행입니다. 시간 자료는 섞어서 나누지 않습니다. 과거로 배우고 미래로 채점해야 실전과 같은 점수가 나옵니다.
        """, "5월 11일부터의 행 네 개", TEST_ROWS),
    exact_rows(f"""
        **훈련에도 테스트에도 넣지 않는 행**을 고르세요.
        """, BOUNDARY, f"""
        `2026-05-08` 행입니다. 입력은 훈련 기간이지만 정답이 `{TEST_START}`의 종가라서, 훈련에 넣으면 테스트 첫날 답이 새고 테스트에 넣으면 입력이 과거라 둘 다 어색합니다. 경계의 하루는 버립니다.
        """, "5월 8일 행 하나", EDGE_ROWS),
    ask=["경계의 하루를 넣으면 점수가 얼마나 달라져?", "테스트 80거래일은 어떻게 정한 거야?", "퀴즈 전부 풀어서 채점해 줘"])


# ---- Titanic: kinds of columns ------------------------------------------------------------------
COLUMN_KINDS = quiz('column-kinds-table', '표에서 고르기 · 열의 종류',
    exact_columns("""
        **빈칸이 있는 열**을 모두 고르세요. 이 표에서 한 칸이라도 비어 있으면 됩니다.
        """, X_TABLE, """
        `나이`, `선실`, `구명보트`, `시신번호`, `출신목적지`에 빈칸이 있습니다. 빈칸은 0이 아니라 "모른다"이고, 열마다 빈칸 수를 세는 것이 자료를 받고 맨 먼저 하는 일입니다.
        """, "나이, 선실, 구명보트, 시신번호, 출신목적지", ["나이", "선실", "구명보트", "시신번호", "출신목적지"]),
    exact_columns("""
        **글자가 든 열**을 모두 고르세요. 숫자처럼 보여도 글자면 글자입니다.
        """, X_TABLE, """
        `이름`, `성별`, `티켓`, `선실`, `탑승항구`, `구명보트`, `출신목적지`가 글자입니다. `구명보트`는 숫자 같지만 "D", "C"처럼 글자 번호가 섞여 있습니다. 모델은 숫자만 받으므로 쓸 글자 열은 One-hot으로 바꿉니다.
        """, "이름, 성별, 티켓, 선실, 탑승항구, 구명보트, 출신목적지", ["이름", "성별", "티켓", "선실", "탑승항구", "구명보트", "출신목적지"]),
    exact_rows("""
        **나이를 모르는 승객의 행**을 모두 고르세요. 평균 나이를 구할 때 분모에서 빠지는 사람들입니다.
        """, X_TABLE, """
        `나이`가 빈 행입니다. `mean()`은 빈칸을 빼고 평균을 내므로, "평균 나이"라고 말할 때는 "나이를 아는 승객 몇 명 중"을 붙여야 합니다.
        """, "나이가 빈 행", rows_where(X_TABLE, "나이", lambda v: v.strip() == "")),
    ask=["빈칸을 0으로 두면 평균이 어떻게 돼?", "구명보트 열은 왜 글자 열이야?", "퀴즈 전부 풀어서 채점해 줘"])

# ---- Titanic: numerator and denominator ---------------------------------------------------------
GROUPS = table("titanic.csv", rows=[0, 2, 5, 7, 11, 15, 324, 327, 329, 702, 705, 706, 709, 711],
               columns=["객실등급", "생존", "이름", "성별", "나이"])

GROUP_TABLE = quiz('group-table', '표에서 고르기 · 분모와 분자',
    exact_rows("""
        "여성 생존율"을 구합니다. **분모가 되는 행**, 여성 승객을 모두 고르세요.
        """, GROUPS, """
        `성별`이 여성인 행 전부가 분모입니다. 살았든 죽었든 상관없습니다. 비율은 이 수 위에서만 뜻이 있습니다.
        """, "성별이 여성인 행 전부", rows_where(GROUPS, "성별", lambda v: v == "여성")),
    exact_rows("""
        같은 비율의 **분자가 되는 행**, 여성이면서 살아남은 승객을 모두 고르세요.
        """, GROUPS, """
        `성별`이 여성이고 `생존`이 1인 행입니다. 분자를 분모로 나눈 것이 여성 생존율이고, `groupby('성별')['생존'].mean()`이 이 나눗셈을 그룹마다 해 줍니다.
        """, "여성이면서 생존이 1인 행", [i for i, r in enumerate(GROUPS["rows"]) if r[3] == "여성" and r[1] == "1"]),
    exact_rows("""
        "3등실 생존율"의 **분모**, 3등실 승객 행을 모두 고르세요.
        """, GROUPS, """
        `객실등급`이 3인 행입니다. 이 표에서는 다섯 명 중 한 명만 살았습니다. 전체 자료에서도 3등실 생존율이 가장 낮습니다.
        """, "객실등급이 3인 행 전부", rows_where(GROUPS, "객실등급", lambda v: v == "3")),
    exact_rows("""
        "등급별 평균 나이"를 구할 때 **분모에서 빠지는 행**, 나이를 모르는 승객을 모두 고르세요.
        """, GROUPS, """
        `나이`가 빈 행입니다. `agg(['count', 'mean'])`에서 `count`가 생존 수와 다르게 나오는 이유가 이것입니다. 비율이나 평균을 말할 때는 "몇 명 중"을 꼭 붙이세요.
        """, "나이가 빈 행", rows_where(GROUPS, "나이", lambda v: v.strip() == "")),
    ask=["분모가 다르면 비율이 어떻게 달라져?", "count와 sum이 뭐가 달라?", "퀴즈 전부 풀어서 채점해 줘"])

# ---- Titanic: which columns a chart needs -------------------------------------------------------
CHART = table("titanic.csv", rows=TITANIC_ROWS, columns=["객실등급", "생존", "성별", "나이", "형제배우자", "부모자녀", "요금", "탑승항구"])

CHART_TABLE = quiz('chart-table', '표에서 고르기 · 그래프에 필요한 열',
    exact_columns("""
        "성별에 따라 생존율이 다른가?"에 답하는 막대그래프를 그립니다. **필요한 열**을 모두 고르세요.
        """, CHART, """
        `성별`로 묶고 `생존`의 평균을 내면 막대 두 개가 나옵니다. 다른 열은 이 질문에 필요 없습니다. 그래프는 질문에 답하는 것이지 열을 전부 보여 주는 것이 아닙니다.
        """, "성별, 생존", ["성별", "생존"]),
    exact_columns("""
        "탑승 항구마다 요금이 얼마나 달랐나?"에 답하는 막대그래프의 **필요한 열**을 고르세요.
        """, CHART, """
        `탑승항구`로 묶고 `요금`의 평균을 냅니다. 묶는 열 하나, 재는 열 하나가 막대그래프의 기본 재료입니다.
        """, "탑승항구, 요금", ["탑승항구", "요금"]),
    exact_rows("""
        성별 생존율 그래프에서 **여성 막대 하나에 들어가는 승객 행**을 모두 고르세요.
        """, CHART, """
        `성별`이 여성인 행 전부입니다. 막대 높이는 이 행들의 `생존` 평균입니다. 막대 하나 뒤에 승객 몇 명이 있는지 늘 확인하세요.
        """, "성별이 여성인 행 전부", rows_where(CHART, "성별", lambda v: v == "여성")),
    ask=["막대그래프와 히스토그램은 뭐가 달라?", "ax.bar에 뭘 넘기는 거야?", "퀴즈 전부 풀어서 채점해 줘"])

DIST_TABLE = quiz('distribution-table', '표에서 고르기 · 질문에 맞는 열',
    exact_columns("""
        "승객 나이는 어떻게 퍼져 있나?"를 보려고 히스토그램을 그립니다. **필요한 열**을 고르세요.
        """, CHART, """
        `나이` 하나입니다. 히스토그램은 숫자 열 하나를 구간으로 나눠 개수를 세는 그래프라, 열 하나면 됩니다.
        """, "나이", ["나이"]),
    exact_columns("""
        "나이가 많을수록 요금을 더 냈나?"를 보려고 산점도를 그립니다. **필요한 열**을 모두 고르세요.
        """, CHART, """
        `나이`와 `요금`, 숫자 열 두 개입니다. 산점도는 승객 한 명을 점 하나로 찍으므로 두 열 다 숫자여야 하고, 둘 다 있는 승객만 찍힙니다.
        """, "나이, 요금", ["나이", "요금"]),
    exact_columns("""
        **상관계수 표에 넣을 수 있는 열**을 모두 고르세요. 숫자 열만 들어갑니다.
        """, CHART, """
        `객실등급`, `생존`, `나이`, `형제배우자`, `부모자녀`, `요금`입니다. `성별`과 `탑승항구`는 글자라 상관계수를 구할 수 없습니다. `생존`이 0과 1이라 숫자로 들어가는 것도 보세요. 그래서 다른 열과 생존의 상관을 읽을 수 있습니다.
        """, "객실등급, 생존, 나이, 형제배우자, 부모자녀, 요금", ["객실등급", "생존", "나이", "형제배우자", "부모자녀", "요금"]),
    ask=["글자 열은 상관계수를 왜 못 구해?", "산점도에서 빈칸 있는 승객은 어떻게 돼?", "퀴즈 전부 풀어서 채점해 줘"])

# ---- Titanic: a model's predictions next to the answers ----------------------------------------
PRED = dict(columns=["객실등급", "성별", "나이", "요금", "생존", "예측"],
            rows=[[r[0], r[2], r[3], r[6], r[1], p] for r, p in zip(CHART["rows"], ["1", "1", "0", "0", "1", "0", "1", "0", "0", "0"])])

PRED_TABLE = quiz('prediction-table', '표에서 고르기 · 예측과 정답',
    exact_rows("""
        테스트 승객 열 명과 어느 모델의 `예측`입니다. **모델이 맞힌 행**을 모두 고르세요.
        """, PRED, """
        `생존`과 `예측`이 같은 행입니다. 열 명 중 여덟 명이 같으니 정확도는 80%입니다.
        """, "생존과 예측이 같은 행", [i for i, r in enumerate(PRED["rows"]) if r[4] == r[5]]),
    exact_rows("""
        **기준 모델**은 입력을 보지 않고 가장 많은 답만 찍습니다. 전체 자료는 사망이 더 많아 "전원 사망"을 찍습니다. 이 열 명에서 **기준 모델이 틀리는 행**을 모두 고르세요.
        """, PRED, """
        살아남은 사람, 즉 `생존`이 1인 행 전부입니다. 기준 모델은 생존자를 한 명도 못 맞힙니다. 그래서 정확도가 그럴듯해 보여도 F1이 0입니다.
        """, "생존이 1인 행 전부", [i for i, r in enumerate(PRED["rows"]) if r[4] == "1"]),
    exact_rows("""
        모델이 **살아남은 사람을 놓친 행**(실제 생존인데 사망으로 예측)을 모두 고르세요.
        """, PRED, """
        `생존`이 1인데 `예측`이 0인 행입니다. 정확도 80%라는 숫자 하나로는 이 놓침이 보이지 않습니다. 그래서 생존자를 얼마나 찾아냈는지(재현율)를 따로 봅니다.
        """, "생존이 1이고 예측이 0인 행", [i for i, r in enumerate(PRED["rows"]) if r[4] == "1" and r[5] == "0"]),
    ask=["정확도 80%면 좋은 거야?", "기준 모델이 찍은 답은 어떻게 정해?", "퀴즈 전부 풀어서 채점해 줘"])

# ---- Credit: confusion cells and a threshold -------------------------------------------------
PROBA = dict(columns=["고객번호", "신용한도", "상환_9월", "실제", "확률", "예측(0.5)"],
             rows=[["1", "20000", "2", "1", "0.72", "1"], ["2", "120000", "-1", "1", "0.41", "0"], ["3", "90000", "0", "0", "0.18", "0"],
                   ["4", "50000", "0", "0", "0.55", "1"], ["5", "50000", "-1", "0", "0.09", "0"], ["6", "50000", "0", "0", "0.33", "0"],
                   ["7", "500000", "0", "0", "0.12", "0"], ["8", "100000", "0", "1", "0.27", "0"]])

PROBA_TABLE = quiz('proba-table', '표에서 고르기 · 확률과 기준값',
    exact_rows("""
        부도 모델이 고객 여덟 명에게 매긴 `확률`과, 기준값 0.5로 가른 `예측`입니다. **놓친 부도 고객**(실제 1, 예측 0)을 모두 고르세요.
        """, PROBA, """
        `실제`가 1인데 `예측`이 0인 행입니다. 혼동행렬의 FN입니다. 부도를 놓치면 빌려준 돈을 잃으므로 이 칸이 가장 비쌉니다.
        """, "실제 1, 예측 0인 행", [i for i, r in enumerate(PROBA["rows"]) if r[3] == "1" and r[5] == "0"]),
    exact_rows("""
        **헛경보**(실제 0, 예측 1) 행을 고르세요.
        """, PROBA, """
        `실제`가 0인데 `예측`이 1인 행, FP입니다. 멀쩡한 고객의 한도를 줄이는 비용이 듭니다. 놓침보다는 싸지만 공짜는 아닙니다.
        """, "실제 0, 예측 1인 행", [i for i, r in enumerate(PROBA["rows"]) if r[3] == "0" and r[5] == "1"]),
    exact_rows("""
        기준값을 **0.3**으로 내리면 **부도로 분류되는 고객**을 모두 고르세요.
        """, PROBA, """
        `확률`이 0.3 이상인 행입니다. 기준값을 내리면 부도로 잡는 사람이 늘어 놓침(FN)은 줄고 헛경보(FP)는 늡니다. 기준값은 두 비용을 저울질해 정합니다.
        """, "확률이 0.3 이상인 행", [i for i, r in enumerate(PROBA["rows"]) if float(r[4]) >= 0.3]),
    exact_rows("""
        기준값 0.3에서 **여전히 놓치는 부도 고객**을 고르세요.
        """, PROBA, """
        `실제`가 1인데 `확률`이 0.3보다 낮은 행입니다. 기준값을 내려도 확률이 낮게 매겨진 부도는 남습니다. 모델 자체를 좋게 만드는 일과 기준값을 고르는 일은 다른 일입니다.
        """, "실제 1이고 확률이 0.3 미만인 행", [i for i, r in enumerate(PROBA["rows"]) if r[3] == "1" and float(r[4]) < 0.3]),
    ask=["기준값을 0.1로 내리면 어떻게 돼?", "FN과 FP 중 뭐가 더 비싸?", "퀴즈 전부 풀어서 채점해 줘"])

# (chapter id, unit id, quiz, after): each slots in right after the activity `after` (the unit's
# first concept, so the eye is trained before the code), or after 단원 점검 when None.
PLACEMENTS = [
    ("pandas", "missing", MISSING_TABLE, "missing-values"),
    ("eda", "titanic-structure", TARGET_TABLE, "target"),
    ("eda", "titanic-structure", COLUMN_KINDS, "missing-per-column"),
    ("eda", "titanic-groups", GROUP_TABLE, "denominator"),
    ("visualization", "bar-chart", CHART_TABLE, "axes"),
    ("visualization", "distribution", DIST_TABLE, "distribution-types"),
    ("modeling", "features", XY_TABLE, "leakage"),
    ("modeling", "preprocessing", SPLIT_TABLE, "fit-train"),
    ("modeling", "classifiers", PRED_TABLE, "baselines"),
    ("credit", "credit-target", CREDIT_TABLE, "credit-definition"),
    ("credit", "credit-metrics", PROBA_TABLE, "manual-metrics"),
    ("stock", "stock-features", LAG_TABLE, "lag-target"),
    ("stock", "stock-split", TIME_TABLE, "temporal-boundary"),
]
