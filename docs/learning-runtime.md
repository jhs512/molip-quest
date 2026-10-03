# 표·그래프와 환경 진단

`scripts/setup-learning.ps1`을 실행하면 프로젝트 안에 학습용 Python 환경을 만듭니다. 운영 앱은 `MOLIP_PYTHON`에 해당 환경의 Python 실행 파일을 지정합니다. 개발 빌드는 프로젝트의 `target/ml-env` 환경을 자동으로 찾습니다.

실행 결과에 pandas DataFrame과 Series를 그리드로 표시합니다. 마지막 표현식, `display(df)` 호출, 변수에 저장된 DataFrame을 지원합니다. 최대 100행·30열 미리보기이며 전체 크기도 표시합니다. SQL DB 접속 관리 화면은 포함하지 않습니다.

matplotlib와 seaborn 그래프는 실행 결과의 이미지로 표시합니다. `plt.show()`와 실행 종료 시 남은 figure를 수집합니다. 최대 8개 그래프를 표시하며 일반 텍스트 출력과 에러도 함께 유지합니다. 실행 제한은 60초입니다.

**환경 진단**에서 Python, pandas, matplotlib, seaborn, scikit-learn, openpyxl, Claude CLI 설치와 Claude 로그인 여부를 확인합니다. Claude 로그인 여부는 호출 가능 잔여량이나 모델 사용 권한을 보장하지 않습니다.
