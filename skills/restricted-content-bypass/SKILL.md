---
name: restricted-content-bypass
description: "Techniques for fetching and re-hosting content from Telegram channels with restricted saving (noforwards flag) using MTProto in Rust (restricted)."
version: 1.0.0
category: telegram-mtproto
author: Telegram MTProto Engineers
tags: [restricted-content, noforwards, grammers, mtproto, media-downloader, rust]
---

# Restricted Telegram Media Extraction & Re-Hosting Standards

High-speed extraction of media from Telegram channels and chats where forwarding and saving are restricted (`noforwards` flag) via pure Rust MTProto (`/root/bots/restricted`).

## 1. MTProto Extraction Architecture
Telegram client applications enforce `noforwards` by disabling the UI forward/save button. The raw MTProto protocol still delivers `MessageMediaDocument` and `MessageMediaPhoto` with access hashes to authorized member accounts.
- **Client**: Use `grammers-client` authorized with a user session (userbot).
- **Resolution**: Fetch the specific message by ID using `client.invoke(&tl::functions::channels::GetMessages { ... })`.

## 2. Streaming Without Memory Bloat
1. **Direct Stream Re-Hosting**: Download chunks sequentially (typically 128KB chunks) and stream directly to local disk or re-upload pipe.
2. **Chunk Checksums**: Verify chunk byte lengths to prevent corrupted media uploads.
3. **FloodWait Discipline**: Handle code 420 gracefully; sleep with random jitter before continuing sequential downloads.
