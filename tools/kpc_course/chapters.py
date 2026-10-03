"""The fixed 7-chapter, 20-unit outline. Unit files are named by day and period."""
import importlib

from kpc_course.prompts import PROMPTS

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
        "입력은 `input()` 한 줄씩, 숫자는 `int()`/`float()`로 형 변환.",
        "출력은 `print()`와 f-string으로 요구 형식 그대로. 디버그 출력 금지.",
        "변수 이름은 문제 그대로. 매직 넘버 대신 준비된 변수로 계산.",
        "표 자료는 리스트·딕셔너리 → `pandas.DataFrame`.",
    ], why="""
검사기는 출력을 글자 단위로 비교하고 결과를 변수 이름으로 읽습니다. 형 변환·f-string·변수 이름 유지처럼 모양을 고정하는 말이 있어야 AI가 반올림하거나 설명을 섞거나 이름을 바꾸지 않습니다.
"""),
    "pandas": dict(principles=[
        "읽기는 `read_csv`/`read_excel`/`read_html`, 경로는 문제의 상대 경로 그대로.",
        "행·열 선택은 `loc`/`iloc`와 불리언 마스크. 행 반복문 대신 벡터화.",
        "결측은 `isna().sum()`으로 먼저 세고, 채울 값은 명시. 원본은 바꾸지 않고 새 변수에.",
        "저장은 `to_csv(index=False)`.",
    ], why="""
`loc`, 불리언 마스크, 벡터화, 결측 같은 pandas 용어를 쓰면 AI가 느린 반복문이나 경고 나는 연쇄 할당 대신 표준 코드를 줍니다.
"""),
    "eda": dict(principles=[
        "타깃(target) 열을 먼저 정한다.",
        "집계는 `groupby(...).agg(['count','sum','mean'])`로 분모(인원)를 함께.",
        "비율은 0~1로 계산, 출력할 때만 퍼센트. 반올림은 요구한 자릿수만.",
        "범주형은 `value_counts()`, 수치형은 `describe()`로 분포부터.",
    ], why="""
타깃, 분모, 범주형·수치형이라는 말을 쓰면 AI가 비율만 덜렁 내놓지 않고 count·sum·mean을 함께 계산합니다.
"""),
    "visualization": dict(principles=[
        "`fig, ax = plt.subplots()`로 Figure·Axes를 만들고 `ax.set_xlabel`/`set_ylabel`·제목.",
        "범주 비교는 막대, 분포는 히스토그램·박스플롯, 관계는 산점도, 시간은 선그래프.",
        "`plt.show()`는 호출, 파일 저장·백엔드 변경은 금지. 검사기는 `ax` 객체를 읽는다.",
    ], why="""
검사기는 그림 파일이 아니라 `ax` 객체의 데이터와 축 이름을 읽습니다. 그래서 Figure·Axes 방식과 축 이름이 프롬프트에 있어야 합니다.
"""),
    "modeling": dict(principles=[
        "입력 `X`와 정답 `y`를 분리. 사고 뒤에 적히는 열(`boat`, `body`)은 누수(leakage)라 제외.",
        "`train_test_split(test_size=0.2, stratify=y, random_state=42)`. 전처리 기준은 훈련 자료에서만 `fit`.",
        "전처리는 `ColumnTransformer`+`Pipeline`: 수치형 `SimpleImputer(median)`+`StandardScaler`, 범주형 `SimpleImputer(most_frequent)`+`OneHotEncoder(handle_unknown='ignore')`.",
        "`DummyClassifier(most_frequent)` 기준선과 같은 테스트 자료에서 비교. accuracy와 F1 함께.",
    ], why="""
누수, 층화 분할(stratify), 훈련 자료에서만 fit, Pipeline, 기준선. 이 다섯 말이 테스트 자료로 기준을 정하거나 기준선 없이 점수만 내놓는 실수를 막습니다.
"""),
    "credit": dict(principles=[
        "타깃은 `default payment next month`. 숫자 코드 범주형(`SEX`, `EDUCATION`, `MARRIAGE`)은 One-hot, `ID`는 제외.",
        "불균형 자료: accuracy 외에 precision·recall·F1. 확률은 `predict_proba`, 임계값(threshold) 명시.",
        "혼동 행렬로 거짓 양성·거짓 음성을 구분하고 어느 쪽이 비싼지 적는다.",
    ], why="""
부도는 소수라 accuracy가 높아도 쓸모없을 수 있습니다. precision·recall·F1, 임계값, 혼동 행렬이라는 말이 있어야 AI가 "정확도 78%"에서 멈추지 않습니다.
"""),
    "stock": dict(principles=[
        "`parse_dates`로 읽어 날짜 인덱스, `sort_index()`. 섞지 말고 앞 기간 훈련·뒤 기간 테스트(temporal split).",
        "특징은 과거 값만: `pct_change()`, `rolling(n).mean()`, `shift(1)`. 정답은 `shift(-1)`. 미래 값이 입력에 섞이면 누수.",
        "기준은 '내일 종가 = 오늘 종가'(naive forecast). 점수는 MAE·RMSE·R²를 같은 테스트 기간에서.",
        "선형 회귀·Ridge·Lasso는 `StandardScaler`+`Pipeline`. 기준보다 나빠도 그대로 보고.",
    ], why="""
temporal split, lag(shift), naive forecast 기준선. 이 말이 없으면 AI는 날짜를 섞거나 내일 값을 입력에 넣어 점수를 부풀립니다.
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
                    problem = activity["problem"]
                    problem["expertise"] = dict(principles=list(expertise["principles"]), why=expertise["why"].strip())
                    if problem["id"] not in PROMPTS:
                        raise SystemExit(f"{unit['id']}/{problem['id']}: tools/kpc_course/prompts.py에 인간 버전 프롬프트가 없습니다.")
                    problem["prompt"], problem["prompt_why"] = PROMPTS[problem["id"]]
        chapters.append(dict(id=chapter_id, title=title, units=units))
    return chapters
