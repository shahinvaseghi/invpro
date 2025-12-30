# 🔍 Standards Checker

ابزار خودکار برای چک کردن رعایت استانداردهای پروژه ERP

---

## 📁 ساختار فولدر

```
standards_checker/
├── README.md                           # همین فایل
├── HOW_TO_USE.md                       # راهنمای استفاده سریع ⭐
├── FUTURE_CHECKS.md                    # چک‌های پیشنهادی برای آینده 📋
│
├── check_standards.py                  # Core checker
├── interactive_checker_v2.py           # Interactive checker (curses) ⭐
│
├── check_manual.sh                     # Launcher سریع ⭐
├── install_checker.sh                  # نصب و راه‌اندازی
├── pre-commit.sh                       # Git pre-commit hook
│
├── docs/                               # مستندات
│   ├── README_STANDARDS_CHECKER.md      # Overview کلی
│   ├── STANDARDS_CHECKER_README.md      # راهنمای جامع
│   ├── CHECKER_SUMMARY.md               # خلاصه فنی
│   └── CHECKER_QUICK_START.md           # شروع سریع
│
├── tools/                              # ابزارهای کمکی
│   ├── compare_reports.py               # مقایسه گزارش‌ها
│   ├── check.sh                         # چک سریع
│   └── weekly_report.sh                 # گزارش هفتگی
│
└── reports/                            # گزارش‌های تولید شده
    └── .gitkeep
```

---

## ⚡ شروع سریع

### نصب (اولین بار):

```bash
cd standards_checker
./install_checker.sh
```

---

## 🛠️ سه ابزار اصلی

### 🔹 ابزار 0: چک تعاملی (Interactive Checker) ⭐ RECOMMENDED!

**ساده‌ترین روش** برای چک کردن فایل‌ها - با UI گرافیکی کامل!

```bash
# راه 1: با اسکریپت launcher (آسان‌ترین) ⭐
./check_manual.sh

# راه 2: مستقیم Python
python3 interactive_checker_v2.py
```

**قابلیت‌ها**:
- ✅ **چک دستی (Manual Check)** - انتخاب و چک یک فایل با File Browser
- ✅ **چک ماژول (Module Check)** - چک تمام فایل‌های یک ماژول یکجا ⭐
- ✅ **چک کامل (All Check)** - چک کل پروژه با یک کلید ⭐
- ✅ **نمایش نتایج جامع** - گزارش کامل با تفکیک فایل و severity
- ✅ **قابلیت اسکرول** - مشاهده راحت تمام ایرادات (↑↓ PgUp/PgDn)
- ✅ **رنگ‌بندی حرفه‌ای** - Critical, Error, Warning
- ✅ **پایدار و سریع** - استفاده از curses (کتابخانه استاندارد Python)
- ✅ **بدون نیاز به نصب** - فقط Python 3، بدون dependency!

**📖 راهنمای کامل: [HOW_TO_USE.md](HOW_TO_USE.md)**

**مثال خروجی**:
```
RESULTS
════════════════════════════════════════════

Total Issues: 4
  Warnings: 4

────────────────────────────────────────────

[WARNING] (4 issues)

  1. Line 45
     Variable name 'x' is too short. Use descriptive names.
     Code:
       def calculate(x):
       
  2. Line 67
     Function 'getData' should use snake_case naming
     
────────────────────────────────────────────
[↑/↓] Scroll  [PgUp/PgDn] Page  [Q] Back
            Line 1-10/50
```

---

## 🛠️ دو ابزار اصلی

### 🔹 ابزار 1: چک سریع (`check.sh`)

**استفاده روزانه برای توسعه‌دهندگان**

```bash
# چک کردن فایل‌های تغییر یافته در git
./tools/check.sh

# چک کردن یک ماژول خاص
./tools/check.sh inventory

# چک کردن همه پروژه
./tools/check.sh all
```

**قابلیت‌ها**:
- ✅ چک فایل‌های staged در git
- ✅ چک یک ماژول خاص
- ✅ خروجی ساده و قابل فهم
- ✅ نمایش تعداد مشکلات
- ✅ Auto-detect ماژول فعلی

**مثال خروجی**:
```
🔍 Checking staged files...

✓ 3 files checked
✗ 2 issues found

inventory/views/items.py:
  [ERROR] Line 45: Using ListView instead of BaseListView

templates/items.html:
  [ERROR] Line 67: Inline style detected

💡 Fix issues before committing
```

---

### 🔹 ابزار 2: گزارش هفتگی (`weekly_report.sh`)

**استفاده برای tracking پیشرفت**

