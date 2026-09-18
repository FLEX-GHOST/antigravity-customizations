---
trigger: always_on
description: Anti-AI UI slop rules, semantic color ramps, button hierarchy, 6 interactive states, and SVG standards
---

# Anti-AI UI Slop, Color Discipline & Button Architecture

Strictly forbid cookie-cutter AI aesthetic defaults. Ship intentional, human-crafted, production-ready interfaces.

## 1. Anti-Default UI Slop Discipline (The Craft Floor)
- **Banned AI Cliches**:
  - Never generate generic AI-purple/violet gradients (`#7c3aed`, `#8b5cf6`, `#6366f1`) on dark backgrounds.
  - Never use glowing blur blobs, centered mesh backgrounds, or amorphous radial glow behind hero sections.
  - Never use the three identical floating cards layout (icon + heading + paragraph). Use asymmetric layouts or contextual grids.
  - Never use the hero-metric template (giant number + tiny label + accent) unless mathematically justified.
  - Never place a kicker or uppercase tracked-out eyebrow label (`text-xs uppercase tracking-widest`) above headings. Let the heading speak.
  - Never use gradient text (`background-clip: text`). Visual emphasis comes from typography weight, scale, and contrast.
- **No Faux Glassmorphism**: Avoid slapping `backdrop-filter: blur()` and transparent borders on elements without structural hierarchy or clear purpose.
- **Intentional Aesthetic Direction**: Infer the domain and user audience before styling. Pair typography thoughtfully; avoid defaulting to unstyled browser fonts or generic centered templates.

## 2. Color Systems & Semantic Discipline
- **Ramps Over Random Colors**: Design with disciplined lightness ramps (50-950 or 1-12) rather than picking ad-hoc hex values by eye.
- **Primitives vs Semantics**: Primitive tokens (`--blue-500`) must never be used directly in components. Map primitives to semantic role tokens (`--color-interactive-primary`, `--color-text-secondary`, `--color-surface-elevated`).
- **WCAG 2.2 AA Contrast Compliance**: Ensure normal text achieves at least 4.5:1 contrast against its rendered background; large text and interactive boundaries must achieve at least 3:1.
- **One Primary Action Per Screen**: Only one primary action gets the dominant accent fill. Secondary and peer actions remain visually neutral.

## 3. Button Hierarchy & Complete State Coverage
- **Action Hierarchy**:
  - **Primary**: Solid brand accent fill for the single key CTA.
  - **Secondary**: Neutral solid, outlined, or subtle contrast.
  - **Tertiary / Ghost**: Transparent background, text-only or link styling.
  - **Destructive**: Red accent, distinct from primary.
- **Mandatory Six Interactive States**: Every interactive element must implement all 6 states:
  - `rest`: Base color, pointer cursor.
  - `hover`: Distinct luminance shift (darker or lighter depending on theme).
  - `active` / `pressed`: Noticeable feedback (subtle scale-down or darker pressed shade).
  - `focus-visible`: High-contrast visible focus ring with `outline-offset` for keyboard navigation.
  - `disabled`: Low contrast, `cursor: not-allowed`, and `aria-disabled="true"`.
  - `loading`: Visual spinner or pulse with preserved element dimensions.

## 4. Vector Iconography & Browser Surfaces
- **SVGs Over Emojis**: Never dump raw emojis into UI buttons, badges, or headers. Use clean, scalable SVGs from standard libraries (`lucide`, `phosphor`, `heroicons` via `better-icons`).
- **Consistent Metrics**: Match stroke width, bounding box (16px, 20px, 24px), and optical weight across all icons on the same page.
- **Style Browser Surfaces**: Custom focus rings, text selection (`::selection`), caret color, and scrollbars must be themed to match the palette rather than left at ugly browser defaults.
