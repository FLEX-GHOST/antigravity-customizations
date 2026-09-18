---
trigger: model_decision
description: "Official Rust API Guidelines (naming conventions, traits, conversions, borrowing idioms, type safety, and predictability)."
---

# Official Rust API Guidelines & Idiomatic Standards

Strictly enforce official Rust community design standards (rust-lang.github.io/api-guidelines) for readable, predictable, ergonomic, and future-proof public interfaces.

---

## 1. Naming Conventions (C-NAMING)

### Casing Standards (C-CASE)
- **UpperCamelCase**: Types, traits, enum names, and enum variants (`UpdateHandler`, `TenantSession`, `UserRole::SuperAdmin`).
- **snake_case**: Functions, methods, variables, and module names (`process_update`, `bot_id`, `handlers::callbacks`).
- **SCREAMING_SNAKE_CASE**: Constants and statics (`MAX_RETRY_ATTEMPTS`, `DEFAULT_TIMEOUT_SECS`).
- **Acronyms as Words (C-WORD-ORDER)**: Treat acronyms as ordinary words in camel-cased identifiers (`HttpServer` NOT `HTTPServer`, `JsonParser` NOT `JSONParser`, `BotId` NOT `BOTID`).

### Conversion Methods (C-CONV)
Adhere strictly to prefix semantics according to cost and ownership:
| Prefix | Cost | Ownership | Example Signature |
|---|---|---|---|
| `as_` | Free (zero-cost reference) | Borrowed $\rightarrow$ Borrowed | `fn as_bytes(&self) -> &[u8]` |
| `to_` | Expensive (allocation or computation) | Borrowed $\rightarrow$ Owned | `fn to_string(&self) -> String` |
| `into_` | Moves data (ownership transfer) | Consuming $\rightarrow$ Owned | `fn into_inner(self) -> T` |

### Getter and Accessor Conventions (C-GETTER)
- **No `get_` prefix for simple accessors**:
  - CORRECT: `tenant.id()`, `session.created_at()`, `bot.token()`.
  - FORBIDDEN: `tenant.get_id()`, `bot.get_token()`.
- **Mutable accessors must end with `_mut`**: `session.buffer_mut()`, `config.settings_mut()`.
- **Reserve `get_` prefix for fallible lookups or searches**: `map.get(&key)` returning `Option<&V>`, or when an accessor requires parameters to retrieve data.

### Iterator Conventions (C-ITER & C-ITER-TY)
- Methods producing iterators must follow standard naming:
  - `iter(&self)` $\rightarrow$ yields shared references `&T`.
  - `iter_mut(&mut self)` $\rightarrow$ yields mutable references `&mut T`.
  - `into_iter(self)` $\rightarrow$ consumes self and yields owned values `T`.
- The iterator types must match the method name: `Iter`, `IterMut`, `IntoIter`.

---

## 2. Common Trait Implementations (C-COMMON-TRAITS)

### Standard Trait Derivations
- **Universal Debug**: Every public type must implement `std::fmt::Debug`. Never leave a public struct or enum without `Debug`.
- **Value Semantics**: Derive or implement `Clone`, `PartialEq`, `Eq`, `Default`, and `Hash` whenever semantically meaningful and valid for the type's domain:
  - If `PartialEq` is implemented, implement `Eq` unless floating-point values or non-reflexive equality is present.
  - Implement `Default` instead of a zero-argument `new()` method that takes no arguments, or make `new()` call `Default::default()`.
- **Display vs Debug**:
  - `Display` is for user-facing, localized, or end-user rendering.
  - `Debug` is for developer diagnostics, debugging, and tracing. Never use `Debug` strings for end-user UI or database keys.
- **Concurrency Safety Markers (`Send + Sync`)**:
  - Public types representing shared state, background workers, or caches must implement `Send + Sync`.
  - Avoid raw pointers or non-thread-safe containers (`Rc`, `RefCell`) in public interfaces of multi-threaded or async libraries.

---

## 3. Ergonomic Borrowing & Parameter Flexibility (C-BORROW & C-CONV)

### Slices Over Owned Collections (C-BORROW)
- Always accept borrowed slices instead of references to owned containers:
  - Accept `&str` instead of `&String`.
  - Accept `&[T]` instead of `&Vec<T>`.
  - Accept `&Path` or `impl AsRef<Path>` instead of `&PathBuf`.
- **Borrowing vs Moving**:
  - Pass by value (`T`) when the function unconditionally takes ownership, stores, or sinks the data.
  - Pass by reference (`&T`) when the function only needs to read or inspect the data.

### Idiomatic Conversions (C-FROM-NOT-INTO)
- **Implement `From<T>`, not `Into<U>`**: Implementing `From<T> for U` automatically provides `Into<U> for T` via blanket implementation. Never implement `Into` directly unless `From` cannot be implemented due to orphan rules.
- **Accept `impl Into<T>` for Constructors**: For constructors and setters, accepting `impl Into<String>` or `impl Into<PathBuf>` provides maximum caller ergonomics without sacrificing efficiency.

