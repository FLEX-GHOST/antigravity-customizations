---
name: nextjs-app-router-patterns
description: "Production Next.js App Router patterns: React Server Components (RSC), Server Actions with Zod validation, Suspense streaming, and edge caching."
version: 1.0.0
category: frontend-framework
author: Full-Stack Architecture Engineers
tags: [nextjs, react, app-router, server-components, server-actions, rsc]
---

# Next.js App Router & Server Components Engineering Standards

Build scalable, SEO-optimized web applications with Next.js 14/15 App Router.

## 1. Server vs. Client Boundary Architecture
- **Server Components (Default)**: Fetch data directly, access database/backend without exposing API keys, zero bundle footprint.
- **Client Components (`'use client'`)**: Reserve strictly for interactive state (`useState`, `useEffect`, event listeners, browser APIs).
- **Rule**: Push client boundaries to the leaves of the component tree.

## 2. Server Actions with Validation
```typescript
'use server'
import { z } from 'zod';

const ActionSchema = z.object({
  botToken: z.string().regex(/^\d{8,11}:[A-Za-z0-9_-]{35}$/),
  webhookUrl: z.string().url(),
});

export async function configureBotWebhook(formData: FormData) {
  const parsed = ActionSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) {
    return { error: 'Invalid parameters', details: parsed.error.flatten() };
  }
  // Execute database/API mutations securely
}
```

## 3. Streaming with Suspense
Wrap slow data-fetching components in `<Suspense fallback={<Skeleton />}>` to stream HTML progressively without blocking the initial page render.
