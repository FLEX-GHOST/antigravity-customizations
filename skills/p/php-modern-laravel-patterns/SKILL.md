---
name: php-modern-laravel-patterns
description: Master guide for PHP 8.3+ development covering strict typing, Laravel 11 clean service architecture, Octane/Swoole concurrency, and Pest testing.
language: php
category: programming-languages
quality_score: 100
tier: official
triggers:
  - php
  - laravel
  - symfony
  - octane
  - swoole
  - pest
  - composer
  - php 8
---
# Modern PHP 8.3+ Architecture, Laravel 11 & High-Concurrency APIs

Engineering guidelines for building modern, type-safe, and lightning-fast web applications with PHP 8.3+ and Laravel 11.

## 1. PHP 8.3 Strict Typing & Language Invariants
* **Strict Types Mandate**: Every PHP file must declare `declare(strict_types=1);` on line 1.
* **Readonly Properties & Classes**: Model domain DTOs with `readonly class` to guarantee immutability.
  ```php
  <?php
  declare(strict_types=1);

  namespace App\Domain\DTO;

  readonly class CreateUserDTO {
      public function __construct(
          public string $email,
          public string $fullName,
          public ?string $phoneNumber = null
      ) {}
  }
  ```
* **Enums with Methods**: Use backed enums for domain status codes and business rule mappings.

## 2. Laravel 11 Architecture & Performance
* **Thin Controllers, Rich Actions**: Controllers only handle HTTP validation and response formatting. All business logic lives in single-action classes or domain services.
* **Laravel Octane / Swoole Ready**: Eliminate static state pollution and memory leaks to run seamlessly on long-running application servers.
* **Database Optimization**: Always eager-load relationships via `with(...)` to eliminate N+1 query disasters.
