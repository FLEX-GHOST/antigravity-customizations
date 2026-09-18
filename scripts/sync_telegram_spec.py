#!/usr/bin/env python3
"""
Automated Telegram Bot API Specification Synchronizer
Fetches the latest official Bot API specification, updates skills, references,
embedded Go data, re-compiles multi-arch binaries, and dynamically updates README badges,
metrics, and version counts using scripts/update_readme_metrics.py.
"""
import urllib.request
import json
import os
import sys
import shutil
import re
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT_DIR / "skills" / "telegram-bot-api-methods"
MCP_DIR = ROOT_DIR / "mcp-servers" / "skills-engine"
SCRIPTS_DIR = ROOT_DIR / "scripts"
SPEC_URL = "https://raw.githubusercontent.com/PaulSonOfLars/telegram-bot-api-spec/main/api.json"

sys.path.insert(0, str(SCRIPTS_DIR))
import update_readme_metrics

def fetch_and_sync(force: bool = False):
    print(f"[*] Fetching latest Telegram Bot API specification from: {SPEC_URL}")
    req = urllib.request.Request(SPEC_URL, headers={"User-Agent": "Antigravity-BotAPI-Sync/2.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        new_data = json.loads(resp.read().decode("utf-8"))

    new_version = new_data.get("version", "Unknown")
    new_methods = new_data.get("methods", {})
    new_types = new_data.get("types", {})
    new_release_date = new_data.get("release_date", "Unknown")

    clean_ver = new_version.replace("Bot API", "").replace("Telegram", "").strip()

    refs_dir = SKILL_DIR / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)
    methods_file = refs_dir / "api_methods.json"
    types_file = refs_dir / "api_types.json"
    version_file = refs_dir / "version.json"

    current_version = ""
    if version_file.exists() and not force:
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                current_version = json.load(f).get("version", "")
        except Exception:
            pass

    if current_version == clean_ver and not force:
        print(f"[✓] Telegram Bot API is already up-to-date ({clean_ver}). Verifying README metrics...")
        update_readme_metrics.update_readme()
        return False, clean_ver, len(new_methods), len(new_types)

    print(f"[*] Updating from {current_version or 'initial'} -> {clean_ver} ({len(new_methods)} methods, {len(new_types)} types)")

    # 1. Save raw JSON references in skill directory
    with open(methods_file, "w", encoding="utf-8") as f:
        json.dump(new_methods, f, indent=2, ensure_ascii=False)

    with open(types_file, "w", encoding="utf-8") as f:
        json.dump(new_types, f, indent=2, ensure_ascii=False)

    version_data = {
        "version": clean_ver,
        "release_date": new_release_date,
        "total_methods": len(new_methods),
        "total_types": len(new_types),
        "updated_at": os.popen("date -u +'%Y-%m-%dT%H:%M:%SZ'").read().strip()
    }
    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(version_data, f, indent=2)

    # 2. Re-generate methods markdown table
    table_lines = [
        f"# Telegram Bot API Complete Methods Reference ({clean_ver})",
        "",
        f"**Official Specification Version**: `{clean_ver}` ({new_release_date})",
        f"**Total Official Methods**: `{len(new_methods)}` | **Total Types**: `{len(new_types)}`",
        "",
        "| # | Method Name | Return Type | Required Parameters | Summary |",
        "| :-: | :--- | :--- | :--- | :--- |"
    ]

    for idx, (m_name, m_info) in enumerate(sorted(new_methods.items()), 1):
        ret = m_info.get("returns", ["None"])
        ret_str = ", ".join(ret) if isinstance(ret, list) else str(ret)
        fields = m_info.get("fields", [])
        req_fields = [f.get("name") for f in fields if f.get("required") is True]
        req_str = ", ".join(req_fields) if req_fields else "*None*"
        desc = "".join(m_info.get("description", [])) if isinstance(m_info.get("description"), list) else m_info.get("description", "")
        clean_desc = desc.replace("\n", " ").strip()[:90] + ("..." if len(desc) > 90 else "")
        table_lines.append(f"| {idx} | `{m_name}` | `{ret_str}` | {req_str} | {clean_desc} |")

    with open(refs_dir / "methods_table.md", "w", encoding="utf-8") as f:
        f.write("\n".join(table_lines) + "\n")

    # 3. Synchronize to Go embedded data directory
    go_tg_dir = MCP_DIR / "data" / "telegram"
    if go_tg_dir.exists():
        shutil.copyfile(methods_file, go_tg_dir / "api_methods.json")
        shutil.copyfile(types_file, go_tg_dir / "api_types.json")
        shutil.copyfile(version_file, go_tg_dir / "version.json")
        print(f"[*] Updated embedded Go data in {go_tg_dir}")

    # 4. Re-compile Go multi-arch binaries if go is installed
    if shutil.which("go"):
        print("[*] Re-compiling Go multi-architecture static binaries with new Telegram spec...")
        try:
            subprocess.run(["go", "build", "-ldflags=-s -w", "-o", "skills-engine", "."], cwd=MCP_DIR, check=True)
            subprocess.run(["go", "build", "-ldflags=-s -w", "-o", "skills-engine-linux-arm64", "."], cwd=MCP_DIR, env={**os.environ, "GOOS": "linux", "GOARCH": "arm64", "CGO_ENABLED": "0"}, check=True)
            subprocess.run(["go", "build", "-ldflags=-s -w", "-o", "skills-engine-linux-amd64", "."], cwd=MCP_DIR, env={**os.environ, "GOOS": "linux", "GOARCH": "amd64", "CGO_ENABLED": "0"}, check=True)
            print("[✓] Re-compiled skills-engine, skills-engine-linux-arm64, and skills-engine-linux-amd64 successfully!")
        except Exception as e:
            print(f"[!] Re-compilation note: {e}")

    # 5. Dynamically update README.md badges, numbers, and versions
    metrics = update_readme_metrics.get_current_metrics()
    metrics["tg_version"] = clean_ver
    metrics["tg_methods"] = len(new_methods)
    metrics["tg_types"] = len(new_types)
    update_readme_metrics.update_readme(metrics)

    # 6. Synchronize to runtime and workspace directories if accessible
    extra_dirs = [
        Path("/root/bots/factory/.agents/skills/telegram-bot-api-methods"),
        Path("/root/.gemini/config/skills/telegram-bot-api-methods"),
        Path("/root/.gemini/skills-catalog/skills/telegram-bot-api-methods"),
    ]
    for d in extra_dirs:
        try:
            if d.exists() and d != SKILL_DIR:
                dest_refs = d / "references"
                dest_refs.mkdir(parents=True, exist_ok=True)
                for fname in ["api_methods.json", "api_types.json", "version.json", "methods_table.md"]:
                    src = refs_dir / fname
                    if src.exists():
                        shutil.copyfile(src, dest_refs / fname)
        except Exception:
            pass

    print(f"[✓] Successfully synchronized Telegram Bot API to version {clean_ver}!")
    return True, clean_ver, len(new_methods), len(new_types)

if __name__ == "__main__":
    force_run = "--force" in sys.argv
    changed, ver, m_cnt, t_cnt = fetch_and_sync(force=force_run)
    sys.exit(0)
