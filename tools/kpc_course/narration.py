"""해설 모드 scripts, compiled at build time so /auto and /auto-all play at once, without a CLI.

Every mission carries `narration`: the list of agent actions (assets/layout/agent.js) that the
tutor would otherwise have to improvise. The app runs them straight away and shows the lines.

- Slides: compiled from the deck's presenter script (one line per slide, then finish).
- Quizzes: compiled from each question's explanation, then the answers are filled and graded.
- Concepts and coding problems: hand-written in narration_<chapter>.py, keyed by activity id.
  * A concept entry is a list of (anchor, line). `anchor` is a fragment of the body text (as
    the student reads it: no backticks or bold); the app scrolls that block into view and
    speaks `line`. `"title"` points at the heading, `"check"` at the check question. The check
    is then answered with its explanation as the spoken 풀이.
  * A coding entry is a list of steps: ("problem", line), ("examples", line), ("hint", line),
    ("starter", line), ("code", chunk, line), ("run", line), ("output", line), ("submit", line).
    The code chunks, after the starter's own code lines, must join into the reference solution
    exactly. problem/run/output/submit get default lines when left out.

The rule this module enforces: when a body or a solution changes, its narration changes too.
A stale anchor or a chunk set that no longer matches the solution fails the build.
"""
import importlib
import os
import pathlib
import re

from kpc_course.dsl import split_slides

def load():
    """Every tools/kpc_course/narration_*.py, merged by activity id."""
    table = {}
    here = pathlib.Path(__file__).parent
    for path in sorted(here.glob("narration_*.py")):
        module = importlib.import_module(f"kpc_course.{path.stem}")
        for key, value in module.NARRATION.items():
            if key in table:
                raise SystemExit(f"narration: '{key}'가 두 모듈에 있습니다.")
            table[key] = value
    return table


FENCE = re.compile(r"```.*?```", re.S)
COMMENT = re.compile(r"<!--.*?-->", re.S)


def spoken(text):
    """Markdown prose as it is read aloud and shown in the caption: no bold, code marks or links."""
    text = COMMENT.sub("", str(text))
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`([^`\n]+)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    return re.sub(r"[ \t]+", " ", text).strip()


def body_text(markdown):
    """The concept body as the browser shows it: fences become their own text, prose loses marks."""
    parts = []
    for block in FENCE.split(markdown):
        parts.append(spoken(block))
    for fence in FENCE.findall(markdown):
        parts.append(fence.strip("`").strip())
    return "\n".join(parts)


def _say(target, text):
    return {"action": "say", "target": target, "text": spoken(text)}


def compile_slides(deck):
    front, parts = split_slides(deck["markdown"])
    actions = []
    for n, part in enumerate(parts):
        inner = [c[4:-3].strip() for c in COMMENT.findall(part)]
        line = " ".join(spoken(c) for c in inner if c and not c.startswith("_"))
        if not line:
            raise SystemExit(f"{deck['id']}: {n + 1}번째 장에 스크립트가 없어 해설을 만들 수 없습니다.")
        actions.append(_say("slides", line))
        if n + 1 < len(parts):
            actions.append({"action": "next_slide"})
    actions.append({"action": "finish_slides"})
    return actions


def _answer(question):
    """What answer_quiz fills in: the 1-based option number (options are shuffled at build
    time, so the number is final), or the first accepted short answer."""
    if question["type"] == "choice":
        return str(question["correct"] + 1)
    return question["accepted"][0]


def compile_quiz(activity):
    actions = []
    answers = {}
    for n, question in enumerate(activity["questions"], start=1):
        actions.append(_say(f"quiz:{n}", f"{n}번. " + question["explanation"]))
        answers[str(n)] = _answer(question)
    actions.append({"action": "answer_quiz", "answers": answers, "say": "자, 답을 넣고 채점할게요."})
    return actions


def compile_concept(activity, entry, where):
    if not isinstance(entry, (list, tuple)) or not entry:
        raise SystemExit(f"{where}: 개념 해설은 (구절, 말) 목록이어야 합니다.")
    text = body_text(activity["body"])
    actions = []
    for item in entry:
        if not (isinstance(item, (list, tuple)) and len(item) == 2):
            raise SystemExit(f"{where}: 개념 해설 항목은 (구절, 말) 둘이어야 합니다 → {item!r}")
        anchor, line = item
        anchor = spoken(anchor)
        if anchor == "title":
            actions.append(_say("title", line))
        elif anchor == "check":
            actions.append(_say("quiz:1", line))
        else:
            if anchor not in text:
                raise SystemExit(f"{where}: 해설이 가리키는 구절이 본문에 없습니다 → {anchor!r}. 본문을 바꿨다면 해설도 고치세요.")
            actions.append(_say("text:" + anchor, line))
    check = activity["check"]
    actions.append({"action": "answer_quiz", "answers": {"1": _answer(check)}, "say": spoken(check["explanation"])})
    return actions


def _starter_prefix(problem, solution):
    """The starter's own code (its trailing '# ...하세요' comment lines dropped) when the solution
    begins with it; the narration keeps that part and types only what follows."""
    lines = problem["starter_code"].rstrip("\n").split("\n")
    while lines and (not lines[-1].strip() or lines[-1].lstrip().startswith("#")):
        lines.pop()
    prefix = "\n".join(lines) + "\n" if lines else ""
    return prefix if prefix and solution.startswith(prefix) else ""


