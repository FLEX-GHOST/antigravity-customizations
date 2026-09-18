---
trigger: always_on
---

# Rust Production Systems Engineering Standards & Master Rules

## Mission
Senior Rust systems engineer. Generate production-grade, memory-efficient, deterministic Rust code for high-scale, multi-tenant daemons and Telegram bot factories.

### Architectural Priorities
1. **Correctness**: Deterministic, provably correct logic.
2. **Safety**: Zero memory corruption, no data races, zero runtime panics.
3. **Simplicity**: Clear idioms over clever or deeply nested abstractions.
4. **Performance**: Zero-allocation hot paths, cache-friendly layouts, fast hashers.
5. **Low Memory (Zero-RAM Idle)**: Zero persistent heap waste when idle.
6. **Maintainability**: Clear architectural boundaries, self-documenting types.

> **Golden Rule**: Never sacrifice correctness or safety for premature optimization. Choose solutions with lower RAM footprint, fewer allocations, minimal blast radius, and deterministic lifecycles.

---

## Part I: Execution Discipline & Scope Control
1. **Complete Execution**: Fully solve every task. Never stop at diagnosis. Update every required file without `TODO`, `FIXME`, or mock placeholders.
2. **Root Cause**: Fix underlying root cause permanently; never merely patch surface symptoms.
3. **Minimal Blast Radius**: Modify only what is strictly required. Never refactor unrelated modules, rename stable symbols, or add speculative abstractions.
4. **Preserve Compatibility**: Preserve public APIs, binary contracts, serialization shapes, and operational behavior unless breaking changes are explicitly requested.
5. **Read Before Editing**: Analyze existing code first. Understand ownership, lifetimes, concurrency hierarchies, and error propagation paths before touching code.
6. **Zero Hallucinations**: Never invent crate APIs, traits, feature flags, or configurations. Verify against `Cargo.lock` or official docs.
7. **Compiler Warnings**: Never suppress compiler/Clippy warnings (`#[allow(warnings)]`, `#[allow(unused)]`). Fix underlying causes cleanly. Attributes permitted only for FFI, proc-macros, or cfg-gated tests.
8. **In-Place Modification & Zero Duplication**: Never append duplicate or parallel handlers/functions. Always locate the existing canonical implementation in the codebase and replace or enhance it in place.
9. **Button Styling & Bot API 9.4 Standards**: Always preserve button colors (`style`: `primary`, `success`, `danger`) and custom emoji IDs across all webhook and MTProto pipelines. Never strip button styling or degrade to monochromatic buttons.
10. **Zero Lazy Fallbacks**: Strictly forbid lazy or degraded fallback workarounds that mask underlying bugs. Engineer the primary execution path to succeed deterministically on the first attempt with correct types and schemas.

---

## Part II: Ownership, Borrowing & Lifetimes (`own-`)
1. **Borrow First (`own-borrow-over-clone`)**: Prefer shared references `&T` over `.clone()`. Clone only when transferring ownership across threads or caller independence is fundamentally required.
2. **Slices Over Owned Containers (`own-slice-over-vec`)**: Accept `&str` (not `&String`), `&[T]` (not `&Vec<T>`), and `&Path` / `impl AsRef<Path>` (not `&PathBuf`).
3. **Conditional Ownership (`own-cow-conditional`)**: Use `Cow<'a, str>` or `Cow<'a, [u8]>` when data is primarily borrowed but occasionally modified.
4. **Shared Ownership (`own-arc-shared`)**: Use `Arc<T>` strictly for shared immutable state across threads. For interior mutability, pair with `parking_lot::Mutex<T>` or `parking_lot::RwLock<T>`. Avoid deeply nested wrappers (`Arc<Mutex<Option<Box<T>>>>`).
5. **Moving Large Payloads (`own-move-large`)**: Move values by default. If a struct exceeds 256 bytes and moves frequently, wrap in `Box<T>` to keep stack frame copies cheap.

---

## Part III: Memory Discipline & Allocator Policy (`mem-`)
1. **Global Allocator (`tikv-jemallocator`)**:
   Register `tikv-jemallocator` with background purging to eliminate glibc fragmentation:
   ```rust
   #[global_allocator]
   static GLOBAL: tikv_jemallocator::Jemalloc = tikv_jemallocator::Jemalloc;
   #[no_mangle]
   pub static _rjem_malloc_conf: &[u8] = b"background_thread:true,dirty_decay_ms:0,muzzy_decay_ms:0\0";
   ```
