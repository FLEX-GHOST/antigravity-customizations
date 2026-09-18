---
name: telegram-mini-app
description: Complete, production-grade guide for building Telegram Mini Apps (TWA) with seamless native integration. Covers the Telegram WebApp JS SDK, cryptographic HMAC-SHA256 authentication in Rust, UI lifecycle (MainButton, BackButton, HapticFeedback), theme parameter synchronization, and multi-tenant bot dashboard integration.
---

# Telegram Mini App (TWA) Production Architecture & SDK Standards

Build high-performance, native-feeling Telegram Mini Apps (TWA) integrated seamlessly with Telegram bots and backend APIs.

---

## 1. Telegram WebApp Frontend Lifecycle

### 1. Essential HTML Document Header
Mini Apps run inside Telegram's internal WebKit/Chromium WebView. Load the official Telegram script synchronously in `<head>`:
```html
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <!-- Official Telegram WebApp SDK -->
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <div id="app"></div>
  <script src="js/app.js"></script>
</body>
</html>
```

### 2. Initialization & Viewport Expansion
Invoke `ready()` and `expand()` immediately on boot to remove loading overlays and expand to full mobile viewport height:
```javascript
const tg = window.Telegram?.WebApp;

if (tg) {
  // Notify Telegram client that the Mini App is fully initialized
  tg.ready();
  
  // Expand WebView to full height (eliminates initial collapsed half-sheet)
  tg.expand();
  
  // Prevent accidental vertical swipe-to-dismiss when scrolling inside the app
  if (tg.isVerticalSwipesEnabled !== undefined) {
    tg.disableVerticalSwipes();
  }
}
```

---

## 2. Cryptographic HMAC-SHA256 Authentication (Rust Backend)

Never trust client-provided `user_id` or query parameters directly. Telegram provides `Telegram.WebApp.initData`, a cryptographically signed query string that the backend MUST verify using the bot token.

### Cryptographic Verification Algorithm:
1. Parse the `initData` query string into key-value pairs.
2. Extract the `hash` parameter and remove it from the data dictionary.
3. Sort all remaining pairs alphabetically by key and format as `key=value\n`.
4. Compute `secret_key = HMAC-SHA256("WebAppData", bot_token)`.
5. Compute `calculated_hash = HMAC-SHA256(secret_key, sorted_data_string)`.
6. Verify `calculated_hash == hash` using constant-time comparison (`subtle::ConstantTimeEq`).
7. Verify `auth_date` is within a reasonable window (e.g., within 24 hours) to prevent replay attacks.

### Idiomatic Rust Verification Implementation:
```rust
use hmac::{Hmac, Mac};
use sha2::Sha256;
use std::collections::BTreeMap;
use subtle::ConstantTimeEq;

type HmacSha256 = Hmac<Sha256>;

pub fn verify_telegram_init_data(init_data: &str, bot_token: &str) -> Result<TelegramUser, AuthError> {
    let mut params = BTreeMap::new();
    let mut provided_hash = None;

    for part in init_data.split('&') {
        if let Some((key, val)) = part.split_once('=') {
            let key = urlencoding::decode(key).map_err(|_| AuthError::MalformedData)?;
            let val = urlencoding::decode(val).map_err(|_| AuthError::MalformedData)?;
            if key == "hash" {
                provided_hash = Some(val.into_owned());
            } else {
                params.insert(key.into_owned(), val.into_owned());
            }
        }
    }

    let hash_hex = provided_hash.ok_or(AuthError::MissingHash)?;

    // Construct data-check-string (sorted alphabetically)
    let data_check_string: String = params
        .iter()
        .map(|(k, v)| format!("{k}={v}"))
        .collect::<Vec<_>>()
        .join("\n");

    // secret_key = HMAC_SHA256(b"WebAppData", bot_token)
    let mut mac = HmacSha256::new_from_slice(b"WebAppData").map_err(|_| AuthError::CryptoFailed)?;
    mac.update(bot_token.as_bytes());
    let secret_key = mac.finalize().into_bytes();

    // calculated_hash = HMAC_SHA256(secret_key, data_check_string)
    let mut mac = HmacSha256::new_from_slice(&secret_key).map_err(|_| AuthError::CryptoFailed)?;
    mac.update(data_check_string.as_bytes());
    let expected_hash = hex::encode(mac.finalize().into_bytes());

    if expected_hash.as_bytes().ct_eq(hash_hex.as_bytes()).unwrap_u8() != 1 {
        return Err(AuthError::InvalidSignature);
    }

    // Extract verified user json
    let user_json = params.get("user").ok_or(AuthError::MissingUser)?;
    let user: TelegramUser = serde_json::from_str(user_json).map_err(|_| AuthError::MalformedUser)?;

    Ok(user)
}
```

