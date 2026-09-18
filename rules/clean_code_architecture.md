---
trigger: model_decision
description: Clean code and architectural standards, early returns, max nesting depth, and modularity
---

# Clean Code & Architectural Standards

Enforce high readability, maintainability, and modular design.

## 1. Flow Control & Structure
- **Early Returns (Guard Clauses)**: Handle edge cases, invalid states, and errors first with early returns or breaks. Never nest business logic inside deep `if/else` ladders.
- **Maximum Nesting Depth**: Code must not exceed a nesting depth of 2 levels. Extract nested blocks or loop bodies into helper functions if depth exceeds 2.
- **Bounded Function Size**: Functions must focus on a single responsibility and should not exceed 30–40 lines. Decompose multi-step workflows into cohesive, named private helpers.

## 2. Naming & Readability
- **Intention-Revealing Identifiers**: Use descriptive names reflecting domain concepts (e.g., `active_user_session`, `fetch_pending_invoices`). Strictly avoid single-letter (except trivial loop indices `i`), generic (`data`, `temp`, `info`), or cryptic abbreviations.
- **Self-Documenting Code**: Express intent through clear types and structure rather than redundant explanatory comments.
