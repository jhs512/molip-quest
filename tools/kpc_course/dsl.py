"""Authoring vocabulary for the KPC course. Each unit file builds one `UNIT` with these helpers.

Text is written as Markdown by hand; nothing is auto-formatted. Multiple-choice options are
shuffled deterministically so the correct answer does not always sit in the first slot.
"""
import random
import re
import textwrap

# Reference answers collected while units are built; written to courses/kpc-solutions.json.
SOLUTIONS = {}

REVISION = 4

# Shared preparation code. Every problem is independent, so these are repeated per problem.
PD = "import pandas as pd\n"
TI = PD + "titanic = pd.read_csv('data/titanic.csv')\n"
CR = PD + "credit = pd.read_csv('data/credit.csv')\ntarget = '다음달 부도'\n"
ST = PD + "prices = pd.read_csv('data/stock.csv', parse_dates=['날짜']).set_index('날짜').sort_index()\n"
ORDERS = PD + "orders = pd.DataFrame({'product':['A','B','A','C'], 'price':[10000,20000,12000,None], 'quantity':[3,2,4,1]})\n"
PLOT = "import matplotlib.pyplot as plt\nimport seaborn as sns\n"
FEATURES = "features=['객실등급','성별','나이','형제배우자','부모자녀','요금','탑승항구']\nX=titanic[features].copy()\ny=titanic['생존'].astype(int)\n"
SPLIT = "from sklearn.model_selection import train_test_split\nX_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)\n"
PREP = "from sklearn.compose import ColumnTransformer\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import OneHotEncoder,StandardScaler\ndef make_preprocessor():\n    return ColumnTransformer([('numeric',Pipeline([('fill',SimpleImputer(strategy='median')),('scale',StandardScaler())]),['객실등급','나이','형제배우자','부모자녀','요금']),('category',Pipeline([('fill',SimpleImputer(strategy='most_frequent')),('encode',OneHotEncoder(handle_unknown='ignore'))]),['성별','탑승항구'])])\n"
ST_FRAME = ST + "frame=pd.DataFrame(index=prices.index)\nframe['close']=prices['종가']\nframe['return_1']=prices['종가'].pct_change()\nframe['ma5']=prices['종가'].rolling(5).mean()\nframe['lag_close_1']=prices['종가'].shift(1)\nframe['target_next_close']=prices['종가'].shift(-1)\nframe['target_date']=pd.Series(prices.index,index=prices.index).shift(-1)\nframe=frame.dropna().copy()\n"
TIME_SPLIT = "feature_columns=['close','return_1','ma5','lag_close_1']\nX=frame[feature_columns]\ny=frame['target_next_close']\ntest_start=frame.index[-80]\ntrain_mask=(frame.index<test_start)&(frame['target_date']<test_start)\ntest_mask=frame.index>=test_start\nX_train,X_test=X.loc[train_mask],X.loc[test_mask]\ny_train,y_test=y.loc[train_mask],y.loc[test_mask]\n"
REG = "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LinearRegression,Ridge,Lasso\nfrom sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score\n"

CHECKER_HEAD = (
    "import matplotlib\nmatplotlib.use('Agg')\nimport runpy, sys\n"
    "try:\n    s = runpy.run_path(sys.argv[1])\nexcept Exception as error:\n"
    "    raise AssertionError('작성한 코드가 실행되지 않았습니다. 실행 결과를 확인하세요.') from error\n"
)
CHECKER_TAIL = (
    "\nexcept (KeyError,TypeError,AttributeError,ValueError,IndexError) as error:\n"
    "    raise AssertionError('결과 변수의 값과 자료형을 확인하세요.') from error\nprint('미션 검사 통과')\n"
)


def text(value):
    """Triple-quoted prose: drop common indentation and surrounding blank lines."""
    return textwrap.dedent(value).strip()


def short(prompt, accepted, explanation):
    return dict(prompt=text(prompt), type="short_answer", accepted=list(accepted), explanation=text(explanation))


def choice(prompt, options, correct, explanation):
    """`correct` is the index in the author's order; quiz() shuffles the options later."""
    return dict(prompt=text(prompt), type="choice", options=[text(o) for o in options], correct=correct, explanation=text(explanation))


def io(input, expected):
    return dict(input=input, expected=expected)


def concept(id, title, body, check):
    return dict(id=id, title=title, kind="concept", body=text(body), check=dict(check, id="check"))


def coding(id, title, goal, hint, starter, solution, check=None, tests=None, intro=None):
    """A standalone main.py problem. `check` is assertion source over `s` (the student's globals)."""
    content = ""
    if intro:
        content += "### 문제에서 필요한 설명\n\n" + text(intro) + "\n\n"
    content += "### 목표\n\n" + text(goal) + "\n\n### 힌트\n\n" + text(hint)
    problem = dict(id=id, title=title, content=content, starter_code=starter)
    if check:
        assertions = text(check)
        required = sorted(set(re.findall(r"\bs\[['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]\]", assertions)))
        body = "\n".join("    " + line for line in assertions.splitlines())
        problem["checker"] = (
            CHECKER_HEAD
            + f"assert set({required!r}).issubset(s), '문제에서 요청한 결과 변수를 준비하세요.'\n"
            + "try:\n" + body + CHECKER_TAIL
        )
    else:
        problem["tests"] = list(tests)
    SOLUTIONS[id] = solution
    return dict(id=id, title=title, kind="coding", problem=problem)


def challenge(id, title, **kwargs):
    """A chapter capstone: a coding problem that needs everything the chapter taught."""
    activity = coding(id, '★ 도전 과제 · ' + title, **kwargs)
    activity["challenge"] = True
    return activity


def quiz(id, title, *questions):
    shuffled = []
    for index, question in enumerate(questions):
        question = dict(question, id=f"q{index + 1}")
        if question["type"] == "choice":
            order = list(range(len(question["options"])))
            random.Random(f"{id}:{index}").shuffle(order)
            question["options"] = [question["options"][i] for i in order]
            question["correct"] = order.index(question["correct"])
        shuffled.append(question)
    return dict(id=id, title=title, kind="quiz", questions=shuffled)


def unit(id, title, activities):
    return dict(id=id, title=title, content="", revision=REVISION, activities=list(activities))
