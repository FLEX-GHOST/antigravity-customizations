---
name: ruby-rails-performance
description: Production-grade Ruby and Rails engineering skill covering YJIT optimization, Hotwire/Turbo, background jobs with Solid Queue, and concurrency with Ractor.
language: ruby
category: programming-languages
quality_score: 100
tier: official
triggers:
  - ruby
  - rails
  - hotwire
  - turbo
  - yjit
  - solid queue
  - sidekiq
  - rspec
---
# Ruby 3.3+ & Rails 7/8 High-Performance Architecture

Best practices for writing clean, idiomatic, and high-throughput Ruby software on Rails.

## 1. Ruby 3.3+ Language & Runtime Optimization
* **YJIT Production Deployment**: Enable Ruby's Just-In-Time compiler (`RUBY_YJIT_ENABLE=1`) for 15-30% latency reductions.
* **Object Allocation Discipline**: Prefer `freeze` on string literals (`# frozen_string_literal: true`) and avoid allocating temporary hashes in tight loops.
* **Pattern Matching**: Leverage native Ruby 3 pattern matching for complex payload unpacking.
  ```ruby
  # frozen_string_literal: true

  case event
  in { type: "payment.succeeded", amount: Integer => cents, currency: "USD" }
    handle_successful_payment(cents)
  in { type: "payment.failed", reason: String => err }
    handle_failure(err)
  else
    logger.warn("Unknown event type")
  end
  ```

## 2. Modern Rails Design Principles
* **Skinny Models, Service Objects**: Keep ActiveRecord models focused on associations and validation. Complex transactions belong in service objects or form objects.
* **Hotwire & Turbo Over Heavy SPAs**: Deliver fast, server-rendered dynamic UIs with Turbo Frames and Turbo Streams without the weight of client-side JS bundles.
* **Background Worker Hygiene**: Use idempotent job processors with exponential backoff retries and explicit timeouts.
