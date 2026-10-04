"""3일차 · 2교시 — 수익률·이동평균·lag"""
from kpc_course.dsl import *

UNIT = unit('stock-features', '3일차 · 2교시 — 수익률·이동평균·lag', [
    concept('lag-target', '과거 열은 입력, 미래 열은 정답',
        body="""
        타이타닉에서는 입력 열이 이미 표에 있었습니다. 주가 표에는 종가 하나뿐이라 입력도, 정답도 **우리가 만들어야** 합니다. 재료는 "어제보다 얼마나 올랐나"(수익률), "최근 며칠 평균은 얼마인가"(이동평균), "어제 종가는 얼마였나"(전일 종가)이고, 정답은 "내일 종가는 얼마인가"입니다. 전부 종가 열을 위아래로 밀어서 만듭니다.

        ```interactive
        위젯: moving
        ```

        ```comic-gen
        제목: 위로 밀면 어제, 아래로 밀면 내일
        등장인물:
          준호:
            그림: 사람
            이름표: 준호 · 은행 직원
            외형: {머리색: "#303746", 옷색: "#b88646"}
          파이썬: {그림: 서버, 이름표: Python}
        컷:
          - 인물: [{식별자: 준호, 표정: 어리둥절}, 파이썬]
            대사:
              - {화자: 준호, 상대: 파이썬, 내용: "shift(1)이랑 shift(-1)이 뭐가 달라?"}
              - 화자: 파이썬
                상대: 준호
                내용: |-
                  shift(1)은 어제 값을 오늘 줄로,
                  shift(-1)은 내일 값을 오늘 줄로.
          - 구성: 이전
            인물: [{식별자: 준호, 표정: 보통}, {식별자: 파이썬, 손모양: 가리키는손}]
            대사:
              - {화자: 준호, 상대: 파이썬, 내용: "그럼 내일 값은 정답이네?"}
              - {화자: 파이썬, 상대: 준호, 내용: "응. 그걸 입력에 넣으면 답을 보고 답을 맞히는 누수야."}
        ```

        | 날짜 | 종가 | shift(1) 어제 | shift(-1) 내일 |
        | --- | ---: | ---: | ---: |
        | 1/13 | 54100 | 빈칸 | 53900 |
        | 1/14 | 53900 | 54100 | 53700 |
        | 1/15 | 53700 | 53900 | 54300 |

        `shift(1)`은 열을 **한 칸 아래로** 밉니다. 그러면 각 행에 "어제 종가"가 놓입니다. 첫 행은 어제가 없어 빈칸입니다. `shift(-1)`은 **한 칸 위로** 밀어 각 행에 "내일 종가"를 놓습니다. 마지막 행은 내일이 아직 없어 빈칸입니다. 같은 밀기인데 하나는 과거라 **입력**이 되고, 하나는 미래라 **정답**이 됩니다. 이 둘을 헷갈리면 앞서 배운 누수가 그대로 재현됩니다.

        ```comic-gen
        제목: 한 칸 아래로, 한 칸 위로
        등장인물:
          민지:
            그림: 사람
            이름표: 민지 · 수강생
            외형: {머리모양: 단발, 옷: 후드, 옷색: "#4f8a8b"}
          판다스: {그림: 서버, 이름표: pandas}
        컷:
          - 인물: [{식별자: 민지, 표정: 어리둥절}, 판다스]
            대사:
              - {화자: 민지, 상대: 판다스, 내용: "오늘 행에 어제 종가를 적고 싶어."}
              - {화자: 판다스, 상대: 민지, 내용: "shift(1). 종가 열을 한 칸 아래로 밀면 각 행 옆에 어제 값이 와요."}
          - 구성: 이전
            인물: [{식별자: 민지, 표정: 기쁨}, {식별자: 판다스, 손모양: 가리키는손}]
            대사:
              - {화자: 민지, 상대: 판다스, 내용: "그럼 내일 종가는?"}
              - {화자: 판다스, 상대: 민지, 내용: "shift(-1). 한 칸 위로. 그건 입력이 아니라 정답 열이에요."}
        ```

        ```python
        prices['return_1'] = prices['종가'].pct_change()         # (오늘 - 어제) / 어제
        prices['ma5'] = prices['종가'].rolling(5).mean()          # 오늘 포함 최근 5거래일 평균
        prices['lag_close_1'] = prices['종가'].shift(1)           # 어제 종가 (입력)
        prices['target_next_close'] = prices['종가'].shift(-1)    # 내일 종가 (정답)
        ```

        `pct_change()`는 어제 대비 변화율이라 첫 행이 비고, `rolling(5).mean()`은 5개가 모여야 평균을 낼 수 있어서 처음 네 행이 빕니다. 빈칸이 있는 행은 모델에 넣을 수 없으니 네 열을 다 만든 뒤 `dropna()`로 한 번에 정리합니다. 그러면 앞쪽 몇 행과 마지막 한 행이 빠집니다.

        마지막으로 정답이 **어느 날짜의 값인지**도 표에 적어 둡니다. `target_date` 열입니다. 숫자가 맞아 보여도 하루 어긋난 정답을 쓰고 있으면 다른 문제를 푼 것이고, 다음 단원에서 훈련과 테스트를 나눌 때 이 날짜가 꼭 필요합니다.
        """,
        check=short('종가 열을 한 칸 위로 밀어 각 행에 다음 거래일 종가를 놓는 표현은 `shift(___)`입니다. 괄호 안의 숫자는?', ['-1'],
                    '`shift(-1)`이 다음 행의 값을 가져옵니다. 이것이 정답 열이고, 입력에 넣으면 누수입니다. `shift(1)`은 어제 값이라 입력으로 씁니다.')),
    coding('daily-return', '어제보다 얼마나 올랐나',
        goal="""
        첫 재료입니다. `prices['종가'].pct_change()`를 `return_1` 열로 추가하고 `prices.head()`로 확인하세요.

        첫 행은 어제가 없어 비어 있고, 둘째 행은 (53900 − 54100) / 54100, 약 −0.0037이 나옵니다.
        """,
        hint="""
        새 열은 `prices['return_1'] = prices['종가'].pct_change()`처럼 대괄호에 새 이름을 적어 넣습니다. `pct_change()`가 (오늘 − 어제) / 어제를 행마다 계산합니다.
        """,
        starter=ST + "# return_1 열을 만들고 head()를 확인하세요\n",
        solution=ST + "prices['return_1'] = prices['종가'].pct_change()\nprices.head()\n",
        check="import pandas as pd\nassert pd.isna(s['prices']['return_1'].iloc[0])\nassert abs(s['prices']['return_1'].iloc[1]-(53900/54100-1))<1e-12"),
    coding('moving-average', '최근 5거래일 평균',
        goal="""
        둘째 재료입니다. `prices['종가'].rolling(5).mean()`을 `ma5` 열로 추가하고 `prices.head(6)`으로 확인하세요.

        처음 네 행은 5개가 안 모여 비어 있고, 다섯째 행은 첫 5개 종가의 평균 53940입니다.
        """,
        hint="""
        `rolling(5)`가 "오늘 포함 최근 5행"이라는 창을 만들고 `.mean()`이 그 평균을 냅니다. 창이 다 차지 않은 앞쪽 네 행은 `NaN`입니다.
        """,
        starter=ST + "# ma5 열을 만들고 head(6)을 확인하세요\n",
        solution=ST + "prices['ma5'] = prices['종가'].rolling(5).mean()\nprices.head(6)\n",
        check="assert s['prices']['ma5'].iloc[:4].isna().all()\nassert s['prices']['ma5'].iloc[4]==53940\nassert s['prices']['ma5'].isna().sum()==4"),
    coding('lag-next', '어제 종가와 내일 종가',
        goal="""
        밀기 두 번입니다. `prices['종가'].shift(1)`을 `lag_close_1` 열로, `prices['종가'].shift(-1)`을 `target_next_close` 열로 추가하세요.

        첫 행의 `lag_close_1`과 마지막 행의 `target_next_close`가 비어 있으면 맞게 밀린 것입니다. 둘째 행의 `lag_close_1`은 첫 행 종가 54100입니다.
        """,
        hint="""
        `shift(1)`은 아래로 한 칸(어제 값), `shift(-1)`은 위로 한 칸(내일 값)입니다. 개념의 표를 옆에 두고 `prices.head()`와 `prices.tail()`로 양 끝을 확인해 보세요.
        """,
        starter=ST + "# 두 열을 만드세요\n",
        solution=ST + "prices['lag_close_1']=prices['종가'].shift(1)\nprices['target_next_close']=prices['종가'].shift(-1)\nprices.head()\n",
        check="assert __import__('pandas').isna(s['prices']['lag_close_1'].iloc[0])\nassert s['prices']['lag_close_1'].iloc[1]==54100\nassert s['prices']['target_next_close'].iloc[0]==53900\nassert __import__('pandas').isna(s['prices']['target_next_close'].iloc[-1])"),
    coding('stock-frame', '입력 네 열과 정답, 그리고 정답 날짜',
        goal="""
        재료를 한 표에 모읍니다. 빈 표 `frame`에 `close`(오늘 종가), `return_1`, `ma5`, `lag_close_1`, `target_next_close`, `target_date` 여섯 열을 만드세요. `target_date`는 날짜 인덱스를 `pd.Series(prices.index, index=prices.index)`로 열로 만든 뒤 `shift(-1)`한 것입니다. 마지막에 `frame.dropna().copy()`로 빈칸이 있는 행을 빼세요.

        401행 중 앞 네 행과 마지막 한 행이 빠져 396행 6열이 남습니다. `target_date`가 모든 행에서 인덱스 날짜보다 뒤인지 보세요.
        """,
        hint="""
        네 재료는 앞 미션들 그대로입니다. `frame['close'] = prices['종가']`, `frame['return_1'] = prices['종가'].pct_change()`, `frame['ma5'] = prices['종가'].rolling(5).mean()`, `frame['lag_close_1'] = prices['종가'].shift(1)`, `frame['target_next_close'] = prices['종가'].shift(-1)`, `frame['target_date'] = pd.Series(prices.index, index=prices.index).shift(-1)`. 마지막에 `frame = frame.dropna().copy()`.
        """,
        starter=ST + "frame=pd.DataFrame(index=prices.index)\n# 여섯 열을 만들고 불완전한 행을 제외하세요\n",
        solution=ST_FRAME + "print(frame.shape)\nframe.head()\n",
        check="assert s['frame'].shape==(396,6)\nassert s['frame'].notna().all().all()\nassert (s['frame']['target_date']>s['frame'].index).all()\nassert s['frame']['ma5'].iloc[0]==s['prices']['종가'].iloc[:5].mean()"),
    quiz('feature-time-check', '3일차 2교시 점검',
        choice('`target_next_close`를 입력 `X`에도 넣으면 어떻게 되나요?',
               ['내일 종가로 내일 종가를 맞히는 누수가 된다', '정확도가 조금 오른다', '아무 문제 없다'], 0,
               '정답을 입력에 넣는 것이라 앞서 배운 누수 그대로입니다. 숫자가 거의 완벽하게 맞지만 쓸모없는 모델이 됩니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「조금 오른다」: 거의 완벽하게 맞지만 쓸모없다.\n- 「아무 문제 없다」: 내일 값은 오늘 저녁에 모른다."),
        short('어제 종가를 각 행에 놓는 표현은 `shift(__)`입니다. 괄호 안은?', ['1'],
              '`shift(1)`은 열을 한 칸 아래로 밀어 어제 값을 놓습니다. 과거라서 입력으로 쓸 수 있습니다.'),
        choice('`pct_change()`의 첫 행이 비어 있는 이유는 무엇인가요?',
               ['비교할 어제가 없어서', '계산 오류라서', '첫날은 가격이 0이라서'], 0,
               '변화율은 (오늘 − 어제) / 어제인데 첫 행에는 어제가 없습니다. 빈칸은 나중에 `dropna()`로 정리합니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「첫날 가격이 0」: 가격은 있다. 어제가 없을 뿐.\n- 「계산 오류」: 정상 동작이다."),
        short('`rolling(5).mean()`에서 값이 비는 행은 처음 몇 행인가요?', ['4', '4행', '네'],
              '다섯 개가 모여야 평균을 낼 수 있으니 처음 네 행이 빕니다. 다섯째 행부터 값이 생깁니다.'),
        choice('`target_date` 열을 따로 두는 이유는 무엇인가요?',
               ['정답이 어느 날짜의 값인지 확인하고, 다음 단원에서 훈련·테스트를 나눌 때 쓰려고', '그래프 색을 정하려고', '행 수를 늘리려고'], 0,
               '숫자만 보면 하루 어긋난 정답을 알아채기 어렵습니다. 날짜가 있어야 "훈련의 정답이 테스트 기간을 침범하지 않았는지"도 확인할 수 있습니다.' "\n\n**다른 보기는 왜 아닌가**\n\n- 「그래프 색」: 날짜는 색과 무관하다.\n- 「행 수를 늘리려고」: 열이 늘지 행은 그대로다."),
        choice("""**프롬프트 고르기** · 어제 종가와 내일 종가 열을 만들어야 합니다. 방향을 틀리면 누수가 됩니다. 어떤 프롬프트가 맞을까요?""",
               ["""pandas. prices['종가'].shift(1)을 lag_close_1(어제) 열로, shift(-1)을 target_next_close(내일) 열로 추가. 코드만""", """종가 밀어서 열 두 개 만들어 줘""", """어제랑 내일 종가 열 추가해 줘""", """shift 써서 피처 만들어 줘"""], 0,
               """정답은 shift의 부호와 열 이름, 뜻(어제/내일)을 짝지어 적었습니다. 부호를 틀리면 과거와 미래가 바뀌어 누수가 됩니다.

**다른 보기는 왜 아닌가**

- 「밀어서 열 두 개」: 어느 방향으로 밀지 없다.
- 「어제랑 내일 종가」: 열 이름이 없어 검사기가 못 읽는다.
- 「shift 써서 피처」: 몇 칸, 어느 방향, 무슨 이름인지 없다."""),
        choice("""**프롬프트 고르기** · AI가 입력 `X`에 `target_next_close`도 넣어 MAE가 거의 0이 됐다고 합니다. 바로잡는 프롬프트는 무엇인가요?""",
               ["""target_next_close는 정답이야. 입력에 넣으면 내일 값으로 내일을 맞히는 누수라 점수가 무의미해. feature_columns=['close','return_1','ma5','lag_close_1']만 입력으로 다시 해 줘""", """MAE 0이면 완벽하네. 보고서 써 줘""", """더 넣을 열 없어?""", """점수가 너무 낮은데 이상하지 않아?"""], 0,
               """정답은 어떤 열이 왜 문제인지(정답 열, 누수)를 짚고 쓸 열을 이름으로 지정했습니다.

**다른 보기는 왜 아닌가**

- 「완벽하네」: 누수 결과를 보고하게 된다.
- 「더 넣을 열 없어?」: 누수를 키운다.
- 「이상하지 않아?」: AI가 아니라고 답할 수 있다. 판단은 사람이 한다."""),
    ),
])
