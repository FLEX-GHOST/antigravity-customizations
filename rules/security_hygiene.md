---
trigger: model_decision
description: Security standards, zero hardcoded secrets, input sanitization, and SQL injection prevention
---

# Security & Secrets Hygiene Rules

Strictly enforce foundational security and data protection standards across all projects.

## 1. Secrets & Credentials Protection
- **Zero Hardcoded Secrets**: Never hardcode API keys, JWT secrets, passwords, database credentials, or private tokens into code.
- **Environment Driven**: Secrets must always be injected via environment variables (.env, secret managers) and added to .gitignore.
- **Log Sanitization**: Never log authorization headers, passwords, session tokens, or sensitive user PII in console or tracing outputs.

## 2. Injection & Input Validation
- **Parameterized Queries**: Never concatenate raw user input into SQL, LibSQL, or database queries. Always use parameterized bindings.
- **Input Sanitization**: Validate and bound all incoming payloads (strings, arrays, query params) before processing to prevent buffer exhaustion and injection attacks.
- **Path Traversal Prevention**: Never construct file paths directly from unvalidated user input. Canonicalize paths and verify directory bounds.
