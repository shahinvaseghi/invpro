# 🚀 راهنمای استفاده از Interactive Checker

## استفاده سریع

### اجرا:
```bash
cd standards_checker
./check_manual.sh
```

یا:
```bash
python3 interactive_checker_v2.py
```

---

## 📖 مراحل استفاده

### 1️⃣ منوی اصلی
وقتی برنامه اجرا می‌شه، منوی زیر نمایش داده می‌شه:

```
╔════════════════════════════════════════════╗
║   Standards Checker - Interactive          ║
╚════════════════════════════════════════════╝

1. چک دستی (Manual Check)
2. چک ماژول (Module Check)        ⭐ NEW!
3. چک کامل (All Check)            ⭐ NEW!
4. گزارش هفتگی (Weekly Report)
5. تنظیمات (Settings)
Q. خروج (Exit)

Select option:
```

### گزینه‌های موجود:
- **گزینه 1**: چک یک فایل خاص (با File Browser)
- **گزینه 2**: چک تمام فایل‌های یک ماژول ⭐
- **گزینه 3**: چک کل پروژه (تمام ماژول‌ها) ⭐

---

### 2️⃣ گزینه 1: چک دستی (Manual Check)

#### انتخاب فایل (File Browser)

یک **File Browser تعاملی** نمایش داده می‌شه:

```
File Browser - Select a File
═════════════════════════════════════════════

  [+] invproj
    [+] imaccounting
    [+] imadmin
    [+] imconfig
    [+] imdocs
    [+] imhr
>   [+] iminventory
    [+] production
    
────────────────────────────────────────────
[UP/DOWN] Navigate  [ENTER] Select  [ESC] Back  [Q] Quit
```

#### کلیدها:
- **↑ / ↓**: حرکت بین فایل‌ها و پوشه‌ها
- **Enter**: 
  - اگر روی **پوشه** باشی → باز می‌شه
  - اگر روی **فایل** باشی → انتخاب می‌شه و چک می‌شه
- **ESC**: 
  - اگر پوشه باز باشه → بسته می‌شه
  - وگرنه → یک سطح به عقب برمی‌گرده
- **Q**: خروج

---

### 3️⃣ گزینه 2: چک ماژول (Module Check) ⭐

با این گزینه می‌تونی **تمام فایل‌های یک ماژول** رو یکجا چک کنی!

#### مراحل:

1. از منوی اصلی عدد `2` رو بزن
2. لیست ماژول‌های پروژه نمایش داده می‌شه:

```
Select Module to Check
═════════════════════════════════════════════

  > imaccounting
    imadmin
    imconfig
    imdocs
    imhr
    iminventory
    production

────────────────────────────────────────────
[UP/DOWN] Navigate  [ENTER] Select  [ESC] Cancel
```

3. با کلیدهای **↑ / ↓** ماژول مورد نظر رو انتخاب کن
4. **Enter** بزن
5. برنامه شروع می‌کنه به چک کردن تمام فایل‌ها:

```
Checking Module: iminventory
═════════════════════════════════════════════
Total files: 45
─────────────────────────────────────────────

[1/45] inventory/models.py
[2/45] inventory/views/base.py
[3/45] inventory/forms/product.py
...
```

6. بعد از اتمام، **گزارش جامع** نمایش داده می‌شه:

```
RESULTS - iminventory
══════════════════════════════════════════

SUMMARY
  Total Files Checked: 45
  Files with Issues:   12
  Total Issues:        28
    Errors:   8
    Warnings: 20

══════════════════════════════════════════

ISSUES BY FILE

📄 inventory/models.py (3 issues)

  [ERROR] Line 45
    Missing select_related() for foreign key
    
  [WARNING] Line 67
    Function name should use snake_case
    
─────────────────────────────────────────

📄 inventory/views/base.py (5 issues)
...
```

**مفیده برای**: چک کردن سریع یک ماژول خاص که روش کار می‌کنی

---

### 4️⃣ گزینه 3: چک کامل (All Check) ⭐

چک کردن **کل پروژه** - تمام ماژول‌ها یکجا!

#### مراحل:

1. از منوی اصلی عدد `3` رو بزن
2. یک **تایید** ازت می‌خواد (چون ممکنه زمان‌بره):

```
Check Entire Project?

This will check ALL modules and may take some time.

Continue? [Y/N]
```

3. `Y` بزن برای تایید
4. برنامه شروع می‌کنه به چک کردن تمام ماژول‌ها:

```
Checking Entire Project
═════════════════════════════════════════════
Total modules: 8
─────────────────────────────────────────────

[1/8] imaccounting (23 files)
[2/8] imadmin (12 files)
[3/8] imconfig (8 files)
...
```

5. در آخر **گزارش جامع کل پروژه** نمایش داده می‌شه

**مفیده برای**: 
- قبل از commit کردن یک feature بزرگ
- چک کردن وضعیت کلی پروژه
- آماده‌سازی برای release

---

### 5️⃣ اجرای چک‌ها

بعد از انتخاب فایل، چک‌ها شروع می‌شه:

```
CHECKING FILE
═════════════════════════════════════════════
inventory/forms/base.py
═════════════════════════════════════════════

Running checks...

✓ Checking base classes...
✓ Checking docstrings...
✓ Checking security...
✓ Checking naming conventions...

Completed 4 checks
Generating report...
```

---

### 6️⃣ نمایش نتایج

#### اگر مشکلی پیدا نشد:
```
        No issues found!
   All checks passed successfully.
        
Press any key to continue...
```

#### اگر مشکل پیدا شد:
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
     Function 'getData' should use snake_case naming. 
     Suggestion: get_data
     
  3. Line 89
     Missing docstring for public method 'process'
     
  4. Line 102
     Consider using select_related() for foreign key access
     
