"""Editorial checks that run at build time. A failing check stops the build."""
import collections
import re

# Tooling and trivia that students never touch in this course.
FORBIDDEN = ["uv", "Anaconda", "Jupyter", "Selenium", "yfinance", "FinanceDataReader", "폰트", "891행", "번째 보기"]
FENCED = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]+`")


def broken_backtick(value):
    """Code split across backticks, e.g. `groupby`('`gender`') or `index`=`False` or ['`price`']."""
    prose = FENCED.sub("", value)
    for match in INLINE_CODE.finditer(prose):
        before = prose[match.start() - 1] if match.start() > 0 else ""
        after = prose[match.end()] if match.end() < len(prose) else ""
        # `name`(그리고 …) is a Korean parenthetical; `name`() or `name`('x') is split code.
        parenthetical = prose[match.end() + 1 : prose.find(")", match.end()) if prose.find(")", match.end()) != -1 else len(prose)]
        split_call = after == "(" and not re.search(r"[가-힣]", parenthetical) and not parenthetical.startswith("`")
        quoted = bool(before) and before in "'\"" and bool(after) and after in "'\""
        if split_call or (after and after in "[=") or quoted:
            return match.group(0) + after
    return None


def _texts(activity):
    if activity["kind"] == "concept":
        yield "body", activity["body"]
        yield "check", activity["check"]["prompt"] + "\n" + activity["check"]["explanation"]
    elif activity["kind"] == "coding":
        yield "content", activity["problem"]["content"]
    else:
        for q in activity["questions"]:
            yield q["id"], q["prompt"] + "\n" + q["explanation"] + "\n" + "\n".join(q.get("options", []))


def run(chapters):
    problems = []
    positions = collections.Counter()
    choices = 0
    for chapter in chapters:
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                where = f"{unit['id']}/{activity['id']}"
                for label, value in _texts(activity):
                    broken = broken_backtick(value)
                    if broken:
                        problems.append(f"{where} {label}: 코드가 백틱으로 쪼개져 있습니다 → {broken!r}")
                    for word in FORBIDDEN:
                        if re.search(rf"(?<![A-Za-z]){re.escape(word)}(?![A-Za-z])", value):
                            problems.append(f"{where} {label}: 수업 밖 용어 {word!r}")
                if activity["kind"] == "concept":
                    paragraphs = [p for p in activity["body"].split("\n\n") if p.strip()]
                    if not 2 <= len(paragraphs) <= 8:
                        problems.append(f"{where}: 개념 본문은 2~8문단이어야 합니다 (현재 {len(paragraphs)})")
                    if "```" not in activity["body"]:
                        problems.append(f"{where}: 개념에 코드 예시 블록이 없습니다")
                if activity["kind"] == "quiz":
                    for q in activity["questions"]:
                        if q["type"] == "choice":
                            positions[q["correct"]] += 1
                            choices += 1
    if choices >= 10 and max(positions.values()) / choices > 0.6:
        problems.append(f"객관식 정답 위치가 한쪽에 쏠려 있습니다: {dict(positions)}")
    return problems
