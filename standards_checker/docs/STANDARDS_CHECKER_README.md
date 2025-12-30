# Standards Checker - راهنمای استفاده

ابزار خودکار برای چک کردن رعایت استانداردهای توسعه پروژه ERP

## 📋 ویژگی‌ها

### ✅ چک‌های موجود

1. **Base Classes**
   - تشخیص استفاده مستقیم از Django generic views
   - پیشنهاد استفاده از Base Classes

2. **Templates**
   - شناسایی inline styles
   - شناسایی inline JavaScript (onclick, onchange, etc.)
   - بررسی استفاده از generic templates
   - چک کردن load template tags

3. **Documentation**
   - بررسی وجود docstrings در classes و functions
   - پیشنهاد format صحیح

4. **Security**
   - شناسایی SQL injection vulnerabilities
   - تشخیص استفاده نامناسب از |safe و mark_safe
   - یافتن hardcoded secrets (SECRET_KEY, PASSWORD, API_KEY)

5. **Naming Conventions**
   - بررسی PascalCase برای classes
   - بررسی snake_case برای functions

## 🚀 نصب و راه‌اندازی

### نصب dependencies (اختیاری)

```bash
# اگر می‌خواهید coverage هم چک شود:
pip install coverage
```

### دادن permission اجرا

```bash
chmod +x check_standards.py
```

## 💻 استفاده

### حالت‌های مختلف اجرا

#### 1. چک کردن همه پروژه

```bash
python check_standards.py
```

#### 2. چک کردن یک ماژول خاص

```bash
python check_standards.py --module inventory
python check_standards.py --module production
python check_standards.py --module shared
```

#### 3. خروجی جزئی (Verbose)

```bash
python check_standards.py --verbose
python check_standards.py -v
```

#### 4. خروجی JSON (برای CI/CD)

```bash
python check_standards.py --json report.json
```

#### 5. Auto-fix (در حال توسعه)

```bash
python check_standards.py --fix
```

## 📊 نمونه خروجی

### خروجی عادی

```
======================================================================
          ERP Standards Checker
======================================================================

📁 Scanning 245 files...
   - Python files: 180
   - Template files: 65

Checking Python files...
Checking Template files...

======================================================================
                         Results
======================================================================

Summary:
  Total Issues: 23
  Critical: 2
  Errors: 8
  Warnings: 13
  Auto-fixable: 3

Issues:

Base Classes (5 issues)
[ERROR] inventory/views/master_data.py:45
  Category: Base Classes
  Class 'ItemTypeListView' uses 'ListView' instead of 'BaseListView'
  💡 Suggestion: Replace 'from django.views.generic import ListView' with 'from shared.views.base import BaseListView'

Template - CSS (8 issues)
[ERROR] inventory/templates/inventory/items.html:67
  Category: Template - CSS
  Inline style detected
  💡 Suggestion: Move styles to shared.css

Security - secrets (2 issues)
[CRITICAL] config/settings/development.py:12
  Category: Security - secrets
  Hardcoded SECRET_KEY - use environment variables
  💡 Suggestion: Review security best practices in DEVELOPMENT_GUIDE.md

❌ FAILED - Fix errors before committing
```

### خروجی JSON

```json
{
  "summary": {
    "total_issues": 23,
    "critical": 2,
    "errors": 8,
    "warnings": 13,
    "info": 0,
    "auto_fixable": 3
  },
  "issues": [
    {
      "file": "inventory/views/master_data.py",
      "line": 45,
      "severity": "error",
      "category": "Base Classes",
      "message": "Class 'ItemTypeListView' uses 'ListView' instead of 'BaseListView'",
      "suggestion": "Replace 'from django.views.generic import ListView' with 'from shared.views.base import BaseListView'",
      "auto_fixable": false
    }
  ]
}
```

## 🔧 Severity Levels

| Level | معنی | Action Required |
|-------|------|-----------------|
| **CRITICAL** | مشکل امنیتی جدی | باید حتماً قبل از commit رفع شود |
| **ERROR** | نقض استانداردها | باید رفع شود |
| **WARNING** | توصیه می‌شود رفع شود | بهتر است رفع شود |
| **INFO** | اطلاعاتی | اختیاری |