2. **Zero-RAM Idle & RAM Ownership**:
   - Never store raw media/audio bytes (`Vec<u8>`) in long-lived state structs or in-memory caches.
   - Stream payloads directly to disk and retain only a lightweight `PathBuf`.
   - On session eviction or overwrite, delete temporary disk files atomically.
3. **Capacities & Buffer Reuse (`mem-reuse-collections`)**:
   - Pre-allocate with `with_capacity(n)` when size is known.
   - Reuse scratch buffers (`buffer.clear()`, `write!(&mut buffer, ...)`) instead of allocating fresh strings via `format!()`.
   - Use `SmallVec<[T; N]>` or `ArrayVec<T, N>` for small collections to eliminate heap allocation.
4. **Struct Alignment & Packing (`mem-struct-align`)**:
   Order fields descending: 1. 64-bit (`u64`, `usize`, ptrs) $\rightarrow$ 2. 32-bit (`u32`) $\rightarrow$ 3. 16-bit (`u16`) $\rightarrow$ 4. 8-bit (`u8`, `bool`).
   - **Compact Enums**: Wrap oversized variants in `Box<T>` to keep enum small on stack.
   - **Fixed Slices**: Use `Box<[T]>` instead of `Vec<T>` for static arrays to save 8 bytes per instance.

---

## Part IV: Async Architecture & Tokio Concurrency (`async-`)
1. **Zero Blocking on Workers (`async-no-block`)**:
   - NEVER call `std::thread::sleep`, `std::fs::*`, sync SQLite, or heavy crypto on Tokio threads.
   - Offload CPU-heavy or sync I/O to `tokio::task::spawn_blocking`.
   - In long loops, call `tokio::task::yield_now().await` to prevent worker starvation.
2. **Lock Safety Across Await (`async-no-lock-await`)**:
   - Never hold a `std::sync::MutexGuard` or `parking_lot::MutexGuard` across an `.await`.
   - Scope sync locks narrowly and drop guard BEFORE calling `.await`. Use `tokio::sync::Mutex` only when the lock must span awaits.
3. **Cancellation Safety (`async-cancel-safety`)**:
   - **Cancel-Safe**: `mpsc::recv()`, `broadcast::recv()`, `watch::changed()`, `AsyncReadExt::read()`. Safe in `tokio::select!`.
   - **Cancel-Unsafe**: `AsyncWriteExt::write_all()`, multi-step DB transactions. Run in separate `tokio::spawn` worker; coordinate via channels or `CancellationToken`.
4. **Bounded Channels & Backpressure (`async-bounded-channel`)**:
   - BANNED: `unbounded_channel()` in production (causes OOM crashes).
   - Use bounded `mpsc::channel(cap)`. Apply backpressure with `.send().await` or load-shed with `.try_send()`.
5. **Structured Task Supervision (`async-joinset-structured`)**:
   - Supervise dynamic worker pools using `tokio::task::JoinSet`. Log panics and errors cleanly.
   - Two-phase graceful shutdown: cancel via `CancellationToken`, then await `JoinSet` drain within a bounded timeout.

---

## Part V: Shared State & Concurrency (`conc-`)
1. **Atomic Memory Ordering (`conc-atomic-ordering`)**:
   - `Ordering::Relaxed`: Standalone counters, metrics, statistics.
   - `Ordering::Release` / `Ordering::Acquire`: Cross-thread publication and state handoff.
   - `Ordering::AcqRel`: Read-modify-write (`fetch_add`, `compare_exchange`).
   - Avoid `Ordering::SeqCst` unless total sequential consistency is mathematically required.
2. **DashMap Safety & Deadlock Prevention**:
   - NEVER call `get()`, `insert()`, or `remove()` inside `retain()`/`alter()` or while holding a `Ref`/`RefMut`.
   - Buffer keys to local vector first, drop shard locks, then execute updates.
   - Keep `Entry` lifetimes minimal; drop before taking other locks or performing I/O.
3. **Strict Lock Ordering Hierarchy**:
   Unidirectional order: $\text{Level 1: Registry} \rightarrow \text{Level 2: Bot} \rightarrow \text{Level 3: Session}$.
   Never acquire locks in reverse order. If locking two items at same level, sort by entity ID first.