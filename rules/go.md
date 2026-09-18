---
trigger: always_on
description: Idiomatic Go language rules, explicit error handling, interfaces, and high-concurrency memory efficiency
---

# Go Language Rules

Expert Go developer. Simple, explicit, idiomatic.

## 1. Error Handling & Wrapping
- **Always Handle Errors**: Never assign errors to `_` without an explicit, documented reason.
- **Context Preservation**: Use `fmt.Errorf("context: %w", err)` for wrapping, and inspect with `errors.Is()` / `errors.As()`.
- **Custom Error Types**: Use structured domain error types for programmatic inspection.

## 2. Interfaces & Design
- **Accept Interfaces, Return Structs**: Define interfaces at the consumer (call site), not the producer (implementation site).
- **Keep Interfaces Small**: Prefer single-method interfaces (`io.Reader`, `http.Handler`).

## 3. Concurrency & Context
- **Context First**: Pass `context.Context` as the first parameter to any blocking or I/O function. Always call `defer cancel()` after creating cancellable contexts.
- **Goroutine Termination**: Every spawned goroutine must have an explicit exit condition or listen on `ctx.Done()`. Never leak goroutines.
- **Synchronization**: Use channels for communication and `sync.Mutex` / `sync.RWMutex` for state protection.

## 4. High-Concurrency & Zero-Allocation (100K Bots)
- **Zero-Allocation Buffers**: Use `sync.Pool` for byte buffers (`bytes.Buffer`), JSON decoders, and request wrappers in hot paths.
- **Shared HTTP Transport**: All bot instances must share a single `*http.Client` with custom `http.Transport` (`MaxIdleConns: 10000`, `IdleConnTimeout: 90s`). Never instantiate an `http.Client` per bot.
- **Worker Pools over Unbounded Goroutines**: Never spawn unconstrained `go func()` per incoming update. Use bounded worker channels to cap peak concurrency.
- **GC & Memory Safety**: Respect `GOMEMLIMIT` and avoid storing large byte slices or inactive bot state in in-memory maps. Evict idle tenant state to disk/SQLite.

## 5. Testing & Hygiene
- **Table-Driven Tests**: Structure unit tests using table-driven test patterns.
- **No Global Mutable State**: Inject dependencies explicitly via constructors.
