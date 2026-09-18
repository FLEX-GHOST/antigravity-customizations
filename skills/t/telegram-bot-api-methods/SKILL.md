---
name: telegram-bot-api-methods
description: Complete, official master reference for ALL 185 Telegram Bot API methods and 400 types (Bot API 10.3). Includes method signatures, parameter tables, return types, Rust/HTTP execution patterns, and Bot API 9.4+ button styling standards.
triggers:
  - telegram bot api methods
  - telegram method
  - botapi methods
  - sendmessage parameters
  - inline keyboard style
  - telegram api spec
  - telegram webhook methods
  - teloxide methods
  - bot api 10
  - bot api 9.4
---

# Complete Telegram Bot API Methods & Types Master Reference (Bot API 10.3)

## 1. Overview & Architectural Standards
This skill is the canonical, authoritative catalog of **all 185 Telegram Bot API methods** and **all 400 types** as of late 2026 (Bot API 10.3).

### Bot API 9.4+ Standards & Invariants
1. **Button Styling (`InlineKeyboardButton`)**:
   - Buttons support the `style` field: `"primary"` (dominant blue/brand), `"success"` (green confirmation), `"danger"` (red destructive).
   - Never strip button styling or degrade to monochromatic buttons.
2. **Chat ID Formatting**:
   - User private chats: Positive string without `-100` (e.g. `"6149403807"`).
   - Supergroups & Channels: Always prefixed with `"-100"` (e.g. `"-1002149403807"`).
   - Basic groups: Standard negative ID without `-100`.
3. **Secret Token Header**:
   - Webhook updates must be verified with `X-Telegram-Bot-Api-Secret-Token`.

---

## 2. Categorized Methods Index (185 Methods)

