---
trigger: model_decision
description: Project structure, layer separation, no circular dependencies, and anti-spaghetti architecture
---

# Project Structure & Architecture Standards

Enforce disciplined codebase organization, clean layer separation, and zero circular coupling.

## 1. Architectural Layering (Inward Dependency Rule)
- **Ingress / Presentation Layer**: API routes, HTTP controllers, CLI commands, and UI components live at the edge. They must never contain raw database queries or core domain algorithms.
- **Domain / Core Business Logic**: Pure, deterministic domain models, use cases, and business validations. Core domain code must be framework-agnostic and must NEVER import from controllers, UI components, or specific DB drivers.
- **Infrastructure Layer**: Database connectors, external API clients, message brokers, and filesystem drivers. Infrastructure implements domain abstractions/interfaces, never the reverse.

## 2. Cohesion & File Organization
- **Feature-First Organization (Vertical Slicing)**: When a codebase grows beyond a few files, group by domain feature (e.g., `modules/auth/`, `features/billing/`) containing its handler, service, and types together, rather than global dumping grounds.
- **No Monolithic Dumping Grounds**: Never dump unrelated helpers into a generic 1,000-line `utils.ts` or `helpers.py`. Organize utilities by cohesive domain (e.g., `crypto/`, `date_formatting/`).
- **No Circular Dependencies**: Strictly forbid bidirectional or circular module imports (e.g., Module A imports B, and B imports A). Extract shared contracts to an independent layer.

## 3. Anti-Overengineering (Deep Modules)
- **No Speculative Skeleton Folders**: Do not generate 10 empty folders or single-line pass-through abstractions for simple tasks. Start simple and extract boundaries only when complexity warrants it.
- **Single Source of Truth for Configuration**: Centralize environment variable loading and application settings in a dedicated `config` module. Never scatter raw `process.env` or hardcoded URLs across component files.
