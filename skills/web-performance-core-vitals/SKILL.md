---
name: web-performance-core-vitals
description: "Core Web Vitals optimization (LCP < 2.5s, INP < 200ms, CLS < 0.1): zero layout shift, font subsetting, lazy loading, and critical CSS inlining."
version: 1.0.0
category: web-performance
author: Web Performance Engineers
tags: [core-web-vitals, performance, lcp, cls, inp, optimization, web-vitals]
---

# Web Performance & Core Web Vitals Engineering Master Standards

Deliver lightning-fast web pages achieving 100/100 Lighthouse performance metrics.

## 1. Core Web Vitals Targets
- **Largest Contentful Paint (LCP)**: `<= 2.5 seconds` on mobile 4G.
- **Interaction to Next Paint (INP)**: `<= 200 milliseconds`.
- **Cumulative Layout Shift (CLS)**: `<= 0.1` (Target: `0.00`).

## 2. Zero Cumulative Layout Shift (CLS = 0)
1. **Explicit Dimensions on All Media**: Every `<img>`, `<video>`, and `<iframe>` MUST define `width` and `height` attributes or CSS `aspect-ratio`.
2. **Font Display Optional**: Use `font-display: swap` paired with matching fallback metrics (`size-adjust`, `ascent-override`) to eliminate FOUT/FOIT shifts.
3. **Dynamic Elements**: Reserve structural space with skeleton placeholders before fetching remote data.

## 3. LCP Optimization
1. **Preload Hero Assets**: `<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">`.
2. **Critical CSS Inlining**: Inline the above-the-fold critical CSS into `<style>` in `<head>`; load non-critical CSS asynchronously.
3. **Image Formats**: Serve modern AVIF (first choice) or WebP with responsive `srcset`.
