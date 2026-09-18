---
name: rusttgcalls
description: "Master guide for pure Rust Telegram VoIP and Group Calls (rusttgcalls): WebRTC, Opus RTP loop, DTLS handshake, zero-RAM pipes, and multi-chat streaming."
version: 1.0.0
category: rust-telegram-voip
author: Senior Rust VoIP Engineers
tags: [rusttgcalls, rust, webrtc, voip, rtp, opus, telegram-group-call, audio-streaming]
---

# Rusttgcalls Pure Rust Telegram VoIP Master Engineering Guide

High-throughput, memory-efficient WebRTC group call and voice chat streaming engine in pure Rust (`FLEX-GHOST/rusttgcalls`).

## 1. Core WebRTC Pipeline Architecture
- **Protocol**: WebRTC RTP / RTCP over UDP with DTLS-SRTP encryption.
- **Audio Frame Rate**: 50 packets per second (1 packet every 20ms).
- **Opus Frame Size**: 960 samples per channel at 48kHz.
- **Clock Rate**: 48,000 Hz. Timestamp increment per packet = 960.

## 2. Audio Streaming Loop with Tokio
```rust
use tokio::time::{interval, Duration};

pub async fn stream_pcm_to_voip(
    mut pcm_stream: impl tokio::io::AsyncRead + Unpin,
    mut rtp_sender: RtpSender,
) -> anyhow::Result<()> {
    let mut ticker = interval(Duration::from_millis(20));
    let mut pcm_buf = [0u8; 3840]; // 960 * 2 channels * 2 bytes (16-bit)
    let mut seq: u16 = 0;
    let mut timestamp: u32 = 0;

    loop {
        ticker.tick().await;
        let n = tokio::io::AsyncReadExt::read_exact(&mut pcm_stream, &mut pcm_buf).await;
        if n.is_err() {
            break; // Stream finished
        }

        let opus_frame = encode_opus(&pcm_buf)?;
        rtp_sender.send_rtp_packet(seq, timestamp, &opus_frame).await?;

        seq = seq.wrapping_add(1);
        timestamp = timestamp.wrapping_add(960);
    }
    Ok(())
}
```

## 3. Production Invariants & Memory Policy
1. **Zero-RAM Idle (`anti-raw-bytes-ram`)**: Never load raw media bytes into `Vec<u8>` in RAM. Stream directly from FFmpeg stdout child pipes into the RTP encoder.
2. **Cancellation Safety (`async-cancel-safety`)**: Coordinate voice chat departure using `tokio_util::sync::CancellationToken` to ensure DTLS session closure and clean RTCP Bye packets.
3. **Lock Hierarchy**: Maintain lock hierarchy: Level 1 (Chat Lock) -> Level 2 (Stream Lock). Never acquire locks across `.await` points.
