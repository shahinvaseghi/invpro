# تحلیل Refactoring فایل‌های HTML

**تاریخ ایجاد**: 2024-12-05  
**آخرین به‌روزرسانی**: 2024-12-06  
**هدف**: شناسایی الگوهای تکراری در فایل‌های HTML/Template و برنامه‌ریزی برای refactoring

---

## 📖 مقدمه و هدف

این سند مکمل فایل `shared_architecture_refactoring.md` است و به **refactoring لایه Presentation (Template/HTML)** می‌پردازد.

### چرا این فایل ایجاد شد؟

پس از تکمیل refactoring لایه View (Django Views) و انتقال کدهای تکراری به Base Classes مشترک، نیاز به **استانداردسازی و refactoring لایه Template** احساس شد.

### چه مشکلی را حل می‌کند؟

1. **کد تکراری در Templateها**: الگوهای یکسان در چندین فایل HTML تکرار شده‌اند
2. **عدم استفاده از Generic Templates**: برخی فایل‌ها از base templates استفاده نمی‌کنند
3. **JavaScript Inline**: کد JavaScript در templateها به صورت inline نوشته شده و تکرار شده
4. **CSS Inline**: استایل‌ها به صورت inline در templateها نوشته شده‌اند
5. **Inline Event Handlers**: استفاده از `onclick` و `onchange` به جای event listeners

### چه کاری می‌خواهیم انجام دهیم؟

1. **Migrate Detail Views**: انتقال تمام Detail Views به `generic_detail.html`
2. **Migrate List/Form Views**: اطمینان از استفاده همه فایل‌ها از generic templates
3. **Refactor JavaScript**: انتقال JavaScript inline به فایل‌های مشترک
4. **Refactor CSS**: انتقال CSS inline به فایل‌های مشترک
5. **استفاده از Partials**: جایگزینی کدهای تکراری با partials مشترک

### ارتباط با `shared_architecture_refactoring.md`

- **`shared_architecture_refactoring.md`**: refactoring لایه **View (Python/Django)**
- **`HTML_REFACTORING_ANALYSIS.md`**: refactoring لایه **Template (HTML/JavaScript/CSS)**

این دو فایل با هم، refactoring کامل لایه‌های Backend و Frontend را پوشش می‌دهند.

### مزایای Refactoring

- ✅ **کاهش کد تکراری**: حذف ~1,200+ خط کد تکراری
- ✅ **بهبود Maintainability**: تغییرات در یک جا اعمال می‌شود
- ✅ **یکنواختی UI**: استفاده از یک الگوی مشترک
- ✅ **بهبود Performance**: استفاده از فایل‌های static cached
- ✅ **سهولت توسعه**: افزودن featureهای جدید سریع‌تر می‌شود

---

## 📊 خلاصه وضعیت فعلی

### ✅ فایل‌های که از Generic Templates استفاده می‌کنند

#### List Views (72 فایل)
- اکثر فایل‌های list از `shared/generic/generic_list.html` extend می‌کنند ✅
- فقط `table_headers` و `table_rows` را override می‌کنند ✅
- استفاده از `row_actions.html` partial در برخی فایل‌ها ✅

#### Form Views (30+ فایل)
- اکثر فایل‌های form از `shared/generic/generic_form.html` extend می‌کنند ✅
- فقط `form_sections` را override می‌کنند ✅

#### Delete Views
- از `shared/generic/generic_confirm_delete.html` استفاده می‌شود ✅

---

## ⚠️ مشکلات و الگوهای تکراری شناسایی شده

### 1. **Detail Views - عدم استفاده از Generic Template**

**مشکل**: اکثر فایل‌های `*_detail.html` از `shared/base.html` یا `inventory/base.html` extend می‌کنند به جای `shared/generic/generic_detail.html`

**فایل‌های نیازمند Refactor** (حدود 40+ فایل):

#### ماژول `inventory` (12 فایل):
- `inventory/itemtype_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/itemcategory_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/itemsubcategory_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/item_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/warehouse_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/supplier_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/suppliercategory_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/purchase_request_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/warehouse_request_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/stocktaking_deficit_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/stocktaking_surplus_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/stocktaking_record_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/receipt_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/issue_detail.html` → باید از `generic_detail.html` extend کند
- `inventory/issue_warehouse_transfer_detail.html` → باید از `generic_detail.html` extend کند

