# 1차 조사 결과 · pandas

조사자가 찾은 이상한 곳이에요. 예시 fix는 참고용이고, 같은 목소리로 더 낫게 써도 돼요. 미션마다 severity(0~3).


## d1_p4_files.py (9 missions)


### file-table · concept · severity 2
- 메모: 본문 4문단 + 코드 1 + 만화 1. 네 문단 모두 끝이 '~것이 핵심/보통/미션입니다'라는 명사형 마무리예요. narration anchor 6개(문장 4, 만화 제목 1, 코드 1).
- [long] 전: 거래 내역은 Excel로 오고, 주가는 CSV로 내려받고, 설문 결과는 또 다른 CSV입니다.
  후: 거래 내역은 Excel로 와요. 주가는 CSV로 내려받죠. 설문 결과는 또 다른 CSV고요.
- [long] 전: Excel 파일(.xlsx)은 시트와 서식이 있는 문서라서 더 복잡하지만, `pandas`로 읽으면 둘 다 똑같은 `DataFrame`이 됩니다.
  후: Excel 파일(.xlsx)은 시트와 서식이 있어서 더 복잡해요. 그래도 `pandas`로 읽으면 둘 다 똑같은 `DataFrame`이 돼요.
- [stiff] 전: 어디서 왔든 표가 된 다음부터는 다루는 법이 같다는 것이 핵심입니다.
  후: 어디서 왔든 표가 된 다음부터는 다루는 법이 같아요. 이게 핵심이에요.
- [long] 전: `DataFrame`은 행마다 0, 1, 2… 번호(인덱스)를 달고 있는데, 이 번호를 파일에 함께 적으면 다시 읽을 때 "이름 없는 열"이 하나 더 생겨 버립니다.
  후: `DataFrame`은 행마다 0, 1, 2… 번호(인덱스)를 달고 있어요. 이 번호를 파일에 같이 적으면요? 다시 읽을 때 "이름 없는 열"이 하나 더 생겨 버려요.
- [stiff] 전: 번호는 데이터가 아니니 빼고 저장하는 것이 보통입니다.
  후: 번호는 데이터가 아니니 보통 빼고 저장해요.
- [long] 전: `df.head()`로 앞 5행을 훑어보고, `df.shape`로 몇 행 몇 열인지 세고, `df.columns`로 열 이름을 확인합니다.
  후: `df.head()`로 앞 5행을 훑어요. `df.shape`로 몇 행 몇 열인지 세요. `df.columns`로 열 이름을 확인하고요.
- [long] 전: 열은 `df['price']`처럼 이름으로, 행은 `df.iloc[:2]`처럼 자리 번호로, 또는 `df.loc[조건]`처럼 조건으로 고릅니다.
  후: 열은 `df['price']`처럼 이름으로 골라요. 행은 `df.iloc[:2]`처럼 자리 번호로 고르거나, `df.loc[조건]`처럼 조건으로 골라요.
- [stiff] 전: 이 단원의 미션은 이 동작들을 하나씩 해 보는 것입니다.
  후: 이 단원 미션에서 이 동작들을 하나씩 해 봐요.

### inspect-frame · coding · severity 1
- [long] 전: 행 수를 `n_rows`, 열 수를 `n_columns`, 열 이름 리스트를 `column_names`에 저장하고 세 값을 출력하세요.
  후: 행 수는 `n_rows`, 열 수는 `n_columns`에 담으세요. 열 이름 리스트는 `column_names`에요. 세 값을 출력하면 돼요.
- [unclear] 전: 4행 3열이고 열 이름은 `product`, `price`, `quantity`입니다.
  후: 4행 3열, 열 이름이 `product`, `price`, `quantity`로 나오면 맞아요. (다른 미션처럼 '~면 맞아요' 꼴로 통일)
- [long] 전: `orders.shape`는 `(4, 3)` 같은 쌍이라 `n_rows, n_columns = orders.shape`로 한 번에 두 변수에 나눠 담을 수 있습니다.
  후: `orders.shape`는 `(4, 3)` 같은 쌍이에요. 그래서 `n_rows, n_columns = orders.shape`로 두 변수에 한 번에 나눠 담을 수 있어요.

### to-csv · coding · severity 1
- [stiff] 전: 저장할 때 `index=False`를 꼭 붙입니다.
  후: 저장할 때 `index=False`를 꼭 붙이세요.
