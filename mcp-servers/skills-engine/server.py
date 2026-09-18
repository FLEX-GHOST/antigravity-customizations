import functools
import math
import os
import re
import sqlite3
import sys
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("skills-engine")

DB_PATH = Path("/root/.gemini/mcp-servers/skills-engine/skills_index.db")

SEARCH_PATHS = [
    Path("/root/.gemini/skills-catalog/repos/anthropics-skills"),
    Path("/root/.gemini/skills-catalog/repos/alirezarezvani-claude-skills"),
    Path("/root/.gemini/skills-catalog/repos/awesome-cursorrules"),
    Path("/root/.gemini/skills-catalog/repos/composiohq-awesome-claude-skills"),
    Path("/root/.gemini/config"),
    Path("/root/.gemini/antigravity-ide/brain/anti_slop_official_rules"),
    Path("/root/bots/factory/.agents"),
    Path("/root/storage-dashboard/.agents/skills"),
    Path("/root/.gemini/skills-catalog"),
]

# Comprehensive everyday Arab & Iraqi programmer dialect and technical intent map
AR_STEM_MAP = {
    # --- Common Everyday Actions & Directives (أوامر وطلبات البرمجة اليومية) ---
    "حل مشكل": "root-cause systematic-debugging troubleshooting fix bug code_integrity",
    "حل المشكل": "root-cause systematic-debugging troubleshooting fix bug code_integrity",
    "مشكل": "debugging root-cause fix patch troubleshooting error",
    "اضف ميز": "feature implementation builder scaffolding new-feature",
    "اضافة ميز": "feature implementation builder scaffolding new-feature",
    "ضيف ميز": "feature implementation builder scaffolding new-feature",
    "سوي ميز": "feature implementation builder scaffolding new-feature",
    "ضيف": "feature implementation builder add-feature",
    "سويلي": "feature builder create implement",
    "سوي": "feature builder create implement",
    "ابني": "scaffolding builder architecture implementation",
    "صلح": "fix bug refactor patch correct code_integrity systematic-debugging",
    "فيكس": "bugfix patch refactor repair integrity systematic-debugging",

    # --- UI, Design & Slop (واجهات، ألوان، أزرار، تصميم تعبان/زبالة/خايس) ---
    "ازرار": "button-states interactive hover focus active telegram-button-styling button_hierarchy",
    "زرار": "button-states interactive hover focus active telegram-button-styling",
    "زر": "button states hierarchy interactive hover focus aria active",
    "دكم": "button states hierarchy interactive hover focus telegram-button-styling",
    "دكمه": "button states hierarchy interactive hover focus telegram-button-styling",
    "كبس": "button states interactive click trigger action",
    "تعبان": "anti-ui-slop anti_ai_design design-taste-frontend better-ui visual-design",
    "زبال": "anti-ui-slop anti_ai_design clean-code refactor unslop",
    "خايس": "anti-ui-slop anti_ai_design clean-code refactor unslop",
    "سلوب": "anti-ui-slop antislop anti_ai_design unslop visual-design",
    "تصميم": "ui frontend visual design styling typography web better-ui design-taste-frontend",
    "واجه": "ui frontend visual design styling typography web css better-ui",
    "فرونت": "frontend react nextjs ui tailwind css design",
    "الوان": "colors palette contrast semantic tokens wcag accessibility better-colors",
    "لون": "colors palette contrast semantic tokens better-colors",
    "بنفسج": "anti-ui-slop purple gradient bloat aesthetic anti_ai_design",
    "ايقون": "icons svg vector symbols lucide phosphor better-icons",
    "رمز": "icons svg vector symbols lucide better-icons",
    "خطوط": "better-typography web-typography font hierarchy scale readability",
    "خط": "typography font hierarchy scale readability web-typography",
    "كود وصخ": "clean-code refactor clean-architecture code_integrity unslop",
    "نظف": "refactor clean-code architecture unslop code_integrity",
    "رتب": "refactor clean-code architecture project_structure_standards",
    "تنظيف": "refactor clean-code architecture unslop",
    "معمار": "clean-architecture modularity decoupled ddd ports-adapters",

    # --- Performance, Crashes & Memory (الأداء، التعليق، الرام، الكراش) ---
    "معلك": "deadlock mutex lock synchronization concurrency tokio async freeze hang",
    "صافن": "deadlock tokio async hang freeze mutex concurrency",
    "واكف": "debugging crash troubleshooting error resilience",
    "عطلان": "debugging crash troubleshooting error resilience",
    "ما يشتغل": "debugging troubleshooting root-cause fix error",
    "ثكيل": "performance latency speed zero-allocation optimize profiling benchmark",
    "بطي": "performance latency speed zero-allocation optimize bottleneck",
    "سرع": "performance optimization fast speed latency low-latency",
    "اداء": "performance latency speed zero-allocation profiling benchmark",
    "تحسين": "optimization performance profiling clean architecture",
    "ذاكر": "memory optimization ram buffer cache leak jemalloc zero-allocation",
    "رام": "memory optimization ram buffer leak jemalloc zero-allocation zero-ram-idle",
    "ياكل رام": "memory optimization ram leak buffer jemalloc zero-ram-idle",
    "تسريب": "memory leak buffer retain cycle jemalloc resource-cleanup",
    "ليك": "memory leak buffer jemalloc resource cleanup",
    "كراش": "panic zero-panic resilience fault-tolerance recovery error-handling",
    "يطفي": "crash panic resilience supervisor systemd recovery",
    "يموت": "crash panic resilience supervisor systemd recovery",
    "ضرب": "panic crash error exception fault",
    "قفل": "deadlock mutex lock synchronization concurrency parking_lot dashmap",
    "تزامن": "concurrency async tokio channel joinset worker pool",
    "توازي": "parallel async concurrency worker thread pool",

    # --- Telegram Bots & MTProto (تليكرام، بوتات، فلود، ويب هوك) ---
    "تليجرام": "telegram bot webhook floodwait mtproto teloxide",
    "تيليجرام": "telegram bot webhook floodwait mtproto teloxide",
    "تليغرام": "telegram bot webhook floodwait mtproto teloxide",
    "تليكرام": "telegram bot webhook floodwait mtproto teloxide",
    "تلكرام": "telegram bot webhook floodwait mtproto teloxide",
    "تلي": "telegram bot webhook floodwait mtproto teloxide",
    "بوت": "bot telegram automation client webhook worker polling",
    "بوتات": "telegram bot factory multi-tenant webhook architecture",
    "قناة": "channel broadcast telegram bot admin notification",
    "كروب": "group chat supergroup telegram bot permissions",
    "مجموعة": "group chat telegram bot permissions management",
    "كيبورد": "inline-keyboard reply-markup telegram-button-styling",
    "انلاين": "inline-keyboard callback-query telegram-button-styling",
    "ويب هوك": "webhook telegram-webhook axum warp actix",
    "ويبهوك": "webhook telegram-webhook axum warp actix",
    "بولينغ": "polling long-polling telegram worker loop",
    "بولينج": "polling long-polling telegram worker loop",
    "فلود": "floodwait rate-limit retry backoff jitter telegram 420",
    "حظر": "floodwait rate-limit retry backoff jitter telegram ban",
    "ستيكر": "sticker custom-emoji telegram bot media",
    "ايموجي": "custom-emoji telegram-button-styling vector icons",

    # --- Errors & Resilience (الأخطاء والاستثناءات) ---
    "خطا": "error handling thiserror anyhow result resilience backoff",
    "ايرور": "error exception traceback debug fault-tolerance",
    "اكسبشن": "exception error handling debug traceback",
    "انفايند": "null undefined error handling option result",
    "نل": "null-safety option result error handling",

    # --- Database & Storage (قواعد البيانات والتخزين) ---
    "قاعد": "database sql sqlite postgres storage query schema migration",
    "بيان": "database data storage dataset persist sqlite postgres",
    "داتا": "database sqlite postgres sql query storage",
    "سيكول": "sql sqlite postgres database query migration",
    "جدول": "database table schema sql migration sqlite",
    "تخزين": "storage persist database file-system cache",
    "كويري": "query sql database indexing optimization",

    # --- Languages & Frameworks (لغات وأطر العمل) ---
    "رست": "rust tokio memory cargo async zero-allocation jemalloc",
    "روست": "rust tokio memory cargo async zero-allocation jemalloc",
    "بايثون": "python fastapi pydantic pytest asyncio",
    "جو": "go golang goroutine channel gin-gonic",
    "تايب": "typescript ts types interfaces generics react",
    "جافاسكربت": "javascript nodejs ecmascript typescript",
    "رياكت": "react frontend hooks state components nextjs",
    "نيكست": "nextjs react ssr frontend components",

    # --- System & DevOps (الأنظمة، السيرفرات، الشبكات) ---
    "لينكس": "linux debian ubuntu systemd process terminal bash shell",
    "سيرفر": "server daemon systemd linux deployment proxy nginx",
    "خادم": "server daemon systemd linux deployment proxy nginx",
    "حاوي": "docker container dockerfile compose kubernetes",
    "دوكر": "docker container dockerfile compose orchestration",
    "شبك": "network http websocket tls client rate-limit",
    "ويب": "web html css vanilla responsive api integration",
    "امان": "security vulnerability injection scanner sanitize auth owasp",
    "حماي": "security vulnerability sanitize authentication jwt ssl",
    "ثغر": "vulnerability exploit patch security injection xss sql",
    "اختبار": "testing tdd pytest unit integration verification e2e",
    "تيست": "testing unit integration verification tdd",

    # --- Permissions & Governance (صلاحيات، حوكمة، صدق تقني) ---
    "برمشن": "permission policy allow auto-approve authorization turbo",
    "صلاحي": "permission policy authorization grant allow access",
    "إذن": "permission policy allow authorization grant",
    "مجامل": "honest-engineering anti-sycophancy unslop frank blunt truth",
    "تزلف": "anti-sycophancy honest-engineering frank blunt",
    "نفاق": "anti-sycophancy honest-engineering frank",
    "صراح": "honest-engineering frank blunt technical truth",
}

