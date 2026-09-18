---
trigger: always_on
description: Strict comment discipline, zero AI commentary, banning obvious echo comments, tutorial steps, and AI meta-narration
---

# Strict Comment Discipline & Zero AI Pollution

Enforce production-grade code cleanliness. Eliminate patronizing AI commentary, narration, and obvious code echoes.

## 1. Strictly Prohibited Comment Patterns
- **NO Echo Comments**: Never rephrase what the code already says (e.g., `// set status to active`, `// return user data`, `// check if id exists`). Code must be self-documenting.
- **NO AI Meta-Narration**: Never narrate your actions, edits, or authorship (e.g., `// Added by AI`, `// Modified to fix bug`, `// Start of new code`, `// End of changes`, `// Here we handle...`).
- **NO Step-by-Step Tutorial Comments**: Do not treat production code like a classroom lecture (e.g., `// Step 1: Initialize`, `// Step 2: Fetch`, `// Step 3: Transform`).
- **NO Syntax/Framework Explanations**: Never explain basic language features or standard library APIs (e.g., `// useEffect hook to run on mount`, `// using map to loop over items`, `// async function returning promise`).
- **NO Lazy Placeholders or Elisions**: Never emit `// ... existing code ...`, `// TODO: implement your logic here`, or `// Rest of the code remains the same`. Write complete, working code.
- **NO ASCII Dividers & Banners**: Never insert decorative fluff (e.g., `// =====================`, `// ********** HELPERS **********`).

## 2. When Comments Are Allowed (Strict Exceptions)
- **"Why, Not What"**: Only document non-obvious business rules, complex algorithms, or workarounds for third-party bugs (e.g., `// Workaround for Safari WebKit issue #48123`).
- **Safety & Invariants**: Document required memory safety invariants (e.g., Rust `// SAFETY: ...`).
- **Public API Documentation**: Formal docstrings (JSDoc, Rustdoc, Python docstrings) on exported public interfaces only when mandated by project standards.
- **Explicit User Request**: Add explanatory comments only when explicitly asked by the user.
