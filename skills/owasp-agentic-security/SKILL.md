---
name: owasp-agentic-security
description: "Master security standards for AI Agent tool execution, prompt injection defense, sandboxing, and parameter sanitization based on OWASP Agentic Top 10."
version: 1.0.0
category: security
author: Google DeepMind & Security Community
tags: [security, owasp, agentic, prompt-injection, sandboxing, input-validation, defense]
---

# OWASP Agentic Security & Tool Sandboxing Master Standard

Strictly enforce defensive security controls when building and running autonomous AI agents and tool-calling systems.

## 1. Threat Model & OWASP Top 10 for Agentic Systems
- **ASI-01: Prompt Injection & Jailbreak Traps**: External user inputs or scraped web payloads attempt to hijack agent directives.
- **ASI-02: Insecure Tool Execution**: Unvalidated tool execution resulting in shell command injection, unauthorized file system access, or arbitrary code execution.
- **ASI-03: Excessive Agency**: Granting agents elevated permissions (root, write access to all tables, blanket API keys) without human-in-the-loop approval.
- **ASI-04: Unchecked Parameter & Slot Tampering**: Malicious inputs manipulating JSON schemas or injecting SSRF targets (e.g. `http://127.0.0.1:6379`).
- **ASI-05: Cross-Agent Memory Poisoning**: Contaminating shared memory stores with poisoned instructions that trigger secondary agent exploits.

## 2. Mandatory Security Invariants
1. **SSRF Defense**: Never allow tool-calling agents to fetch from localhost (`127.0.0.1`, `localhost`, `::1`, `169.254.169.254`, or internal subnets `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
2. **Schema Whitelisting**: Every tool parameter must be strictly typed with JSON Schema. Strip unlisted properties before invoking execution handlers.
3. **Execution Sandboxing**: Shell commands must execute under unprivileged users with strict resource limits (`ulimit`, `cgroups`) and read-only root filesystems.
4. **Output Sanitization**: Sanitize tool outputs before returning them into the LLM context to prevent indirect prompt injection.
5. **Human Approval Threshold**: Any destructive action (deleting databases, sending mass broadcasts, billing charges) requires explicit user confirmation.
