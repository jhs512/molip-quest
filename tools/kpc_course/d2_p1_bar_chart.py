"""2일차 · 1교시 — Figure·Axes와 막대그래프"""
from kpc_course.dsl import *

UNIT = unit('bar-chart', '2일차 · 1교시 — Figure·Axes와 막대그래프', [
    concept('axes', '종이 한 장과 그 위의 그래프',
        body="""
        어제 마지막 시간에 성별 생존율 표를 만들었습니다. 숫자 두 개를 비교하는 데는 표로 충분하지만, 그룹이 넷, 여섯으로 늘어나면 눈이 숫자를 따라가지 못합니다. 그래서 오늘은 표를 그림으로 바꿉니다. 둘째 날은 그래프로 시작해서 "누가 살아남았나"를 맞히는 모델로 끝납니다.

        Python에서 그래프를 그리는 도구는 `matplotlib`입니다. 처음 보면 낯선 단어가 둘 나오는데, 비유 하나면 됩니다. `Figure`는 **종이 한 장**이고 `Axes`는 그 종이 위에 그려지는 **그래프 영역 하나**입니다. 종이 한 장에 그래프를 하나만 그릴 수도, 여럿 그릴 수도 있습니다. 우리는 거의 항상 하나만 그리므로 시작은 늘 같은 한 줄입니다.

        ```python
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()          # 종이(fig) 한 장, 그래프 영역(ax) 하나
        ax.bar(['A', 'B', 'C'], [30000, 40000, 60000])   # 막대 그리기
        ax.set(title='Amount by stock', ylabel='Amount')  # 제목과 축 이름
        plt.show()                        # 앱 화면에 표시
        ```

        그리는 명령은 종이가 아니라 **그래프 영역 `ax`**에 붙입니다. `ax.bar(이름들, 값들)`가 막대그래프, `ax.set(...)`이 제목·축 이름·축 범위 지정, 마지막 `plt.show()`가 "다 그렸으니 보여 줘"입니다. 이 네 줄이 오늘 모든 그래프의 뼈대입니다.

        그래프를 그리기 전에 두 가지를 정해 두면 그림이 흔들리지 않습니다. 첫째, **y축이 무엇인가.** 인원인지 비율인지 퍼센트인지에 따라 같은 그림이 다른 말을 합니다. 생존율처럼 0~1 사이의 비율은 100을 곱해 퍼센트로 그리고 y축 범위를 `ylim=(0, 100)`으로 고정하는 것이 읽기 쉽습니다. 둘째, **축을 어디서 시작하는가.** y축을 0이 아니라 60부터 시작하게 자르면 62%와 70%의 차이가 두 배처럼 보입니다. 과장하려는 뜻이 없어도 그렇게 읽힙니다. 비율 막대는 0부터 그리세요.

        축 이름과 제목은 영어로 적습니다. 한글 글꼴이 없는 컴퓨터에서는 한글이 네모로 깨지기 때문입니다.
        """,
        check=short('`matplotlib`에서 종이 한 장에 해당하는 전체 그림 객체의 이름은 무엇인가요? (`fig, ax = plt.subplots()`의 `fig`)', ['Figure', 'figure', '피겨'],
                    '`Figure`가 종이 한 장, `Axes`가 그 위의 그래프 영역입니다. 막대나 선은 `ax`에 그립니다.')),
    coding('simple-bar', '리스트로 첫 막대그래프',
        goal="""
        어제 종목 세 개의 금액으로 첫 막대그래프를 그립니다. `fig, ax = plt.subplots()`로 종이와 그래프 영역을 만들고, `ax.bar(names, amounts)`로 막대를 그린 뒤, `ax.set(title='Amount by stock', ylabel='Amount')`로 제목과 y축 이름을 붙이고 `plt.show()`로 띄우세요.

        막대 세 개가 30000, 40000, 60000 높이로 보이면 맞게 한 것입니다.
        """,
        hint="""
        개념의 네 줄 그대로입니다. 순서는 `subplots` → `bar` → `set` → `show`. `ax.set()`의 괄호 안에 `title=`, `ylabel=`을 쉼표로 나란히 적습니다.
        """,
        starter="import matplotlib.pyplot as plt\nnames = ['A', 'B', 'C']\namounts = [30000, 40000, 60000]\n# fig, ax를 만들고 막대그래프를 그리세요\n",
        solution="import matplotlib.pyplot as plt\nnames = ['A', 'B', 'C']\namounts = [30000, 40000, 60000]\nfig, ax = plt.subplots()\nax.bar(names, amounts)\nax.set(title='Amount by stock', ylabel='Amount')\nplt.show()\n",
        check="assert len(s['ax'].patches)==3\nassert [p.get_height() for p in s['ax'].patches]==[30000,40000,60000]\nassert s['ax'].get_ylabel()=='Amount'"),
    coding('sex-bar', '성별 생존율을 퍼센트로 그리기',
        goal="""
        어제의 성별 생존율 표를 그림으로 바꿉니다. `rates`에 성별 `survived` 평균을 저장하고, `rates * 100`을 막대로 그리세요. y축 범위는 `ylim=(0, 100)`, x축 이름은 `Sex`, y축 이름은 `Survival rate (%)`로 지정하고 `plt.show()`로 띄웁니다.

        막대 두 개가 각각 여성·남성 생존율 퍼센트 높이로 보이면 맞게 한 것입니다.
        """,
        hint="""
        `rates = titanic.groupby('gender')['survived'].mean()`은 어제와 같습니다. `ax.bar(rates.index, rates * 100)`로 그리고 `ax.set(xlabel='Sex', ylabel='Survival rate (%)', ylim=(0, 100), title='Survival by gender')`로 꾸미세요.
        """,
        starter=TI + PLOT + "# rates, fig, ax를 만들고 막대그래프를 그리세요\n",
        solution=TI + PLOT + "rates=titanic.groupby('gender')['survived'].mean()\nfig,ax=plt.subplots()\nax.bar(rates.index,rates*100)\nax.set(xlabel='Sex',ylabel='Survival rate (%)',ylim=(0,100),title='Survival by gender')\nplt.show()\n",
        check="assert len(s['ax'].patches)==2\nassert s['ax'].get_ylim()==(0.0,100.0)\nassert s['ax'].get_ylabel()=='Survival rate (%)'\nassert s['ax'].get_xlabel()=='Sex'\nheights = {label.get_text(): bar.get_height() for label,bar in zip(s['ax'].get_xticklabels(),s['ax'].patches)}\nassert set(heights)=={'female','male'}\nassert abs(heights['female']-339/466*100)<1e-8\nassert abs(heights['male']-161/843*100)<1e-8"),
    coding('pclass-bar', '등급별 생존율 막대그래프',
        goal="""
        같은 그림을 객실 등급으로 그립니다. `rates`에 등급별 `survived` 평균을 저장하고 `rates * 100`을 막대로 그리세요. y축 범위 0~100, x축 이름 `Pclass`, y축 이름 `Survival rate (%)`입니다.

        막대 세 개가 1등급에서 3등급으로 갈수록 낮아지는지 보세요.
        """,
        hint="""
        성별 그래프에서 `groupby('gender')`를 `groupby('pclass')`로 바꾸면 됩니다. 등급 1·2·3이 숫자라 x축 간격이 어색하면 `ax.bar(rates.index.astype(str), rates * 100)`처럼 글자로 바꿔 넘기세요.
        """,
        starter=TI + PLOT + "# rates, fig, ax를 만들고 막대그래프를 그리세요\n",
        solution=TI + PLOT + "rates = titanic.groupby('pclass')['survived'].mean()\nfig, ax = plt.subplots()\nax.bar(rates.index.astype(str), rates * 100)\nax.set(xlabel='Pclass', ylabel='Survival rate (%)', ylim=(0, 100), title='Survival by class')\nplt.show()\n",
        check="assert len(s['ax'].patches)==3\nassert s['ax'].get_ylim()==(0.0,100.0) and s['ax'].get_xlabel()=='Pclass'\nheights=sorted(p.get_height() for p in s['ax'].patches)\nassert abs(heights[0]-181/709*100)<1e-8 and abs(heights[2]-200/323*100)<1e-8"),
    quiz('bar-check', '2일차 1교시 점검',
        short('종이 위에서 실제로 그래프가 그려지는 영역, `fig, ax = plt.subplots()`의 `ax`를 부르는 이름은 무엇인가요?', ['Axes', 'axes', '축 영역'],
              '`Axes`가 그래프 영역입니다. 막대·선·축 이름은 전부 `ax`에 붙입니다.'),
        choice('`fig, ax = plt.subplots()` 다음에 막대를 그리는 명령은 어느 것인가요?',
               ['`ax.bar(...)`', '`fig.bar(...)`', '`plt.subplots.bar(...)`'], 0,
               '그리는 명령은 그래프 영역 `ax`에 붙입니다. `fig`는 종이라서 그 자체에는 막대를 그리지 않습니다.'),
        choice('생존율 0.4를 퍼센트 막대로 그리려면 어떤 값을 넘기나요?',
               ['`0.4 * 100`, 즉 40', '`0.4` 그대로', '`0.4 / 100`'], 0,
               '비율에 100을 곱하면 퍼센트입니다. y축 범위도 0~100으로 맞춰야 막대 높이가 퍼센트로 읽힙니다.'),
        choice('y축을 0이 아니라 60부터 시작하도록 자르면 어떤 일이 생기나요?',
               ['작은 차이가 크게 보여 과장된다', '그림이 더 정확해진다', '막대가 사라진다'], 0,
               '62%와 70%의 막대 높이 차이가 몇 배로 보이게 됩니다. 비율 막대는 0부터 그리는 것이 안전합니다.'),
        short('다 그린 그래프를 앱 화면에 띄우는 마지막 명령은 무엇인가요?', ['plt.show()', 'plt.show', 'show()'],
              '`plt.show()`가 "보여 줘"입니다. 이 줄이 없으면 그래프가 화면에 나오지 않습니다.'),
        choice('막대그래프를 보고 "여성 생존율이 두 배 높다"고 말하기 전에 먼저 확인할 것은 무엇인가요?',
               ['y축이 퍼센트인지 인원인지, 그리고 각 그룹이 몇 명인지', '막대 색이 예쁜지', '제목이 영어인지'], 0,
               '같은 높이 차이도 y축 단위에 따라 뜻이 다르고, 분모가 작은 그룹의 비율은 흔들립니다. 어제 배운 "몇 명 중"이 그림에서도 그대로 적용됩니다.'),
    ),
])
