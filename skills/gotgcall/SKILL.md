---
name: gotgcall
description: "Master guide for Go Telegram VoIP and Group Calls (github.com/annihilatorrrr/gotgcall): WebRTC group call joining, RTCP, Pion WebRTC, and Opus audio streaming."
version: 1.0.0
category: go-telegram-voip
author: Telegram VoIP Systems Engineers
tags: [gotgcall, pion, webrtc, opus, telegram-voip, group-call, audio-streaming, go]
---

# Gotgcall Telegram Group Call Master Engineering Guide

Build high-performance, real-time voice chat music and streaming bots in Go using `github.com/annihilatorrrr/gotgcall` and `pion/webrtc/v4`.

## 1. Group Call Architecture
`gotgcall` connects directly to Telegram's WebRTC SFU (Selective Forwarding Unit) via `gogram` MTProto updates:
```go
package main

import (
    "github.com/amarnathcjd/gogram/telegram"
    "github.com/annihilatorrrr/gotgcall"
)

func initVoIP(client *telegram.Client) (*gotgcall.TgCall, error) {
    tgCall, err := gotgcall.NewTgCall(client)
    if err != nil {
        return nil, err
    }
    return tgCall, nil
}
```

## 2. Streaming Audio into Voice Chat
Stream 48kHz Stereo 20ms Opus frames into the active group call:
```go
func playAudio(tgCall *gotgcall.TgCall, chatID int64, filePath string) error {
    return tgCall.Play(chatID, gotgcall.AudioInput{
        FilePath: filePath,
        Live:     false,
    })
}
```

## 3. High-Performance Audio Pipeline Invariants
1. **FFmpeg Demuxing**: Transcode source streams with `-f s16le -ac 2 -ar 48000` directly to stdin/stdout pipes.
2. **Zero-RAM Buffering**: Never buffer entire songs in memory. Read in chunks of 3840 bytes (960 samples * 2 channels * 2 bytes/sample).
3. **Pion WebRTC Integration**: Tune DTLS retransmission timers and SRTP replay protection windows for minimal packet loss over variable mobile connections.
