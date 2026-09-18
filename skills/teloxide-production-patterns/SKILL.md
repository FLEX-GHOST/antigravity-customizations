---
name: teloxide-production-patterns
description: "Production Rust Telegram bot engineering with Teloxide: dptree dispatching, dialogue state machines, Axum webhook sharing, and Bot API 9.4."
version: 1.0.0
category: rust-telegram
author: Senior Rust Systems Engineers
tags: [rust, teloxide, telegram, dptree, dialogue, webhook, bot-api-9.4, tokio]
---

# Teloxide Production Systems Engineering Master Guide

Implement deterministic, high-concurrency Telegram bots in pure Rust using the Teloxide framework.

## 1. Handler Tree Architecture (`dptree`)
- Structure update dispatching hierarchically using `dptree`:
  - Layer 1: Global middleware (Authentication, Rate-Limiting, Metrics).
  - Layer 2: Update branch (Messages, Callback Queries, Inline Queries).
  - Layer 3: Command & State matching.
- Prevent unhandled branch fallthrough by attaching a terminal logging fallback handler.

## 2. Dialogue State Machine
```rust
#[derive(Clone, Default, serde::Serialize, serde::Deserialize)]
pub enum BotState {
    #[default]
    Start,
    AwaitingUrl { service: String },
    Processing { task_id: String },
}
```
- Back dialogue state with Redis or memory store (`InMemStorage<BotState>`).

## 3. Axum Webhook Co-Hosting
- Share a single HTTPS listening port for both the Telegram webhook receiver and healthcheck/API dashboard:
  - Route `/webhook` to `teloxide::dispatching::update_listeners::webhooks::axum()`.
  - Route `/health` to standard Axum handler.

## 4. Bot API 9.4 Standards
- Use colored buttons (`InlineKeyboardButton` with `.style(ButtonStyle::Primary)`).
- Handle FloodWait (code 420) via custom error policy wrapper.
