---
trigger: model_decision
description: Python development best practices, strict type hints, asyncio, and high-scale daemon memory hygiene
---

# Python Language Rules

Senior Python systems developer. Idiomatic, type-safe, and asynchronous.

## 1. Project Tooling & Structure
- **Package Management**: Prefer `uv` for package management and `ruff` for linting and formatting.
- **Layout**: Follow src-layout (`src/package/`) with test code located in a root `tests/` directory.

## 2. Type Annotations & Clean Code
- **Strict Typing**: Provide explicit type hints for all function parameters and return values (including `-> None`).
- **Modern Syntax**: Use Python 3.10+ union syntax (`str | None`) and `typing.Protocol` for structural subtyping.
- **No Wildcard Imports**: Never use `from module import *`.

## 3. Asyncio & Performance
- **Non-Blocking Runtime**: Use `asyncio` for network calls and background tasks. Always attach timeouts to external I/O.
- **Thread Offloading**: Never execute blocking CPU or sync I/O directly in the event loop; offload to `asyncio.to_thread()`.

## 4. High-Scale Bot Factory & Zero-RAM Discipline
- **Shared Async Client Session**: All bots must share a single `httpx.AsyncClient` or `aiohttp.ClientSession` with connection pooling. Never instantiate a client per bot.
- **Stateless Tenant Dispatch**: Never keep 100,000 bot/client instances in RAM. Load tenant tokens and state ephemerally from SQLite/LibSQL on incoming webhook updates, process, and release.
- **Memory Footprint Optimization**: Use `__slots__` or frozen dataclasses/models to avoid Python dict overhead. Cap all in-memory caches using bounded LRU (`functools.lru_cache(maxsize=1000)`).
- **Zero Raw Bytes in Heap**: Stream media chunks directly to disk; never accumulate complete media files in heap variables.

## 5. Testing & Error Boundaries
- **Pytest**: Use `pytest` exclusively with isolated fixtures.
- **Explicit Exceptions**: Catch specific exceptions; never use bare `except:` or catch `BaseException` silently.
