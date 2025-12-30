# 🎯 Standards Checker - ابزار چک خودکار استانداردها

## خلاصه

یک ابزار کامل Python برای **چک خودکار رعایت استانداردهای پروژه** که به صورت CLI، Pre-commit Hook و CI/CD قابل استفاده است.

---

## 🎁 فایل‌های ایجاد شده

| فایل | نوع | حجم | توضیح |
|------|-----|------|--------|
| `check_standards.py` | اصلی | ~600 خط | ابزار اصلی چک کردن |
| `install_checker.sh` | نصب | ~100 خط | نصب خودکار |
| `pre-commit.sh` | Hook | ~50 خط | Git pre-commit hook |
| `compare_reports.py` | ابزار | ~250 خط | مقایسه گزارش‌ها |
| `STANDARDS_CHECKER_README.md` | مستندات | کامل | راهنمای جامع |
| `CHECKER_SUMMARY.md` | خلاصه | جامع | خلاصه قابلیت‌ها |
| `CHECKER_QUICK_START.md` | شروع سریع | ساده | شروع در 3 دقیقه |
| این فایل | Overview | خلاصه | نمای کلی |

---

## ⚡ شروع سریع

### نصب:
```bash
./install_checker.sh
```

### اجرا:
```bash
# همه پروژه
python check_standards.py

# یک ماژول
python check_standards.py --module inventory
```

---

## 🔍 چک‌های موجود

| Category | چه چیزی چک می‌کند | Severity |
|----------|-------------------|----------|
| **Base Classes** | استفاده از BaseListView بجای ListView | ERROR |
| **Template - CSS** | inline styles | ERROR |
| **Template - JavaScript** | inline event handlers | ERROR |
| **Template - Structure** | استفاده از generic templates | WARNING |
| **Documentation** | وجود docstrings | WARNING |
| **Security - SQL** | SQL injection | CRITICAL |
| **Security - XSS** | استفاده نامناسب از \|safe | CRITICAL |
| **Security - Secrets** | hardcoded secrets | CRITICAL |
| **Naming - Class** | PascalCase | WARNING |
| **Naming - Function** | snake_case | WARNING |

---

## 📊 نمونه خروجی

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
  Critical: 2      # 🔴 باید حتماً رفع شود
  Errors: 8        # 🔴 باید رفع شود
  Warnings: 13     # 🟡 بهتر است رفع شود
  Auto-fixable: 3  # 🟢 قابل رفع خودکار

Base Classes (5 issues)
[ERROR] inventory/views/master_data.py:45
  Category: Base Classes
  Class 'ItemTypeListView' uses 'ListView' instead of 'BaseListView'
  💡 Suggestion: Replace with BaseListView from shared.views.base

Security - secrets (2 issues)
[CRITICAL] config/settings.py:12
  Category: Security - secrets
  Hardcoded SECRET_KEY - use environment variables
  💡 Suggestion: Use os.getenv('SECRET_KEY')

❌ FAILED - Fix errors before committing
```

---

## 🎯 کاربردها

### 1. قبل از Commit (خودکار)
```bash
git commit -m "message"
# Pre-commit hook خودکار چک می‌کند
```

### 2. مرور کد (دستی)
```bash
python check_standards.py --module inventory
```

### 3. CI/CD Pipeline
```bash
python check_standards.py --json report.json
# خروجی JSON برای processing
```

### 4. گزارش هفتگی
```bash
python check_standards.py --json reports/report_$(date +%Y%m%d).json
python compare_reports.py old.json new.json
```

---

## 🏗️ معماری

```
check_standards.py
├── BaseClassChecker      # چک Base Classes
├── TemplateChecker       # چک Templates
├── DocstringChecker      # چک Documentation
├── SecurityChecker       # چک Security
├── NamingChecker         # چک Naming
└── StandardsChecker      # Orchestrator اصلی

compare_reports.py        # مقایسه گزارش‌ها

pre-commit.sh             # Git Hook