---

## 4. Type-Driven Safety & Invariants (C-TYPE)

### Newtype Pattern (C-NEWTYPE)
- Wrap primitive integers and strings into domain-specific newtypes to prevent parameter confusion bugs:
  ```rust
  #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
  pub struct BotId(pub i64);

  #[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
  pub struct UserId(pub i64);
  ```
- Functions must take `(bot_id: BotId, user_id: UserId)` instead of `(i64, i64)`.

### Make Invalid States Unrepresentable
- Use enums with variant-specific data rather than structs with multiple optional fields:
  ```rust
  // BAD: multiple optional fields with loose temporal coupling
  pub struct Session {
      pub is_authenticated: bool,
      pub auth_token: Option<String>,
      pub failed_attempts: u32,
  }

  // GOOD: impossible to represent unauthenticated session with a token
  pub enum SessionState {
      Anonymous { failed_attempts: u32 },
      Authenticated { token: String, expires_at: u64 },
  }
  ```

### Builder Pattern with `#[must_use]` (C-BUILDER)
- Use the builder pattern for types with multiple optional configuration parameters:
  - Separate `ConfigBuilder` from the resulting immutable `Config`.
  - Mark builder mutation methods and construction methods with `#[must_use]`.
  - Consume self (`self`) in chaining methods for zero-cost moves:
  ```rust
  #[derive(Default)]
  pub struct BotConfigBuilder {
      timeout_secs: Option<u64>,
      max_connections: Option<usize>,
  }

  impl BotConfigBuilder {
      #[must_use]
      pub fn timeout_secs(mut self, secs: u64) -> Self {
          self.timeout_secs = Some(secs);
          self
      }

      pub fn build(self) -> Result<BotConfig, ConfigError> { ... }
  }
  ```

---

## 5. Predictability & Principle of Least Surprise (C-PREDICTABLE)

### Overloaded Operators (C-OPERATOR)
- Implement `std::ops` traits (`Add`, `Sub`, `Index`, `Deref`) only when the semantics are mathematically or conceptually natural and unsurprising.
- Never implement `Deref` / `DerefMut` solely to emulate inheritance. `Deref` is reserved strictly for smart pointer types (`Box`, `Arc`, `Ref`, `CustomGuard`).

### Pure Functions & Side Effects
- Methods named with nouns or standard adjectives (`len()`, `is_empty()`, `capacity()`) must be pure, non-blocking, and free of side effects.
- Methods that mutate internal state or perform I/O must use active verb phrases (`update_status()`, `flush_buffer()`, `sync_to_disk()`).

---

## 6. Dependability & Panic Safety (C-FAILURE)

### Recoverable Errors vs Invariant Violations
- **Return `Result<T, E>` for all recoverable operational failures**: Network errors, parsing failures, timeouts, missing database records, and invalid inputs.
- **Prohibit `.unwrap()` and `.expect()` in runtime code**:
  - Never call `.unwrap()` or `.expect()` in handlers, worker loops, or request parsers.
  - Handle missing collection elements with `.get(idx)` and pattern matching (`if let Some(...) = ...`) rather than direct indexing (`slice[idx]`).
- **Panic Conditions**:
  - Reserve `panic!` strictly for violated unrecoverable internal invariants that indicate a bug in the code itself.
  - If a function can panic under specific arguments, it MUST be prominently documented in a dedicated `# Panics` docstring section.

---

## 7. Documentation Standards (C-DOC)

### Comprehensive Docstrings
- Every public module, struct, enum, variant, function, and trait must have a descriptive `///` or `//!` docstring.
- Structure fallible and complex function documentation with standard sections:
  - `# Arguments`: Parameter constraints and semantic meanings.
  - `# Errors`: Exact error conditions and returned error variants.
  - `# Panics`: Any edge case that could trigger a panic.
  - `# Safety`: Mandatory for all `unsafe fn`, detailing invariants callers must uphold.
  - `# Examples`: Runnable, compiling doctests asserting expected behavior.

---

## 8. Future-Proofing & Extensibility (C-FUTURE-PROOF)

### Forward Compatibility (C-NON-EXHAUSTIVE)
- Mark public structs and enums that may gain new fields or variants in future releases with `#[non_exhaustive]`:
  ```rust
  #[non_exhaustive]
  #[derive(Debug, Clone, PartialEq, Eq)]
  pub enum UpdateKind {
      Message(Message),
      CallbackQuery(Callback),
      InlineQuery(InlineQuery),
  }
  ```
  This prevents breaking downstream consumers when new variants or fields are introduced.

### Sealed Traits Pattern (C-SEALED)
- When a public trait must be implemented only by your crate (and not by downstream consumers), use the sealed trait pattern:
  ```rust
  mod private {
      pub trait Sealed {}
  }

  pub trait InternalUpdate: private::Sealed {
      fn dispatch(&self);
  }
  ```
