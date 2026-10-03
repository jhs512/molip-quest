"""The fixed 7-chapter, 20-unit outline. Unit files are named by day and period."""
import importlib

OUTLINE = [
    ("python", "1. 파이썬 개발 환경과 기본 문법 이해", ["d1_p1_environment", "d1_p2_structures", "d1_p3_control"]),
    ("pandas", "2. 데이터 수집 기초 및 pandas 활용", ["d1_p4_files", "d1_p5_missing", "d1_p6_html"]),
    ("eda", "3. Titanic 데이터 탐색 및 기초 분석", ["d1_p7_titanic_structure", "d1_p8_titanic_groups"]),
    ("visualization", "4. Titanic 데이터 시각화 분석", ["d2_p1_bar_chart", "d2_p2_distribution", "d2_p3_insight"]),
    ("modeling", "5. Titanic 전처리 및 머신러닝 모델링", ["d2_p4_features", "d2_p5_preprocessing", "d2_p6_classifiers"]),
    ("credit", "6. 금융 데이터 분석 및 신용카드 부도 예측", ["d2_p7_credit_target", "d2_p8_credit_metrics"]),
    ("stock", "7. 주가 데이터 기반 회귀 분석 프로젝트", ["d3_p1_stock_data", "d3_p2_stock_features", "d3_p3_stock_split", "d3_p4_regression_project"]),
]


