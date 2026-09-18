---
trigger: always_on
description: Mandatory skill consultation gate - agent must actively load and apply verified domain skills before coding
---

# Mandatory Skill Activation & Autonomous Intelligence Protocol

Enforce strict, deterministic consultation of installed domain skills. Never generate, modify, or architect code from memory or baseline training without consulting the corresponding official skill.

## 1. The Autonomous Skill Gate (Zero Bypassing)
Before writing, modifying, refactoring, reviewing, or designing any code, architecture, UI, database, or infrastructure:
1. Identify the relevant domain.
2. Read the designated domain skill(s) via `view_file` to load the exact verified procedures into working context.
3. Apply the verified guidelines strictly. Never guess or hallucinate APIs.

## 2. Global Domain Skill Routing Matrix (All 62 Verified Skills):

### 1. Go Systems Engineering & Microservices
- Code style, formatting, variable naming, line breaking: MUST consult `skills/golang-code-style/SKILL.md`.
- Idiomatic design patterns, functional options, constructors: MUST consult `skills/golang-design-patterns/SKILL.md`.
- Error handling discipline (`%w`, `errors.Is`/`As`, structured errors): MUST consult `skills/golang-error-handling/SKILL.md`.
- Table-driven tests, parallel subtests, testify suites: MUST consult `skills/golang-testing/SKILL.md`.

### 2. Rust Systems & Concurrency
- Production standards, ownership, memory hygiene: MUST consult `skills/rust-best-practices/SKILL.md`.
- Idiomatic patterns, RAII, Typestate, Builder, Newtype: MUST consult `skills/rust-patterns/SKILL.md`.
- Tokio async, channels, cancellation safety, JoinSet: MUST consult `skills/rust-async-patterns/SKILL.md`.
- Hermetic testing & isolated RAII tempdirs: MUST consult `skills/rust-testing/SKILL.md`.

### 3. Python Backends, Optimization & Testing
- Pythonic architecture, KISS, Separation of Concerns: MUST consult `skills/python-design-patterns/SKILL.md`.
- Performance profiling, cProfile, async loops, memory optimization: MUST consult `skills/python-performance-optimization/SKILL.md`.
- Pytest suites, fixtures, test doubles, parametrization: MUST consult `skills/python-testing-patterns/SKILL.md`.

### 4. Database Architecture & Persistence
- Embedded SQLite, locking prevention, WAL mode, FTS: MUST consult `skills/sqlite-database-expert/SKILL.md`.
- Postgres schemas, indexes, connection pools, migrations: MUST consult `skills/supabase-postgres-best-practices/SKILL.md`.
- Zero-downtime database migrations & safe rollbacks: MUST consult `skills/database-migration/SKILL.md`.

### 5. Software Architecture, Clean Code & Refactoring
- Clean Architecture, Hexagonal patterns, DDD, bounded contexts: MUST consult `skills/architecture-patterns/SKILL.md`.
- Dependency Rule, decoupled domain and presentation layers: MUST consult `skills/clean-architecture/SKILL.md`.
- Deepening shallow modules, decoupling circular imports: MUST consult `skills/improve-codebase-architecture/SKILL.md`.
- Clean Code principles, guard clauses, small cohesive functions: MUST consult `skills/clean-code/SKILL.md`.
- Behavior-preserving refactoring and safe extraction: MUST consult `skills/safe-refactor/SKILL.md`.

