"""Migrate older teaching scripts to correct code and visible output checkpoints."""
import ast
import re

from kpc_course import narration


def explicit_prints(code):
    """Replace top-level notebook-only expressions, retaining comments and line layout."""
    try:
        tree = ast.parse(code)
    except (SyntaxError, IndentationError):
        return code  # A correct chunk may continue an earlier loop or function.
    lines = code.splitlines(keepends=True)
    for node in reversed(tree.body):
        preview_call = (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                        and isinstance(node.value.func, ast.Attribute)
                        and node.value.func.attr in {"head", "tail", "describe"})
        if isinstance(node, ast.Expr) and (preview_call or not isinstance(node.value, (ast.Call, ast.Constant))):
            start, end = node.lineno - 1, node.end_lineno
            expression = ast.get_source_segment(code, node)
            lines[start:end] = [" " * node.col_offset + f"print({expression})\n"]
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#") and re.search(r"(마지막 줄.*(이름|적으면)|변수 이름만|print.*(안 써|없이|필요 없))", line):
            lines[i] = " " * (len(line) - len(line.lstrip())) + "# print로 표를 출력해 값을 확인해요.\n"
    return "".join(lines)


def clean_entry(entry):
    """Drop try→undo spans and defer runs until a value or graph can be seen.

    Correct code and its explanation remain incremental; no fake prints, transient values,
    or new training steps are inserted. The final source must still equal the solution.
    """
    result = []
    depth = 0
    pending = ""
    skip_output = False
    for index, step in enumerate(entry):
        kind = step[0]
        if kind == "try":
            depth += 1
            continue
        if kind == "undo":
            depth -= 1
            if depth < 0:
                raise ValueError("undo without try")
            continue
        if depth:
            continue
        if kind == "code":
            code = explicit_prints(step[1])
            line = step[2]
            if re.search(r"(이름만|df만|print.*(필요 없|안 써)|마지막 줄에.*(이름|head|만 적|만 쓰))", line):
                line = "print로 표를 출력해 값을 확인해요."
            result.append((kind, code, line))
            pending += code + "\n"
        elif kind == "run":
            skip_output = not narration.has_visible_output(pending)
            # Finish the chart, including labels and show(), before presenting it.
            if not re.search(r"\bprint\s*\(|\.show\s*\(", pending) and any(
                s[0] == "code" and re.search(r"\.show\s*\(", s[1]) for s in entry[index + 1:]
            ):
                skip_output = True
            if not skip_output:
                result.append((kind, "실행해 볼게요."))
                pending = ""
        elif kind == "output":
            if not skip_output:
                result.append((kind, step[1].replace("글자 출력은 없고 ", "").replace("글자 출력은 비어 있고 ", "")))
        elif kind == "caution" and re.search(r"(print\(.*(쉬운데|밋밋)|이름만 두세요)", step[1]):
            continue
        else:
            result.append(step)
    if depth:
        raise ValueError("try without undo")
    return result


EMPTY_EXPLANATION = re.compile(r"(아무것도|출력.{0,12}(없|비어|안 |않)|안 나오|안 보이|표.{0,8}안 보여|아직.*꺼내|띄우는 줄이 없|주석만|print로 감싸야)")


def needs_output_rewrite(entry):
    return any(step[0] == "output" and EMPTY_EXPLANATION.search(step[1]) for step in entry)
