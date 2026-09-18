---
name: better-icons
description: Search, retrieve, optimize, and embed scalable SVG icons from 200+ icon libraries (Iconify) including Lucide, Heroicons, Material Design, Phosphor, and Tabler. Use for UI design, Telegram Mini Apps, and web interfaces. Never use raw emojis in production buttons or badges.
---

# Better Icons: Complete SVG Vector Iconography Guide

Search, retrieve, and embed production-ready SVG vector icons across 200+ icon sets (200,000+ icons) via Iconify and the `better-icons` CLI/API.

---

## 1. Zero Raw Emojis Rule (Anti-AI Slop Standard)

- **BANNED**: Never dump raw emojis (e.g. `🔥`, `🚀`, `⭐`, `⚙️`, `🗑️`, `📊`, `❌`, `✅`) into production UI buttons, headers, status badges, or navigation bars. Emojis render inconsistently across operating systems, lack optical alignment with text, cannot inherit font color (`currentColor`), and degrade professional aesthetic quality.
- **MANDATORY**: Use clean, scalable vector SVGs with consistent stroke width, aligned bounding boxes, and dynamic color inheritance (`currentColor`).

---

## 2. Installation & CLI Usage

### Installation
```bash
# Global installation (recommended for CLI and AI agents)
npm install -g better-icons
# or with Bun:
bun add -g better-icons
```

### CLI Command Reference
```bash
# Search icons across 200+ libraries
better-icons search <query> [--prefix <prefix>] [--limit <n>] [--json]

# Download single icon SVG directly to stdout or file
better-icons get <prefix:icon-name> [--color <color>] [--size <px>] > icon.svg

# Batch download search results to directory
better-icons search <query> -d ./icons/ [--color <color>] [--size <px>] [--limit 32]

# List all supported collections
better-icons list

# Get information about an icon set
better-icons info <prefix>
```

### Practical CLI Examples
```bash
# Search for home icons in Lucide
better-icons search home --prefix lucide --limit 5

# Download a Lucide settings icon
better-icons get lucide:settings > public/icons/settings.svg

# Download an outline trash icon for a destructive button
better-icons get heroicons:trash-20-solid --color currentColor > trash.svg

# Search across all sets and output structured JSON
better-icons search arrow --json | jq '.icons[0]'
```

---

## 3. Direct HTTP API Access (Zero-Install Fallback)

If the `better-icons` CLI is not installed in the environment, fetch SVG assets directly from the Iconify REST API via `curl` or `fetch`:

### Direct SVG Retrieval via `curl`
```bash
# Format: https://api.iconify.design/{prefix}/{name}.svg
curl -s "https://api.iconify.design/lucide/home.svg" > home.svg
curl -s "https://api.iconify.design/heroicons/check-circle.svg?color=%2322c55e" > check.svg
curl -s "https://api.iconify.design/tabler/refresh.svg?width=24&height=24" > refresh.svg
```

### REST API Query Parameters
| Parameter | Description | Default | Example |
|---|---|---|---|
| `color` | Color replacement (URL encoded hex or keyword) | `currentColor` | `?color=%23ff0000` |
| `width` | Explicit rendered width in pixels | Natural set width | `?width=20` |
| `height` | Explicit rendered height in pixels | Natural set height | `?height=20` |
| `rotate` | Rotate icon in degrees (90, 180, 270) | `0` | `?rotate=90` |
| `flip` | Flip orientation (`horizontal`, `vertical`) | none | `?flip=horizontal` |
| `box` | Preserve original view box bounds (`true`/`false`) | `false` | `?box=true` |

### Search API Endpoint
```bash
# Query icons via REST API
curl -s "https://api.iconify.design/search?query=lock&limit=5" | jq '.icons'
```

---

## 4. Popular & Recommended Icon Libraries

| Library Prefix | Library Name | Total Icons | Style & Characteristics | Recommended For |
|---|---|---|---|---|
| `lucide:` | Lucide Icons | ~1,400 | Crisp, 2px stroke, clean geometric bounds | Modern SaaS, bot factory dashboards, settings |
| `heroicons:` | Heroicons | ~300 | 20px solid & 24px outline | Forms, transactional modals, clean alerts |
| `ph:` | Phosphor Icons | ~9,000 | 6 weights (thin, light, regular, bold, fill, duotone) | Creative apps, media controls, status indicators |
| `tabler:` | Tabler Icons | ~5,200 | Consistent 2px stroke, extensive technical set | High-density tables, system monitors, telemetry |
| `solar:` | Solar Icons | ~7,400 | Modern broken, linear, bold duotone | Telegram Mini Apps, Web3 wallets, mobile apps |
| `mdi:` | Material Design | ~7,000 | Standard Google Material symbols | Enterprise portals, mobile navigation, utility bars |
| `carbon:` | IBM Carbon Icons | ~2,100 | Precise, engineered, 16/20/24/32px grids | Financial systems, logs, cloud management |
| `ri:` | Remix Icon | ~2,800 | Neutral, balanced line & fill | Content management, blogs, social widgets |
| `radix-icons:` | Radix Icons | ~300 | 15×15px optical precision | Precision UI, dropdown menus, context toolbars |
| `simple-icons:`| Simple Icons | ~3,100 | Authentic brand and technology vectors | Telegram, TON, GitHub, payment systems, OAuth |

