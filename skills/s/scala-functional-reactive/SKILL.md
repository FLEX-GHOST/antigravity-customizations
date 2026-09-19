---
name: scala-functional-reactive
description: Master guide for Scala 3 pure functional programming, type classes, contextual abstractions, ZIO, and Cats Effect distributed streaming.
language: scala
category: programming-languages
quality_score: 100
tier: official
triggers:
  - scala
  - scala 3
  - zio
  - cats effect
  - sbt
  - functional programming
  - typeclass
---
# Scala 3 Functional & Reactive Systems (ZIO, Cats Effect)

Architectural patterns for pure functional, concurrent, and resilient distributed systems in Scala 3.

## 1. Pure Functional Architecture & Effect Systems
* **Referential Transparency**: Model all asynchronous and side-effecting operations inside managed effects (`ZIO[R, E, A]` or `IO[A]`).
* **Error Modeling**: Differentiate between expected domain failures (typed in error channel `E`) and unrecoverable defects (`Die`).
  ```scala
  import zio.*

  trait UserRepo:
    def findById(id: Long): IO[DatabaseError, Option[User]]

  object UserService:
    def getUser(id: Long): ZIO[UserRepo, DatabaseError, User] =
      for
        repo <- ZIO.service[UserRepo]
        user <- repo.findById(id).someOrFail(DatabaseError.NotFound(id))
      yield user
  ```

## 2. Scala 3 New Features
* **Enums & ADTs**: Use concise Scala 3 `enum` constructs instead of sealed trait hierarchies.
* **Givens & Extension Methods**: Replace implicit conversions with explicit `given` instances and clean `extension` methods.
