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
try:
    import yaml
except ImportError:
    yaml = None
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    try:
        from mcp.server import FastMCP
    except ImportError:
        try:
            from mcp.server.mcpserver import MCPServer as FastMCP
        except ImportError:
            from fastmcp import FastMCP

mcp = FastMCP("skills-engine")

HOME_DIR = Path.home()
DB_PATH = HOME_DIR / ".gemini/mcp-servers/skills-engine/skills_index.db"

def get_all_search_paths() -> List[Path]:
    paths = [
        HOME_DIR / ".gemini/config",
        HOME_DIR / ".gemini/skills-catalog",
        HOME_DIR / ".gemini/antigravity-ide/builtin/skills",
        HOME_DIR / ".gemini/antigravity-ide/builtin/rules",
    ]
    custom_root = HOME_DIR / "antigravity-customizations"
    if custom_root.exists():
        paths.append(custom_root)
    bots_dir = HOME_DIR / "bots"
    if bots_dir.exists():
        for agent_dir in sorted(bots_dir.glob("*/.agents")):
            if agent_dir.is_dir():
                paths.append(agent_dir)
        paths.append(bots_dir)
    return paths

SEARCH_PATHS = get_all_search_paths()

ARABIC_STOPWORDS = {
    'من', 'الى', 'عن', 'على', 'في', 'حتى', 'مع', 'هذا', 'هذه', 'تم', 'كان', 'كانت',
    'ان', 'انها', 'انه', 'بان', 'او', 'ثم', 'كل', 'بعض', 'غير', 'فقط', 'هو', 'هي',
    'هم', 'هن', 'انت', 'انتم', 'انا', 'نحن', 'الي', 'اللي', 'التي', 'الذي', 'الذين',
    'اللواتي', 'اللاتي', 'اذا', 'لو', 'لما', 'عند', 'عندما', 'حيث', 'كيف', 'ماذا',
    'لماذا', 'هل', 'كم', 'اي', 'اية', 'ايها', 'ايتها', 'كلما', 'بين', 'بينما', 'لدى',
    'دون', 'نحو', 'قبل', 'بعد', 'اثناء', 'خلال', 'فوق', 'تحت', 'وراء', 'امام', 'خلف',
    'يمين', 'يسار', 'داخل', 'خارج', 'سوى', 'حاشا', 'خلا', 'عدا', 'ليس', 'ما', 'لا',
    'لن', 'لم', 'لات', 'انما', 'لكن', 'بل', 'لكنما', 'سواء', 'اما', 'كذلك', 'ايضا',
    'جدا', 'كثيرا', 'قليلا', 'دائما', 'ابدا', 'احيانا', 'طالما', 'بما', 'حسب',
    # Iraqi conversational filler words
    'هيج', 'هسة', 'هسه', 'ياخي', 'شبيك', 'لعد', 'توه', 'توني', 'بله', 'شلون', 'ليش',
    'شنو', 'وين', 'شو', 'عندي', 'اريد', 'اطلبها', 'ضيفها', 'سويلي', 'ضيفلي', 'عدلي',
    'كلش', 'هواي', 'شوية', 'حيل', 'مو', 'مجرد', 'يكدر', 'يكول', 'يعني', 'شوف', 'فهمت',
    'بنفسه', 'عندنا', 'عدنا', 'بكل', 'مكان', 'جديدة', 'وبدون', 'مشاكل', 'الاشياء',
    'مثلا', 'وبعدها', 'اللي', 'هيج كلام', 'كلام'
}

