---
name: rust-async-patterns
description: Comprehensive guide for asynchronous Rust programming with Tokio. Covers task supervision (JoinSet), channel architectures (mpsc, broadcast, watch, oneshot), the actor pattern, cancellation safety in tokio::select!, graceful shutdown with CancellationToken, and zero-blocking I/O.
---

# Rust Async Patterns: Comprehensive Tokio Production Guide

Architect scalable, cancel-safe, and high-throughput concurrent systems using the Tokio runtime in Rust.

---

## 1. Async Runtime Architecture & Execution Model

Rust futures are **lazy**: no work is done until a future is polled by an executor.
```
Future (lazy) ─── poll(&mut Context) ───> Poll::Ready(Output) | Poll::Pending
                        ↑                                            │
                  Waker::wake() ◄── Event Registered on Reactor ─────┘
```

### Key Rules:
- **Never block the worker thread**: Wrap synchronous I/O or heavy CPU work in `tokio::task::spawn_blocking`.
- **Drop Mutex guards before await**: Never hold a `std::sync::MutexGuard` or `parking_lot::MutexGuard` across an `.await` boundary.
- **Cooperative Budget**: In long compute loops, invoke `tokio::task::yield_now().await` to prevent starving other tasks.

---

## 2. Pattern 1: Structured Task Execution & Supervision (`JoinSet`)

Avoid unmanaged, detached `tokio::spawn` calls. Track dynamic task pools using `tokio::task::JoinSet`:

```rust
use tokio::task::JoinSet;
use anyhow::Result;

pub async fn execute_batch_tasks<T, R, F, Fut>(items: Vec<T>, worker_fn: F) -> Result<Vec<R>>
where
    T: Send + 'static,
    R: Send + 'static,
    F: Fn(T) -> Fut + Send + Sync + 'static + Copy,
    Fut: std::future::Future<Output = Result<R>> + Send + 'static,
{
    let mut set = JoinSet::new();

    for item in items {
        set.spawn(async move {
            worker_fn(item).await
        });
    }

    let mut results = Vec::new();
    while let Some(res) = set.join_next().await {
        match res {
            Ok(Ok(value)) => results.push(value),
            Ok(Err(task_err)) => tracing::error!(%task_err, "Task returned domain error"),
            Err(join_err) if join_err.is_panic() => tracing::error!("Worker task panicked"),
            Err(join_err) => tracing::error!(%join_err, "Task join failed"),
        }
    }

    Ok(results)
}
```

### Bounded Concurrency Slicing (`buffer_unordered`)
When processing thousands of items, cap maximum concurrent network requests:
```rust
use futures::stream::{self, StreamExt};

pub async fn process_with_concurrency_limit<T, R, Fut>(
    items: Vec<T>,
    limit: usize,
    handler: impl Fn(T) -> Fut,
) -> Vec<R>
where
    Fut: std::future::Future<Output = R>,
{
    stream::iter(items)
        .map(handler)
        .buffer_unordered(limit) // Maximum concurrent in-flight requests
        .collect::<Vec<R>>()
        .await
}
```

---

## 3. Pattern 2: Channel Architectures & Backpressure

Tokio provides specialized channel types. Never default to unbounded channels:

### 1. `tokio::sync::mpsc` (Multi-Producer, Single-Consumer)
Use for worker task queues and ingestion pipelines:
```rust
let (tx, mut rx) = tokio::sync::mpsc::channel::<UpdatePayload>(1024);

// Producer: apply backpressure or load shed
tx.send(payload).await.map_err(|_| SystemError::ChannelClosed)?;

// Consumer worker loop:
while let Some(msg) = rx.recv().await {
    process_message(msg).await;
}
```

