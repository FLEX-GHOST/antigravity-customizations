---
name: java-enterprise-patterns
description: Master guide for enterprise Java development covering Java 21+ LTS, Virtual Threads (Project Loom), Spring Boot 3, Hibernate/JPA optimization, Record patterns, and zero-leak concurrency.
language: java
category: programming-languages
quality_score: 100
tier: official
triggers:
  - java
  - spring boot
  - virtual threads
  - loom
  - maven
  - gradle
  - jvm
  - jpa
---
# Java 21+ Enterprise Architecture, Virtual Threads & Spring Boot 3

Comprehensive architectural handbook for designing scalable, type-safe, and low-latency enterprise Java applications.

## 1. Core Language Standards (Java 21 LTS)
* **Virtual Threads (Project Loom)**: Replace heavyweight OS-thread worker pools with lightweight virtual threads for high-throughput I/O.
  ```java
  try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
      IntStream.range(0, 10_000).forEach(i -> executor.submit(() -> fetchHttpData(i)));
  }
  ```
* **Pattern Matching & Records**: Model immutable domain entities using `record` and exhaustive `switch` pattern matching.
  ```java
  public sealed interface PaymentMethod permits CreditCard, BankTransfer, CryptoWallet {}
  public record CreditCard(String cardNumber, YearMonth expiry) implements PaymentMethod {}
  public record BankTransfer(String iban, String bic) implements PaymentMethod {}
  public record CryptoWallet(String walletAddress, String network) implements PaymentMethod {}

  public static String resolveFee(PaymentMethod method) {
      return switch (method) {
          case CreditCard cc -> "Fee: 2.5%";
          case BankTransfer bt -> "Fee: 0.1%";
          case CryptoWallet cw -> "Fee: Network Gas";
      };
  }
  ```

## 2. Spring Boot 3 & Native Microservice Patterns
* **GraalVM Native Images**: Design applications with AOT (Ahead-of-Time) compilation for sub-50ms cold starts in serverless.
* **Declarative HTTP Interfaces**: Use `@HttpExchange` instead of boilerplate RestTemplate or WebClient code.
* **Transactional Invariants**: Keep `@Transactional` boundaries minimal and read-only by default (`@Transactional(readOnly = true)`).

## 3. Concurrency & Memory Hygiene
* **Never Pin Carrier Threads**: Avoid `synchronized` blocks around blocking I/O calls when using virtual threads; use `ReentrantLock` instead.
* **Zero NullPointerExceptions**: Enforce `@NonNullByDefault` and domain-driven value objects instead of raw primitives.
