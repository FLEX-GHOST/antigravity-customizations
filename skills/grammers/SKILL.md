---
name: grammers
description: "Master guide for pure Rust Telegram MTProto client (grammers-client, grammers-session, grammers-tl-types, grammers-mtsender): connection, auth, update loops, and raw TL calls."
version: 1.0.0
category: rust-telegram
author: Senior Rust Systems Engineers
tags: [grammers, rust, mtproto, telegram, tl-types, userbot, session, tokio]
---

# Grammers Pure Rust MTProto Client Master Engineering Standards

Production-grade MTProto client systems in pure Rust using `grammers-client` (0.10+).

## 1. Connection & Session Initialization
```rust
use grammers_client::{Client, Config, InitParams, Update};
use grammers_session::Session;
use std::sync::Arc;

pub async fn init_grammers_client(session_path: &str, api_id: i32, api_hash: &str) -> anyhow::Result<Client> {
    let session = Session::load_file_or_create(session_path)?;
    let client = Client::connect(Config {
        session,
        api_id,
        api_hash: api_hash.to_string(),
        params: InitParams {
            catch_up: true,
            ..Default::default()
        },
    }).await?;

    Ok(client)
}
```

## 2. Update Processing Loop
Run the update loop inside a dedicated Tokio task supervised by a JoinSet:
```rust
pub async fn run_update_listener(client: Client) -> anyhow::Result<()> {
    while let Some(update) = client.next_update().await? {
        match update {
            Update::NewMessage(message) => {
                if message.outgoing() {
                    continue;
                }
                let text = message.text();
                let chat = message.chat();
                // Handle message concurrently without blocking update loop
                tokio::spawn(handle_message(client.clone(), chat, text.to_string()));
            }
            Update::CallbackQuery(cb) => {
                tokio::spawn(handle_callback(client.clone(), cb));
            }
            _ => {}
        }
    }
    Ok(())
}
```

## 3. Raw TL Function Invocations
When calling MTProto methods not wrapped by high-level abstractions:
```rust
use grammers_tl_types as tl;

// Example: Resolving a username
let resolved = client.invoke(&tl::functions::contacts::ResolveUsername {
    username: "username".to_string(),
}).await?;
```

## 4. Production Rust Invariants (Zero-Panic)
1. **No Panics (`err-no-unwrap-prod`)**: Never call `.unwrap()` or `.expect()` inside update handlers. Propagate with `?` or handle gracefully.
2. **Lock Discipline (`async-no-lock-await`)**: Never hold sync `parking_lot::MutexGuard` across `client.invoke().await`.
3. **FloodWait Handling**: Intercept `grammers_client::client::errors::InvocationError::Rpc(rpc_err)` with code 420; sleep with jitter before retrying.
4. **Disk Streaming (`anti-raw-bytes-ram`)**: Download media with `client.download_media(&media, &mut tokio::fs::File::create(path).await?)`.
