---
name: cpp20-modern-systems
description: Master engineering guide for modern C++20/23 covering Concepts, Coroutines, std::span, RAII, memory sanitizers, and lock-free concurrency.
language: cpp
category: programming-languages
quality_score: 100
tier: official
triggers:
  - cpp
  - c++
  - c++20
  - c++23
  - concepts
  - coroutines
  - cmake
  - clang-tidy
---
# Modern C++20/23 Systems Architecture & Zero-Cost Abstractions

Engineering standards for high-performance, memory-safe, and low-latency systems programming in modern C++.

## 1. Concepts & Constrained Templates
* **Explicit Constraints**: Replace legacy SFINAE with readable C++20 `concepts` to provide crystal-clear compiler error diagnostics.
  ```cpp
  #include <concepts>
  #include <span>
  #include <cstdint>

  template <typename T>
  concept Serializable = requires(T a) {
      { a.serialize() } -> std::same_as<std::span<const uint8_t>>;
  };

  template <Serializable T>
  void transmitPayload(const T& object) {
      auto bytes = object.serialize();
      // Send bytes over wire
  }
  ```

## 2. Lifetime Hygiene & Modern RAII
* **Rule of Zero / Five**: Prefer the Rule of Zero using standard smart pointers (`std::unique_ptr`, `std::shared_ptr`). If custom resource acquisition is needed, implement all 5 special member functions cleanly.
* **Sanitizer Enforcement**: Always compile test suites with AddressSanitizer (`-fsanitize=address,undefined`) to eliminate memory leaks and undefined behavior before production release.
