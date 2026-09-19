# Antigravity Enterprise Customizations & Autonomous Skills Engine

[![Antigravity IDE](https://img.shields.io/badge/Google%20Antigravity-IDE%20%7C%20CLI%20%7C%202.0-blue.svg)](https://github.com/FLEX-GHOST/antigravity-customizations)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-10.3%20(185%20Methods%20%7C%20400%20Types)-2CA5E0?logo=telegram&logoColor=white)](https://core.telegram.org/bots/api)
[![Active MCP Tools](https://img.shields.io/badge/MCP%20Tools-61%20Tools-success.svg)](#complete-mcp-tool-suite-61-enterprise-tools)
[![Engine Architecture](https://img.shields.io/badge/Engine-Python%203.10%2B%20%7C%20FastMCP%20Engine-blue.svg)](#fastmcp-zero-dependency-architecture)
[![Indexed Entities](https://img.shields.io/badge/Indexed%20Entities-6%2C650%2B%20(FastMCP%20%26%20SQLite)-orange.svg)](#)
[![Zero-Prompt Policy](https://img.shields.io/badge/Execution%20Policy-Turbo%20%7C%20Always--Proceed-brightgreen.svg)](#quick-start-one-command-installation)
[![Autonomous CI/CD](https://img.shields.io/badge/GitHub%20Actions-Auto--Sync%20Bot-blueviolet.svg)](https://github.com/FLEX-GHOST/antigravity-customizations/actions)
[![CI/CD Test Suite](https://img.shields.io/badge/CI%2FCD-Automated%20Test%20Suite-success.svg)](https://github.com/FLEX-GHOST/antigravity-customizations/actions/workflows/test-mcp-engine.yml)

Enterprise-grade customization framework, sovereign engineering rules, complete Telegram Bot API master specification, and autonomous Model Context Protocol (MCP) skills engine engineered for **Google Antigravity IDE**, **Antigravity CLI (`agy`)**, and agentic AI systems.

---

## Quick Start: One-Command Installation (التثبيت بأمر واحد)

Run this single command on **any Linux server or cloud environment** (Ubuntu, Debian, CentOS, RHEL, Fedora, macOS, etc.) to set up the entire ecosystem automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/FLEX-GHOST/antigravity-customizations/main/install.sh | bash
```

Or via Git:

```bash
git clone https://github.com/FLEX-GHOST/antigravity-customizations.git ~/.gemini/antigravity-customizations
cd ~/.gemini/antigravity-customizations
./install.sh
```

### What This Command Provisions:
1. **Zero-Prompt Permissions**: Configures `permissionPreset: turbo` and `toolExecutionPolicy: always-proceed` across IDE and CLI to permanently eliminate confirmation dialogs.
2. **Core Sovereign Rules**: Deploys anti-slop, honest engineering, strict comments, and memory safety rules to `~/.gemini/config/rules/`.
3. **FastMCP Enterprise Engine**: Deploys the zero-dependency Python FastMCP server, hot-activating all 61 tools, SQLite FTS5 search across 6,361+ indexed skills (4,060+ bundled, including 818 cybersecurity skills), and strict alphabetical prompt caching.
4. **Telegram Bot API 10.3 Master Engine**: Ingests and builds real-time SQLite FTS5 indices for all **185 methods** and **400 types**.
5. **Intelligent Dialect NLU Hook**: Deploys the Pre-Invocation hook with Arabic, Iraqi dialect, and English intent normalization.

---

## System Architecture

```
                               +-------------------------------------------------------+
                               |              Google Antigravity Platform              |
                               |          (Antigravity IDE  /  Antigravity CLI)        |
                               +-------------------------------------------------------+
                                      |                                       |
                   [Pre-Invocation Interceptor]                      [Model Context Protocol]
                   - Arabic & Iraqi Dialect NLU                      skills-engine (FastMCP Python Native, 61 Tools)
                   - Pre-loaded Method Spec                                   |
                   - Zero-Latency Prompt Injection                            v
                                                              +-------------------------------+
                                                              |   SQLite WAL FTS5 Database    |
                                                              |    6,650+ Skills, Rules &     |
                                                              |    185 methods / 400 Types    |
                                                              +-------------------------------+
                                                                              |
                     +--------------------------------+-----------------------+-----------------------+
                     |                                |                                               |
                     v                                v                                               v
        [Telegram Bot API 10.3]             [Sovereign Governance]                          [Curated Repositories]
        - 185 Official Methods              - anti_ai_design.md                             - anthropics/skills
        - 400 Official Types                - honest_engineering.md                         - alirezarezvani/claude-skills
        - Bot API 9.4+ Button Styling       - strict_comment_discipline.md                  - PatrickJS/awesome-cursorrules
        - Rust / Tokio Execution            - code_integrity.md                             - ComposioHQ/awesome-claude-skills
```

---

## Dual Autonomous Update Pipeline (Zero-Server Maintenance)

The repository maintains an automated, self-healing synchronization loop that ensures Telegram Bot API specifications never become stale:

```
 [Telegram Official Releases]
              |
              v (Every 3 Hours)
 [GitHub Actions Bot] ---------------------> [GitHub Repository: main]
 (Runs on GitHub Cloud,                       - Auto-commits updated spec
  Zero Server Overhead)                       - Updates version.json & tables
                                              - Author: github-actions[bot]
                                                             |
                                                             | (Live Detection)
                                                             v
                                              [MCP Autonomous Watcher]
                                              - In-process daemon thread
                                              - Detects remote SHA change
                                              - Runs git pull & SQLite reindex
                                              - Hot-invalidates in-memory cache
```

1. **Cloud Autonomous Updater (`github-actions[bot]`)**:
   - Runs automatically on GitHub Cloud via [`.github/workflows/update-telegram-api.yml`](.github/workflows/update-telegram-api.yml) every 3 hours or on `workflow_dispatch`.
   - Fetches upstream specification changes, regenerates schema models, and pushes directly to `main` as a verified GitHub Contributor.
2. **Local Edge Autonomous Watcher (`server.py`)**:
   - Embedded directly in the MCP server process (`mcp-github-watcher` thread).
   - Monitors repository state via zero-rate-limit git protocol, automatically pulls updates, and refreshes the SQLite FTS5 database in <1 second with **no cron jobs or systemd units required**.

---

## Telegram Bot API 10.3 Master Reference

Full official specification with real-time sub-millisecond retrieval (< 0.2ms):

| Domain | Methods Count | Core Capabilities |
| :--- | :---: | :--- |
| **Messages & Media** | 28 | `sendMessage`, `sendPhoto`, `sendAudio`, `sendVideo`, `sendVoice`, `sendDocument`, `sendPaidMedia`, `sendSticker`, `sendDice`, `sendGame` |
| **Editing & Deletions** | 9 | `editMessageText`, `editMessageCaption`, `editMessageMedia`, `editMessageReplyMarkup`, `deleteMessage`, `deleteMessages` |
| **Chat & Member Governance** | 46 | `banChatMember`, `unbanChatMember`, `restrictChatMember`, `promoteChatMember`, `setChatPermissions`, `createChatInviteLink`, `createChatSubscriptionInviteLink` |
| **Forum & Topic Management** | 13 | `createForumTopic`, `editForumTopic`, `closeForumTopic`, `reopenForumTopic`, `deleteForumTopic`, `unpinAllForumTopicMessages` |
| **Gifts, Stars & Payments** | 21 | `sendGift`, `getAvailableGifts`, `verifyUser`, `verifyChat`, `removeUserVerification`, `getStarTransactions`, `refundStarPayment` |
| **Webhooks & Configuration** | 22 | `getMe`, `setWebhook`, `deleteWebhook`, `getWebhookInfo`, `getUpdates`, `setMyCommands`, `setChatMenuButton`, `setMyDefaultAdministratorRights` |
| **Telegram Business & Misc** | 46 | `getBusinessConnection`, `setBusinessIntro`, `setMessageReaction`, `answerCallbackQuery`, `answerInlineQuery` |

### Bot API 9.4+ Strict Styling Standard
All button constructs adhere strictly to modern Telegram specifications:
- **Button Colors**: Validated `style` property (`primary` | `success` | `danger`).
- **Vector Icons**: Verified `icon_custom_emoji_id` parameters without falling back to monochromatic or emoji-polluted interfaces.
- **Entity Precision**: Numeric strings for private chats; negative `-100` prefixes for channels and supergroups.

---

## Complete MCP Tool Suite (61 Enterprise Tools)

The MCP server exposes 61 deterministic tools, sorted strictly in alphabetical order to maximize LLM prompt caching hit rates (>95%):

### 1. Telegram & Microservice Operations
- `get_telegram_bot_api_spec`: Instant parameter, type, and Rust code retrieval for all 185 methods.
- `diagnose_telegram_error`: Root-cause diagnosis and Rust healing code generator for Telegram API errors (400, 403, 420, 429).
- `explore_telegram_workflow_graph`: Interrelated methods, expected callbacks, and lifecycle transitions mapper.
- `validate_telegram_payload`: Strict offline schema & payload validator for Bot API 10.3 / 9.4+ requests (styling, buttons, limits).
- `sync_telegram_bot_api_upstream`: Fetches, validates, and indexes upstream Telegram specification into SQLite.
- `resolve_bot_service`: Resolves and binds Telegram bot microservice ports and handlers.
- `scaffold_telegram_microservice`: Generates clean, zero-allocation Tokio/Axum Telegram bot templates.
- `simulate_telegram_load`: Simulates high-concurrency webhook traffic and measures latency.
- `simulate_telegram_webhook_update`: Validates end-to-end webhook update payload pipelines.

### 2. Search, Discovery & Retrieval
- `search_agent_capabilities`: Hybrid BM25 + SQLite FTS5 search with Arabic/Iraqi dialect stemming.
- `get_exact_skill`: 100% verbatim skill document retrieval with zero token truncation.
- `get_exact_rule`: Verbatim governance rule retrieval.
- `get_skill_toc`: Generates interactive structural outline for surgical token-efficient reading.
- `get_skill_section`: Surgical section reader (saving 85%+ context window tokens).
- `get_smart_skill_summary`: Algorithmic executive summary of long-form skill guides.
- `get_top_rated_skills`: Filter skills by quality tier (Official, Verified, Community).
- `discover_tools`: Semantic tool discovery for autonomous agentic workflows.

### 3. Governance, Quality & Auditing
- `get_core_governance_rules`: Instant retrieval of foundational anti-slop and engineering rules.
- `audit_anti_sycophancy`: Scans agent code and output for servile openers and ungrounded flattery.
- `audit_ui_design`: Linter for AI-slop purple gradients, missing button states, and contrast failures.
- `audit_web_application_quality`: Comprehensive audit for web applications and Mini Apps.
- `audit_webhook_health`: Analyzes endpoint latency, error rates, and security posture.
- `audit_project_full_governance`: Evaluates complete codebase adherence to master rules.
- `audit_skill_quality`: Programmatic quality scoring (length, structure, examples, stubs).
- `fix_code_rule_violations`: Automatic rule patcher for codebase violations.

### 4. Autonomous Code Intelligence & Compiler Diagnostics
- `extract_code_symbols`: Structural architectural outlines (structs, classes, functions, traits, enums, methods) across 24 programming languages (Rust, Python, Go, TypeScript/JS, C/C++, Java, Kotlin, Swift, C#, PHP, Ruby, Dart, Scala, Elixir, Zig, Haskell, Lua, Shell, SQL, Julia, R) without token bloat.
- `ast_structural_search`: Pattern-based syntax search (finding functions missing error handling, unwrap calls, async without await, unsafe blocks).
- `run_compiler_diagnostics`: Unified diagnostic engine across 24 languages (Rust `cargo check`, Python syntax & ruff, TypeScript `tsc`, Go `go vet`, C/C++, PHP `php -l`, Ruby `ruby -c`, Java, Kotlin, Zig).
- `analyze_blast_radius`: Cross-project dependency and call-graph impact analyzer before refactoring.
- `fetch_api_reference`: Live and cached documentation lookup for packages across Crates.io, PyPI, NPM, Maven Central, NuGet, Packagist, RubyGems, Pub.dev, GoProxy, and Telegram Bot API 10.3.
- `execute_sandboxed_snippet`: Isolated micro-execution runner to safely verify algorithms, regex, and edge cases.

### 4b. 818 Enterprise Cybersecurity & AppSec Skills (MITRE ATT&CK & NIST CSF)
The catalog integrates 818 structured cybersecurity and ethical engineering skills mapped across 6 industry governance frameworks (MITRE ATT&CK, NIST CSF 2.0, MITRE ATLAS, D3FEND, NIST AI RMF, and MITRE F3):
- **Web & API Security**: Assessing JWT implementations, OAuth 2.0 flows, WebSocket channels, SSRF, SQLi, and Cross-Site Scripting.
- **Threat Hunting & SOC Operations**: Splunk SIEM triage, KAPE forensic parsing, IOC pivot hunting, and memory artifact analysis.
- **Cloud & Container Infrastructure**: AWS/Azure threat telemetry, Kubernetes admission control, IAM privilege escalation vectors.
- **AI & RAG Defense**: Indirect prompt injection defense in RAG pipelines (NVIDIA garak, Promptfoo, PyRIT), model inversion safeguards.
- **Zero Trust & Supply Chain**: TPM 2.0 measured-boot attestation, Sigstore SLSA build provenance verification, post-quantum crypto migration.

### 5. Code Integrity & Verification
- `verify_and_heal_code_patch`: Validates unified git diffs before applying to disk.
- `verify_python_ast`: Validates Python code syntax and catches compilation errors.
- `benchmark_search_performance`: Benchmarks SQLite FTS5 latency and query execution plans.
- `simulate_bot_pipeline`: End-to-end behavioral pipeline simulator.

### 6. Workflows, Pinning & Agent Learning
- `activate_tool_suite`: Batch activation of domain-specific tool suites.
- `list_available_suites`: Catalog of pre-configured tool bundles.
- `pin_skill_for_session`: Locks priority skills into session memory.
- `unpin_skill_for_session`: Unlocks pinned skills.
- `plan_agentic_workflow`: Generates structured, multi-phase execution plans.
- `synthesize_and_learn_skill`: Programmatically authors and indexes newly learned skills on the fly.

### 7. Catalog Management & Federation
- `list_all_skills_manifest`: Complete manifest of all 5,400+ indexed skills with metrics.
- `list_all_rules_manifest`: Complete manifest of all governance rules.
- `list_rules_overview`: Paginated rules catalog.
- `register_custom_directory`: Dynamically mounts and indexes arbitrary directories at runtime.
- `register_federated_mcp_server`: Connects external MCP servers into the skills-engine federation.
- `reload_skills_index`: Forces an immediate re-scan and index re-build.
- `read_skill_resource_file`: Reads nested assets, templates, and reference files.
- `explain_ecosystem_map`: Returns topological relationship map of skills, rules, and tools.
- `get_distributed_trace_spans`: Distributed tracing inspection for agent tool calls.
- `get_system_telemetry`: Real-time memory, CPU, and SQLite WAL telemetry.
- `get_mcp_task_status`: Inspects asynchronous background MCP worker states.
- `cancel_mcp_task`: Gracefully terminates background tasks.
- `create_new_skill`: Scaffold builder for compliant new skill directories.
- `detect_project_stack`: Universal language and framework stack detector.

---

## High-Performance Local IPC, Mock Server & Dynamic Scoping

### 1. Sub-Millisecond IPC & Telegram Bot API Mock Server
The engine embeds a local IPC loopback and complete sandbox mock server running concurrently on port `14993` and UNIX domain sockets:
- **HTTP Loopback**: `http://127.0.0.1:14993/api/spec/<method>` and `http://127.0.0.1:14993/api/health`
- **Telegram Bot API Sandbox Mock**: Point any bot client to `http://127.0.0.1:14993` for 100% offline integration testing:
  - `POST /bot<token>/sendMessage` (records messages, returns Telegram Bot API JSON)
  - `POST /bot<token>/editMessageText` (in-memory state update)
  - `POST /bot<token>/deleteMessage`
  - `GET /bot<token>/getMe` (returns mock bot profile)
  - `GET /mock/messages` (inspect recorded messages during test suites)
  - `POST /mock/reset` (clears sandbox state)
- **UNIX Domain Socket**: `/tmp/skills-engine.sock` (IPC stream for zero-network-stack lookups)

### 2. Progressive Tool Scoping (Token Optimization)
To save 75%+ prompt tokens in context-constrained environments, enable dynamic tool scoping:
```bash
export MCP_DYNAMIC_SCOPING=1
```
When enabled, only 9 core discovery & validation tools are exposed initially. Specialised tool suites (`telegram`, `governance`, `systems_rust`, `agentic_memory`, `search_catalog`, or `all`) are dynamically injected when activated via `activate_tool_suite("<suite>")`.

---

## FastMCP Zero-Dependency Architecture

The `skills-engine` MCP server is built as a self-contained, pure Python 3 service with **zero external pip dependencies**:
- **Zero-Dependency Core**: Built entirely on Python standard libraries (`sqlite3`, `json`, `pathlib`, `hashlib`, `concurrent.futures`), requiring no `pip install` or compiler toolchain.
- **Instant Deployment**: Universal `install.sh` executes in under 3 seconds across any Linux or macOS environment without downloading compilers or build tools.
- **Full FTS5 Search & Caching**: SQLite Full-Text Search (FTS5) index over **5,400+ indexed skills** (4,060+ bundled, including 818 cybersecurity skills) and **870+ sovereign rules** with in-memory LRU caching (<0.1ms).
- **Telegram Bot API 10.3 Specification**: Complete built-in catalog for all 185 methods and 400 types with production Rust payload generation and Arabic dialect NLU.

---

## Sovereign Engineering Rules

The repository strictly enforces four non-negotiable governance pillars across all code generation:

1. **Anti-AI UI Slop & Color Discipline (`anti_ai_design.md`)**:
   - Banned: Purple/violet gradients (`#7c3aed`), glowing blur blobs, centered floating cards, raw emojis in buttons.
   - Mandated: 6 interactive button states (`rest`, `hover`, `active`, `focus-visible`, `disabled`, `loading`), WCAG 2.2 AA contrast, and disciplined lightness ramps.
2. **Honest Engineering & Zero Sycophancy (`honest_engineering.md`)**:
   - Banned: Servile flattery ("Great question", "You are absolutely right", Arabic conversational pleasantries like "من عيوني" or "تدلل").
   - Mandated: Direct conclusions at the top, clear trade-off surfacing, and zero reflexive folding.
3. **Strict Comment Discipline (`strict_comment_discipline.md`)**:
   - Banned: Echo comments, AI narration (`// Added by AI`), tutorial lectures, and lazy placeholders (`// TODO: ...`).
   - Mandated: Self-documenting code; comments reserved strictly for "Why, Not What" and complex memory invariants.
4. **Rust Production Systems Engineering (`rust_standards.md`)**:
   - Zero runtime panics (`.unwrap()` and `.expect()` banned in production handlers).
   - Zero persistent heap waste (Zero-RAM idle, memory-mapped I/O, `tikv-jemallocator`).
   - Tokio concurrency safety (no sync mutex guards held across `.await`, cancellation-safe select blocks).

---

## License

Distributed under the **MIT License**. Engineered for enterprise-grade autonomous development in Google Antigravity, Claude Code, and Cursor.

