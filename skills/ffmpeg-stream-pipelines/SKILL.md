---
name: ffmpeg-stream-pipelines
description: "Zero-RAM FFmpeg pipelines, stream piping, hardware transcoding, and process lifecycle management without zombie leaks."
version: 1.0.0
category: media-engineering
author: Media Streaming Infrastructure
tags: [ffmpeg, transcoding, streaming, hardware-acceleration, pipes, zero-ram]
---

# Zero-RAM FFmpeg Stream Pipelines & Hardware Transcoding

Deploy memory-efficient, hardware-accelerated FFmpeg pipelines for audio and video extraction and streaming.

## 1. Zero-RAM Pipe Streaming
- **Standard Audio Demuxing (Telegram Voice Chat)**:
  ```bash
  ffmpeg -re -i input.mp4 -vn -f s16le -ac 2 -ar 48000 -acodec pcm_s16le pipe:1
  ```
- **Live Stream Input (HLS / RTMP)**:
  ```bash
  ffmpeg -re -i "https://stream.url/live.m3u8" -vn -f s16le -ac 2 -ar 48000 -loglevel error pipe:1
  ```

## 2. Hardware Acceleration
- **VAAPI (Linux / Intel / AMD)**:
  ```bash
  ffmpeg -vaapi_device /dev/dri/renderD128 -i input.mp4 -vf 'format=nv12,hwupload' -c:v h264_vaapi output.mp4
  ```
- **NVENC (NVIDIA)**:
  ```bash
  ffmpeg -hwaccel cuda -i input.mp4 -c:v h264_nvenc -preset p4 -b:v 5M output.mp4
  ```

## 3. Process Lifecycle & Zombie Prevention
1. **Non-Blocking Pipes**: Read from `stdout` asynchronously using Tokio (`tokio::process::ChildStdout`) or Go reader routines.
2. **Graceful Termination**: Send `SIGTERM` first; wait 500ms; escalate to `SIGKILL` if process does not exit.
3. **Zombie Reaping**: Always call `.wait().await` or `cmd.Wait()` to reclaim process descriptors.
