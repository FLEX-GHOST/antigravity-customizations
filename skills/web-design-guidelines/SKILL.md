---
name: web-design-guidelines
description: "Enforce Vercel Web Interface Guidelines: accessibility, focus states, Core Web Vitals, and UX."
license: MIT
metadata:
  author: vercel
  version: "1.1.0"

---

# Web Interface Guidelines (Vercel Labs Official)

Adopted from **[vercel-labs/web-interface-guidelines](https://github.com/vercel-labs/web-interface-guidelines)** (626,000+ installs on skills.sh).

Use when building, styling, or reviewing web applications, landing pages, and components.

## Rules

### 1. Accessibility & Semantics
- **Icon-Only Buttons**: Must have `aria-label` (e.g. `<button aria-label="Close dialog">`).
- **Form Controls**: Must have `<label>` with `htmlFor` or `aria-label`.
- **Keyboard Handlers**: Interactive elements need `onKeyDown` / `onKeyUp`.
- **Semantic HTML First**: `<button>` for actions, `<a>`/`<Link>` for navigation. NEVER `<div onClick>`.
- **Images**: Explicit `alt` (or `alt=""` if purely decorative). Decorative icons need `aria-hidden="true"`.
- **Async Updates**: Toasts, dynamic validation, and streaming text need `aria-live="polite"`.
- **Heading Hierarchy**: Proper `<h1>` through `<h6>`; include skip links for main content.

### 2. Focus States & Interaction
- **Visible Focus**: Interactive elements must have visible focus rings (`focus-visible:ring-2`).
- **Never `outline-none`**: Never remove outline without an explicit `focus-visible` replacement.
- **`:focus-visible` over `:focus`**: Prevent ugly focus rings on mouse click while preserving keyboard accessibility.
- **Compound Controls**: Use `:focus-within` on form groups or compound inputs.
- **Overlays**: Sticky headers, bottom bars, and modal overlays must never obscure the focused element.

### 3. Forms & Data Entry
- **Autocomplete & Names**: Inputs need meaningful `name` and proper `autocomplete` attributes.
- **Input Types**: Use correct `type` (`email`, `tel`, `url`, `number`) and `inputmode`.
- **Never Block Paste**: Never prevent `onPaste`.
- **Inline Errors**: Display validation errors next to fields; focus the first error on invalid submit.
- **Submit Loading**: Keep submit button enabled until network request starts; show spinner during request.

### 4. Animation & Motion
- **Respect `prefers-reduced-motion`**: Provide reduced variant or disable animations entirely.
- **Compositor-Friendly**: Animate `transform` and `opacity` only.
- **Never `transition: all`**: Always specify animated properties explicitly (e.g., `transition: opacity 150ms ease, transform 150ms ease`).
- **Interruptible**: Animations must gracefully handle user cancellation or new inputs mid-animation.

### 5. Layout, Typography & Text Handling
- **Prevent Widows**: Use `text-wrap: balance` on headlines and `text-pretty` on body copy.
- **Text Truncation**: Flex children need `min-w-0` to allow `truncate` / `line-clamp` to function without blowout.
- **Empty States**: Never render broken UI for empty strings or empty arrays; always provide graceful empty states.
- **Mobile Safe Areas**: Full-bleed layouts need `env(safe-area-inset-*)` for mobile notches and home indicators.
- **CLS Prevention**: `<img>` and `<video>` tags MUST have explicit `width` and `height` attributes or aspect ratios.

### 6. Performance & Hydration Safety
- **Virtualize Large Lists**: Lists with >50 items must use virtualization (`virtua` or CSS `content-visibility: auto`).
- **Batch DOM Reads**: Avoid interleaving layout reads (`getBoundingClientRect`, `offsetHeight`) with writes.
- **Hydration Safety**: In Next.js / SSR, guard client-only values (dates, localStorage) to prevent hydration mismatches.
