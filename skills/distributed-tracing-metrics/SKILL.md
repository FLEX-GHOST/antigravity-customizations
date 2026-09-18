---
name: distributed-tracing-metrics
description: "Prometheus metrics, OpenTelemetry spans, and healthcheck telemetry for multi-tenant Telegram bot clusters in Rust and Go."
version: 1.0.0
category: metrics-telemetry
author: Site Reliability Engineers
tags: [prometheus, opentelemetry, metrics, grafana, bot-cluster, rust, go]
---

# Distributed Tracing & Prometheus Metrics for Bot Clusters

Monitor latency, update throughput, memory usage, and FloodWait events in real-time across your bot empire.

## 1. Key Metrics to Export
- `telegram_updates_received_total{bot_id, update_type}`: Monotonic counter.
- `telegram_update_processing_duration_seconds`: Histogram with buckets [0.01, 0.05, 0.1, 0.5, 1.0, 5.0].
- `telegram_flood_wait_events_total{bot_id}`: Counter tracking code 420 rate limits.
- `active_voice_chats_gauge`: Number of live WebRTC voice streams.
- `process_resident_memory_bytes`: Physical RAM tracked via Jemalloc statistics.

## 2. Prometheus Endpoint Integration (Axum)
```rust
use metrics_exporter_prometheus::PrometheusBuilder;

let handle = PrometheusBuilder::new().install_recorder()?;
let app = Router::new().route("/metrics", get(move || async move { handle.render() }));
```
