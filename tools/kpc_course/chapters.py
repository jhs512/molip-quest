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


def build():
    chapters = []
    for chapter_id, title, modules in OUTLINE:
        units = [importlib.import_module(f"kpc_course.{name}").UNIT for name in modules]
        for unit in units:
            for activity in unit["activities"]:
                if activity["kind"] == "coding":
                    problem = activity["problem"]
                    if problem["id"] not in PROMPTS:
                        raise SystemExit(f"{unit['id']}/{problem['id']}: tools/kpc_course/prompts.py에 인간 버전 프롬프트가 없습니다.")
                    problem["prompt"], problem["prompt_why"] = PROMPTS[problem["id"]]
        chapters.append(dict(id=chapter_id, title=title, units=units))
    return chapters
