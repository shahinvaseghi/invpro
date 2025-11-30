# چک‌لیست انتقال Template های ماژول Ticketing به Template های عمومی

این مستند شامل چک‌لیست کامل برای انتقال template های اختصاصی ticketing به template های generic است.

## وضعیت فعلی

### ✅ **منتقل شده (9 مورد)**
- **Categories**: ✅ 3 template (list, form, delete)
- **Subcategories**: ✅ 3 template (list, form, delete)
- **Templates**: ✅ 3 template (list, form, delete)

**جمع کل: 9 / 9 (100%)**

---

## فاز 1: انتقال Categories Templates (3 مورد)

### 1.1 Categories List
- [ ] بررسی `templates/ticketing/categories_list.html`
- [ ] بررسی view: `ticketing/views/categories.py` (TicketCategoryListView)
- [ ] ایجاد `templates/ticketing/categories_list.html` جدید که extends `shared/generic/generic_list.html`
- [ ] Extract کردن `filter_fields` block
- [ ] Extract کردن `table_rows` block
- [ ] به‌روزرسانی view برای استفاده از context variables مناسب
- [ ] تغییر `context_object_name` به `'object_list'` (اگر لازم باشد)
- [ ] تست صفحه لیست categories
- [ ] حذف فایل قدیمی (بعد از تست موفق)

**فایل‌های مرتبط:**
- View: `ticketing/views/categories.py` (TicketCategoryListView)
- Template قدیمی: `templates/ticketing/categories_list.html`

---

### 1.2 Category Form
- [ ] بررسی `templates/ticketing/category_form.html`
- [ ] بررسی نیازهای خاص (مثل permission_formset)
- [ ] ایجاد `templates/ticketing/category_form.html` جدید که extends `shared/generic/generic_form.html`
- [ ] Override کردن blocks لازم (form_sections, form_extra برای permission_formset)
- [ ] بررسی context variables در view
- [ ] تست صفحه ایجاد category
- [ ] تست صفحه ویرایش category
- [ ] حذف فایل قدیمی (بعد از تست موفق)

**فایل‌های مرتبط:**
- Views: `ticketing/views/categories.py` (TicketCategoryCreateView, TicketCategoryUpdateView)
- Template قدیمی: `templates/ticketing/category_form.html`

---

### 1.3 Category Delete
- [ ] بررسی `templates/ticketing/category_confirm_delete.html`
- [ ] بررسی نیازهای خاص (warning برای subcategories)
- [ ] به‌روزرسانی view برای ارسال context مناسب به `shared/generic/generic_confirm_delete.html`
- [ ] تغییر `template_name` به `'shared/generic/generic_confirm_delete.html'`
- [ ] اضافه کردن warning message برای subcategories (در `warning_message`)
- [ ] تست صفحه حذف category
- [ ] حذف فایل قدیمی (بعد از تست موفق)

**فایل‌های مرتبط:**
- View: `ticketing/views/categories.py` (TicketCategoryDeleteView)
- Template قدیمی: `templates/ticketing/category_confirm_delete.html`

---

## فاز 2: انتقال Subcategories Templates (3 مورد)

### 2.1 Subcategories List
- [ ] بررسی `templates/ticketing/subcategories_list.html`
- [ ] بررسی view: `ticketing/views/subcategories.py` (TicketSubcategoryListView)
- [ ] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [ ] Extract کردن `filter_fields` و `table_rows`
- [ ] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `ticketing/views/subcategories.py` (TicketSubcategoryListView)
- Template قدیمی: `templates/ticketing/subcategories_list.html`

---

### 2.2 Subcategory Form
- [ ] بررسی `templates/ticketing/subcategory_form.html`
- [ ] بررسی نیازهای خاص (مثل permission_formset)
- [ ] ایجاد template جدید که extends `shared/generic/generic_form.html`
- [ ] Override کردن blocks لازم
- [ ] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

**فایل‌های مرتبط:**
- Views: `ticketing/views/subcategories.py` (TicketSubcategoryCreateView, TicketSubcategoryUpdateView)
- Template قدیمی: `templates/ticketing/subcategory_form.html`

---

### 2.3 Subcategory Delete
- [ ] بررسی `templates/ticketing/subcategory_confirm_delete.html`
- [ ] به‌روزرسانی view برای استفاده از `shared/generic/generic_confirm_delete.html`
- [ ] تست و حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `ticketing/views/subcategories.py` (TicketSubcategoryDeleteView)
- Template قدیمی: `templates/ticketing/subcategory_confirm_delete.html`