- [long] 전: `index=False`를 빼면 `Unnamed: 0`이라는 열이 하나 더 생겨 열 수가 4가 됩니다.
  후: `index=False`를 빼면 `Unnamed: 0`이라는 열이 하나 더 생겨요. 그러면 열 수가 4가 돼요.
- [stiff] 전: 다시 읽은 표가 원래처럼 4행 3열이고 열 이름이 같으면 맞게 한 것입니다.
  후: 다시 읽은 표가 원래처럼 4행 3열이고 열 이름도 같으면 맞게 한 거예요. (세 파일의 모든 코딩 미션에 같은 고정구가 있어요)

### csv-excel · coding · severity 1
- [long] 전: 같은 표를 CSV와 Excel 두 형식으로 저장하고 각각 다시 읽어 `csv_df`, `excel_df`에 저장하세요.
  후: 같은 표를 CSV와 Excel 두 형식으로 저장하세요. 각각 다시 읽어 `csv_df`, `excel_df`에 담으세요.
- [stiff] 전: 파일 형식이 달라도 읽고 나면 같은 `DataFrame`이라는 것을 확인하는 미션입니다.
  후: 파일 형식이 달라도 읽고 나면 같은 `DataFrame`이에요. 그걸 눈으로 확인하는 미션이에요.
- [long] 전: 저장은 `orders.to_csv('orders.csv', index=False)`와 `orders.to_excel('orders.xlsx', index=False)`, 읽기는 `pd.read_csv('orders.csv')`와 `pd.read_excel('orders.xlsx')`입니다.
  후: 저장은 `orders.to_csv('orders.csv', index=False)`와 `orders.to_excel('orders.xlsx', index=False)`예요. 읽기는 `pd.read_csv('orders.csv')`와 `pd.read_excel('orders.xlsx')`고요.

### series-vs-frame · coding · severity 2
- 메모: 목표 둘째 문단이 개념 설명인데 세 문장 모두 45자를 훌쩍 넘어요.
- [long] 전: `orders['price']`를 `price_series`에, `orders[['price']]`를 `price_frame`에 저장하고 각각 `type()`을 출력해 보세요.
  후: `orders['price']`를 `price_series`에 담으세요. `orders[['price']]`는 `price_frame`에요. 각각 `type()`을 출력해 보세요.
- [long] 전: 대괄호 한 겹은 **열 하나**를 세로줄 하나로 꺼내는 것이고, 두 겹은 "이 이름들의 열로 된 **표**를 달라"는 뜻입니다.
  후: 대괄호 한 겹은 **열 하나**를 세로줄 하나로 꺼내요. 두 겹은 "이 이름들의 열로 된 **표**를 달라"는 뜻이에요.
- [long] 전: 앞으로 `.sum()`, `.mean()`처럼 열 하나에 계산할 때는 한 겹, 열 여러 개를 골라 표로 쓸 때는 두 겹을 씁니다.
  후: 앞으로 `.sum()`, `.mean()`처럼 열 하나에 계산할 때는 한 겹이에요. 열 여러 개를 골라 표로 쓸 때는 두 겹이고요.
- [long] 전: `orders['price']`는 한 열인 `Series`, `orders[['price']]`는 열 이름 리스트를 넣은 것이라 `DataFrame`입니다.
  후: `orders['price']`는 열 하나라 `Series`예요. `orders[['price']]`는 열 이름 리스트를 넣은 거라 `DataFrame`이고요.

### selection · coding · severity 1
- [long] 전: `product`와 `price` 두 열만 고른 표를 `selected`에, 자리 번호로 첫 두 행만 고른 표를 `first_two`에 저장하세요.
  후: `product`와 `price` 두 열만 고른 표를 `selected`에 담으세요. 자리 번호로 첫 두 행만 고른 표는 `first_two`에요.
- [long] 전: 리스트와 같은 규칙이라 끝 번호 2는 포함되지 않아 0번과 1번 행만 남습니다.
  후: 리스트와 같은 규칙이에요. 끝 번호 2는 안 들어가니 0번과 1번 행만 남아요.

### loc-condition · coding · severity 1
- [long] 전: 수량이 3 이상인 거래만 골라 `many`에 저장하고 마지막 줄에 `many`를 적어 표를 확인하세요.
  후: 수량이 3 이상인 거래만 골라 `many`에 담으세요. 마지막 줄에 `many`를 적어 표를 확인하세요.
