---
name: high-throughput-logging
description: "Non-blocking, zero-allocation structured logging for Telegram bot factories in Rust (tracing + tracing-appender) and Go (zerolog / zap)."
version: 1.0.0
category: observability
author: Systems Observability Engineers
tags: [logging, tracing, tracing-appender, non-blocking, zerolog, zap, rust, go]
---

# High-Throughput Non-Blocking Logging Architecture

Handle millions of Telegram events per hour without blocking async Tokio workers or Goroutines.

## 1. Rust Tracing with Non-Blocking Worker Thread
```rust
use tracing_appender::non_blocking::WorkerGuard;

pub fn init_production_logging() -> WorkerGuard {
    let (non_blocking_writer, guard) = tracing_appender::non_blocking(std::io::stderr());
    tracing_subscriber::fmt()
        .with_writer(non_blocking_writer)
        .with_env_filter("info,guard_rust=debug")
        .json()
        .init();
    guard // Hold in main to prevent premature worker shutdown
}
```

## 2. Invariants for High-Scale Bots
1. **Never Write Synchronously to Disk on Tokio Threads**: Direct `std::fs::write` or sync `println!` halts the Tokio reactor.
2. **JSON Structured Output**: Always log machine-parseable fields: `bot_id`, `chat_id`, `update_id`, `latency_ms`.
3. **Log Scrubbing**: Automatically mask phone numbers, bot tokens, and user credentials.
