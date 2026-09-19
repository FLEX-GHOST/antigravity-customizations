#!/usr/bin/env python3
"""
Antigravity Pre-Invocation Context Injection Hook (2026 Autonomous Edition)
Intercepts user prompts in real-time, queries skills_index.db with FTS5 + BM25,
and injects the top matching skill instructions and active governance rules
directly into the LLM context.
"""
import json
import sqlite3
import os
import sys
import time
import re
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

def normalize_arabic(text: str) -> str:
    text = re.sub(r"[\u064B-\u065F\u0670\u0640]", "", text)
    text = re.sub(r"[أإآ]", "ا", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ؤ", "و", text)
    text = re.sub(r"ئ", "ي", text)
    text = re.sub(r"گ", "ك", text)
    text = re.sub(r"پ", "ب", text)
    text = re.sub(r"ڤ", "ف", text)
    text = re.sub(r"ژ", "ز", text)
    text = re.sub(r"چ", "ج", text)
    return text.lower()

def clean_query_text(text: str) -> str:
    t = normalize_arabic(text)
    t = re.sub(r"\b(ال|وال|بال|كال|لل|فال)([a-zA-Z\u0621-\u064A]+)", r"\2", t)
    t = re.sub(r"\b(تلقرام|تلغرام)\b", "تلكرام", t)
    t = re.sub(r"\b(روست)\b", "رست", t)
    return t

def extract_stems(norm_text: str) -> set:
    words = re.findall(r"[\u0621-\u064A]+", norm_text)
    stems = set(words)
    for w in words:
        for suf in ("ات", "ين", "ون", "ية", "ان", "هم", "هن", "كم", "نا", "ها", "ة", "ه", "ي"):
            if len(w) > len(suf) + 2 and w.endswith(suf):
                stems.add(w[:-len(suf)])
        for pref in ("وال", "فال", "بال", "كال", "لل", "ال"):
            if len(w) > len(pref) + 2 and w.startswith(pref):
                stems.add(w[len(pref):])
        for single in ("و", "ف", "ب", "ل"):
            if len(w) > len(single) + 2 and w.startswith(single):
                stems.add(w[len(single):])
    return stems

CONCEPT_MAP: Dict[str, List[str]] = {
    # UI & Styling
    "زر": ["button", "telegram_button_styling", "inline_keyboard", "design-button-hierarchy"],
    "ازرار": ["button", "telegram_button_styling", "inline_keyboard", "design-button-hierarchy"],
    "دكم": ["button", "telegram_button_styling"],
    "تصميم": ["better-ui", "better-typography", "arabic-design", "anti_ai_design"],
    "واجهه": ["better-ui", "telegram-mini-app", "better-typography"],
    "واجهة": ["better-ui", "telegram-mini-app", "better-typography"],
    "خط": ["better-typography", "arabic-design"],
    "ايقونات": ["better-icons", "better-ui"],
    "الوان": ["better-ui", "anti_ai_design"],
    "لون": ["better-ui", "anti_ai_design"],

    # Telegram
    "بوت": ["telegram", "bot", "teloxide", "telegram-bot-api-methods"],
    "تلكرام": ["telegram", "bot", "inline_keyboard", "telegram-bot-api-methods"],
    "تيليجرام": ["telegram", "bot", "inline_keyboard", "telegram-bot-api-methods"],
    "تليجرام": ["telegram", "bot", "inline_keyboard", "telegram-bot-api-methods"],
    "ميثود": ["telegram-bot-api-methods", "telegram", "botapi"],
    "ميثودات": ["telegram-bot-api-methods", "telegram", "botapi"],
    "دوال": ["telegram-bot-api-methods", "telegram", "botapi"],
    "ويب هوك": ["webhook-automation", "webhook", "axum"],
    "هوك": ["webhook-automation", "webhook"],
    "ميني": ["telegram-mini-app"],

    # Performance & Concurrency
    "ذاكره": ["rust-performance-memory", "jemalloc", "alloc_metrics", "memory"],
    "ذاكرة": ["rust-performance-memory", "jemalloc", "alloc_metrics", "memory"],
    "رام": ["rust-performance-memory", "jemalloc", "zero-ram"],
    "ضغط": ["simulate_telegram_load", "load", "concurrency"],
    "محاكاه": ["simulate_telegram_load", "simulation"],
    "محاكاة": ["simulate_telegram_load", "simulation"],

    # Rust & Systems
    "رست": ["rust-standards", "rust-skills", "rust-patterns", "tokio"],
    "روست": ["rust-standards", "rust-skills", "rust-patterns", "tokio"],
    "مكتبه": ["dependency_hygiene", "cargo-workflows"],
    "مكتبة": ["dependency_hygiene", "cargo-workflows"],

    # Architecture & Clean Code
    "معماريه": ["clean-architecture", "clean-code", "code_integrity"],
    "معمارية": ["clean-architecture", "clean-code", "code_integrity"],
    "كلين": ["clean-architecture", "clean-code"],
    "نظيف": ["clean-code", "clean-architecture"],
    "قانون": ["no_lazy_fallbacks", "rust_standards", "governance"],
    "قواعد": ["no_lazy_fallbacks", "rust_standards", "governance"],
    "حوكمه": ["governance", "code_integrity", "honest_engineering"],
    "حوكمة": ["governance", "code_integrity", "honest_engineering"],

    # Testing & Verification
    "تست": ["rust-testing", "clean-code", "cargo-workflows"],
    "اختبار": ["rust-testing", "clean-code", "cargo-workflows"],
    "فحص": ["code_integrity", "run_compiler_diagnostics"],
    "لينت": ["clean-code", "rust-skills"],

    # Cybersecurity & Reversing
    "امان": ["security_hygiene", "zero_trust", "cybersecurity"],
    "سيكيورتي": ["security_hygiene", "penetration-testing", "cybersecurity"],
    "ثغره": ["security_hygiene", "vulnerability-assessment", "sql-injection"],
    "ثغرة": ["security_hygiene", "vulnerability-assessment", "sql-injection"],
    "اختراق": ["penetration-testing", "reverse-engineering", "cybersecurity"],
    "تهكير": ["penetration-testing", "reverse-engineering", "cybersecurity"],
    "اندبوينت": ["api-reverse-engineering", "endpoint", "api-discovery"],
    "اندبوينتس": ["api-reverse-engineering", "endpoint", "api-discovery"],
    "نقطه": ["api-reverse-engineering", "endpoint"],
    "نقطة": ["api-reverse-engineering", "endpoint"],
    "اعلان": ["reverse-engineering-android-malware-with-jadx", "apktool"],
    "اعلانات": ["reverse-engineering-android-malware-with-jadx", "apktool"],
    "تطبيق": ["conducting-mobile-app-penetration-test", "apktool", "jadx"],
    "اندرويد": ["conducting-mobile-app-penetration-test", "apktool", "jadx"],
    "apk": ["reverse-engineering-android-malware-with-jadx", "analyzing-android-malware-with-apktool"],
    "endpoint": ["api-reverse-engineering", "api-endpoint-builder-v2"],
    "endpoints": ["api-reverse-engineering", "api-endpoint-builder-v2"],
    "jadx": ["reverse-engineering-android-malware-with-jadx"],
    "apktool": ["analyzing-android-malware-with-apktool"],
    "burp": ["burpsuite", "penetration-testing"],
    "sql": ["sql-injection", "database-security"],
    "xss": ["xss-prevention", "web-security"],
    "api": ["api-rate-limiting", "telegram-bot-api-methods"],
    "mcp": ["skills-engine", "tools", "mcp"],
    "مهاره": ["skills-engine", "synthesize_and_learn_skill"],
    "مهارة": ["skills-engine", "synthesize_and_learn_skill"],
}

TG_QUICK_DETECTION = {
    "sendmessage": "sendMessage",
    "sendphoto": "sendPhoto",
    "sendvideo": "sendVideo",
    "sendvoice": "sendVoice",
    "sendaudio": "sendAudio",
    "sendpaidmedia": "sendPaidMedia",
    "sendsticker": "sendSticker",
    "senddice": "sendDice",
    "banchatmember": "banChatMember",
    "unbanchatmember": "unbanChatMember",
    "restrictchatmember": "restrictChatMember",
    "promotechatmember": "promoteChatMember",
    "exportchatinvitelink": "exportChatInviteLink",
    "createchatinvitelink": "createChatInviteLink",
    "pinchatmessage": "pinChatMessage",
    "answercallbackquery": "answerCallbackQuery",
    "inlinekeyboardbutton": "InlineKeyboardButton",
    "inlinekeyboardmarkup": "InlineKeyboardMarkup",
    "setwebhook": "setWebhook",
    "getupdates": "getUpdates",
    "getme": "getMe",
    "حظر": "banChatMember",
    "طرد": "banChatMember",
    "كتم": "restrictChatMember",
    "تقييد": "restrictChatMember",
    "ازرار": "InlineKeyboardButton (style: primary/success/danger)",
    "كيبورد": "InlineKeyboardMarkup",
    "رابط دعوة": "createChatInviteLink",
    "نجوم": "sendPaidMedia (Telegram Stars)",
    "هدية": "sendGift",
    "ويب هوك": "setWebhook / Axum router",
    "ميثود": "Telegram Bot API 10.3 (185 methods)",
}

def extract_latest_user_prompt(transcript_path: str) -> str:
    if not transcript_path or not os.path.exists(transcript_path):
        return ""
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            buffer_size = min(262144, size)
            f.seek(-buffer_size, 2)
            tail = f.read().decode("utf-8", errors="ignore")

        for line in reversed(tail.splitlines()):
            try:
                data = json.loads(line)
                if data.get("type") == "USER_INPUT":
                    content = data.get("content", "")
                    m = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", content, re.DOTALL)
                    if m:
                        return m.group(1).strip()
                    return content.strip()
            except Exception:
                pass
    except Exception:
        pass
    return ""

def clean_skill_instructions(raw_content: str, max_chars: int = 950) -> str:
    if not raw_content:
        return ""
    text = re.sub(r"^---\n.*?\n---\n", "", raw_content, flags=re.DOTALL).strip()
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL).strip()
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    cleaned = "\n".join(lines)
    if len(cleaned) > max_chars:
        return cleaned[:max_chars].rsplit("\n", 1)[0] + "\n..."
    return cleaned

