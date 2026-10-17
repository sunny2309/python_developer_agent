---
name: explain-code
description: Explain Python code step by step for developers who want to understand what code does, how it works, and what output it produces.
---

# Explain Code Skill

## Goal
Explain the supplied Python code accurately and accessibly. Do not rewrite it unless asked.

## Workflow
1. Identify the purpose of the code in one or two sentences.
2. Explain important variables, functions, and data structures.
3. Walk through execution in order.
4. Trace a small concrete input when possible.
5. Show expected output when determinable.
6. Explain the time and space complexity using Big-O notation.
7. Mention relevant assumptions or edge cases without inventing behavior.

## Required response format
Use these Markdown sections in this order:

### 1. Overview
- State what the code does.

### 2. How It Works
- Explain the main steps as numbered bullets.

### 3. Example Walkthrough
- Show a small input and trace important changes.

### 4. Expected Output
- Show output in a fenced code block when determinable and explain it.

### 5. Time and Space Complexity
- Explain the time and space complexity using Big-O notation in simple terms.

### 6. Important Notes
- Mention relevant edge cases, assumptions, or limitations.

## Rules
- Keep explanations technically accurate.
- Define unfamiliar terms.
- Do not claim code was executed unless it actually was.
- If code is incomplete, identify what is missing.
- Write the content of every section using bullet points only.
- Explain why important operations work, not just what they do.