```bash
# تولید گزارش هفتگی
./tools/weekly_report.sh

# مشاهده گزارش‌های قبلی
./tools/weekly_report.sh list

# مقایسه با هفته قبل
./tools/weekly_report.sh compare
```

**قابلیت‌ها**:
- ✅ تولید گزارش JSON با تاریخ
- ✅ مقایسه با گزارش قبلی
- ✅ نمایش روند پیشرفت
- ✅ خلاصه آماری
- ✅ ذخیره تاریخچه

**مثال خروجی**:
```
📊 Weekly Standards Report
Date: 2024-12-23

Current Status:
  Total Issues: 15
  Critical: 1
  Errors: 5
  Warnings: 9

Compared to last week:
  ↓ -8 issues (improvement!)
  ↓ -2 errors
  ↓ -6 warnings

Top Categories:
  1. Template - CSS: 5 issues
  2. Base Classes: 3 issues
  3. Documentation: 4 issues

📈 Trend: Improving ✅
```

---

## 🎯 سناریوهای استفاده

### سناریو 1: قبل از Commit

```bash
# روش 1: دستی
cd standards_checker
./tools/check.sh

# روش 2: خودکار (با pre-commit hook)
git commit -m "message"
# خودکار چک می‌شود
```

### سناریو 2: کار روی Feature جدید

```bash
# وقتی روی inventory کار می‌کنید
cd standards_checker
./tools/check.sh inventory

# یا اگر در فولدر inventory هستید
cd inventory
../standards_checker/tools/check.sh
```

### سناریو 3: Code Review

```bash
# قبل از merge
cd standards_checker
./tools/check.sh production

# بررسی فایل‌های خاص
python check_standards.py --verbose
```

### سناریو 4: جلسه هفتگی

```bash
# آماده‌سازی گزارش
cd standards_checker
./tools/weekly_report.sh

# نمایش به تیم
cat reports/report_YYYYMMDD.json | jq '.summary'
```

---

## 📚 مستندات کامل

| فایل | محتوا | مخاطب |
|------|-------|--------|
| [`docs/CHECKER_QUICK_START.md`](docs/CHECKER_QUICK_START.md) | شروع در 3 دقیقه | تازه‌واردها ⭐ |
| [`docs/README_STANDARDS_CHECKER.md`](docs/README_STANDARDS_CHECKER.md) | Overview کلی | همه ⭐ |
| [`docs/STANDARDS_CHECKER_README.md`](docs/STANDARDS_CHECKER_README.md) | راهنمای جامع | توسعه‌دهندگان |
| [`docs/CHECKER_SUMMARY.md`](docs/CHECKER_SUMMARY.md) | خلاصه فنی | توسعه‌دهندگان |

---

## 🔍 چی چک می‌کنه؟

| Category | توضیح | Severity |
|----------|-------|----------|
| **Base Classes** | استفاده از `BaseListView` بجای `ListView` | ERROR |
| **Template - CSS** | Inline styles در HTML | ERROR |
| **Template - JavaScript** | Inline event handlers | ERROR |
| **Security - SQL** | SQL injection | CRITICAL |
| **Security - Secrets** | Hardcoded secrets | CRITICAL |
| **Documentation** | Missing docstrings | WARNING |
| **Naming** | PascalCase, snake_case | WARNING |

---

## 🎓 مثال‌های عملی

### مثال 1: چک سریع قبل از commit

```bash
# در هر جای پروژه
cd standards_checker
./tools/check.sh

# خروجی:
# ✓ All checks passed!
# Ready to commit
```

### مثال 2: چک یک ماژول

```bash
cd standards_checker
./tools/check.sh inventory

# خروجی:
# Checking module: inventory
# ✗ 3 issues found
# Fix issues before committing
```

### مثال 3: گزارش هفتگی

```bash
cd standards_checker
./tools/weekly_report.sh

# خروجی:
# Report saved to: reports/report_20241223.json
# 
# Summary:
#   Total Issues: 15 (-8 from last week)
#   Status: Improving ✅
```

---

## 🔧 Configuration

### تنظیمات ابزار چک سریع

در `tools/check.sh` می‌توانید تنظیم کنید:

```bash
# فقط CRITICAL و ERROR را نشان بده
SHOW_WARNINGS=false

# تعداد issues نمایش داده شود
MAX_ISSUES_DISPLAY=5

# رنگ خروجی
COLORED_OUTPUT=true
```

### تنظیمات گزارش هفتگی

در `tools/weekly_report.sh` می‌توانید تنظیم کنید:

```bash
# مسیر ذخیره گزارش‌ها
REPORTS_DIR="reports"

# فرمت نام فایل
REPORT_FORMAT="report_%Y%m%d.json"

# خودکار مقایسه با قبل
AUTO_COMPARE=true
```

