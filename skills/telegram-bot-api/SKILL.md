---
name: telegram-bot-api
description: "Production Telegram Bot API 9.4+ Master Reference: Bot API 9.4 button styles (primary, success, danger), custom emojis, deterministic chat IDs, and webhook architecture."
version: 1.0.0
category: telegram
author: Telegram Bot API Standards Committee
tags: [telegram-bot-api, bot-api-9.4, button-styles, custom-emoji, webhook, floodwait, teloxide]
---

# Telegram Bot API 9.4+ Master Engineering Standards

Comprehensive, production-ready specification for building high-scale bots conforming to Telegram Bot API 9.4+.

## 1. Bot API 9.4 Button Styling & Custom Emoji Invariants
Never degrade buttons to monochromatic defaults or dump raw emojis.

### Inline Keyboard Button Schema (Bot API 9.4)
```json
{
  "inline_keyboard": [
    [
      {
        "text": "Accept Action",
        "callback_data": "act_accept",
        "style": "success"
      },
      {
        "text": "Cancel",
        "callback_data": "act_cancel",
        "style": "danger"
      }
    ],
    [
      {
        "text": "Open Dashboard",
        "web_app": { "url": "https://dashboard.example.com" },
        "style": "primary"
      }
    ]
  ]
}
```
Supported `style` values:
- `"primary"`: Dominant brand accent fill for the primary CTA.
- `"success"`: Green accent fill for confirmations, acceptances, and positive feedback.
- `"danger"`: Red accent fill for destructive actions, cancellations, and deletions.

## 2. Deterministic Chat ID Formatting (`no_lazy_fallbacks`)
Strictly forbid prepending `-100` blindly to chat IDs:
- **Private User Chats**: Positive numeric string directly (e.g. `"6149403807"`).
- **Supergroups & Channels**: Use `-100` prefix format (e.g. `"-1002149403807"`).
- **Basic Groups**: Standard negative format without `-100` (e.g. `"-456789123"`).

## 3. Webhook Architecture with Axum
Co-host the Telegram webhook endpoint alongside your health check on a single port:
```rust
let app = Router::new()
    .route("/webhook", post(telegram_webhook_handler))
    .route("/health", get(|| async { "OK" }));
```
Validate `X-Telegram-Bot-Api-Secret-Token` header on every incoming request.

## 4. FloodWait (Code 420) Backoff & Jitter
```
sleep = wait_seconds + random_jitter(100ms..1000ms)
```
