# تحلیل Refactoring فایل‌های HTML

**تاریخ ایجاد**: 2024-12-05  
**هدف**: شناسایی الگوهای تکراری و فایل‌های نیازمند refactor

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
| List Views → Generic | 8 | 🟡 متوسط |
| Form Views → Generic | 4-5 | 🟡 متوسط |
| Row Actions → Partial | 10+ | 🟢 پایین |
| Pagination → Partial | 5+ | 🟢 پایین |
| **جمع کل** | **60+ فایل** | |

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

### فاز 4: Partials (اولویت پایین)
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

**آخرین به‌روزرسانی**: 2024-12-05

