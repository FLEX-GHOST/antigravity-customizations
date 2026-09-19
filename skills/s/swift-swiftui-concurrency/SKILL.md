---
name: swift-swiftui-concurrency
description: Authoritative guide for Swift 6 structured concurrency, Actor isolation, Sendable enforcement, and 120 FPS SwiftUI declarative state architecture.
language: swift
category: programming-languages
quality_score: 100
tier: official
triggers:
  - swift
  - swiftui
  - actors
  - swift 6
  - concurrency
  - sendable
  - async-await
  - xcode
---
# Swift 6 Concurrency, Actors & High-Performance SwiftUI

Architectural standards for building robust, thread-safe, and stutter-free Apple platform software using Swift 6.

## 1. Swift 6 Concurrency & Actor Isolation
* **Strict Concurrency Checking**: Enable complete concurrency checking (`SWIFT_STRICT_CONCURRENCY=complete`) in SPM and Xcode.
* **Actor Protection**: Guard mutable shared state with `actor` types. Use `@MainActor` strictly on UI view models and presentation boundaries.
  ```swift
  actor CacheStore {
      private var storage: [String: Data] = [:]
      
      func get(_ key: String) -> Data? {
          return storage[key]
      }
      
      func set(_ key: String, data: Data) {
          storage[key] = data
      }
  }
  ```
* **Sendable Types**: Ensure any type crossing actor boundaries conforms to `Sendable` (immutable structs, final classes with locking, or value types).

## 2. SwiftUI Performance Invariants (Zero Stutter)
* **View Body Purity**: Keep `var body: some View` free from disk I/O, heavy calculations, or async task spawning.
* **Concentric View Slicing**: Break down large view hierarchies into small, reusable subviews to localize recomposition.
* **Modern State Management**: Use `@Observable` (Observation framework) instead of `@StateObject` and `ObservableObject` in modern SwiftUI.
