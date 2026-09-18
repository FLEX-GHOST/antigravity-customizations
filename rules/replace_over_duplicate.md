# Strict In-Place Modification & Anti-Duplication Rule

## Core Principle: Replace Existing Code, Never Duplicate or Append Redundant Logic

1. **Locate Canonical Implementation First**:
   - Before adding any new function, handler, state check, or callback processor, thoroughly search the codebase to identify where that logic is already handled.
   - Never append a new/duplicate function or helper at the bottom of a file when the logic already exists in the file.

2. **In-Place Modification (Surgical Replacement)**:
   - Always edit and update the existing canonical implementation directly in place.
   - Never create parallel handlers, duplicate matching branches, or shadow dispatcher functions.

3. **Single Source of Truth**:
   - Every domain action (e.g. pending input states, rank permissions, callback queries, bot settings) must have exactly one authoritative execution path.
   - If a flow needs enhancement or bug fixing, replace the flawed lines in the existing function rather than introducing a second handler.

4. **Zero Dead Code & Shadow Handlers**:
   - Never leave dead, uncalled, or shadowed code paths.
   - Any modification must maintain clean architecture, minimum blast radius, and zero code duplication.
