---
name: agentic-dialogue-management
description: "Dialogue State Tracking (DST), parameter slot-filling algorithms, context compaction, and conversational state machines for Telegram bots."
version: 1.0.0
category: ai-agent
author: Conversational AI Engineering
tags: [agentic, dialogue-state-tracking, slot-filling, context-compaction, nlu, telegram]
---

# Agentic Dialogue State Tracking & Slot-Filling Systems

Build conversational AI agents that understand free-form user intents, track dialogue state across turns, and slot-fill missing parameters naturally.

## 1. Dialogue State Machine (DST)
```
[User Utterance] ──> [Intent Classifier] ──> [Entity & Slot Extractor]
                             │
                             ▼
                 [Are Required Slots Complete?]
                       │               │
                      YES              NO
                       │               │
                       ▼               ▼
             [Execute Bot Tool]   [Emit Slot-Filling Prompt]
```

## 2. Slot Extraction & Normalization
1. **Multi-Dialect Normalization**: Normalize colloquial Arabic (Iraqi, Levantine, Gulf) and developer jargon before slot extraction.
2. **Slot Whitelist**: Each bot service defines required and optional slots:
   - `instagram_downloader`: Required `url` (regex: `https?://(www\.)?instagram\.com/.*`).
   - `music_voice_chat`: Required `query_or_url`, optional `chat_id`.
   - `session_generator`: Required `framework`, `phone_number`.
3. **Conversational Slot-Filling**: When a slot is missing, emit a natural, contextual prompt asking only for the missing detail. Never repeat completed slots.

## 3. Context Compaction
- Remove polite conversational filler words while preserving extracted slots in working memory.
- Evict stale dialogue states after 15 minutes of inactivity.
