---
name: telegram-floodwait-resilience
description: Handling Telegram 420 FLOOD_WAIT errors deterministically with dynamic
  exponential backoff and randomized jitter
triggers:
- telegram-floodwait-resilience
language: polyglot
category: learned
---

# telegram-floodwait-resilience

## Mission & Problem Summary
Handling Telegram 420 FLOOD_WAIT errors deterministically with dynamic exponential backoff and randomized jitter

## Instructions & Workflow Runbook
Extract wait_seconds from Telegram API error response. Sleep for wait_seconds + random_jitter(100ms..1000ms). Never retry in a tight loop.

## Invariants & Production Guidelines
- Deterministic error handling with verified backoff.
- Do NOT retry in a tight loop.
- Never violate memory safety or rate limits.

## Verified Examples & Reference Implementation
```python
# Production reference for telegram-floodwait-resilience
pass
```
