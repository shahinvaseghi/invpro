# transportation/views.py - Views

**هدف**: Views برای ماژول حمل و نقل

---

## Views

### Dashboard

#### `TransportationDashboardView(FeaturePermissionRequiredMixin, TemplateView)`

**توضیح**: Dashboard view برای ماژول حمل و نقل.

**Attributes**:
- `template_name`: `'transportation/dashboard.html'`
- `feature_code`: `'transportation.dashboard'`
- `required_action`: `'view'`

**Context**:
- `active_module`: `'transportation'`
- `page_title`: `'حمل و نقل'`

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