### 2. `tokio::sync::broadcast` (Fan-Out Pub/Sub)
Use when multiple independent subscribers must all receive every event:
```rust
let (tx, _) = tokio::sync::broadcast::channel::<SystemEvent>(256);
let mut rx1 = tx.subscribe();

// Handle lagging subscribers cleanly
match rx1.recv().await {
    Ok(event) => handle_event(event),
    Err(tokio::sync::broadcast::error::RecvError::Lagged(n)) => {
        tracing::warn!(skipped = n, "Slow consumer lagged behind event stream");
    }
    Err(tokio::sync::broadcast::error::RecvError::Closed) => return,
}
```

### 3. `tokio::sync::watch` (Latest State Distribution)
Use for shared configurations, health status, and metrics:
```rust
let (tx, rx) = tokio::sync::watch::channel(ServerStatus::Starting);

// Producer publishes new state:
tx.send(ServerStatus::Healthy).unwrap();

// Consumer checks latest state or awaits changes:
let current = *rx.borrow();
```

### 4. `tokio::sync::oneshot` (Request/Response Pairing)
Use for returning a value from an asynchronous worker task back to the caller:
```rust
let (tx, rx) = tokio::sync::oneshot::channel::<ResponseData>();
worker_tx.send(Command::Query { respond_to: tx }).await.unwrap();
let response = rx.await.map_err(|_| SystemError::WorkerDropped)?;
```

---

## 4. Pattern 3: The Actor Pattern in Rust

Instead of wrapping complex mutable shared state in `Arc<Mutex<State>>`, encapsulate state inside a dedicated background task and communicate via messages:

```rust
pub enum SessionCommand {
    Get { user_id: i64, respond_to: oneshot::Sender<Option<Session>> },
    Update { user_id: i64, data: Session, respond_to: oneshot::Sender<()> },
}

pub struct SessionActor {
    receiver: mpsc::Receiver<SessionCommand>,
    sessions: ahash::AHashMap<i64, Session>,
}

impl SessionActor {
    pub async fn run(mut self) {
        while let Some(cmd) = self.receiver.recv().await {
            match cmd {
                SessionCommand::Get { user_id, respond_to } => {
                    let _ = respond_to.send(self.sessions.get(&user_id).cloned());
                }
                SessionCommand::Update { user_id, data, respond_to } => {
                    self.sessions.insert(user_id, data);
                    let _ = respond_to.send(());
                }
            }
        }
    }
}
```

---

## 5. Pattern 4: Cancellation Safety in `tokio::select!`

When a `tokio::select!` branch completes, all other active branches are cancelled immediately by dropping their futures.

### Safe vs Unsafe Operations:
- **Cancel-Safe**: Simple channel `.recv()`, socket `.read()`, timer `.sleep()`, `watch::changed()`.
- **Cancel-Unsafe**: `AsyncWriteExt::write_all()`, reading lines from `BufReader`, multi-step database mutations.

### Idiomatic Racing Pattern:
```rust
use tokio::select;

loop {
    select! {
        // Safe: recv() is cancel-safe (message remains in queue if another branch wins)
        Some(msg) = rx.recv() => {
            handle_message(msg).await;
        }
        // Safe: cancellation token changed is cancel-safe
        _ = shutdown_token.cancelled() => {
            tracing::info!("Shutdown signal received, draining...");
            break;
        }
        // Safe: timeout expiration
        _ = tokio::time::sleep(Duration::from_secs(300)) => {
            heartbeat().await;
        }
    }
}
```

---

## 6. Pattern 5: Graceful Shutdown with `CancellationToken`

Coordinate clean termination across distributed workers:
```rust
use tokio_util::sync::CancellationToken;

let root_token = CancellationToken::new();

// Spawn child token for worker
let worker_token = root_token.child_token();
tokio::spawn(async move {
    loop {
        tokio::select! {
            _ = worker_token.cancelled() => {
                // Perform clean flush before exiting
                flush_to_disk().await;
                break;
            }
            update = fetch_update() => {
                process(update).await;
            }
        }
    }
});

// On OS signal (SIGINT / SIGTERM):
tokio::signal::ctrl_c().await.unwrap();
root_token.cancel(); // Propagates cancellation to all child tokens instantly
```
