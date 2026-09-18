# Antigravity Enterprise Customizations & MCP Skills Engine

[![Antigravity Compatible](https://img.shields.io/badge/Antigravity%20IDE-Compatible-success.svg)](https://github.com/FLEX-GHOST/antigravity-customizations)
[![Active Items](https://img.shields.io/badge/Indexed%20Skills%20%26%20Rules-4%2C200%2B-blue.svg)](#)
[![Budget Free](https://img.shields.io/badge/Context%20Budget%20Free-%3E80%25-brightgreen.svg)](#)
[![Governance](https://img.shields.io/badge/Governance-Anti--Slop%20%7C%20Anti--Sycophancy-orange.svg)](#)

Enterprise-grade configuration, sovereign engineering rules, and on-demand MCP skills engine for **Google Antigravity IDE** and agentic coding workflows.

---

## Quick Start: One-Command Installation (التثبيت بأمر واحد)

Run this single command on **any server** (Debian, Ubuntu, Fedora, macOS, etc.) to set up everything automatically:

```bash
curl -fsSL https://raw.githubusercontent.com/FLEX-GHOST/antigravity-customizations/main/install.sh | bash
```

Or via Git:

```bash
git clone https://github.com/FLEX-GHOST/antigravity-customizations.git ~/.gemini/antigravity-customizations
cd ~/.gemini/antigravity-customizations
./install.sh
```

---

## Core Architecture

```
                               +--------------------------------------------+
                               |         Google Antigravity IDE             |
                               +--------------------------------------------+
                                      |                              |
            [Always-On Core Rules: 11.6%]             [On-Demand MCP: 0.7%]
            - anti_ai_design.md                       skills-engine (26 Tools)
            - honest_engineering.md                                  |
            - strict_comment_discipline.md                           v
            - code_integrity.md                       +-----------------------------+
                                                      |  SQLite WAL FTS5 Database   |
                                                      |   4,200+ Skills & Rules     |
                                                      +-----------------------------+
                                                                     |
                                      +------------------------------+------------------------------+
                                      |                              |                              |
                                      v                              v                              v
                           [Anthropic Official]            [Top-Starred Curated]          [Cursor & Slop Rules]
                            - mcp-builder                   - zero-hallucination           - PatrickJS CursorRules
                            - frontend-design               - memory-engineering           - 66 Anti-Slop Gates
                            - webapp-testing                - chaos-engineering            - Universal Stacks
```

---

## Key Capabilities

### 1. 81%+ Free Context Budget (No Prompt Bloat)
- Solves the **"Customization Budget Exceeded"** issue completely.
- Moves large skill collections out of the eager prompt budget into an on-demand MCP index.
- Reduces token footprint from **40.6% (8,121 tokens)** down to **0.7% (132 tokens)** while granting instant access to 4,200+ skills.

### 2. Top-Starred Community & Official Skills
Integrated directly with:
- **`anthropics/skills`**: Official Anthropic production skills (`mcp-builder`, `skill-creator`, `canvas-design`, `webapp-testing`).
- **`alirezarezvani/claude-skills`**: 840+ top-starred engineering, architecture, and reliability skills.
- **`PatrickJS/awesome-cursorrules`**: 257 modern framework and language rules.
- **`ComposioHQ/awesome-claude-skills`**: Multi-platform integration and automation skills.

### 3. Non-Negotiable Governance & Anti-Slop
- **`anti_ai_design`**: Strictly bans generic AI purple/violet gradients, faux glassmorphism, raw emojis in buttons; mandates 6 interactive button states and WCAG 2.2 AA contrast.
- **`honest_engineering`**: Zero sycophancy, zero flattery; leads with blunt technical verdicts and surfaces trade-offs upfront.
- **`strict_comment_discipline`**: Zero echo comments, zero AI meta-narration, zero tutorial padding.
- **`code_integrity`**: Minimal blast radius, surgical modifications, zero breaking changes.

### 4. Zero-Permission Auto-Approval (IDE + CLI)
- Pre-configures `permissionPreset: turbo` and `mcp(*)` / `mcp(skills-engine/*)` allow grants out of the box.
- Eliminates manual permission prompts and interruptions across both Antigravity IDE and `agy` CLI workflows.

### 5. High-Performance Zero-Copy Engine & Dialect NLU
- **Zero-Copy MMAP & LRU Cache**: 256MB memory-mapped zero-copy I/O with in-memory caching (< 0.005ms repeat lookups).
- **Everyday Arabic & Iraqi Dialect Intent NLU**: Native recognition for conversational developer phrasing (`حل مشكلة الازرار`, `الالوان تعبانة زبالة`, `البوت معلك وصافن`, `ياكل رام`, `الكود وصخ نظفه ورتبه`, etc.).
- **Token-Optimized Output**: Automatically filters markdown badge slop (`[![...](...)...`) to save 40%+ token footprint in search results.

---

## 26 Built-in MCP Tools

| Tool | Purpose |
| :--- | :--- |
| `search_agent_capabilities` | Hybrid SQLite FTS5 + BM25 search with Arabic stemming and quality weighting. |
| `get_exact_skill` | 100% verbatim skill retrieval with zero loss or truncation. |
| `get_exact_rule` | 100% verbatim rule retrieval. |
| `get_top_rated_skills` | Filter top-starred skills by category, language, and tier (Score >= 70). |
| `audit_skill_quality` | Programmatic analysis of skill length, structure, examples, and stubs. |
| `get_core_governance_rules` | Instant access to Anti-UI Slop, Honest Engineering, and Strict Comments. |
| `audit_anti_sycophancy` | Automated scanner for servile openers, reflexive folding, and AI buzzwords. |
| `audit_ui_design` | Automated scanner for AI purple gradients, raw emojis, and missing button states. |
| `detect_project_stack` | Universal tech-stack detector (Rust, Go, Python, React, Next.js, Docker, SQLite). |
| `verify_code_rules` | Real-time linter for language-specific invariants. |
| `get_skill_toc` | Returns table of contents for surgical section reading. |
| `get_skill_section` | Reads single specific section, saving 85%+ tokens. |
| `register_custom_directory` | Dynamically indexes any new folder on disk at runtime. |
| `create_new_skill` | Programmatically authors new skills in the catalog. |
| `list_skills_overview` | Paginated catalog view sorted by quality score. |
| `list_rules_overview` | Paginated rules catalog view. |
| `read_skill_resource_file` | Accesses nested skill templates and configuration files. |
| `reload_skills_index` | Forces full re-index across all directories. |

---

## License

MIT License. Designed for Antigravity IDE, Claude Code, Cursor, and agentic workflows.