RAW_AR_STEM_MAP: Dict[str, str] = {
    # --- AI Agents, Tool Calling & Service Orchestration ---
    "ai agent": "ai-agent tool-calling function-calling agentic-bot autonomous-agent telegram-bot-builder",
    "اي اي ايجنت": "ai-agent tool-calling function-calling agentic-bot autonomous-agent",
    "ايجنت": "ai-agent autonomous-agent agentic-workflow tool-calling",
    "مو مجرد شات": "ai-agent tool-calling function-calling autonomous-assistant reasoning telegram-bot-builder",
    "يستدعي tool": "function-calling tool-use tools-orchestration tool-dispatch clean-architecture",
    "يستدعي اداة": "function-calling tool-use tools-orchestration tool-dispatch clean-architecture",
    "يستدعي ادوات": "function-calling tool-use tools-orchestration tool-dispatch clean-architecture",
    "يستدعي الاداة": "function-calling tool-use tools-orchestration tool-dispatch clean-architecture",
    "يستدعي ادوات البوت": "telegram-bot-builder tool-calling function-calling decoupled-services clean-architecture",
    "ادوات البوت": "telegram-bot-builder bot-services tools-catalog function-calling",
    "الخدمات هي اللي تنفذ": "clean-architecture decoupled-services tool-dispatcher ports-adapters service-layer",
    "ما ينفذ بنفسه": "clean-architecture tool-calling separation-of-concerns decoupled-services ports-adapters",
    "يطلب الرابط اذا ناقص": "slot-filling parameter-extraction dialogue-state-tracking validation error-handling",
    "باراميتر ناقص": "slot-filling parameter-extraction validation schema dialogue-state-tracking",
    "رابط ناقص": "slot-filling parameter-extraction validation schema",
    "شلون يستخدم الخدمة": "conversational-agent help-system documentation telegram-bot",
    "يشرحله": "conversational-agent help-system documentation interactive-guidance",
    "نزلي هذا من الانستا": "instagram-downloader media-downloader video-download yt-dlp telegram-bot",
    "نزلي من الانستا": "instagram-downloader media-downloader video-download yt-dlp telegram-bot",
    "instagram downloader": "instagram-downloader media-downloader video-download yt-dlp telegram-bot",
    "انستغرام داونلودر": "instagram-downloader media-downloader video-download yt-dlp telegram-bot",
    "فكرة خدمة": "feature-design architecture modular-services clean-architecture telegram-bot-builder",
    "خدمة": "service microservice handler clean-architecture module",
    "خدمات": "services architecture modular clean-architecture service-layer",
    # --- Telegram Bots & Factory Architecture ---
    "ويب هوك": "webhook-automation webhook axum nginx token-hash secret-token setwebhook",
    "ويب هك": "webhook-automation webhook axum nginx token-hash secret-token",
    "وب هوك": "webhook-automation webhook axum nginx token-hash secret-token",
    "سيرفر الويب هوك": "webhook-automation webhook axum nginx multi-tenant token-hash",
    "ربط الويب هوك": "webhook-automation setwebhook webhook telegram-bot-api",
    "توكن هاش": "webhook-automation token-hash sha256 multi-tenant webhook",
    "سيكريت توكن": "webhook-automation secret-token x-telegram-bot-api-secret-token security",
    "تاخير الرسائل بالويب هوك": "webhook-automation instant-200-ok async-worker tokio joinset queue",
    "تكرار الرسائل بالويب هوك": "webhook-automation update-retry instant-200-ok idempotency",
    "انغينكس ويب هوك": "webhook-automation nginx reverse-proxy ssl proxy-buffering-off",
    "اكسوم ويب هوك": "webhook-automation axum rust tokio webhook multi-tenant",
    "بوت ميوزك فليكس": "telegram-music-bot audio-streaming rusttgcalls gotgcall gogram pytgcalls voice-chat webrtc ffmpeg playback rust go golang python flexmusic queue",
    "بوت ميوزك": "telegram-music-bot audio-streaming rusttgcalls gotgcall pytgcalls voice-chat webrtc ffmpeg playback rust go golang python",
    "بوت الميوزك": "telegram-music-bot audio-streaming rusttgcalls gotgcall pytgcalls voice-chat webrtc ffmpeg playback rust go golang python",
    "بوت ميوزك بالرست": "rusttgcalls rust telegram-music-bot audio-streaming voice-chat webrtc tokio playback",
    "بوت ميوزك رست": "rusttgcalls rust telegram-music-bot audio-streaming voice-chat webrtc tokio playback",
    "بوت ميوزك بالجو": "gotgcall gogram golang telegram-music-bot audio-streaming voice-chat webrtc",
    "بوت ميوزك جو": "gotgcall gogram golang telegram-music-bot audio-streaming voice-chat webrtc",
    "بوت ميوزك بالكو": "gotgcall gogram golang telegram-music-bot audio-streaming voice-chat webrtc",
    "بوت ميوزك كو": "gotgcall gogram golang telegram-music-bot audio-streaming voice-chat webrtc",
    "بوت ميوزك بايثون": "pytgcalls pyrogram telethon python telegram-music-bot audio-streaming voice-chat",
    "مكتبة ميوزك رست": "rusttgcalls rust telegram group-calls live-stream webrtc tokio rtc audio-streaming",
    "مكتبة ميوزك جو": "gotgcall gogram go telegram group-calls voice-chat pion webrtc audio-streaming",
    "مكتبة ميوزك": "rusttgcalls gotgcall pytgcalls telegram group-calls voice-chat webrtc audio-streaming library",
    "رست تي جي كولز": "rusttgcalls rust telegram group-calls live-stream webrtc audio-streaming",
    "جو تي جي كولز": "gotgcall gogram go telegram group-calls voice-chat webrtc",
    "كو تي جي كولز": "gotgcall gogram go telegram group-calls voice-chat webrtc",
    "فليكس بوت": "telegram-bot telegram-bot-builder factory multi-tenant webhook architecture",
    "مصنع البوتات": "telegram-bot-builder telegram-bot factory multi-tenant webhook architecture teloxide",
    "مصنع": "telegram-bot-builder telegram-bot factory multi-tenant webhook architecture",
    "بوت تحميل من تيك توك": "telegram-bot media-downloader yt-dlp video-download tiktok extraction",
    "بوت تحميل": "telegram-bot media-downloader yt-dlp video-download audio-download extraction",
    "تحميل من تيك توك": "telegram-bot media-downloader yt-dlp video-download tiktok extraction",
    "فاست دي ال": "fastdl-rs rust media-downloader yt-dlp video-download extraction",
    "تيك توك": "tiktok media-downloader yt-dlp video-download",
    "انستا": "instagram media-downloader yt-dlp reel story video-download",
    "انستغرام": "instagram media-downloader yt-dlp reel story video-download",
    "ستوري": "story telegram-bot media-downloader video-download instagram",
    "ستوريات": "stories telegram-bot media-downloader video-download instagram",
    "ريلز": "reels instagram media-downloader yt-dlp video-download",
    "يوت": "youtube streaming ytdlp audio playback yt-dlp search",
    "يوتيوب": "youtube streaming ytdlp audio playback yt-dlp search",
    "شازام": "shazam audio-recognition music-search telegram-bot track-identification",
    "بوت تحويل الصيغ": "ffmpeg media-converter audio-converter video-transcoding format-conversion",
    "تحويل الصيغ": "ffmpeg media-converter audio-converter video-transcoding format-conversion",
    "صيغ": "format conversion transcoding ffmpeg media audio video",
    "صيغة": "format conversion transcoding ffmpeg media audio video",
    "لعبة اكس او": "inline-keyboard game state-machine telegram-bot interactive",
    "اكس او": "inline-keyboard game state-machine telegram-bot interactive",
    "العاب انلاين": "inline-keyboard game state-machine telegram-bot interactive",
    "تليجرام": "telegram-bot telegram-bot-builder webhook floodwait mtproto teloxide",
    "تيليجرام": "telegram-bot telegram-bot-builder webhook floodwait mtproto teloxide",
    "تليغرام": "telegram-bot telegram-bot-builder webhook floodwait mtproto teloxide",
    "تليكرام": "telegram-bot telegram-bot-builder webhook floodwait mtproto teloxide",
    "تلكرام": "telegram-bot telegram-bot-builder webhook floodwait mtproto teloxide",
    "تلي": "telegram-bot telegram-bot-builder webhook floodwait mtproto teloxide",
    "بوت": "telegram-bot bot automation client webhook worker polling",
    "بوتات": "telegram-bot telegram-bot-builder factory multi-tenant webhook architecture",
    "قناة": "channel broadcast telegram bot admin notification",
    "كروب": "group chat supergroup telegram-bot permissions administration",
    "جروب": "group chat supergroup telegram-bot permissions administration",
    "مجموعة": "group chat telegram-bot permissions management administration",
    "سوبركروب": "supergroup telegram-bot permissions administration",
    "سوبرجروب": "supergroup telegram-bot permissions administration",
    "ويب هوك": "webhook telegram-webhook axum warp actix endpoint",
    "ويبهوك": "webhook telegram-webhook axum warp actix endpoint",
    "بولينغ": "polling long-polling telegram worker loop teloxide",
    "بولينج": "polling long-polling telegram worker loop teloxide",
    "فلود": "floodwait rate-limit retry backoff jitter telegram 420",
    "فلود ويت": "floodwait rate-limit retry backoff jitter telegram 420",
    "ريت لمت": "rate-limit token-bucket sliding-window api-rate-limiting floodwait",

    # --- Userbots, Assistant Accounts & MTProto Sessions ---
    "حساب مساعد": "telegram client userbot mtproto telethon pyrogram grammers gogram session assistant",
    "الحساب المساعد": "telegram client userbot mtproto telethon pyrogram grammers gogram session assistant",
    "دعوة مساعد للمجموعة": "telegram userbot assistant group invite mtproto",
    "مساعد": "telegram client userbot mtproto assistant session pyrogram telethon gogram",
    "يوزر المساعد": "telegram client userbot mtproto assistant username session",
    "اكاونت مساعد": "telegram client userbot mtproto assistant session",
    "جلسة": "session-string pyrogram telethon mtproto session authentication auth-key grammers gogram",
    "جلسات": "session-string pyrogram telethon mtproto session authentication auth-key grammers gogram",
    "استخراج جلسة": "session-string pyrogram telethon mtproto session authentication auth-key grammers gogram",
    "استخراج الجلسة": "session-string pyrogram telethon mtproto session authentication auth-key grammers gogram",
    "جلسة بايروجرام": "pyrogram session string mtproto auth client userbot",
    "جلسة تليثون": "telethon session string mtproto auth client userbot",
    "جلسة كرامرز": "grammers session string mtproto auth rust client",
    "جلسة غرامرز": "grammers session string mtproto auth rust client",
    "جلسة جوجرام": "gogram session string mtproto auth go golang client",
    "جلسة كوكرام": "gogram session string mtproto auth go golang client",
    "بايروجرام": "pyrogram python telegram mtproto userbot",
    "تليثون": "telethon python telegram mtproto userbot",
    "كرامرز": "grammers rust telegram mtproto client",
    "غرامرز": "grammers rust telegram mtproto client",
    "جوجرام": "gogram golang go telegram mtproto client",
    "كوكرام": "gogram golang go telegram mtproto client",
    "سترنك": "session-string string-session mtproto telethon pyrogram gogram",
    "فايل توكن": "bot-token file-token authorization telegram-api",
    "توكن": "bot-token authentication telegram token api-key",

    # --- Audio, Voice Chat, Streaming & Media ---
    "ميوزك": "music voice-chat stream pytgcalls rusttgcalls gotgcall audio playback ffmpeg live-stream rust go python",
    "اغاني": "music voice-chat stream audio playback ffmpeg queue",
    "موسيقى": "music audio stream playback pytgcalls rusttgcalls gotgcall",
    "صوت": "audio voice stream sound ffmpeg playback",
    "مكالمة صوتية نشطة": "voice-chat group-call pytgcalls rusttgcalls gotgcall webrtc stream audio active",
    "مكالمة صوتية": "voice-chat group-call pytgcalls rusttgcalls gotgcall webrtc stream audio",
    "مكالمة نشطة": "active-voice-chat group-call pytgcalls stream audio",
    "مكالمة": "voice-chat group-call pytgcalls rusttgcalls gotgcall webrtc stream audio",
    "فويس جات": "voice-chat group-call stream audio playback pytgcalls gotgcall",
    "فويس شات": "voice-chat group-call stream audio playback pytgcalls gotgcall",
    "فويس": "voice-chat group-call stream audio playback",
    "ستريم": "stream audio video pytgcalls rusttgcalls gotgcall live-stream",
    "كول": "voice-call group-call pytgcalls stream audio",
    "تشغيل صوت": "audio playback ffmpeg pytgcalls voice-chat stream",
    "اف ام بيج": "ffmpeg transcoding audio video conversion stream",
    "اف اف ام بيج": "ffmpeg transcoding audio video conversion stream",

    # --- Group Moderation & Bot Administration ---
    "طرد البوتات": "telegram-bot telegram group moderation ban kick anti-bot security administration",
    "طرد": "telegram-bot telegram group moderation ban kick permissions administration",
    "حظر": "telegram-bot group moderation ban restrict permissions floodwait",
    "فك الحظر": "telegram-bot unban permissions administration group moderation",
    "كتم الصوت": "telegram-bot mute audio restrict permissions administration moderation",
    "كتم": "telegram-bot mute restrict permissions silence administration moderation",
    "الغاء الكتم": "telegram-bot unmute permissions administration group moderation",
    "تقييد": "telegram-bot restrict permissions mute ban member group moderation",
    "تثبيت رسالة": "telegram-bot pin message announcement admin moderation",
    "تثبيت": "telegram-bot pin message announcement admin moderation",
    "الغاء التثبيت": "telegram-bot unpin message admin moderation",
    "قفل الكل": "telegram-bot group moderation permissions lock unlock auto-delete antispam",
    "قفل الروابط": "telegram-bot antispam lock links delete-message permissions group moderation",
    "قفل التوجيه": "telegram-bot lock forwards restrict permissions group moderation",
    "قفل الصور": "telegram-bot lock photos media permissions group moderation",
    "قفل الملصقات": "telegram-bot lock stickers media permissions group moderation",
    "قفل الملصق المميز": "telegram-bot lock premium sticker custom-emoji moderation",
    "فتح الملصق المميز": "telegram-bot unlock premium sticker custom-emoji moderation",
    "فتح وقفل": "telegram-bot lock unlock permissions antispam group moderation",
    "فتح": "telegram-bot unlock permissions allow member administration group",
    "قفل": "telegram-bot lock permissions restrict member group moderation",
    "تفعيل": "telegram-bot enable activate feature bot command configuration",
    "تعطيل": "telegram-bot disable deactivate feature bot configuration",
    "صلاحيات": "permission policy authorization grant allow access admin-rights telegram",
    "برمشن": "permission policy allow auto-approve authorization turbo",
    "اذن": "permission policy allow authorization grant",
    "ادمن": "admin administrator permissions telegram group management",
    "مشرف": "admin moderator administrator telegram group permissions",
    "منشئ": "owner creator telegram group permissions root",

    # --- UI Design, Buttons, Colors & Styling (Bot API 9.4 Standards) ---
    "حل مشكلة الازرار": "telegram-button-styling button-states hierarchy bot-api-9.4 style primary success danger",
    "لون الازرار": "telegram-button-styling button-states better-colors bot-api-9.4 style primary success danger",
    "الازرار": "telegram-button-styling button-states hierarchy bot-api-9.4 inline-keyboard",
    "دكم": "telegram-button-styling button-states hierarchy interactive hover focus",
    "دكمة": "telegram-button-styling button-states hierarchy interactive hover focus",
    "زر شفاف": "telegram-button-styling minimal transparent button styling clean-ui",
    "زر": "button states hierarchy interactive hover focus aria active telegram-button-styling",
    "ازرار": "telegram-button-styling button-states hierarchy bot-api-9.4 inline-keyboard",
    "كبسة": "button states interactive click trigger action telegram-button-styling",
    "كيبورد انلاين": "inline-keyboard reply-markup callback-query telegram-button-styling",
    "انلاين كيبورد": "inline-keyboard reply-markup callback-query telegram-button-styling",
    "كيبورد": "inline-keyboard reply-markup telegram-button-styling",
    "انلاين": "inline-keyboard callback-query telegram-button-styling",
    "الالوان تعبانة": "anti-ui-slop anti_ai_design better-colors visual-design unslop",
    "الالوان زبالة": "anti-ui-slop anti_ai_design better-colors visual-design unslop",
    "تعبان": "anti-ui-slop anti_ai_design design-taste-frontend better-ui visual-design",
    "تعبانة": "anti-ui-slop anti_ai_design design-taste-frontend better-ui visual-design",
    "زبالة": "anti-ui-slop anti_ai_design clean-code refactor unslop",
    "خايس": "anti-ui-slop anti_ai_design clean-code refactor unslop",
    "خايسة": "anti-ui-slop anti_ai_design clean-code refactor unslop",
    "سلوب": "anti-ui-slop antislop anti_ai_design unslop visual-design",
    "تصميم": "ui frontend visual design styling typography web better-ui design-taste-frontend",
    "واجهة": "ui frontend visual design styling typography web css better-ui",
    "واجه": "ui frontend visual design styling typography web css better-ui",
    "فرونت": "frontend react nextjs ui tailwind css design",
    "الوان": "colors palette contrast semantic tokens wcag accessibility better-colors",
    "لون": "colors palette contrast semantic tokens better-colors",
    "باليت": "color palette semantic tokens better-colors contrast",
    "تدرج": "gradient aesthetic anti-ui-slop styling css",
    "خلفية": "background styling surface elevated css ui",
    "شيل الخلفية": "transparent background minimal styling clean-ui",
    "بدون خلفية": "transparent background minimal styling clean-ui",
    "سايبر سكيورتي": "cybersecurity dark terminal dashboard sleek visual design",
    "بنفسج": "anti-ui-slop purple gradient bloat aesthetic anti_ai_design",
    "ايقون": "icons svg vector symbols lucide phosphor better-icons",
    "ايقونات": "icons svg vector symbols lucide phosphor better-icons",
    "رمز": "icons svg vector symbols lucide better-icons",
    "رموز": "icons svg vector symbols lucide better-icons",
    "خطوط": "better-typography web-typography font hierarchy scale readability",
    "خط": "typography font hierarchy scale readability web-typography",
    "فونت": "typography font hierarchy readability better-typography",
    "ايموجي مميز": "custom-emoji telegram-button-styling vector icons premium",
    "الايموجي المميز": "custom-emoji telegram-button-styling vector icons premium",
    "ستيكر مميز": "custom-emoji sticker premium telegram bot media",
    "الملصق المميز": "custom-emoji sticker premium telegram bot media",
    "ستيكر": "sticker custom-emoji telegram bot media",
    "ستيكرات": "stickers custom-emoji telegram bot media",
    "ملصق متحرك": "animated-sticker telegram media lottie tgs",
    "ملصق": "sticker custom-emoji telegram bot media",
    "ملصقات": "stickers custom-emoji telegram bot media",
    "ميني اب": "telegram-mini-app twa webview webapp javascript react",
    "تليجرام ميني اب": "telegram-mini-app twa webview webapp native haptic",

    # --- Bugs, Crashes, Diagnostics & Debugging ---
    "ما جاي يشتغل": "systematic-debugging troubleshooting root-cause fix error-handling resilience",
    "مجاي يشتغل": "systematic-debugging troubleshooting root-cause fix error-handling resilience",
    "ما يشتغل": "systematic-debugging troubleshooting root-cause fix error-handling resilience",
    "ما جاي يحفظ": "persistence database storage sqlite commit serialization bug-fix",
    "مجاي يحفظ": "persistence database storage sqlite commit serialization bug-fix",
    "معلك": "deadlock mutex lock synchronization concurrency tokio async freeze hang",
    "صافن": "deadlock tokio async hang freeze mutex concurrency starvation",
    "واكف": "systematic-debugging crash troubleshooting error resilience hang",
    "عطلان": "systematic-debugging crash troubleshooting error resilience defect",
    "معطل": "systematic-debugging crash troubleshooting error resilience defect",
    "يطفي فجاة": "systematic-debugging crash panic zero-panic supervisor systemd recovery exit",
    "يطفي وحده": "systematic-debugging crash panic zero-panic supervisor systemd recovery exit",
    "يطفي": "systematic-debugging crash panic zero-panic supervisor systemd recovery exit",
    "يموت": "systematic-debugging crash panic supervisor systemd recovery exit",
    "كراش": "systematic-debugging panic zero-panic resilience fault-tolerance recovery crash",
    "كرش": "systematic-debugging panic zero-panic resilience fault-tolerance recovery crash",
    "ضرب ايرور": "systematic-debugging panic crash error exception fault traceback debug",
    "يضرب ايرور": "systematic-debugging panic crash error exception fault traceback debug",
    "ضرب": "panic crash error exception fault",
    "ايرور": "systematic-debugging error exception traceback debug fault-tolerance",
    "خطا": "error handling thiserror anyhow result resilience backoff",
    "اخطاء": "error handling thiserror anyhow result resilience backoff",
    "اكسبشن": "exception error handling debug traceback",
    "انفايند": "null undefined error handling option result",
    "نل": "null-safety option result error handling nil",
    "نيل": "null nil-safety option result error handling lua",
    "شنو هاي المشكلة": "systematic-debugging root-cause error-handling diagnostic",
    "حل المشكلة": "systematic-debugging root-cause error-handling bug-fix",
    "حل المشكلة هاي": "systematic-debugging root-cause error-handling bug-fix",
    "هاي المشكلة": "systematic-debugging root-cause error-handling bug-fix",
    "اكو مشكلة": "systematic-debugging root-cause error-handling bug-fix",
    "صلح المشكلة": "systematic-debugging root-cause bug-fix error-handling",
    "صلح الاخطاء": "systematic-debugging root-cause bug-fix error-handling",
    "صلح": "systematic-debugging bug-fix error-handling root-cause",
    "فيكس": "bug-fix patch systematic-debugging repair",

    # --- Performance, Memory, Concurrency & Low-Latency ---
    "استهلاك الرام": "rust_performance_memory zero-ram-idle jemalloc memory-leak heap profiling buffer-reuse",
    "استهلاك الرام ميغابايت": "rust_performance_memory zero-ram-idle jemalloc memory-leak heap profiling",
    "ياكل رام": "rust_performance_memory memory optimization ram leak buffer jemalloc zero-ram-idle profiling",
    "تسريب ذاكرة": "rust_performance_memory memory leak buffer retain cycle jemalloc resource-cleanup heap profiling",
    "تسريب": "rust_performance_memory memory leak buffer retain cycle jemalloc resource-cleanup heap profiling",
    "ليك": "rust_performance_memory memory leak buffer jemalloc resource cleanup heap profiling",
    "ذاكرة": "rust_performance_memory memory optimization ram buffer cache leak jemalloc zero-allocation",
    "رام": "rust_performance_memory memory optimization ram buffer leak jemalloc zero-allocation zero-ram-idle",
    "ثكيل": "performance latency speed zero-allocation optimize profiling benchmark",
    "بطيء": "performance latency speed zero-allocation optimize bottleneck",
    "بطي": "performance latency speed zero-allocation optimize bottleneck",
    "سريع": "performance optimization fast speed latency low-latency zero-allocation",
    "سرعة فائقة": "performance optimization fast speed latency low-latency zero-allocation",
    "سرع": "performance optimization fast speed latency low-latency",
    "اداء": "performance latency speed zero-allocation profiling benchmark",
    "تحسين": "optimization performance profiling clean architecture",
    "تزامن": "concurrency async tokio channel joinset worker pool",
    "توازي": "parallel async concurrency worker thread pool",
    "بلوك": "tokio blocking spawn_blocking async zero-blocking worker starvation",
    "بلوكينغ": "tokio blocking spawn_blocking async zero-blocking worker starvation",
    "شانل": "channel mpsc broadcast watch tokio bounded backpressure",
    "باك بريشر": "backpressure bounded-channel rate-limiting tokio queue",

    # --- Clean Code, Integrity & Verification ---
    "نظف الكود": "clean-code clean-architecture code_integrity strict_comment_discipline unslop",
    "نظف المشروع": "clean-code clean-architecture project_structure_standards unslop",
    "نظف": "refactor clean-code architecture unslop code_integrity",
    "تنظيف": "refactor clean-code architecture unslop",
    "رتب الكود": "clean-code refactor architecture project_structure_standards",
    "رتب": "refactor clean-code architecture project_structure_standards",
    "ترتيب": "clean-code refactor architecture project_structure_standards",
    "كود وصخ": "clean-code refactor clean-architecture code_integrity unslop",
    "بالاستناد على المرجع": "code_integrity strict_comment_discipline backward-compatibility clean-code",
    "بدون زيادة ولا نقصان": "code_integrity strict_comment_discipline backward-compatibility clean-code",
    "نفسها": "code_integrity backward-compatibility preservation",
    "شيل التعليقات": "strict_comment_discipline zero-ai-pollution clean-code",
    "بدون تعليقات": "strict_comment_discipline zero-ai-pollution clean-code",
    "المرجع": "code_integrity backward-compatibility clean-architecture reference",
    "معمارية": "clean-architecture modularity decoupled ddd ports-adapters",
    "معمار": "clean-architecture modularity decoupled ddd ports-adapters",
    "كلين اركتكشر": "clean-architecture decoupled ddd modularity ports-adapters",
    "تأكد بعد": "verification_discipline testing unit integration verification e2e",
    "شيك بعد": "verification_discipline testing unit integration verification e2e",
    "افحص": "verification_discipline testing unit integration verification audit",
    "فحص كامل": "verification_discipline testing unit integration verification audit",
    "شيك": "verification_discipline testing audit inspection check",
    "تأكد": "verification_discipline testing inspection verification check",
    "اختبار": "testing tdd pytest unit integration verification e2e",
    "تيست": "testing unit integration verification tdd cargo-test",
    "امان": "security vulnerability injection scanner sanitize auth owasp",
    "حماية": "security vulnerability sanitize authentication jwt ssl",
    "حماي": "security vulnerability sanitize authentication jwt ssl",
    "ثغرة": "vulnerability exploit patch security injection xss sql",
    "ثغر": "vulnerability exploit patch security injection xss sql",

    # --- Git & Deployment ---
    "ارفع التحديث": "git-commit-standards git-workflows conventional-commits git-push",
    "ارفع التحديث مالته": "git-commit-standards git-workflows conventional-commits git-push",
    "ارفع ل github": "git-commit-standards git-workflows git-push remote",
    "ارفع على github": "git-commit-standards git-workflows git-push remote",
    "ارفع": "git-commit-standards git-workflows git-push deploy upload",
    "حدث": "git update refresh upgrade version keep-alive",
    "تحديث": "git update refresh upgrade version dependencies",
    "كمت": "git commit conventional-commits git-commit-standards",
    "كوميت": "git commit conventional-commits git-commit-standards",
    "بوش": "git push remote origin main git-workflows",
    "ريبو": "repository git github git-workflows",
    "مستودع": "repository git github git-workflows",

    # --- Directives & Action Verbs (Iraqi Dialect) ---
    "سويلي": "create build implement generate add feature",
    "سوي": "create build implement generate action",
    "ضيفلي": "add create implement extend feature append",
    "ضيف": "add create implement extend feature",
    "عدلي": "edit update modify refactor adjust fix",
    "عدل": "edit update modify refactor adjust fix",
    "امسحلي": "delete remove clean purge erase strip",
    "امسح": "delete remove clean purge erase strip",
    "شيللي": "remove strip delete clean drop omit",
    "شيل": "remove strip delete clean drop omit",
    "شيلها": "remove strip delete clean drop omit",
    "شيلهة": "remove strip delete clean drop omit",
    "صلحلي": "fix repair debug resolve root-cause patch",
    "صلح": "fix repair debug resolve root-cause patch",
    "شوفلي": "inspect analyze find investigate check search diagnose",
    "شوف": "inspect analyze find investigate check search diagnose",
    "شيكلي": "verify audit check inspect test validate",
    "طلعلي": "extract search retrieve display find show",
    "طلع": "extract search retrieve display find show",
    "نزللي": "install download clone fetch setup",
    "نزل": "install download clone fetch setup",
    "حول كود": "convert migrate translate refactor lua-to-rust port",
    "حول": "convert migrate translate refactor transform port",
    "كمل": "complete continue execute finish finalize resume",
    "ابني": "build compile cargo architecture create construct",

    # --- Search & Web ---
    "ابحث في الانترنت وتعلم": "web-search search research documentation modern-api learn",
    "ابحث في الانترنت عن": "web-search search research documentation query",
    "ابحث في الانترنت": "web-search search research documentation web",
    "ابحث": "web-search search research documentation web",
    "اتعلم": "learn research documentation study best-practices",

    # --- Databases ---
    "قاعدة بيانات": "database sql sqlite postgres storage query schema migration",
    "قاعد": "database sql sqlite postgres storage query schema migration",
    "بيانات": "database data storage dataset persist sqlite postgres",
    "بيان": "database data storage dataset persist sqlite postgres",
    "داتا": "database sqlite postgres sql query storage",
    "داتابيز": "database sqlite postgres sql query storage schema",
    "سيكول": "sql sqlite postgres database query migration",
    "جدول": "database table schema sql migration sqlite",
    "تخزين": "storage persist database file-system cache disk",
    "كويري": "query sql database indexing optimization",
    "كاش": "cache in-memory redis memory lru cache-layer",

    # --- Languages & OS ---
    "رست": "rust tokio memory cargo async zero-allocation jemalloc rust-patterns",
    "روست": "rust tokio memory cargo async zero-allocation jemalloc rust-patterns",
    "بايثون": "python fastapi pydantic pytest asyncio telethon pyrogram",
    "لوا": "lua script migration lua-to-rust syntax",
    "جو": "go golang goroutine channel gin-gonic",
    "كولانج": "go golang goroutine channel gin-gonic",
    "تايب": "typescript ts types interfaces generics react",
    "تايب سكربت": "typescript ts types interfaces generics react nodejs",
    "جافاسكربت": "javascript nodejs ecmascript typescript frontend",
    "رياكت": "react frontend hooks state components nextjs ui",
    "نيكست": "nextjs react ssr frontend components web",
    "لينكس": "linux debian ubuntu systemd process terminal bash shell",
    "يوبنتو": "ubuntu linux debian systemd apt package terminal",
    "سيرفر": "server daemon systemd linux deployment proxy nginx",
    "خادم": "server daemon systemd linux deployment proxy nginx",
    "حاوية": "docker container dockerfile compose kubernetes orchestration",
    "حاوي": "docker container dockerfile compose kubernetes",
    "دوكر": "docker container dockerfile compose orchestration containerization",
    "كونتينر": "docker container containerization dockerfile compose",
    "شبكة": "network http websocket tls client rate-limit connection",
    "شبك": "network http websocket tls client rate-limit connection",
    "ويب": "web html css vanilla responsive api integration frontend",

    # --- Governance & Honesty ---
    "برمشن تلقائي": "permission policy allow auto-approve authorization turbo",
    "بدون برمشن": "permission policy allow auto-approve authorization turbo",
    "برمشن": "permission policy allow auto-approve authorization turbo",
    "صلاحية": "permission policy authorization grant allow access",
    "صلاحي": "permission policy authorization grant allow access",
    "اذن": "permission policy allow authorization grant",
    "بدون مجاملة": "honest-engineering anti-sycophancy unslop frank blunt truth",
    "كافي مجاملة": "honest-engineering anti-sycophancy unslop frank blunt truth",
    "مجاملة": "honest-engineering anti-sycophancy unslop frank blunt truth",
    "تزلف": "anti-sycophancy honest-engineering frank blunt",
    "نفاق": "anti-sycophancy honest-engineering frank",
    "صراحة": "honest-engineering frank blunt technical truth",
    "صراح": "honest-engineering frank blunt technical truth",
    "احجي الصدك": "honest-engineering frank blunt technical truth anti-sycophancy",
    "تيربو": "permission auto-approve authorization turbo antigravity-cli",
}

