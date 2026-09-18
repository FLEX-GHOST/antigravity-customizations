---
trigger: always_on
---

# No Lazy Fallbacks & Exact Root-Cause Engineering

Enforce 100% correct primary implementations. Strictly forbid lazy, degraded, or hacky fallback workarounds that mask underlying bugs.

## 1. The Anti-Fallback Mandate
- **No Masking Root Causes**: Never introduce degraded fallback paths (e.g. stripping features, downgrading styling, falling back to plain text, or guessing alternative formats) to hide a bug in the primary implementation.
- **Solve Correctly First**: Engineer the primary pathway to succeed deterministically on the first attempt with provably correct data structures, exact types, and verified API contracts.
- **No Monochromatic / Feature Degradation**: When a feature (such as button colors, custom emojis, or rich media) is designed, never implement fallbacks that degrade the UI to monochromatic or generic states.

## 2. Exact Telegram Protocol & Entity Precision
- **Deterministic ID Formatting**:
  - **Private User Chats**: Use positive numeric string `chat_id` directly (e.g. `"6149403807"`). Never prepend `-100` or convert private user IDs into channel formats.
  - **Supergroups & Channels**: Use `-100` prefix format with the bare channel ID (e.g. `"-1002149403807"`).
  - **Basic Groups**: Use standard negative ID format without `-100` (e.g. `"-456789123"`).
- **Correct API Payloads**: Always send verified, standard JSON schemas conforming to Telegram Bot API 9.4+ (`style: "primary" | "success" | "danger"`, valid URL/callback structures).

## 3. Systematic Diagnosis Over Guesswork
- **Trace the Root Cause**: When a request or command fails, inspect the exact Telegram API error response, logs, and data flow. Fix the root cause in the canonical code in place.
- **Zero Mock / Dummy Handlers**: Never provide dummy fallbacks, synthetic no-ops, or shadow handlers.
