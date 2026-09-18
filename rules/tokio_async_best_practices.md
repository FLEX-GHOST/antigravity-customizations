---
trigger: model_decision
description: "Tokio async best practices (non-blocking workers, cross-await lock rules, cancellation safety matrix, bounded channels, JoinSet supervision)."
---

# Tokio Async Architecture & Production Concurrency Standards

Enforce official Tokio team standards and high-throughput async resilience for multi-tenant, high-concurrency systems.

---

## 1. Zero Blocking on Async Worker Threads

### Absolute Prohibition of Blocking Calls
Tokio worker threads execute a cooperative task scheduler. Any blocking system call freezes the thread's event reactor and starves all other tasks multiplexed on that worker thread:
- **STRICTLY FORBIDDEN on async threads**:
  - `std::thread::sleep` $\rightarrow$ Use `tokio::time::sleep`.
  - Synchronous filesystem calls (`std::fs::*`, `std::io::Read/Write` on files) $\rightarrow$ Use `tokio::fs` or `spawn_blocking`.
  - Synchronous networking (`std::net::*`) $\rightarrow$ Use `tokio::net::*`.
  - Blocking database queries (synchronous SQLite, blocking r2d2 pools) $\rightarrow$ Offload to `spawn_blocking` or use async drivers.
  - Heavy CPU computations, encryption/decryption (`argon2`, RSA, PBKDF2, AES), and audio transcoding $\rightarrow$ Must be offloaded to `spawn_blocking`.

### The `spawn_blocking` Offload Pattern
Wrap CPU-intensive or synchronous I/O operations in `tokio::task::spawn_blocking` with explicit error propagation:
```rust
let compressed_data = tokio::task::spawn_blocking(move || {
    compress_payload(&raw_data)
})
.await
.map_err(|e| SystemError::TaskJoinFailed(e))??;
```

### Cooperative Scheduling & Budgeting
- Tokio executes tasks in cooperative 128-tick batches before checking other work.
- In long-running CPU loops (e.g., parsing thousands of incoming updates or processing large batches), periodically invoke `tokio::task::yield_now().await` to return execution time to the reactor and prevent task starvation.

---

## 2. Lock Safety Across `.await` Boundaries

### Strict Prohibition of Synchronous Guards Across Await
Never hold a `std::sync::MutexGuard` or `parking_lot::MutexGuard` across an `.await` point. If a thread yields while holding a synchronous guard, another worker thread attempting to acquire the lock will deadlock the runtime.

### Recommended Patterns:
#### Pattern 1: Narrowly-Scoped Synchronous Lock (Preferred)
Keep critical sections minimal, synchronous, and non-suspending:
```rust
// CORRECT: lock is acquired, state is updated, and guard is dropped BEFORE await
let payload = {
    let mut state = self.session_state.lock();
    state.prepare_and_drain_updates()
}; // MutexGuard dropped here

// Safe to await over network
self.http_client.send_updates(payload).await?;
```

#### Pattern 2: `tokio::sync::Mutex` (Only When Holding Across Await Is Unavoidable)
Use `tokio::sync::Mutex` exclusively when internal state must remain locked while an asynchronous operation is in flight. Always minimize the critical section duration:
```rust
let mut connection = self.async_connection.lock().await;
connection.write_message_frame(&frame).await?;
```

---

## 3. Comprehensive Cancellation Safety Matrix (`tokio::select!`)

### Cancellation Mechanics
When a branch in `tokio::select!` completes, all other pending branches are dropped immediately at their current yield point. If a future is cancelled midway through a non-atomic operation, state corruption or data loss occurs.

### Cancellation Safety Matrix:
| Operation | Safety Status | Behavioral Impact When Cancelled | Correct Mitigation |
|---|---|---|---|
| `tokio::sync::mpsc::Receiver::recv()` | **CANCEL-SAFE** | No item lost; item remains in queue until fully returned. | Safe to use directly in `select!`. |
| `tokio::sync::broadcast::Receiver::recv()` | **CANCEL-SAFE** | Message not lost if not returned. | Safe to use directly in `select!`. |
| `tokio::sync::watch::Receiver::changed()` | **CANCEL-SAFE** | Mark as changed retained. | Safe to use directly in `select!`. |
| `tokio::io::AsyncReadExt::read()` | **CANCEL-SAFE** | Bytes not read remain in socket/stream. | Safe to use directly in `select!`. |
| `tokio::net::TcpListener::accept()` | **CANCEL-SAFE** | Uncompleted connection remains in backlog. | Safe to use directly in `select!`. |
| `tokio::io::AsyncWriteExt::write_all()` | **CANCEL-UNSAFE** | Partial bytes written; remainder lost, corrupting stream framing. | Buffer full payload or offload to background task. |
| `tokio::io::AsyncBufReadExt::lines()` | **CANCEL-UNSAFE** | Partial line buffer discarded on drop. | Use a stateful line reader struct. |
| Multi-step database updates | **CANCEL-UNSAFE** | Intermediate state committed, subsequent steps aborted. | Wrap in transactions or run in separate `tokio::spawn`. |

