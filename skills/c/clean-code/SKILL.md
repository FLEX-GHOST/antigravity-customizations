---
name: clean-code
description: 'Write readable, maintainable code through disciplined naming, small functions, clean error handling, and elimination of code smells. Covers SRP, comment discipline, formatting, error handling without nulls, the full code smell catalog, and clean unit testing (FIRST principles).'
license: MIT
metadata:
  author: wondelai
  version: "2.0.0"
---

# Clean Code Engineering Standard

A disciplined approach to writing software that communicates intent clearly, minimizes surprises, and welcomes change. Based on Robert C. Martin's *Clean Code* and production-grade engineering principles.

---

## 1. Core Principles

- **The Read-to-Write Ratio (> 10:1)**: Code is read far more often than it is written. Every naming choice, function boundary, and structural layout either reduces cognitive friction for the reader or compounds tech debt.
- **The Boy Scout Rule**: Always check in code cleaner than you found it. Every commit should incrementally improve the health of surrounding files.
- **Self-Documenting Logic**: If a block of code requires a comment to explain *what* it does, the code is poorly named or excessively nested. Refactor the code to reveal its own intent.

---

## 2. Meaningful Naming Standards

Names are the most pervasive documentation in software. A well-chosen name eliminates the need to inspect an implementation; a deceptive or cryptic name forces reverse-engineering.

### Rules of Naming
1. **Reveal Intent**: A name must answer why it exists, what it does, and how it is used.
   - ❌ `let d: u32;` $\rightarrow$ ✅ `let elapsed_time_in_days: u32;`
   - ❌ `def get_data():` $\rightarrow$ ✅ `def fetch_pending_invoices():`
2. **Avoid Disinformation**: Do not refer to a grouping of accounts as `accountList` unless it is genuinely a `List`. Prefer `accounts` or `account_group`.
3. **Pronounceable & Searchable**: Never invent private phonetic abbreviations (`genymdhms`, `mod_dat`). Single-letter variables are permitted strictly as trivial loop counters (`i`, `j`, `k`) in scopes under 5 lines.
4. **No Hungarian Encodings or Type Prefixes**: Modern IDEs provide instant type introspection. Avoid `str_name`, `m_address`, `b_is_active`.
5. **Class & Struct Names**: Nouns or noun phrases (`Customer`, `AccountRegistry`, `Parser`). Avoid generic mush like `Data`, `Info`, `Manager`, `Processor`.
6. **Method & Function Names**: Verbs or verb phrases (`post_payment`, `delete_page`, `save`).
7. **Boolean Predicates**: Prefix booleans with predicate verbs that read naturally in conditional statements: `is_active`, `has_permission`, `can_edit`, `should_retry`.
8. **One Word Per Concept**: Pick one domain word and stick to it across the codebase. Do not intermix `fetch`, `retrieve`, and `get` for identical retrieval operations.

---

## 3. Function Design & Architecture

Functions are the fundamental building blocks of applications. Clean functions do one thing, do it well, and do it only.

### Key Rules
1. **Small Size**: Functions should ideally be 5–15 lines, rarely exceeding 30 lines.
2. **One Level of Abstraction (Step-Down Rule)**: Code should read like top-down prose. Every function should descend exactly one level of abstraction to its child helpers:
   ```rust
   pub fn render_report(&self) -> String {
       let data = self.fetch_report_data();
       let formatted = self.format_markdown(&data);
       self.wrap_in_document_template(&formatted)
   }
   ```
3. **Argument Count**:
   - `0` arguments: Ideal (niladic).
   - `1` argument: Clean (monadic: query or transformation).
   - `2` arguments: Acceptable (dyadic: coordinate pairs, key-value).
   - `3+` arguments: Smells (polyadic). Bundle into a dedicated configuration struct or parameter object.
4. **Zero Flag Arguments**: Passing boolean flags (`render(is_admin: bool)`) proves the function does two distinct things. Split into two cohesive functions: `render_admin_view()` and `render_user_view()`.
5. **Command-Query Separation (CQS)**: A function should either change the state of an entity or return information about it, never both.
6. **Guard Clauses & Early Returns**: Handle error states, null conditions, and boundary checks at the top of the function with immediate returns. Never nest core business logic inside 3+ layers of `if/else`.
7. **No Side Effects**: A function named `check_password()` must never initialize a user session or mutate telemetry counters behind the caller's back.

---

## 4. Comment Discipline & Code Cleanliness

Comments are not pure positive assets. Comments require maintenance; when code changes and comments are neglected, comments turn into active disinformation.

### When Comments Are Prohibited (Code Smells)
- **Echo Comments**: Rephrasing code syntax (e.g. `// increment count`, `// return result`).
- **Prologues & Attributions**: Author names, dates, git histories (leave to `git blame` and commit logs).
- **Commented-Out Code**: Delete immediately. Version control preserves history permanently.
- **Tutorial & Lecture Banners**: Decorative dividers (`// ================== HELPERS ==================`).

