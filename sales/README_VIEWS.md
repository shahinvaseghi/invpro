# sales/views.py - Views

**هدف**: Views برای ماژول فروش

---

## Views

### Dashboard

#### `SalesDashboardView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Dashboard view برای ماژول فروش.

**Attributes**:
- `template_name`: `'sales/dashboard.html'`
- `feature_code`: `'sales.dashboard'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'sales'`
- `page_title`: `'فروش'`

---

### Sales Invoice

#### `SalesInvoiceCreateView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Create view برای صدور فاکتور فروش.

**Attributes**:
- `template_name`: `'sales/invoice_create.html'`
- `feature_code`: `'sales.invoice'`
- `required_action`: `'create'`

**Context**:
- `active_module`: `'sales'`
- `page_title`: `'صدور فاکتور فروش'`

---

## وابستگی‌ها

- `django.views.generic`: `TemplateView`
- `shared.mixins`: `FeaturePermissionRequiredMixin`

---

## استفاده در پروژه

تمام views از `FeaturePermissionRequiredMixin` برای بررسی دسترسی استفاده می‌کنند و از `TemplateView` برای نمایش صفحات خالی استفاده می‌شوند.

---

## نکات مهم

1. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` برای بررسی دسترسی استفاده می‌کنند
2. **Placeholder Views**: در حال حاضر تمام views به صورت placeholder هستند و فقط template را نمایش می‌دهند
3. **Active Module**: تمام views `active_module` را در context تنظیم می‌کنند برای navigation highlighting

