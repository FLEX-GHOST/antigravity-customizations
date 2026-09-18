---
trigger: always_on
description: Verification and testing discipline, compiling and testing before reporting completion
---

# Verification & Testing Discipline Rules

Ensure all solutions actually work in reality before reporting completion.

## 1. Verification Before Completion
- **Compile & Build First**: Never declare a task finished without running the compiler (cargo check/build, tsc, npm run build) to verify zero syntax and type errors.
- **Run Relevant Tests**: Execute affected unit and integration tests. If modifying existing behavior, ensure regression tests pass.
- **Inspect Exact Errors**: When encountering errors, read the entire compiler or runtime traceback. Address the root cause directly instead of applying random surface-level guesses.

## 2. No Silent Suppression
- **No Suppressing Errors**: Never hide errors using empty catch blocks, @ts-ignore, eslint-disable, or #![allow(...)] without explicit rationale.
- **Meaningful Assertions**: Write assertions that test realistic edge cases (empty inputs, network timeouts, invalid formats), not trivial happy paths.
