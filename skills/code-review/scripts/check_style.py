import sys
from pathlib import Path

try:
    import pycodestyle
except ImportError:
    pycodestyle = None


def main():
    """Check a Python file for PEP 8 style violations."""

    if len(sys.argv) < 2:
        print("STATUS: ERROR")
        print("Reason: No Python file path was provided.")
        print("Usage: python check_style.py <python_file>")
        sys.exit(2)

    file_path = Path(sys.argv[1])

    if not file_path.is_file():
        print("STATUS: ERROR")
        print(f"Reason: File not found: {file_path}")
        sys.exit(2)

    if pycodestyle is None:
        print("STATUS: NOT RUN")
        print("Reason: pycodestyle is not installed.")
        print("Install it with: pip install pycodestyle")
        sys.exit(2)

    try:
        style_guide = pycodestyle.StyleGuide(
            quiet=False,
            max_line_length=79,
        )
        report = style_guide.check_files([str(file_path)])

    except Exception as exc:
        print("STATUS: ERROR")
        print(f"Reason: Style check failed: {exc}")
        sys.exit(2)

    print("CHECK: PEP 8")
    print(f"FILE: {file_path}")
    print(f"VIOLATIONS: {report.total_errors}")

    if report.total_errors == 0:
        print("STATUS: PASSED")
        print("No pycodestyle violations were found.")
    else:
        print("STATUS: VIOLATIONS FOUND")
        print(
            "Review the violation locations and codes below. "
            "Prioritize meaningful issues over minor style preferences."
        )


if __name__ == "__main__":
    main()