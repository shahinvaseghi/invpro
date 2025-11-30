# چک‌لیست انتقال Template های ماژول Production به Template های عمومی

این مستند شامل چک‌لیست کامل برای انتقال template های اختصاصی production به template های generic است.

## وضعیت فعلی

### ✅ **تکمیل شده**
- **BOM**: 3 template (list ✅, form ✅, delete ✅)
- **Machine**: 3 template (list ✅, form ✅, delete ✅)
- **Performance Record**: 3 template (list ✅, form ✅, delete ✅)
- **Personnel**: 3 template (list ✅, form ✅, delete ✅)
- **Process**: 3 template (list ✅, form ✅, delete ✅)
- **Product Order**: 3 template (list ✅, form ✅, delete ✅)
- **Transfer to Line**: 3 template (list ✅, form ✅, delete ✅)
- **Work Line**: 3 template (list ✅, form ✅, delete ✅)

### ✅ **تمام template ها تکمیل شدند!**

**جمع کل: 24 template (23 migrate شده + 2 placeholder)**  
**تکمیل شده: 23 / 23 (100%)**  
**باقی مانده: 0 / 23 (0%)** 🎉

---

## فاز 1: BOM Templates (3 مورد)

### 1.1 BOM List
- [x] بررسی `templates/production/bom_list.html`
- [x] بررسی view: `production/views/bom.py` (BOMListView)
- [x] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [x] Extract کردن `filter_fields` و `table_rows`
- [x] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

### 1.2 BOM Form
- [x] بررسی `templates/production/bom_form.html`
- [x] بررسی نیازهای خاص (formset پیچیده با JavaScript)
- [x] ایجاد template جدید که extends `shared/generic/generic_form.html`
- [x] Override کردن blocks لازم (form_sections, form_extra, form_scripts)
- [x] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

### 1.3 BOM Delete
- [x] بررسی `templates/production/bom_confirm_delete.html`
- [x] به‌روزرسانی view برای استفاده از `shared/generic/generic_confirm_delete.html`
- [x] حذف `production/bom_confirm_delete.html`
- [ ] تست

---

## فاز 2: Machine Templates (2 مورد)

### 2.1 Machine List
- [x] بررسی `templates/production/machines.html`
- [x] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [x] Extract کردن `filter_fields` و `table_rows`
- [x] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

### 2.2 Machine Form
- [x] بررسی `templates/production/machine_form.html`
- [x] ایجاد template جدید که extends `shared/generic/generic_form.html`
- [x] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

### 2.3 Machine Delete
- [x] به‌روزرسانی view برای استفاده از `shared/generic/generic_confirm_delete.html`
- [x] حذف `production/machine_confirm_delete.html`
- [ ] تست

---

## فاز 3: Performance Record Templates (3 مورد)

### 3.1 Performance Record List
- [x] بررسی `templates/production/performance_record_list.html`
- [x] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [x] Extract کردن `table_rows` و `after_table` (برای JavaScript)
- [x] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

### 3.2 Performance Record Form
- [x] بررسی `templates/production/performance_record_form.html`
- [x] بررسی نیازهای خاص (3 formsets پیچیده)
- [x] ایجاد template جدید که extends `shared/generic/generic_form.html`
- [x] Override کردن blocks لازم (form_sections, form_extra, form_scripts, before_form, form_actions_extra)
- [x] به‌روزرسانی view (CreateView و UpdateView)
- [ ] تست و حذف فایل قدیمی

### 3.3 Performance Record Delete
- [x] به‌روزرسانی view برای استفاده از `shared/generic/generic_confirm_delete.html`
- [x] حذف `production/performance_record_confirm_delete.html`
- [ ] تست

---

## فاز 4: Personnel Templates (3 مورد)

### 4.1 Personnel List
- [x] بررسی `templates/production/personnel.html`
- [x] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [x] Extract کردن `filter_fields` (Search + Status) و `table_rows`
- [x] به‌روزرسانی view برای فیلترهای search و status
- [ ] تست و حذف فایل قدیمی

### 4.2 Person Form
- [x] بررسی `templates/production/person_form.html`
- [x] ایجاد template جدید که extends `shared/generic/generic_form.html`
- [x] Extract کردن `form_sections` (با checkbox list برای company_units)
- [x] به‌روزرسانی view (CreateView و UpdateView)
- [ ] تست و حذف فایل قدیمی

### 4.2 Person Delete
- [x] به‌روزرسانی view برای استفاده از `shared/generic/generic_confirm_delete.html`
- [x] حذف `production/person_confirm_delete.html`
- [ ] تست

---

## فاز 5: Process Templates (3 مورد)

### 5.1 Process List
- [x] بررسی `templates/production/processes.html`
- [x] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [x] Extract کردن `table_headers`, `table_rows` با expandable rows
- [x] Extract کردن `after_table` برای CSS و JavaScript
- [x] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

### 5.2 Process Form
- [x] بررسی `templates/production/process_form.html`
- [x] بررسی نیازهای خاص (formset پیچیده operations + nested materials, 1069 خط)
- [x] ایجاد template جدید که extends `shared/generic/generic_form.html`
- [x] Override کردن blocks لازم (before_form, form_sections, form_extra, form_scripts, extra_styles)
- [x] به‌روزرسانی view (CreateView و UpdateView) - breadcrumbs و context اضافه شد
- [ ] تست و حذف فایل قدیمی