def route_intent_with_content(prompt: str, db_path: str) -> Dict[str, Any]:
    res = {
        "matched_skills": [],
        "matched_rules": [],
        "top_skill_content": None,
        "top_skill_name": None,
        "top_skill_quality": None,
        "top_skill_tier": None,
    }
    if not prompt or not os.path.exists(db_path):
        return res

    norm = clean_query_text(prompt)
    stems = extract_stems(norm)

    keywords = set()
    for s in stems:
        if s in CONCEPT_MAP:
            keywords.update(CONCEPT_MAP[s])

    en_tokens = re.findall(r"[a-zA-Z0-9_-]+", prompt)
    for tok in en_tokens:
        tok_lower = tok.lower()
        if len(tok_lower) > 2:
            keywords.add(tok_lower)
            if tok_lower in CONCEPT_MAP:
                keywords.update(CONCEPT_MAP[tok_lower])

    if not keywords:
        return res

    fts_terms = [f'"{k}"*' for k in list(keywords)[:10]]
    fts_query = " OR ".join(fts_terms)

    try:
        conn = sqlite3.connect(db_path, timeout=0.5)
        cur = conn.cursor()
        cur.execute("""
            SELECT items.name, items.item_type, items.quality_score, items.source_tier, items.content, items.description
            FROM items_fts
            JOIN items ON items.id = items_fts.id
            WHERE items_fts MATCH ?
            ORDER BY rank
            LIMIT 10
        """, (fts_query,))
        rows = cur.fetchall()
        conn.close()

        for r in rows:
            name, item_type, q_score, tier, raw_content, desc = r
            if item_type == "skill":
                if not res["top_skill_name"]:
                    res["top_skill_name"] = name
                    res["top_skill_quality"] = q_score
                    res["top_skill_tier"] = tier
                    res["top_skill_content"] = clean_skill_instructions(raw_content)
                if name not in res["matched_skills"]:
                    res["matched_skills"].append(name)
            elif item_type == "rule":
                if name not in res["matched_rules"]:
                    res["matched_rules"].append(name)
    except Exception:
        pass

    return res

