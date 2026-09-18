# Antigravity Agent Customizations (Global Rules & Skills)

مستودع خاص يحتوي على كافة المهارات والقوانين الخاصة بـ Antigravity AI جاهزة للتثبيت الفوري في أي خادم أو بيئة.

---

## ⚡ أمر واحد للتثبيت المباشر على أي خادم (One-Liner Install)

انسخ والصق هذا الأمر مباشرة في الطرفية (Terminal) على أي خادم جديد لتنزيل جميع المهارات والقوانين ونقلها مباشرة إلى `~/.gemini/config/` (Global):

```bash
git clone https://github.com/FLEX-GHOST/antigravity-customizations.git /tmp/cust && mkdir -p ~/.gemini/config && cp -rf /tmp/cust/{rules,skills,plugins} ~/.gemini/config/ && rm -rf /tmp/cust && echo "=== ALL SKILLS & RULES INSTALLED TO GLOBAL SUCCESSFULLY ==="
```

---

## 📂 محتويات المستودع:
- `rules/`: جميع القوانين الـ 27 (Anti-AI slop, Rust standards, Go, Architecture, Security, Telegram).
- `skills/`: جميع المهارات الـ 95 (Full domain skills).
- `plugins/`: الإضافات (مثل `securecoder`).
- `install.sh`: سكربت التثبيت التلقائي.