---

## 5. Architectural Standards for UI Embedding

### Optical Metrics & Sizing Consistency
Maintain uniform icon dimensions within the same visual hierarchy:
- **Small (16×16px)**: Badges, inline pills, compact table cells, input clear buttons.
- **Default (20×20px)**: Primary buttons, standard form controls, list items, dropdown options.
- **Medium (24×24px)**: Main navigation bars, tab bars, card headers, floating action buttons.
- **Large (32×32px)**: Metric summary headers, feature highlight callouts.
- **Hero / Empty States (48×48px to 64×64px)**: Empty states, error recovery illustrations.

### Color Inheritance & Dynamic Theming
Always configure SVG paths with `currentColor` so the icon automatically matches font color, button hover states, and dark/light mode transitions:

```html
<!-- Button with Inline SVG inheriting text color -->
<button class="btn btn-primary">
  <svg class="icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M5 12h14M12 5l7 7-7 7"/>
  </svg>
  <span>Continue</span>
</button>
```

```css
/* Ensure all inline icons inherit color and maintain stroke consistency */
.icon {
  display: inline-block;
  vertical-align: middle;
  flex-shrink: 0;
  color: inherit;
}
```

---

## 6. Pure CSS Icon Masking Technique (Zero-JS & Zero Extra HTTP Requests)

CSS Masking allows any SVG icon to be used as a background mask while controlling its color entirely through standard CSS `background-color`. This enables hover color changes, gradient fills, and theme adaptation without mutating the SVG XML:

```css
.icon-mask {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-color: currentColor;
  -webkit-mask-size: contain;
  mask-size: contain;
  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-position: center;
}

/* Example with Lucide check icon */
.icon-check {
  -webkit-mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 6 9 17l-5-5'/%3E%3C/svg%3E");
  mask-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M20 6 9 17l-5-5'/%3E%3C/svg%3E");
}
```

---

## 7. Telegram Mini App (TWA) SVG Optimization

In Telegram Mini Apps, webview performance and low memory consumption are critical:

1. **Inline SVGs or SVG Symbol Sprites**: Never fire separate HTTP requests for icons on load. Bundle icons into a hidden SVG sprite at the end of `index.html`:
   ```html
   <!-- Hidden Sprite Sheet -->
   <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
     <symbol id="icon-home" viewBox="0 0 24 24">
       <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
     </symbol>
     <symbol id="icon-user" viewBox="0 0 24 24">
       <path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"/>
     </symbol>
   </svg>

   <!-- Usage in Components -->
   <svg class="icon" width="24" height="24"><use href="#icon-home"/></svg>
   ```

2. **Strip Metadata & XML Headers**: Strip `<?xml...>`, `<title>`, redundant IDs, and editor comments to minimize DOM weight:
   ```bash
   # SVG Optimization with SVGO
   npx svgo --multipass icon.svg -o icon.min.svg
   ```

3. **Stroke Scalability**: Always add `vector-effect="non-scaling-stroke"` when icons are transformed or scaled via CSS animations so that stroke weights remain optical and do not distort.

---

## 8. Web Accessibility Standards (WCAG 2.2 AA)

1. **Decorative Icons**: When an icon accompanies descriptive button text or label, hide it from screen readers:
   ```html
   <button class="btn">
     <svg aria-hidden="true" focusable="false" class="icon" ...>...</svg>
     <span>Save Settings</span>
   </button>
   ```

2. **Standalone Icon Buttons (Icon-Only)**: When an interactive button contains only an icon, provide an accessible label:
   ```html
   <button class="btn-icon" aria-label="Delete bot instance">
     <svg aria-hidden="true" focusable="false" class="icon" ...>...</svg>
   </button>
   ```

3. **Informational Standalone Icons**: When an icon conveys standalone status (e.g. status indicator dot):
   ```html
   <svg role="img" aria-labelledby="status-title" class="icon-status" ...>
     <title id="status-title">Active and Healthy</title>
     <circle cx="12" cy="12" r="10" fill="currentColor"/>
   </svg>
   ```

---

## 9. MCP Server Tools for AI Agents

When the `better-icons` MCP server is enabled in the agent environment, use:
- `search_icons(query, prefix, limit)`: Search across 200+ icon libraries.
- `get_icon(icon_id, color, size)`: Fetch clean SVG string directly into working context.
- `recommend_icons(use_case, style)`: Get expert suggestions for specific UI domains.
- `list_collections()`: Browse all installed icon sets and metadata.
