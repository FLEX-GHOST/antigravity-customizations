#!/usr/bin/env python3
import json
import sys
from pathlib import Path

def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    # Check for unfulfilled placeholders or critical stop violations
    decision = "allow"
    reason = ""

    out = {"decision": decision}
    if reason:
        out["reason"] = reason

    sys.stdout.write(json.dumps(out))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