#### ماژول `production` (7 فایل):
- `production/person_detail.html` → باید از `generic_detail.html` extend کند
- `production/machine_detail.html` → باید از `generic_detail.html` extend کند
- `production/work_line_detail.html` → باید از `generic_detail.html` extend کند
- `production/process_detail.html` → باید از `generic_detail.html` extend کند
- `production/bom_detail.html` → باید از `generic_detail.html` extend کند
- `production/product_order_detail.html` → باید از `generic_detail.html` extend کند
- `production/transfer_to_line_detail.html` → باید از `generic_detail.html` extend کند
- `production/performance_record_detail.html` → باید از `generic_detail.html` extend کند

#### ماژول `accounting` (6 فایل):
- `accounting/account_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/fiscal_year_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/gl_account_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/sub_account_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/tafsili_account_detail.html` → باید از `generic_detail.html` extend کند
- `accounting/tafsili_hierarchy_detail.html` → باید از `generic_detail.html` extend کند

#### ماژول `ticketing` (4 فایل):
- `ticketing/category_detail.html` → باید از `generic_detail.html` extend کند
- `ticketing/subcategory_detail.html` → باید از `generic_detail.html` extend کند
- `ticketing/template_detail.html` → باید از `generic_detail.html` extend کند
- `ticketing/ticket_detail.html` → باید از `generic_detail.html` extend کند

#### ماژول `shared` (6 فایل):
- `shared/user_detail.html` → باید از `generic_detail.html` extend کند
- `shared/company_detail.html` → باید از `generic_detail.html` extend کند
- `shared/company_unit_detail.html` → باید از `generic_detail.html` extend کند
- `shared/group_detail.html` → باید از `generic_detail.html` extend کند
- `shared/access_level_detail.html` → باید از `generic_detail.html` extend کند
- `shared/smtp_server_detail.html` → باید از `generic_detail.html` extend کند

**جمع کل**: حدود **35 فایل Detail View** نیازمند refactor

---

### 2. **Row Actions - عدم استفاده از Partial**

**مشکل**: برخی فایل‌های list، row actions را inline می‌نویسند به جای استفاده از `shared/partials/row_actions.html`

**فایل‌های نیازمند Refactor**:
- `inventory/item_types.html` - row actions inline نوشته شده
- `inventory/item_categories.html` - row actions inline نوشته شده
- `production/machines.html` - row actions inline نوشته شده
- و سایر فایل‌های list که از `row_actions.html` استفاده نمی‌کنند

**راه حل**: همه باید از `{% include 'shared/partials/row_actions.html' %}` استفاده کنند

---

### 3. **Pagination - عدم استفاده از Partial**

**مشکل**: برخی فایل‌های list، pagination را override می‌کنند به جای استفاده از `shared/partials/pagination.html`

**فایل‌های نیازمند Refactor**:
- `production/machines.html` - pagination block override شده
- سایر فایل‌هایی که pagination را override می‌کنند

**راه حل**: همه باید از `shared/partials/pagination.html` استفاده کنند

---

### 4. **List Views - فایل‌هایی که از Generic List استفاده نمی‌کنند**

**فایل‌های نیازمند Refactor**:

#### ماژول `accounting` (6 فایل):
- `accounting/treasury/accounts.html` → باید از `generic_list.html` extend کند
- `accounting/parties/accounts.html` → باید از `generic_list.html` extend کند
- `accounting/parties/list.html` → باید از `generic_list.html` extend کند
- `accounting/income_expense/categories.html` → باید از `generic_list.html` extend کند
- `accounting/income_expense/cost_centers.html` → باید از `generic_list.html` extend کند
- `accounting/attachments/list.html` → باید از `generic_list.html` extend کند

#### ماژول `ticketing` (2 فایل):
- `ticketing/categories.html` → باید از `generic_list.html` extend کند (placeholder است)
- `ticketing/subcategories.html` → باید از `generic_list.html` extend کند (placeholder است)

**جمع کل**: حدود **8 فایل List View** نیازمند refactor

---

### 5. **Form Views - فایل‌هایی که از Generic Form استفاده نمی‌کنند**