- [stiff] 전: 앞 단원의 `if`가 표 전체에 한꺼번에 적용되는 셈입니다.
  후: 앞 단원의 `if`가 표 전체에 한꺼번에 걸리는 셈이에요.

### read-csv-titanic · coding · severity 1
- [long] 전: 앱이 준비해 둔 `data/titanic.csv`를 읽어 `titanic`에 저장하고, `titanic.shape`를 출력한 뒤 마지막 줄에 `titanic.head()`를 적어 앞 5행을 보세요.
  후: 앱이 준비해 둔 `data/titanic.csv`를 읽어 `titanic`에 담으세요. `titanic.shape`를 출력하세요. 마지막 줄에 `titanic.head()`를 적어 앞 5행을 보세요.
- [long] 전: `pd.read_csv('data/titanic.csv')`처럼 파일 경로를 따옴표로 감싸 넘기고 결과를 `titanic`에 저장하세요.
  후: `pd.read_csv('data/titanic.csv')`처럼 파일 경로를 따옴표로 감싸 넘기세요. 결과는 `titanic`에 담아요.
- [long] 전: 자료는 `data/` 폴더 안에 있어서 경로의 `data/`를 빼면 파일을 찾지 못합니다.
  후: 자료는 `data/` 폴더 안에 있어요. 경로에서 `data/`를 빼면 파일을 못 찾아요.

### files-check · quiz · severity 1
- 메모: 문항 8개(choice 6, short 1, 프롬프트 고르기 2). 「다른 보기는 왜 아닌가」 블록은 '...' "\n\n**..." 문자열 이어붙이기라 따옴표 종류가 섞여 있어요.
- [filler] 전: `iloc`은 자리 번호 전용이고, 마지막 보기는 문법 자체가 틀렸습니다.
  후: 해설 첫 줄은 "조건으로 고를 때는 `loc`이에요."까지만 두세요. 다른 보기 설명은 바로 아래 「다른 보기는 왜 아닌가」가 한 번 더 하거든요.
- [fact] 전: - 「orders['quantity' >= 2]」: 글자와 숫자를 비교하는 문법 오류다.
  후: - 「orders['quantity' >= 2]」: 글자 'quantity'와 숫자 2를 먼저 비교하게 돼서 오류가 나요. 열을 먼저 꺼내고 비교해야 해요. (문법은 맞고 실행 중 TypeError가 나요)
- [unclear] 전: 두 결과의 변수 이름이 검사 조건입니다.
  후: 검사는 두 결과의 변수 이름을 봐요.

## d1_p5_missing.py (8 missions)


### missing-values · concept · severity 2
- 메모: 본문 4문단 + 코드 2 + 만화 2. 셋째 문단에 '두 가지 길'과 '원본은 그대로' 두 생각이 들어 있고, 넷째 문단은 결측에서 조건 필터로 주제가 바뀌는데 다리 문장이 어색해요. anchor 8개(문장 4, 만화 제목 2, 코드 2).
- [long] 전: 표에서 비어 있는 칸을 결측(missing)이라고 부르고, `pandas`는 그 자리에 `NaN`이라고 표시합니다.
  후: 표에서 비어 있는 칸을 결측(missing)이라고 불러요. `pandas`는 그 자리에 `NaN`이라고 표시해요.
- [long] 전: 결측과 0을 혼동하면 평균이 엉뚱하게 낮아지고, 그 평균으로 한 모든 계산이 같이 틀어집니다.
  후: 결측과 0을 섞으면 평균이 엉뚱하게 내려가요. 그 평균으로 한 계산도 전부 같이 틀어져요.
- [long] 전: `isna()`는 빈 칸을 `True`로 표시한 표를 돌려주고, 거기에 `.sum()`을 붙이면 열마다 `True`의 개수, 즉 결측 개수가 나옵니다.
  후: `isna()`는 빈 칸을 `True`로 표시한 표를 돌려줘요. 거기에 `.sum()`을 붙이면 열마다 `True`의 개수가 나와요. 그게 결측 개수예요.
- [long] 전: 어느 쪽이 옳은지는 상황마다 다르고, 두 선택의 결과가 얼마나 달라지는지는 이 단원 마지막 미션에서 직접 보게 됩니다.
  후: 어느 쪽이 옳은지는 상황마다 달라요. 두 선택의 결과가 얼마나 달라지는지는 이 단원 마지막 미션에서 직접 봐요.
