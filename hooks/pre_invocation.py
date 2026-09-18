#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def main():
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
    except Exception:
        payload = {}

    workspaces = payload.get("workspacePaths", [])
    ws = Path(workspaces[0]) if workspaces else Path("/root/bots/factory")
    stack_items = []

    if (ws / "Cargo.toml").exists():
        stack_items.append("Rust (Telegram Factory Core)")
    if (ws / "package.json").exists():
        stack_items.append("Node.js/React (Frontend)")
    if (ws / "go.mod").exists():
        stack_items.append("Go (Microservices)")
    if (ws / "pyproject.toml").exists() or (ws / "requirements.txt").exists():
        stack_items.append("Python (Daemon/AI)")

    stack_desc = ", ".join(stack_items) if stack_items else "General Polyglot"
    msg = (
        f"⚡ [skills-engine Active] Workspace Stack: {stack_desc}. "
        "Governance rules and 33 MCP tools loaded. "
        "Autonomous protocol: Use discover_tools / AST checkers before reporting completion."
    )

    out = {
        "injectSteps": [
            {
                "ephemeralMessage": msg
            }
        ]
    }
    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
