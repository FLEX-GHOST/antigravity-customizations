---
name: rust-best-practices
description: >
  Master guide for writing idiomatic, high-performance Rust based on Apollo GraphQL's best practices handbook.
  Covers ownership, borrowing, Copy vs Move, Clippy discipline, profiling with flamegraph, error handling with
  thiserror & anyhow, automated testing, static vs dynamic dispatch, the type state pattern, documentation standards,
  and thread-safe pointer architectures (Send/Sync, Arc, Mutex).
license: MIT
compatibility: Rust 1.70+, Cargo
metadata:
  author: apollographql
  version: "2.0.0"
allowed-tools: Bash(cargo:*) Bash(rustc:*) Bash(rustfmt:*) Bash(clippy:*) Read Write Edit Glob Grep
---

# Rust Best Practices: Complete Apollo GraphQL Systems Engineering Handbook

Production-grade engineering standards and patterns for building safe, memory-efficient, and maintainable Rust systems. Derived from Apollo GraphQL's Rust Best Practices Handbook and high-scale production services.

---

## 1. Coding Styles & Idioms

### Borrowing Over Cloning (`&T` over `T.clone()`)
- **Default to Borrowing**: Pass `&T` or `&mut T`. Rust's ownership model is designed around zero-cost borrowing.
- **Valid Reasons to Clone**:
  - You need to modify data while preserving an immutable snapshot.
  - Incrementing reference counts on `Arc<T>` or `Rc<T>`.
  - Transferring data across thread boundaries where ownership is fundamentally required.
  - Caching results or satisfying owned foreign API contracts.
- **Clone Traps to Eliminate**:
  - Auto-cloning in iterator loops (`.map(|x| x.clone())`); use `.cloned()` or `.copied()` at the end of the pipeline.
  - Cloning large collections (`Vec<T>`, `HashMap<K, V>`) instead of borrowing slices (`&[T]`) or references.
  - Cloning arguments because a function signature requested `&T` but the body immediately cloned it. If ownership is required, accept `T` by value so the caller can choose to move.

### When to Pass by Value (`Copy` Trait)
- If a type is small and cheap to copy, pass it by value.
- **Copy Criteria**:
  - Size $\le$ 24 bytes (up to 3 words on 64-bit architectures).
  - All fields implement `Copy` with zero heap allocations (no `Vec`, no `String`).
  - **Rule**: Never implement both `Copy` and `Iterator` on the same type to avoid confusing consumption semantics.

### Conditional Ownership with `Cow<'a, T>`
Use `std::borrow::Cow` (Clone-On-Write) when a function mostly reads borrowed data but occasionally needs to modify or allocate:

```rust
use std::borrow::Cow;

fn sanitize_input<'a>(input: &'a str) -> Cow<'a, str> {
    if input.contains('<') || input.contains('>') {
        Cow::Owned(input.replace('<', "&lt;").replace('>', "&gt;"))
    } else {
        Cow::Borrowed(input) // Zero allocation
    }
}
```

### Option & Result Handling Combinators
Prefer combinator pipelines over imperative `match` chains for clean readability:
- `.map()`: Transform inner value.
- `.and_then()`: Flatten operations that return `Option` or `Result`.
- `.ok_or_else(|| ...)`: Convert `Option` to `Result` with lazy error construction.
- `.unwrap_or_else(|| ...)`: Fallback with lazy evaluation.

### Function Boundaries: Duplication vs Wrong Abstraction
- A small amount of duplication is far cheaper than the wrong abstraction.
- Extract functions when business logic is reused with identical intent, not merely because two routines happen to share three lines of syntax.

---

## 2. Clippy and Linting Discipline

### Mandatory Daily Linting
Run Clippy across all targets and features with warnings treated as errors:

```bash
cargo clippy --all-targets --all-features --locked -- -D warnings
```

Recommended strict additions for libraries and daemons:
```bash
cargo clippy --all-targets --all-features -- -D warnings -W clippy::pedantic -W clippy::nursery
```

### Critical Clippy Lints & Rationale

| Lint Name | Category | Why It Matters | Remediation |
|---|---|---|---|
| `redundant_clone` | Perf | Detects useless heap allocations and clones | Remove `.clone()` and borrow |
| `needless_borrow` | Style | Unnecessary `&` references | Pass directly |
| `large_enum_variant` | Memory | Oversized enum variants inflate the enum stack size | Wrap large variant in `Box<T>` |
| `needless_collect` | Perf | Allocates temporary `Vec` when chaining iterators | Remove `.collect()` and continue iterating |
| `clone_on_copy` | Complexity | Calling `.clone()` on types implementing `Copy` | Rely on implicit copy |
| `unnecessary_wraps` | Design | Functions that always return `Ok` or `Some` | Return inner type directly |
| `manual_ok_or` | Style | Manual `match` to convert Option to Result | Use `.ok_or()` or `.ok_or_else()` |

