---
trigger: model_decision
description: Telegram bots and Mini Apps best practices, flood wait handling, non-blocking handlers, and multi-tenant bot factories
---

# Telegram Bot & Mini App Development Standards

Ensure production reliability, resilience against rate limits, and secure webhook/polling execution.

## 1. Rate Limiting & Flood Control
- **Dynamic FloodWait Backoff**: Always catch `FloodWait` / HTTP 420 errors dynamically and sleep for the exact duration requested by Telegram plus random jitter. Never retry immediately in a tight loop.
- **Outbound Request Throttling**: Bound outbound message sending rates (max 30 messages/sec global, max 1 message/sec per private chat) using token bucket or queue-based throttlers.

## 2. Concurrency & Non-Blocking Updates
- **Worker Offloading**: Update handlers (polling or webhooks) must acknowledge or dispatch immediately. Never execute long-running I/O, heavy downloads, or CPU encoding directly in the update loop; offload to background tasks or worker pools.
- **Graceful Shutdown**: On `SIGINT`/`SIGTERM`, flush pending updates, wait for active background tasks to complete within a bounded grace period, and close MTProto/HTTP sessions cleanly.

## 3. Formatting & Payload Safety
- **Text Entity Escaping**: When using `MarkdownV2` or `HTML` parse modes, always escape dynamic user-generated text through a dedicated escaping helper before formatting to prevent parse breakdown errors.
- **Secret Protection**: Never log bot tokens, MTProto session strings, or authentication hashes in application logs or traces.

## 4. Mini App (TWA) Security
- **HMAC Signature Verification**: Backend API endpoints receiving Telegram WebApp `initData` must validate the cryptographic HMAC-SHA256 signature against the bot token before trusting `user_id` or query parameters.

## 5. Multi-Tenant Bot Factory (100K Scale)
- **Stateless Webhook Multiplexing**: Never run 100,000 polling loops. Route all updates through a single webhook listener (`POST /webhook/:bot_id`).
- **Zero-RAM Idle State**: Idle bots must consume 0 bytes of RAM. Fetch bot config and permissions on-demand from disk (SQLite WAL / LibSQL), process the update, and immediately free the instance.
- **Global Connection Pooling**: Share a single outbound HTTP/2 client connection pool across all tenant bots.
