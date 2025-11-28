# 📋 لیست کامل داکیومنت‌های بخش Process (فرایندهای تولید)

این فایل شامل لیست کامل تمام داکیومنت‌های مربوط به بخش **Process** (فرایندهای تولید) در ماژول **production** است.

---

## 📁 مستندات اصلی ماژول Production

### 1. `production/README.md`
- **مسیر**: `/home/shahin/invproj/production/README.md`
- **توضیحات**: مستندات کلی ماژول production که شامل توضیح کامل مدل `Process` و `ProcessStep` است
- **بخش‌های مرتبط**:
  - بخش "Process Definitions" (خط 26-28)
  - توضیحات کامل مدل `Process` و فیلدهای آن
  - توضیحات `ProcessStep` و ارتباط آن با Process

### 2. `docs/production_module_db_design_plan.md`
- **مسیر**: `/home/shahin/invproj/docs/production_module_db_design_plan.md`
- **توضیحات**: طرح کامل طراحی دیتابیس ماژول production
- **بخش‌های مرتبط**:
  - جدول `production_process` (خط 181-216)
  - جدول `production_process_step` (خط 218-253)
  - تمام فیلدها، constraints، و روابط

---

## 📄 مستندات Views (نمایش)

### 3. `production/views/README_PROCESS.md`
- **مسیر**: `/home/shahin/invproj/production/views/README_PROCESS.md`
- **توضیحات**: مستندات کامل تمام view های مربوط به Process
- **شامل**:
  - `ProcessListView`: فهرست فرآیندها
  - `ProcessCreateView`: ایجاد فرآیند جدید
  - `ProcessUpdateView`: ویرایش فرآیند
  - `ProcessDeleteView`: حذف فرآیند
  - تمام متدها، پارامترها، و URL patterns

### 4. `production/views/process.py`
- **مسیر**: `/home/shahin/invproj/production/views/process.py`
- **توضیحات**: کد منبع view های Process (154 خط)
- **کلاس‌ها**:
  - `ProcessListView`
  - `ProcessCreateView`
  - `ProcessUpdateView`
  - `ProcessDeleteView`

### 5. `production/views/README.md`
- **مسیر**: `/home/shahin/invproj/production/views/README.md`
- **توضیحات**: مستندات کلی تمام views ماژول production
- **بخش مرتبط**: بخش `process.py` (خط 11-13)

---

## 📝 مستندات Forms (فرم‌ها)

### 6. `production/forms/README_PROCESS.md`
- **مسیر**: `/home/shahin/invproj/production/forms/README_PROCESS.md`
- **توضیحات**: مستندات کامل فرم Process
- **شامل**:
  - تمام فیلدهای `ProcessForm`
  - توضیح کامل متدها (`__init__`, `save`, `save_m2m`)
  - Company filtering logic
  - Permission-based filtering برای `approved_by`

### 7. `production/forms/process.py`
- **مسیر**: `/home/shahin/invproj/production/forms/process.py`
- **توضیحات**: کد منبع فرم Process (130 خط)
- **کلاس**:
  - `ProcessForm`: فرم ایجاد/ویرایش فرآیند تولید

### 8. `production/README_FORMS.md`
- **مسیر**: `/home/shahin/invproj/production/README_FORMS.md`
- **توضیحات**: مستندات کلی فرم‌های ماژول production
- **بخش مرتبط**: بخش `ProcessForm` (خطوط 492-501)

---

## 🗄️ مستندات Models (مدل‌ها)

### 9. `production/models.py`
- **مسیر**: `/home/shahin/invproj/production/models.py`
- **توضیحات**: کد منبع مدل‌های production
- **کلاس‌های مرتبط**:
  - `Process` (خط 453-522): مدل اصلی فرآیند تولید
  - `ProcessStep` (خط 525-584): مراحل فرآیند (اختیاری - در حال حاضر استفاده نمی‌شود)

---

## 🎨 مستندات Templates (قالب‌ها)

### 10. `templates/production/processes.html`
- **مسیر**: `/home/shahin/invproj/templates/production/processes.html`
- **توضیحات**: قالب HTML برای نمایش فهرست فرآیندها (108 خط)
- **ویژگی‌ها**:
  - جدول لیست فرآیندها
  - نمایش Code، Finished Item، BOM، Revision، Work Lines
  - دکمه‌های Edit و Delete
  - Empty state

### 11. `templates/production/process_form.html`
- **مسیر**: `/home/shahin/invproj/templates/production/process_form.html`
- **توضیحات**: قالب HTML برای فرم ایجاد/ویرایش فرآیند (355 خط)
- **ویژگی‌ها**:
  - تمام فیلدهای فرم
  - Multi-select برای Work Lines
  - Styling و validation messages

### 12. `templates/production/process_confirm_delete.html`
- **مسیر**: `/home/shahin/invproj/templates/production/process_confirm_delete.html`
- **توضیحات**: قالب HTML برای تأیید حذف فرآیند

---

## 🔗 مستندات URLs و Routing

### 13. `production/urls.py`
- **مسیر**: `/home/shahin/invproj/production/urls.py`
- **توضیحات**: مسیرهای URL برای Process
- **URL patterns**:
  - `/production/processes/` → `ProcessListView`
  - `/production/processes/create/` → `ProcessCreateView`
  - `/production/processes/<pk>/edit/` → `ProcessUpdateView`
  - `/production/processes/<pk>/delete/` → `ProcessDeleteView`

---

## 🔐 مستندات Permissions (دسترسی‌ها)

