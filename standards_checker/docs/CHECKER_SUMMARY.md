# خلاصه Standards Checker

## 📦 فایل‌های ایجاد شده

### 1. `check_standards.py` - ابزار اصلی ✨
**خط کد**: ~600 خط  
**وظایف اصلی**:

#### Checkers موجود:

1. **BaseClassChecker**
   - چک می‌کند که از `BaseListView`, `BaseCreateView` و... استفاده شده
   - تشخیص استفاده مستقیم از Django generic views

2. **TemplateChecker**
   - شناسایی inline styles (`style="..."`)
   - شناسایی inline JavaScript (`onclick=`, `onchange=`, etc.)
   - بررسی استفاده از generic templates
   - چک کردن load template tags

3. **DocstringChecker**
   - بررسی وجود docstrings در classes
   - بررسی وجود docstrings در functions

4. **SecurityChecker**
   - شناسایی SQL injection (`cursor.execute(f"...")`)
   - تشخیص استفاده نامناسب از `|safe` و `mark_safe`
   - یافتن hardcoded secrets (SECRET_KEY, PASSWORD, API_KEY)

5. **NamingChecker**
   - بررسی PascalCase برای classes
   - بررسی snake_case برای functions

#### خروجی:
- رنگی و قابل خواندن در ترمینال
- JSON برای CI/CD
- گروه‌بندی بر اساس category
- نمایش severity (CRITICAL, ERROR, WARNING, INFO)
- پیشنهادات برای رفع مشکلات

### 2. `STANDARDS_CHECKER_README.md` - مستندات کامل 📚
**محتوا**:
- راهنمای نصب
- نحوه استفاده با مثال‌ها
- نمونه خروجی
- Integration با CI/CD (GitHub Actions, GitLab CI)
- Severity Levels
- تفسیر نتایج
- عیب‌یابی
- راهنمای توسعه

### 3. `pre-commit.sh` - Git Hook 🪝
**وظیفه**:
- اجرای خودکار قبل از هر commit
- جلوگیری از commit در صورت وجود ERROR یا CRITICAL
- نمایش پیام‌های رنگی
- راهنمایی برای bypass (با `--no-verify`)

### 4. `install_checker.sh` - نصب خودکار 🔧
**وظایف**:
- چک کردن Python و Git
- دادن permission اجرا
- نصب pre-commit hook
- ایجاد دایرکتوری reports
- تست اجرا
- نمایش راهنمای استفاده

### 5. `compare_reports.py` - مقایسه گزارش‌ها 📊
**قابلیت‌ها**:
- مقایسه دو گزارش JSON
- نمایش تغییرات در metrics
- لیست issues جدید
- لیست issues رفع شده
- مقایسه بر اساس category
- خروجی رنگی

---

## 🚀 نحوه استفاده

### نصب اولیه:

```bash
# نصب با یک دستور
./install_checker.sh

# یا دستی:
chmod +x check_standards.py
chmod +x pre-commit.sh
cp pre-commit.sh .git/hooks/pre-commit
```

### استفاده روزانه:

```bash
# قبل از commit (اجرای دستی)
python check_standards.py

# چک کردن یک ماژول خاص
python check_standards.py --module inventory

# با جزئیات کامل
python check_standards.py --verbose

# خروجی JSON برای CI/CD
python check_standards.py --json report.json
```

### استفاده هفتگی:

```bash
# تولید گزارش هفتگی
python check_standards.py --json reports/report_$(date +%Y%m%d).json

# مقایسه با هفته قبل
python compare_reports.py reports/report_20241216.json reports/report_20241223.json
```

---

## 📊 مثال خروجی

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
  Total Issues: 15
  Critical: 1
  Errors: 5
  Warnings: 9
  Auto-fixable: 2

Issues:

Security - secrets (1 issues)
[CRITICAL] config/settings/development.py:12
  Category: Security - secrets
  Hardcoded SECRET_KEY - use environment variables
  💡 Suggestion: Review security best practices in DEVELOPMENT_GUIDE.md

Base Classes (3 issues)
[ERROR] inventory/views/master_data.py:45
  Category: Base Classes
  Class 'ItemTypeListView' uses 'ListView' instead of 'BaseListView'
  💡 Suggestion: Replace with 'from shared.views.base import BaseListView'

Template - CSS (5 issues)
[ERROR] inventory/templates/inventory/items.html:67
  Category: Template - CSS
  Inline style detected
  💡 Suggestion: Move styles to shared.css

