# Autonomous Skills Engine & Capability Integration Rules

Mandate continuous, autonomous utilization of the `skills-engine` Model Context Protocol (MCP) server as the canonical intelligence, capability discovery, and governance core for all programming tasks.

## 1. Mandatory Pre-Execution Capability Discovery
- **Autonomous Tool & Pattern Lookup**: Before implementing features, planning architectures, or writing non-trivial code, the agent MUST query `skills-engine` via `call_mcp_tool` with `discover_tools` or `search_agent_capabilities`.
- **Zero Hallucinated Standards**: Never guess Telegram Bot API 9.4 button schemas, FloodWait backoff algorithms, jemalloc allocator policies, or Axum webhook structures. Always retrieve verified blueprints from `skills-engine`.
- **Stack & Governance Enforcement**: Upon entering any workspace or repository, invoke `detect_project_stack` to determine programming languages, framework ecosystems, and automatically enforce the applicable governance rules.

## 2. Structural AST Verification Before Delivery
- **Zero Silent Errors**: For all Python code modifications, run `verify_python_ast` to detect silent exception suppression (`except: pass`), mutable default arguments, and raw SQL injection risks.
- **Master Rule Auditing**: For Rust, Go, or general systems code, invoke `fix_code_rule_violations` to detect `MutexGuard` across await points, unbounded channels, direct memory byte caches, and naked production `.unwrap()` calls.

## 3. Autonomous Decision Making & Quality Auditing
- **Proactive Execution**: Do NOT ask the user for permission to query `skills-engine` tools. Invoke them autonomously as standard operating procedure.
- **Adversarial Integrity**: Use `audit_anti_sycophancy` to verify that technical trade-offs are surfaced honestly and that responses contain zero sycophantic fluff or colloquial flattery.
- **Anti-AI Slop Enforcement**: For frontend web components or CSS, invoke `audit_ui_design` to ensure strict adherence to color ramps, interactive button state coverage, and clean typography.
