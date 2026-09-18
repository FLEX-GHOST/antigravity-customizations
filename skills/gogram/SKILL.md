---
name: gogram
description: "Master guide for Go Telegram MTProto client library (github.com/amarnathcjd/gogram): client setup, update handlers, session strings, RPC execution, and userbots."
version: 1.0.0
category: go-telegram
author: Go Telegram Systems Engineers
tags: [gogram, go, golang, telegram, mtproto, session, userbot, rpc]
---

# Gogram Master Systems Engineering Guide

High-performance Telegram MTProto client development in pure Go using `github.com/amarnathcjd/gogram`.

## 1. Client Architecture & Initialization
```go
package main

import (
    "context"
    "log"
    "github.com/amarnathcjd/gogram/telegram"
)

func main() {
    client, err := telegram.NewClient(telegram.ClientConfig{
        AppID:   6, // Official Telegram API ID
        AppHash: "eb06d4abfb49dc3eeb1aeb98ae0f581e",
        Session: "session.dat", // or StringSession
    })
    if err != nil {
        log.Fatalf("failed to initialize gogram: %v", err)
    }

    // Login with Bot Token or Phone
    if err := client.LoginBot("BOT_TOKEN"); err != nil {
        log.Fatalf("login failed: %v", err)
    }

    client.Idle()
}
```

## 2. Event Handling & Middlewares
- **Message Filters**: Use typed event listeners with explicit filters:
```go
client.On(telegram.OnMessage, func(m *telegram.NewMessage) error {
    if m.IsPrivate() {
        return m.Reply("Hello from gogram!")
    }
    return nil
})
```

## 3. String Session Handling
- Exporting: `strSession := client.ExportSession()`
- Importing: Load Pyrogram/Telethon compatible session strings directly into `ClientConfig.StringSession`.

## 4. Production Go Concurrency & Error Discipline
1. **Zero Silent Errors**: BANNED: `_ = err`. Always return or handle `if err != nil`.
2. **Context Cancellation**: Pass `context.Context` to all network and database calls.
3. **Goroutine Leak Prevention**: Use bounded worker pools with buffered channels; never spawn unbounded `go func()` on incoming updates.
4. **Zero-RAM Media**: Stream incoming documents directly to disk via `m.Download(&telegram.DownloadOptions{FilePath: "/path/to/disk"})`.
