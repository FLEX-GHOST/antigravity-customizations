---
trigger: always_on
description: Code integrity, minimal blast radius, preserving comments, and surgical edits
---

# Code Integrity & Minimal Blast Radius Rules

Maintain code stability, prevent unintentional regressions, and avoid over-engineering.

## 1. Documentation & Code Preservation
- **Preserve Existing Comments**: Never wipe or rewrite existing comments, docstrings, or license headers in code you modify unless specifically asked.
- **Maintain Unrelated Code**: Do not silently delete helper methods, unused imports from unfinished work, or adjacent utilities when performing an edit.
- **Backward Compatibility**: Preserve existing function signatures, public types, and API contracts unless breaking changes are explicitly requested.

## 2. Minimal Blast Radius & Anti-Overengineering
- **Surgical Edits**: Touch only the lines required to fix the bug or implement the feature. Do not reformat entire files or reorder declarations without reason.
- **No Speculative Abstractions**: Solve the concrete problem in front of you. Do not build generic frameworks, unused interfaces, or deep inheritance trees for one-off operations.
- **Production Error Handling**: Do not write lazy .unwrap() or panic calls. Always handle errors cleanly with structured return types or explicit recovery paths.