---

## 3. Native Telegram UI Components & Controls

### MainButton (Bottom Action Button)
Integrate with the native floating action button at the bottom of the client screen:
```javascript
const mainButton = tg.MainButton;

// Show Primary Action Button
mainButton.setText("حفظ الإعدادات");
mainButton.show();
mainButton.enable();

// Handle Click
mainButton.onClick(() => {
  mainButton.showProgress(); // Shows native spinner
  saveSettings().finally(() => {
    mainButton.hideProgress();
  });
});
```

### BackButton (Navigation Bar)
Handle multi-page history inside the Mini App:
```javascript
const backButton = tg.BackButton;

function navigateToDetail() {
  history.pushState({ page: 'detail' }, '');
  backButton.show();
}

backButton.onClick(() => {
  if (history.state?.page === 'detail') {
    history.back();
    backButton.hide();
  }
});
```

### Haptic Feedback (Physical Touch Sensations)
Provide tangible tactile feedback for user actions:
```javascript
const haptics = tg.HapticFeedback;

// Light tap for button clicks and toggles
haptics.impactOccurred('light'); // 'light', 'medium', 'heavy', 'rigid', 'soft'

// Notification feedback for state transitions
haptics.notificationOccurred('success'); // 'success', 'warning', 'error'

// Selection tick when scrolling through picker lists
haptics.selectionChanged();
```

---

## 4. Native Theme Synchronization

Synchronize CSS variables with Telegram's active color palette (`tg.themeParams`) so the Mini App seamlessly matches light mode, dark mode, and custom user themes:

```javascript
function applyTelegramTheme() {
  const theme = tg.themeParams;
  const root = document.documentElement;

  if (theme) {
    if (theme.bg_color) root.style.setProperty('--tg-bg-color', theme.bg_color);
    if (theme.text_color) root.style.setProperty('--tg-text-color', theme.text_color);
    if (theme.hint_color) root.style.setProperty('--tg-hint-color', theme.hint_color);
    if (theme.link_color) root.style.setProperty('--tg-link-color', theme.link_color);
    if (theme.button_color) root.style.setProperty('--tg-button-color', theme.button_color);
    if (theme.button_text_color) root.style.setProperty('--tg-button-text-color', theme.button_text_color);
    if (theme.secondary_bg_color) root.style.setProperty('--tg-secondary-bg-color', theme.secondary_bg_color);
  }

  // Sync header color with secondary background
  tg.setHeaderColor?.(theme.secondary_bg_color || 'bg_color');
  tg.setBackgroundColor?.(theme.bg_color || 'secondary_bg_color');
}

tg.onEvent('themeChanged', applyTelegramTheme);
applyTelegramTheme();
```

---

## 5. Launching Mini Apps from Telegram Bots

### 1. Inline Keyboard Button (Chat Access)
```rust
// Grammers / Telegram Bot API: InlineKeyboardButton with web_app
let inline_btn = InlineKeyboardButton::web_app("لوحة التحكم", "https://my-app.domain.com/panel");
```

### 2. Menu Button (Persistent Bot Profile Menu)
Set the persistent menu button via `setChatMenuButton`:
```json
{
  "menu_button": {
    "type": "web_app",
    "text": "فتح المصنع",
    "web_app": {
      "url": "https://my-app.domain.com"
    }
  }
}
```

### 3. Direct Link URL Format
Mini Apps can be opened from any chat, channel, or message via deep links:
`https://t.me/BotUsername/app_short_name?startapp=custom_payload`
Inside the Mini App, access the payload via `tg.initDataUnsafe.start_param`.
