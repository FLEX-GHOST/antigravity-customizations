---
name: telegram-stars-monetization
description: Production-grade guide for Telegram Stars monetization, digital goods, paid media (sendPaidMedia), star transactions, refunds, and recurring paid channel subscriptions under Bot API 10.3 / 9.4+.
---

# Telegram Stars Monetization & Paid Media Architecture

Engineered for production Telegram bot factories deploying Telegram Stars monetization, digital product sales, and monthly channel subscriptions.

---

## 1. Core Telegram Stars Lifecycle

```
[User Interaction] -> [sendPaidMedia / sendInvoice] 
         |
         v
[Payment Confirmation: StarTransaction] -> [WebHook: successful_payment / PaidMediaPurchased]
         |
         v
[Ledger Idempotency Check (DB)] -> [Grant Digital Entitlement / Channel Access]
```

### Essential Bot API 10.3 Methods
1. **`sendPaidMedia`**:
   - Sends photos or videos that users pay Telegram Stars to unlock.
   - Requires `star_count: Integer` (> 0) and `media: Array of InputPaidMedia`.
2. **`createChatSubscriptionInviteLink`**:
   - Creates a subscription invite link for a channel or supergroup with recurring Star payments.
   - Parameters: `chat_id`, `subscription_period: 2592000` (30 days), `subscription_price: Integer`.
3. **`getStarTransactions`**:
   - Returns bot Star transactions with pagination (`offset`, `limit`).
4. **`refundStarPayment`**:
   - Refunds a Star payment using `user_id` and `telegram_payment_charge_id`.

---

## 2. Production Rust Structs (Zero-RAM & Type Safe)

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SendPaidMediaPayload {
    pub chat_id: String,
    pub star_count: u32,
    pub media: Vec<InputPaidMedia>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub caption: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parse_mode: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum InputPaidMedia {
    #[serde(rename = "photo")]
    Photo { media: String },
    #[serde(rename = "video")]
    Video { media: String, duration: Option<u32> },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StarRefundPayload {
    pub user_id: i64,
    pub telegram_payment_charge_id: String,
}
```

---

## 3. Idempotent Accounting & Ledger Schema

Never credit user entitlements without a database unique constraint on `telegram_payment_charge_id`:

```sql
CREATE TABLE IF NOT EXISTS star_transactions (
    charge_id TEXT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    star_amount INTEGER NOT NULL,
    transaction_type TEXT NOT NULL, -- 'purchase', 'subscription', 'refund'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'COMPLETED'
);

CREATE INDEX IF NOT EXISTS idx_star_user ON star_transactions(user_id);
```

---

## 4. Refund & Dispute Mitigation Policy

1. **Deterministic Charge Verification**:
   Always verify the transaction in your local ledger before calling `refundStarPayment`.
2. **Revocation of Channel Access**:
   When a star payment is refunded or subscription expires, call `banChatMember` followed immediately by `unbanChatMember` to cleanly evict the user without blacklisting them from future purchases.
