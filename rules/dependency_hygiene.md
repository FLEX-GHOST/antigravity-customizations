---
trigger: always_on
description: Dependency hygiene, minimal external dependencies, lockfile integrity, and standard library priority
---

# Dependency & Supply Chain Hygiene Rules

Minimize external dependency footprint and protect project reproducibility.

## 1. Dependency Minimalism
- **Standard Library First**: Prioritize the programming language's standard library and existing dependencies. Never install a third-party package for utility functions achievable in <= 10 lines of standard code (e.g., string padding, simple date math, basic deep clone).
- **Audit Value vs Weight**: Before introducing any new external dependency, verify that its functionality cannot be cleanly implemented natively, and ensure it does not bring an unbounded tree of transitive dependencies.

## 2. Lockfile & Version Integrity
- **No Unprompted Major Bumps**: Never upgrade major dependency versions or alter locked versions unless explicitly instructed by the user or strictly necessary to fix a breaking bug.
- **Preserve Lockfiles**: Keep lockfiles (`Cargo.lock`, `package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`) consistent and check them into version control.
