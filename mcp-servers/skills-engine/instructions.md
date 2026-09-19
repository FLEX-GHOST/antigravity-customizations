# Skills Engine Operating Manual & Tool Decision Matrix

## Server Overview
`skills-engine` is the canonical autonomous software engineering intelligence, capability discovery, structural AST auditing, and bot factory governance server. It exposes 57 enterprise tools across 5 suites (code_intelligence, systems_rust, telegram, governance, and search_catalog).

## Autonomous Calling Protocol

### 1. Project Exploration & Navigation
* **File Architecture**: Call `extract_code_symbols(file_path="...")` to retrieve structural outlines (structs, classes, functions, traits, enums, methods) without reading whole files into the context window.
* **Stack Discovery**: Call `detect_project_stack(directory_path="...")` to discover frameworks, languages, and project topology.
* **Capability Search**: Call `search_agent_capabilities(query="...")` or `discover_tools(intent="...")` to find exact governance guidelines.

### 2. Large-Scale Refactoring & Impact Analysis
* **Blast Radius Analysis**: Call `analyze_blast_radius(symbol_name="...", project_dir="...")` *before* refactoring or changing any public function, struct, or type to identify every downstream caller and import across the repository.
* **Structural Search**: Call `ast_structural_search(pattern="...", search_path="...")` to locate structural patterns (e.g., banned `.unwrap()` calls, unhandled errors, async functions missing await).

### 3. Verification, Compiler Diagnostics & Delivery
* **Compiler-Grade Verification**: Call `run_compiler_diagnostics(target_path="...")` after modifying code to get structured compiler errors (Rust `cargo check`, Go `go vet`, Python syntax/ruff, TypeScript `tsc`).
* **Patch Healing**: Call `verify_and_heal_code_patch(file_path="...", patch_content="...")` to validate syntax and automatically remedy delimiter or style defects in memory.
* **Sandboxed Testing**: Call `execute_sandboxed_snippet(code="...", language="...")` to safely test algorithmic edge cases, regex, or mathematical calculations before embedding them into production code.

### 4. Live API References & Zero Hallucination
* **API Documentation**: Call `fetch_api_reference(library_name="...", language="...")` to fetch live, cached signatures and versions for Rust crates, PyPI packages, NPM modules, and Telegram Bot API.

### 5. Telegram Microservices & Bot Architecture
* **Spec Lookup**: Call `get_telegram_bot_api_spec(query="...")` for authoritative Bot API 9.4+ / 10.3 signatures.
* **Payload Validation**: Call `validate_telegram_payload(method="...", payload_json="...")` to check button styles, byte limits, and required parameters.
* **Pipeline Simulation**: Call `simulate_bot_pipeline(...)` and `simulate_telegram_load(...)` to test concurrency and backoff.