CORE_GOVERNANCE_IDS = [
    "rule:anti_ai_design",
    "skill:anti-ui-slop",
    "rule:honest_engineering",
    "skill:anti-sycophancy",
    "rule:61_unslop_conversational_anti_sycophancy_rules",
    "rule:strict_comment_discipline",
    "rule:clean_code_architecture",
    "rule:code_integrity",
    "rule:security_hygiene",
]

_local = threading.local()

def get_db_conn() -> sqlite3.Connection:
    if not hasattr(_local, "conn") or _local.conn is None:
        conn = sqlite3.connect(str(DB_PATH), timeout=15.0, check_same_thread=False)
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA cache_size = -131072")  # 128MB RAM cache
        conn.execute("PRAGMA mmap_size = 268435456") # 256MB memory mapped zero-copy I/O
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA busy_timeout = 15000")
        _local.conn = conn
    return _local.conn

def init_db():
    conn = get_db_conn()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        item_type TEXT,
        name TEXT,
        description TEXT,
        triggers TEXT,
        language TEXT,
        category TEXT,
        path TEXT,
        mtime REAL,
        content TEXT,
        quality_score INTEGER DEFAULT 50,
        source_tier TEXT DEFAULT 'community'
    )
    """)
    cur = conn.execute("PRAGMA table_info(items)")
    cols = {row[1] for row in cur.fetchall()}
    if "quality_score" not in cols:
        conn.execute("ALTER TABLE items ADD COLUMN quality_score INTEGER DEFAULT 50")
    if "source_tier" not in cols:
        conn.execute("ALTER TABLE items ADD COLUMN source_tier TEXT DEFAULT 'community'")

    conn.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS items_fts USING fts5(
        id UNINDEXED,
        name,
        description,
        triggers,
        language,
        category,
        content,
        tokenize='unicode61 remove_diacritics 2'
    )
    """)
    conn.commit()

