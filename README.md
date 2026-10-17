# AI Agent Skills Tutorial

Run Jupyter notebook to understand agent step by step.

When running agent.py file, keep in mind that code should be provided in three backticks section. Check below example.


```markdown
Please review this Python function and suggest improvements.

```python
def calculate_average(numbers):
    if not numbers:
        return 0

    total = sum(numbers)
    count = len(numbers)

    return total / count
```

```

Companion Skill files for the Jupyter notebook.

- `skills/explain-code/SKILL.md`
- `skills/code-review/SKILL.md`
- `skills/code-review/references/review-checklist.md`
- `skills/code-review/assets/severity-guide.json`
- `skills/code-review/scripts/inspect_python.py`

Set `OPEN_ROUTER_KEY` in a `.env` file before running model calls.
