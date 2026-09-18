---
trigger: always_on
description: Error handling discipline, structured errors, context preservation, and fail-fast invariants
---

# Error Handling & Failure Contract Standards

Ensure resilient, debuggable, and structured error propagation across all applications.

## 1. Error Representation
- **Structured over Stringly-Typed**: Never emit generic string errors (e.g., `throw "error"`, `Err("failed")`, or ad-hoc strings). Model domain and operational errors using strongly-typed enums, classes, or structured domain error types.
- **Context Preservation**: When propagating an error across architectural boundaries (I/O, database, network, domain), attach descriptive operational context and preserve the underlying root cause (`anyhow::Context`, `cause: err`, `%w`). Never swallow the original stack trace or error detail.

## 2. Recovery & Failure Boundaries
- **Expected Errors vs Bugs**: Handle anticipated failures (validation, missing records, unauthorized access) gracefully with standard return types (`Result`, `Option`, structured HTTP responses). Reserve panics or fatal crashes strictly for unrecoverable invariant violations and programmer bugs.
- **Never Discard Errors**: Never silence errors using empty catch blocks, `_ = ...`, or ignoring fallible operations without an explicit and justified reason.
