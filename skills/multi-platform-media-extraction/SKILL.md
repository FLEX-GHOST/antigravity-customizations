---
name: multi-platform-media-extraction
description: "High-throughput media extraction for Instagram, TikTok, YouTube, and Pinterest without authentication walls in Rust (fastdl-rs, social)."
version: 1.0.0
category: media-extraction
author: Media Infrastructure Engineers
tags: [fastdl-rs, instagram, tiktok, youtube, media-extraction, yt-dlp, rust]
---

# Multi-Platform High-Performance Media Extraction Architecture

Architect resilient, high-speed extractors for social platforms (Instagram Reels/Stories, TikTok watermark-free, YouTube) in Rust (`fastdl-rs`, `social`).

## 1. Platform-Specific Strategies
- **Instagram**: Query internal GraphQL endpoints (`doc_id` / `query_hash`) or extract JSON payload from `<script type="application/json">` tags. Avoid login walls by using rotating clean user-agents.
- **TikTok**: Extract the `play_addr` or `download_addr` from the video object and strip the watermark parameter (`watermark=0` / clean CDN URL).
- **YouTube**: Use stream URL deobfuscation with cipher solver; prefer direct video/audio muxing with FFmpeg.

## 2. Zero-RAM Streaming Invariant
- Never hold full video files in RAM (`Vec<u8>`).
- Stream response body directly to `tokio::fs::File` with buffered chunks.
- When sending to Telegram, pass the file path directly to `Multipart` or file descriptor.