- [stiff] 전: 한 가지 주의할 점은 `fillna`와 `dropna`가 **새 표를 돌려줄 뿐 원본은 그대로**라는 것입니다.
  후: 하나 조심할 게 있어요. `fillna`와 `dropna`는 **새 표를 돌려줄 뿐 원본은 그대로**예요. (이 문장부터 새 문단으로 떼면 생각이 둘로 나뉘어요)
- [unclear] 전: 조건으로 행을 고르는 일도 한 단계 늘어납니다.
  후: 조건으로 행 고르기도 한 단계 더 나가요. (결측 얘기에서 조건 얘기로 넘어가는 자리라 한 줄 다리가 필요해요)
- [long] 전: 앞 단원에서는 조건이 하나였지만, "가격이 12000 이상**이고** 수량이 2 이상"처럼 둘을 합칠 때는 각 조건을 괄호로 감싸고 `&`(그리고)로 잇습니다.
  후: 앞 단원에서는 조건이 하나였죠? "가격이 12000 이상**이고** 수량이 2 이상"처럼 둘을 합칠 때가 있어요. 그러면 각 조건을 괄호로 감싸고 `&`(그리고)로 이어요.
- [stiff] 전: 비어 있는 칸은 결측(missing)이며 `pandas`는 `NaN`으로 표시합니다.
  후: 비어 있는 칸은 결측(missing)이에요. `pandas`는 `NaN`으로 표시해요.

### count-missing · coding · severity 1
- [long] 전: `orders`에서 열마다 빈 칸이 몇 개인지 `orders.isna().sum()`으로 구해 `missing_counts`에 저장하세요.
  후: `orders`에서 열마다 빈 칸이 몇 개인지 세요. `orders.isna().sum()`의 결과를 `missing_counts`에 담으면 돼요.
- [long] 전: 결과는 열 이름으로 꺼내는 `Series`라서 `missing_counts['price']`로 가격 열 값을 꺼내고 `int()`로 감싸세요.
  후: 결과는 열 이름으로 꺼내는 `Series`예요. `missing_counts['price']`로 가격 열 값을 꺼내고 `int()`로 감싸세요.

### fill-median · coding · severity 1
- [long] 전: `orders['price']`의 중앙값을 `median_price`에 저장하고, 빈 칸을 그 값으로 채운 열을 `filled_price`에 저장해 둘 다 출력하세요.
  후: `orders['price']`의 중앙값을 `median_price`에 담으세요. 빈 칸을 그 값으로 채운 열은 `filled_price`에요. 둘 다 출력하세요.
- [stiff] 전: 원본 `orders`는 건드리지 않습니다.
  후: 원본 `orders`는 건드리지 마세요.
- [long] 전: `orders['price'].fillna(median_price)`는 빈 칸만 그 값으로 바꾼 **새** 열을 돌려주고 원본은 그대로 둡니다.
  후: `orders['price'].fillna(median_price)`는 빈 칸만 그 값으로 바꾼 **새** 열을 돌려줘요. 원본은 그대로예요.

### drop-missing · coding · severity 1
- [long] 전: 가격이 비어 있는 행을 제외한 표를 `dropped`에 저장하고, 남은 행 수를 `n_left`에 담아 출력하세요.
  후: 가격이 빈 행을 뺀 표를 `dropped`에 담으세요. 남은 행 수는 `n_left`에 담아 출력하세요.
- [long] 전: `subset`을 빼고 `orders.dropna()`라고 쓰면 어느 열이든 빈 행을 전부 빼는데, 이 표에서는 결과가 같지만 열이 많은 표에서는 크게 달라집니다.
  후: `subset`을 빼고 `orders.dropna()`라고 쓰면 어느 열이든 빈 행을 전부 빼요. 이 표에서는 결과가 같아요. 열이 많은 표에서는 크게 달라지고요.

### filter-orders · coding · severity 1
- [long] 전: 열은 `product`, `price`, `quantity` 세 개를 유지하고, 뒤에서 수정해도 원본이 안 바뀌도록 `.copy()`를 붙입니다.
  후: 열은 `product`, `price`, `quantity` 세 개를 그대로 두세요. 뒤에서 고쳐도 원본이 안 바뀌게 `.copy()`를 붙이세요.
