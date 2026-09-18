# Telegram Button Styling, Colors & Bot API 9.4 Standards

Enforce complete button styling, disciplined color semantics, and Telegram Bot API 9.4+ standards across all Telegram bots, webhooks, and MTProto pipelines.

## 1. Bot API 9.4 & MTProto Styling Equivalence
- **Full Color Support in Webhooks**: Telegram Bot API 9.4+ natively supports button styling and colors via the `style` field (`"primary" | "success" | "danger"`). Never strip button styling or degrade to monochromatic buttons.
- **Semantic Button Style Mapping**:
  - `bg_primary: true` $\rightarrow$ `"style": "primary"` (Blue accent: for primary navigation, source channel, informational actions, and main CTAs).
  - `bg_success: true` $\rightarrow$ `"style": "success"` (Green accent: for bot developer, enabled features, active locks, confirmations).
  - `bg_danger: true` $\rightarrow$ `"style": "danger"` (Red accent: for adding bot to groups, disabled locks, bans, kicks, deletions, and cancellation).
- **Custom Emoji Support**:
  - `icon: Some(id)` $\rightarrow$ `"icon_custom_emoji_id": "<id>"` in Bot API inline keyboards.

## 2. Canonical Start Menu Button Styling Standard
For all public/sub-bot `/start` menus, the standard button layout and color mapping is strictly enforced:
- **Row 1**:
  - `• المطور •` (`url`: `tg://user?id=<sudo_id>`) $\rightarrow$ `"style": "success"` (Green).
  - `• السورس •` (`url`: `<source_url>`) $\rightarrow$ `"style": "primary"` (Blue).
- **Row 2**:
  - `• اضفني •` (`url`: `https://t.me/<bot_uname>?startgroup=true...`) $\rightarrow$ `"style": "danger"` (Red).

## 3. Universal Converter Coverage (`buttons_to_botapi_markup`)
- **All Button Variants**: Every button type (`Callback`, `Url`, `UserProfile`, `WebView`) must pass through `apply_style_to_json` to attach `"style"` and `"icon_custom_emoji_id"`.
- **Zero Loss Conversion**: Converting MTProto TL structures into Telegram Bot API JSON schemas must never omit or drop styling attributes.
- **Premium Emoji Isolation**: If a bot lacks Telegram Premium for custom emojis and API returns an emoji error, strip ONLY `icon_custom_emoji_id`. Never strip the `style` attribute, as button colors are standard for all bots.

## 4. Keyboard Construction Discipline
- **Canonical Builders**: All inline keyboards must be constructed using `src/styling/keyboards.rs` and `src/styling/buttons.rs` (`styled_button_data`, `styled_button_url`, `make_button_style`).
- **No Monochromatic Downgrades**: Never remove `style` parameters from `make_button_style` or send raw unstyled button JSON when styled buttons are expected.

## 5. Daemon Reload & Process Verification
- **Immediate Process Replacement**: After compiling a new binary with button styling changes, never leave an old process running. Terminate the obsolete PID and launch the fresh binary in the screen session immediately to ensure updates are live.