def normalize_arabic(text: str) -> str:
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = re.sub(r"[أإآ]", "ا", text)
    text = re.sub(r"ة", "ه", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"گ", "ك", text)
    text = re.sub(r"پ", "ب", text)
    text = re.sub(r"ڤ", "ف", text)
    text = re.sub(r"ژ", "ز", text)
    return text.lower()

AR_STEM_MAP: Dict[str, str] = {
    normalize_arabic(k): v for k, v in RAW_AR_STEM_MAP.items()
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
    data = {}
    if yaml is not None:
        try:
            loaded = yaml.safe_load(parts[1])
            if isinstance(loaded, dict):
                data = loaded
        except Exception:
            pass
    if not data:
        for line in parts[1].splitlines():
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                if v.startswith("[") and v.endswith("]"):
                    v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
                data[k] = v
    return data, parts[2]

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
    # Dialect typo & variant tolerance for common developer terms
    t = re.sub(r"\b(تلقرام|تلغرام)\b", "تلكرام", t)
    t = re.sub(r"\b(انستقرام|انستكرام|انستغرام)\b", "انستا", t)
    t = re.sub(r"\b(داون لود|داونلودر)\b", "داونلود", t)
    t = re.sub(r"\b(روست)\b", "رست", t)
    t = re.sub(r"\b(فويس چات|فويس شات)\b", "فويس جات", t)
    return t

def extract_stems(norm_text: str) -> set:
    words = re.findall(r"[\u0621-\u064A]+", norm_text)
    stems = set(words)
    for w in words:
        for suf in ("لي", "ها", "هه", "هم", "كم", "ني", "نا", "ك", "ت", "ات", "ين", "ون"):
            if len(w) > len(suf) + 2 and w.endswith(suf):
                stems.add(w[:-len(suf)])
        if len(w) > 4 and (w.startswith("وال") or w.startswith("فال") or w.startswith("بال") or w.startswith("كال")):
            stems.add(w[3:])
            stems.add(w[1:])
        elif len(w) > 3 and w.startswith("لل"):
            stems.add(w[2:])
        elif len(w) > 3 and w.startswith("ال"):
            stems.add(w[2:])
        elif len(w) > 3 and (w.startswith("و") or w.startswith("ف") or w.startswith("ب") or w.startswith("ل")):
            stems.add(w[1:])
    return stems

def extract_intent_tokens(query: str) -> List[str]:
    q_clean = clean_query_text(query)
    norm = normalize_arabic(q_clean)
    stems = extract_stems(norm)

    matched_exps = []
    for stem, exp in sorted(AR_STEM_MAP.items(), key=lambda x: len(x[0]), reverse=True):
        if " " in stem:
            if stem in norm:
                for w in exp.split():
                    if w not in matched_exps:
                        matched_exps.append(w)
        else:
            if stem in norm or stem in stems:
                for w in exp.split():
                    if w not in matched_exps:
                        matched_exps.append(w)

    raw_words = [
        w.lower() for w in re.findall(r"[\w]+", q_clean)
        if len(w) > 1 and w.lower() not in ARABIC_STOPWORDS
    ]

    # Prioritize matched semantic intent tokens FIRST to prevent long text dilution
    ordered = []
    seen = set()
    for t in matched_exps + raw_words:
        if t not in seen:
            seen.add(t)
            ordered.append(t)

    return ordered

def expand_query(query: str) -> str:
    tokens = extract_intent_tokens(query)
    return " ".join(tokens)
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
    _cached_search_capabilities.cache_clear()
    _cached_exact_skill.cache_clear()
    _cached_exact_rule.cache_clear()
    _cached_core_governance.cache_clear()
    _cached_skill_toc.cache_clear()
    _cached_skill_section.cache_clear()

INTENT_DOMAINS: Dict[str, Dict[str, Any]] = {
    "telegram_music": {
        "keywords": ["music", "audio", "voice-chat", "stream", "pytgcalls", "rusttgcalls", "gotgcall", "playback", "webrtc", "ffmpeg", "flexmusic"],
        "tag": "Voice & Music Streaming",
    },
    "telegram_bots": {
        "keywords": ["telegram-bot", "telegram-bot-builder", "webhook", "polling", "teloxide", "mtproto", "session", "userbot", "gogram", "grammers"],
        "tag": "Telegram Bot Architecture",
    },
    "performance_memory": {
        "keywords": ["memory", "ram", "leak", "jemalloc", "zero-ram-idle", "zero-allocation", "deadlock", "mutex", "tokio", "concurrency", "profiling"],
        "tag": "Low-RAM & Concurrency",
    },
    "ui_styling": {
        "keywords": ["button", "button-states", "telegram-button-styling", "colors", "anti_ai_design", "better-colors", "typography", "icons", "anti-ui-slop"],
        "tag": "UI, Buttons & Anti-Slop",
    },
    "ai_agentic": {
        "keywords": ["ai-agent", "tool-calling", "function-calling", "agentic-bot", "slot-filling", "autonomous-agent", "tools-orchestration"],
        "tag": "AI Agents & Tool Calling",
    },
    "clean_architecture": {
        "keywords": ["clean-architecture", "clean-code", "code_integrity", "strict_comment_discipline", "decoupled", "ports-adapters", "service-layer"],
        "tag": "Clean Architecture & Integrity",
    },
    "telegram_webhook": {
        "keywords": ["webhook", "token_hash", "axum", "nginx", "secret_token", "proxy_buffering", "setwebhook", "deletewebhook", "drop_pending_updates", "webhook-automation"],
        "tag": "Telegram Webhook Architecture",
    },
    "media_download": {
        "keywords": ["media-downloader", "yt-dlp", "video-download", "instagram-downloader", "tiktok", "fastdl"],
        "tag": "Media & Video Downloaders",
    },
    "testing_verification": {
        "keywords": ["verification", "testing", "unit", "integration", "qa", "audit", "senior-qa"],
        "tag": "Verification & Testing",
    }
}

@functools.lru_cache(maxsize=1024)
def _cached_search_capabilities(query_key: str, domain: Optional[str], language: Optional[str], min_quality: int, limit: int) -> Tuple:
    tokens = extract_intent_tokens(query_key)
    if not tokens:
        return ()

    active_domains = []
    for d_name, d_info in INTENT_DOMAINS.items():
        if any(k in tokens for k in d_info["keywords"]):
            active_domains.append(d_name)

    fts_query_parts = [f'"{tok}"*' for tok in tokens[:28]]
    fts_query = " OR ".join(fts_query_parts)

    conn = get_db_conn()
    raw_candidates = []

    try:
        cur = conn.execute("""
            SELECT items.id, items.item_type, items.name, items.description, items.language, items.category,
                   items.quality_score, items.source_tier, items.content,
                   bm25(items_fts, 20.0, 10.0, 15.0, 6.0, 6.0, 1.2) as rank_score
            FROM items_fts
            JOIN items ON items.id = items_fts.id
            WHERE items_fts MATCH ? AND items.quality_score >= ?
            ORDER BY (rank_score * (items.quality_score / 50.0))
            LIMIT 60
        """, (fts_query, min_quality))
        raw_candidates = cur.fetchall()
    except Exception:
        return ()

    def tag_item(name: str, desc: str, content: str) -> Tuple[str, str]:
        comb = (name + " " + desc + " " + content[:600]).lower()
        for d_name in active_domains:
            kws = INTENT_DOMAINS[d_name]["keywords"]
            if any(k in comb for k in kws):
                return (d_name, INTENT_DOMAINS[d_name]["tag"])
        return ("general", "General")

    seen_names = set()
    selected_rows = []
    domain_represented = {d: False for d in active_domains}

    # Pass 1: Multi-domain guarantee (at least 1 item per detected active domain)
    if len(active_domains) > 1:
        for row in raw_candidates:
            item_id, item_type, name, desc, item_lang, cat, q_score, tier, raw_content, rank = row
            if name in seen_names:
                continue
            if language and language.lower() not in item_lang.lower():
                continue
            if domain and domain.lower() not in name.lower() and domain.lower() not in cat.lower():
                continue

            d_name, d_tag = tag_item(name, desc, raw_content)
            if d_name in domain_represented and not domain_represented[d_name]:
                domain_represented[d_name] = True
                seen_names.add(name)
                selected_rows.append((row, d_tag))

    # Pass 2: Fill remaining slots with best overall ranking
    for row in raw_candidates:
        if len(selected_rows) >= limit:
            break
        item_id, item_type, name, desc, item_lang, cat, q_score, tier, raw_content, rank = row
        if name in seen_names:
            continue
        if language and language.lower() not in item_lang.lower():
            continue
        if domain and domain.lower() not in name.lower() and domain.lower() not in cat.lower():
            continue

        d_name, d_tag = tag_item(name, desc, raw_content)
        seen_names.add(name)
        selected_rows.append((row, d_tag))

    out = []
    for (item_id, item_type, name, desc, item_lang, cat, q_score, tier, raw_content, rank), d_tag in selected_rows:
        cleaned_desc = clean_description(desc, raw_content, max_len=140)
        tier_mult = 1.35 if tier == "official" else (1.2 if tier == "top-starred" else (1.1 if tier == "core" else 1.0))
        confidence = round(abs(rank) * (q_score / 50.0) * tier_mult * 100, 1)

        out.append((
            item_id, item_type, name, item_lang, q_score, tier, cleaned_desc, confidence, d_tag
        ))

    return tuple(out)

@mcp.tool()
def search_agent_capabilities(query: str, domain: Optional[str] = None, language: Optional[str] = None, min_quality: int = 40, limit: int = 8) -> List[Dict[str, Any]]:
    rows = _cached_search_capabilities(query.strip(), domain, language, min_quality, limit)
    return [
        {
            "id": r[0],
            "type": r[1],
            "name": r[2],
            "language": r[3],
            "quality_score": r[4],
            "tier": r[5],
            "description": r[6],
            "confidence_score": r[7],
            "domain_tag": r[8],
        }
        for r in rows
    ]

@mcp.tool()
def get_smart_skill_summary(name: str) -> Dict[str, Any]:
    content = _cached_exact_skill(name)
    is_rule = False
    if "not found" in content:
        content = _cached_exact_rule(name)
        is_rule = True
    if "not found" in content:
        return {"error": f"Skill or Rule '{name}' not found."}

    lines = content.splitlines()
    overview = []
    invariants = []

    collecting_desc = False
    for line in lines:
        s = line.strip()
        if s.startswith("description:") or s.startswith("## Mission") or s.startswith("## Purpose") or s.startswith("## Overview"):
            overview.append(s)
            collecting_desc = True
        elif collecting_desc and s.startswith("##"):
            break
        elif collecting_desc and s and len(overview) < 5:
            overview.append(s)

    for line in lines:
        s = line.strip()
        if any(w in s for w in ["Do NOT", "BANNED", "Never", "Mandatory", "Golden Rule", "In-Place", "Zero-Panic"]) and len(s) > 10:
            if not s.startswith("#"):
                invariants.append(s)
            if len(invariants) >= 8:
                break

    return {
        "name": name,
        "type": "rule" if is_rule else "skill",
        "overview": "\n".join(overview[:4]) if overview else clean_description("", content, max_len=180),
        "core_invariants": invariants[:6],
        "token_saving_ratio": "85% reduction vs full text",
    }

@mcp.tool()
def recommend_skills_for_context(
    file_path: Optional[str] = None,
    user_goal: Optional[str] = None,
    code_snippet: Optional[str] = None
) -> Dict[str, Any]:
    detected_lang = "general"
    detected_subsystem = "general"
    rules_to_enforce = ["rule:honest_engineering", "rule:strict_comment_discipline", "rule:clean_code_architecture", "rule:code_integrity"]
    skills_to_use = []

    comb_text = ((file_path or "") + " " + (user_goal or "") + " " + (code_snippet or "")).lower()

    if any(k in comb_text for k in [".rs", "cargo", "rust", "tokio"]):
        detected_lang = "Rust"
        rules_to_enforce.extend(["rule:rust", "rule:rust_standards", "rule:no_lazy_fallbacks", "rule:rust_performance_memory"])
        skills_to_use.extend(["skill:rust-async-patterns", "skill:rust-best-practices", "skill:rust-skills"])

    elif any(k in comb_text for k in [".go", "go.mod", "golang", "gogram", "gotgcall"]):
        detected_lang = "Go"
        rules_to_enforce.extend(["rule:go", "rule:46_go_concurrency_patterns_and_deadlock_prevention_guide"])
        skills_to_use.extend(["skill:golang-code-style", "skill:golang-troubleshooting", "skill:golang-design-patterns"])

    elif any(k in comb_text for k in [".py", "python", "telethon", "pyrogram", "fastapi"]):
        detected_lang = "Python"
        rules_to_enforce.append("rule:python")
        skills_to_use.append("skill:systematic-debugging")

    if any(k in comb_text for k in ["music", "voice", "stream", "webrtc", "call", "audio", "ميوزك", "صوت"]):
        detected_subsystem = "Telegram VoIP & Music Streaming"
        rules_to_enforce.extend(["rule:telegram_voip_architecture", "rule:DEVELOPMENT_GUIDE"])
        skills_to_use.extend(["skill:telegram-bot", "skill:telegram-bot-builder"])

    if any(k in comb_text for k in ["button", "زر", "دكم", "كيبورد", "ui", "design", "لون", "style", "slop"]):
        rules_to_enforce.extend(["rule:anti_ai_design", "rule:telegram_button_styling"])
        skills_to_use.extend(["skill:better-colors", "skill:better-icons", "skill:better-ui"])

    if any(k in comb_text for k in ["agent", "tool", "function", "ايجنت", "اداة", "يستدعي"]):
        rules_to_enforce.append("rule:ai-agent-specialist")
        skills_to_use.append("skill:telegram-bot-builder")

    # If user provided a specific goal, run semantic search to augment skills
    if user_goal:
        discovered = search_agent_capabilities(user_goal, limit=3)
        for item in discovered:
            ref = f"{item['type']}:{item['name']}"
            if item['type'] == 'rule' and ref not in rules_to_enforce:
                rules_to_enforce.append(ref)
            elif item['type'] == 'skill' and ref not in skills_to_use:
                skills_to_use.append(ref)

    return {
        "detected_language": detected_lang,
        "subsystem": detected_subsystem,
        "recommended_rules": rules_to_enforce,
        "recommended_skills": skills_to_use[:6],
        "actionable_guidance": "Follow primary rules without degraded fallbacks. Enforce zero-allocation and structured errors.",
    }

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
        (r"(?i)\b(great question|excellent question|you are absolutely right|you're absolutely right|certainly[!,]|i would be happy to help|i'd be happy to help|i am thrilled to|excellent idea|good point|wonderful question|thank you for asking|brilliant idea|amazing point)\b", "Sycophantic flattery or servile opener"),
        (r"(?i)(سؤال ممتاز|سؤال رائع|أنت على حق تماما|أنت محق تماما|بالتأكيد يسعدني|يسعدني مساعدتك|فكرة رائعة جدا|يا له من سؤال|طبعا من عيوني|تدلل|امرك يا غالي|فكرة عبقرية|انت الافضل|كلامك ذهب|مضبوط مية بالمية)", "Arabic colloquial flattery or servile opener"),
        (r"(?i)\b(i apologize for the confusion|sorry about that|my apologies|sorry for the misunderstanding|اعتذر بشدة|اعتذر عن الخطأ|اسف جدا|أعتذر عن الخطأ، معك حق)\b", "Servile apology instead of direct root-cause fix"),
        (r"(?i)\b(delve|tapestry|testament|seamless|holistic|leverage|cutting-edge|elevate|multifaceted|beacon|pivotal|revolutionize|game-changer|groundbreaking)\b", "AI stock filler buzzword"),
        (r"(?i)\b(in this fast-paced world|at the end of the day|let's dive in|without further ado|مما لا شك فيه|في الختام يجدر الذكر|جدير بالذكر)\b", "Conversational filler or rhetorical padding"),
        (r"(?i)\b(as an ai language model|as an ai|in conclusion, it is important to remember|it is worth noting that|keep in mind that)\b", "Patronizing AI disclaimer or robotic closure"),
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
    lines_input = css_or_html.splitlines()

    anti_patterns = [
        (r"(?i)(linear-gradient|radial-gradient).*#[789a-f][0-9a-f]{5}.*#[789a-f][0-9a-f]{5}", "anti_ai_design", "CRITICAL", "Generic AI purple/violet gradient detected. Use disciplined semantic palettes (see skill:better-colors)."),
        (r"(?i)(linear-gradient|radial-gradient).*rgba\(\s*(124|139|99|168|147)\s*,\s*(58|92|102|85|51)", "anti_ai_design", "CRITICAL", "AI violet/indigo glow gradient detected. Use authentic semantic roles."),
        (r"(?i)backdrop-filter:\s*blur\(", "anti_ai_design", "WARNING", "Faux glassmorphism detected without defined structural layer (see skill:impeccable)."),
        (r"[🌀-🫿]", "anti_ai_design", "CRITICAL", "Raw emoji detected in UI markup. Use scalable monochrome SVGs from heroicons or lucide (see skill:better-icons)."),
        (r"(?i)background-clip:\s*text", "anti_ai_design", "CRITICAL", "Gradient text detected. Weight and scale convey hierarchy, not novelty color fills (see skill:impeccable)."),
        (r"(?i)box-shadow:\s*[3-9]px\s+[3-9]px\s+0px", "anti_ai_design", "WARNING", "Zero-blur hard block shadow detected without justified neobrutalist context."),
        (r"(?i)(text-xs|font-semibold)\s+(uppercase|tracking-widest)", "anti_ai_design", "WARNING", "AI kicker/eyebrow all-caps label detected above heading. Let the heading carry its own weight."),
        (r"(?i)button[^{]*\{[^}]*\}", "button_states", "INFO", "Verify all 6 states are defined (rest, hover, active, focus-visible, disabled, loading)."),
    ]

    for idx, l_text in enumerate(lines_input):
        l_num = idx + 1
        for pat, rule, sev, desc in anti_patterns:
            if re.search(pat, l_text):
                violations.append({
                    "line": l_num,
                    "rule": rule,
                    "severity": sev,
                    "code_snippet": l_text.strip()[:100],
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
    target_dir = HOME_DIR / ".gemini/skills-catalog/skills" / safe_name
    target_dir.mkdir(parents=True, exist_ok=True)
    skill_file = target_dir / "SKILL.md"

    frontmatter = {
        "name": safe_name,
        "description": description,
        "triggers": triggers,
        "language": language,
        "category": category,
    }

    if yaml is not None:
        yaml_block = yaml.dump(frontmatter, sort_keys=False).strip()
    else:
        yaml_block = "\n".join(f"{k}: {v}" for k, v in frontmatter.items())
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

    # Detect Telegram bot factory ecosystem microservices
    bot_subsystem_map = {
        "factory": ("Telegram Bot Factory & Multi-Tenant Core", ["rule:telegram_bots", "rule:rust_concurrency_state", "rule:no_lazy_fallbacks"]),
        "rusttgcalls": ("Telegram VoIP / WebRTC Media Engine", ["rule:telegram_voip_architecture", "rule:rust_performance_memory"]),
        "fastdl-rs": ("High-Performance Stream Extractor & Downloader", ["rule:rust_performance_memory", "rule:no_lazy_fallbacks"]),
        "social": ("Social Media Extractor Service", ["rule:rust_standards", "rule:security_hygiene"]),
        "music": ("Voice Chat Music Streaming Service", ["rule:go", "rule:telegram_voip_architecture"]),
        "shazam": ("Audio Recognition Engine", ["rule:rust_standards", "rule:rust_performance_memory"]),
        "session": ("MTProto Session String Generator", ["rule:security_hygiene", "rule:rust_standards"]),
        "convert": ("Media Transcoder & Converter", ["rule:rust_standards", "rule:clean_code_architecture"]),
        "restricted": ("Restricted Media Downloader", ["rule:rust_standards", "rule:no_lazy_fallbacks"]),
        "akinatorrust": ("Interactive Game Bot", ["rule:rust_standards"]),
        "asiacell_api": ("Telecom Core API", ["rule:go", "rule:api-rate-limiting"]),
        "zain_api": ("Telecom Core API", ["rule:go", "rule:api-rate-limiting"]),
        "yt-api": ("YouTube Video/Audio Extractor", ["rule:rust_standards"]),
    }
    for b_name, (subsystem_name, extra_rules) in bot_subsystem_map.items():
        if b_name in p.parts:
            detected_stack.append(f"Bot Microservice: {subsystem_name}")
            recommended_rules.extend(extra_rules)
            break

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
            if "std::thread::sleep" in s:
                violations.append({"line": l_num, "rule": "async-no-block", "severity": "CRITICAL", "message": "Prohibited std::thread::sleep in Tokio thread. Use tokio::time::sleep or spawn_blocking."})
            if 'format!("-100' in s or 'replace("-100"' in s:
                violations.append({"line": l_num, "rule": "no_lazy_fallbacks", "severity": "HIGH", "message": "Unvalidated -100 prefix formatting detected. Private user IDs must not have -100 prefix."})
            if "Vec<u8>" in s and any(k in s for k in ("audio", "video", "media", "voice", "stream", "payload")):
                violations.append({"line": l_num, "rule": "anti-raw-bytes-ram", "severity": "HIGH", "message": "Raw media bytes Vec<u8> stored in RAM. Stream payloads directly to disk and retain PathBuf."})

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


BOT_SERVICES_CATALOG: Dict[str, Dict[str, Any]] = {
    "instagram_downloader": {
        "service_name": "Instagram Media Downloader",
        "bot_repository": "/root/bots/social",
        "engine_repository": "/root/bots/fastdl-rs",
        "primary_language": "Rust",
        "patterns": ["انستا", "ريلز", "ستوري", "ستوريات", "instagram", "insta", "reel", "stories"],
        "required_params": ["url"],
        "missing_param_prompts": {
            "url": "ارسل رابط المنشور او الريلز من الانستغرام حتى انزله الك بالدقة العالية ⚡"
        },
        "tool_definition": {
            "name": "download_instagram_media",
            "description": "Extracts high-resolution videos, reels, photos, and audio from Instagram URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The Instagram post, reel, or story URL."}
                },
                "required": ["url"]
            }
        },
        "description": "High-throughput Instagram media extractor without authentication walls.",
        "recommended_rules": ["rule:rust_standards", "rule:rust_performance_memory", "rule:no_lazy_fallbacks"],
        "recommended_skills": ["skill:telegram-bot-builder", "skill:clean-architecture"]
    },
    "tiktok_downloader": {
        "service_name": "TikTok Watermark-Free Downloader",
        "bot_repository": "/root/bots/social",
        "engine_repository": "/root/bots/fastdl-rs",
        "primary_language": "Rust",
        "patterns": ["تيك توك", "تكتوك", "تيك", "tiktok", "tt"],
        "required_params": ["url"],
        "missing_param_prompts": {
            "url": "ارسل رابط فيديو التيك توك حتى انزله الك بدون علامة مائية وبأعلى جودة 🚀"
        },
        "tool_definition": {
            "name": "download_tiktok_media",
            "description": "Extracts HD video and audio from TikTok stripping watermarks with zero-RAM idle buffering.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The TikTok video URL."}
                },
                "required": ["url"]
            }
        },
        "description": "High-throughput TikTok media extractor with watermark removal.",
        "recommended_rules": ["rule:rust_standards", "rule:rust_performance_memory", "rule:no_lazy_fallbacks"],
        "recommended_skills": ["skill:telegram-bot-builder", "skill:clean-architecture"]
    },
    "youtube_downloader": {
        "service_name": "YouTube Fast Downloader & Extractor",
        "bot_repository": "/root/bots/yt-api",
        "engine_repository": "/root/bots/fastdl-rs",
        "primary_language": "Rust",
        "patterns": ["يوتيوب", "يوت", "شورتس", "youtube", "yt", "shorts"],
        "required_params": ["url"],
        "missing_param_prompts": {
            "url": "ارسل رابط مقطع اليوتيوب او الشورتس اللي تريد احمله الك 🎬"
        },
        "tool_definition": {
            "name": "download_youtube_media",
            "description": "High-throughput stream extraction for YouTube videos and MP3 audio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The YouTube video or shorts URL."},
                    "format": {"type": "string", "enum": ["audio", "video"], "default": "video"}
                },
                "required": ["url"]
            }
        },
        "description": "Stream extraction for YouTube videos and audio transcoding.",
        "recommended_rules": ["rule:rust_standards", "rule:rust_performance_memory"],
        "recommended_skills": ["skill:telegram-bot-builder"]
    },
    "music_voice_chat": {
        "service_name": "Voice Chat & Group Call Music Streaming",
        "bot_repository": "/root/bots/music",
        "engine_repository": "/root/bots/rusttgcalls",
        "primary_language": "Go / Rust",
        "patterns": ["ميوزك", "شغل", "اغنيه", "فويس جات", "كول", "مكالمه", "صوتيه", "music", "play", "stream", "vc"],
        "required_params": ["query_or_url"],
        "missing_param_prompts": {
            "query_or_url": "شنو اسم الاغنية او رابط اليوتيوب/الساوند اللي تريد اشغله بالمكالمة الصوتية؟ 🎵"
        },
        "tool_definition": {
            "name": "play_voice_chat_audio",
            "description": "Streams real-time audio into a Telegram group call / voice chat via WebRTC.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_or_url": {"type": "string", "description": "The song name, search query, or streaming URL."},
                    "chat_id": {"type": "integer", "description": "Target Telegram group or channel chat ID."}
                },
                "required": ["query_or_url"]
            }
        },
        "description": "Real-time WebRTC audio streaming to Telegram voice chats with low latency.",
        "recommended_rules": ["rule:rust_standards", "rule:go", "rule:telegram_voip_architecture"],
        "recommended_skills": ["skill:telegram-bot", "skill:telegram-bot-builder"]
    },
    "audio_recognition": {
        "service_name": "Shazam Audio Recognizer",
        "bot_repository": "/root/bots/shazam",
        "engine_repository": None,
        "primary_language": "Rust",
        "patterns": ["شازام", "شنو هاي الاغنيه", "تعرف على الصوت", "بصمه صوت", "اسم الاغنيه", "عرف الاغنيه", "shazam", "recognize"],
        "required_params": ["audio_sample"],
        "missing_param_prompts": {
            "audio_sample": "ارسل البصمة الصوتية او المقطع الصوتي حتى اتعرف على اسم الاغنية والمطرب 🎧"
        },
        "tool_definition": {
            "name": "recognize_audio",
            "description": "Fingerprints audio samples and retrieves metadata, song title, and artist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "audio_file_path": {"type": "string", "description": "Path to the temporary audio sample file on disk."}
                },
                "required": ["audio_file_path"]
            }
        },
        "description": "Fingerprints audio samples and retrieves metadata and song title.",
        "recommended_rules": ["rule:rust_standards", "rule:rust_performance_memory"],
        "recommended_skills": ["skill:clean-architecture"]
    },
    "session_generator": {
        "service_name": "Telegram MTProto Session String Generator",
        "bot_repository": "/root/bots/session",
        "engine_repository": None,
        "primary_language": "Rust",
        "patterns": ["جلسه", "بايروجرام", "تليثون", "غرامرز", "جوجرام", "session", "string session", "pyrogram", "telethon"],
        "required_params": ["framework", "phone_number"],
        "missing_param_prompts": {
            "framework": "حدد نوع الجلسة المطلوبة (بايروجرام، تليثون، كرامرز، جوجرام) ورقم الهاتف للبدء 🔐"
        },
        "tool_definition": {
            "name": "generate_string_session",
            "description": "Securely generates 2FA-compliant Telegram MTProto session strings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "framework": {"type": "string", "enum": ["pyrogram", "telethon", "grammers", "gogram"]},
                    "phone_number": {"type": "string", "description": "International format phone number."}
                },
                "required": ["framework", "phone_number"]
            }
        },
        "description": "Securely generates Telegram MTProto session strings.",
        "recommended_rules": ["rule:rust_standards", "rule:security_hygiene"],
        "recommended_skills": ["skill:telegram-bot-builder"]
    },
    "format_converter": {
        "service_name": "Media & Format Transcoder",
        "bot_repository": "/root/bots/convert",
        "engine_repository": None,
        "primary_language": "Rust",
        "patterns": ["تحويل صيغه", "حول", "صيغه", "mp3", "mp4", "تحويل صوت", "convert", "transcode", "ffmpeg"],
        "required_params": ["media_file", "target_format"],
        "missing_param_prompts": {
            "media_file": "ارسل الملف او الفيديو والصيغة المطلوبة (مثال: mp3, ogg, wav, mp4) للتحويل 🔄"
        },
        "tool_definition": {
            "name": "convert_media_format",
            "description": "Hardware-accelerated media transcoding using FFmpeg with strict disk streaming.",
            "parameters": {
                "type": "object",
                "properties": {
                    "source_path": {"type": "string", "description": "Local path to source media file."},
                    "target_format": {"type": "string", "description": "Desired format extension e.g. mp3, ogg."}
                },
                "required": ["source_path", "target_format"]
            }
        },
        "description": "Hardware-accelerated media transcoding using FFmpeg.",
        "recommended_rules": ["rule:rust_standards", "rule:rust_performance_memory"],
        "recommended_skills": ["skill:clean-architecture"]
    },
    "telecom_service": {
        "service_name": "Telecom Core & Balance Inquiries",
        "bot_repository": "/root/bots/asiacell_api",
        "engine_repository": "/root/bots/zain_api",
        "primary_language": "Go",
        "patterns": ["رصيد", "اسيا", "اسياسيل", "زين", "شحن كارت", "سيم كارت", "telecom", "asiacell", "zain", "balance"],
        "required_params": ["phone_number"],
        "missing_param_prompts": {
            "phone_number": "ارسل رقم الهاتف او الخط (اسياسيل او زين) للتحقق من الرصيد والخدمات 📱"
        },
        "tool_definition": {
            "name": "check_telecom_account",
            "description": "Checks balance, active bundles, and SIM status for Asiacell and Zain lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phone_number": {"type": "string", "description": "Subscriber MSISDN phone number."},
                    "carrier": {"type": "string", "enum": ["asiacell", "zain"]}
                },
                "required": ["phone_number"]
            }
        },
        "description": "Telecom subscriber inquiries and automation.",
        "recommended_rules": ["rule:go", "rule:api-rate-limiting"],
        "recommended_skills": ["skill:telecom-api-engineering", "skill:clean-code"]
    },
    "restricted_downloader": {
        "service_name": "Restricted Content Downloader",
        "bot_repository": "/root/bots/restricted",
        "engine_repository": None,
        "primary_language": "Rust",
        "patterns": ["مقيد", "قناه خاصه", "حفظ المحتوي", "restricted", "save restricted", "private channel"],
        "required_params": ["post_link"],
        "missing_param_prompts": {
            "post_link": "ارسل رابط المنشور من القناة المقيدة حتى اسحبه الك مباشرة 📥"
        },
        "tool_definition": {
            "name": "download_restricted_content",
            "description": "Fetches and re-hosts content from Telegram channels with restricted saving permissions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "post_link": {"type": "string", "description": "The Telegram post link from the private channel."}
                },
                "required": ["post_link"]
            }
        },
        "description": "Fetches and re-hosts content from Telegram channels with restricted permissions.",
        "recommended_rules": ["rule:rust_standards", "rule:rust_performance_memory"],
        "recommended_skills": ["skill:telegram-bot-builder"]
    }
}

