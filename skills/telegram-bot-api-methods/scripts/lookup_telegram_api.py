#!/usr/bin/env python3
import json
import sys
import os
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "references" / "api_methods.json"
TYPES_PATH = Path(__file__).parent.parent / "references" / "api_types.json"

def lookup(target: str):
    if not DATA_PATH.exists():
        print(f"Error: {DATA_PATH} not found.")
        sys.exit(1)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        methods = json.load(f)

    with open(TYPES_PATH, "r", encoding="utf-8") as f:
        types = json.load(f)

    # Check methods
    match_m = [m for m in methods if m.lower() == target.lower()]
    if match_m:
        m_name = match_m[0]
        m = methods[m_name]
        print(f"### Method: {m_name}")
        desc = m.get("description", [])
        print("".join(desc) if isinstance(desc, list) else desc)
        print(f"\n**Returns**: `{m.get('returns')}`")
        print("\n#### Parameters:")
        fields = m.get("fields", [])
        if not fields:
            print("*No parameters required.*")
        else:
            print("| Parameter | Type | Required | Description |")
            print("| :--- | :---: | :---: | :--- |")
            for f in fields:
                req = "Yes" if f.get("required") else "No"
                f_desc = "".join(f.get("description", [])) if isinstance(f.get("description"), list) else f.get("description", "")
                f_type = ", ".join(f.get("types", [])) if isinstance(f.get("types"), list) else f.get("types", "")
                print(f"| `{f.get('name')}` | `{f_type}` | {req} | {f_desc} |")
        return

    # Check types
    match_t = [t for t in types if t.lower() == target.lower()]
    if match_t:
        t_name = match_t[0]
        t = types[t_name]
        print(f"### Type: {t_name}")
        desc = t.get("description", [])
        print("".join(desc) if isinstance(desc, list) else desc)
        print("\n#### Fields:")
        fields = t.get("fields", [])
        if not fields:
            print("*No fields.*")
        else:
            print("| Field | Type | Required | Description |")
            print("| :--- | :---: | :---: | :--- |")
            for f in fields:
                req = "Yes" if f.get("required") else "No"
                f_desc = "".join(f.get("description", [])) if isinstance(f.get("description"), list) else f.get("description", "")
                f_type = ", ".join(f.get("types", [])) if isinstance(f.get("types"), list) else f.get("types", "")
                print(f"| `{f.get('name')}` | `{f_type}` | {req} | {f_desc} |")
        return

    # Partial search
    candidates_m = [m for m in methods if target.lower() in m.lower()]
    candidates_t = [t for t in types if target.lower() in t.lower()]
    print(f"No exact match for '{target}'.")
    if candidates_m:
        print(f"Similar Methods: {', '.join(candidates_m[:10])}")
    if candidates_t:
        print(f"Similar Types: {', '.join(candidates_t[:10])}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 lookup_telegram_api.py <method_or_type_name>")
        sys.exit(0)
    lookup(sys.argv[1])