- [unclear] 전: 가격이 빈 C는 비교 자체가 안 되어 빠집니다.
  후: 가격이 빈 C는 `NaN`이라 조건이 거짓이 돼서 빠져요.
- [long] 전: `orders.loc[조건, ['product', 'price', 'quantity']].copy()`처럼 `loc`의 쉼표 뒤에 열 이름 리스트를 넣으면 행과 열을 한 번에 고릅니다.
  후: `loc`의 쉼표 뒤에 열 이름 리스트를 넣으면 행과 열을 한 번에 골라요. `orders.loc[조건, ['product', 'price', 'quantity']].copy()`처럼요.

### or-filter · coding · severity 1
- [long] 전: 제품이 A**이거나** 수량이 1인 거래를 `either`에 저장하고 마지막 줄에 `either`를 적어 확인하세요.
  후: 제품이 A**이거나** 수량이 1인 거래를 `either`에 담으세요. 마지막 줄에 `either`를 적어 확인하세요.
- [long] 전: 괄호가 없으면 Python이 `'A' | orders['quantity']`를 먼저 계산하려다 오류를 냅니다.
  후: 괄호가 없으면 파이썬이 `'A' | orders['quantity']`를 먼저 계산하려고 해요. 그래서 오류가 나요.

### missing-totals · coding · severity 2
- 메모: 힌트가 정답 코드를 두 문장에 통째로 넣었고, `['amount'] = ['price'] * ['quantity']`는 실제로 돌지 않는 반쪽 코드라 학생이 그대로 칠 수 있어요.
- [long] 전: `filled`는 가격 결측을 중앙값으로 채운 표, `dropped`는 가격이 빈 행을 뺀 표입니다.
  후: `filled`는 가격 결측을 중앙값으로 채운 표예요. `dropped`는 가격이 빈 행을 뺀 표고요.
- [long] 전: 각 표에 가격 × 수량 열 `amount`를 만들고, 합계를 `filled_total`과 `dropped_total`에 저장해 둘 다 출력하세요.
  후: 각 표에 가격 × 수량 열 `amount`를 만드세요. 합계는 `filled_total`과 `dropped_total`에 담아 둘 다 출력하세요.
- [stiff] 전: 빈 칸 하나를 어떻게 다루기로 했는지에 따라 답이 달라진다는 것, 그래서 보고서에는 그 선택을 적어야 한다는 것이 이 미션의 요점입니다.
  후: 빈 칸 하나를 어떻게 다루느냐에 따라 답이 달라져요. 그래서 보고서에는 그 선택을 적어야 해요. 이게 이 미션의 요점이에요.
- [long] 전: `filled = orders.copy()`를 만든 뒤 `filled['price'] = filled['price'].fillna(filled['price'].median())`로 채우고, `dropped = orders.dropna(subset=['price']).copy()`로 뺀 표를 만드세요.
  후: `filled = orders.copy()`를 먼저 만드세요. `filled['price'] = filled['price'].fillna(filled['price'].median())`로 채워요. 뺀 표는 `dropped = orders.dropna(subset=['price']).copy()`예요.
- [unclear] 전: 두 표 각각 `['amount'] = ['price'] * ['quantity']`를 만들고 `['amount'].sum()`으로 합계를 구합니다.
  후: 두 표 각각 `amount` 열을 가격 × 수량으로 만들어요. `filled['amount'] = filled['price'] * filled['quantity']`처럼요. 합계는 `filled['amount'].sum()`처럼 구해요.

### missing-check · quiz · severity 1
- 메모: 문항 8개(choice 5, short 2, 프롬프트 고르기 2). 괄호 문항 해설 원문은 `orders[\'quantity\']`처럼 따옴표가 이스케이프돼 있어요.
- [long] 전: Python은 `&`를 `>=`보다 먼저 계산하려고 해서 `12000 & orders['quantity']`부터 시도하다 오류를 냅니다.
  후: 파이썬은 `&`를 `>=`보다 먼저 계산해요. 그래서 `12000 & orders['quantity']`부터 시도하다 오류를 내요. 조건마다 괄호를 치세요.
- [long] 전: 정답은 어느 열, 어떤 값으로, 결과를 어디에, 그리고 "원본은 바꾸지 마"라는 제약까지 있습니다.
  후: 정답에는 어느 열을 어떤 값으로 채워 어디에 담을지가 있어요. "원본은 바꾸지 마"라는 제약까지 있고요.

## d1_p6_html.py (7 missions)


