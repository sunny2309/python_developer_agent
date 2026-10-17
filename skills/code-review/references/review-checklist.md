# Python Code Review Checklist

Use this checklist as a guide, not as a reason to invent findings.

## Correctness
- Does the code implement the apparent intent?
- Are calculations and conditions correct?
- Are return values consistent?

## Edge cases and validation
- What happens with empty inputs?
- What happens with None, unexpected types, or boundary values?
- Are assumptions about input shape documented?

## Error handling
- Could a common input cause an exception?
- Should the function validate input or let the caller handle the error?
- Are exceptions being hidden?

## Readability and maintainability
- Are names clear?
- Is the logic unnecessarily complex?
- Is behavior documented where it is not obvious?

## Performance
- Is there a concrete avoidable cost?
- Would an optimization matter for realistic input sizes?
- Avoid speculative performance claims.

## Tests
- Is the normal case covered?
- Are important edge cases covered?
- Do tests verify behavior rather than implementation details?