❌ FAILED - Fix errors before committing
```

---

## 🎯 مزایا

### 1. اتوماسیون کامل ✨
- چک خودکار قبل از commit
- نیازی به بررسی دستی نیست
- صرفه‌جویی در زمان

### 2. کیفیت کد بالا 📈
- رعایت استانداردها
- کد یکپارچه در تمام پروژه
- کاهش Technical Debt

### 3. یادگیری سریع‌تر 🎓
- توسعه‌دهندگان جدید سریع‌تر یاد می‌گیرند
- پیشنهادات واضح برای رفع مشکلات
- یادآوری مستمر بهترین روش‌ها

### 4. امنیت بهتر 🔒
- شناسایی مشکلات امنیتی
- جلوگیری از commit secrets
- تشخیص SQL injection و XSS

### 5. Tracking پیشرفت 📊
- مقایسه گزارش‌ها در طول زمان
- مشاهده بهبود یا رگرسیون
- آمار دقیق

---

## 🔧 سفارشی‌سازی

### اضافه کردن Checker جدید:

```python
class MyCustomChecker:
    """توضیح checker"""
    
    def check_file(self, file_path: str) -> List[Issue]:
        """چک کردن یک فایل"""
        issues = []
        
        # منطق چک کردن
        with open(file_path, 'r') as f:
            content = f.read()
        
        if 'something_bad' in content:
            issues.append(Issue(
                file_path=file_path,
                line_number=1,
                severity=Severity.ERROR,
                category="My Category",
                message="Found something bad",
                suggestion="Don't do that",
                auto_fixable=False
            ))
        
        return issues

# در StandardsChecker.__init__():
self.my_checker = MyCustomChecker()

# در StandardsChecker.check_all():
self.result.issues.extend(
    self.my_checker.check_file(file_str)
)
```

### تنظیم Severity:

```python
# برای تغییر severity یک مشکل خاص
if some_condition:
    severity = Severity.WARNING  # به جای ERROR
```

### Exempt کردن فایل‌ها:

```python
# در هر Checker
EXEMPT_MODULES = {'shared', 'migrations', 'tests', 'my_special_module'}
```

---

## 🔮 توسعه‌های آینده

### Phase 1 (فعلی) ✅
- [x] Base Classes checker
- [x] Template checker (inline styles/JS)
- [x] Docstring checker
- [x] Security checker
- [x] Naming checker
- [x] Pre-commit hook
- [x] Report comparison

### Phase 2 (آینده نزدیک) 🚧
- [ ] Auto-fix قابلیت
- [ ] Test coverage checker
- [ ] Import order checker
- [ ] Type hints checker
- [ ] Performance profiler

### Phase 3 (آینده) 💡
- [ ] Web dashboard
- [ ] Real-time monitoring
- [ ] VS Code extension
- [ ] AI-powered suggestions
- [ ] Custom rules per project
- [ ] Git blame integration

---

## 📈 Metrics و KPIs

### Metrics قابل tracking:

1. **Total Issues**
   - تعداد کل مشکلات
   - روند در طول زمان

2. **Issues per Category**
   - Base Classes
   - Templates
   - Security
   - Documentation
   - Naming

3. **Severity Distribution**
   - Critical
   - Error
   - Warning
   - Info

4. **Fix Rate**
   - تعداد issues رفع شده
   - زمان متوسط رفع

5. **Compliance Score**
   - درصد فایل‌های بدون مشکل
   - درصد بهبود نسبت به قبل

---

## 🤝 مشارکت

### برای بهبود ابزار:

1. **گزارش Bug**
   - در صورت مشاهده false positive
   - اگر چیزی چک نمی‌شود که باید شود

2. **پیشنهاد Feature**
   - Checker جدید
   - بهبود خروجی
   - Integration جدید

3. **بهبود Documentation**
   - اضافه کردن مثال
   - توضیح بیشتر
   - ترجمه

---

## 📞 پشتیبانی

در صورت مشکل:

1. مستندات `STANDARDS_CHECKER_README.md` را بررسی کنید
2. مستندات `DEVELOPMENT_GUIDE.md` را مطالعه کنید
3. با تیم هماهنگ کنید
4. Issue در Git ایجاد کنید

---

## 📝 Changelog

### Version 1.0 (2024-12-23)
- ✨ Release اولیه
- 5 Checker اصلی
- Pre-commit hook
- Report comparison
- مستندات کامل

---

**نسخه**: 1.0  
**تاریخ**: 2024-12-23  
**نگهدارنده**: تیم توسعه ERP  
**License**: Internal Use Only