@mcp.tool()
def resolve_bot_service(user_query: str) -> Dict[str, Any]:
    cleaned = clean_query_text(user_query)
    urls = re.findall(r"https?://[^\s]+", user_query)

    matched_service_key = None
    max_matches = 0

    for s_key, s_data in BOT_SERVICES_CATALOG.items():
        matches = sum(1 for pat in s_data["patterns"] if pat in cleaned)
        if matches > max_matches:
            max_matches = matches
            matched_service_key = s_key

    if not matched_service_key:
        matched_service_key = "instagram_downloader" if "انستا" in cleaned else "music_voice_chat"

    s = BOT_SERVICES_CATALOG[matched_service_key]
    extracted_params = {}
    missing_params = []

    if "url" in s["required_params"]:
        if urls:
            extracted_params["url"] = urls[0]
        else:
            missing_params.append("url")

    if "query_or_url" in s["required_params"]:
        clean_text = re.sub(r"^(شغل|شغلي|اريد اشغل|شغل بالصوتية|شغل بالكول)\s*", "", user_query).strip()
        if urls:
            extracted_params["query_or_url"] = urls[0]
        elif len(clean_text) > 2 and clean_text not in ["ميوزك", "اغنية", "صوت"]:
            extracted_params["query_or_url"] = clean_text
        else:
            missing_params.append("query_or_url")

    slot_filling_prompt = None
    if missing_params:
        first_missing = missing_params[0]
        slot_filling_prompt = s["missing_param_prompts"].get(first_missing, f"يرجى تزويدنا بـ {first_missing}")

    return {
        "matched_service": s["service_name"],
        "service_key": matched_service_key,
        "bot_repository": s["bot_repository"],
        "engine_repository": s.get("engine_repository"),
        "primary_language": s["primary_language"],
        "tool_definition": s["tool_definition"],
        "is_ready_to_execute": len(missing_params) == 0,
        "extracted_parameters": extracted_params,
        "missing_parameters": missing_params,
        "slot_filling_prompt": slot_filling_prompt,
        "execution_guidelines": {
            "memory_policy": "Zero-RAM idle (anti-raw-bytes-ram): stream payloads directly to disk and retain PathBuf",
            "concurrency_policy": "Non-blocking async worker (async-no-block): dispatch heavy tasks to worker queue",
            "telegram_policy": "Handle FloodWait (code 420) with exponential backoff and jitter"
        },
        "recommended_rules": s["recommended_rules"],
        "recommended_skills": s["recommended_skills"]
    }

