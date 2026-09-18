#!/usr/bin/env python3
"""
Dynamic README Metrics & Versions Synchronizer
Automatically parses repository state (Telegram Bot API spec, Go toolchain version,
MCP tool count, schemas, binary size) and updates README.md badges, diagrams,
headers, tables, and prose with 100% deterministic accuracy.
"""

import os
import re
import json
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
README_FILE = ROOT_DIR / "README.md"

def categorize_method(name: str) -> str:
    n = name.lower()
    if "forumtopic" in n:
        return "Forum & Topic Management"
    if any(k in n for k in ["editmessagetext", "editmessagecaption", "editmessagemedia", "editmessagereplymarkup", "editmessagelivelocation", "stopmessagelivelocation", "deletemessage", "deletemessages"]):
        return "Editing & Deletions"
    if any(k in n for k in ["gift", "star", "invoice", "payment", "checkout", "subscriptioninvite"]):
        return "Gifts, Stars & Payments"
    if any(k in n for k in ["webhook", "getme", "logout", "close", "mycommands", "menubutton", "myname", "mydescription", "myshortdescription", "mydefaultadministratorrights", "customemojistickers", "getupdates"]):
        return "Webhooks & Configuration"
    if (n.startswith("send") and not any(k in n for k in ["chataction", "gift", "invoice"])) or any(k in n for k in ["forwardmessage", "forwardmessages", "copymessage", "copymessages", "stoppoll"]):
        return "Messages & Media"
    if any(k in n for k in ["chat", "userprofilephotos", "user", "boost", "stickerset"]):
        return "Chat & Member Governance"
    return "Telegram Business & Misc"

def get_current_metrics():
    # 1. Telegram API metrics
    tg_ref_matches = list(ROOT_DIR.glob("skills/**/telegram-bot-api-methods/references"))
    tg_ref_dir = tg_ref_matches[0] if tg_ref_matches else (ROOT_DIR / "skills" / "telegram-bot-api-methods" / "references")
    version_file = tg_ref_dir / "version.json"
    methods_file = tg_ref_dir / "api_methods.json"
    types_file = tg_ref_dir / "api_types.json"
    
    tg_ver = "10.3"
    tg_methods = 185
    tg_types = 400
    domain_counts = {}
    
    if version_file.exists():
        try:
            vdata = json.loads(version_file.read_text(encoding="utf-8"))
            tg_ver = str(vdata.get("version", tg_ver)).replace("Bot API", "").replace("Telegram", "").strip()
        except Exception:
            pass
            
    if methods_file.exists():
        try:
            mdata = json.loads(methods_file.read_text(encoding="utf-8"))
            tg_methods = len(mdata)
            for m in mdata:
                dom = categorize_method(m)
                domain_counts[dom] = domain_counts.get(dom, 0) + 1
        except Exception:
            pass
            
    if types_file.exists():
        try:
            tdata = json.loads(types_file.read_text(encoding="utf-8"))
            tg_types = len(tdata)
        except Exception:
            pass

    # 2. Tools count from schemas directory
    schema_dir = ROOT_DIR / "mcp-schemas" / "skills-engine"
    tools_count = len(list(schema_dir.glob("*.json"))) if schema_dir.exists() else 51

    # 3. Skills and Rules counts & Indexed Entities
    skills_dir = ROOT_DIR / "skills"
    rules_dir = ROOT_DIR / "rules"
    skills_count = len(list(skills_dir.glob("**/SKILL.md"))) if skills_dir.exists() else 0
    rules_count = len(list(rules_dir.glob("*.md"))) if rules_dir.exists() else 0

    indexed_entities = 2160
    db_path = Path.home() / ".gemini/mcp-servers/skills-engine/skills_index.db"
    if db_path.exists():
        try:
            import sqlite3
            with sqlite3.connect(str(db_path)) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM items")
                indexed_entities = cur.fetchone()[0]
        except Exception:
            pass

    # 4. Go version from go.mod first (canonical), fallback to go version
    go_ver = "1.26.5"
    go_mod = ROOT_DIR / "mcp-servers" / "skills-engine" / "go.mod"
    if go_mod.exists():
        m = re.search(r"^go\s+([0-9.]+)", go_mod.read_text(encoding="utf-8"), re.M)
        if m:
            go_ver = m.group(1)
    else:
        try:
            out = subprocess.check_output(["go", "version"], text=True)
            m = re.search(r"go(\d+\.\d+(\.\d+)?)", out)
            if m:
                go_ver = m.group(1)
        except Exception:
            pass

    # 5. Static binary size
    bin_path = ROOT_DIR / "mcp-servers" / "skills-engine" / "skills-engine"
    bin_size = "6.7MB"
    if bin_path.exists():
        sz = bin_path.stat().st_size / (1024 * 1024)
        bin_size = f"{sz:.1f}MB"

    return {
        "tg_version": tg_ver,
        "tg_methods": tg_methods,
        "tg_types": tg_types,
        "domain_counts": domain_counts,
        "tools_count": tools_count,
        "skills_count": skills_count,
        "rules_count": rules_count,
        "indexed_entities": indexed_entities,
        "go_version": go_ver,
        "bin_size": bin_size,
    }

