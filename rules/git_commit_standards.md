---
trigger: model_decision
description: Conventional Commits standard, atomic changes, and clean VCS history
---

# Git Standards & Conventional Commits

Ensure predictable, structured, and parseable version control history.

## 1. Commit Message Structure
- **Format**: Follow the Conventional Commits specification: `<type>(<scope>): <subject>`.
  - Allowed types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`.
  - Example: `feat(auth): add rate limiting to login endpoint`.
- **Imperative Mood**: Write the subject line in the imperative present tense (e.g., "add", "fix", "refactor", never "added" or "fixing").
- **Length Constraint**: Keep the first line under 72 characters.

## 2. Atomic Commits
- **Single Logical Change**: Every commit must represent one atomic, self-contained unit of work. Never bundle unrelated bug fixes, feature additions, or style changes into a single commit.
- **Passing State**: Every commit must leave the repository in a compiling, test-passing state.
