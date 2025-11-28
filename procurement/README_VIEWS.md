# procurement/views.py - Views

**هدف**: Views برای ماژول تدارکات

---

## Views

### Dashboard

#### `ProcurementDashboardView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Dashboard view برای ماژول تدارکات.

**Attributes**:
- `template_name`: `'procurement/dashboard.html'`
- `feature_code`: `'procurement.dashboard'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'procurement'`
- `page_title`: `'تدارکات'`

---

### Purchase Views

#### `PurchaseListView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: List view برای خریدها.

**Attributes**:
- `template_name`: `'procurement/purchase_list.html'`
- `feature_code`: `'procurement.purchases'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'procurement'`
- `page_title`: `'خریدها'`

---

### Buyer Views

#### `BuyerListView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: List view برای خریداران.

**Attributes**:
- `template_name`: `'procurement/buyer_list.html'`
- `feature_code`: `'procurement.buyers'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'procurement'`
- `page_title`: `'خریداران'`

---

#### `BuyerCreateView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Create view برای تعریف خریدار.

**Attributes**:
- `template_name`: `'procurement/buyer_form.html'`
- `feature_code`: `'procurement.buyers'`
- `required_action`: `'create'`

**Context**:
- `active_module`: `'procurement'`
- `page_title`: `'تعریف خریدار'`

---

#### `BuyerAssignmentView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: View برای تخصیص خریداران.

**Attributes**:
- `template_name`: `'procurement/buyer_assignment.html'`
- `feature_code`: `'procurement.buyers'`
- `required_action`: `'edit_own'`

**Context**:
- `active_module`: `'procurement'`
- `page_title`: `'تخصیص خریداران'`

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

