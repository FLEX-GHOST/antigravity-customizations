---
trigger: model_decision
description: "Rust performance and low-RAM memory discipline (zero-copy Bytes, jemalloc tuning, enum sizing, struct alignment, and ahash)."
---

# Rust High-Performance & Low-Allocation Memory Discipline

Enforce zero-allocation hot paths, cache-aligned memory layouts, disciplined allocator tuning, and micro-architectural optimizations derived from The Rust Performance Book.

---

## 1. Zero-Allocation Hot Paths & Buffer Reuse

### Zero-Copy Network & Media Slicing
- Use `bytes::Bytes` and `bytes::BytesMut` for all network frames, Telegram MTProto payloads, webhook bodies, and media chunks.
- Slicing a `Bytes` instance is an atomic reference count increment with pointer adjustment; it NEVER copies the underlying heap memory buffer.
- Never clone raw `Vec<u8>` or allocate fresh string buffers in update dispatch loops.

### String Allocation Discipline & `Cow<'a, str>`
- Accept borrowed string slices `&str` instead of owned `String` in all inspection and validation functions.
- Use `std::borrow::Cow<'a, str>` when data is predominantly borrowed but occasionally requires mutation, escaping, or dynamic formatting.
- **Avoid `format!()` in Hot Loops**:
  ```rust
  // BAD: Allocates a new heap String on every iteration
  for item in items {
      let key = format!("tenant:{}:{}", tenant_id, item.id);
      map.insert(key, item);
  }

  // GOOD: Re-use a single scratch buffer
  let mut key_buffer = String::with_capacity(64);
  for item in items {
      key_buffer.clear();
      use std::fmt::Write;
      write!(&mut key_buffer, "tenant:{}:{}", tenant_id, item.id).unwrap();
      map.insert(&key_buffer, item);
  }
  ```

### Stack Allocation for Small Collections
- For collections that rarely exceed a few elements, use `smallvec::SmallVec<[T; N]>` or `arrayvec::ArrayVec<T, N>`.
- Stores elements inline on the stack up to capacity $N$, bypassing heap allocation entirely.

---

## 2. Memory Layout, Alignment & Cache Efficiency

### Struct Field Ordering (Eliminating Padding)
The Rust compiler aligns fields to multiples of their natural size. Unordered struct fields produce alignment holes and inflate RAM footprint:
```rust
// BAD: 32 bytes on 64-bit architecture due to alignment padding
pub struct UnpaddedTenant {
    pub is_active: bool,     // 1 byte + 7 padding bytes
    pub bot_id: i64,         // 8 bytes
    pub retry_count: u16,    // 2 bytes + 6 padding bytes
    pub last_seen: u64,      // 8 bytes
}

// GOOD: 24 bytes (strictly ordered by descending alignment size)
pub struct CompactTenant {
    pub bot_id: i64,         // 8 bytes
    pub last_seen: u64,      // 8 bytes
    pub retry_count: u16,    // 2 bytes
    pub is_active: bool,     // 1 byte (+ 5 trailing padding bytes)
}
```
**Mandatory Field Ordering**:
1. 64-bit / 8-byte types first: `u64`, `i64`, `usize`, pointers, references, `Arc<T>`.
2. 32-bit / 4-byte types second: `u32`, `i32`, `f32`.
3. 16-bit / 2-byte types third: `u16`, `i16`.
4. 8-bit / 1-byte types last: `u8`, `i8`, `bool`.

### Compact Enum Footprint (`large_enum_variant`)
- The size of an enum is equal to its largest variant plus discriminator tag and alignment padding.
- If one variant contains a large struct, wrap that specific variant in `Box<T>`:
  ```rust
  pub enum UpdateAction {
      Ack,
      Ignore,
      // Box large payload to prevent 500-byte enum instances in collections
      ProcessMessage(Box<ComplexMessagePayload>),
  }
  ```

### Immutable Slices Over Vectors
- For read-only or static arrays whose length is known at creation time and never resizes, store `Box<[T]>` instead of `Vec<T>`.
- Drops the 8-byte `capacity` field, saving 8 bytes per instance across millions of items.

---

## 3. Allocator Hygiene & Memory Purging (`jemalloc`)

### Global Allocator Registration
For long-running servers and multi-tenant bot factories, standard glibc `malloc` suffers from severe memory fragmentation. Always register `tikv-jemallocator`:
```rust
#[global_allocator]
static GLOBAL: tikv_jemallocator::Jemalloc = tikv_jemallocator::Jemalloc;
```

### Aggressive Background Memory Purging
Configure jemalloc via the `_rjem_malloc_conf` symbol to run a dedicated background purging thread and return dirty pages to the Linux OS immediately:
```rust
#[no_mangle]
pub static _rjem_malloc_conf: &[u8] = b"background_thread:true,dirty_decay_ms:0,muzzy_decay_ms:0\0";
```
- `background_thread:true`: Offloads page reclamation to an asynchronous OS thread.
- `dirty_decay_ms:0`: Purges dirty pages immediately back to the OS upon deallocation.
- `muzzy_decay_ms:0`: Disables muzzy page caching to keep the process resident set size (RSS) minimal.

### RAM Ownership & Disk Offloading
- Never store raw image/media buffers (`Vec<u8>`) inside long-lived structs or in-memory caches.
- Stream large media directly to disk (`tempfile` or designated cache directory) and store only the file `PathBuf`.
- Evict expired disk files atomically using a background TTL cleanup loop.

---

## 4. High-Throughput Hashing & Collection Lookup

### Fast Internal Hashing (`ahash`)
- The standard library `std::collections::HashMap` uses cryptographic SipHash 1-3 to defend against HashDoS attacks, incurring a 2x–5x performance penalty.
- For internal collections keyed on trusted integers, bot IDs, or system enums, use `ahash::AHashMap` and `ahash::AHashSet`:
  ```rust
  use ahash::AHashMap;

  let mut tenant_cache: AHashMap<BotId, TenantMetadata> = AHashMap::with_capacity(1024);
  ```
- Retain cryptographic hashers only for external, untrusted user-supplied string keys.

---

## 5. Micro-Optimization & Inlining Discipline

### Inlining Hot Paths
- Apply `#[inline]` to small, frequently called helper functions (< 15 lines), especially across crate/module boundaries, enabling cross-module vectorization and constant folding.
- **Cold Path Annotation**:
  - Mark error formatting, exception handlers, and rare bailouts with `#[cold]` and `#[inline(never)]`.
  - Keeps cold error instructions out of the processor's primary L1 instruction cache.

### Production Release Profile Standards
For production releases, ensure `Cargo.toml` specifies:
```toml
[profile.release]
opt-level = 3
lto = "thin"
codegen-units = 1
panic = "abort"
strip = true
```
- `lto = "thin"`: Performs whole-program cross-crate optimization without excessive compile times.
- `codegen-units = 1`: Enables maximum global compiler optimization.
- `panic = "abort"`: Eliminates exception unwinding landing pad tables, shrinking binary footprint and improving instruction cache density.
