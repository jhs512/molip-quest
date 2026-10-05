"""AI 나레이션 재작업: write the 해설 script of every concept and coding mission whose content
changed since its script was written, with the Claude CLI installed on this computer.

    python tools/narrate.py              # stale or missing entries only
    python tools/narrate.py --all        # every concept and coding mission
    python tools/narrate.py --ids hello numbers-text
    python tools/narrate.py --import     # move the hand-written narration_*.py entries into the cache
    python tools/narrate.py --check      # list what is stale, write nothing

Each mission's script lives in tools/kpc_course/narration_cache/<id>.json with the hash of the
content it was written for (narration.source_hash). The build (tools/build-kpc-course.py)
refuses a stale entry, so "content changed → narration rewritten" is enforced, and nothing
is recomputed when nothing changed. A generated entry must pass the same compile checks the
build runs (anchors present in the body, code chunks joining into the solution); the model
gets the error and tries again, up to three times. Coding missions include the solution's real
output so the 결과 line states what the student will actually see. No network of its own:
the CLI's login is used, like the app's tutor.
"""
import argparse
import concurrent.futures
import json
import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kpc_course import chapters as outline, dsl, narration  # noqa: E402

RULES = (ROOT / "docs" / "agents" / "narration.md").read_text(encoding="utf-8")

VOICE = """말투: 강사의 해요체 구어. "자,"로 장면을 열고 "~거든요", "~죠?", "~면 돼요"로 끝낸다. 한 줄은 1~2문장, 한 문장 25~45자.
수강생은 "여러분", 강사는 "저". 코드 이름은 백틱 없이 그대로 쓴다(price). 수업의 말(입력 X, 정답 y, 훈련 자료/테스트 자료,
기준 모델, 누수, 하이퍼파라미터)을 그대로 쓰고, 비유는 수업의 것(빵 공장, 콜센터, 문제집과 모의고사)만 쓴다.
진도 말("1일차", "3교시")은 쓰지 않는다. 본문에 없는 숫자나 주장을 지어내지 않는다."""


def python_executable():
    candidates = [ROOT / "target" / "ml-env" / "Scripts" / "python.exe", ROOT / "target" / "ml-env" / "bin" / "python"]
    for c in candidates:
        if c.exists():
            return str(c)
    return os.environ.get("MOLIP_PYTHON", sys.executable)


def run_solution(problem, solution):
    """The reference solution's real output (first test input when there is one), for the 결과 line."""
    stdin = problem["tests"][0]["input"] if problem.get("tests") else ""
    try:
        # As in the app's runner (assets/python/rich_runner.py): no windows, Korean fonts.
        env = dict(os.environ, MPLBACKEND="Agg")
        prelude = ("import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as _plt; "
                   "_plt.rcParams['font.family'] = ['Malgun Gothic', 'Apple SD Gothic Neo', 'AppleGothic', 'NanumGothic', 'Noto Sans KR', 'Noto Sans CJK KR', 'DejaVu Sans']; "
                   "_plt.rcParams['axes.unicode_minus'] = False
")
        result = subprocess.run([python_executable(), "-X", "utf8", "-c", prelude + solution], input=stdin, capture_output=True,
                                text=True, encoding="utf-8", timeout=120, cwd=str(ROOT / "courses"), env=env)
        out = (result.stdout + ("\n" + result.stderr if result.returncode else "")).strip()
    except Exception as error:  # noqa: BLE001
        out = f"(실행 실패: {error})"
    return out[:1500]


def concept_prompt(activity):
    check = activity["check"]
    return f"""{RULES}

{VOICE}

아래 개념 미션의 해설 대본을 JSON으로만 답하세요. 형식: [["구절", "말"], ...]
- "구절"은 본문에 글자 그대로 있는 문단 앞부분 10~30자(백틱·굵게 표시는 뺀 글자). 만화·그림·코드 블록은 펜스 안의 글자(예: "제목: ...", 코드 한 줄)로 가리킨다.
- 첫 항목은 ["title", "..."]로 시작해도 되고, 마지막 항목은 ["check", "..."]로 확인 문항을 짚어도 된다. 본문의 위에서 아래 순서로 4~8줄.
- 각 "말"은 그 문단이 하는 말을 강사가 설명하듯 1~2문장으로. 본문 밖의 내용을 지어내지 않는다.

## 미션: {activity['title']}

### 본문
{activity['body']}

### 확인 문항
{check['prompt']}
(인정 답안: {', '.join(check['accepted'])}) 풀이: {check['explanation']}
"""


def coding_prompt(activity, solution, output, prefix):
    problem = activity["problem"]
    rest = solution[len(prefix):] if prefix and solution.startswith(prefix) else solution
    return f"""{RULES}

{VOICE}

아래 코딩 미션의 해설 대본을 JSON으로만 답하세요. 형식: 단계 목록
[["problem", "말"], ["starter", "말"], ["code", "코드 조각", "말"], ..., ["run", "말"], ["output", "말"], ["submit", "말"]]
- "code" 조각들을 순서대로 이어 붙이면 아래 '타이핑할 코드'와 글자 하나까지 같아야 한다(띄어쓰기·줄 바꿈 포함). 조각은 2~4줄씩, 한 조각에 새로 배우는 것 하나. 한 줄짜리면 조각 하나.
- "starter"는 준비 코드가 있을 때만(아래 '그대로 두는 준비 코드'가 비어 있지 않을 때) 넣고, 무엇이 준비되어 있는지 말한다.
- "output"은 아래 '실제 실행 결과'에 나온 값을 말한다. 결과가 길면 무엇을 볼지를 말한다.
- "examples", "hint", "input"은 필요할 때만.

## 미션: {activity['title']}

### 문제
{problem['content']}

### 그대로 두는 준비 코드
```python
{prefix if prefix else '(없음: 첫 조각이 편집기를 비우고 시작)'}
```

### 타이핑할 코드 (조각을 이으면 이것과 같아야 함)
```python
{rest}
```

### 실제 실행 결과
```
{output}
```
"""


def ask_claude(prompt):
    command = os.environ.get("MOLIP_CLAUDE", "claude")
    args = [command, "-p", "--output-format", "text"]
    if os.name == "nt":
        args = ["cmd", "/C", *args]
    result = subprocess.run(args, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=600)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip()[:300])
    return result.stdout