---

## 💡 Tips & Tricks

### Tip 1: Alias برای استفاده راحت‌تر

اضافه کنید به `~/.bashrc` یا `~/.zshrc`:

```bash
alias check='cd ~/invproj/standards_checker && ./tools/check.sh'
alias weekly='cd ~/invproj/standards_checker && ./tools/weekly_report.sh'
```

بعد می‌توانید از هر جا:
```bash
check inventory
weekly
```

### Tip 2: Integration با VS Code

در `.vscode/tasks.json`:
```json
{
  "label": "Check Standards",
  "type": "shell",
  "command": "${workspaceFolder}/standards_checker/tools/check.sh",
  "group": "test",
  "presentation": {
    "echo": true,
    "reveal": "always",
    "focus": false,
    "panel": "shared"
  }
}
```

### Tip 3: CI/CD Integration

در `.gitlab-ci.yml` یا `.github/workflows/check.yml`:
```yaml
standards-check:
  script:
    - cd standards_checker
    - python check_standards.py --json ../reports/ci_report.json
```

---

## 🐛 عیب‌یابی

### مشکل: "Permission denied"

```bash
cd standards_checker
chmod +x install_checker.sh check_standards.py
chmod +x tools/*.sh
```

### مشکل: "Module not found"

```bash
# مطمئن شوید در فولدر پروژه هستید
cd /home/shahin/invproj
cd standards_checker
./tools/check.sh inventory
```

### مشکل: خیلی مشکل پیدا می‌کند

```bash
# فقط CRITICAL و ERROR
cd standards_checker
python check_standards.py | grep -E "CRITICAL|ERROR"

# یا یک ماژول در یک زمان
./tools/check.sh shared
```

---

## 📈 Roadmap

### v1.0 (فعلی) ✅
- [x] 5 Checker اصلی
- [x] Pre-commit hook
- [x] Report comparison
- [x] ابزار check سریع
- [x] ابزار weekly report

### v1.1 (آینده نزدیک) 🚧
- [ ] Auto-fix برای مشکلات ساده
- [ ] Test coverage check
- [ ] Interactive mode
- [ ] Email notifications

### v2.0 (آینده) 💡
- [ ] Web dashboard
- [ ] Real-time monitoring
- [ ] AI suggestions
- [ ] Team statistics

---

## 🤝 مشارکت

برای بهبود ابزار:

1. **گزارش Bug**: Issue در Git
2. **پیشنهاد Feature**: با تیم هماهنگ کنید
3. **بهبود مستندات**: Pull Request

---

## 🔮 توسعه آینده

### چک‌های پیشنهادی

برای دیدن لیست کامل چک‌هایی که باید اضافه شوند، فایل **[FUTURE_CHECKS.md](FUTURE_CHECKS.md)** را مطالعه کنید.

**خلاصه چک‌های پیشنهادی:**
- 🧪 Testing Standards (Unit Tests, Coverage)
- ⚡ Performance Checks (select_related, prefetch_related, N+1 queries)
- 🌐 API Standards (Response format, Versioning)
- 💾 Database & Migration (Indexes, Best practices)
- 📊 Error Handling & Logging
- 🔧 Shared Components Usage (Filter Functions, Mixins, JS files)
- 🔒 Security Enhancements (CSRF, Authentication)
- 📝 Code Quality (Duplication, Complexity)
- 🔄 Git Workflow (Commit messages, Branch naming)

**وضعیت فعلی**: حدود 30-40% از استانداردهای `DEVELOPMENT_GUIDE.md` پوشش داده می‌شود.

---

## 📞 پشتیبانی

- 📖 مستندات کامل: `docs/`
- 🚀 Quick Start: `docs/CHECKER_QUICK_START.md`
- 🔮 Future Checks: `FUTURE_CHECKS.md`
- 💬 تیم توسعه
- 🐛 Git Issues

---

## ⚙️ دستورات مفید

```bash
# نصب
./install_checker.sh

# چک سریع
./tools/check.sh

# چک ماژول خاص
./tools/check.sh inventory

# گزارش هفتگی
./tools/weekly_report.sh

# مقایسه گزارش‌ها
./tools/compare_reports.py report1.json report2.json

# چک دستی با گزینه‌ها
python check_standards.py --verbose
python check_standards.py --json report.json
python check_standards.py --module shared
```

---

**شروع کنید**: `./install_checker.sh` 🚀

---

**نسخه**: 1.0  
**تاریخ**: 2024-12-23  
**وضعیت**: ✅ Production Ready  
**نگهدارنده**: تیم توسعه ERP

