---
name: telegram-mtproto-crypto
description: "MTProto 2.0 cryptographic protocols in pure Rust and Go: AES-256-IGE, Diffie-Hellman AuthKey exchange, SHA-256 message keys, and obfuscated TCP."
version: 1.0.0
category: cryptography
author: Telegram Cryptography Engineers
tags: [mtproto, aes-ige, diffie-hellman, authkey, sha256, cryptography, rust, go]
---

# MTProto 2.0 Cryptographic Protocol Master Standards

Implement deterministic, secure MTProto 2.0 cryptographic primitives in Rust (`grammers`) and Go (`gogram`).

## 1. Core Primitives
- **AES-256-IGE (Infinite Garble Extension)**: Dual 128-bit block cipher chaining used for payload encryption.
- **Diffie-Hellman Key Exchange (DH)**: Generates the 2048-bit `auth_key` during client registration.
- **Message Key Derivation**:
  ```
  msg_key = SHA256(auth_key[88..88+32] + plaintext_payload)[8..8+16]
  ```
- **Obfuscated TCP Transport (Abridged / Intermediate / Padded)**: 64-byte random handshake preventing ISP deep packet inspection (DPI).

## 2. Production Security Invariants
1. **Constant-Time Comparison**: Use `subtle::ConstantTimeEq` for comparing message keys to prevent side-channel timing attacks.
2. **Zeroize Sensitive Keys**: Wipe session keys from RAM immediately upon disconnection using `zeroize::Zeroize`.
3. **Replay Defense**: Enforce strictly increasing `msg_id` values based on synchronized Unix timestamps.