### html-selectors · concept · severity 2
- 메모: 본문 5문단 + 코드 2(html, python) + 만화 1. 선택자 문단이 한 문단에 선택자 세 종류·BeautifulSoup·select/select_one·get_text까지 다 넣어 가장 빽빽해요. 쉼표 지우기 문단의 "`replace(',', '')`로 쉼표를 지운 뒤에 `int()`를 거쳐야 ..."도 60자라 둘로 자르면 좋아요. anchor 8개(문장 5, 만화 제목 1, 코드 2).
- [long] 전: 브라우저가 보여 주는 화면의 정체는 HTML이라는 글자 파일이고, 그 안에 가격이 적혀 있습니다.
  후: 브라우저가 보여 주는 화면의 정체는 HTML이라는 글자 파일이에요. 그 안에 가격이 적혀 있어요.
- [stiff] 전: 문제는 가격 말고도 광고, 메뉴, 제목 같은 글자가 수천 줄 섞여 있다는 것입니다.
  후: 문제는 가격 말고도 광고, 메뉴, 제목 같은 글자가 수천 줄 섞여 있다는 거예요.
- [stiff] 전: 거기서 원하는 칸만 집어내는 것이 이 단원의 일입니다.
  후: 거기서 원하는 칸만 집어내요. 그게 이 단원의 일이에요.
- [long] 전: `#prices`는 `id`가 prices인 요소, `.name`은 `class`가 name인 요소, `#prices li`는 "prices 안에 있는 모든 `li`"입니다.
  후: `#prices`는 `id`가 prices인 요소예요. `.name`은 `class`가 name인 요소고요. `#prices li`는 "prices 안에 있는 모든 `li`"예요.
- [long] 전: `BeautifulSoup`이라는 도구가 HTML을 읽어 두면 `select(선택자)`로 해당 요소를 전부, `select_one(선택자)`으로 첫 하나를 꺼낼 수 있습니다.
  후: `BeautifulSoup`이라는 도구가 HTML을 읽어 둬요. 그러면 `select(선택자)`로 맞는 요소를 전부 꺼내요. `select_one(선택자)`은 첫 하나만 꺼내고요.
- [jargon] 전: 꺼낸 요소에서 글자만 뽑을 때는 `get_text(strip=True)`를 씁니다.
  후: '태그'로 소개해 놓고 갑자기 '요소'로 바꿔 불러요. 선택자 문단 첫 줄에 "태그 하나하나를 요소(element)라고 불러요"를 한 번 넣고 그다음부터 요소로 통일하세요.
- [long] 전: 뽑아낸 가격은 `'10,000'`이라는 **글자**이고 쉼표까지 들어 있어서 `int()`로 바로 바꾸면 오류가 납니다.
  후: 뽑아낸 가격은 `'10,000'`이라는 **글자**예요. 쉼표까지 들어 있어서 `int()`로 바로 바꾸면 오류가 나요.
- [stiff] 전: 원리는 같으니 저장된 문서로 네 단계를 몸에 익히는 것이 먼저입니다.
  후: 원리는 같아요. 저장된 문서로 네 단계를 먼저 몸에 익혀요.

### string-to-int · coding · severity 1
- [long] 전: 쉼표를 지우고 `int()`로 바꿔 `price`에 저장한 뒤 `price * 3`을 출력하세요.
  후: 쉼표를 지우고 `int()`로 바꿔 `price`에 담으세요. 그다음 `price * 3`을 출력하세요.

### select-one · coding · severity 1
- [long] 전: `#prices li`에 해당하는 요소가 몇 개인지 `n_items`에, 첫 번째 종목의 이름(`.name` 요소의 글자)을 `first_name`에 저장하고 출력하세요.
  후: `#prices li`에 맞는 요소가 몇 개인지 `n_items`에 담으세요. 첫 종목의 이름(`.name` 요소의 글자)은 `first_name`에요. 둘 다 출력하세요.
- [long] 전: 첫 요소 `[0]`에서 `.select_one('.name')`으로 이름 요소를 찾고 `.get_text(strip=True)`로 글자만 꺼내세요.
  후: 첫 요소 `[0]`에서 `.select_one('.name')`으로 이름 요소를 찾으세요. `.get_text(strip=True)`로 글자만 꺼내요.

