---
trigger: model_decision
description: "Production error handling, thiserror vs anyhow architecture, zero-panic discipline, and Telegram FloodWait backoff."
---

# Rust Production Error Handling & Resilient Backoff Architecture

Enforce structured error architecture, zero-panic runtime discipline, context preservation, and resilient rate-limiting backoff.

---

## 1. Domain Errors vs Application Context (`thiserror` vs `anyhow`)

### Architectural Error Boundary Separation
- **Subsystem & Domain Modules (`thiserror`)**:
  - Every core module (`bot`, `factory`, `db`, `handlers`, `webhook`, `config`) must define strongly-typed domain error enums using `thiserror::Error`.
  - Enables callers to programmatically inspect, match, and recover from specific error conditions.
- **Application Edge & Top-Level Entrypoints (`anyhow`)**:
  - Use `anyhow::Result` exclusively at the edge of the binary (`main.rs`, CLI entrypoints).
  - Attach operational context using `.context("...")` or `.with_context(|| ...)` before bubbling errors to the top.

### Error Enum Design & Stack Bloat Prevention
- Use `#[from]` for zero-boilerplate conversions, and `#[source]` to preserve underlying error causes:
  ```rust
  #[derive(thiserror::Error, Debug)]
  pub enum FactoryError {
      #[error("database query failed: {0}")]
      Database(#[from] sqlx::Error),

      #[error("telegram client error: {0}")]
      Telegram(#[from] grammers_client::InvocationError),

      #[error("tenant bot {0} not found")]
      TenantNotFound(i64),

      // Box large foreign error variants to keep Result<T, E> stack footprint minimal
      #[error("auth negotiation failed: {0}")]
      AuthFailed(#[source] Box<grammers_client::SignInError>),
  }
  ```
- **Enum Size Rule**: If an error payload variant is large (> 64 bytes), wrap it in `Box<T>`. This ensures `Result<T, E>` remains small and cache-friendly on the function call stack.
- **Message Formatting**: Start error strings in lowercase without trailing punctuation (`#[error("failed to load configuration")]`).

---

## 2. Zero-Panic Runtime Discipline

### Absolute Ban on `.unwrap()` and `.expect()` in Production Code
- Never call `.unwrap()` or `.expect()` in update handlers, webhook receivers, database queries, or background worker loops.
- Handle fallible outcomes using:
  - The `?` operator for clean propagation.
  - Pattern matching (`match` or `if let Some(...) = ...`).
  - Safe fallbacks (`unwrap_or_default()`, `unwrap_or_else()`).
- **The Role of `panic!`**:
  - Reserve `panic!` strictly for violated unrecoverable code invariants that indicate bugs in the program logic (e.g., internal state machine transitions that are mathematically impossible).
  - Never use `panic!` for expected runtime failures (bad network, invalid user input, malformed JSON, database timeouts).

### Safe Slice, Array & Map Indexing
- Never index slices or vectors directly (`vec[index]`). If `index >= vec.len()`, Rust triggers an immediate runtime panic, killing the process.
- **MANDATORY**: Always use `.get(index)` and handle the resulting `Option<&T>`:
  ```rust
  // FORBIDDEN: Panics on unexpected payload length
  let command = tokens[0];

  // MANDATORY: Safe slice access
  let command = tokens.get(0).copied().unwrap_or("");
  ```

---

## 3. Telegram FloodWait & Rate Limit Handling

### Dynamic FloodWait Backoff
Telegram MTProto and Bot API strictly enforce rate limits via `FloodWait` (HTTP 420). Calling Telegram APIs in a tight loop during a FloodWait will result in exponential penalty escalation and temporary IP bans.
- **Dynamic Catch & Sleep Architecture**:
  ```rust
  pub async fn execute_with_floodwait<F, Fut, T>(mut action: F) -> Result<T, FactoryError>
  where
      F: FnMut() -> Fut,
      Fut: std::future::Future<Output = Result<T, FactoryError>>,
  {
      let mut attempts = 0;
      loop {
          attempts += 1;
          match action().await {
              Ok(value) => return Ok(value),
              Err(FactoryError::Telegram(grammers_client::InvocationError::Rpc(rpc_err))) 
                  if rpc_err.code == 420 || rpc_err.name.starts_with("FLOOD_WAIT_") => 
              {
                  let wait_secs = rpc_err.value.unwrap_or(5) as u64;
                  // Add random jitter (100ms - 1000ms) to prevent thundering herd
                  let jitter_ms = rand::random::<u64>() % 900 + 100;
                  let total_wait = Duration::from_secs(wait_secs) + Duration::from_millis(jitter_ms);
                  
                  tracing::warn!(wait_secs, attempts, "Telegram FloodWait encountered, sleeping");
                  tokio::time::sleep(total_wait).await;
              }
              Err(err) if attempts < 3 && is_transient_network_error(&err) => {
                  let backoff = Duration::from_millis(200 * (1 << attempts));
                  tracing::warn!(attempts, ?backoff, "Transient network failure, retrying");
                  tokio::time::sleep(backoff).await;
              }
              Err(err) => return Err(err),
          }
      }
  }
  ```

---

## 4. Context Preservation & Error Chaining

### Never Swallow Errors
- Never discard `Result` using `let _ = fallible_call();` or empty match arms without an explicit, documented reason.
- When transforming or mapping errors, always preserve the underlying root cause:
  ```rust
  // BAD: Discards the database error details
  let user = db.get_user(id).map_err(|_| AppError::UserNotFound)?;

  // GOOD: Preserves cause and adds operational context
  let user = db.get_user(id)
      .with_context(|| format!("failed to load user {id} from database"))?;
  ```

---

## 5. Task Isolation & Panic Boundaries

### Supervising Task Panics in Multi-Tenant Systems
In a bot factory multiplexing thousands of bots, an unforeseen panic in a single tenant handler must NEVER crash the entire process daemon.
- Use `tokio::spawn` as an isolation boundary. A panic inside a spawned task is caught by Tokio and returned as `JoinError::Panic`:
  ```rust
  let handle = tokio::spawn(async move {
      tenant_handler.handle_update(update).await
  });

  match handle.await {
      Ok(Ok(())) => {},
      Ok(Err(app_err)) => tracing::error!(%app_err, "Tenant update failed"),
      Err(join_err) if join_err.is_panic() => {
          tracing::error!(tenant_id, "Tenant update task panicked, recovering gracefully");
          // Increment panic metrics and continue running
      }
      Err(join_err) => tracing::error!(%join_err, "Tenant task cancelled"),
  }
  ```