def parse_entry(text):
    match = re.search(r"\[\s*\[.*\]\s*\]", text, re.S)
    if not match:
        raise ValueError("JSON 목록을 찾지 못했습니다")
    entry = json.loads(match.group(0))
    return [tuple(item) for item in entry]


def validate(activity, entry, solution):
    """The build's own compile; returns the error text or None."""
    try:
        if activity["kind"] == "concept":
            narration.compile_concept(activity, entry, activity["id"])
        else:
            narration.compile_coding(activity, entry, solution, activity["id"])
    except SystemExit as error:
        return str(error)
    return None


def generate(activity, solution, attempts=3):
    if activity["kind"] == "coding":
        problem = activity["problem"]
        output = run_solution(problem, solution)
        prefix = narration._starter_prefix(problem, solution.rstrip("\n") + "\n")
        prompt = coding_prompt(activity, solution.rstrip("\n") + "\n", output, prefix)
    else:
        prompt = concept_prompt(activity)
    feedback = ""
    last_error = None
    for _ in range(attempts):
        try:
            entry = parse_entry(ask_claude(prompt + feedback))
        except (ValueError, json.JSONDecodeError, RuntimeError) as error:
            last_error = f"응답 해석 실패: {error}"
            feedback = f"\n\n이전 답은 JSON으로 읽히지 않았습니다 ({error}). JSON 목록만 다시 답하세요."
            continue
        error = validate(activity, entry, solution)
        if error is None:
            return entry
        last_error = error
        feedback = f"\n\n이전 답이 검사에 걸렸습니다:\n{error}\n고쳐서 JSON 목록만 다시 답하세요."
    raise RuntimeError(last_error or "실패")


def missions(chapters):
    for chapter in chapters:
        for unit in chapter["units"]:
            for activity in unit["activities"]:
                if activity["kind"] in ("concept", "coding"):
                    yield unit, activity


def main():
    parser = argparse.ArgumentParser(description="AI 나레이션 재작업")
    parser.add_argument("--all", action="store_true", help="모든 개념·코딩 미션을 다시 쓴다")
    parser.add_argument("--ids", nargs="*", default=[], help="이 미션들만")
    parser.add_argument("--import", dest="import_modules", action="store_true", help="narration_*.py의 손글 항목을 캐시로 옮긴다")
    parser.add_argument("--check", action="store_true", help="낡은 항목만 나열한다")
    parser.add_argument("--jobs", type=int, default=4)
    args = parser.parse_args()

    chapters = outline.build()
    solutions = dsl.SOLUTIONS
    todo = []
    for unit, activity in missions(chapters):
        solution = solutions[activity["problem"]["id"]] if activity["kind"] == "coding" else None
        hash_ = narration.source_hash(activity, solution)
        entry, status = narration.entry_for(activity, solution)
        if args.import_modules:
            if status == "module":
                error = validate(activity, entry, solution)
                if error:
                    print(f"  ! {activity['id']}: {error}")
                    continue
                narration.write_cache(activity["id"], hash_, entry, "hand")
                print(f"  → {activity['id']} (캐시로 옮김)")
            continue
        wanted = args.all or activity["id"] in args.ids or status in ("stale", "none", "module")
        if args.ids and activity["id"] not in args.ids:
            wanted = False
        if args.check:
            if status != "fresh":
                print(f"  {status:6} {unit['id']}/{activity['id']}")
            continue
        if wanted:
            todo.append((unit, activity, solution, hash_, status))
    if args.import_modules or args.check:
        return
    print(f"{len(todo)}개 미션의 해설을 다시 씁니다 (Claude CLI, 동시 {args.jobs})")

    def work(item):
        unit, activity, solution, hash_, status = item
        try:
            entry = generate(activity, solution)
        except Exception as error:  # noqa: BLE001
            return f"  ! {unit['id']}/{activity['id']}: {error}"
        narration.write_cache(activity["id"], hash_, entry, "claude")
        return f"  ✓ {unit['id']}/{activity['id']} ({status} → 새 해설 {len(entry)}줄)"

    failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        for line in pool.map(work, todo):
            print(line, flush=True)
            failed += line.strip().startswith("!")
    if failed:
        sys.exit(f"{failed}개 실패. 다시 실행하면 실패한 것만 다시 씁니다.")
    print("끝. python tools/build-kpc-course.py 로 빌드하세요.")


if __name__ == "__main__":
    main()
