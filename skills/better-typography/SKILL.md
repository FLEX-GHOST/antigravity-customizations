---
name: better-typography
description: 'Master web typography: type scales, line-height ratios, variable fonts, OpenType features (tnum, slashed-zero), wrapping & line measure (65ch), smart punctuation, CSS Cheat Sheet with Tailwind mappings, and mobile input accessibility.'
license: MIT
metadata:
  version: "2.0.0"
---

# Web Typography: Complete Engineering Handbook

A comprehensive engineering guide for digital typography: type scales, line heights, variable font axes, OpenType features, measure capping, smart punctuation, and mobile input accessibility.

---

## 1. Core Principles of Typography

Typography is mostly restraint: a disciplined scale, comfortable vertical rhythm, and sufficient contrast.
- **Serve `.woff2`**: Use modern WOFF2 with Brotli compression on the web. `.ttf` and `.otf` are uncompressed desktop formats.
- **Properties over Raw Tags**: When a CSS property exists, use it (`font-weight: 650`, `font-optical-sizing: auto`, `font-variant-numeric: tabular-nums`). Reserve raw `font-feature-settings` for custom axes (`"GRAD" 80`) or niche stylistic sets (`"ss01"`).
- **Fewer Fonts & Weights**: Rarely use more than two typeface families (primary body/heading + monospace code).
- **Weight Floor**: Below `18px`, stay at weight `400` or heavier. Weights under `300` are display-only at `28px`+; they degrade and disappear at small sizes.
- **Font Smoothing on Root**:
  ```css
  html {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  ```

---

## 2. Type Scale & Role Hierarchy

A disciplined type scale maps each semantic role to an exact size, line-height, and weight:

| Role | CSS Size | Equivalent Pixels | Line-Height | Recommended Weight | Tailwind Class |
|---|---|---|---|---|---|
| **Display** | `2.25rem` | 36px | `1.1` | `700` (Bold) | `text-4xl leading-tight font-bold` |
| **Title / H1** | `1.5rem` | 24px | `1.2` | `600` (SemiBold) | `text-2xl leading-snug font-semibold` |
| **Heading / H2**| `1.125rem` | 18px | `1.3` | `600` (SemiBold) | `text-lg leading-snug font-semibold` |
| **Body (Default)**| `1.0rem` | 16px | `1.5`–`1.6` | `400` (Regular) | `text-base leading-relaxed font-normal` |
| **UI / Inputs** | `0.875rem` | 14px | `1.4` | `500` (Medium) | `text-sm leading-normal font-medium` |
| **Captions / Pills**| `0.8125rem` | 13px | `1.3` | `500` (Medium) | `text-xs leading-normal font-medium` |

### Heading Hierarchy Rules
- Map heading levels to descending steps of the scale. A visually subordinate heading must never overpower its parent.
- Never choose an HTML heading element (`<h1>`–`<h6>`) merely for its browser default size; choose semantics first, then style in CSS.

---

## 3. Line-Height, Letter-Spacing & Measure

### Line-Height by Role
- **Headings**: Tighter leading (`1.1` to `1.25`).
- **Body Text**: Generous leading (`1.5` to `1.65`). Never use `leading-none` or `line-height: 1.1` on text that wraps to 3+ lines.

### Letter-Spacing (Tracking)
- **Large Headings**: Slightly negative tracking (`-0.01em` to `-0.02em` / `tracking-tight`).
- **Uppercase Badges & Overlines**: Slightly positive tracking (`0.05em` to `0.1em` / `tracking-wider`).
- **Arabic Text**: Strictly `letter-spacing: 0` (Banned in Arabic script).

### Line Measure (Capping Length)
Lines longer than 75 characters strain reading comprehension. Cap long-form prose between 60–75 characters per line:
```css
.article-body, .prose {
  max-width: 65ch; /* Or max-w-2xl in Tailwind */
}
```

---

## 4. Wrapping, Overflow & Truncation

