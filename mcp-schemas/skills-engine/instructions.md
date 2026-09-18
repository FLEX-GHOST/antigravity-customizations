# Skills Engine Operating Manual & Tool Decision Matrix

## Server Overview
`skills-engine` is the canonical capability discovery, structural AST auditing, and bot factory governance server. It exposes 32 tools, 4 resources, and 3 parameterized prompts.

## Autonomous Calling Protocol
1. **At Task Start**:
   - Call `discover_tools(intent="...")` or `search_agent_capabilities(query="...")` to retrieve blueprints and guidelines.
   - Call `detect_project_stack(directory_path="...")` to discover frameworks and apply required rules.
2. **Before Code Delivery**:
   - Python: Call `verify_python_ast(code="...")` to detect silent error suppression.
   - Rust/Go/Polyglot: Call `fix_code_rule_violations(code_content="...", language="...")` to detect concurrency and memory hazards.
3. **For Telegram Bots**:
   - `resolve_bot_service`: Resolve user query to bot microservice.
   - `simulate_bot_pipeline`: Verify intent parsing and routing.
   - `simulate_telegram_load`: Model high-concurrency floodwait backoff.
4. **Telemetry**:
   - Call `get_system_telemetry()` or read resource `system://metrics/realtime` to verify operational latency.
