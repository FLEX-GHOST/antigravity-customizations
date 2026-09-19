---
name: bash-defensive-scripting
description: Authoritative skill for bulletproof, production-grade shell scripting covering unofficial strict mode, signal trapping, error handling, and cross-platform portability.
language: bash
category: programming-languages
quality_score: 100
tier: official
triggers:
  - bash
  - shell
  - sh
  - zsh
  - scripting
  - posix
  - automation
  - shellcheck
---
# Defensive Bash & POSIX Shell Automation Architecture

Industrial-strength principles for writing reliable, self-healing shell automation scripts.

## 1. Unofficial Strict Mode Mandate
* Every bash script must start with the strict mode safety prelude:
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  IFS=$'
	'
  ```
* **Explanation of Flags**:
  * `-e`: Exit immediately if a command exits with a non-zero status.
  * `-u`: Treat unset variables as an error and exit immediately.
  * `-o pipefail`: The return value of a pipeline is the status of the last command to exit with a non-zero status.

## 2. Resource Cleanup & Signal Trapping
* **Atomic Temp Directories**: Always create temporary workspaces via `mktemp -d` and guarantee their deletion with an `EXIT` trap.
  ```bash
  TEMP_DIR=$(mktemp -d)
  trap 'rm -rf "$TEMP_DIR"' EXIT INT TERM
  ```
* **Quote Every Variable**: Never leave variable expansions unquoted (`"$VARIABLE"`) to prevent globbing and word splitting bugs.
