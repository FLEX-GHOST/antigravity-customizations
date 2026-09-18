---
trigger: always_on
description: Network and HTTP request hygiene, preventing waterfalls, duplicate requests, and unhandled rate limits
---

# Engineering Excellence & Request Hygiene Rules

Ensure production-grade reliability, avoid wasteful network traffic, and maintain code discipline.

## 1. Network & Request Hygiene
- **No Sequential Waterfalls**: Independent network calls must execute in parallel (Promise.all in JS, tokio::join! in Rust). Never serialize requests that do not depend on each other's output.
- **In-Flight Deduplication**: Never fire multiple simultaneous HTTP requests for the same read-only resource. Share the pending promise/future.
- **Mandatory Request Cancellation**: Always attach cancellation mechanisms (AbortController in JS/React, cancellation tokens in backend) to search inputs, unmounting views, and rapid filter actions.
- **Idempotency & Bounded Backoff**: Handle HTTP 429 and transient 5xx errors using exponential backoff with random jitter. Always respect upstream Retry-After headers.

## 2. Code Quality & Scope Discipline
- **Minimal Dependencies**: Never install large third-party libraries for trivial helpers that take 5 lines of native code.
- **Pattern Preservation**: Match the existing architectural conventions, error types, and naming styles of the surrounding codebase.
- **No Hallucinated APIs**: Always verify signatures and imports against actual crate/package documentation before generating code.