| Goal | CSS Declaration | Tailwind Equivalent | Use Case |
|---|---|---|---|
| Balance heading wraps | `text-wrap: balance;` | `text-balance` | Short 2-3 line headlines |
| Prevent single orphaned words | `text-wrap: pretty;` | `text-pretty` | Card descriptions, paragraphs |
| Break long URLs or IDs | `overflow-wrap: break-word;` | `break-words` | User IDs, hashes, links |
| Single-line truncation | `white-space: nowrap; overflow: hidden; text-overflow: ellipsis;` | `truncate` | Table cells, badges |
| Multi-line clamp | `display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;` | `line-clamp-2` | Summary cards |

---

## 5. Variable Fonts & OpenType Features

### Common Variable Font Axes
- `wght` (Weight: 100–900): Controlled via `font-weight: 550;`.
- `opsz` (Optical Sizing): Controlled via `font-optical-sizing: auto;`.
- `wdth` (Width): Controlled via `font-stretch: 90%;`.

### High-Impact OpenType Features

```css
/* 1. Tabular Numbers: Equal-width digits for changing counters/tables */
.tabular-nums {
  font-variant-numeric: tabular-nums;
}

/* 2. Slashed Zero: Distinguish number 0 from letter O */
.slashed-zero {
  font-variant-numeric: slashed-zero;
}

/* 3. Real Small Capitals */
.small-caps {
  font-variant-caps: small-caps;
}

/* 4. Stylistic Sets (e.g. Inter single-story 'a' or curved 'r') */
.custom-style {
  font-feature-settings: "ss01" 1, "cv11" 1;
}
```

---

## 6. CSS Cheat Sheet: Vanilla CSS to Tailwind Mappings

| Style Goal | Vanilla CSS | Tailwind CSS |
|---|---|---|
| **Tabular Numbers** | `font-variant-numeric: tabular-nums;` | `tabular-nums` |
| **Slashed Zero** | `font-variant-numeric: slashed-zero;` | `slashed-zero` |
| **Heading Balance** | `text-wrap: balance;` | `text-balance` |
| **Orphan Prevention** | `text-wrap: pretty;` | `text-pretty` |
| **Tight Tracking** | `letter-spacing: -0.025em;` | `tracking-tight` |
| **Wide Tracking** | `letter-spacing: 0.05em;` | `tracking-wider` |
| **Underline Offset** | `text-underline-offset: 4px;` | `underline-offset-4` |
| **Skip Descenders** | `text-decoration-skip-ink: auto;` | `[text-decoration-skip-ink:auto]` |
| **Text Truncation** | `overflow: hidden; text-overflow: ellipsis; white-space: nowrap;` | `truncate` |
| **Line Clamp (3 lines)**| `-webkit-line-clamp: 3;` | `line-clamp-3` |
| **Font Smoothing** | `-webkit-font-smoothing: antialiased;` | `antialiased` |

---

## 7. Mobile Accessibility & Punctuation Rules

### 16px Input Rule for iOS Safari
iOS Safari automatically zooms in and scales the entire viewport when any input element has a `font-size` smaller than `16px`.
- Always set input font size to at least `16px` on mobile:
  ```css
  input, select, textarea {
    font-size: 16px; /* Prevents auto-zoom on mobile */
  }
  @media (min-width: 640px) {
    input, select, textarea {
      font-size: 14px; /* Scaled down for desktop */
    }
  }
  ```

### Smart Punctuation in Prose
- **En Dash for Ranges**: Use `2024–2026`, not hyphen `2024-2026`.
- **Em Dash for Asides**: Use `—` instead of two hyphens `--`.
- **Ellipsis Character**: Use `…` (`&hellip;`), not three separate periods `...`.
- **Non-Breaking Spaces**: Use `&nbsp;` between numbers and units (e.g. `16&nbsp;px`, `50&nbsp;MB`) so values never split across line wraps.
