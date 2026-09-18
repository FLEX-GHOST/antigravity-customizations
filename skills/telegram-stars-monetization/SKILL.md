---
name: telegram-stars-monetization
description: "Telegram Stars monetization API, digital invoices, pre-checkout verification, and paid media streaming in Rust and Go (Bot API 9.4+)."
version: 1.0.0
category: monetization
author: Telegram Fintech Engineers
tags: [telegram-stars, payments, invoices, bot-api-9.4, paid-media, monetization]
---

# Telegram Stars Monetization & Invoicing Master Guide

Implement native Telegram Stars payments for digital services, subscriptions, and paid media downloads.

## 1. Payment Lifecycle
```
[User Clicks Buy] ──> [sendInvoice / createInvoiceLink (Currency: "XTR")]
                             │
                             ▼
                 [User Approves Stars Transaction]
                             │
                             ▼
                 [pre_checkout_query update received]
                             │
                             ▼
                 [answerPreCheckoutQuery(ok: true) within 10s]
                             │
                             ▼
                 [successful_payment received ──> Deliver Digital Goods]
```

## 2. Production Rules & Invariants
1. **Pre-Checkout SLA**: You MUST call `answerPreCheckoutQuery` within 10 seconds, or Telegram automatically cancels the transaction.
2. **Idempotency**: Check `telegram_payment_charge_id` in database before fulfilling orders to prevent duplicate deliveries.
3. **Refund Handling**: Call `refundStarPayment` when delivery fails or customer support approves a refund.