install_checker.sh        # نصب
```

---

## 🔮 قابلیت‌های کلیدی

### ✅ پیاده شده

1. **5 Checker مستقل**
   - قابل گسترش
   - مستقل از یکدیگر
   - قابل فعال/غیرفعال کردن

2. **خروجی چند فرمتی**
   - Terminal (رنگی)
   - JSON (برای CI/CD)
   - گروه‌بندی شده

3. **Severity Levels**
   - CRITICAL (امنیتی)
   - ERROR (استاندارد)
   - WARNING (توصیه)
   - INFO (اطلاعات)

4. **Smart Suggestions**
   - پیشنهاد رفع مشکل
   - مثال کد
   - لینک به documentation

5. **Auto-fix Ready**
   - flag برای auto-fixable
   - آماده برای پیاده‌سازی

6. **Git Integration**
   - Pre-commit hook
   - جلوگیری از commit ناقص
   - قابل bypass

7. **Report Comparison**
   - مقایسه زمانی
   - Tracking پیشرفت
   - Metrics

### 🚧 برای آینده

1. **Auto-fix Implementation**
   - رفع خودکار مشکلات ساده
   - Preview قبل از اعمال

2. **Test Coverage**
   - Integration با coverage.py
   - هشدار برای coverage پایین

3. **Performance Profiler**
   - شناسایی N+1 queries
   - بررسی missing indexes

4. **Web Dashboard**
   - نمایش Metrics
   - Trend Analysis
   - Team Statistics

---

## 📈 مزایا

### برای توسعه‌دهندگان:
- ✅ یادگیری سریع‌تر استانداردها
- ✅ پیشنهادات واضح
- ✅ کاهش وقت Code Review
- ✅ اطمینان بیشتر از کد

### برای تیم:
- ✅ کد یکپارچه‌تر
- ✅ کیفیت بالاتر
- ✅ کمتر Technical Debt
- ✅ Onboarding راحت‌تر

### برای پروژه:
- ✅ امنیت بیشتر
- ✅ نگهداری آسان‌تر
- ✅ Performance بهتر
- ✅ مستندات بهتر

---

## 🎓 مستندات

| فایل | محتوا | مخاطب |
|------|-------|--------|
| `CHECKER_QUICK_START.md` | شروع در 3 دقیقه | تازه‌واردها |
| `STANDARDS_CHECKER_README.md` | راهنمای کامل | همه |
| `CHECKER_SUMMARY.md` | خلاصه فنی | توسعه‌دهندگان |
| `DEVELOPMENT_GUIDE.md` | استانداردها | همه |

---

## 💻 مثال‌های عملی

### مثال 1: رفع مشکل Base Class

```python
# ❌ مشکل شناسایی شده
[ERROR] inventory/views/master_data.py:45
  Class 'ItemTypeListView' uses 'ListView'

# Code فعلی:
from django.views.generic import ListView

class ItemTypeListView(ListView):
    model = ItemType
    template_name = 'inventory/item_types.html'

# ✅ رفع شده:
from shared.views.base import BaseListView

class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']
    feature_code = 'inventory.master.item_types'
    # template_name خودکار تنظیم می‌شود
```

### مثال 2: رفع Inline Style

```django
{# ❌ مشکل شناسایی شده #}
[ERROR] templates/inventory/items.html:67
  Inline style detected

{# Code فعلی: #}
<div style="padding: 20px; margin-bottom: 10px; border: 1px solid #ddd;">
    ...
</div>

{# ✅ رفع شده: #}
{# در shared.css: #}
.card-container {
    padding: 20px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
}

{# در template: #}
<div class="card-container">
    ...
</div>
```

### مثال 3: رفع Security Issue

```python
# ❌ مشکل شناسایی شده
[CRITICAL] config/settings.py:12
  Hardcoded SECRET_KEY

# Code فعلی:
SECRET_KEY = 'django-insecure-my-secret-key-123'

# ✅ رفع شده:
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')

# در .env:
SECRET_KEY=your-secret-key-here
```

---

## 🔄 Workflow توصیه شده

```
1. توسعه Feature
   ↓
2. چک دستی (اختیاری)
   python check_standards.py --module my_module
   ↓
3. رفع مشکلات
   ↓
4. Commit
   git commit -m "feat: new feature"
   ↓
5. Pre-commit Hook (خودکار)
   - اگر PASS → Commit ✅
   - اگر FAIL → رفع مشکلات ❌
   ↓
6. Push
   ↓
7. CI/CD Pipeline (خودکار)
   - چک استانداردها
   - تولید گزارش
```

---

## 🎯 Target Metrics

هدف پروژه:
- ✅ **0 CRITICAL Issues**
- ✅ **0 ERROR Issues**
- 🎯 **< 10 WARNING per module**
- 📈 **Improvement trend**

---

## 🤝 مشارکت

### اضافه کردن Checker جدید:

1. کلاس جدید بسازید
2. متد `check_file()` پیاده کنید
3. لیست `Issue` برگردانید
4. به `StandardsChecker` اضافه کنید
5. Test و Document کنید

### گزارش Bug:

1. فایل و خط مشکل
2. خروجی ابزار
3. خروجی مورد انتظار
4. محیط (Python version, OS)

---

## 📞 پشتیبانی

- 📖 مستندات: `STANDARDS_CHECKER_README.md`
- 🚀 Quick Start: `CHECKER_QUICK_START.md`
- 💬 تیم توسعه
- 🐛 Git Issues

---

## ✨ ویژگی‌های خاص

### 1. رنگی و قابل خواندن
- خروجی ترمینال رنگی
- گروه‌بندی واضح
- Emoji برای visibility بهتر

### 2. هوشمند
- تشخیص context
- پیشنهادات مرتبط
- لینک به documentation

### 3. سریع
- Parallel processing (آینده)
- Caching (آینده)
- Incremental check (آینده)

### 4. قابل گسترش
- Architecture modular
- Plugin system (آینده)
- Custom rules (آینده)

---

## 🏆 موفقیت

ابزار با موفقیت:
- ✅ ساخته شد (~1000 خط کد)
- ✅ مستندسازی کامل (~2000 خط)
- ✅ آماده استفاده
- ✅ قابل گسترش
- ✅ Production-ready

---

**نصب کنید و شروع کنید**: `./install_checker.sh` 🚀

---

**نسخه**: 1.0  
**تاریخ**: 2024-12-23  
**وضعیت**: ✅ Production Ready  
**نگهدارنده**: تیم توسعه ERP

