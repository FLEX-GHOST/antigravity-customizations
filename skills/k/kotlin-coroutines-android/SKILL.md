---
name: kotlin-coroutines-android
description: Definitive Kotlin engineering skill covering structured concurrency, CoroutineScope supervision, StateFlow/SharedFlow, Jetpack Compose, and Kotlin Multiplatform (KMP).
language: kotlin
category: programming-languages
quality_score: 100
tier: official
triggers:
  - kotlin
  - coroutines
  - stateflow
  - flow
  - android
  - kmp
  - compose
  - ktor
---
# Kotlin Coroutines, Flow & Modern Multiplatform Architecture

Production-grade engineering principles for modern Kotlin applications across Android, Ktor backend, and Kotlin Multiplatform.

## 1. Structured Concurrency & Coroutine Scope
* **SupervisorJob Discipline**: Always bind coroutines to dedicated supervised lifecycle scopes (`viewModelScope`, `lifecycleScope`, or custom `CoroutineScope(SupervisorJob() + Dispatchers.IO)`).
* **Cancellation Safety**: Ensure blocking or iterative loops cooperatively check for cancellation via `yield()` or `ensureActive()`.
  ```kotlin
  suspend fun processLargePayload(items: List<Payload>) = withContext(Dispatchers.Default) {
      for (item in items) {
          ensureActive()
          transform(item)
      }
  }
  ```

## 2. Reactive Data Streams with StateFlow & SharedFlow
* **Cold Flows vs Hot Flows**: Use cold `Flow` for reactive query executions, and hot `StateFlow` for state containers in UI or domain layers.
* **Backpressure Handling**: Apply buffer strategies (`buffer()`, `conflate()`) on high-frequency sensor or message streams to prevent buffer exhaustion.

## 3. Clean Architecture & Multiplatform Invariants
* **Domain Sealing**: Use sealed classes/interfaces for UI states (`Loading`, `Success`, `Error`).
* **Kotlin Multiplatform Sharing**: Structure common code cleanly in `commonMain`, abstracting platform specifics via `expect`/`actual` interfaces.