**فایل‌های نیازمند Refactor**:

#### ماژول `accounting` (4 فایل):
- `accounting/attachments/upload.html` → باید از `generic_form.html` extend کند
- سایر formهای accounting که از `base.html` extend می‌کنند

**جمع کل**: حدود **4-5 فایل Form View** نیازمند refactor

---

### 6. **JavaScript Inline - عدم استفاده از فایل‌های مشترک**

**مشکل**: JavaScript برای مدیریت formset، cascading dropdowns، table export و سایر عملکردها در چندین template به صورت inline نوشته شده است:

#### 6.1 Formset Management JavaScript
**فایل‌های نیازمند Refactor** (18+ فایل):
- `production/bom_form.html` - JavaScript inline برای formset management (~200 خط)
- `production/process_form.html` - JavaScript inline برای formset management
- `production/performance_record_form.html` - JavaScript inline برای formset management
- `production/transfer_to_line_form.html` - JavaScript inline برای formset management
- `inventory/item_form.html` - JavaScript inline برای unit formset management
- `inventory/receipt_form.html` - JavaScript inline برای line formset management
- `inventory/issue_form.html` - JavaScript inline برای line formset management
- `inventory/warehouse_request_form.html` - استفاده از `formset.js` ✅ (مثال خوب)
- و سایر formهای با formset

**راه حل**: استفاده از `static/js/formset.js` و `static/js/formset-table.js`

**صرفه‌جویی**: حذف ~500 خط کد JavaScript تکراری

#### 6.2 Cascading Dropdowns JavaScript
**فایل‌های نیازمند Refactor** (10+ فایل):
- `production/bom_form.html` - JavaScript inline برای cascading (Type → Category → Subcategory → Item) (~300 خط)
- `inventory/item_form.html` - JavaScript inline برای cascading (Category → Subcategory) (~100 خط)
- `inventory/warehouse_request_form.html` - استفاده از `cascading-dropdowns.js` ✅ (مثال خوب)
- و سایر formهای با cascading dropdowns

**راه حل**: استفاده از `static/js/cascading-dropdowns.js`

**صرفه‌جویی**: حذف ~300 خط کد JavaScript تکراری

#### 6.3 Table Export JavaScript
**فایل‌های نیازمند Refactor** (5+ فایل):
- `shared/generic/generic_report.html` - JavaScript inline برای `exportToExcel()` (~50 خط)
- `inventory/inventory_balance.html` - JavaScript inline برای `exportToExcel()` (~50 خط)
- و سایر templateهای با export functionality

**راه حل**: استفاده از `static/js/table-export.js`

**صرفه‌جویی**: حذف ~100 خط کد JavaScript تکراری

#### 6.4 Approval/Reject Functions JavaScript
**فایل‌های نیازمند Refactor** (3+ فایل):
- `production/rework_document_list.html` - JavaScript inline برای `approveDocument()`, `rejectDocument()` (~50 خط)
- `production/qc_operations_list.html` - JavaScript inline برای `approveOperation()`, `rejectOperation()` (~80 خط)
- `production/rework_operations_list.html` - JavaScript inline برای `showNotes()` (~20 خط)

**راه حل**: ایجاد `static/js/approval-actions.js` با توابع مشترک

**صرفه‌جویی**: حذف ~150 خط کد JavaScript تکراری

#### 6.5 Modal Dialogs JavaScript
**فایل‌های نیازمند Refactor** (3+ فایل):
- `production/rework.html` - JavaScript inline برای `showNotes()` modal
- `production/qc_operations_list.html` - JavaScript inline برای `showNotes()` modal
- `production/rework_operations_list.html` - JavaScript inline برای `showNotes()` modal

**راه حل**: ایجاد `static/js/modal-dialogs.js` با توابع مشترک

**صرفه‌جویی**: حذف ~50 خط کد JavaScript تکراری

**جمع کل JavaScript**: حدود **30+ فایل** نیازمند refactor

---

### 7. **Inline Event Handlers - عدم استفاده از Event Listeners**

**مشکل**: استفاده از inline event handlers (`onclick`, `onchange`) به جای event listeners:

**فایل‌های نیازمند Refactor**:
- `inventory/purchase_requests.html` - `onclick="window.print()"`
- `inventory/receipt_temporary.html` - `onclick="window.print()"`, `onclick="return confirm(...)"`
- `inventory/items.html` - `onclick="window.print()"`, `onclick="document.getElementById(...).style.display='...'"`
- `inventory/warehouse_requests.html` - `onclick="window.print()"`
- `shared/partials/row_actions.html` - `onclick="return confirm(...)"`
- `shared/generic/generic_list.html` - `onclick="window.print()"`

**راه حل**: 
- ایجاد `static/js/common-actions.js` با توابع مشترک:
  - `printPage()` - برای print functionality
  - `confirmAction(message, callback)` - برای confirmation dialogs
  - `toggleElementVisibility(elementId)` - برای show/hide elements

**صرفه‌جویی**: حذف ~50 خط کد تکراری و بهبود maintainability

---

### 8. **Inline CSS Styles - عدم استفاده از CSS Classes**

**مشکل**: استفاده از inline styles و `<style>` tags در templateها:

**فایل‌های نیازمند Refactor**:
- `production/bom_form.html` - `<style>` tag با CSS inline (~50 خط)
- `inventory/purchase_requests.html` - `<style>` tag
- `inventory/receipt_temporary.html` - `<style>` tag
- `inventory/warehouse_requests.html` - `<style>` tag
- `shared/generic/generic_detail.html` - `<style>` tag
- `shared/generic/generic_list.html` - `<style>` tag
- و فایل‌های با inline `style="..."` attributes

**راه حل**: 
- انتقال CSS به فایل‌های مشترک در `static/css/`
- ایجاد CSS classes مشترک برای الگوهای تکراری
- استفاده از utility classes

**صرفه‌جویی**: حذف ~200 خط CSS تکراری و بهبود maintainability

---

## 📋 لیست کامل فایل‌های نیازمند Refactor

### دسته‌بندی بر اساس نوع

#### 1. Detail Views (35 فایل)
- **inventory**: 15 فایل
- **production**: 8 فایل
- **accounting**: 6 فایل
- **ticketing**: 4 فایل
- **shared**: 6 فایل

#### 2. List Views (8 فایل)
- **accounting**: 6 فایل
- **ticketing**: 2 فایل

#### 3. Form Views (4-5 فایل)
- **accounting**: 4-5 فایل

#### 4. Row Actions (10+ فایل)
- فایل‌های list که row actions را inline می‌نویسند

#### 5. Pagination (5+ فایل)
- فایل‌های list که pagination را override می‌کنند

#### 6. JavaScript Inline (30+ فایل)
- **Formset Management**: 18+ فایل
- **Cascading Dropdowns**: 10+ فایل
- **Table Export**: 5+ فایل
- **Approval/Reject Functions**: 3+ فایل
- **Modal Dialogs**: 3+ فایل

#### 7. Inline Event Handlers (10+ فایل)
- فایل‌های با `onclick`, `onchange` inline handlers

#### 8. Inline CSS Styles (10+ فایل)
- فایل‌های با `<style>` tags و inline `style="..."` attributes

---

## 🎯 الگوهای تکراری شناسایی شده

### 1. **Detail View Pattern**
```django
{% extends "shared/base.html" %}
<div class="container-fluid">
  <nav aria-label="breadcrumb">...</nav>
  <div class="card">
    <div class="card-header"><h2>...</h2></div>
    <div class="card-body">
      <div class="info-banner">...</div>
      <div class="form-section">
        <h3>Basic Information</h3>
        <div class="row">
          <div class="col-md-6">
            <div class="form-group">
              <label>...</label>
              <div class="readonly-field">...</div>
            </div>
          </div>
        </div>
      </div>
      <div class="form-section">
        <h3>Audit Information</h3>
        ...
      </div>
      <div class="form-actions">
        <a href="{{ list_url }}" class="btn btn-secondary">Back to List</a>
        <a href="{{ edit_url }}" class="btn btn-primary">Edit</a>
      </div>
    </div>
  </div>
</div>
```

**این الگو در 35+ فایل تکرار شده است!**