---

## فاز 3: انتقال Templates (Ticket Templates) (3 مورد)

### 3.1 Templates List
- [ ] بررسی `templates/ticketing/templates_list.html`
- [ ] بررسی view: `ticketing/views/templates.py` (TicketTemplateListView)
- [ ] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [ ] Extract کردن `filter_fields` و `table_rows`
- [ ] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `ticketing/views/templates.py` (TicketTemplateListView)
- Template قدیمی: `templates/ticketing/templates_list.html`

---

### 3.2 Template Form
- [ ] بررسی `templates/ticketing/template_form.html`
- [ ] بررسی نیازهای خاص
- [ ] ایجاد template جدید که extends `shared/generic/generic_form.html`
- [ ] Override کردن blocks لازم
- [ ] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

**فایل‌های مرتبط:**
- Views: `ticketing/views/templates.py` (TicketTemplateCreateView, TicketTemplateUpdateView)
- Template قدیمی: `templates/ticketing/template_form.html`

---

### 3.3 Template Delete
- [ ] بررسی `templates/ticketing/template_confirm_delete.html`
- [ ] به‌روزرسانی view برای استفاده از `shared/generic/generic_confirm_delete.html`
- [ ] تست و حذف فایل قدیمی

**فایل‌های مرتبط:**
- View: `ticketing/views/templates.py` (TicketTemplateDeleteView)
- Template قدیمی: `templates/ticketing/template_confirm_delete.html`

---

## فاز 4: پاکسازی و به‌روزرسانی نهایی

### 4.1 پاکسازی فایل‌های قدیمی
- [ ] حذف `templates/ticketing/categories_list.html` (بعد از تست موفق)
- [ ] حذف `templates/ticketing/category_form.html` (بعد از تست موفق)
- [ ] حذف `templates/ticketing/category_confirm_delete.html` (بعد از تست موفق)
- [ ] حذف `templates/ticketing/subcategories_list.html` (بعد از تست موفق)
- [ ] حذف `templates/ticketing/subcategory_form.html` (بعد از تست موفق)
- [ ] حذف `templates/ticketing/subcategory_confirm_delete.html` (بعد از تست موفق)
- [ ] حذف `templates/ticketing/templates_list.html` (بعد از تست موفق)
- [ ] حذف `templates/ticketing/template_form.html` (بعد از تست موفق)
- [ ] حذف `templates/ticketing/template_confirm_delete.html` (بعد از تست موفق)

### 4.2 به‌روزرسانی README ها
- [ ] به‌روزرسانی `ticketing/views/README_CATEGORIES.md`
- [ ] به‌روزرسانی `ticketing/views/README_SUBCATEGORIES.md`
- [ ] به‌روزرسانی `ticketing/views/README_TEMPLATES.md`
- [ ] به‌روزرسانی `ticketing/views/README.md`

### 4.3 تست نهایی
- [ ] تست کامل تمام صفحات لیست
- [ ] تست کامل تمام صفحات ایجاد
- [ ] تست کامل تمام صفحات ویرایش
- [ ] تست کامل تمام صفحات حذف
- [ ] تست فیلترها و جستجو
- [ ] تست pagination
- [ ] تست permission formsets (در category و subcategory forms)

---

## نکات مهم

1. **Ticketing Base Template**: Template های ticketing از `ticketing/base.html` extend می‌کنند که خودش از `base.html` extend می‌کند. باید بررسی کنیم که آیا نیاز به تغییر است یا نه.
2. **Permission Formsets**: Category و Subcategory forms دارای permission_formset هستند که باید حفظ شود.
3. **Warning Messages**: Category delete دارای warning برای subcategories است که باید در `warning_message` context variable قرار گیرد.
4. **Context Variables**: باید context variables مناسب برای generic templates ارسال شود.

---

**پیشرفت کلی:**
- **انجام شده:** 9 / 9 (100%)
- **باقی مانده:** 0 / 9 (0%)

## ✅ **تمام template های ماژول Ticketing با موفقیت منتقل شدند!**

تمام template های ticketing اکنون از generic templates استفاده می‌کنند:
- `categories_list.html` extends `shared/generic/generic_list.html`
- `category_form.html` extends `shared/generic/generic_form.html`
- Category Delete از `shared/generic/generic_confirm_delete.html` استفاده می‌کند
- همینطور برای Subcategories و Templates

**فایل‌های قدیمی حذف شده:**
- `category_confirm_delete.html`
- `subcategory_confirm_delete.html`
- `template_confirm_delete.html`