### Fix Warnings, Never Silence Silently
- **Never** slap unannotated `#[allow(...)]` attributes on production code.
- Use `#[expect(clippy::lint_name)]` with a mandatory doc comment explaining *why* the warning is an acceptable design choice:
  ```rust
  // Fast path: cache line alignment preferred over enum packing
  #[expect(clippy::large_enum_variant)]
  enum Message {
      Ping,
      Payload(Box<[u8; 1024]>),
  }
  ```

---

## 3. Performance Mindset: Measure, Profile, Optimize

### Golden Rule: Don't Guess, Measure
- Always profile and benchmark with the `--release` flag enabled. Development builds lack compiler optimizations and produce deceptive bottlenecks.
- Micro-benchmarking: Use `criterion` or `cargo bench` to validate that an optimization produces at least a measurable 5% improvement.

### Profiling with Flamegraphs
Visualize CPU cycles and call-stack depth:

```bash
# Install cargo-flamegraph
cargo install flamegraph

# Profile release binary
cargo flamegraph --bin my_daemon

# Profile unit and integration tests
cargo flamegraph --unit-test -- test_worker_pool
```
- **Flamegraph Interpretation**:
  - **Y-Axis**: Call-stack depth (main is at the bottom).
  - **Box Width**: Total CPU time spent in that function and its children. Wider boxes indicate prime targets for optimization.

### Allocation Hygiene & In-Place Mutation
- Pre-allocate collections with `with_capacity(n)` when the item count is known or bounded.
- Reuse scratch buffers (`buffer.clear()`, `write!(&mut buffer, ...)`) inside loops instead of instantiating fresh strings with `format!()`.
- Prefer `ArrayVec` or `SmallVec` for small, bounded collections to keep allocations on the stack.

---

## 4. Error Handling Architecture

### `Result` vs `panic!`
- Use `Result<T, E>` for all anticipated, recoverable failures (I/O, parsing, network, validation).
- Reserve `panic!` strictly for violated unrecoverable invariants and programming bugs.
- Informative panic macros:
  - `unreachable!()`: Code paths proven mathematically impossible.
  - `unimplemented!()`: Declared interfaces intentionally unready.
  - `todo!()`: Development markers caught by compiler lints.

### Production Zero-Panic Discipline
- **Banned**: `.unwrap()` and `.expect()` in production daemons, request handlers, and message loops.
- Handle `None` and `Err` cleanly using `let ... else` guard clauses:
  ```rust
  let Ok(payload) = serde_json::from_slice::<Update>(&bytes) else {
      return Err(BotError::MalformedUpdate);
  };
  ```

### `thiserror` for Libraries vs `anyhow` for Binaries
- **Domain & Subsystem Libraries**: Use `thiserror` to model strongly-typed, structured errors:
  ```rust
  #[derive(Debug, thiserror::Error)]
  pub enum StorageError {
      #[error("Record not found for key: {0}")]
      NotFound(String),
      #[error("Database lock timeout after {timeout_ms}ms")]
      LockTimeout { timeout_ms: u64 },
      #[error(transparent)]
      Io(#[from] std::io::Error),
  }
  ```
- **Top-Level Binaries (`main.rs`, CLI)**: Use `anyhow::Result` with `.context(...)` to annotate failures with operational context before reporting:
  ```rust
  let config = Config::load(&path)
      .with_context(|| format!("failed to load configuration from {}", path.display()))?;
  ```

---

## 5. Automated Testing Standards

### Test Naming Conventions (Arrange-Act-Assert)
Name tests clearly to describe the unit under test, the scenario, and the expected outcome:
```rust
#[cfg(test)]
mod tests {
    mod process_payment {
        use super::*;

        #[test]
        fn should_return_error_when_balance_is_insufficient() {
            // Arrange
            let account = Account::with_balance(50);
            
            // Act
            let result = account.charge(100);
            
            // Assert
            assert_eq!(result, Err(AccountError::InsufficientFunds));
        }
    }
}
```

### One Logical Assertion Per Test
- Keep test cases isolated and focused on one specific assertion or failure condition.
- Avoid 100-line multi-stage integration tests masquerading as unit tests.

### Snapshot Testing with `insta`
Use `cargo insta` for complex data structures, ASTs, and generated JSON/SQL:
```rust
#[test]
fn test_bot_config_serialization() {
    let config = BotConfig::default();
    insta::assert_json_snapshot!(config);
}
```

---

## 6. Generics, Static Dispatch & Dynamic Dispatch

> **Rule of Thumb**: Static dispatch (`impl Trait`) where you can; dynamic dispatch (`dyn Trait`) where you must.

