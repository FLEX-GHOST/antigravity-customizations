---
name: owasp-web-security-standards
description: "Production web security standards: Content Security Policy Level 3, CSRF Double-Submit Cookies, XSS sanitization, HSTS, and secure cookie configuration."
version: 1.0.0
category: web-security
author: Application Security Architects
tags: [owasp, web-security, csp, csrf, xss, hsts, security-headers]
---

# OWASP Web Security & Defense-in-Depth Standards

Harden websites, APIs, and Telegram Mini Apps against OWASP Web Top 10 vulnerabilities.

## 1. Mandatory HTTP Security Headers
Every web response MUST deliver these headers:
```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://telegram.org; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.telegram.org; frame-ancestors 'self' https://web.telegram.org;
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## 2. Cookie Security Configuration
All session and authentication cookies MUST declare:
`Set-Cookie: session_id=...; Secure; HttpOnly; SameSite=Strict; Path=/; Max-Age=86400`

## 3. Cross-Site Scripting (XSS) & CSRF Defense
1. **Never Use `innerHTML` or `v-html` with Untrusted Input**: Use DOMPurify if HTML rendering is required.
2. **CSRF Protection**: Verify custom headers (`X-Requested-With` or `X-CSRF-Token`) on all state-mutating requests (POST/PUT/DELETE).