### A. Updates & Webhooks (4 Methods)
* [`getUpdates`](references/methods_table.md#getupdates): Receive incoming updates using long polling.
* [`setWebhook`](references/methods_table.md#setwebhook): Specify a URL and receive incoming updates via an outgoing webhook. Supports `secret_token`, `allowed_updates`, `ip_address`, `drop_pending_updates`.
* [`deleteWebhook`](references/methods_table.md#deletewebhook): Remove webhook integration.
* [`getWebhookInfo`](references/methods_table.md#getwebhookinfo): Get current webhook status, pending update count, and last error.

### B. Basic Bot Identity & Commands (14 Methods)
* [`getMe`](references/methods_table.md#getme): Basic information about the bot (id, username, can_join_groups, can_read_all_group_messages, supports_inline_queries).
* [`setMyCommands`](references/methods_table.md#setmycommands) / [`getMyCommands`](references/methods_table.md#getmycommands) / [`deleteMyCommands`](references/methods_table.md#deletemycommands): Manage bot commands with specific `BotCommandScope`.
* [`setMyName`](references/methods_table.md#setmyname) / [`getMyName`](references/methods_table.md#getmyname): Change bot name.
* [`setMyDescription`](references/methods_table.md#setmydescription) / [`getMyDescription`](references/methods_table.md#getmydescription): Change bot description shown in empty chats.
* [`setMyShortDescription`](references/methods_table.md#setmyshortdescription) / [`getMyShortDescription`](references/methods_table.md#getmyshortdescription): Change text on bot profile page.

### C. Sending Messages & Rich Content (23 Methods)
* [`sendMessage`](references/methods_table.md#sendmessage): Send text messages. Supports `parse_mode` (`HTML` / `MarkdownV2`), `entities`, `reply_markup` (`InlineKeyboardMarkup`, `ReplyKeyboardMarkup`), `link_preview_options`.
* [`forwardMessage`](references/methods_table.md#forwardmessage) / [`forwardMessages`](references/methods_table.md#forwardmessages): Forward single or batch messages.
* [`copyMessage`](references/methods_table.md#copymessage) / [`copyMessages`](references/methods_table.md#copymessages): Copy messages without link to original author.
* [`sendPhoto`](references/methods_table.md#sendphoto), [`sendAudio`](references/methods_table.md#sendaudio), [`sendDocument`](references/methods_table.md#senddocument), [`sendVideo`](references/methods_table.md#sendvideo), [`sendAnimation`](references/methods_table.md#sendanimation), [`sendVoice`](references/methods_table.md#sendvoice), [`sendVideoNote`](references/methods_table.md#sendvideonote): Send media files via file_id or multipart upload.
* [`sendPaidMedia`](references/methods_table.md#sendpaidmedia): Send paid media requiring Telegram Stars to unlock.
* [`sendMediaGroup`](references/methods_table.md#sendmediagroup): Send album of up to 10 photos/videos.
* [`sendLocation`](references/methods_table.md#sendlocation), [`sendVenue`](references/methods_table.md#sendvenue), [`sendContact`](references/methods_table.md#sendcontact), [`sendPoll`](references/methods_table.md#sendpoll), [`sendDice`](references/methods_table.md#senddice).
* [`sendChatAction`](references/methods_table.md#sendchataction): Broadcast typing/uploading status (e.g. `typing`, `upload_photo`, `record_voice`).
* [`setMessageReaction`](references/methods_table.md#setmessagereaction): Set custom emoji or standard reactions on messages.

### D. Updating & Deleting Messages (7 Methods)
* [`editMessageText`](references/methods_table.md#editmessagetext): Edit text of sent messages or inline messages.
* [`editMessageCaption`](references/methods_table.md#editmessagecaption): Edit media captions.
* [`editMessageMedia`](references/methods_table.md#editmessagemedia): Replace photo/video in existing message.
* [`editMessageReplyMarkup`](references/methods_table.md#editmessagereplymarkup): Dynamically update button states and colors.
* [`stopPoll`](references/methods_table.md#stoppoll): Stop active poll.
* [`deleteMessage`](references/methods_table.md#deletemessage) / [`deleteMessages`](references/methods_table.md#deletemessages): Atomic single or batch message deletion.

### E. Chat Management & Moderation (44 Methods)
* [`banChatMember`](references/methods_table.md#banchatmember) / [`unbanChatMember`](references/methods_table.md#unbanchatmember): Ban user from supergroup/channel with optional `until_date` and `revoke_messages`.
* [`restrictChatMember`](references/methods_table.md#restrictchatmember): Granular permissions (`can_send_messages`, `can_send_media_messages`, `can_send_polls`, etc.).
* [`promoteChatMember`](references/methods_table.md#promotechatmember): Assign admin rights (`can_change_info`, `can_post_messages`, `can_edit_messages`, `can_delete_messages`, `can_invite_users`, `can_restrict_members`, `can_pin_messages`, `can_manage_video_chats`, `can_manage_topics`).
* [`exportChatInviteLink`](references/methods_table.md#exportchatinvitelink) / [`createChatInviteLink`](references/methods_table.md#createchatinvitelink) / [`editChatInviteLink`](references/methods_table.md#editchatinvitelink): Create primary or custom invite links with expiration, member limits, or join requests.
* [`createChatSubscriptionInviteLink`](references/methods_table.md#createchatsubscriptioninvitelink): Monthly recurring Telegram Star subscription channel invites.
* [`getChat`](references/methods_table.md#getchat): Retrieve chat object, member count, pinned message, permissions, active usernames.
* [`getChatAdministrators`](references/methods_table.md#getchatadministrators) / [`getChatMember`](references/methods_table.md#getchatmember).
* Forum Topics: [`createForumTopic`](references/methods_table.md#createforumtopic), [`editForumTopic`](references/methods_table.md#editforumtopic), [`closeForumTopic`](references/methods_table.md#closeforumtopic), [`reopenForumTopic`](references/methods_table.md#reopenforumtopic), [`deleteForumTopic`](references/methods_table.md#deleteforumtopic).

### F. Inline Mode & User Interactions (4 Methods)
* [`answerCallbackQuery`](references/methods_table.md#answercallbackquery): Acknowledge button clicks, display toast notification (`text`), or open alert modal (`show_alert: true`).
* [`answerInlineQuery`](references/methods_table.md#answerinlinequery): Return inline search results (articles, photos, music).
* [`answerWebAppQuery`](references/methods_table.md#answerwebappquery): Pass data back from Telegram Mini App to chat.
* [`savePreparedInlineMessage`](references/methods_table.md#savepreparedinlinemessage): Pre-save message for mini-app sharing.

### G. Payments, Telegram Stars & Gifts (13 Methods)
* [`sendInvoice`](references/methods_table.md#sendinvoice) / [`createInvoiceLink`](references/methods_table.md#createinvoicelink): Invoices for Stars (`currency: "XTR"`) or fiat currencies.
* [`answerShippingQuery`](references/methods_table.md#answershippingquery) / [`answerPreCheckoutQuery`](references/methods_table.md#answerprecheckoutquery): Authorize payment before charge.
* [`getStarTransactions`](references/methods_table.md#getstartransactions): Ledger of earned and spent Stars.
* [`refundStarPayment`](references/methods_table.md#refundstarpayment): Refund Star transaction.
* [`sendGift`](references/methods_table.md#sendgift): Send Telegram collectible gifts to users.
* Verification: [`verifyUser`](references/methods_table.md#verifyuser), [`verifyChat`](references/methods_table.md#verifychat), [`removeUserVerification`](references/methods_table.md#removeuserverification).

### H. Telegram Business (1 Method)
* [`getBusinessConnection`](references/methods_table.md#getbusinessconnection): Inspect connected business bot account status.

### I. Stickers & Custom Emojis (16 Methods)
* [`sendSticker`](references/methods_table.md#sendsticker), [`getStickerSet`](references/methods_table.md#getstickerset), [`getCustomEmojiStickers`](references/methods_table.md#getcustomemojistickers), [`createNewStickerSet`](references/methods_table.md#createnewstickerset), [`addStickerToSet`](references/methods_table.md#addstickertoset).

---

## 3. High-Performance Execution Pattern in Rust (Reqwest / Axum)

```rust
use serde::{Serialize, Deserialize};

#[derive(Serialize)]
pub struct SendMessagePayload<'a> {
    pub chat_id: &'a str,
    pub text: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parse_mode: Option<&'a str>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reply_markup: Option<InlineKeyboardMarkup>,
}

#[derive(Serialize)]
pub struct InlineKeyboardMarkup {
    pub inline_keyboard: Vec<Vec<InlineKeyboardButton>>,
}

#[derive(Serialize)]
pub struct InlineKeyboardButton {
    pub text: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub callback_data: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub style: Option<String>, // "primary" | "success" | "danger" (Bot API 9.4+)
}

pub async fn send_telegram_message(
    client: &reqwest::Client,
    bot_token: &str,
    chat_id: &str,
    text: &str,
    markup: Option<InlineKeyboardMarkup>
) -> Result<reqwest::Response, reqwest::Error> {
    let url = format!("https://api.telegram.org/bot{}/sendMessage", bot_token);
    let payload = SendMessagePayload {
        chat_id,
        text,
        parse_mode: Some("HTML"),
        reply_markup: markup,
    };
    client.post(&url).json(&payload).send().await
}
```

---

## 4. Local Lookup Utility
Query any method or type parameter specification instantly via:
```bash
python3 scripts/lookup_telegram_api.py sendMessage
python3 scripts/lookup_telegram_api.py InlineKeyboardButton
python3 scripts/lookup_telegram_api.py sendPaidMedia
```