# What an expert insists on in each chapter. `principles` are copied into the answer prompt
# that students paste into an external AI, so they are written in the vocabulary a working
# analyst would use; `why` explains them in the in-app prompt guide.
EXPERTISE = {
    "python": dict(principles=[
        "표준 입력은 `input()`으로 한 줄씩 읽고, 숫자는 `int()`·`float()`로 명시적으로 형 변환(type casting)합니다.",
        "출력은 `print()`와 f-string으로 요구 형식을 글자 단위로 맞추고, 디버그용 출력을 남기지 않습니다.",
        "변수 이름은 문제가 지정한 그대로 쓰고, 값을 직접 적는 매직 넘버 대신 준비된 변수로 계산합니다.",
        "표 형태 자료는 리스트·딕셔너리로 구성한 뒤 `pandas.DataFrame`으로 만듭니다.",
    ], why="""
1단원의 검사기는 출력을 글자 단위로 비교하고 결과를 변수 이름으로 읽습니다. 그래서 "형 변환", "f-string", "변수 이름 유지"처럼 **모양을 고정하는 용어**를 적어야 AI가 임의로 반올림하거나, 설명 문장을 함께 출력하거나, 변수 이름을 바꾸지 않습니다. 매직 넘버 금지는 가격이 바뀌어도 맞는 코드를 받기 위한 조건입니다.
"""),
    "pandas": dict(principles=[
        "자료는 `pd.read_csv`·`pd.read_excel`·`pd.read_html`로 읽고, 파일 경로는 문제에 주어진 상대 경로를 그대로 씁니다.",
        "행·열 선택은 `loc`/`iloc`와 불리언 마스크(boolean mask)로 하고, 행 단위 반복문 대신 벡터화 연산을 씁니다.",
        "결측치(NaN)는 `isna().sum()`으로 먼저 세고, 채울 값(중앙값·최빈값)은 명시하며, 원본 표를 바꾸지 않고 결과를 새 변수에 받습니다.",
        "저장은 `to_csv(index=False)`처럼 인덱스 열이 끼어들지 않게 합니다.",
    ], why="""
`loc`, 불리언 마스크, 벡터화, 결측치 같은 pandas 관용 용어를 쓰면 AI는 느린 `for` 루프나 경고가 나는 연쇄 할당(chained assignment) 대신 표준 코드를 내놓습니다. "원본을 바꾸지 않는다"는 조건은 검사기가 원본 표와 결과 표를 둘 다 확인하기 때문에 필요합니다.
"""),
    "eda": dict(principles=[
        "맞히려는 칸인 타깃(target) 열을 먼저 지정하고, 집계는 `groupby(...).agg(['count', 'sum', 'mean'])`처럼 분모(표본 수)를 함께 보고합니다.",
        "비율은 0~1 사이 소수로 계산하고 출력할 때만 퍼센트로 바꿉니다. 반올림은 문제가 요구한 자릿수만 적용합니다.",
        "범주형 열은 `value_counts()`, 수치형 열은 `describe()`로 분포를 먼저 확인한 뒤 집계합니다.",
    ], why="""
탐색 단계의 전문성은 "무엇을 맞힐지"와 "몇 명 중"을 분명히 하는 데 있습니다. 타깃, 분모, 범주형·수치형이라는 말을 쓰면 AI는 비율만 덜렁 내놓지 않고 `count`·`sum`·`mean`을 함께 계산하며, 검사기도 그 세 값을 확인합니다.
"""),
    "visualization": dict(principles=[
        "`fig, ax = plt.subplots()`로 Figure와 Axes를 명시적으로 만들고, 축 이름(`set_xlabel`/`set_ylabel`)과 제목을 붙입니다.",
        "그래프 종류는 질문에 맞춥니다. 범주 비교는 막대그래프, 분포는 히스토그램·박스플롯, 두 수치의 관계는 산점도, 시간 흐름은 선그래프입니다.",
        "`plt.show()`는 호출하되 파일 저장이나 백엔드 설정은 바꾸지 않습니다. 검사기는 Figure 객체의 데이터와 축을 직접 읽습니다.",
    ], why="""
검사기는 그림 파일이 아니라 `fig`·`ax` 객체의 데이터와 축 이름을 읽습니다. 그래서 "Figure·Axes를 명시적으로", "축 이름"이라는 용어가 프롬프트에 있어야 하고, 그래프 종류를 질문 유형과 짝지어 적어야 AI가 엉뚱한 그림을 그리지 않습니다.
"""),
    "modeling": dict(principles=[
        "입력 `X`와 정답 `y`를 분리하고, 사고 이후에만 알 수 있는 열(`boat`, `body`)처럼 타깃 누수(data leakage)를 일으키는 열은 입력에서 제외합니다.",
        "`train_test_split(test_size=0.2, stratify=y, random_state=42)`로 나누고, 전처리 기준(중앙값, 범주 목록)은 훈련 자료에서만 `fit`합니다.",
        "전처리는 `ColumnTransformer`와 `Pipeline`으로 묶습니다. 수치형은 `SimpleImputer(strategy='median')`+`StandardScaler`, 범주형은 `SimpleImputer(strategy='most_frequent')`+`OneHotEncoder(handle_unknown='ignore')`입니다.",
        "모델 점수는 `DummyClassifier(strategy='most_frequent')` 기준선(baseline)과 같은 테스트 자료에서 비교하고, accuracy와 F1을 함께 보고합니다.",
    ], why="""
머신러닝 프롬프트에서 전문가와 초보를 가르는 말은 **누수(leakage)**, **층화 분할(stratify)**, **훈련 자료에서만 fit**, **Pipeline**, **기준선(baseline)**입니다. 이 다섯 용어를 적으면 AI는 테스트 자료로 전처리 기준을 정하거나 기준선 없이 점수만 내놓는 흔한 실수를 피합니다. 검사기도 분리 방식과 기준 비교를 확인합니다.
"""),
    "credit": dict(principles=[
        "타깃은 `default payment next month`이며, 숫자 코드로 적힌 범주형 열(`SEX`, `EDUCATION`, `MARRIAGE`)은 One-hot으로 다루고 고객 번호 `ID`는 입력에서 뺍니다.",
        "클래스 불균형 자료이므로 accuracy만 보지 않고 precision·recall·F1을 함께 보고하며, 확률은 `predict_proba`로 받아 임계값(threshold)을 명시해 분류합니다.",
        "혼동 행렬(confusion matrix)로 거짓 양성·거짓 음성을 구분해 해석하고, 어느 쪽 오류가 더 비싼지 적습니다.",
    ], why="""
부도 예측은 부도가 소수인 **불균형 자료**라 accuracy가 높아도 쓸모없을 수 있습니다. precision·recall·F1, 임계값, 혼동 행렬이라는 용어를 쓰면 AI가 "정확도 78%"에서 멈추지 않고 어떤 오류를 얼마나 내는지까지 계산합니다. 숫자 코드 열을 범주형으로 다루라는 조건은 성별 2가 1보다 크다는 식의 잘못된 규칙을 막습니다.
"""),
    "stock": dict(principles=[
        "날짜를 `parse_dates`로 읽어 인덱스로 올리고 `sort_index()`로 정렬합니다. 시계열은 무작위로 섞지 않고 앞 기간으로 훈련, 뒤 기간으로 테스트합니다(temporal split).",
        "특징(feature)은 과거 값만으로 만듭니다. 수익률 `pct_change()`, 이동평균 `rolling(n).mean()`, 전일 종가 `shift(1)`. 정답은 `shift(-1)`이며 입력에 미래 값이 섞이면 누수입니다.",
        "기준 모델은 '내일 종가 = 오늘 종가'(naive forecast)이고, 회귀 점수는 MAE·RMSE·R²를 같은 테스트 기간에서 비교합니다.",
        "선형 회귀·Ridge·Lasso는 `StandardScaler`와 `Pipeline`으로 묶고, 결과가 기준보다 나빠도 그대로 보고합니다.",
    ], why="""
시계열에서는 **temporal split**, **lag(shift)**, **naive forecast 기준선**이라는 말이 프롬프트의 핵심입니다. 이 용어가 없으면 AI는 `train_test_split`으로 날짜를 섞거나 내일 값을 입력에 넣어 점수를 부풀립니다. "기준보다 나빠도 그대로 보고"는 결과를 고르지 않고 정직하게 비교하라는 조건이며, 검사기는 이기는 모델이 아니라 같은 기간의 정직한 비교를 확인합니다.
"""),
}


def build():
    chapters = []
    for chapter_id, title, modules in OUTLINE:
        units = [importlib.import_module(f"kpc_course.{name}").UNIT for name in modules]
        expertise = EXPERTISE[chapter_id]
        for unit in units:
            for activity in unit["activities"]:
                if activity["kind"] == "coding":
                    activity["problem"]["expertise"] = dict(principles=list(expertise["principles"]), why=expertise["why"].strip())
        chapters.append(dict(id=chapter_id, title=title, units=units))
    return chapters