def clean_description(desc: str, content: str = "", max_len: int = 150) -> str:
    text = desc or ""
    if not text or len(text.strip()) < 10 or text.startswith("[!") or text.startswith("#"):
        for line in content.splitlines():
            s = line.strip()
            if not s or s.startswith("#") or s.startswith("---") or s.startswith("[!") or s.startswith("!["):
                continue
            if len(s) > 15:
                text = s
                break
    text = re.sub(r'\[\!\[.*?\]\(.*?\)\]\(.*?\)', '', text)
    text = re.sub(r'\!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[#*`_>~|]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        cut = text[:max_len].rsplit(' ', 1)[0]
        return cut + "..."
    return text

def compute_quality_score(path_str: str, content: str) -> Tuple[int, str]:
    length = len(content.strip())
    if length < 300 or "Insert instructions below" in content or "Replace with description" in content:
        return (5, "stub")

    score = 0
    tier = "community"

    if "anthropics-skills" in path_str or "anti_slop_official_rules" in path_str:
        score += 35
        tier = "official"
    elif "alirezarezvani" in path_str or "awesome-cursorrules" in path_str or "composiohq" in path_str:
        score += 25
        tier = "top-starred"
    elif "config" in path_str:
        score += 20
        tier = "core"

    if length >= 3500:
        score += 35
    elif length >= 1800:
        score += 25
    elif length >= 800:
        score += 15
    else:
        score += 5

    if "##" in content:
        score += 10
    if "```" in content:
        score += 10
    if any(k in content for k in ("Workflow", "Instructions", "Examples", "Guidelines", "Standard", "Prerequisites")):
        score += 10
    if any(k in content for k in ("Do NOT", "Never", "Avoid", "Forbidden", "Banned")):
        score += 5

    return (min(100, score), tier)

def extract_meta(content: str) -> Tuple[Dict[str, Any], str]:
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    try:
        data = yaml.safe_load(parts[1])
        if isinstance(data, dict):
            return data, parts[2]
    except Exception:
        pass
    return {}, parts[2]

def extract_first_desc(content: str) -> str:
    return clean_description("", content, max_len=200)

def detect_language_from_text(name: str, content: str) -> str:
    n = name.lower()
    c = content[:1500].lower()
    combined = n + " " + c
    if any(k in combined for k in ["rust", "cargo", "tokio", "diesel", "serde", "jemalloc"]):
        return "rust"
    if any(k in combined for k in ["golang", "goroutine", "go.mod", "gin-gonic"]):
        return "go"
    if any(k in combined for k in ["python", "pytest", "fastapi", "django", "pydantic"]):
        return "python"
    if any(k in combined for k in ["typescript", "tsx", "next.js", "nextjs", "react", "tailwind", "vue", "svelte"]):
        return "typescript"
    if any(k in combined for k in ["docker", "kubernetes", "k8s", "helm", "devops"]):
        return "devops"
    if any(k in combined for k in ["sqlite", "postgres", "sql", "migration", "prisma"]):
        return "database"
    return "general"

last_sync_time = 0.0

def sync_all_directories(force: bool = False):
    global last_sync_time
    now = time.time()
    # 1-hour debounce in normal runs to eliminate disk traversal latency
    if not force and (now - last_sync_time < 3600.0):
        return

    conn = get_db_conn()
    cur = conn.execute("SELECT id, path, quality_score FROM items")
    existing_items = {row[0]: (row[1], row[2]) for row in cur.fetchall()}

    to_insert_items = []
    to_insert_fts = []
    purged_stubs = []

    for root_dir in SEARCH_PATHS:
        if not root_dir.exists():
            continue

        for p in root_dir.glob("**/SKILL.md"):
            if ".git" in p.parts:
                continue
            name = p.parent.name
            item_id = f"skill:{name}"

            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                mtime = p.stat().st_mtime
                q_score, tier = compute_quality_score(str(p), content)

                if q_score <= 10:
                    purged_stubs.append(item_id)
                    continue

                if item_id in existing_items:
                    curr_path, curr_score = existing_items[item_id]
                    if q_score <= curr_score:
                        continue

                meta, body = extract_meta(content)
                desc = clean_description(str(meta.get("description") or ""), content)
                trigs = meta.get("triggers", [])
                trigs_str = " ".join(str(t) for t in trigs) if isinstance(trigs, list) else str(trigs)
                lang = meta.get("language") or detect_language_from_text(name, content)
                cat = meta.get("category") or "skill"

                to_insert_items.append((item_id, "skill", name, desc, trigs_str, lang, str(cat), str(p), mtime, content, q_score, tier))
                to_insert_fts.append((item_id, name, desc, trigs_str, lang, str(cat), body[:3000]))
                existing_items[item_id] = (str(p), q_score)
            except Exception:
                continue

        for p in list(root_dir.glob("**/*.md")) + list(root_dir.glob("**/*.mdc")):
            if ".git" in p.parts or p.name in ("SKILL.md", "README.md", "CONTRIBUTING.md", "LICENSE", "CHANGELOG.md", "CODE_OF_CONDUCT.md"):
                continue
            is_rule = "rules" in str(p).lower() or "official_rules" in str(p).lower() or p.suffix == ".mdc"
            if not is_rule:
                continue

            name = p.stem.replace(".cursorrules", "").replace("-cursorrules-prompt-file", "")
            item_id = f"rule:{name}"

            try:
                content = p.read_text(encoding="utf-8", errors="replace")
                mtime = p.stat().st_mtime
                q_score, tier = compute_quality_score(str(p), content)

                if q_score <= 10:
                    purged_stubs.append(item_id)
                    continue

                if item_id in existing_items:
                    curr_path, curr_score = existing_items[item_id]
                    if q_score <= curr_score:
                        continue

                desc = clean_description("", content)
                lang = detect_language_from_text(name, content)

                to_insert_items.append((item_id, "rule", name, desc, "", lang, "rule", str(p), mtime, content, q_score, tier))
                to_insert_fts.append((item_id, name, desc, "", lang, "rule", content[:3000]))
                existing_items[item_id] = (str(p), q_score)
            except Exception:
                continue

    for sid in purged_stubs:
        conn.execute("DELETE FROM items WHERE id = ?", (sid,))
        conn.execute("DELETE FROM items_fts WHERE id = ?", (sid,))

    if to_insert_items:
        conn.executemany("INSERT OR REPLACE INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", to_insert_items)
        conn.executemany("INSERT OR REPLACE INTO items_fts VALUES (?, ?, ?, ?, ?, ?, ?)", to_insert_fts)
        conn.commit()

    last_sync_time = now
    clear_all_caches()

def ensure_initialized():
    init_db()
    conn = get_db_conn()
    cur = conn.execute("SELECT 1 FROM items LIMIT 1")
    if cur.fetchone() is None:
        sync_all_directories(force=True)

ensure_initialized()

def normalize_arabic(text: str) -> str:
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = re.sub(r"[أإآ]", "ا", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"ى", "ي", text)
    return text.lower()

def expand_query(query: str) -> str:
    norm = normalize_arabic(query)
    expanded = query
    matched_exps = set()
    for stem, exp in sorted(AR_STEM_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if stem in norm:
            for word in exp.split():
                matched_exps.add(word)
    if matched_exps:
        expanded += " " + " ".join(matched_exps)
    return expanded

# In-memory LRU caching for ultra-low latency (< 0.1ms)
@functools.lru_cache(maxsize=512)
def _cached_exact_skill(name: str) -> str:
    conn = get_db_conn()
    cur = conn.execute("SELECT content FROM items WHERE item_type = 'skill' AND (name = ? OR id = ?) ORDER BY quality_score DESC LIMIT 1", (name, f"skill:{name}"))
    row = cur.fetchone()
    if row:
        return row[0]
    return f"Skill '{name}' not found."

@functools.lru_cache(maxsize=512)
def _cached_exact_rule(name: str) -> str:
    conn = get_db_conn()
    cur = conn.execute("SELECT content FROM items WHERE item_type = 'rule' AND (name = ? OR id = ?) ORDER BY quality_score DESC LIMIT 1", (name, f"rule:{name}"))
    row = cur.fetchone()
    if row:
        return row[0]
    return f"Rule '{name}' not found."

@functools.lru_cache(maxsize=64)
def _cached_core_governance() -> Dict[str, Any]:
    conn = get_db_conn()
    rules_data = {}
    for rule_id in CORE_GOVERNANCE_IDS:
        cur = conn.execute("SELECT name, content FROM items WHERE id = ? ORDER BY quality_score DESC LIMIT 1", (rule_id,))
        row = cur.fetchone()
        if row:
            rules_data[row[0]] = row[1]
    return {
        "description": "Essential non-negotiable architectural governance: Anti-AI UI Slop, Honest Engineering, Anti-Sycophancy, Strict Comment Discipline, Clean Code Architecture.",
        "rules_count": len(rules_data),
        "rules": rules_data,
    }

@functools.lru_cache(maxsize=512)
def _cached_skill_toc(name: str) -> Tuple:
    content = _cached_exact_skill(name)
    if "not found" in content:
        return (name, None, content)
    headings = []
    for line in content.splitlines():
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            headings.append((len(m.group(1)), m.group(2).strip()))
    return (name, tuple(headings), None)

@functools.lru_cache(maxsize=512)
def _cached_skill_section(name: str, section_heading: str) -> str:
    content = _cached_exact_skill(name)
    if "not found" in content:
        return content

    lines = content.splitlines()
    target_idx = -1
    target_level = 0
    norm_target = section_heading.strip().lower()

    for idx, line in enumerate(lines):
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m and norm_target in m.group(2).strip().lower():
            target_idx = idx
            target_level = len(m.group(1))
            break

    if target_idx == -1:
        return f"Section '{section_heading}' not found in skill '{name}'."

    extracted = [lines[target_idx]]
    for line in lines[target_idx + 1:]:
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m and len(m.group(1)) <= target_level:
            break
        extracted.append(line)

    return "\n".join(extracted)

def clear_all_caches():
    _cached_exact_skill.cache_clear()
    _cached_exact_rule.cache_clear()
    _cached_core_governance.cache_clear()
    _cached_skill_toc.cache_clear()
    _cached_skill_section.cache_clear()

@mcp.tool()
def search_agent_capabilities(query: str, domain: Optional[str] = None, language: Optional[str] = None, min_quality: int = 40, limit: int = 8) -> List[Dict[str, Any]]:
    full_query = expand_query(query).strip()
    words = re.findall(r"[\w]+", full_query)
    clean_tokens = []
    seen = set()
    for w in words:
        wl = w.lower().strip()
        if len(wl) > 1 and wl not in seen:
            seen.add(wl)
            clean_tokens.append(wl)

    if not clean_tokens:
        return []

    # Weighted query parts: prefix search
    fts_query_parts = [f'"{tok}"*' for tok in clean_tokens[:14]]
    fts_query = " OR ".join(fts_query_parts)

    conn = get_db_conn()
    results = []

    try:
        cur = conn.execute("""
            SELECT items.id, items.item_type, items.name, items.description, items.language, items.category,
                   items.quality_score, items.source_tier, items.content,
                   bm25(items_fts, 20.0, 10.0, 15.0, 6.0, 6.0, 1.2) as rank_score
            FROM items_fts
            JOIN items ON items.id = items_fts.id
            WHERE items_fts MATCH ? AND items.quality_score >= ?
            ORDER BY (rank_score * (items.quality_score / 50.0))
            LIMIT 50
        """, (fts_query, min_quality))

        for row in cur.fetchall():
            item_id, item_type, name, desc, item_lang, cat, q_score, tier, raw_content, rank = row
            if language and language.lower() not in item_lang.lower():
                continue
            if domain and domain.lower() not in name.lower() and domain.lower() not in cat.lower():
                continue

            cleaned_desc = clean_description(desc, raw_content, max_len=140)

            tier_mult = 1.35 if tier == "official" else (1.2 if tier == "top-starred" else (1.1 if tier == "core" else 1.0))
            confidence = round(abs(rank) * (q_score / 50.0) * tier_mult * 100, 1)

            results.append({
                "id": item_id,
                "type": item_type,
                "name": name,
                "language": item_lang,
                "quality_score": q_score,
                "tier": tier,
                "description": cleaned_desc,
                "confidence_score": confidence,
            })
            if len(results) >= limit:
                break
    except Exception:
        pass

    return results

@mcp.tool()
def get_top_rated_skills(category: Optional[str] = None, language: Optional[str] = None, tier: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db_conn()
    query = "SELECT id, name, item_type, language, category, quality_score, source_tier, description, content FROM items WHERE item_type = 'skill' AND quality_score >= 60"
    params: List[Any] = []
    if category:
        query += " AND (category LIKE ? OR name LIKE ?)"
        params.extend([f"%{category}%", f"%{category}%"])
    if language:
        query += " AND language LIKE ?"
        params.append(f"%{language}%")
    if tier:
        query += " AND source_tier = ?"
        params.append(tier)
    query += " ORDER BY quality_score DESC LIMIT ?"
    params.append(limit)

    cur = conn.execute(query, params)
    results = []
    for row in cur.fetchall():
        results.append({
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "language": row[3],
            "category": row[4],
            "quality_score": row[5],
            "tier": row[6],
            "description": clean_description(row[7], row[8], max_len=140),
        })
    return results

@mcp.tool()
def audit_skill_quality(skill_name_or_id: str) -> Dict[str, Any]:
    conn = get_db_conn()
    cur = conn.execute("SELECT id, name, path, quality_score, source_tier, length(content), content FROM items WHERE id = ? OR name = ? LIMIT 1", (skill_name_or_id, skill_name_or_id))
    row = cur.fetchone()
    if not row:
        return {
            "status": "NOT_FOUND",
            "message": f"Skill {skill_name_or_id} not found in index.",
        }

    item_id, name, path, q_score, tier, length, content = row
    has_examples = "```" in content
    has_sections = "##" in content
    has_negative_rules = any(k in content for k in ("Do NOT", "Never", "Avoid", "Banned", "Forbidden"))
    is_stub = length < 300 or "Insert instructions below" in content or "Replace with description" in content

    return {
        "id": item_id,
        "name": name,
        "path": path,
        "quality_score": q_score,
        "tier": tier,
        "length_bytes": length,
        "is_stub": is_stub,
        "has_code_examples": has_examples,
        "has_sections": has_sections,
        "has_negative_rules": has_negative_rules,
        "evaluation": "EXCELLENT" if q_score >= 80 else ("GOOD" if q_score >= 60 else ("WEAK_NEEDS_UPGRADE" if q_score >= 30 else "STUB_SHOULD_PURGE")),
    }

@mcp.tool()
def get_exact_skill(name: str) -> str:
    return _cached_exact_skill(name)

@mcp.tool()
def get_exact_rule(name: str) -> str:
    return _cached_exact_rule(name)

@mcp.tool()
def get_core_governance_rules() -> Dict[str, Any]:
    return _cached_core_governance()

@mcp.tool()
def audit_anti_sycophancy(response_text: str) -> Dict[str, Any]:
    violations = []
    lines = response_text.splitlines()

    sycophancy_indicators = [
        (r"(?i)\b(great question|excellent question|you are absolutely right|you're absolutely right|certainly[!,]|i would be happy to help|i'd be happy to help|i am thrilled to|excellent idea|good point|wonderful question|thank you for asking)\b", "Sycophantic flattery or servile opener"),
        (r"(?i)(سؤال ممتاز|سؤال رائع|أنت على حق تماما|أنت محق تماما|بالتأكيد يسعدني|يسعدني مساعدتك|فكرة رائعة جدا|يا له من سؤال|مما لا شك فيه|في الختام يجدر الذكر)", "Arabic sycophantic flattery or conversational filler"),
        (r"(?i)\b(delve|tapestry|testament|seamless|holistic|leverage|cutting-edge|elevate|multifaceted|beacon|pivotal|revolutionize)\b", "AI stock filler buzzword"),
        (r"(?i)\b(as an ai language model|as an ai|in conclusion, it is important to remember|it is worth noting that|keep in mind that)\b", "Patronizing AI disclaimer or robotic closure"),
        (r"(?i)(i apologize for the confusion|my apologies, you are right|sorry about that, you're right|أعتذر عن الخطأ، معك حق)", "Reflexive folding to user pushback without technical justification"),
    ]

    for idx, line in enumerate(lines):
        l_num = idx + 1
        s = line.strip()
        for pat, desc in sycophancy_indicators:
            m = re.findall(pat, s)
            if m:
                matched_words = [str(x[0] if isinstance(x, tuple) else x) for x in m]
                violations.append({
                    "line": l_num,
                    "matched": matched_words,
                    "rule": "honest_engineering",
                    "severity": "WARNING",
                    "feedback": desc,
                })

    return {
        "status": "FAILED" if violations else "PASSED",
        "violations_count": len(violations),
        "verdict": "Text contains sycophantic flattery or AI filler words. Strip them and lead with direct technical facts." if violations else "Clean, objective, professional text adhering to honest engineering.",
        "violations": violations,
    }

@mcp.tool()
def audit_ui_design(css_or_html: str) -> Dict[str, Any]:
    violations = []
    lines = css_or_html.splitlines()

    anti_patterns = [
        (r"(?i)(linear-gradient|radial-gradient).*#[789a-f][0-9a-f]{5}.*#[789a-f][0-9a-f]{5}", "anti_ai_design", "CRITICAL", "Generic AI purple/violet gradient detected. Use disciplined semantic palettes."),
        (r"(?i)backdrop-filter:\s*blur\(", "anti_ai_design", "WARNING", "Faux glassmorphism detected without defined structural layer."),
        (r"[\U0001F300-\U0001FAFF]", "anti_ai_design", "CRITICAL", "Raw emoji detected in UI markup. Use scalable SVGs (heroicons/lucide)."),
        (r"(?i)button[^{]*\{[^}]*\}", "button_states", "INFO", "Verify all 6 states are defined (rest, hover, active, focus-visible, disabled, loading)."),
    ]

    for idx, line in enumerate(lines):
        l_num = idx + 1
        for pat, rule, sev, desc in anti_patterns:
            if re.search(pat, line):
                violations.append({
                    "line": l_num,
                    "rule": rule,
                    "severity": sev,
                    "code_snippet": line.strip()[:100],
                    "issue": desc,
                })

    return {
        "status": "FAILED" if any(v["severity"] == "CRITICAL" for v in violations) else "PASSED",
        "violations_count": len(violations),
        "violations": violations,
    }

@mcp.tool()
def get_skill_toc(name: str) -> Dict[str, Any]:
    s_name, headings, err = _cached_skill_toc(name)
    if err:
        return {"error": err}
    return {
        "skill": s_name,
        "table_of_contents": [{"level": h[0], "heading": h[1]} for h in (headings or [])],
    }

@mcp.tool()
def get_skill_section(name: str, section_heading: str) -> str:
    return _cached_skill_section(name, section_heading)

@mcp.tool()
def register_custom_directory(directory_path: str) -> Dict[str, Any]:
    p = Path(directory_path).resolve()
    if not p.exists() or not p.is_dir():
        return {"error": f"Directory {directory_path} does not exist."}

    if p not in SEARCH_PATHS:
        SEARCH_PATHS.append(p)

    sync_all_directories(force=True)
    conn = get_db_conn()
    cur = conn.execute("SELECT count(*) FROM items WHERE path LIKE ?", (f"{str(p)}%",))
    count = cur.fetchone()[0]

    return {
        "status": "SUCCESS",
        "registered_directory": str(p),
        "indexed_items": count,
    }

@mcp.tool()
def create_new_skill(name: str, description: str, triggers: List[str], instructions: str, language: str = "general", category: str = "custom") -> Dict[str, Any]:
    safe_name = re.sub(r"[^\w-]", "-", name.lower().strip())
    target_dir = Path("/root/.gemini/skills-catalog/skills") / safe_name
    target_dir.mkdir(parents=True, exist_ok=True)
    skill_file = target_dir / "SKILL.md"

    frontmatter = {
        "name": safe_name,
        "description": description,
        "triggers": triggers,
        "language": language,
        "category": category,
    }

    yaml_block = yaml.dump(frontmatter, sort_keys=False).strip()
    full_content = f"---\n{yaml_block}\n---\n\n# {name}\n\n{instructions}\n"

    skill_file.write_text(full_content, encoding="utf-8")
    sync_all_directories(force=True)

    return {
        "status": "CREATED",
        "name": safe_name,
        "path": str(skill_file),
    }

@mcp.tool()
def detect_project_stack(directory_path: str = "/root/bots/factory") -> Dict[str, Any]:
    p = Path(directory_path).resolve()
    if not p.exists():
        return {"error": f"Path {directory_path} does not exist."}

    detected_stack = []
    recommended_rules = ["rule:honest_engineering", "rule:strict_comment_discipline", "rule:clean_code_architecture", "rule:code_integrity"]

    if (p / "Cargo.toml").exists():
        detected_stack.append("Rust")
        recommended_rules.extend(["rule:rust", "rule:rust_standards", "rule:no_lazy_fallbacks"])

    if (p / "go.mod").exists():
        detected_stack.append("Go")
        recommended_rules.extend(["rule:go", "skill:golang-code-style", "skill:golang-design-patterns"])

    if (p / "pyproject.toml").exists() or (p / "requirements.txt").exists() or (p / "setup.py").exists():
        detected_stack.append("Python")
        recommended_rules.extend(["skill:python-design-patterns", "skill:python-performance-optimization"])

    if (p / "package.json").exists():
        pkg_text = (p / "package.json").read_text(errors="ignore")
        if "next" in pkg_text:
            detected_stack.append("Next.js")
        elif "react" in pkg_text:
            detected_stack.append("React")
        else:
            detected_stack.append("Node.js/JavaScript")
        recommended_rules.extend(["rule:anti_ai_design", "skill:anti-ui-slop", "skill:better-colors", "skill:button-states"])

    if (p / "Dockerfile").exists() or (p / "docker-compose.yml").exists():
        detected_stack.append("Docker")
        recommended_rules.append("skill:docker-patterns")

    if any(p.glob("*.db")) or any(p.glob("*.sqlite*")):
        detected_stack.append("SQLite")
        recommended_rules.append("skill:sqlite-database-expert")

    return {
        "path": str(p),
        "detected_technologies": detected_stack or ["Unknown / General"],
        "governance_rules": list(dict.fromkeys(recommended_rules)),
    }

@mcp.tool()
def verify_code_rules(code_content: str, language: str) -> Dict[str, Any]:
    violations = []
    lines = code_content.splitlines()
    lang = language.lower().strip()

    for idx, line in enumerate(lines):
        l_num = idx + 1
        s = line.strip()

        if lang in ("rust", "rs"):
            if ".unwrap()" in s:
                violations.append({"line": l_num, "rule": "err-no-unwrap-prod", "severity": "CRITICAL", "message": "Prohibited .unwrap() in production Rust. Propagate with ? or handle gracefully."})
            if ".expect(" in s:
                violations.append({"line": l_num, "rule": "err-no-unwrap-prod", "severity": "CRITICAL", "message": "Prohibited .expect() in production Rust. Propagate with ? or handle gracefully."})
            if "#![allow(" in s or "#[allow(" in s:
                violations.append({"line": l_num, "rule": "no-allow-warnings", "severity": "HIGH", "message": "Suppressed compiler warning detected. Fix the underlying root cause."})
            if "unbounded_channel" in s:
                violations.append({"line": l_num, "rule": "async-bounded-channel", "severity": "CRITICAL", "message": "Banned unbounded channel. Use bounded mpsc::channel(cap) with backpressure."})

        elif lang in ("go", "golang"):
            if "_ = " in s and ("err" in s or "error" in s):
                violations.append({"line": l_num, "rule": "go-error-discipline", "severity": "CRITICAL", "message": "Silenced error with blank identifier `_ = err`. Always handle errors explicitly."})

        elif lang in ("python", "py"):
            if re.search(r"except\s*:\s*pass", s) or re.search(r"except\s+Exception\s*:\s*pass", s):
                violations.append({"line": l_num, "rule": "anti-empty-catch", "severity": "CRITICAL", "message": "Empty except/pass block silences runtime errors. Log or handle explicitly."})

        if re.search(r"//\s*(TODO|FIXME|hack|temporary)", s, re.I) or re.search(r"#\s*(TODO|FIXME|hack|temporary)", s, re.I):
            violations.append({"line": l_num, "rule": "code_integrity", "severity": "HIGH", "message": "TODO/FIXME placeholder detected. Complete execution required."})

    return {
        "status": "FAILED" if any(v["severity"] == "CRITICAL" for v in violations) else "PASSED",
        "violations_count": len(violations),
        "violations": violations,
    }

@mcp.tool()
def list_skills_overview(category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_conn()
    query = "SELECT id, name, category, language, quality_score, source_tier, description, content FROM items WHERE item_type = 'skill'"
    params = []
    if category:
        query += " AND category = ?"
        params.append(category)
    query += " ORDER BY quality_score DESC LIMIT ?"
    params.append(limit)

    cur = conn.execute(query, params)
    results = []
    for row in cur.fetchall():
        results.append({
            "id": row[0],
            "name": row[1],
            "category": row[2],
            "language": row[3],
            "quality_score": row[4],
            "tier": row[5],
            "description": clean_description(row[6], row[7], max_len=120),
        })
    return results

@mcp.tool()
def list_rules_overview(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_conn()
    cur = conn.execute("SELECT id, name, language, quality_score, source_tier, description, content FROM items WHERE item_type = 'rule' ORDER BY quality_score DESC LIMIT ?", (limit,))
    results = []
    for row in cur.fetchall():
        results.append({
            "id": row[0],
            "name": row[1],
            "language": row[2],
            "quality_score": row[3],
            "tier": row[4],
            "description": clean_description(row[5], row[6], max_len=120),
        })
    return results

@mcp.tool()
def read_skill_resource_file(skill_name: str, relative_path: str) -> str:
    conn = get_db_conn()
    cur = conn.execute("SELECT path FROM items WHERE item_type = 'skill' AND (name = ? OR id = ?) ORDER BY quality_score DESC LIMIT 1", (skill_name, f"skill:{skill_name}"))
    row = cur.fetchone()

    if not row:
        return f"Skill '{skill_name}' not found."

    skill_md = Path(row[0])
    target = (skill_md.parent / relative_path).resolve()

    if not target.exists() or not str(target).startswith(str(skill_md.parent)):
        return f"File '{relative_path}' not found in skill '{skill_name}'."

    return target.read_text(encoding="utf-8", errors="replace")

@mcp.tool()
def reload_skills_index() -> Dict[str, Any]:
    sync_all_directories(force=True)
    conn = get_db_conn()
    total = conn.execute("SELECT count(*) FROM items").fetchone()[0]
    skills_count = conn.execute("SELECT count(*) FROM items WHERE item_type = 'skill'").fetchone()[0]
    rules_count = conn.execute("SELECT count(*) FROM items WHERE item_type = 'rule'").fetchone()[0]
    high_quality = conn.execute("SELECT count(*) FROM items WHERE quality_score >= 70").fetchone()[0]
    return {
        "status": "RELOADED",
        "total_items": total,
        "skills_count": skills_count,
        "rules_count": rules_count,
        "high_quality_items": high_quality,
    }

def main():
    mcp.run()

if __name__ == "__main__":
    main()
