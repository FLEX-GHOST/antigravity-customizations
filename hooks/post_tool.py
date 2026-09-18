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

    # Output empty json per PostToolUse contract
    sys.stdout.write(json.dumps({}))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
