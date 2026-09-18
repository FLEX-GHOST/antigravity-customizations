---
name: telecom-api-engineering
description: "Master guide for telecom API integration, USSD/SMS automation, session tokens, OTP validation, and balance checks in Go and Rust (asiacell_api, zain_api)."
version: 1.0.0
category: telecom
author: Telecom Systems Engineers
tags: [telecom, ussd, sms, otp, asiacell, zain, api-reverse-engineering, go, rust]
---

# Telecom Core API Engineering & Automation Standards

Design and maintain high-reliability telecom microservices (`asiacell_api`, `zain_api`) for subscriber validation, balance inquiries, recharge processing, and OTP handling.

## 1. Session Lifecycle & Token Management
- **Token Rotation**: Cache session tokens in Redis with dynamic TTL (expire 5 minutes prior to upstream expiry).
- **Auto-Reauth**: Intercept HTTP 401/403 responses and trigger transparent re-authentication with exponential backoff.
- **Circuit Breaker**: Trip circuit breaker when upstream telecom gateways return 5xx errors to prevent IP bans.

## 2. Production Invariants in Go (`asiacell_api`, `zain_api`)
1. **Strict Error Handling**: Ban `_ = err`. Return structured domain errors (`ErrInvalidMsisdn`, `ErrGatewayTimeout`).
2. **Payload Masking**: Never log subscriber MSISDN, PIN, or OTP in plain text. Mask MSISDN: `+964770****123`.
3. **Concurrency Control**: Use distributed locks (`redlock`) on subscriber MSISDN during recharge transactions to prevent double-spending.
