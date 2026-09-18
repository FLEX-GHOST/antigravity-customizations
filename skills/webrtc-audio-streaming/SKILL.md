---
name: webrtc-audio-streaming
description: "Real-time WebRTC audio streaming, Opus frame packetization, jitter buffering, and RTP transmission for Telegram group calls and voice chats."
version: 1.0.0
category: media-streaming
author: High-Performance Media Systems
tags: [webrtc, audio, opus, rtp, streaming, telegram-voice-chat, rusttgcalls, gotgcall]
---

# WebRTC Real-Time Audio Streaming & Opus Pipeline Standards

Build high-throughput, low-latency audio streaming engines for Telegram voice chats (group calls) using pure Rust (`rusttgcalls`) and Go (`gotgcall`).

## 1. Technical Audio Parameters
- **Audio Codec**: Opus (RFC 6716).
- **Sampling Rate**: 48,000 Hz (48 kHz).
- **Channels**: 2 (Stereo) or 1 (Mono) depending on group call capabilities.
- **Frame Duration**: 20 milliseconds (ms).
- **Samples per Frame**: 960 samples per channel (48,000 * 0.02 = 960).
- **PCM Format**: 16-bit Signed Linear PCM (s16le), Little-Endian.

## 2. Zero-Latency Pipeline Architecture
1. **Source Demuxing**: Stream audio from disk or pipe directly into FFmpeg (`-f s16le -ac 2 -ar 48000`).
2. **Opus Encoding**: Pass 960 PCM samples to `libopus` encoder. Set bitrate dynamically (e.g., 64 kbps to 128 kbps).
3. **RTP Packetization**: Wrap encoded Opus frames into RTP packets:
   - Increment sequence number by 1 per packet (wraps at 65535).
   - Increment timestamp by 960 per packet.
   - Set Payload Type to dynamic (typically 111 for Opus).
   - Set SSRC matching the Telegram Group Call participant SSRC.
4. **Jitter Buffer & Packet Loss Concealment (PLC)**:
   - Handle out-of-order and dropped packets using circular packet buffers.
   - Invoke `opus_decode` with `NULL` data to generate concealment frames when packets are lost.
5. **Zero-RAM Idle Rule**: Never store raw audio chunks in in-memory queues; stream from disk pipes to keep memory footprint < 10MB idle.
