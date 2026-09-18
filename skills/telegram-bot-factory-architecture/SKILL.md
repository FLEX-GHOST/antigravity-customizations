---
name: telegram-bot-factory-architecture
description: High-scale multi-tenant daemon architecture for hosting thousands of Telegram bots in a single process with webhook multiplexing, per-bot circuit breakers, and zero-RAM idle.
---

# Multi-Tenant Telegram Bot Factory Architecture

Engineered for hosting hundreds or thousands of tenant Telegram bots inside a unified Tokio/Go daemon with strict resource isolation.

---

## 1. Multiplexed Webhook Ingestion

Never bind individual network ports per bot. Expose a single HTTP listener with dynamic path dispatch:

```
[Telegram Webhook Ingress]
         |
         v  POST /webhook/:bot_id
[Path Router & Token Validator] -> [Tenant Registry (DashMap / Concurrent Map)]
         |
         v
[Tenant Worker Channel (Bounded mpsc)] -> [Handler Pipeline]
```

### Route Design
- Endpoint: `POST /webhook/{bot_id}`
- Secret Token Verification: Match header `X-Telegram-Bot-Api-Secret-Token` against tenant secret in memory.
- Early Return: Always return HTTP 200 OK immediately to Telegram before asynchronous pipeline processing to prevent webhook retries.

---

## 2. Per-Bot Rate Limiting & FloodWait Isolation

When one bot hits Telegram rate limits (HTTP 420), never block the entire process:

```rust
// Circuit breaker state per tenant
pub struct TenantCircuitBreaker {
    pub is_blocked: AtomicBool,
    pub resume_at: AtomicU64,
}

impl TenantCircuitBreaker {
    pub fn trigger_floodwait(&self, retry_after_secs: u64) {
        let resume = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap()
            .as_secs() + retry_after_secs + 1;
        self.resume_at.store(resume, Ordering::Release);
        self.is_blocked.store(true, Ordering::Release);
    }
}
```

---

## 3. Dynamic Bot Registration & Zero-Downtime Provisioning

1. **Hot Registration**: New tenants can register a bot token via database insertion or IPC without restarting the factory daemon.
2. **Automated Webhook Binding**: Factory automatically calls `setWebhook` with the standardized URL `https://your-domain.com/webhook/{bot_id}` and an HMAC secret token.
3. **Dead Bot Pruning**: If a bot receives error 403 (`bot was blocked by the user` or deleted bot), flag tenant status in DB and suspend outbound polling immediately.