## 🎯 استفاده در CI/CD

### GitHub Actions

```yaml
# .github/workflows/standards-check.yml
name: Standards Check

on: [push, pull_request]

jobs:
  check-standards:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Run Standards Checker
        run: |
          python check_standards.py --json report.json
      
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: standards-report
          path: report.json
```

### GitLab CI

```yaml
# .gitlab-ci.yml
standards-check:
  stage: test
  script:
    - python check_standards.py --json report.json
  artifacts:
    reports:
      junit: report.json
```

## 🪝 Pre-commit Hook

برای اجرای خودکار قبل از هر commit:

```bash
# نصب pre-commit hook
cp pre-commit.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

محتوای `pre-commit.sh`:

```bash
#!/bin/bash

echo "Running standards checker..."
python check_standards.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Standards check failed!"
    echo "Please fix the issues before committing."
    echo ""
    exit 1
fi

echo "✅ Standards check passed!"
exit 0
```

## 📝 گزارش‌های دوره‌ای

### چک کردن هفتگی

```bash
# اسکریپت برای چک کردن هفتگی
#!/bin/bash

DATE=$(date +%Y%m%d)
REPORT_DIR="reports"

mkdir -p $REPORT_DIR

echo "Running weekly standards check..."
python check_standards.py --json $REPORT_DIR/report_$DATE.json

echo "Report saved to $REPORT_DIR/report_$DATE.json"
```

### مقایسه گزارش‌ها

```bash
# مقایسه دو گزارش
python compare_reports.py report_20241201.json report_20241208.json
```

## 🔍 تفسیر نتایج

### مشکلات رایج

#### 1. استفاده از ListView به جای BaseListView

```python
# ❌ اشتباه
from django.views.generic import ListView

class ItemTypeListView(ListView):
    model = ItemType

# ✅ درست
from shared.views.base import BaseListView

class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']
    feature_code = 'inventory.master.item_types'
```

#### 2. Inline Styles در Template

```django
{# ❌ اشتباه #}
<div style="padding: 20px; margin: 10px;">

{# ✅ درست #}
<div class="card-body">
```

#### 3. Hardcoded Secrets

```python
# ❌ اشتباه
SECRET_KEY = 'django-insecure-my-secret-key'

# ✅ درست
import os
SECRET_KEY = os.getenv('SECRET_KEY')
```

## 🐛 عیب‌یابی

### مشکل: ابزار فایل‌های خاصی را نادیده می‌گیرد

بررسی کنید که فایل در `EXEMPT_MODULES` نباشد:

```python
EXEMPT_MODULES = {'shared', 'migrations', 'tests'}
```

### مشکل: False positives زیاد

می‌توانید در کد ابزار، patterns را تنظیم کنید.

## 📈 بهبودهای آینده

- [ ] Auto-fix برای مشکلات ساده
- [ ] چک کردن test coverage
- [ ] Integration با linters (flake8, pylint)
- [ ] Dashboard برای tracking مشکلات در طول زمان
- [ ] Custom rules برای هر پروژه
- [ ] Performance profiling
- [ ] Git blame integration

## 🤝 مشارکت

برای اضافه کردن checker جدید:

1. کلاس جدید بسازید (مثلاً `MyChecker`)
2. متد `check_file(self, file_path)` را پیاده‌سازی کنید
3. لیستی از `Issue` برگردانید
4. در `StandardsChecker.check_all()` اضافه کنید

مثال:

```python
class MyCustomChecker:
    def check_file(self, file_path: str) -> List[Issue]:
        issues = []
        
        # منطق چک کردن شما
        
        return issues
```

## 📞 پشتیبانی

در صورت مشکل:
1. مستندات `DEVELOPMENT_GUIDE.md` را بررسی کنید
2. با تیم هماهنگ کنید
3. Issue در Git ایجاد کنید

---

**نسخه**: 1.0  
**تاریخ**: 2024-12-23  
**نگهدارنده**: تیم توسعه ERP

