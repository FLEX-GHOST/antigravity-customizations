---
name: redis-high-concurrency
description: "Distributed locking, sliding-window rate limiting, pub/sub messaging, and high-throughput session state caching for multi-instance Telegram bots."
version: 1.0.0
category: distributed-systems
author: Distributed Systems Engineering
tags: [redis, distributed-locks, redlock, rate-limiting, pubsub, high-concurrency, telegram]
---

# High-Concurrency Redis Architecture for Distributed Bot Clusters

Architect resilient, horizontally scalable bot clusters with Redis for state coordination, locking, and rate limiting.

## 1. Core Concurrency Patterns
- **Distributed Locking (Redlock)**:
  - Acquire lock via atomic `SET resource_name my_random_token NX PX 30000`.
  - Release lock strictly using Lua script verifying token identity:
    ```lua
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    ```
- **Sliding-Window Rate Limiting**:
  - Track requests with sorted sets (`ZADD rate_limit:user_id current_timestamp request_uuid`).
  - Prune expired entries: `ZREMRANGEBYSCORE rate_limit:user_id 0 (current_timestamp - window_size)`.
  - Check count: `ZCARD rate_limit:user_id`. Deny if count exceeds limit.

## 2. Telegram State & Session Storage
1. **Connection Pooling**: Use multiplexed connection pools with health checks and bounded timeouts (`connect_timeout = 2s`, `timeout = 500ms`).
2. **Pipelining**: Batch independent read/write operations with `PIPELINE` to slash network round-trips (RTT) by up to 90%.
3. **Pub/Sub Event Bus**: Use Redis Pub/Sub or Redis Streams for decoupling message receivers (webhooks) from worker tasks.
4. **Key Expiry Invariants**: Every cache key MUST have an explicit TTL (Time-To-Live). Never write unbounded persistent keys without expiration.