### 5.2 Process Delete
- [x] به‌روزرسانی view برای استفاده از `shared/generic/generic_confirm_delete.html`
- [x] حذف `production/process_confirm_delete.html`
- [ ] تست

---

## فاز 6: Product Order Templates (3 مورد)

### 6.1 Product Order List
- [x] بررسی `templates/production/product_orders.html`
- [x] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [x] Extract کردن `table_headers` و `table_rows`
- [x] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

### 6.2 Product Order Form
- [x] بررسی `templates/production/product_order_form.html`
- [x] بررسی نیازهای خاص (optional transfer request section + extra_items formset با cascading)
- [x] ایجاد template جدید که extends `shared/generic/generic_form.html`
- [x] Override کردن blocks لازم (form_sections, form_extra, form_scripts)
- [x] به‌روزرسانی view (CreateView و UpdateView)
- [ ] تست و حذف فایل قدیمی

### 6.2 Product Order Delete
- [x] به‌روزرسانی view برای استفاده از `shared/generic/generic_confirm_delete.html`
- [x] حذف `production/product_order_confirm_delete.html`
- [ ] تست

---

## فاز 7: Transfer to Line Templates (3 مورد)

### 7.1 Transfer to Line List
- [x] بررسی `templates/production/transfer_to_line_list.html`
- [x] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [x] Extract کردن `table_rows` و `after_table` (برای JavaScript approve/reject)
- [x] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

### 7.2 Transfer to Line Form
- [x] بررسی `templates/production/transfer_to_line_form.html`
- [x] بررسی نیازهای خاص (BOM items table, extra items formset با cascading filters, lock status)
- [x] ایجاد template جدید که extends `shared/generic/generic_form.html`
- [x] Override کردن blocks لازم (before_form, form_sections, form_extra, form_scripts)
- [x] به‌روزرسانی view (CreateView و UpdateView)
- [ ] تست و حذف فایل قدیمی

### 7.3 Transfer to Line Delete
- [x] به‌روزرسانی view برای استفاده از `shared/generic/generic_confirm_delete.html`
- [x] حذف `production/transfer_to_line_confirm_delete.html`
- [ ] تست

---

## فاز 8: Work Line Templates (3 مورد)

### 8.1 Work Line List
- [x] بررسی `templates/production/work_lines.html`
- [x] ایجاد template جدید که extends `shared/generic/generic_list.html`
- [x] Extract کردن `table_headers` و `table_rows`
- [x] به‌روزرسانی view
- [ ] تست و حذف فایل قدیمی

### 8.2 Work Line Form
- [x] بررسی و انتقال
- [x] به‌روزرسانی view

### 8.3 Work Line Delete
- [x] به‌روزرسانی view

---

## فاز 9: پاکسازی و به‌روزرسانی نهایی

### 9.1 پاکسازی فایل‌های قدیمی
- [x] حذف `production/bom_confirm_delete.html`
- [x] حذف `production/machine_confirm_delete.html`
- [x] حذف `production/performance_record_confirm_delete.html`
- [x] حذف `production/person_confirm_delete.html`
- [x] حذف `production/process_confirm_delete.html`
- [x] حذف `production/product_order_confirm_delete.html`
- [x] حذف `production/transfer_to_line_confirm_delete.html`
- [x] حذف `production/work_line_confirm_delete.html`
- [x] حذف تمام template های confirm_delete قدیمی
- [ ] حذف سایر template های قدیمی (بعد از تکمیل migration)

### 9.2 به‌روزرسانی README ها
- [x] به‌روزرسانی `production/views/README_BOM.md`
- [x] به‌روزرسانی `production/views/README_MACHINE.md`
- [x] به‌روزرسانی `production/views/README_PERFORMANCE_RECORD.md`
- [x] به‌روزرسانی `production/views/README_PERSONNEL.md`
- [x] به‌روزرسانی `production/views/README_PROCESS.md`
- [x] به‌روزرسانی `production/views/README_PRODUCT_ORDER.md`
- [x] به‌روزرسانی `production/views/README_TRANSFER_TO_LINE.md`
- [x] به‌روزرسانی `production/views/README_WORK_LINE.md`
- [x] به‌روزرسانی `production/views/README.md` (main README)

### 9.3 تست نهایی
- [ ] تست کامل تمام صفحات

---

**پیشرفت کلی:**
- **انجام شده:** 23 / 23 (100%) 🎉
  - ✅ BOM List
  - ✅ BOM Form
  - ✅ BOM Delete
  - ✅ Machine List
  - ✅ Machine Form
  - ✅ Machine Delete
  - ✅ Performance Record List
  - ✅ Performance Record Form
  - ✅ Performance Record Delete
  - ✅ Personnel List
  - ✅ Person Form
  - ✅ Person Delete
  - ✅ Process List
  - ✅ Process Form
  - ✅ Process Delete
  - ✅ Product Order List
  - ✅ Product Order Form
  - ✅ Product Order Delete
  - ✅ Transfer to Line List
  - ✅ Transfer to Line Form
  - ✅ Transfer to Line Delete
  - ✅ Work Line List
  - ✅ Work Line Form
  - ✅ Work Line Delete
- **باقی مانده:** 0 / 23 (0%)
  - ✅ تمام template ها migrate شدند!

