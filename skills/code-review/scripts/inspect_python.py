import ast
import json
import sys
from pathlib import Path

def inspect_source(source: str) -> dict:
    # Parse source without executing it; return basic structural facts.
    result = {
        "line_count": len(source.splitlines()),
        "function_names": [],
        "class_names": [],
        "has_try_except": False,
        "syntax_error": None,
    }
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        result["syntax_error"] = f"{exc.msg} (line {exc.lineno})"
        return result

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["function_names"].append(node.name)
        elif isinstance(node, ast.ClassDef):
            result["class_names"].append(node.name)
        elif isinstance(node, ast.Try):
            result["has_try_except"] = True
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python inspect_python.py path/to/file.py")
    source_path = Path(sys.argv[1])
    print(json.dumps(inspect_source(source_path.read_text(encoding="utf-8")), indent=2))
