---
name: shazam-audio-fingerprinting
description: "Audio landmark extraction, peak constellation hashing, spectrogram analysis, and Shazam track recognition in Rust (songrec-lib, shazam)."
version: 1.0.0
category: audio-recognition
author: Audio DSP Systems Engineers
tags: [shazam, audio-fingerprint, spectrogram, songrec, rust, dsp, audio-recognition]
---

# Shazam Audio Fingerprinting & Song Recognition Architecture

Build low-latency, memory-efficient song identification bots in pure Rust using `songrec-lib` and Shazam protocols (`/root/bots/shazam`).

## 1. DSP Fingerprinting Pipeline
```
[Raw Audio Sample] ──> [FFmpeg Demux: 16kHz Mono PCM] ──> [STFT Spectrogram]
                             │
                             ▼
                 [Peak Constellation Extraction]
                             │
                             ▼
                 [Landmark Frequency Pair Hashing] ──> [Shazam API Signature]
```

## 2. Rust Performance Standards
1. **Downmixing**: Convert input media to 16,000 Hz, 1 channel (Mono), 16-bit signed PCM.
2. **Buffer Bounds**: Sample duration must be 4 to 8 seconds max. Longer clips waste CPU and network bandwidth without improving recognition accuracy.
3. **Zero-RAM Disk Pipes**: Stream audio from Telegram voice messages directly to disk; never accumulate raw PCM in memory.