def _default_problem_line(problem):
    goal = problem["content"].split("### 목표", 1)[-1].split("### 힌트", 1)[0]
    paragraph = next((p for p in FENCE.sub("", goal).split("\n\n") if p.strip()), "")
    return "자, 문제부터 볼게요. " + spoken(paragraph)


def compile_coding(activity, entry, solution, where):
    if not isinstance(entry, (list, tuple)) or not entry:
        raise SystemExit(f"{where}: 코딩 해설은 단계 목록이어야 합니다.")
    problem = activity["problem"]
    solution = solution.rstrip("\n") + "\n"
    prefix = _starter_prefix(problem, solution)
    steps = {step[0]: step for step in entry if step and step[0] != "code"}
    chunks = [step for step in entry if step and step[0] == "code"]
    if not chunks:
        raise SystemExit(f"{where}: 코딩 해설에 code 단계가 없습니다.")
    joined = prefix + "".join(c[1].rstrip("\n") + "\n" for c in chunks)
    if joined != solution:
        raise SystemExit(f"{where}: 해설의 코드 조각을 이으면 정답 코드가 되어야 합니다. 정답을 바꿨다면 해설도 고치세요.\n--- 조각 ---\n{joined}--- 정답 ---\n{solution}")
    known = {"problem", "examples", "hint", "starter", "code", "run", "input", "output", "submit"}
    for step in entry:
        if not step or step[0] not in known:
            raise SystemExit(f"{where}: 모르는 해설 단계 {step!r} (가능: {', '.join(sorted(known))})")
        if step[0] == "code" and len(step) != 3:
            raise SystemExit(f"{where}: code 단계는 ('code', 코드, 말) 셋이어야 합니다.")
        if step[0] != "code" and len(step) != 2:
            raise SystemExit(f"{where}: {step[0]} 단계는 ('{step[0]}', 말) 둘이어야 합니다.")
    actions = [_say("problem", steps["problem"][1] if "problem" in steps else _default_problem_line(problem))]
    if "examples" in steps:
        actions.append(_say("examples", steps["examples"][1]))
    elif problem.get("tests"):
        first = problem["tests"][0]
        shown_input = first["input"].strip().replace("\n", ", ") or "없음"
        actions.append(_say("examples", f"예제를 보면 입력이 {shown_input}일 때 {first['expected'].strip()}이 나와야 해요."))
    if "hint" in steps:
        actions.append(_say("hint", steps["hint"][1]))
    if prefix:
        actions.append({"action": "set_code", "code": prefix,
                        "say": steps["starter"][1] if "starter" in steps else "준비 코드는 그대로 두고, 그 아래에 이어서 써요."})
    elif "starter" in steps:
        raise SystemExit(f"{where}: 정답이 준비 코드로 시작하지 않아 starter 단계를 쓸 수 없습니다.")
    for n, (_, chunk, line) in enumerate(chunks):
        action = {"action": "type_code", "code": chunk.rstrip("\n") + "\n", "say": spoken(line)}
        if n == 0 and not prefix:
            action["replace"] = True
        actions.append(action)
    if "input" in steps:
        actions.append(_say("input", steps["input"][1]))
    actions.append({"action": "run", "say": spoken(steps["run"][1]) if "run" in steps else "자, 실행해 볼게요."})
    actions.append(_say("output", steps["output"][1] if "output" in steps else "결과가 나왔죠? 예상한 값이 맞는지 보세요."))
    actions.append({"action": "submit", "say": spoken(steps["submit"][1]) if "submit" in steps else "제출해서 채점할게요."})
    return actions


def attach(chapters, solutions):
    """Give every activity its `narration`; refuse to build when a concept or coding problem
    has none, or when a hand-written one no longer matches its content."""
    table = load()
    used = set()
    missing = []
    for chapter in chapters:
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                where = f"{unit['id']}/{activity['id']}"
                kind = activity["kind"]
                if kind == "slides":
                    activity["narration"] = compile_slides(activity)
                elif kind == "quiz":
                    activity["narration"] = compile_quiz(activity)
                else:
                    entry = table.get(activity["id"])
                    if entry is None:
                        if os.environ.get("KPC_LENIENT"):
                            missing.append(where)
                            activity["narration"] = []
                            continue
                        raise SystemExit(f"{where}: tools/kpc_course/narration_*.py에 해설 스크립트가 없습니다.")
                    used.add(activity["id"])
                    if kind == "concept":
                        activity["narration"] = compile_concept(activity, entry, where)
                    else:
                        activity["narration"] = compile_coding(activity, entry, solutions[activity["problem"]["id"]], where)
    stale = sorted(set(table) - used)
    if stale:
        raise SystemExit(f"narration: 미션에 없는 해설 항목 {stale}")
    if missing:
        print(f"narration: 해설 없는 미션 {len(missing)}개 (lenient): {', '.join(missing[:8])}{' …' if len(missing) > 8 else ''}")
    return chapters
