"""도전 과제 강사 자료 만들기: the practice problems' commented solutions and 해설 scripts, under
the same content rules as the course (docs/content-rules.md), encrypted into site/data/instructor.json.

    python tools/practice-materials.py            # regenerate comments and narration, then encrypt
    python tools/practice-materials.py --verify   # decrypt and replay what is published, write nothing

Plaintext never enters the repository: the bare solutions and 풀이 요약 live in
target/course-guide-authoring/practice-source.json, the generated materials go to
target/course-guide-authoring/solutions.json, and the password is read from
target/course-guide-authoring/password.txt by this script only (never printed). The encryption
matches src/practice.rs decrypt: PBKDF2-SHA-256 (310,000 rounds) → AES-256-GCM, salt/iv/ciphertext
base64, the GCM tag appended to the ciphertext.

Each problem is treated as a coding mission: tools/annotate.py adds the comments (checked to
strip back to the bare code and to still print the expected output), tools/narrate.py writes the
incremental 해설 (correct code → visible output → run, no intentional errors), and
kpc_course.narration.compile_coding turns it into the agent actions the app plays. The code is
stored with "cafe-sales.xlsx" (the web practice page's layout); the app maps it to
data/cafe-sales.xlsx itself.
"""
import argparse
import base64
import concurrent.futures
import importlib.util
import json
import os
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kpc_course import comments, narration  # noqa: E402

AUTHORING = ROOT / "target" / "course-guide-authoring"
SOURCE = AUTHORING / "practice-source.json"
MATERIALS = AUTHORING / "solutions.json"
PASSWORD = AUTHORING / "password.txt"
PUBLISHED = ROOT / "site" / "data" / "instructor.json"
COURSE = ROOT / "courses" / "morning-practice.json"
EXCEL = ROOT / "site" / "data" / "cafe-sales.xlsx"
ITERATIONS = 310000
APP_PATH, WEB_PATH = '"data/cafe-sales.xlsx"', '"cafe-sales.xlsx"'


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def problems():
    course = json.loads(COURSE.read_text(encoding="utf-8"))
    return {unit["id"]: unit for chapter in course["chapters"] for unit in chapter["units"]}


def activity_for(unit):
    """The practice problem as the course tools see a coding mission."""
    return {
        "id": unit["id"],
        "kind": "coding",
        "title": unit["title"],
        "problem": {"id": unit["id"], "content": unit["content"], "starter_code": unit["starter_code"], "tests": unit.get("tests", [])},
    }


# The files the app's runner puts under data/ (src/runner.rs), so a solution runs here as there.
DATA_FILES = [EXCEL, *(ROOT / "courses" / "data" / name for name in ("titanic.csv", "credit.csv", "stock.csv", "prices.html", "croissant.csv"))]


def sandbox():
    """A working directory with every data file where the solutions expect it (data/…)."""
    directory = pathlib.Path(tempfile.mkdtemp(prefix="practice-"))
    (directory / "data").mkdir()
    for path in DATA_FILES:
        shutil.copy(path, directory / "data" / path.name)
    return directory


def read_password():
    return PASSWORD.read_text(encoding="utf-8").strip()


def encrypt(materials):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS).derive(read_password().encode("utf-8"))
    ciphertext = AESGCM(key).encrypt(iv, json.dumps(materials, ensure_ascii=False).encode("utf-8"), None)
    return {"version": 1, "iterations": ITERATIONS, "salt": base64.b64encode(salt).decode(), "iv": base64.b64encode(iv).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode()}


def decrypt(blob):
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=base64.b64decode(blob["salt"]), iterations=blob["iterations"]).derive(read_password().encode("utf-8"))
    plaintext = AESGCM(key).decrypt(base64.b64decode(blob["iv"]), base64.b64decode(blob["ciphertext"]), None)
    return json.loads(plaintext)


def replay(actions, starter=""):
    """The editor's text after the agent plays the actions (assets/layout/agent.js semantics)."""
    text = ""
    for action in actions:
        kind = action["action"]
        if kind == "set_code":
            text = action["code"]
        elif kind == "type_code":
            if action.get("replace"):
                text = ""
            body = action["code"]
            if not body.endswith("\n"):
                body += "\n"
            if text and not text.endswith("\n"):
                body = "\n" + body
            text += body
    return text


