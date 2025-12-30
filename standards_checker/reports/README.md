# 📊 Reports Folder

این فولدر شامل تمام گزارش‌های تولید شده توسط Standards Checker است.

---

## 📁 ساختار فایل‌ها

گزارش‌ها به صورت خودکار با نام‌گذاری زیر ذخیره می‌شوند:

### فرمت نام فایل:
```
{check_type}_{target_name}_{timestamp}.txt
```

### مثال‌ها:

#### Manual Check (چک دستی):
```
manual_inventory_views_base.py_20241223_143022.txt
```

#### Module Check (چک ماژول):
```
module_iminventory_20241223_143155.txt
```

#### All Check (چک کامل):
```
all_invproj_20241223_143500.txt
```

---

## 📋 محتوای گزارش

هر گزارش شامل:

1. **اطلاعات کلی**:
   - نوع چک (Manual/Module/All)
   - Target (فایل/ماژول/پروژه)
   - تاریخ و زمان
   - تعداد فایل‌های چک شده
   - تعداد فایل‌های دارای مشکل
   - تعداد کل Issues

2. **خلاصه بر اساس Severity**:
   - Critical Issues
   - Errors
   - Warnings

3. **جزئیات Issues**:
   - تفکیک بر اساس فایل
   - شماره خط
   - پیام کامل
   - کد snippet (در صورت وجود)

---

## 🔍 نحوه استفاده

### مشاهده گزارش‌ها:
```bash
cd standards_checker/reports
ls -lt  # لیست گزارش‌ها بر اساس تاریخ
```

### مشاهده آخرین گزارش:
```bash
cd standards_checker/reports
ls -t | head -1 | xargs cat
```

### جستجو در گزارش‌ها:
```bash
cd standards_checker/reports
grep -r "Missing docstring" *.txt
```

### مقایسه گزارش‌ها:
```bash
cd standards_checker/reports
diff report1.txt report2.txt
```

---

## 🗑️ مدیریت فایل‌ها

### حذف گزارش‌های قدیمی (بیشتر از 30 روز):
```bash
cd standards_checker/reports
find . -name "*.txt" -mtime +30 -delete
```

### آرشیو گزارش‌های قدیمی:
```bash
cd standards_checker/reports
mkdir -p archive
find . -name "*.txt" -mtime +7 -exec mv {} archive/ \;
```

---

## 📝 نکات

- ✅ گزارش‌ها به صورت خودکار ذخیره می‌شوند
- ✅ هر بار که یک چک انجام می‌شه، یک گزارش جدید ساخته می‌شه
- ✅ گزارش‌ها با timestamp ذخیره می‌شن تا نام‌ها تکراری نباشن
- ✅ می‌تونی گزارش‌ها رو برای مقایسه یا بررسی بعدی نگه داری

---

## 🔗 لینک‌های مفید

- [HOW_TO_USE.md](../HOW_TO_USE.md) - راهنمای استفاده از Interactive Checker
- [README.md](../README.md) - مستندات کامل Standards Checker
- [tools/compare_reports.py](../tools/compare_reports.py) - ابزار مقایسه گزارش‌ها

---

**موفق باشی! 🎉**

