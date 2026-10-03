# KPC 수업 자료

C:/works/kpc-lec에 있던 강의 제공 자료를 읽어 앱의 고정된 오프라인 실습 자료로 구성했습니다. 원본 프로젝트는 수정하지 않았습니다. 수강생 명단은 사용하지 않습니다.

- titanic.csv: 기존강사 수업자료/titanic.xlsx를 CSV로 변환. 1309행·14열이며 결측과 컬럼 이름을 유지합니다.
- credit.csv: 기존강사 수업자료/default of credit card clients.xlsx의 두 번째 행을 헤더로 읽어 CSV로 변환. 30000행·25열. 교재가 연결한 원자료는 UCI Default of Credit Card Clients입니다.
- stock.csv: 기존강사 수업자료/_ko_stock/stock_data/005930.csv를 그대로 복사. 401행이며 Date 포함 7열입니다. 이 고정 파일로만 학습하며 실시간 가격과 섞지 않습니다.
- prices.html: practice/prices.html의 가상 가격 문서. 라이브 사이트 접근 대신 선택자와 문자열 변환 원리를 연습합니다.

실행기는 매번 새 작업 폴더의 data/에 원본 자료를 준비합니다. 학생 코드가 변경한 파일과 이전 실행의 임시 파일은 다음 실행으로 이어지지 않습니다. 학생은 main.py 하나만 편집하며 데이터 파일을 직접 준비하지 않습니다.