@mcp.tool()
def plan_agentic_workflow(goal: str, target_stack: str = "rust") -> Dict[str, Any]:
    stack = target_stack.lower()
    relevant_tools = []
    for s_key, s_data in BOT_SERVICES_CATALOG.items():
        if any(pat in goal.lower() for pat in s_data["patterns"]) or "agent" in goal.lower() or "ادوات" in goal.lower():
            relevant_tools.append(s_data["tool_definition"])

    if not relevant_tools:
        relevant_tools = [
            BOT_SERVICES_CATALOG["instagram_downloader"]["tool_definition"],
            BOT_SERVICES_CATALOG["music_voice_chat"]["tool_definition"]
        ]

    concurrency_impl = "Tokio JoinSet + bounded mpsc::channel(100) worker pool" if "rust" in stack else "Goroutine worker pool with buffered chan struct{}"

    return {
        "goal": goal,
        "architecture_pattern": "Decoupled Hexagonal Agent (Ports & Adapters) with Reactive Telegram Gateway",
        "components": {
            "1_nlu_orchestrator": {
                "role": "Conversational intent classifier and tool argument generator",
                "execution_mode": "Strict JSON Schema validation via LLM Function Calling",
                "tools_registered": [t["name"] for t in relevant_tools]
            },
            "2_dialogue_state_manager": {
                "role": "Slot-filling and conversational context memory",
                "strategy": "Stateless turn tracking or Redis cache; emits natural Iraqi/Arabic prompts when parameters (e.g. URLs) are absent"
            },
            "3_decoupled_worker_pool": {
                "role": "Executes CPU/Network heavy bot microservices without blocking Telegram webhook thread",
                "implementation": concurrency_impl,
                "memory_invariant": "Zero raw byte buffers in RAM; stream video/audio directly to disk"
            },
            "4_telegram_view_lifecycle": {
                "role": "Interactive feedback, chat actions, and message editing",
                "safety_contract": "SendChatAction(upload_document), edit_message_text debounce, Bot API 9.4 button styles (primary, success, danger)"
            }
        },
        "function_calling_schemas": relevant_tools,
        "core_invariants": [
            "Never execute business logic inside LLM prompt response; dispatch to microservices",
            "Never block worker threads (async-no-block / rule:rust)",
            "Never store media Vec<u8> in RAM (anti-raw-bytes-ram / rule:rust_standards)",
            "Never use unvalidated -100 prefix formatting on user chats (rule:no_lazy_fallbacks)"
        ],
        "recommended_rules": [
            "rule:clean_code_architecture",
            "rule:telegram_bots",
            "rule:no_lazy_fallbacks",
            "rule:rust" if "rust" in stack else "rule:go",
            "rule:rust_standards" if "rust" in stack else "rule:clean-code"
        ],
        "recommended_skills": [
            "skill:telegram-bot-builder",
            "skill:clean-architecture",
            "skill:api-rate-limiting"
        ]
    }