### select-prices · coding · severity 1
- [long] 전: `#prices li b`로 가격 요소를 모두 찾고, 하나씩 글자를 꺼내 쉼표를 지우고 `int()`로 바꾼 값을 `prices` 리스트에 모으세요.
  후: `#prices li b`로 가격 요소를 모두 찾으세요. 하나씩 글자를 꺼내 쉼표를 지우고 `int()`로 바꿔요. 그 값을 `prices` 리스트에 모으면 돼요.
- [long] 전: `prices = []`로 빈 리스트를 만들고 `for tag in soup.select('#prices li b'):`로 돌면서 `prices.append(int(tag.get_text(strip=True).replace(',', '')))`를 하세요.
  후: `prices = []`로 빈 리스트를 만드세요. `for tag in soup.select('#prices li b'):`로 돌아요. 안에서 `prices.append(int(tag.get_text(strip=True).replace(',', '')))`를 하면 돼요.

### parse-html · coding · severity 2
- 메모: 목표 둘째 문장이 146자(절 5개)로 세 파일에서 가장 길어요. 준비 코드가 이미 `html`을 읽어 뒀는데 목표는 '`data/prices.html`을 읽어'라고 해서 학생이 read_text부터 다시 하려 할 수 있어요.
- [long] 전: `data/prices.html`을 읽어 `soup`를 만들고, `#prices li`를 하나씩 돌면서 종목 코드(`data-code` 속성), 이름(`.name`), 가격(`b`, 쉼표 없는 정수)을 담은 딕셔너리를 `rows` 리스트에 모은 뒤, `rows`로 `df`를 만드세요.
  후: 준비 코드가 읽어 둔 `html`로 `soup`를 만드세요. `#prices li`를 하나씩 돌면서 딕셔너리를 만들어요. 종목 코드(`data-code` 속성), 이름(`.name`), 가격(`b`, 쉼표 없는 정수)을 담아요. 그 딕셔너리를 `rows` 리스트에 모은 뒤 `rows`로 `df`를 만드세요.
- [stiff] 전: 딕셔너리 리스트가 표가 되는 것은 앞 단원에서 본 그대로입니다.
  후: 딕셔너리 리스트가 표가 되는 건 앞 단원에서 본 그대로예요.
- [long] 전: `for item in soup.select('#prices li'):` 안에서 코드는 `item['data-code']`, 이름은 `item.select_one('.name').get_text(strip=True)`, 가격은 `int(item.select_one('b').get_text(strip=True).replace(',', ''))`로 꺼내 `{'code': ..., 'name': ..., 'price': ...}` 딕셔너리를 `rows`에 `append`하세요.
  후: `for item in soup.select('#prices li'):` 안에서 세 값을 꺼내요. 코드는 `item['data-code']`예요. 이름은 `item.select_one('.name').get_text(strip=True)`고요. 가격은 `int(item.select_one('b').get_text(strip=True).replace(',', ''))`예요. 셋을 `{'code': ..., 'name': ..., 'price': ...}` 딕셔너리로 묶어 `rows`에 `append`하세요.
- [filler] 전: 마지막에 `df = pd.DataFrame(rows)`.
  후: 마지막에 `df = pd.DataFrame(rows)`로 표를 만들어요.

### live-web · concept · severity 2
- 메모: 본문 5문단 + 코드 2, 만화 없음. 둘째 문단은 User-Agent·timeout·저장·수업 이유까지 네 생각이 한 문단이고, 넷째 문단은 '도구 고르기'와 '수집 예의'가 한 문단이에요. "같은 서버에 초당 수십 번 요청하는 것은 수집이 아니라 공격입니다"도 '~것은'이라 "요청하면 수집이 아니라 공격이에요"로. anchor 6개(문장 4, 코드 2).
- [long] 전: `headers`의 `User-Agent`는 "브라우저입니다"라고 밝히는 명함이고(없으면 거절하는 사이트가 있습니다), `timeout`은 응답이 없을 때 무한정 기다리지 않게 합니다.
  후: `headers`의 `User-Agent`는 "저 브라우저예요"라고 밝히는 명함이에요. 없으면 거절하는 사이트가 있거든요. `timeout`은 응답이 없을 때 무한정 기다리지 않게 해요.
- [unclear] 전: 수업이 저장 파일을 쓰는 이유도 그것입니다.
  후: '그것'이 뭘 가리키는지 안 잡혀요. "수업이 저장 파일을 쓰는 이유도 같아요. 모두가 같은 숫자로 연습하고, 사이트가 바뀌어도 미션이 안 깨지거든요." (앞 개념 끝에서 이미 한 말이라 한 줄로 줄여도 돼요)
