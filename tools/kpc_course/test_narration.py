"""The coding 해설 compiler enforces the content rules (docs/content-rules.md) without the AI.

    python -m pytest tools/kpc_course/test_narration.py -q
"""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from kpc_course import comments, narration  # noqa: E402

SOLUTION = "price = 10000\nquantity = 3\namount = price * quantity\nprint(amount)\n"
ACTIVITY = {
    "id": "variable-print",
    "kind": "coding",
    "title": "1-1-8 변수에 저장하고 출력하기",
    "problem": {"id": "variable-print", "content": "### 목표\n\n곱해서 출력하세요.", "starter_code": "price = 10000\nquantity = 3\n# amount를 만들고 출력하세요\n", "tests": [{"input": "", "expected": "30000\n"}]},
}
GOOD = [
    ("problem", "같은 계산을 이름표로 해요."),
    ("starter", "준비 코드 두 줄은 그대로 둘게요."),
    ("code", "amount = price * quantity\n", "가격과 수량을 곱해요."),
    ("code", "print(amount)\n", "print로 금액을 출력해요."),
    ("run", "실행해요."),
    ("output", "30000이 나왔죠?"),
    ("submit", "제출할게요."),
]


def compile_(entry):
    return narration.compile_coding(ACTIVITY, entry, SOLUTION, "test")


def test_short_solution_waits_for_print_and_runs_once():
    actions = compile_(GOOD)
    assert [a["action"] for a in actions].count("run") == 1
    assert actions[-1]["action"] == "submit"
    typed = "".join(a["code"] for a in actions if a["action"] == "type_code")
    assert "price = 10000\nquantity = 3\n" + typed == SOLUTION


def test_assignment_only_checkpoint_is_rejected():
    entry = list(GOOD)
    entry[3:3] = [("run", "실행해요."), ("output", "아무것도 안 나와요.")]
    with pytest.raises(SystemExit, match="출력 없는 실행"):
        compile_(entry)


@pytest.mark.parametrize("kind", ["try", "undo"])
def test_intentional_error_steps_are_rejected(kind):
    entry = list(GOOD)
    entry.insert(2, (kind, "print(amount\n", "틀려 봐요.") if kind == "try" else (kind, "되돌려요."))
    with pytest.raises(SystemExit, match="일부러 틀리는"):
        compile_(entry)


def test_multiple_visible_checkpoints_must_be_executed_incrementally():
    solution = SOLUTION + "print(amount * 2)\n"
    entry = GOOD[:-1] + [("code", "print(amount * 2)\n", "두 배를 출력해요."),
                         ("run", "실행해요."), ("output", "60000이에요."), GOOD[-1]]
    assert len([a for a in narration.compile_coding(ACTIVITY, entry, solution, "test") if a["action"] == "run"]) == 2
    once = [s for i, s in enumerate(entry) if i not in (4, 5)]
    with pytest.raises(SystemExit, match="반복"):
        narration.compile_coding(ACTIVITY, once, solution, "test")


def test_output_must_immediately_follow_run():
    entry = list(GOOD)
    entry.insert(4, ("output", "run 없이 나온 output"))
    with pytest.raises(SystemExit, match="output은 run 바로 뒤"):
        compile_(entry)


def test_clean_entry_removes_empty_runs_and_error_demonstration_without_changing_solution():
    from kpc_course.clean_narration import clean_entry
    old = GOOD[:3] + [("run", "실행해요."), ("output", "아무것도 없어요."),
                     ("try", "print('amount')\n", "틀려 봐요."), ("run", "실행해요."),
                     ("output", "amount 글자예요."), ("undo", "되돌려요.")] + GOOD[3:]
    cleaned = clean_entry(old)
    assert not {"try", "undo"}.intersection(s[0] for s in cleaned)
    assert sum(s[0] == "run" for s in cleaned) == 1
    assert compile_(cleaned)


def test_notebook_expressions_and_their_comments_become_prints():
    from kpc_course.clean_narration import explicit_prints
    code = "df = {'a': 1}\n# 마지막 줄에 변수 이름만 쓰면 보여요.\ndf\n"
    fixed = explicit_prints(code)
    assert fixed.endswith("print(df)\n")
    assert "이름만" not in fixed
    assert "df = {'a': 1}" in fixed
    assert explicit_prints("df.head()\n") == "print(df.head())\n"


def test_runtime_verification_rejects_empty_output_but_accepts_a_captured_graph():
    import narrate
    entry = [("code", "print('')\n", "출력해요."), ("run", "실행해요.")]
    assert narrate.run_errors(entry, [""])
    assert not narrate.run_errors(entry, ["(그래프 출력)"])


def test_execution_errors_cannot_hide_behind_long_stdout(monkeypatch):
    import narrate
    from types import SimpleNamespace
    monkeypatch.setattr(narrate.subprocess, "run", lambda *args, **kwargs:
                        SimpleNamespace(returncode=1, stdout="x" * 2000, stderr="Traceback: NameError"))
    out = narrate.run_solution({}, "print('x')")
    assert out.startswith("(실행 실패:")
    assert "NameError" in out


def test_empty_canvas_is_not_an_output_checkpoint():
    assert not narration.has_visible_output("fig, ax = plt.subplots()\n")
    assert narration.has_visible_output("ax.plot([1, 2], [3, 4])\n")
    assert not narration.has_visible_output("# print(amount)\namount = 3\n")


def test_final_notebook_only_expression_is_rejected_even_after_an_earlier_print():
    solution = SOLUTION + "amount\n"
    with pytest.raises(SystemExit, match="print로 출력"):
        narration.compile_coding(ACTIVITY, GOOD, solution, "test")


def test_chunks_must_join_into_the_solution_with_comments_intact():
    commented = "price = 10000\nquantity = 3\n# 금액을 계산해요.\namount = price * quantity\nprint(amount)  # 출력\n"
    entry = [GOOD[0], GOOD[1],
             ("code", "# 금액을 계산해요.\namount = price * quantity\nprint(amount)  # 출력\n", "금액을 출력해요."),
             *GOOD[4:]]
    actions = narration.compile_coding(ACTIVITY, entry, commented, "test")
    assert "price = 10000\nquantity = 3\n" + "".join(a["code"] for a in actions if a["action"] == "type_code") == commented
    with pytest.raises(SystemExit, match="정답 코드가 되어야"):
        narration.compile_coding(ACTIVITY, entry, SOLUTION, "test")
    assert comments.strip_comments(commented) == comments.strip_comments(SOLUTION)


def test_unused_imports_are_dropped_from_starter_and_solution_alike():
    from kpc_course import dsl
    starter = "import matplotlib.pyplot as plt\nimport seaborn as sns\n# fig, ax를 만드세요\n"
    solution = "import matplotlib.pyplot as plt\nimport seaborn as sns\nfig, ax = plt.subplots()\n"
    new_starter, new_solution = dsl.drop_unused_imports(starter, solution)
    assert "seaborn" not in new_starter and "seaborn" not in new_solution
    assert new_starter == "import matplotlib.pyplot as plt\n# fig, ax를 만드세요\n"
    assert new_solution.startswith("import matplotlib.pyplot as plt\nfig, ax")
    kept = "import pandas as pd\nfrom bs4 import BeautifulSoup\n"
    used = kept + "soup = BeautifulSoup(html)\ndf = pd.DataFrame()\n"
    assert dsl.drop_unused_imports(kept, used) == (kept, used)
    assert dsl.unused_imports("import time\nfrom sklearn.metrics import accuracy_score, f1_score\nprint(f1_score)\n") == ["import time"]
