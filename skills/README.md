# Antigravity Skills Catalog

Curated, high-performance skills catalog organized alphabetically from `0-9` and `a` through `z` for the Antigravity Autonomous Engine.

## Catalog Architecture

- **Alphabetical Organization**: Skills are partitioned into buckets (`0-9/`, `a/` to `z/`) to optimize browsing speed and repository structure.
- **Autonomous Discovery**: Each skill directory contains a `SKILL.md` specification automatically ingested and indexed by the `skills-engine` MCP server with Full-Text Search (FTS5).
- **Zero Prompt Overhead**: Skills are retrieved on-demand by the assistant via `get_exact_skill` or `search_agent_capabilities`, maintaining zero system prompt token bloat.

## Directory Structure

```
skills/
├── 0-9/
├── a/
├── b/
├── ...
└── z/
```
