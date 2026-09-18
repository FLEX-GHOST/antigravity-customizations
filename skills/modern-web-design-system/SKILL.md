---
name: modern-web-design-system
description: "Master design system architecture: semantic tokens, 50-950 lightness ramps, dark mode palettes, component state coverage, and WCAG 2.2 AA contrast."
version: 1.0.0
category: web-design
author: Senior Design Systems Engineers
tags: [design-system, css, tokens, dark-mode, wcag, ui-architecture, semantic-colors]
---

# Modern Web Design System & Semantic Token Architecture

Build production-grade, unslop web interfaces with strict mathematical color discipline and complete interactive state coverage.

## 1. Primitives vs. Semantic Tokens
Never use primitive hex values or tokens (`#3b82f6` or `--blue-500`) directly inside UI components.
```css
:root {
  /* 1. Primitive Lightness Ramps */
  --blue-500: #3b82f6;
  --blue-600: #2563eb;
  --neutral-900: #0f172a;
  --neutral-100: #f1f5f9;

  /* 2. Semantic Role Mapping (Light Mode) */
  --color-surface-base: #ffffff;
  --color-surface-elevated: #f8fafc;
  --color-text-primary: #0f172a;
  --color-text-secondary: #475569;
  --color-interactive-primary: var(--blue-600);
  --color-interactive-hover: var(--blue-500);
}

[data-theme="dark"] {
  /* Semantic Role Mapping (Dark Mode) */
  --color-surface-base: #0b0f19;
  --color-surface-elevated: #151d2f;
  --color-text-primary: #f8fafc;
  --color-text-secondary: #94a3b8;
  --color-interactive-primary: var(--blue-500);
  --color-interactive-hover: var(--blue-600);
}
```

## 2. The Six Mandatory Interactive States
Every button, link, and interactive widget MUST implement all 6 states:
- `rest`: Standard semantic fill, pointer cursor.
- `hover`: Distinct luminance shift (10-15%).
- `active`: Noticeable scale down (`transform: scale(0.98)`).
- `focus-visible`: 2px high-contrast outline with `outline-offset: 2px`.
- `disabled`: Contrast muted, `cursor: not-allowed`, `aria-disabled="true"`.
- `loading`: Visual spinner or pulse; preserves exact button dimensions.

## 3. WCAG 2.2 AA Contrast Compliance
- Normal body text: Minimum **4.5:1** contrast ratio against its background.
- Large text (18pt+ or 14pt bold): Minimum **3:1** contrast ratio.
- Interactive boundaries and icons: Minimum **3:1** contrast ratio.