### Static Dispatch (`impl Trait` / `<T: Trait>`)
- Monomorphized at compile time into concrete machine code.
- Zero runtime overhead; fully inlinable by the compiler.
- Trade-off: Increased binary size if called with many distinct concrete types.

```rust
// Static dispatch
fn process_events<E: EventHandler>(handler: &E, event: &Event) {
    handler.handle(event);
}
```

### Dynamic Dispatch (`&dyn Trait` / `Box<dyn Trait>`)
- Dispatched via runtime vtable pointer (fat pointer: data pointer + vtable pointer).
- Enables heterogeneous collections (e.g. `Vec<Box<dyn Plugin>>`).
- Prevents inlining and adds pointer indirection.

```rust
// Dynamic dispatch for heterogeneous plugins
struct Engine {
    plugins: Vec<Box<dyn Plugin + Send + Sync>>,
}
```

### Object Safety Rules
A trait is object-safe (can be made into `dyn Trait`) only if:
1. It does not require `Self: Sized`.
2. All methods do not return `Self`.
3. All methods have no generic type parameters.

---

## 7. The Type State Pattern

Encode operational states directly in the type system. Invalid transitions become compile-time errors rather than runtime bugs:

```rust
use std::marker::PhantomData;

// State markers
struct Disconnected;
struct Connected;

struct Connection<State> {
    stream: std::net::TcpStream,
    _state: PhantomData<State>,
}

impl Connection<Disconnected> {
    pub fn connect(addr: &str) -> std::io::Result<Connection<Connected>> {
        let stream = std::net::TcpStream::connect(addr)?;
        Ok(Connection {
            stream,
            _state: PhantomData,
        })
    }
}

impl Connection<Connected> {
    pub fn send(&mut self, data: &[u8]) -> std::io::Result<()> {
        use std::io::Write;
        self.stream.write_all(data)
    }

    pub fn disconnect(self) -> Connection<Disconnected> {
        Connection {
            stream: self.stream,
            _state: PhantomData,
        }
    }
}
```

`PhantomData<T>` is a zero-sized type (ZST) stripped during compilation, incurring zero runtime memory overhead.

---

## 8. Comments vs Documentation

| Purpose | Use `// comment` | Use `/// doc` / `//! module doc` |
|---|---|---|
| **Describe Why** | Yes: Tricky workarounds, non-obvious math, hardware bugs | No: Rustdoc is for consumers, not local hackers |
| **Describe API** | No: Buried in source code | Yes: Markdown documentation generated via `cargo doc` |
| **Tests & Verification** | No: Static text | Yes: Executable doctests (`cargo test --doc`) |
| **Visibility** | Internal private code only | Public interfaces, structs, traits, and error variants |

### Comment Format Standard
- Document **Why**, never rephrase **What** the code does.
- Format safety contracts clearly:
  ```rust
  // SAFETY: The slice length is guaranteed non-zero by the caller guard above.
  unsafe { *ptr.offset(0) }
  ```

---

## 9. Pointer Architecture & Thread Safety (Send & Sync)

### Pointer Model Comparison

| Pointer | Overhead | Thread-Safe? | Interior Mutability? | Best Use Case |
|---|---|---|---|---|
| `&T` | 1 word | Yes (if `T: Sync`) | No | Temporary borrowed access |
| `&mut T` | 1 word | Yes (if `T: Send`) | Exclusive | In-place safe mutation |
| `Box<T>` | 1 word | Yes (if `T: Send`) | No | Heap allocation, breaking recursive types |
| `Rc<T>` | 2 words | **No** (Single thread) | With `RefCell` | Shared ownership within single thread |
| `Arc<T>` | 2 words | **Yes** (Atomic count) | With `Mutex`/`RwLock` | Shared ownership across threads |
| `Mutex<T>` | OS mutex | Yes (`Send + Sync`) | Yes (Exclusive lock) | Thread-safe mutable state |
| `RwLock<T>` | OS lock | Yes (`Send + Sync`) | Yes (Many readers/One writer) | Read-heavy thread-safe state |

### The `Send` and `Sync` Invariants
- `T: Send`: Ownership of `T` can be transferred safely across thread boundaries.
- `T: Sync`: References `&T` can be accessed concurrently by multiple threads (`T: Sync` $\iff$ `&T: Send`).
- Primitives and structs made of `Send` fields are automatically `Send`. Types with raw pointers (`*const T`, `*mut T`) or thread-unsafe wrappers (`Rc<T>`, `Cell<T>`) are `!Send` and `!Sync`.

### Lock Discipline Across Async Boundaries
- **Never** hold `std::sync::MutexGuard` or `parking_lot::MutexGuard` across an `.await` point. This leads to thread pool starvation and deadlocks.
- Scope locks narrowly so guards drop before calling async functions, or use `tokio::sync::Mutex` when the critical section must span an `.await`.