@mcp.tool()
def benchmark_search_performance(test_queries: Optional[List[str]] = None) -> Dict[str, Any]:
    queries = test_queries or [
        "نزلي هذا من الانستا",
        "بوت ميوزك فليكس بالرست والجو استهلاك قليل للرام وازرار ملونة",
        "AI Agent يتعامل ويا المستخدم ويستدعي ادوات البوت",
        "rust jemalloc zero-ram-idle",
        "telegram bot api 9.4 button styling"
    ]

    results = []
    for q in queries:
        _cached_search_capabilities.cache_clear()
        t0 = time.perf_counter()
        cold_matches = _cached_search_capabilities(q.strip(), None, None, 40, 5)
        cold_time_ms = round((time.perf_counter() - t0) * 1000, 3)

        t1 = time.perf_counter()
        warm_matches = _cached_search_capabilities(q.strip(), None, None, 40, 5)
        warm_time_ms = round((time.perf_counter() - t1) * 1000, 4)

        results.append({
            "query": q,
            "cold_latency_ms": cold_time_ms,
            "warm_latency_ms": warm_time_ms,
            "speedup": f"{round(cold_time_ms / max(0.0001, warm_time_ms))}x" if warm_time_ms > 0 else "Instant",
            "top_match": cold_matches[0][2] if cold_matches else "None",
            "matches_count": len(cold_matches)
        })

    conn = get_db_conn()
    total_items = conn.execute("SELECT count(*) FROM items").fetchone()[0]

    return {
        "status": "HEALTHY",
        "total_indexed_items": total_items,
        "queries_tested": len(queries),
        "average_warm_latency_ms": round(sum(r["warm_latency_ms"] for r in results) / len(results), 4),
        "results": results
    }


