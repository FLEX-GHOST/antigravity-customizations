---
trigger: model_decision
description: Resilience, explicit I/O timeouts, safe database migrations, and anti-N+1 query prevention
---

# Resilience & I/O Safety Rules

Ensure distributed reliability, resource protection, and database integrity.

## 1. Bounded I/O Operations
- **Mandatory Timeouts**: Every network call, socket connection, database query, and external process invocation must specify an explicit timeout. Never allow operations to block or wait indefinitely.
- **Graceful Degradation**: When non-critical external dependencies fail or timeout, degrade gracefully with sensible fallbacks or cached state rather than crashing the entire service.

## 2. Database & Data Integrity
- **Safe Migrations (Expand & Contract)**: Never drop columns, rename fields, or change data types destructively in a single migration. Always follow multi-phase backward-compatible rollout: add new -> write to both -> backfill -> read from new -> remove old.
- **Anti-N+1 Query Prevention**: Always batch queries or use eager loading (joins / preloading) when retrieving relational data. Never issue queries inside loops.