### 2. **Row Actions Pattern**
```django
{% if show_actions %}
<td>
  <a href="{% url edit_url_name object.pk %}" class="btn btn-secondary">Edit</a>
  <a href="{% url delete_url_name object.pk %}" class="btn btn-primary">Delete</a>
</td>
{% endif %}
```

**این الگو در 10+ فایل تکرار شده است!**

### 3. **Pagination Pattern**
```django
{% if is_paginated %}
<div class="pagination">
  {% if page_obj.has_previous %}
    <a href="?page=1&...">First</a>
    <a href="?page={{ page_obj.previous_page_number }}&...">Previous</a>
  {% endif %}
  <span>Page {{ page_obj.number }} of {{ page_obj.paginator.num_pages }}</span>
  {% if page_obj.has_next %}
    <a href="?page={{ page_obj.next_page_number }}&...">Next</a>
    <a href="?page={{ page_obj.paginator.num_pages }}&...">Last</a>
  {% endif %}
</div>
{% endif %}
```

**این الگو در 5+ فایل تکرار شده است!**

---

## 💡 پیشنهادات Refactoring

### 1. **Migrate Detail Views به Generic Template**

**قبل**:
```django
{% extends "shared/base.html" %}
<div class="container-fluid">
  <nav aria-label="breadcrumb">...</nav>
  <div class="card">...</div>
</div>
```

**بعد**:
```django
{% extends "shared/generic/generic_detail.html" %}
{% block detail_sections %}
<div class="detail-section">
  <h3>Basic Information</h3>
  <div class="detail-field">
    <label>Name</label>
    <div class="readonly-field">{{ object.name }}</div>
  </div>
</div>
{% endblock %}
```

### 2. **استفاده از Row Actions Partial**

**قبل**:
```django
<td>
  <a href="{% url edit_url_name object.pk %}" class="btn btn-secondary">Edit</a>
  <a href="{% url delete_url_name object.pk %}" class="btn btn-primary">Delete</a>
</td>
```

**بعد**:
```django
{% include 'shared/partials/row_actions.html' with object=object feature_code=feature_code detail_url_name=detail_url_name edit_url_name=edit_url_name delete_url_name=delete_url_name %}
```

### 3. **استفاده از Pagination Partial**

**قبل**: Override کردن `pagination` block

**بعد**: استفاده از `shared/partials/pagination.html` که به صورت خودکار query parameters را حفظ می‌کند

---

## 📊 خلاصه آماری

| نوع Refactor | تعداد فایل | اولویت |
|-------------|-----------|--------|
| Detail Views → Generic | 35 | 🔴 بالا |
| JavaScript Inline → Shared Files | 30+ | 🔴 بالا |
| List Views → Generic | 8 | 🟡 متوسط |
| Form Views → Generic | 4-5 | 🟡 متوسط |
| Inline CSS → Shared CSS | 10+ | 🟡 متوسط |
| Inline Event Handlers → JS Files | 10+ | 🟡 متوسط |
| Row Actions → Partial | 10+ | 🟢 پایین |
| Pagination → Partial | 5+ | 🟢 پایین |
| **جمع کل** | **110+ فایل** | |

---

## 🚀 برنامه Refactoring پیشنهادی

### فاز 1: Detail Views (اولویت بالا)
1. Refactor تمام Detail Views در ماژول `inventory` (15 فایل)
2. Refactor تمام Detail Views در ماژول `production` (8 فایل)
3. Refactor تمام Detail Views در ماژول `accounting` (6 فایل)
4. Refactor تمام Detail Views در ماژول `ticketing` (4 فایل)
5. Refactor تمام Detail Views در ماژول `shared` (6 فایل)

### فاز 2: List Views (اولویت متوسط)
1. Refactor List Views در ماژول `accounting` (6 فایل)
2. Refactor List Views در ماژول `ticketing` (2 فایل)

### فاز 3: Form Views (اولویت متوسط)
1. Refactor Form Views در ماژول `accounting` (4-5 فایل)

### فاز 4: JavaScript Refactoring (اولویت بالا)
1. Refactor Formset Management JavaScript (18+ فایل)
   - استفاده از `static/js/formset.js` و `static/js/formset-table.js`
2. Refactor Cascading Dropdowns JavaScript (10+ فایل)
   - استفاده از `static/js/cascading-dropdowns.js`