### 14. `shared/permissions.py`
- **مسیر**: `/home/shahin/invproj/shared/permissions.py`
- **توضیحات**: تعریف دسترسی‌های سیستم
- **بخش مرتبط**: بخش `production.processes` (خط 123-134)
- **Actions موجود**:
  - `VIEW_OWN`
  - `VIEW_ALL`
  - `CREATE`
  - `EDIT_OWN`
  - `DELETE_OWN`
  - `APPROVE`

---

## 🗃️ مستندات Migrations

### 15. `production/migrations/README.md`
- **مسیر**: `/home/shahin/invproj/production/migrations/README.md`
- **توضیحات**: مستندات کلی migrations ماژول production
- **بخش مرتبط**: بخش "Process Updates" (خط 23-28)

### 16. Migration Files مرتبط:
- `0014_update_process_model.py`: به‌روزرسانی مدل Process
- `0015_remove_effective_dates_from_process.py`: حذف effective dates
- `0016_remove_effective_dates_from_process.py`: (duplicate)
- `0017_fix_process_revision_constraint.py`: رفع constraint revision
- `0018_change_process_approved_by_to_user.py`: تغییر approved_by به User

---

## 📚 مستندات کلی پروژه

### 17. `README.md` (Root)
- **مسیر**: `/home/shahin/invproj/README.md`
- **توضیحات**: مستندات اصلی پروژه
- **بخش مرتبط**: بخش 3.3 "Production Module" (خط 235-254)

### 18. `docs/CHANGELOG.md`
- **مسیر**: `/home/shahin/invproj/docs/CHANGELOG.md`
- **توضیحات**: تاریخچه تغییرات پروژه
- **بخش مرتبط**: تغییرات مربوط به Process approval workflow (خط 1034-1035)

---

## 🔍 نکات مهم

### ساختار مدل Process:
- **Process**: مدل اصلی فرآیند تولید
  - `process_code`: کد خودکار 16 رقمی
  - `finished_item`: کالای نهایی (FK به Item)
  - `bom`: فهرست مواد اولیه (FK به BOM، اختیاری)
  - `work_lines`: خطوط کاری (ManyToMany با WorkLine)
  - `revision`: نسخه (اختیاری)
  - `is_primary`: فرایند اصلی
  - `approval_status`: وضعیت تایید
  - `approved_by`: تایید کننده (FK به User)

### ProcessStep (در حال حاضر استفاده نمی‌شود):
- **ProcessStep**: مراحل فرآیند
  - `process`: فرآیند والد (FK به Process)
  - `work_center`: مرکز کاری
  - `machine`: ماشین (اختیاری)
  - `sequence_order`: ترتیب
  - `labor_minutes_per_unit`: دقیقه کارگر
  - `machine_minutes_per_unit`: دقیقه ماشین
  - `setup_minutes`: زمان راه‌اندازی

### URL Patterns:
```
/production/processes/                    → List
/production/processes/create/             → Create
/production/processes/<pk>/edit/          → Update
/production/processes/<pk>/delete/        → Delete
```

### Permissions:
- Feature Code: `production.processes`
- Actions: `view_own`, `view_all`, `create`, `edit_own`, `delete_own`, `approve`

### فیلدهای Form:
- `bom`: اختیاری
- `work_lines`: ManyToMany، اختیاری
- `revision`: اختیاری
- `description`: اختیاری
- `is_primary`: اختیاری
- `approved_by`: فیلتر شده بر اساس permission
- `notes`: اختیاری
- `is_enabled`: اختیاری
- `sort_order`: اختیاری

---

## 📊 خلاصه فایل‌ها

### مستندات:
1. ✅ `production/README.md` - مستندات کلی ماژول
2. ✅ `docs/production_module_db_design_plan.md` - طراحی دیتابیس
3. ✅ `production/views/README_PROCESS.md` - مستندات Views
4. ✅ `production/forms/README_PROCESS.md` - مستندات Forms
5. ✅ `production/views/README.md` - مستندات کلی Views
6. ✅ `production/README_FORMS.md` - مستندات کلی Forms
7. ✅ `production/migrations/README.md` - مستندات Migrations

### کد منبع:
8. ✅ `production/models.py` - مدل Process و ProcessStep
9. ✅ `production/views/process.py` - View classes
10. ✅ `production/forms/process.py` - Form class
11. ✅ `production/urls.py` - URL patterns
12. ✅ `shared/permissions.py` - Permission definitions

### Templates:
13. ✅ `templates/production/processes.html` - لیست
14. ✅ `templates/production/process_form.html` - فرم
15. ✅ `templates/production/process_confirm_delete.html` - تأیید حذف

### مستندات کلی:
16. ✅ `README.md` (Root) - مستندات اصلی پروژه
17. ✅ `docs/CHANGELOG.md` - تاریخچه تغییرات

---

## 🎯 فایل‌های پیشنهادی برای شروع توسعه

1. **ابتدا مطالعه کنید**:
   - `production/README.md` - برای درک کلی
   - `production/models.py` (بخش Process) - برای درک ساختار داده
   - `docs/production_module_db_design_plan.md` - برای درک طراحی دیتابیس

2. **سپس کدها را بررسی کنید**:
   - `production/views/process.py` - منطق نمایش
   - `production/forms/process.py` - منطق فرم

3. **مستندات کامل را بخوانید**:
   - `production/views/README_PROCESS.md` - جزئیات Views
   - `production/forms/README_PROCESS.md` - جزئیات Forms

4. **Templates را ببینید**:
   - `templates/production/process_form.html` - رابط کاربری فرم
   - `templates/production/processes.html` - رابط کاربری لیست

---

**آخرین به‌روزرسانی**: 2025-01-21

