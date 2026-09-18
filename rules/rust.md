---
trigger: model_decision
description: Rust systems development, memory safety, tokio async, lock discipline, allocation policy, and fast dev build velocity
---

# Rust Systems & Async Rules

Senior Rust systems engineer. Production-grade, safe, high-performance, and memory-efficient.

## 1. Ownership & Memory Efficiency
- **Borrow First**: Prefer borrowing (`&T`, `&str`) over `.clone()` unless transfer of ownership is strictly necessary.
- **Bounded Buffers**: Never store raw media/audio bytes in long-lived structs; stream in chunks or cache to disk with explicit TTL.
- **Allocator Hygiene**: Use jemalloc with background purging (`background_thread:true,dirty_decay_ms:0`) for long-running daemons. Cap all in-memory caches and `DashMap` instances.

## 2. Concurrency & Tokio Async
- **No Blocking Locks across Await**: Never hold `std::sync::MutexGuard` across an `.await` point. Use `tokio::sync::Mutex` only when necessary, or restructure code to drop the guard before yielding.
- **Offload Blocking Operations**: Wrap CPU-heavy computations, cryptography, and blocking file/FFI calls in `tokio::task::spawn_blocking`.
- **Cancellation Safety**: Ensure futures dropped inside `tokio::select!` or on timeout do not leave shared state inconsistent.

## 3. Errors & Production Quality
- **Structured Errors**: Use `thiserror` for domain libraries and `anyhow` with context for applications.
- **No Production Panics**: Avoid `.unwrap()` and `.expect()` in runtime code; propagate via `?` or handle with structured recovery paths.

## 4. Fast Development & Build Velocity
- **No Release Builds in Development**: Never run full `--release` builds (with LTO and single codegen unit) during rapid iteration. Always use incremental dev builds (`cargo build` / `./start dev`).
- **Live Auto-Reloading**: Use `cargo watch` (`./start watch`) for instant rebuilds upon file changes.
- **Instant Type-Checking**: Use `cargo check` (`./start check`) for syntax and type validation (< 2s) before compiling binaries.
- **Single Source of Truth**: Keep production release profiles (`lto = "thin"`, `codegen-units = 1`) strictly for final deployment.

- **Linker Speed (Mold Standard)**: Always use  as default linker ( via ) in  on Linux for parallel linking (< 2s). Never downgrade to  or .