3. Refactor Table Export JavaScript (5+ فایل)
   - استفاده از `static/js/table-export.js`
4. Refactor Approval/Reject Functions (3+ فایل)
   - ایجاد `static/js/approval-actions.js`
5. Refactor Modal Dialogs (3+ فایل)
   - ایجاد `static/js/modal-dialogs.js`

### فاز 5: CSS و Event Handlers (اولویت متوسط)
1. انتقال Inline CSS به فایل‌های مشترک (10+ فایل)
2. جایگزینی Inline Event Handlers با Event Listeners (10+ فایل)
   - ایجاد `static/js/common-actions.js`

### فاز 6: Partials (اولویت پایین)
1. جایگزینی Row Actions inline با partial
2. جایگزینی Pagination override با partial

---

## 📝 نکات مهم

1. **Generic Detail Template**: باید blockهای زیر را پشتیبانی کند:
   - `detail_sections` - برای sections اصلی
   - `info_banner` - برای banner اطلاعات
   - `detail_actions` - برای action buttons

2. **Partials**: باید query parameters را به صورت خودکار حفظ کنند

3. **Backward Compatibility**: باید مطمئن شویم که تغییرات backward compatible هستند

4. **Testing**: باید تمام صفحات را بعد از refactor تست کنیم

---

---

## 📝 JavaScript Refactoring Details

### فایل‌های JavaScript مشترک موجود

✅ **فایل‌های ساخته شده**:
- `static/js/formset.js` - مدیریت formsets (add/remove rows, update indices)
- `static/js/cascading-dropdowns.js` - مدیریت cascading dropdowns
- `static/js/table-export.js` - export جدول به CSV/Excel
- `static/js/formset-table.js` - مدیریت formset در جداول

⏳ **فایل‌های نیازمند ساخت**:
- `static/js/approval-actions.js` - توابع approve/reject مشترک
- `static/js/modal-dialogs.js` - مدیریت modal dialogs
- `static/js/common-actions.js` - توابع مشترک (print, confirm, toggle visibility)

### مثال Refactoring JavaScript

#### قبل (Inline JavaScript):
```javascript
<script>
function addFormsetRow(prefix) {
  const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
  const formCount = parseInt(totalForms.value);
  // ... 50+ خط کد تکراری
}
</script>
```

#### بعد (استفاده از فایل مشترک):
```django
{% load static %}
<script src="{% static 'js/formset.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  // فقط initialization code
  const addButton = document.getElementById('add-row-btn');
  addButton.addEventListener('click', function() {
    addFormsetRow('formset', '#formset-template-row');
  });
});
</script>
```

### مثال Refactoring Cascading Dropdowns

#### قبل (Inline JavaScript):
```javascript
<script>
itemTypeSelect.addEventListener('change', function() {
  const selectedType = this.value;
  fetch('/inventory/api/filtered-categories/?type_id=' + selectedType)
    .then(response => response.json())
    .then(data => {
      // ... 30+ خط کد تکراری
    });
});
</script>
```

#### بعد (استفاده از فایل مشترک):
```django
{% load static %}
<script src="{% static 'js/cascading-dropdowns.js' %}"></script>
<script>
document.addEventListener('DOMContentLoaded', function() {
  initCascadingDropdown(
    '#id_item_type',
    '#id_item_category',
    '/inventory/api/filtered-categories/',
    { parentField: 'type_id' }
  );
});
</script>
```

---

## 📝 CSS Refactoring Details

### الگوهای CSS تکراری

**مشکل**: CSS inline در templateها:
- `<style>` tags در templateها
- Inline `style="..."` attributes
- CSS تکراری برای buttons، cards، tables

**راه حل**:
- انتقال CSS به `static/css/`
- ایجاد utility classes
- استفاده از CSS variables برای colors و spacing

### مثال Refactoring CSS

#### قبل (Inline CSS):
```django
<style>
.item-filters input[type="text"] {
  outline: none;
  border-color: #2563eb;
  background-color: #ffffff;
}
</style>
```

#### بعد (CSS مشترک):
```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/forms.css' %}">
<!-- استفاده از classهای مشترک -->
```

---

**آخرین به‌روزرسانی**: 2024-12-06

