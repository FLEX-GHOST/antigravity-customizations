---
trigger: model_decision
description: "Rust concurrency, shared state, DashMap deadlock prevention, atomic memory ordering, and lock hierarchies."
---

# Rust Concurrency, Shared State & Deadlock Prevention

Enforce production-grade multi-threaded synchronization patterns, strict lock ordering hierarchies, atomic memory ordering discipline, and concurrent collection safety.

---

## 1. Atomic Primitives & Memory Ordering Discipline

### Minimize Mutex Overhead with Atomics
For primitive counters, flags, and metrics, use `std::sync::atomic` types (`AtomicBool`, `AtomicUsize`, `AtomicI64`, `AtomicU64`) instead of wrapping primitives in `Mutex` or `RwLock`.

### Memory Ordering Selection Guide:
Never default blindly to `Ordering::SeqCst`. Select the weakest ordering that guarantees correctness:
- **`Ordering::Relaxed`**:
  - Use for standalone metrics, request counters, throughput counters, and statistics.
  - Guarantees atomicity of the operation, but enforces NO happens-before relationships or memory ordering barriers with other memory locations.
  ```rust
  self.total_processed_updates.fetch_add(1, Ordering::Relaxed);
  ```
- **`Ordering::Release` (Store) & `Ordering::Acquire` (Load)**:
  - Use for synchronizing state changes between threads (message passing, publication).
  - An `Acquire` load observes all memory writes performed before the corresponding `Release` store:
  ```rust
  // Producer thread:
  self.shared_buffer.write_payload(data);
  self.is_ready.store(true, Ordering::Release);

  // Consumer thread:
  if self.is_ready.load(Ordering::Acquire) {
      let data = self.shared_buffer.read_payload(); // Guaranteed valid and visible
  }
  ```
- **`Ordering::AcqRel`**:
  - Use for read-modify-write operations (`compare_exchange`, `fetch_add`) that simultaneously synchronize prior writes and publish new state.
- **`Ordering::SeqCst`**:
  - Enforces a globally consistent execution order across all threads.
  - Incurs heavy memory bus fencing overhead on multi-core CPUs. Use ONLY when multiple atomic variables participate in an interleaved protocol that requires total sequential consistency.

---

## 2. Concurrent Sharded Maps (`DashMap`) & Deadlock Prevention

### Shard Locking Mechanics
`DashMap` partitions keys across multiple internal shards, each protected by an independent `RwLock`. Operating on multiple keys or calling map operations from within callbacks can easily trigger deadlocks.

### Strict DashMap Operational Rules:
1. **Never Nest Lookups or Mutations Inside Iterators/Callbacks**:
   - FORBIDDEN: Invoking `map.get()`, `map.insert()`, or `map.remove()` from inside `map.retain(...)`, `map.alter(...)`, or while holding a `Ref` / `RefMut`.
   - Reason: If the second operation accesses a key that hashes to the same shard currently locked by the callback/guard, the thread permanently deadlocks itself.
2. **Buffer Keys Before Complex Operations**:
   ```rust
   // CORRECT: Collect keys to a temporary local vector first, dropping all shard locks
   let keys_to_evict: Vec<TenantId> = self.tenants
       .iter()
       .filter(|entry| entry.value().is_expired())
       .map(|entry| *entry.key())
       .collect();

   // Now safely remove, acquiring one shard at a time
   for key in keys_to_evict {
       self.tenants.remove(&key);
   }
   ```
3. **Entry Handle Lifetime Scope**:
   - Keep `dashmap::mapref::entry::Entry` handles as short-lived as possible.
   - Always drop the entry reference before performing I/O, awaiting async futures, or taking any other lock.

---

## 3. Deterministic Lock Hierarchy & Total Order

### Mathematical Elimination of Deadlocks
When a workflow requires multiple locks, deadlock is mathematically impossible if and only if all execution paths acquire locks in the exact same predefined hierarchical order.

### Global Lock Order Specification:
Define and strictly respect the project's lock hierarchy:
$$\text{Level 1: Global Registry} \longrightarrow \text{Level 2: Tenant Instance} \longrightarrow \text{Level 3: Session / State}$$

- **Rules of the Hierarchy**:
  1. A thread holding a lock at Level $N$ may only acquire locks at Level $N+1$ or higher.
  2. A thread holding a lock at Level $N$ must NEVER attempt to acquire a lock at Level $N$, $N-1$, or any lower level.
  3. If an operation requires modifying state across two entities at the same level, sort their unique IDs first (e.g., lock the smaller `tenant_id` first, then the larger).

### Minimizing Critical Section Hold Time
- Compute, serialize, or fetch data outside the lock.
- Acquire the lock, execute the minimal in-memory state transition, and release the lock immediately:
```rust
// BAD: Lock held while computing or allocating
let mut guard = self.sessions.lock();
let new_data = expensive_computation();
guard.insert(id, new_data);

// GOOD: Compute outside, lock for instant insert
let new_data = expensive_computation();
{
    let mut guard = self.sessions.lock();
    guard.insert(id, new_data);
}
```

---

## 4. Synchronization Primitives: Selection & Hygiene

### `parking_lot` Over `std::sync`
- Prefer `parking_lot::Mutex` and `parking_lot::RwLock` for synchronous locking:
  - Memory footprint: 1 byte vs 40 bytes in `std::sync`.
  - Faster uncontended acquisition (inline assembly fast path).
  - No lock poisoning (`PoisonError`), simplifying error paths.
  - Fair writer queuing in `RwLock` prevents writer starvation under heavy read concurrency.

### Global Resource Initialization with `std::sync::OnceLock`
- Use `std::sync::OnceLock` or `parking_lot::Once` for lazy thread-safe one-time initialization of immutable global resources.
- Avoid third-party `lazy_static` macros in modern Rust 2024 codebases.

---

## 5. Send, Sync & Thread Safety Invariants

### Trait Bounds Architecture
- **`Send`**: Allows transferring type ownership safely to another thread.
- **`Sync`**: Allows sharing immutable references (`&T`) safely across threads (`T: Sync` $\iff$ `&T: Send`).
- All types stored in `DashMap`, shared application state, or passed across `tokio::spawn` task boundaries must satisfy `Send + Sync + 'static`.

### Unsafe Send/Sync Audits
- Never implement `unsafe impl Send for MyType` or `unsafe impl Sync for MyType` unless wrapping an FFI pointer or raw memory buffer.
- When manual implementation is strictly necessary, provide a comprehensive `// SAFETY:` doc comment detailing why concurrent access cannot induce data races or memory corruption.

---

## 6. Bounded In-Memory State & Multi-Tenant Cache Safety

### Complete Ban on Uncapped HashMaps
In high-concurrency bot factories, shared caches tracking users, sessions, or pending callbacks must NEVER grow unbounded in RAM.
- **Explicit Capacity Bounds**: Always initialize with bounded capacities and couple with active eviction policies (LRU via `lru::LruCache`, or TTL sweeping).
- **Background TTL Sweeper**:
  - Run a periodic background task (e.g., every 60 seconds) to sweep expired sessions and reclaim memory:
  ```rust
  tokio::spawn(async move {
      let mut interval = tokio::time::interval(Duration::from_secs(60));
      loop {
          interval.tick().await;
          state.evict_expired_sessions().await;
      }
  });
  ```