────────────────────────────────────────────────────────
[↑/↓] Scroll  [PgUp/PgDn] Page  [Home/End] Top/Bottom  [Q] Back
```

#### کلیدهای اسکرول:
- **↑ / ↓**: یک خط به بالا/پایین
- **PgUp / PgDn**: یک صفحه به بالا/پایین
- **Home**: رفتن به اول
- **End**: رفتن به آخر
- **Q**: بازگشت به File Browser

---

### 7️⃣ ذخیره خودکار گزارش‌ها ⭐

**همه گزارش‌ها به صورت خودکار ذخیره می‌شن!** 🎉

بعد از هر چک (گزینه 1، 2 یا 3)، یک فایل گزارش در فولدر `reports/` ساخته می‌شه:

```
standards_checker/reports/
├── manual_inventory_views_base.py_20241223_143022.txt
├── module_iminventory_20241223_143155.txt
└── all_invproj_20241223_143500.txt
```

#### فرمت نام فایل:
- **Manual Check**: `manual_{file_path}_{timestamp}.txt`
- **Module Check**: `module_{module_name}_{timestamp}.txt`
- **All Check**: `all_{project_name}_{timestamp}.txt`

#### محتوای گزارش:
- ✅ اطلاعات کامل چک
- ✅ خلاصه Issues بر اساس Severity
- ✅ جزئیات کامل هر Issue با شماره خط و پیام
- ✅ تفکیک بر اساس فایل

#### مشاهده گزارش‌ها:
```bash
cd standards_checker/reports
ls -lt  # لیست بر اساس تاریخ
cat manual_*.txt  # مشاهده یک گزارش
```

**📖 برای اطلاعات بیشتر**: [reports/README.md](reports/README.md)

---

## 🎯 نکات مهم

### ✅ فایل‌های قابل چک:

#### Python Files (`.py`):
- Base Class Checks
- Docstring Checks
- Security Checks
- Naming Convention Checks

#### HTML Templates (`.html`, `.htm`):
- Template Tag Checks
- Security Checks (XSS)

### ❌ فایل‌های نادیده گرفته شده:
- `__pycache__/`
- `.git/`
- `.venv/`, `venv/`, `env/`
- `node_modules/`
- `.pytest_cache/`
- `staticfiles/`, `media/`
- `.idea/`, `.vscode/`

---

## 💡 مثال‌های استفاده

### مثال 1: چک کردن یک فایل خاص (Manual Check)
1. اجرای `./check_manual.sh`
2. انتخاب گزینه `1` (Manual Check)
3. رفتن به `iminventory/` با Enter
4. رفتن به `views/` با Enter
5. انتخاب `base.py` با Enter
6. مشاهده نتایج و اسکرول با کلیدهای Arrow

### مثال 2: چک کردن یک ماژول کامل (Module Check) ⭐
1. اجرای برنامه
2. انتخاب گزینه `2` (Module Check)
3. انتخاب `iminventory` از لیست
4. صبر کردن تا تمام فایل‌ها چک بشن
5. مشاهده گزارش جامع با تفکیک فایل
6. اسکرول و بررسی issues

### مثال 3: چک کردن کل پروژه (All Check) ⭐
1. اجرای برنامه
2. انتخاب گزینه `3` (All Check)
3. تایید با `Y`
4. صبر کردن تا تمام ماژول‌ها چک بشن
5. مشاهده گزارش کامل پروژه
6. شناسایی ماژول‌هایی که بیشترین مشکل رو دارن

---

## ⚡ میانبرها

### اجرای سریع از هر جای پروژه:
```bash
python3 standards_checker/interactive_checker_v2.py
```

### ساختن Alias:
اضافه کردن به `~/.bashrc` یا `~/.zshrc`:
```bash
alias check='cd ~/invproj/standards_checker && ./check_manual.sh'
```

بعد:
```bash
check
```

---

## 🐛 رفع مشکلات

### مشکل: "Python 3 not found"
```bash
sudo apt install python3
```

### مشکل: "Module 'check_standards' not found"
مطمئن شو که از **داخل** پوشه `standards_checker` یا root پروژه اجرا می‌کنی.

### مشکل: Terminal مشکل داره
```bash
export TERM=xterm-256color
```

---

## 📚 منابع بیشتر

- [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) - استانداردهای کامل
- [README.md](README.md) - مستندات Standards Checker
- [INTERACTIVE_GUIDE.md](INTERACTIVE_GUIDE.md) - راهنمای تفصیلی

---

## ❓ سوالات متداول

**Q: میشه چند فایل رو یکجا چک کرد؟**  
A: بله! از گزینه `2` (Module Check) برای چک یک ماژول کامل یا گزینه `3` (All Check) برای چک کل پروژه استفاده کن.

**Q: کدوم گزینه رو استفاده کنم؟**  
A: 
- **گزینه 1**: برای چک سریع یک فایل خاص
- **گزینه 2**: برای چک ماژولی که روش کار می‌کنی
- **گزینه 3**: قبل از commit یا release برای چک کل پروژه

**Q: چند وقت طول می‌کشه All Check؟**  
A: بستگی به سایز پروژه داره. معمولاً 1-3 دقیقه برای پروژه‌های متوسط.

**Q: نتایج ذخیره میشن؟**  
A: بله! ✅ **همه گزارش‌ها به صورت خودکار** در فولدر `reports/` ذخیره می‌شن. بعد از هر چک (گزینه 1، 2 یا 3) یک فایل گزارش با timestamp ساخته می‌شه. برای جزئیات بیشتر [reports/README.md](reports/README.md) رو ببین.

**Q: میشه تنظیمات رو تغییر داد؟**  
A: بله، از گزینه `5` در منوی اصلی (Coming Soon).

---

**موفق باشی! 🎉**

