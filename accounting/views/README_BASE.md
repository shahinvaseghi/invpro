# accounting/views/base.py - Base Views (Complete Documentation)

**هدف**: Base views و mixins برای ماژول accounting

این فایل شامل **1 کلاس**:
- `AccountingBaseView`: Base view با context مشترک برای ماژول accounting

---

## وابستگی‌ها

- `django.contrib.auth.mixins`: `LoginRequiredMixin`
- `django.views.generic`: `View`
- `shared.utils.permissions`: `get_user_feature_permissions`, `has_feature_permission`, `are_users_in_same_primary_group`
- `typing`: `Optional`, `Dict`, `Any`

---

## AccountingBaseView

**Type**: `LoginRequiredMixin`

**توضیح**: Base view با context مشترک برای ماژول accounting. این کلاس برای تمام views حسابداری استفاده می‌شود و قابلیت‌های مشترک را فراهم می‌کند.

**Attributes**:
- `login_url`: `'/admin/login/'` - URL برای redirect در صورت عدم authentication

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس active company فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس active company

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند
2. `active_company_id` را از session می‌گیرد
3. اگر `company_id` وجود دارد و model دارای فیلد `company` یا `company_id` است:
   - queryset را بر اساس `company_id` فیلتر می‌کند
4. queryset فیلتر شده را برمی‌گرداند

**نکته**: این متد برای ListView و DetailView استفاده می‌شود تا فقط records مربوط به company فعال نمایش داده شوند.

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables مشترک را برای تمام views حسابداری اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: context variables از parent classes

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module` اضافه شده

**منطق**:
1. `super().get_context_data(**kwargs)` را فراخوانی می‌کند
2. `active_module` را به context اضافه می‌کند با مقدار `'accounting'`
3. context را برمی‌گرداند

**نکته**: `active_module` برای navigation highlighting در sidebar استفاده می‌شود.

---

#### `filter_queryset_by_permissions(self, queryset, feature_code: str, owner_field: str = 'created_by') -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**پارامترهای ورودی**:
- `queryset` (QuerySet): queryset برای فیلتر کردن
- `feature_code` (str): کد feature برای permission checking (مثلاً 'accounting.fiscal_years')
- `owner_field` (str, default='created_by'): نام فیلدی که شامل owner/creator است

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. اگر کاربر superuser باشد، queryset را بدون تغییر برمی‌گرداند
2. `get_user_feature_permissions` را فراخوانی می‌کند تا permissions کاربر را بگیرد
3. `active_company_id` را از session می‌گیرد
4. بررسی permissions:
   - `can_view_all`: بررسی `view_all` permission
   - `can_view_own`: بررسی `view_own` permission
   - `can_view_same_group`: بررسی `view_same_group` permission
5. اگر `can_view_all` باشد، queryset را بدون تغییر برمی‌گرداند
6. ایجاد `filter_conditions` (Q object) برای ترکیب conditions
7. اگر `can_view_own` باشد و model دارای فیلد `owner_field` است:
   - اضافه کردن condition: `Q(**{owner_field: self.request.user})`
8. اگر `can_view_same_group` باشد و model دارای فیلد `owner_field` است:
   - دریافت primary groups کاربر فعلی: `set(self.request.user.primary_groups.all().values_list('id', flat=True))`
   - دریافت users که در same primary group هستند: `User.objects.filter(primary_groups__id__in=current_user_primary_groups).distinct()`
   - اضافه کردن condition: `Q(**{f'{owner_field}__in': same_group_users})`
9. اگر هیچ condition وجود نداشته باشد:
   - return `queryset.none()`
10. اعمال filter و return `queryset.filter(filter_conditions).distinct()`

**نکته**: این متد برای ListView ها استفاده می‌شود تا فقط records قابل مشاهده برای کاربر نمایش داده شوند.

---

## استفاده در پروژه

### Inheritance Pattern
تمام views حسابداری از `AccountingBaseView` ارث‌بری می‌کنند:

```python
class FiscalYearListView(FeaturePermissionRequiredMixin, AccountingBaseView, ListView):
    # ...
```

### Company Filtering
`get_queryset()` به صورت خودکار queryset را بر اساس `active_company_id` از session فیلتر می‌کند.

### Permission Filtering
`filter_queryset_by_permissions()` برای فیلتر کردن queryset بر اساس permissions کاربر استفاده می‌شود.

### Context Variables
`get_context_data()` به صورت خودکار `active_module` را به context اضافه می‌کند.

---

## نکات مهم

1. **Company Scoping**: تمام queryset ها به صورت خودکار بر اساس active company فیلتر می‌شوند
2. **Permission Checking**: `filter_queryset_by_permissions` برای کنترل دسترسی استفاده می‌شود
3. **Superuser Bypass**: Superuser ها می‌توانند تمام records را ببینند
4. **View Scope**: سیستم از `view_all` و `view_own` permissions پشتیبانی می‌کند
5. **Active Module**: `active_module` برای navigation highlighting استفاده می‌شود

---

**Last Updated**: 2025-12-01

