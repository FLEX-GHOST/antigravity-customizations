---
name: csharp-dotnet-architecture
description: Enterprise master guide for C# 12 and .NET 9 covering Clean Architecture, ASP.NET Core minimal APIs, Entity Framework Core query optimization, and memory efficiency with Span<T>.
language: csharp
category: programming-languages
quality_score: 100
tier: official
triggers:
  - csharp
  - c#
  - .net
  - dotnet
  - asp.net
  - ef core
  - entity framework
  - linq
---
# C# 12 & .NET 9 Clean Architecture, EF Core & High-Performance APIs

Definitive patterns for high-throughput, low-allocation enterprise backend services in modern .NET.

## 1. Clean Architecture & CQRS
* **Dependency Rule**: Core domain entities and use cases must have zero dependencies on external frameworks, databases, or UI layers.
* **Result Pattern Over Exceptions**: Model expected business errors using `Result<T, Error>` structs instead of throwing expensive exceptions.

## 2. High-Performance C# 12 Standards
* **Primary Constructors**: Streamline dependency injection with concise primary constructors on classes and records.
  ```csharp
  public class OrderProcessingService(
      IOrderRepository repository,
      IPaymentGateway gateway,
      ILogger<OrderProcessingService> logger
  ) : IOrderProcessingService {
      public async Task<Result<OrderSummary>> ProcessOrderAsync(OrderRequest request, CancellationToken ct) {
          // Execution logic
      }
  }
  ```
* **Span<T> & Memory Allocation**: Utilize `ReadOnlySpan<char>` and `Memory<T>` for zero-allocation parsing of incoming payloads.
* **Asynchronous Discipline**: Always propagate `CancellationToken` throughout all async pipelines. Avoid `.Result` or `.Wait()`.

## 3. Entity Framework Core Optimization
* **No-Tracking by Default**: Use `.AsNoTracking()` for read-only queries to bypass change tracker overhead.
* **Projection Efficiency**: Project directly to DTOs via `.Select(...)` to prevent querying unnecessary database columns.
