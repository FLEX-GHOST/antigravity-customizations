---
name: mcp-server-engineering
description: "FastMCP server development, zero-latency caching, stdio isolation, JSON-RPC schema contracts, and headless daemon lifecycle management."
version: 1.0.0
category: mcp
author: Anthropic & Open Source MCP Community
tags: [mcp, fastmcp, json-rpc, stdio, agent-tools, caching, tool-engineering]
---

# FastMCP Server Engineering & Production Tool Development

Build ultra-low latency, memory-efficient Model Context Protocol (MCP) servers with clean protocol isolation.

## 1. Stdio Isolation Contract
- **Stdio Integrity**: Stdio (`stdout` / `stdin`) is reserved EXCLUSIVELY for JSON-RPC messages.
- **Strict Logging Rule**: NEVER use `print()` or write to `sys.stdout`. Route all debug, operational, and error logging to `sys.stderr`.
- **Buffer Unbuffering**: Enforce `PYTHONUNBUFFERED=1` to ensure real-time message flushing.

## 2. Low-Latency Performance Invariants
1. **In-Memory LRU Caching**: Wrap hot search and retrieval endpoints with `@functools.lru_cache(maxsize=1024)` to achieve < 0.01ms lookup times.
2. **Database Optimization**: For SQLite backends:
   - `PRAGMA journal_mode = WAL;`
   - `PRAGMA synchronous = NORMAL;`
   - `PRAGMA cache_size = -131072;` (128MB cache)
   - `PRAGMA mmap_size = 268435456;` (256MB zero-copy memory mapping)
3. **Schema Contracts**: Every tool parameter must declare explicit type annotations (`str`, `int`, `Optional[str]`) and clear semantic docstrings.

## 3. Tool Discovery & Auto-Approval
- Configure client presets (`turbo`, `always_allow`) so authorized tools run autonomously without intrusive approval modals.
