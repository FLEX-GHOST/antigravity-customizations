---
name: telegram-resilience-engineering
description: "Telegram Bot API 420 FloodWait backoff, jitter formulas, webhook security, MTProto session migration, and connection pool resilience."
version: 1.0.0
category: telegram
author: Telegram Systems Engineering
tags: [telegram, floodwait, rate-limiting, resilience, retry-jitter, mtproto, webhook]
---

# Telegram Resilience & Anti-FloodWait Engineering Master Standards

Ensure zero downtime, zero message drops, and 100% compliance with Telegram Bot API & MTProto protocol constraints.

## 1. FloodWait (Code 420) Exponential Backoff & Jitter
When Telegram returns `420 FLOOD_WAIT_X` or `FLOOD_WAIT`:
1. **Extract Duration**: Extract `wait_seconds` from API response `retry_after` or error parameter.
2. **Full Jitter Calculation**:
   ```
   sleep_duration = wait_seconds + random_uniform(0.1, 1.0)
   ```
3. **Queue Suspension**: Temporarily pause the specific chat's queue without blocking global workers.
4. **Exponential Backoff for 5xx & Network Failures**:
   ```
   backoff = min(MAX_BACKOFF, BASE_BACKOFF * 2^retry_count) + random_jitter(0.1, 0.5)
   ```

## 2. Webhook & Endpoint Hardening
1. **Secret Token Verification**: Verify `X-Telegram-Bot-Api-Secret-Token` header matches server config on every incoming POST request.
2. **Telegram IP Subnets**: Reject updates not originating from official Telegram IP ranges:
   - `149.154.160.0/20`
   - `91.108.4.0/22`
3. **Fast Acknowledgment**: Return HTTP `200 OK` within 1,000ms. Offload heavy processing to background workers.
4. **Bot API 9.4 Standards**: Preserve button color styles (`style: "primary" | "success" | "danger"`) and custom emojis. Never strip styles on retries.
