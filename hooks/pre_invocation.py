#!/usr/bin/env python3
import json
import sqlite3
import os
import sys
import time
import re
from pathlib import Path

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

CONCEPT_MAP = {
    "زر": ["button", "telegram_button_styling", "inline_keyboard"],
    "ازرار": ["button", "telegram_button_styling", "inline_keyboard"],
    "دكم": ["button", "telegram_button_styling"],
    "بوت": ["telegram", "bot", "telego", "teloxide"],
    "تلكرام": ["telegram", "bot", "inline_keyboard"],
    "تيليجرام": ["telegram", "bot", "inline_keyboard"],
    "تليجرام": ["telegram", "bot", "inline_keyboard"],
    "تصميم": ["better-ui", "better-typography", "arabic-design", "anti_ai_design"],
    "واجهه": ["better-ui", "telegram-mini-app", "better-typography"],
    "واجهة": ["better-ui", "telegram-mini-app", "better-typography"],
    "خط": ["better-typography", "arabic-design"],
    "ايقونات": ["better-icons", "better-ui"],
    "ذاكره": ["rust-performance-memory", "jemalloc", "alloc_metrics", "memory"],
    "ذاكرة": ["rust-performance-memory", "jemalloc", "alloc_metrics", "memory"],
    "رام": ["rust-performance-memory", "jemalloc", "zero-ram"],
    "ضغط": ["simulate_telegram_load", "load", "concurrency"],
    "محاكاه": ["simulate_telegram_load", "simulation"],
    "محاكاة": ["simulate_telegram_load", "simulation"],
    "ويب هوك": ["webhook-automation", "webhook", "axum"],
    "هوك": ["webhook-automation", "webhook"],
    "رست": ["rust-standards", "rust-skills", "rust-patterns", "tokio"],
    "روست": ["rust-standards", "rust-skills", "rust-patterns", "tokio"],
    "قانون": ["no_lazy_fallbacks", "rust_standards", "governance"],
    "قواعد": ["no_lazy_fallbacks", "rust_standards", "governance"],
    "حوكمه": ["governance", "code_integrity", "honest_engineering"],
    "حوكمة": ["governance", "code_integrity", "honest_engineering"],
    "مكتبه": ["dependency_hygiene", "cargo-workflows"],
    "مكتبة": ["dependency_hygiene", "cargo-workflows"],
    "تست": ["rust-testing", "clean-code"],
    "اختبار": ["rust-testing", "clean-code"],
    "امان": ["security_hygiene", "zero_trust"],
    "ثغره": ["security_hygiene", "sql"],
    "ثغرة": ["security_hygiene", "sql"],
    "مهاره": ["skills-engine", "synthesize_and_learn_skill"],
    "مهارة": ["skills-engine", "synthesize_and_learn_skill"],
    "mcp": ["mcp", "skills-engine", "tools"],
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

def route_intent(prompt: str, db_path: str):
    if not prompt or not os.path.exists(db_path):
        return [], []

    norm = clean_query_text(prompt)
    stems = extract_stems(norm)

    keywords = set()
    for s in stems:
        if s in CONCEPT_MAP:
            keywords.update(CONCEPT_MAP[s])

    en_tokens = re.findall(r"[a-zA-Z0-9_-]+", prompt)
    for tok in en_tokens:
        if len(tok) > 2:
            keywords.add(tok.lower())

    if not keywords:
        return [], []

    fts_terms = [f'"{k}"*' for k in list(keywords)[:8]]
    fts_query = " OR ".join(fts_terms)

    try:
        conn = sqlite3.connect(db_path, timeout=0.5)
        cur = conn.cursor()
        cur.execute("""
            SELECT items.name, items.item_type
            FROM items_fts
            JOIN items ON items.id = items_fts.id
            WHERE items_fts MATCH ?
            ORDER BY rank
            LIMIT 12
        """, (fts_query,))
        rows = cur.fetchall()
        conn.close()

        skills = [r[0] for r in rows if r[1] == "skill"][:3]
        rules = [r[0] for r in rows if r[1] == "rule"][:2]
        return skills, rules
    except Exception:
        return [], []

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
        pinned_skills.extend(["telegram-bot", "rust-skills"])
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
    matched_skills, matched_rules = route_intent(prompt, db_path)

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

    msg = (
        f"⚡ [skills-engine Active] Workspace: {stack_desc}. "
        f"📌 Active Skills: [{skills_str}] | Active Rules: [{rules_str}]. "
        "Autonomous protocol: Zero skill/rule loss active. Inspect details via get_exact_skill / get_exact_rule."
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