### When Comments Are Permitted
- **Explain "Why", Not "What"**: Documenting non-obvious business rules, algorithmic complexity, hardware quirks, or third-party workarounds.
- **Safety Invariants**: In languages with manual memory or concurrency:
  ```rust
  // SAFETY: The pointer offset is verified within buffer capacity by the bounds check above.
  unsafe { *ptr.add(offset) }
  ```
- **Legal & License Headers**: Mandatory copyright statements at file roots.
- **Public API Documentation**: Structured docstrings (`///` in Rust, `/** */` in TS) describing public types, error invariants, and usage examples.

---

## 5. Formatting & Layout Discipline

Visual formatting creates the structural cues that allow engineers to scan code effortlessly:
- **The Newspaper Metaphor**: High-level orchestrators and public entry points sit at the top of the file; private helpers and low-level implementations cascade below.
- **Vertical Density & Openness**: Group tightly related lines together; insert a single blank line between logical phases (Arrange, Act, Assert).
- **Variable Proximity**: Declare variables directly adjacent to their first usage, not clustered arbitrarily at the top of long functions.

---

## 6. Error Handling Without Nulls

1. **Exceptions and Results Over Error Codes**: Returning integer error codes (`-1`, `0`, `1`) clutters caller code with deep conditional trees. Use strongly typed `Result<T, E>` or domain exceptions.
2. **Never Return Null / Nil**: Returning null forces every caller to write defensive null checks. If a caller forgets, the application crashes at runtime with NullPointerExceptions.
   - Use `Option<T>` / `Optional<T>`.
   - Use the **Null Object Pattern** (return an empty list `[]`, default empty string `""`, or a NullSpecialization that implements the expected interface without doing harm).
3. **Never Pass Null as an Argument**: Unless an API explicitly documents nullability, passing null creates implicit crash traps.

---

## 7. Master Catalog of Code Smells & Heuristics

### Comment Smells
- **C1: Inappropriate Information**: Putting meta-data, Jira IDs, or commit logs into source comments.
- **C2: Obsolete Comments**: Comments that drifted out of sync with updated code.
- **C3: Redundant Comments**: Comments describing self-evident syntax.
- **C4: Commented-Out Code**: Stale code blocks left behind.

### Function Smells
- **F1: Too Many Arguments**: Functions accepting 4+ parameters.
- **F2: Output Arguments**: Mutating an argument passed by reference to return data. Return values explicitly instead.
- **F3: Flag Arguments**: Boolean arguments that split function execution into two paths.
- **F4: Dead Functions**: Methods that are never invoked anywhere in the codebase.

### General Architectural Smells
- **G1: Multiple Languages in One Source File**: Mixing HTML, CSS, JavaScript, and SQL in one file.
- **G2: Obvious Behavior Unimplemented**: When a function's name implies behavior that is missing.
- **G3: Incorrect Boundaries**: Off-by-one errors and relying on intuition instead of writing tests for edge conditions (`<` vs `<=`).
- **G4: Overridden Safeties**: Disabling compiler warnings, linters, or security checks without documented justification.
- **G5: Duplication (DRY Violation)**: Identical algorithms or logic repeated in multiple modules.
- **G6: Code at Wrong Level of Abstraction**: High-level business logic mixing directly with low-level database or HTTP wire formatting.
- **G7: Base Classes Depending on Derivatives**: Core abstractions importing concrete implementations.
- **G8: Feature Envy**: A method in Class A accessing getters/fields of Class B more than its own state. The method belongs in Class B.
- **G9: Artificial Coupling**: Placing things together that have no logical relationship (e.g. general constants in an unrelated utility class).
- **G10: Transitive Navigation (Law of Demeter)**: Code navigating object graphs (`a.get_b().get_c().do_something()`). Talk only to immediate friends.

---

## 8. Clean Unit Testing & FIRST Principles

Unit tests safeguard refactoring. If tests are dirty, fragile, or slow, developers stop maintaining them.

### The FIRST Criteria
- **F - Fast**: Tests must run in milliseconds. Slow tests are avoided.
- **I - Independent**: Tests must never depend on the outcome or execution order of other tests. Zero shared mutable state.
- **R - Repeatable**: Tests must pass in any environment (local machine, Docker, CI runner, offline) without network reliance.
- **S - Self-Validating**: Tests must yield a boolean pass/fail. Never require a human to inspect log outputs to determine success.
- **T - Timely**: Unit tests should be written concurrently with production code (TDD / Red-Green-Refactor).

### Test Structure: Arrange - Act - Assert (AAA)
```rust
#[test]
fn withdraw_should_decrease_balance_when_funds_are_sufficient() {
    // Arrange
    let mut account = Account::new(100);

    // Act
    let result = account.withdraw(40);

    // Assert
    assert!(result.is_ok());
    assert_eq!(account.balance(), 60);
}
```
- **Single Concept Per Test**: Test one logical behavior per test function rather than cramming 10 unrelated scenarios into one long routine.
