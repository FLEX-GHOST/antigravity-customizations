---
name: telegram-webhook-architecture
description: "Production Telegram Bot Webhook Architecture: Multi-tenant token hashing, Nginx reverse proxy, secret_token validation, sub-100ms HTTP 200 dispatch, and Axum co-hosting."
version: 1.0.0
category: telegram-infrastructure
author: Senior Telegram Infrastructure Engineers
tags: [telegram, webhook, axum, nginx, multi-tenant, token-hashing, secret-token, resilience, tokio]
---

# Telegram Bot Webhook Master Architecture & High-Scale Standards

Production-grade engineering standards for deploying high-throughput, multi-tenant Telegram webhooks handling millions of updates per day with zero message loss and sub-millisecond response latency.

## 1. Core Architectural Pillars
```
[Telegram Cloud SFU] 
       │ HTTPS (Ports 443, 8443, 80, 88)
       ▼
[Nginx SSL Reverse Proxy]
       │ Unix Socket or Local TCP (proxy_buffering off)
       ▼
[Axum Webhook Gateway] ──> [Instant HTTP 200 OK (< 50ms)]
       │
       ├──> Token Hash Lookup (SHA-256 Hash ──> Bot ID)
       ├──> Secret Token Verification (X-Telegram-Bot-Api-Secret-Token)
       │
       ▼ [Bounded Tokio MPSC Channel / JoinSet]
[Async Worker Pool] ──> [Filters / State Machine / LLM / Microservices]
```

## 2. Multi-Tenant Token Hashing (`/webhook/{token_hash}`)
Never expose bot tokens in plain text in URLs or access logs.
- Compute a deterministic SHA-256 hash or HMAC of the bot token:
  ```rust
  use sha2::{Digest, Sha256};

  pub fn compute_token_hash(token: &str) -> String {
      let mut hasher = Sha256::new();
      hasher.update(token.as_bytes());
      hasher.update(b"_factory_salt_v1");
      format!("{:x}", hasher.finalize())[..32].to_string()
  }
  ```
- Register the webhook URL with Telegram as:
  `https://api.yourdomain.com/webhook/{token_hash}`
- Maintain an in-memory bi-directional map (`dashmap::DashMap<String, BotId>`) for O(1) bot resolution.

## 3. The Instant HTTP 200 OK Mandate
Telegram expects an immediate HTTP `200 OK`. If your handler blocks on a database query, file download, or AI model inference, Telegram triggers automatic retries, leading to update flooding and duplicate state executions.
- **Rule**: Send HTTP `200 OK` within < 100ms.
- **Implementation**:
  ```rust
  pub async fn handle_webhook(
      State(state): State<WebhookState>,
      Path(token_hash): Path<String>,
      headers: HeaderMap,
      Json(payload): Json<serde_json::Value>,
  ) -> impl IntoResponse {
      // 1. Verify Secret Token
      let secret_header = headers.get("X-Telegram-Bot-Api-Secret-Token")
          .and_then(|v| v.to_str().ok());
      if secret_header != Some(&state.secret_token) {
          return (StatusCode::UNAUTHORIZED, "Invalid Secret").into_response();
      }

      // 2. Offload work to background Tokio worker
      let ctx = Arc::clone(&state.ctx);
      tokio::spawn(async move {
          dispatch_webhook_payload(ctx, token_hash, payload).await;
      });

      // 3. Immediate Fast Return
      (StatusCode::OK, "OK").into_response()
  }
  ```

## 4. Hardened Nginx Reverse Proxy Configuration
```nginx
# /etc/nginx/sites-available/bot_webhook.conf
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # Telegram IP Allowlist
    allow 149.154.160.0/20;
    allow 91.108.4.0/22;
    deny all;

    location /webhook/ {
        proxy_pass http://127.0.0.1:8080/webhook/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Disable proxy buffering for real-time streaming
        proxy_buffering off;
        proxy_connect_timeout 5s;
        proxy_read_timeout 15s;
        proxy_send_timeout 15s;
    }
}
```

## 5. Webhook Lifecycle Management
- **Startup (`setWebhook`)**:
  - `url`: `https://api.yourdomain.com/webhook/{token_hash}`
  - `secret_token`: High-entropy string (1-256 characters, `[A-Za-z0-9_-]`)
  - `max_connections`: 100 (prevents socket exhaustion)
  - `allowed_updates`: `["message", "edited_message", "callback_query", "inline_query"]`
  - `drop_pending_updates`: `false` (set `true` only on cold emergency reboot)
- **Shutdown (`deleteWebhook`)**:
  - Clean up on SIGINT/SIGTERM to prevent Telegram from sending updates to dead endpoints.

## 6. Co-Hosting with Telegram Mini Apps (TWA)
Combine the webhook handler and mini app frontend/API on the same Axum router:
```rust
let app = Router::new()
    .route("/webhook/health", get(health_check))
    .route("/webhook/{token_hash}", post(handle_webhook))
    .nest("/miniapp", miniapp_router(Arc::clone(&ctx)))
    .with_state(state);
```