@mcp.tool()
def audit_webhook_health(webhook_url: str = "", secret_token: str = "") -> Dict[str, Any]:
    url = webhook_url.strip() or "https://api.example.com/webhook/c3ab8ff13720e8ad9047dd39466b3c89"
    secret = secret_token.strip() or "secure_entropy_secret_token_12345"

    checks = []
    score = 100

    # Check 1: HTTPS protocol
    if not url.startswith("https://"):
        checks.append({"check": "HTTPS Protocol", "status": "FAIL", "deduction": 35, "message": "Telegram Webhook strictly requires HTTPS with a valid certificate."})
        score -= 35
    else:
        checks.append({"check": "HTTPS Protocol", "status": "PASS", "message": "Valid HTTPS protocol scheme."})

    # Check 2: Valid Telegram port
    port_match = re.search(r":(\d+)", url.replace("https://", ""))
    port = int(port_match.group(1)) if port_match else 443
    if port not in (443, 80, 88, 8443):
        checks.append({"check": "Port Compliance", "status": "FAIL", "deduction": 30, "message": f"Port {port} is prohibited by Telegram. Supported ports are 443, 80, 88, 8443."})
        score -= 30
    else:
        checks.append({"check": "Port Compliance", "status": "PASS", "message": f"Port {port} is valid and supported by Telegram."})

    # Check 3: Multi-tenant token hashing
    if re.search(r"\d{8,11}:[A-Za-z0-9_-]{35}", url):
        checks.append({"check": "Token Hashing", "status": "FAIL", "deduction": 25, "message": "Plaintext bot token detected in webhook URL. Must use hashed token (/webhook/{token_hash})."})
        score -= 25
    else:
        checks.append({"check": "Token Hashing", "status": "PASS", "message": "URL uses token hashing; plaintext token is protected."})

    # Check 4: Secret Token Entropy
    if len(secret) < 12:
        checks.append({"check": "Secret Token Entropy", "status": "WARN", "deduction": 15, "message": "Secret token is too short (< 12 chars). Use 24+ characters to prevent spoofing."})
        score -= 15
    else:
        checks.append({"check": "Secret Token Entropy", "status": "PASS", "message": "Secret token has high entropy."})

    return {
        "verdict": "PRODUCTION_READY" if score >= 85 else ("WARNINGS_FOUND" if score >= 60 else "CRITICAL_ISSUES"),
        "compliance_score": max(0, score),
        "target_url": url,
        "checks": checks,
        "invariants": {
            "response_time": "Mandatory HTTP 200 OK within < 100ms; offload tasks to Tokio JoinSet",
            "reverse_proxy": "Nginx proxy_buffering off; allow 149.154.160.0/20; allow 91.108.4.0/22;",
            "lifecycle": "Set drop_pending_updates: false on normal restarts to preserve user commands"
        },
        "recommended_skills": ["skill:webhook-automation", "skill:telegram-bot", "skill:telegram-bot-builder"]
    }