def detect_telegram_method(prompt: str) -> Optional[str]:
    p_lower = prompt.lower()
    for trigger, target in TG_QUICK_DETECTION.items():
        if trigger in p_lower:
            return target
    return None

def main():
    try:
        raw_input = sys.stdin.read()
        payload = json.loads(raw_input) if raw_input.strip() else {}
    except Exception:
        payload = {}

    workspaces = payload.get("workspacePaths", [])
    ws = Path(workspaces[0]) if workspaces else Path("/root/bots/factory")
    stack_items = []
    pinned_rules = []
    pinned_skills = []

    if (ws / "Cargo.toml").exists():
        stack_items.append("Rust (Telegram Factory Core)")
        pinned_rules.extend(["rust_standards", "no_lazy_fallbacks", "telegram_button_styling"])
        pinned_skills.extend(["telegram-bot", "telegram-bot-api-methods", "rust-skills"])
    if (ws / "package.json").exists():
        stack_items.append("Node.js/React (Frontend)")
        pinned_rules.append("anti_ai_design")
        pinned_skills.append("better-ui")
    if (ws / "go.mod").exists():
        stack_items.append("Go (Microservices)")
    if (ws / "pyproject.toml").exists() or (ws / "requirements.txt").exists():
        stack_items.append("Python (Daemon/AI)")

    stack_desc = ", ".join(stack_items) if stack_items else "General Polyglot"

    transcript_path = payload.get("transcriptPath", "")
    db_path = os.path.expanduser("~/.gemini/mcp-servers/skills-engine/skills_index.db")

    prompt = extract_latest_user_prompt(transcript_path)
    route_data = route_intent_with_content(prompt, db_path)

    matched_skills = route_data["matched_skills"]
    matched_rules = route_data["matched_rules"]
    top_skill_name = route_data["top_skill_name"]
    top_skill_content = route_data["top_skill_content"]
    top_skill_q = route_data["top_skill_quality"]
    top_skill_tier = route_data["top_skill_tier"]

    active_skills_set = []
    for s in pinned_skills + matched_skills:
        if s not in active_skills_set:
            active_skills_set.append(s)

    active_rules_set = []
    for r in pinned_rules + matched_rules:
        if r not in active_rules_set:
            active_rules_set.append(r)

    skills_str = ", ".join(active_skills_set[:4])
    rules_str = ", ".join(active_rules_set[:4])

    detected_tg = detect_telegram_method(prompt)
    tg_banner = f" | 🎯 Telegram Target: [{detected_tg}]" if detected_tg else ""

    if top_skill_name and top_skill_content:
        msg = (
            f"⚡ [skills-engine Active Context Injection]\n"
            f"🎯 Matched Skill: `{top_skill_name}` (Quality: {top_skill_q}%, Tier: {top_skill_tier})\n"
            f"📋 Procedural Guidance:\n"
            f"{top_skill_content}\n\n"
            f"📌 Active Governance Invariants: [{rules_str}]{tg_banner}\n"
            f"💡 Quick Tools: get_exact_skill(name='{top_skill_name}') | get_telegram_bot_api_spec(query='...')"
        )
    else:
        msg = (
            f"⚡ [skills-engine Active] Workspace: {stack_desc}. "
            f"📌 Active Skills: [{skills_str}] | Active Rules: [{rules_str}]{tg_banner}. "
            "Autonomous protocol: Use get_telegram_bot_api_spec(query='...') or search_agent_capabilities(query='...')."
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