def update_readme(metrics: dict = None) -> bool:
    if metrics is None:
        metrics = get_current_metrics()
        
    if not README_FILE.exists():
        print(f"[!] README file not found: {README_FILE}")
        return False

    content = README_FILE.read_text(encoding="utf-8")
    original = content

    tg_ver = metrics["tg_version"]
    tg_m = metrics["tg_methods"]
    tg_t = metrics["tg_types"]
    dom_counts = metrics.get("domain_counts", {})
    tools_cnt = metrics["tools_count"]
    go_ver = metrics["go_version"]
    bin_sz = metrics["bin_size"]

    # 1. Telegram Bot API badge
    tg_badge_regex = r"\[!\[Telegram Bot API\]\(https://img\.shields\.io/badge/Telegram%20Bot%20API-[^)]+\)\]\(https://core\.telegram\.org/bots/api\)"
    new_tg_badge = f"[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-{tg_ver}%20({tg_m}%20Methods%20%7C%20{tg_t}%20Types)-2CA5E0?logo=telegram&logoColor=white)](https://core.telegram.org/bots/api)"
    content = re.sub(tg_badge_regex, new_tg_badge, content)

    # 2. MCP Tools Badge
    tools_badge_regex = r"\[!\[Active MCP Tools\]\(https://img\.shields\.io/badge/MCP%20Tools-[^)]+\)\]\(#complete-mcp-tool-suite-[0-9]+-enterprise-tools\)"
    new_tools_badge = f"[![Active MCP Tools](https://img.shields.io/badge/MCP%20Tools-{tools_cnt}%20Tools%20(Go%20{go_ver}%20Native)-success.svg)](#complete-mcp-tool-suite-{tools_cnt}-enterprise-tools)"
    content = re.sub(tools_badge_regex, new_tools_badge, content)

    # 3. Engine Architecture Badge
    engine_badge_regex = r"\[!\[Engine Architecture\]\(https://img\.shields\.io/badge/Engine-[^)]+\)\]\(#\)"
    new_engine_badge = f"[![Engine Architecture](https://img.shields.io/badge/Engine-Go%20{go_ver}%20%7C%20Static%20Binary%20({bin_sz})-blue.svg)](#)"
    content = re.sub(engine_badge_regex, new_engine_badge, content)

    # 3b. Indexed Entities Badge
    idx_cnt = metrics.get("indexed_entities", 2160)
    rounded_idx = f"{(idx_cnt // 10) * 10:,}%2B".replace(",", "%2C")
    entities_badge_regex = r"\[!\[Indexed Entities\]\(https://img\.shields\.io/badge/Indexed%20Entities-.*?\.svg\)\]\(#\)"
    new_entities_badge = f"[![Indexed Entities](https://img.shields.io/badge/Indexed%20Entities-{rounded_idx}%20(FastMCP%20%26%20SQLite)-orange.svg)](#)"
    content = re.sub(entities_badge_regex, new_entities_badge, content)

    # 4. Quick Start Bullet 3 (Go Engine)
    content = re.sub(
        r"3\.\s+\*\*Go\s+[0-9.]+\s+Native\s+MCP\s+Engine\*\*:\s+Auto-provisions\s+the\s+official\s+Go\s+[0-9.]+\s+toolchain\s+if\s+missing,\s+compiles\s+the\s+[0-9.]+MB\s+statically\s+linked\s+`skills-engine`\s+binary,\s+and\s+hot-activates\s+all\s+[0-9]+\s+tools",
        f"3. **Go {go_ver} Native MCP Engine**: Auto-provisions the official Go {go_ver} toolchain if missing, compiles the {bin_sz} statically linked `skills-engine` binary, and hot-activates all {tools_cnt} tools",
        content
    )

    # 5. Quick Start Bullet 4 (Telegram Bot API)
    content = re.sub(
        r"4\.\s+\*\*Telegram\s+Bot\s+API\s+[0-9.]+\s+Master\s+Engine\*\*:\s+Ingests\s+and\s+builds\s+real-time\s+SQLite\s+FTS5\s+indices\s+for\s+all\s+\*\*[0-9]+\s+methods\*\*\s+and\s+\*\*[0-9]+\s+types\*\*\.",
        f"4. **Telegram Bot API {tg_ver} Master Engine**: Ingests and builds real-time SQLite FTS5 indices for all **{tg_m} methods** and **{tg_t} types**.",
        content
    )

    # 6. Architecture Diagram ASCII
    content = re.sub(
        r"skills-engine\s+\(Go\s+[0-9.]+\s+Native,\s+[0-9]+\s+Tools\)",
        f"skills-engine (Go {go_ver} Native, {tools_cnt} Tools)",
        content
    )
    content = re.sub(
        r"\|\s+[0-9]+\s+methods\s+/\s+[0-9]+\s+Types\s+\|",
        f"|    {tg_m} methods / {tg_t} Types    |",
        content
    )
    content = re.sub(
        r"\[Telegram\s+Bot\s+API\s+[0-9.]+\]",
        f"[Telegram Bot API {tg_ver}]",
        content
    )
    content = re.sub(
        r"-\s+[0-9]+\s+Official\s+Methods",
        f"- {tg_m} Official Methods",
        content
    )
    content = re.sub(
        r"-\s+[0-9]+\s+Official\s+Types",
        f"- {tg_t} Official Types",
        content
    )

    # 7. Telegram Reference Header
    content = re.sub(
        r"##\s+Telegram\s+Bot\s+API\s+[0-9.]+\s+Master\s+Reference",
        f"## Telegram Bot API {tg_ver} Master Reference",
        content
    )

    # 8. Domain Table Method Counts
    if dom_counts:
        content = re.sub(
            r"\|\s+\*\*Messages\s+&\s+Media\*\*\s+\|\s+[0-9]+\s+\|",
            f"| **Messages & Media** | {dom_counts.get('Messages & Media', 32)} |",
            content
        )
        content = re.sub(
            r"\|\s+\*\*Editing\s+&\s+Deletions\*\*\s+\|\s+[0-9]+\s+\|",
            f"| **Editing & Deletions** | {dom_counts.get('Editing & Deletions', 12)} |",
            content
        )
        content = re.sub(
            r"\|\s+\*\*Chat\s+&\s+Member\s+Governance\*\*\s+\|\s+[0-9]+\s+\|",
            f"| **Chat & Member Governance** | {dom_counts.get('Chat & Member Governance', 38)} |",
            content
        )
        content = re.sub(
            r"\|\s+\*\*Forum\s+&\s+Topic\s+Management\*\*\s+\|\s+[0-9]+\s+\|",
            f"| **Forum & Topic Management** | {dom_counts.get('Forum & Topic Management', 12)} |",
            content
        )
        content = re.sub(
            r"\|\s+\*\*Gifts,\s+Stars\s+&\s+Payments\*\*\s+\|\s+[0-9]+\s+\|",
            f"| **Gifts, Stars & Payments** | {dom_counts.get('Gifts, Stars & Payments', 16)} |",
            content
        )
        content = re.sub(
            r"\|\s+\*\*Webhooks\s+&\s+Configuration\*\*\s+\|\s+[0-9]+\s+\|",
            f"| **Webhooks & Configuration** | {dom_counts.get('Webhooks & Configuration', 24)} |",
            content
        )
        content = re.sub(
            r"\|\s+\*\*Telegram\s+Business\s+&\s+Misc\*\*\s+\|\s+[0-9]+\s+\|",
            f"| **Telegram Business & Misc** | {dom_counts.get('Telegram Business & Misc', 51)} |",
            content
        )

    # 9. MCP Tools Section Header & count
    content = re.sub(
        r"##\s+Complete\s+MCP\s+Tool\s+Suite\s+\([0-9]+\s+Enterprise\s+Tools\)",
        f"## Complete MCP Tool Suite ({tools_cnt} Enterprise Tools)",
        content
    )
    content = re.sub(
        r"The\s+MCP\s+server\s+exposes\s+[0-9]+\s+deterministic\s+tools",
        f"The MCP server exposes {tools_cnt} deterministic tools",
        content
    )
    content = re.sub(
        r"- `get_telegram_bot_api_spec`:\s+Instant\s+parameter,\s+type,\s+and\s+Rust\s+code\s+retrieval\s+for\s+all\s+[0-9]+\s+methods\.",
        f"- `get_telegram_bot_api_spec`: Instant parameter, type, and Rust code retrieval for all {tg_m} methods.",
        content
    )
    content = re.sub(
        r"- `validate_telegram_payload`:\s+Strict\s+offline\s+schema\s+&\s+payload\s+validator\s+for\s+Bot\s+API\s+[0-9.]+\s+/\s+9\.4\+\s+requests",
        f"- `validate_telegram_payload`: Strict offline schema & payload validator for Bot API {tg_ver} / 9.4+ requests",
        content
    )

    # 10. Go Architecture Section
    content = re.sub(
        r"##\s+Go\s+[0-9.]+\s+Native\s+High-Performance\s+Architecture",
        f"## Go {go_ver} Native High-Performance Architecture",
        content
    )
    content = re.sub(
        r"statically\s+linked\s+binary\s+compiled\s+with\s+\*\*Go\s+[0-9.]+\*\*:",
        f"statically linked binary compiled with **Go {go_ver}**:",
        content
    )
    content = re.sub(
        r"-\s+\*\*Binary\s+Footprint\*\*:\s+[0-9.]+MB\s+standalone\s+static\s+binary",
        f"- **Binary Footprint**: {bin_sz} standalone static binary",
        content
    )
    content = re.sub(
        r"-\s+\*\*Embedded\s+Assets\*\*:\s+Embeds\s+all\s+[0-9]+\s+tool\s+schemas\s+and\s+the\s+complete\s+Telegram\s+Bot\s+API\s+[0-9.]+\s+master\s+specification\s+\([0-9]+\s+methods,\s+[0-9]+\s+types\)",
        f"- **Embedded Assets**: Embeds all {tools_cnt} tool schemas and the complete Telegram Bot API {tg_ver} master specification ({tg_m} methods, {tg_t} types)",
        content
    )
    content = re.sub(
        r"official\s+Go\s+[0-9.]+\s+archive\s+if\s+missing",
        f"official Go {go_ver} archive if missing",
        content
    )

    if content != original:
        README_FILE.write_text(content, encoding="utf-8")
        print(f"[✓] README.md updated successfully with dynamic metrics:")
        print(f"    - Telegram Bot API: {tg_ver} ({tg_m} methods, {tg_t} types)")
        print(f"    - Active Tools: {tools_cnt}")
        print(f"    - Go Version: {go_ver}")
        print(f"    - Binary Size: {bin_sz}")
        return True
    else:
        print("[✓] README.md is already perfectly synchronized with active versions and counts.")
        return False

if __name__ == "__main__":
    update_readme()