def build(units, source, jobs):
    annotate, narrate = load_tool("annotate"), load_tool("narrate")
    work = sandbox()
    os.environ["MOLIP_RUN_CWD"] = str(work)
    materials = {}
    def make(item):
        unit_id, unit = item
        activity = activity_for(unit)
        bare = source[unit_id]["code"].replace(WEB_PATH, APP_PATH)
        prefix = narration._starter_prefix(activity["problem"], bare)
        print(f"  {unit_id}: 주석 달기", flush=True)
        commented = annotate.generate(activity, bare)
        error = comments.check(bare, commented, prefix)
        if error:
            raise SystemExit(f"{unit_id}: {error}")
        print(f"  {unit_id}: 해설 쓰기", flush=True)
        entry = narrate.generate(activity, commented)
        actions = narration.compile_coding(activity, entry, commented, unit_id)
        assert replay(actions).rstrip("\n") == commented.rstrip("\n"), f"{unit_id}: replay != code"
        # Stored in the web page's layout; the app maps the file name to data/ itself.
        for action in actions:
            if "code" in action:
                action["code"] = action["code"].replace(APP_PATH, WEB_PATH)
        material = {"code": commented.replace(APP_PATH, WEB_PATH), "explanation": source[unit_id]["explanation"], "narration": actions}
        runs = sum(1 for a in actions if a["action"] == "run")
        print(f"  ✓ {unit_id}: 주석 {commented.count('#')}개, 해설 {len(actions)}단계, 실행 {runs}번", flush=True)
        return unit_id, material

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as pool:
            for unit_id, material in pool.map(make, units.items()):
                materials[unit_id] = material
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return materials


def verify(materials, units):
    narrate = load_tool("narrate")
    work = sandbox()
    os.environ["MOLIP_RUN_CWD"] = str(work)
    problems_found = []
    try:
        for unit_id, unit in units.items():
            material = materials.get(unit_id)
            if material is None:
                problems_found.append(f"{unit_id}: 자료 없음")
                continue
            code = material["code"].replace(WEB_PATH, APP_PATH)
            typed = replay(material["narration"]).replace(WEB_PATH, APP_PATH)
            if typed.rstrip("\n") != code.rstrip("\n"):
                problems_found.append(f"{unit_id}: 해설을 재생한 코드가 정답과 다릅니다")
            if comments.strip_comments(code) is None or code.count("#") < 2:
                problems_found.append(f"{unit_id}: 주석이 없습니다")
            kinds = [a["action"] for a in material["narration"]]
            if not kinds.count("run"):
                problems_found.append(f"{unit_id}: 실행 단계가 없습니다")
            pending = ""
            for i, action in enumerate(material["narration"]):
                if action["action"] == "set_code" and "type_code" in kinds[:i]:
                    problems_found.append(f"{unit_id}: 입력한 코드를 되돌리는 시연이 있습니다")
                if action["action"] == "type_code":
                    pending += action["code"] + "\n"
                if action["action"] == "run":
                    if not narration.has_visible_output(pending):
                        problems_found.append(f"{unit_id}: 출력문 없이 실행하는 단계가 있습니다")
                    checkpoint = replay(material["narration"][:i]).replace(WEB_PATH, APP_PATH)
                    output = narrate.run_solution(activity_for(unit)["problem"], checkpoint)
                    if "Traceback" in output or output.startswith("(실행 실패:") or not output.strip():
                        problems_found.append(f"{unit_id}: 중간 실행이 실패하거나 출력이 없습니다")
                    pending = ""
            out = narrate.run_solution(activity_for(unit)["problem"], code)
            expected = (unit.get("tests") or [{}])[0].get("expected", "").strip()
            if expected and out.strip() != expected:
                problems_found.append(f"{unit_id}: 실행 결과가 예상 출력과 다릅니다: {out.strip()[:80]!r}")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    return problems_found


def main():
    parser = argparse.ArgumentParser(description="도전 과제 강사 자료")
    parser.add_argument("--verify", action="store_true", help="게시된 자료를 복호화해 검사만 한다")
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    units = problems()
    if args.verify:
        materials = decrypt(json.loads(PUBLISHED.read_text(encoding="utf-8")))
        found = verify(materials, units)
        if found:
            sys.exit("\n".join(found))
        print(f"{len(materials)}개 문제의 자료가 복호화되고, 해설이 정답으로 재생되며, 정답이 예상 출력을 냅니다.")
        return
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    materials = build(units, source, args.jobs)
    found = verify(materials, units)
    if found:
        sys.exit("\n".join(found))
    MATERIALS.write_text(json.dumps(materials, ensure_ascii=False), encoding="utf-8")
    PUBLISHED.write_text(json.dumps(encrypt(materials)), encoding="utf-8")
    print(f"암호화해서 {PUBLISHED.relative_to(ROOT)}에 썼습니다. 평문은 {MATERIALS.relative_to(ROOT)} (Git 제외).")


if __name__ == "__main__":
    main()
