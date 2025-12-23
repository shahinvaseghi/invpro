# Quick Start - Standards Checker

شروع سریع با ابزار Standards Checker در **3 دقیقه** ⚡

---

## 🚀 نصب (30 ثانیه)

```bash
# فقط یک دستور!
./install_checker.sh
```

این دستور:
- ✅ Python و Git را چک می‌کند
- ✅ Permissions را تنظیم می‌کند  
- ✅ Pre-commit hook را نصب می‌کند
- ✅ Directory گزارش‌ها را می‌سازد
- ✅ یک تست می‌کند

---

## 💻 اولین اجرا (1 دقیقه)

### چک کردن یک ماژول کوچک:

```bash
python check_standards.py --module shared
```

**خروجی مثال**:
```
======================================================================
          ERP Standards Checker
======================================================================

📁 Scanning 25 files...
   - Python files: 18
   - Template files: 7

Checking Python files...
Checking Template files...

======================================================================
                         Results
======================================================================

Summary:
  Total Issues: 3
  Errors: 1
  Warnings: 2

✅ PASSED - All checks passed
```

### چک کردن همه پروژه:

```bash
python check_standards.py
```

**⚠️ توجه**: ممکن است کمی طول بکشد (2-3 دقیقه)

---

## 🎯 سناریوهای معمول

### سناریو 1: قبل از Commit

```bash
# دستی چک کنید
python check_standards.py

# اگر مشکلی نبود:
git add .
git commit -m "feat: add new feature"

# اگر مشکل بود:
# مشکلات را رفع کنید و دوباره تلاش کنید
```

**💡 نکته**: Pre-commit hook خودکار چک می‌کند!

### سناریو 2: بررسی یک Feature جدید

```bash
# فقط فایل‌های تغییر یافته را چک کنید
git diff --name-only | grep '\.py$' | xargs python check_standards.py
```

### سناریو 3: گزارش هفتگی

```bash
# تولید گزارش
python check_standards.py --json reports/report_$(date +%Y%m%d).json

# مشاهده گزارش
cat reports/report_*.json | jq '.summary'
```

---

## 🔍 فهم خروجی

### Severity Levels:

| رنگ | Severity | معنی | Action |
|-----|----------|------|--------|
| 🔴 | CRITICAL | مشکل امنیتی جدی | **فوری رفع کنید** |
| 🔴 | ERROR | نقض استانداردها | باید رفع شود |
| 🟡 | WARNING | توصیه می‌شود | بهتر است رفع شود |
| 🔵 | INFO | اطلاعاتی | اختیاری |

### مثال Issue:

```
[ERROR] inventory/views/master_data.py:45
  Category: Base Classes
  Class 'ItemTypeListView' uses 'ListView' instead of 'BaseListView'
  💡 Suggestion: Replace with 'from shared.views.base import BaseListView'
```

**چطور رفع کنیم**:
```python
# ❌ قبل
from django.views.generic import ListView

class ItemTypeListView(ListView):
    model = ItemType

# ✅ بعد
from shared.views.base import BaseListView

class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']
    feature_code = 'inventory.master.item_types'
```

---

## 🛠️ مشکلات رایج و راه‌حل

### 1. "python: command not found"

**راه‌حل**:
```bash
# بررسی نصب Python
python --version
python3 --version

# استفاده از python3
python3 check_standards.py
```

### 2. "Permission denied"

**راه‌حل**:
```bash
chmod +x check_standards.py
./check_standards.py
```

### 3. خیلی مشکل پیدا می‌کند!

**راه‌حل**: نگران نباشید! عادی است:
```bash
# فقط CRITICAL و ERROR ها را ببینید
python check_standards.py | grep -E "CRITICAL|ERROR"

# یا یک ماژول در یک زمان
python check_standards.py --module inventory
```

### 4. نمی‌خواهم pre-commit hook فعال باشد

**راه‌حل**:
```bash
# غیرفعال موقت
git commit --no-verify -m "message"

# حذف hook
rm .git/hooks/pre-commit
```

---

## 📚 مراحل بعدی

### برای یادگیری بیشتر:

1. **مستندات کامل**: `STANDARDS_CHECKER_README.md`
2. **خلاصه**: `CHECKER_SUMMARY.md`
3. **استانداردهای توسعه**: `DEVELOPMENT_GUIDE.md`

### برای استفاده پیشرفته:

```bash
# خروجی JSON
python check_standards.py --json report.json

# مقایسه گزارش‌ها
python compare_reports.py old.json new.json

# Verbose mode
python check_standards.py --verbose
```

---

## 🎓 Best Practices

### ✅ DO:
- همیشه قبل از commit چک کنید
- مشکلات CRITICAL و ERROR را فوراً رفع کنید
- WARNING ها را هم در نظر بگیرید
- گزارش هفتگی تولید کنید

### ❌ DON'T:
- Pre-commit hook را bypass نکنید (بدون دلیل)
- مشکلات امنیتی را نادیده نگیرید
- همه WARNING ها را ignore نکنید
- بدون چک commit نکنید

---

## 💡 Tips & Tricks

### Tip 1: فقط فایل‌های خودتان را چک کنید

```bash
# فایل‌های اضافه شده به staging
git diff --cached --name-only --diff-filter=ACM | \
    grep '\.py$\|\.html$' | \
    xargs -I {} python check_standards.py {}
```

### Tip 2: خروجی را save کنید

```bash
python check_standards.py > check_result.txt 2>&1
less check_result.txt
```

### Tip 3: Integration با IDE

در VS Code، اضافه کنید به `tasks.json`:
```json
{
  "label": "Check Standards",
  "type": "shell",
  "command": "python check_standards.py --module ${fileBasenameNoExtension}",
  "group": "test"
}
```

---

## 🏆 اولین موفقیت

هدف: **صفر ERROR** در ماژول خودتان!

```bash
# 1. چک کنید
python check_standards.py --module my_module

# 2. مشکلات را رفع کنید
# ...

# 3. دوباره چک کنید
python check_standards.py --module my_module

# 4. تبریک! 🎉
```

وقتی این پیام را دیدید، موفق شدید:
```
✅ No issues found! All standards met.
```

---

## 📞 کمک بیشتر

- 📖 Documentation کامل: `STANDARDS_CHECKER_README.md`
- 💬 سوال دارید؟ از تیم بپرسید
- 🐛 Bug پیدا کردید؟ گزارش دهید
- 💡 ایده دارید؟ به اشتراک بگذارید

---

**شروع کنید**: `./install_checker.sh` 🚀

---

**آخرین به‌روزرسانی**: 2024-12-23  
**نسخه**: 1.0