### Architectural Mitigation for Cancel-Unsafe Work
When executing cancel-unsafe tasks alongside timers or cancel tokens:
1. Spawn the task as an independent `tokio::spawn` worker.
2. Communicate with the worker via cancel-safe `oneshot` or `mpsc` channels.
3. Coordinate termination cleanly using `tokio_util::sync::CancellationToken`.

---

## 4. Bounded Channels & Backpressure Control

### Complete Ban on Unbounded Channels
Never call `tokio::sync::mpsc::unbounded_channel` in production ingest pipelines or bot dispatchers. Under load spikes or upstream network pauses, unbounded channels buffer unlimited messages in RAM until an Out-Of-Memory (OOM) process termination occurs.

### Production Channel Architecture:
- **`tokio::sync::mpsc::channel(capacity)`**:
  - Worker task dispatching and update ingestion.
  - Set explicit bounds (e.g., 256 to 4096 depending on payload size).
  - Handle backpressure:
    - Normal backpressure: Call `.send(item).await` to naturally pace upstream producers.
    - Load-shedding backpressure: Call `.try_send(item)` and immediately reject or log HTTP 429 when the queue is saturated.
- **`tokio::sync::broadcast::channel(capacity)`**:
  - Pub/Sub message fan-out to multiple subscribers.
  - Must explicitly handle `RecvError::Lagged(missed_count)` to recover gracefully when slow subscribers lag.
- **`tokio::sync::watch::channel(initial)`**:
  - Global configuration distribution and status monitoring.
  - Stores only the single latest value; consumers never lag.
- **`tokio::sync::oneshot::channel()`**:
  - Request/Response pairing between tasks.

---

## 5. Structured Task Management & Graceful Shutdown

### Avoid Fire-and-Forget `tokio::spawn` Leaks
Detached `tokio::spawn` calls without supervision lead to silent task panics, leaked resources, and zombie tasks.
- **Supervision with `tokio::task::JoinSet`**:
  ```rust
  let mut join_set = tokio::task::JoinSet::new();

  for tenant in active_tenants {
      join_set.spawn(async move {
          tenant.run_worker().await
      });
  }

  // Drain and observe task terminations
  while let Some(res) = join_set.join_next().await {
      match res {
          Ok(Ok(())) => tracing::info!("Tenant worker finished cleanly"),
          Ok(Err(err)) => tracing::error!(%err, "Tenant worker returned error"),
          Err(join_err) => tracing::error!(%join_err, "Tenant worker panicked"),
      }
  }
  ```

### Two-Phase Graceful Shutdown Protocol
1. **Signal Dissemination**:
   - Disseminate shutdown via `tokio_util::sync::CancellationToken`.
   - Close incoming listeners and webhooks immediately.
2. **Bounded Drain Interval**:
   - Wrap worker draining in `tokio::time::timeout`:
   ```rust
   let shutdown_token = CancellationToken::new();
   // ... run application ...
   
   // On SIGINT / SIGTERM:
   shutdown_token.cancel();
   if let Err(_) = tokio::time::timeout(Duration::from_secs(15), join_set.shutdown()).await {
       tracing::warn!("Graceful shutdown timed out, aborting lingering tasks");
   }
   ```

---

## 6. Async I/O, Timers & Connection Pooling

### Mandatory I/O Timeouts
Every outbound network request, remote API call, and database connection acquisition must be wrapped in an explicit timeout:
```rust
match tokio::time::timeout(Duration::from_secs(5), client.execute_query()).await {
    Ok(Ok(data)) => Ok(data),
    Ok(Err(err)) => Err(AppError::Network(err)),
    Err(_) => Err(AppError::Timeout("Database query exceeded 5s".into())),
}
```

### Connection Pool Re-use
- Share a single `reqwest::Client` or outbound HTTP/2 client across all bots and tasks.
- Never instantiate an HTTP client inside a per-update handler or tight loop. Re-use internal connection pools and DNS caches.