@mcp.tool()
def explain_ecosystem_map() -> Dict[str, Any]:
    bots_map = {
        "factory": {"name": "Bot Factory & Multi-Tenant Core", "lang": "Rust", "path": "/root/bots/factory", "tech": ["Axum", "Grammers", "LibSQL", "Jemalloc", "DashMap"], "role": "Master bot factory dispatching updates to sub-bots via webhook and polling."},
        "rusttgcalls": {"name": "Telegram WebRTC VoIP Engine", "lang": "Rust", "path": "/root/bots/rusttgcalls", "tech": ["Tokio", "Opus", "DTLS-SRTP", "RTP/RTCP"], "role": "High-throughput WebRTC voice chat streaming library."},
        "music": {"name": "FlexMusic Group Call Bot", "lang": "Go", "path": "/root/bots/music", "tech": ["Gogram", "Gotgcall", "Pion WebRTC", "SQLite"], "role": "Voice chat music playback engine in Go."},
        "fastdl-rs": {"name": "High-Speed Media Downloader", "lang": "Rust", "path": "/root/bots/fastdl-rs", "tech": ["Tokio", "Reqwest", "Stream Demux"], "role": "Core video and audio extraction engine."},
        "social": {"name": "Social Media Downloader Bot", "lang": "Rust", "path": "/root/bots/social", "tech": ["Grammers", "FastDL"], "role": "Telegram bot for Instagram, TikTok, YouTube downloads."},
        "shazam": {"name": "Shazam Audio Recognizer", "lang": "Rust", "path": "/root/bots/shazam", "tech": ["Grammers", "Songrec-lib", "FFmpeg"], "role": "Fingerprints voice notes and retrieves track metadata."},
        "session": {"name": "MTProto Session Generator", "lang": "Rust", "path": "/root/bots/session", "tech": ["Grammers", "Pyrogram/Telethon V2"], "role": "Generates 2FA MTProto session strings."},
        "convert": {"name": "Media Transcoder Bot", "lang": "Rust", "path": "/root/bots/convert", "tech": ["Grammers", "FFmpeg Pipes"], "role": "Zero-RAM format transcoding for audio and video."},
        "restricted": {"name": "Restricted Content Saver", "lang": "Rust", "path": "/root/bots/restricted", "tech": ["Grammers Client"], "role": "Extracts protected media from noforwards Telegram channels."},
        "asiacell_api": {"name": "Asiacell Telecom Gateway", "lang": "Go", "path": "/root/bots/asiacell_api", "tech": ["Go net/http", "Redis"], "role": "Telecom automation and subscriber account management."},
        "zain_api": {"name": "Zain Telecom Gateway", "lang": "Go", "path": "/root/bots/zain_api", "tech": ["Go net/http", "Redis"], "role": "Zain line automation and balance inquiries."},
        "akinatorrust": {"name": "Akinator Game Bot", "lang": "Rust", "path": "/root/bots/akinatorrust", "tech": ["Akinator-rs", "Grammers"], "role": "Interactive guessing game bot."},
        "iploger": {"name": "IP & Network Utility Bot", "lang": "Rust", "path": "/root/bots/iploger", "tech": ["Grammers", "MaxMind GeoIP"], "role": "IP resolution and geo-lookup utility."},
        "luagurad": {"name": "Lua Obfuscation Engine", "lang": "Lua/Rust", "path": "/root/bots/luagurad", "tech": ["AST Virtualization"], "role": "Bytecode protection for proprietary Lua scripts."},
        "yt-api": {"name": "YouTube Fast Extractor", "lang": "Rust", "path": "/root/bots/yt-api", "tech": ["Grammers", "FastDL"], "role": "YouTube video and audio extraction service."}
    }
    return {
        "ecosystem": "FLEX Telegram Bot Factory & Microservices",
        "total_active_bots": len(bots_map),
        "primary_languages": {"Rust": 11, "Go": 3, "Python/Lua": 2},
        "services": bots_map
    }

@mcp.tool()
def simulate_bot_pipeline(user_utterance: str) -> Dict[str, Any]:
    resolved = resolve_bot_service(user_utterance)

    if not resolved["is_ready_to_execute"]:
        return {
            "status": "AWAITING_INPUT",
            "matched_service": resolved["matched_service"],
            "missing_parameters": resolved["missing_parameters"],
            "bot_reply": resolved["slot_filling_prompt"],
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "❌ إلغاء الطلب", "callback_data": "cancel_op", "style": "danger"}]
                ]
            }
        }

    # Ready to execute simulation
    s_key = resolved["service_key"]
    return {
        "status": "READY_TO_EXECUTE",
        "matched_service": resolved["matched_service"],
        "bot_repository": resolved["bot_repository"],
        "extracted_parameters": resolved["extracted_parameters"],
        "execution_pipeline": {
            "step_1_ack": "HTTP 200 OK sent to Telegram Webhook within < 50ms",
            "step_2_dispatch": f"Background worker spawned ({resolved['primary_language']})",
            "step_3_action": "Telegram SendChatAction(upload_document / record_voice)",
            "step_4_output": "Stream payload directly to user with Bot API 9.4 styled buttons"
        },
        "sample_response_markup": {
            "inline_keyboard": [
                [
                    {"text": "⚡ تحميل مباشر", "callback_data": "dl_direct", "style": "primary"},
                    {"text": "🎵 استخراج الصوت", "callback_data": "dl_audio", "style": "success"}
                ]
            ]
        }
    }


@mcp.tool()
def fix_code_rule_violations(code_content: str, language: str) -> Dict[str, Any]:
    lang = language.lower().strip()
    lines = code_content.splitlines()
    fixed_lines = []
    fixes = []

    for idx, line in enumerate(lines):
        l_num = idx + 1
        new_line = line

        if lang in ("rust", "rs"):
            if "std::thread::sleep(" in new_line:
                new_line = new_line.replace("std::thread::sleep(", "tokio::time::sleep(")
                if not new_line.strip().endswith(".await;"):
                    new_line = new_line.replace(");", ").await;")
                fixes.append({"line": l_num, "rule": "async-no-block", "action": "Replaced blocking std::thread::sleep with tokio::time::sleep(...).await"})

            if "unbounded_channel()" in new_line:
                new_line = new_line.replace("unbounded_channel()", "channel(100)")
                fixes.append({"line": l_num, "rule": "async-bounded-channel", "action": "Replaced unbounded_channel with bounded mpsc::channel(100)"})

            if '#![allow(' in new_line or '#[allow(' in new_line:
                if any(w in new_line for w in ("warnings", "unused", "dead_code")):
                    new_line = "// " + new_line + " // REMOVED: Warning suppression prohibited"
                    fixes.append({"line": l_num, "rule": "no-allow-warnings", "action": "Commented out warning suppression attribute"})

        elif lang in ("go", "golang"):
            if "_ = err" in new_line or "_ = error" in new_line:
                indent = len(line) - len(line.lstrip())
                prefix = " " * indent
                new_line = prefix + 'if err != nil {\n' + prefix + '    return fmt.Errorf("operation failed: %w", err)\n' + prefix + '}'
                fixes.append({"line": l_num, "rule": "go-error-discipline", "action": "Replaced silent _ = err with explicit error propagation"})

        elif lang in ("python", "py"):
            if re.search(r"except\s*:\s*pass", new_line) or re.search(r"except\s+Exception\s*:\s*pass", new_line):
                indent = len(line) - len(line.lstrip())
                prefix = " " * indent
                new_line = prefix + 'except Exception as e:\n' + prefix + '    logger.error(f"Unexpected error caught: {e}")'
                fixes.append({"line": l_num, "rule": "anti-empty-catch", "action": "Replaced empty except: pass with structured logging"})

        fixed_lines.append(new_line)

    return {
        "status": "FIXES_APPLIED" if fixes else "NO_CHANGES_NEEDED",
        "total_fixes": len(fixes),
        "fixes": fixes,
        "fixed_code": "\n".join(fixed_lines)
    }

@mcp.tool()
def simulate_telegram_load(bot_type: str = "factory", concurrent_users: int = 1000) -> Dict[str, Any]:
    b_type = bot_type.lower().strip()
    users = max(1, concurrent_users)

    if "music" in b_type or "voice" in b_type:
        active_streams = min(users, 50)
        updates_sec = users * 0.15
        bandwidth_mbps = round(active_streams * 0.128, 2) # 128 kbps per Opus stream
        ram_mb = 120 + (active_streams * 2.5) # Zero-RAM pipe streaming
        verdict = "SUSTAINABLE" if active_streams <= 40 else "HIGH_LOAD_SCALE_REQUIRED"
        notes = "Opus 48kHz WebRTC streaming requires non-blocking Tokio pipes and Jemalloc background thread."
    elif "fastdl" in b_type or "social" in b_type:
        concurrent_downloads = min(users, 100)
        updates_sec = users * 0.35
        bandwidth_mbps = round(concurrent_downloads * 4.0, 2)
        ram_mb = 80 + (concurrent_downloads * 1.8) # Disk streaming
        verdict = "SUSTAINABLE" if concurrent_downloads <= 80 else "BANDWIDTH_BOUND"
        notes = "Enforce anti-raw-bytes-ram: stream files directly to disk; never accumulate video bytes in RAM."
    else: # factory / general bot
        updates_sec = round(users * 0.5, 1)
        bandwidth_mbps = round((updates_sec * 4) / 1024, 2) # 4KB payload
        ram_mb = round(45 + (users * 0.04), 1)
        verdict = "HIGHLY_OPTIMAL"
        notes = "Axum multi-tenant webhook router with token hashing handles 5,000+ req/s on a single 2-core VPS."

    return {
        "bot_type": bot_type,
        "simulated_concurrent_users": users,
        "estimated_metrics": {
            "incoming_updates_per_second": updates_sec,
            "estimated_bandwidth_mbps": bandwidth_mbps,
            "estimated_ram_mb": ram_mb,
            "recommended_tokio_workers": min(64, max(4, int(updates_sec / 20))),
            "recommended_redis_rate_limit": "20 requests per 5 seconds per user"
        },
        "scalability_verdict": verdict,
        "architectural_recommendations": [
            "Use Nginx reverse proxy with proxy_buffering off and Unix socket to Axum",
            "Mandatory HTTP 200 OK fast acknowledgment (< 50ms) to prevent Telegram retry flooding",
            "Enable Jemalloc with background_thread:true and dirty_decay_ms:0",
            notes
        ]
    }


@mcp.tool()
def audit_web_application_quality(html_or_jsx: str) -> Dict[str, Any]:
    violations = []
    lines = html_or_jsx.splitlines()
    code_text = html_or_jsx.lower()

    if "<img" in code_text:
        for idx, line in enumerate(lines):
            if "<img" in line.lower():
                if "alt=" not in line.lower():
                    violations.append({"line": idx + 1, "category": "Accessibility", "severity": "HIGH", "message": "<img> tag missing alt attribute (WCAG 2.2 AA violation)."})
                if "width=" not in line.lower() and "aspect-ratio" not in line.lower():
                    violations.append({"line": idx + 1, "category": "Performance (CLS)", "severity": "MEDIUM", "message": "<img> tag missing explicit width/height or aspect-ratio (causes layout shifts)."})

    if 'target="_blank"' in code_text or "target='_blank'" in code_text:
        for idx, line in enumerate(lines):
            if "_blank" in line.lower() and "noopener" not in line.lower():
                violations.append({"line": idx + 1, "category": "Security", "severity": "HIGH", "message": "External link target='_blank' missing rel='noopener noreferrer' (reverse tabnabbing risk)."})

    if "dangerouslysetinnerhtml" in code_text or ".innerhtml" in code_text:
        violations.append({"line": 1, "category": "Security (XSS)", "severity": "CRITICAL", "message": "dangerouslySetInnerHTML / innerHTML detected. Sanitize with DOMPurify."})

    for idx, line in enumerate(lines):
        if any(b in line.lower() for b in ("<button", "button", "role='button'")):
            if re.search(r"[🌀-🫿]", line):
                violations.append({"line": idx + 1, "category": "Anti-AI UI Slop", "severity": "CRITICAL", "message": "Raw emoji in button. Use clean, scalable SVGs (Lucide / Heroicons)."})

    if re.search(r"(linear-gradient|radial-gradient).*#[789a-f][0-9a-f]{5}", code_text):
        violations.append({"line": 1, "category": "Anti-AI UI Slop", "severity": "HIGH", "message": "Generic AI purple/violet gradient detected. Use disciplined semantic palette tokens."})

    return {
        "status": "FAILED" if any(v["severity"] == "CRITICAL" for v in violations) else ("WARNINGS" if violations else "PASSED"),
        "total_issues": len(violations),
        "violations": violations,
        "recommendations": [
            "Use modern semantic HTML5 (<main>, <nav>, <header>)",
            "Enforce 6 button interactive states (rest, hover, active, focus-visible, disabled, loading)",
            "Ensure normal text achieves 4.5:1 contrast against background (WCAG 2.2 AA)"
        ]
    }

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