- [long] 전: 화면이 자바스크립트로 **나중에** 그려지거나, 검색창에 글자를 넣고 버튼을 눌러야 결과가 나오는 경우입니다.
  후: 화면이 자바스크립트로 **나중에** 그려지는 경우예요. 아니면 검색창에 글자를 넣고 버튼을 눌러야 결과가 나오는 경우고요.
- [long] 전: 주소를 열고, 검색창을 찾아 글자를 넣고, 엔터를 치고, 그려진 화면의 HTML을 가져옵니다.
  후: 주소를 열어요. 검색창을 찾아 글자를 넣고 엔터를 쳐요. 그려진 화면의 HTML을 가져와요.
- [jargon] 전: 어느 쪽이든 수집 전에 사이트의 이용 약관과 `robots.txt`를 확인하고, 요청 사이에 간격을 둡니다.
  후: 어느 쪽이든 수집 전에 사이트의 이용 약관과 `robots.txt`(수집 허용 범위를 적어 둔 파일)를 확인하세요. 요청 사이에 간격도 두세요. (이 문장부터 새 문단으로 떼면 '도구 고르기'와 '예의'가 나뉘어요)
- [unclear] 전: 받은 결과를 저장한 파일로 네 단계를 연습하고, 받는 두 줄은 회사 컴퓨터에서 붙입니다.
  후: '받는 두 줄'이 어느 줄인지 안 잡혀요. "받은 결과를 저장한 파일로 네 단계를 연습해요. 받는 두 줄(`import requests`와 `requests.get(...)`)은 회사 컴퓨터에서 붙이세요." (어느 두 줄인지 편집자가 확정)
- [long] 전: 검색창에 글자를 넣고 엔터를 치는 것까지 브라우저를 직접 조종해서 페이지를 받는 도구는 무엇인가요?
  후: 검색창에 글자를 넣고 엔터까지 쳐요. 이렇게 브라우저를 직접 조종해서 페이지를 받는 도구는 뭘까요?
- [jargon] 전: 주소만으로 내용이 다 오는 페이지는 `requests`로 충분하고, 자바스크립트로 그려지거나 입력이 필요한 페이지만 Selenium을 씁니다.
  후: 주소만으로 내용이 다 오는 페이지는 `requests`로 충분해요. 자바스크립트(브라우저 안에서 나중에 도는 코드)로 그려지거나 입력이 필요한 페이지만 Selenium을 써요. (본문에도 자바스크립트 풀이가 없어요)

### html-check · quiz · severity 1
- 메모: 문항 9개(choice 5, short 2, 프롬프트 고르기 2).
- [jargon] 전: 정답은 선택자, 추출 → 정리 → 변환 → 저장 네 단계, 결과 변수와 기대값이 다 있습니다.
  후: 정답에는 선택자, 네 단계(찾기 → 글자 뽑기 → 숫자로 고치기 → 리스트에 모으기), 결과 변수와 기대값이 다 있어요. (네 단계 이름을 개념 본문과 맞춰요)
- [jargon] 전: - 「requests.get」: 주소만으로 내용이 다 오는 정적 페이지에 맞는 도구라, 검색 결과는 비어 온다.
  후: - 「requests.get」: 주소만으로 내용이 다 오는 페이지용이에요. 검색 결과는 비어 와요. ('정적 페이지'는 본문에 없는 말이에요)
- [long] 전: `select`는 리스트라 `for`로 돌거나 `[0]`으로 꺼내야 하고, `select_one`은 요소 하나를 바로 돌려줍니다.
  후: `select`는 리스트예요. `for`로 돌거나 `[0]`으로 꺼내야 해요. `select_one`은 요소 하나를 바로 돌려주고요.
- [long] 전: 정답은 어제와 오늘의 결과 차이, 쓴 선택자, 그리고 원하는 답의 종류(확인 코드 + 점검 순서)를 적었습니다.
  후: 정답은 어제와 오늘의 결과 차이와 쓴 선택자를 적었어요. 원하는 답의 종류(확인 코드 + 점검 순서)도 있고요.
- [stiff] 전: 수집 프롬프트는 선택자를 주는 것이 절반입니다.
  후: 수집 프롬프트는 선택자를 주는 게 절반이에요.
