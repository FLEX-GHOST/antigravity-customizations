---
trigger: model_decision
---

# Rust Production Systems Engineering Standards & Master Rules (Part 2)

## Part VI: Production Error Handling & Resilience (`err-`)
1. **Error Architecture (`thiserror` vs `anyhow`)**:
   - Subsystem modules (`bot`, `factory`, `db`, `webhook`) use strongly-typed enums with `thiserror::Error`.
   - Top-level binaries (`main.rs`, CLI) use `anyhow::Result` with `.context(...)`.
   - Box large foreign error variants (`Box<ForeignError>`) to keep `Result<T, E>` stack footprint under 32 bytes.
2. **Zero-Panic Runtime Discipline (`err-no-unwrap-prod`)**:
   - BANNED: `.unwrap()` and `.expect()` in production handlers and workers.
   - Propagate with `?` or handle with pattern matching and `.unwrap_or_default()`.
   - Safe indexing: Never index via `slice[idx]`. Always use `.get(idx)` and handle `Option<&T>`.
   - Reserve `panic!` strictly for violated unrecoverable code invariants, never for runtime I/O or user errors.
3. **Telegram FloodWait & Rate Limit Handling**:
   - Dynamically detect Telegram `FloodWait` (code 420).
   - Sleep for `wait_seconds + random_jitter(100ms..1000ms)` before retrying. Never retry in a tight loop.
   - Apply exponential backoff with jitter for transient network and 5xx failures up to a fixed retry cap.

---

## Part VII: Unsafe Code & Rust 2024 Standards (`unsafe-`)
1. **The `// SAFETY:` Contract**: Every `unsafe` block must have an explicit `// SAFETY:` comment proving invariants. Every `unsafe fn` must have a `# Safety` docstring.
2. **Minimized Unsafe Scope**: Wrap only the exact operation requiring unsafety. Never use `mem::uninitialized()` or `mem::zeroed()`; use `std::mem::MaybeUninit<T>`.
3. **Rust 2024 Compatibility**: Wrap foreign blocks in `unsafe extern { }` and mark with `#[unsafe(no_mangle)]`.

---

## Part VIII: Type-Driven Safety & API Design (`type-` & `api-`)
1. **Newtypes for Identifiers (`type-newtype-ids`)**: Wrap primitive IDs in newtypes (`struct BotId(pub i64);`, `struct UserId(pub i64);`).
2. **Make Invalid States Unrepresentable (`type-enum-states`)**: Model mutually exclusive states with enums rather than structs with multiple optional fields.
3. **Builder Pattern (`api-builder-must-use`)**: Use builders for multi-parameter configurations. Mark builder methods with `#[must_use]`.
4. **Forward Compatibility (`api-non-exhaustive`)**: Mark public enums and structs that may evolve with `#[non_exhaustive]`.

---

## Part IX: Performance & Compiler Optimization (`perf-` & `opt-`)
1. **Fast Hashers (`perf-ahash`)**: Use `ahash::AHashMap` / `AHashSet` for internal maps (2x-5x faster than SipHash). Reserve SipHash for untrusted external input.
2. **Inlining Discipline (`opt-inline-small`)**: Mark small hot-path functions (< 15 lines) with `#[inline]`. Mark error and bailout paths with `#[cold]` and `#[inline(never)]`.
3. **Release Profile**: In `Cargo.toml`: `opt-level = 3`, `lto = "thin"`, `codegen-units = 1`, `panic = "abort"`, `strip = true`.

---

## Part X: Prohibited Anti-Patterns (`anti-`)
- `anti-unwrap-abuse`: `.unwrap()` in handlers $\rightarrow$ Handle gracefully via `?`.
- `anti-lock-across-await`: Holding sync Mutex across `.await` $\rightarrow$ Drop guard before `.await`.
- `anti-index-over-iter`: Direct `items[i]` $\rightarrow$ Use iterators or safe `.get(i)`.
- `anti-stringly-typed`: Strings for IDs $\rightarrow$ Wrap in domain newtypes.
- `anti-empty-catch`: Discarding errors $\rightarrow$ Log or handle with context.
- `anti-format-hot-path`: `format!()` in loops $\rightarrow$ Reuse buffer with `write!()`.
- `anti-unbounded-channel`: `unbounded_channel()` $\rightarrow$ Use bounded with backpressure.
- `anti-raw-bytes-ram`: `Vec<u8>` in RAM $\rightarrow$ Store disk path and stream.

---

## Part XI: Final Validation Checklist
Before completing any task or delivering code, verify:
- [ ] **Task Completeness**: Root cause fixed; no placeholders, mocks, or unfinished logic.
- [ ] **Zero Regressions**: Existing behavior, public interfaces, and data models preserved.
- [ ] **No Hallucinations**: All APIs, crates, and signatures verified against docs/Cargo.lock.
- [ ] **Memory & Allocations**: No unneeded clones, no unbounded collections, no raw byte buffers in RAM.
- [ ] **Async & Concurrency**: No blocking calls on workers, no sync mutex held across `.await`, cancellation safety verified.
- [ ] **Zero Panics**: No `.unwrap()`, no `.expect()`, no unvalidated array indexing.
- [ ] **Clean Compilation**: Zero compiler warnings, clean Clippy checks, production readiness.