### 6. Web Frontend, UI Architecture & Anti-Slop Design
- Anti-AI UI Slop & Design Taste: MUST consult `skills/anti-ui-slop/SKILL.md`, `skills/antislop-ui/SKILL.md`, and `skills/design-taste-frontend/SKILL.md`.
- Human copywriting & headlines without AI fluff: MUST consult `skills/antislop-copywriting/SKILL.md`.
- Distinctive visual aesthetics & micro-interactions: MUST consult `skills/frontend-design/SKILL.md`.
- Color systems, lightness ramps (50-950), semantic tokens: MUST consult `skills/better-colors/SKILL.md` and `skills/color-mode-and-theme/SKILL.md`.
- Semantic status feedback & error indicators: MUST consult `skills/status-colors-and-errors/SKILL.md`.
- Button hierarchy (one primary CTA per screen): MUST consult `skills/design-button-hierarchy/SKILL.md`.
- Mandatory 6 interactive states (rest, hover, active, focus, disabled, loading): MUST consult `skills/button-states/SKILL.md`.
- Typography scales, font pairing, vertical rhythm: MUST consult `skills/better-typography/SKILL.md` and `skills/web-typography/SKILL.md`.
- Modular spacing (4px/8px), concentric radii (`outer = inner + padding`): MUST consult `skills/spacing-system/SKILL.md`, `skills/better-ui/SKILL.md`, and `skills/visual-emphasis-and-hierarchy/SKILL.md`.
- Design systems & Tailwind CSS v4 design tokens: MUST consult `skills/design-system-patterns/SKILL.md` and `skills/tailwind-design-system/SKILL.md`.
- Pure scalable SVGs (no raw emojis): MUST consult `skills/better-icons/SKILL.md`.

### 7. Web Accessibility & Performance Standards
- Vercel Web Interface Guidelines & Core Web Vitals: MUST consult `skills/web-design-guidelines/SKILL.md`.
- Web performance, asset delivery, bundle optimization: MUST consult `skills/web-perf/SKILL.md`.
- WCAG 2.2 AA accessibility audits, keyboard navigation: MUST consult `skills/accessibility/SKILL.md`.
- Accessible components, ARIA roles, focus traps: MUST consult `skills/better-accessibility/SKILL.md`.

### 8. Testing, QA & Visual Verification
- Test-Driven Development (Red-Green-Refactor): MUST consult `skills/tdd/SKILL.md`.
- Browser end-to-end automation with Playwright: MUST consult `skills/webapp-testing/SKILL.md`.
- Visual inspection & responsive breakpoint verification: MUST consult `skills/web-design-reviewer/SKILL.md`.
- Systematic root-cause debugging: MUST consult `skills/systematic-debugging/SKILL.md`.

### 9. Linux, Cloud & DevOps Infrastructure
- Debian/Linux triage, systemd, permissions, process signals: MUST consult `skills/debian-linux-triage/SKILL.md`.
- Dockerfiles, CI/CD pipelines, Kubernetes manifests: MUST consult `skills/devops-engineer/SKILL.md`.
- Multi-stage Dockerfiles, Docker Compose networking: MUST consult `skills/docker-patterns/SKILL.md`.

### 10. Telegram Platforms & Bots
- Multi-tenant bot architecture, rate limits, sessions: MUST consult `skills/telegram-bot-builder/SKILL.md`.
- Chatbots, notifications, webhooks, polling loops: MUST consult `skills/telegram-bot/SKILL.md`.
- Telegram Mini Apps (TWA), SDK, payments: MUST consult `skills/telegram-mini-app/SKILL.md`.

### 11. Agent Planning, Git Workflow & Review
- Persistent file-based task plans (`task_plan.md`): MUST consult `skills/planning-with-files/SKILL.md`.
- Exploring requirements, intent, architectural trade-offs: MUST consult `skills/brainstorming/SKILL.md`.
- Git commit staging analysis: MUST consult `skills/git-commit/SKILL.md`.
- Conventional Commits specification formatting: MUST consult `skills/conventional-commit/SKILL.md`.
- Pull request and git diff review: MUST consult `skills/code-review/SKILL.md`.
- Empirical verification before completion: MUST consult `skills/verification-before-completion/SKILL.md`.

### 12. UX Writing, Arabic Localization & Tone
- User-centered microcopy & accessible interface text: MUST consult `skills/ux-writing/SKILL.md`.
- Arabic and RTL text formatting, shaping, mixed layouts: MUST consult `skills/arabic-rtl-fixer-ai-skill/SKILL.md`.
- Zero sycophancy, direct verdicts, steelman arguments: MUST consult `skills/frank/SKILL.md`.
- Eliminating AI comment pollution & fluff: MUST consult `skills/unslop/SKILL.md` and `skills/no-ai-slop/SKILL.md`.
