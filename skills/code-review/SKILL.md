---
name: code-review
description: Review Python code for correctness, edge cases, error handling, readability, performance, and tests. Use when a user asks for a code review or improvement recommendations.
---

# Code Review Skill

## Goal
Perform a systematic, evidence-based review of the supplied Python code.

## Workflow
1. Understand the intended behavior. If unclear, state your assumption.
2. Inspect correctness and identify likely bugs.
3. Inspect edge cases and input validation.
4. Inspect error handling.
5. Consider readability and maintainability.
6. Consider performance only where there is a concrete reason.
7. Recommend the smallest useful fixes.
8. Suggest tests for important cases.
9. Check for meaningful PEP 8 style violations using available supporting tools.
10. Prioritize findings by severity and practical impact.

## Use Supporting Files

- Consult `references/review-checklist.md` for review questions.
- Consult `assets/severity-guide.json` for severity definitions.
- Use `scripts/inspect_python.py` for static inspection when available.
- Use `scripts/check_style.py` for automated PEP 8 style checks when available.
- Treat script results as supporting evidence, not as a substitute for reasoning or running tests.
- If a supporting script is unavailable or fails, continue the review using the available evidence and state the limitation when relevant.

## Required Response Format

Use these Markdown sections in this exact order. Write the content of every section using bullet points only, except for code blocks.

### 1. Summary

- Give a one- or two-sentence assessment of the code.
- Highlight the most important strengths or risks.

### 2. Findings

- For each meaningful finding, use nested bullets and include:
  - **Severity:** Critical / High / Medium / Low
  - **Category:** Correctness / Edge Case / Error Handling / Readability / Performance / Testing / Style
  - **Issue:** What is wrong or risky?
  - **Impact:** Why does it matter?
  - **Location:** Identify the relevant line, function, or expression when possible.
- Distinguish confirmed issues from potential risks.
- If no meaningful issues are found, say so explicitly.

### 3. Recommended Fix

- Provide corrected code or a focused patch for the important findings.
- Explain the key changes.
- Prefer small, targeted improvements over unnecessary rewrites.
- If no fix is needed, state that explicitly.

### 4. Tests to Add

- List concrete test cases and their expected behavior where useful.
- Include edge cases and failure scenarios relevant to the findings.
- Do not claim tests were run unless they were actually executed.

### 5. Limitations

- State what could not be verified without executing tests or seeing surrounding code.
- Mention when dependencies, supporting files, or execution results were unavailable.
- Clearly distinguish automated static or style checks from actual test execution.
- Do not claim that the code is bug-free or fully compliant based on limited checks.

## Rules

- Do not invent bugs or unsupported findings.
- Distinguish definite bugs from possible risks.
- Do not claim tests were run unless they were actually run.
- Prefer specific, actionable findings over style nitpicks.
- Avoid large rewrites when a small fix is sufficient.
- Write every section using bullet points only, except code blocks.
- Report meaningful PEP 8 violations with line numbers and descriptions when available.
- Use the outputs of supporting scripts accurately; never imply a check passed if it failed or was not performed.