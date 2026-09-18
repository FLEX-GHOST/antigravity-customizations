---
name: telegram-miniapp-security-crypto
description: "Cryptographic HMAC-SHA256 authentication of Telegram Mini App initData in Rust and Go: replay attack prevention, auth_date verification, and Axum integration."
version: 1.0.0
category: security-crypto
author: Cryptography & Telegram Standards Committee
tags: [telegram-miniapp, twa, initdata, hmac-sha256, crypto, rust, go, auth]
---

# Telegram Mini App Cryptographic Authentication & Security Standards

Implement secure, production-grade HMAC-SHA256 validation for Telegram Mini App (TWA) `initData` payloads in Rust and Go.

## 1. The HMAC-SHA256 Verification Algorithm
1. **Extract `hash`**: Separate the `hash` parameter from the raw `initData` query string.
2. **Alphabetical Sorting**: Sort remaining key-value pairs alphabetically and join with `\n` (e.g. `auth_date=...\nquery_id=...\nuser=...`).
3. **Secret Key Derivation**:
   ```
   secret_key = HMAC_SHA256(key = "WebAppData", data = BOT_TOKEN)
   ```
4. **Data Hash Calculation**:
   ```
   calculated_hash = HMAC_SHA256(key = secret_key, data = data_check_string)
   ```
5. **Constant-Time Comparison**: Compare `calculated_hash` with client `hash` using constant-time comparison (`subtle::ConstantTimeEq` in Rust or `hmac.Equal` in Go).

## 2. Replay Attack Defense
- **Freshness Window**: Check `auth_date`. Reject any request where `current_timestamp - auth_date > 86400` (24 hours).
