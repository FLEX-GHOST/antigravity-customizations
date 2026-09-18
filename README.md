# Antigravity Agent Customizations

[![Rules](https://img.shields.io/badge/Rules-27%20Standards-blue?style=flat-square)](./rules)
[![Skills](https://img.shields.io/badge/Skills-95%20Skills-10b981?style=flat-square)](./skills)
[![Plugins](https://img.shields.io/badge/Plugins-SecureCoder-8b5cf6?style=flat-square)](./plugins)
[![Platform](https://img.shields.io/badge/Platform-Antigravity%20IDE-black?style=flat-square&logo=linux&logoColor=white)]()

مستودع شامل للقوانين والمعايير الهندسية والمهارات البرمجية الخاصة بوكيل **Antigravity AI**، مهيأة للتثبيت الفوري في أي خادم أو بيئة عمل.

---

## التثبيت الفوري بأمر واحد (One-Liner Installation)

انسخ الأمر التالي وشغّله في الطرفية (Terminal) على أي خادم لتثبيت كافة المهارات والقوانين مباشرة داخل المسار العام <span dir="ltr"><code>~/.gemini/config/</code></span>:

```bash
git clone https://github.com/FLEX-GHOST/antigravity-customizations.git /tmp/cust && mkdir -p ~/.gemini/config && cp -rf /tmp/cust/{rules,skills,plugins} ~/.gemini/config/ && rm -rf /tmp/cust && echo "=== ALL SKILLS & RULES INSTALLED TO GLOBAL SUCCESSFULLY ==="
```

---

## محتويات المستودع

| المجلد / الملف | الفئة | العدد | الوصف |
| :--- | :--- | :--- | :--- |
| `rules/` | معايير وقوانين | 27 | هندسة Rust و Go، بنية الكود النظيف، مكافحة حشو الـ AI، وضوابط بوتات تلغرام والأمان. |
| `skills/` | مهارات تخصصية | 95 | مهارات الأنظمة، الهندسة العكسية، حماية الشبكات، قواعد البيانات، والتصميم والواجهات. |
| `plugins/` | إضافات الوكيل | 1 | حزمة الفحص والتدقيق الأمني التلقائي (SecureCoder). |
| `install.sh` | سكربت محلي | 1 | أداة تثبيت تنفيذية محلية بديلة. |

---

## التحقق بعد التثبيت

للتأكد من اكتمال التثبيت، يمكنك فحص المسار:

```bash
ls -la ~/.gemini/config/rules ~/.gemini/config/skills
```
