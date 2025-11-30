# production/views/machine.py - Machine Views (Complete Documentation)

**هدف**: Views برای مدیریت ماشین‌آلات در ماژول production

این فایل شامل views برای:
- MachineListView: فهرست ماشین‌آلات
- MachineCreateView: ایجاد ماشین جدید
- MachineUpdateView: ویرایش ماشین
- MachineDeleteView: حذف ماشین

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `MachineForm`
- `production.models`: `Machine`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## MachineListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/machines.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `Machine`
- `template_name`: `'production/machines.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`
- `feature_code`: `'production.machines'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، is_enabled filtering، و optional select_related برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با optimizations

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `Machine.objects.none()` برمی‌گرداند
3. فیلتر: `Machine.objects.filter(company_id=active_company_id, is_enabled=1)`
4. **Optional select_related**:
   - تلاش برای `select_related('work_center')` (با try-except برای جلوگیری از خطا در صورت عدم وجود field)
   - اگر خطا رخ دهد، skip می‌کند
5. مرتب‌سازی: `order_by('public_code')`
6. queryset را برمی‌گرداند

**نکات مهم**:
- `select_related('work_center')` با try-except برای جلوگیری از خطا در صورت عدم وجود field

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/machines/`

---

## MachineCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `production/machine_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `MachineForm`

**Success URL**: `production:machines`

**Attributes**:
- `model`: `Machine`
- `form_class`: `MachineForm`
- `template_name`: `'production/machine_form.html'`
- `success_url`: `reverse_lazy('production:machines')`
- `feature_code`: `'production.machines'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `company_id` را از `request.session.get('active_company_id')` اضافه می‌کند
3. kwargs را برمی‌گرداند

---

#### `form_valid(self, form: MachineForm) -> HttpResponseRedirect`

**توضیح**: Machine را ذخیره می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `MachineForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد:
   - خطا: "Please select a company first."
   - `form_invalid()` برمی‌گرداند
3. تنظیم `form.instance.company_id = active_company_id`
4. تنظیم `form.instance.created_by = request.user`
5. نمایش پیام موفقیت: "Machine created successfully."
6. فراخوانی `super().form_valid(form)` (ذخیره و redirect)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module` و `form_title`

**Context Variables اضافه شده**:
- `form_title`: `_('Create Machine')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `cancel_url`: URL برای cancel button

**URL**: `/production/machines/create/`

---

## MachineUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `production/machine_form.html` (extends `shared/generic/generic_form.html`)

**Form**: `MachineForm`

**Success URL**: `production:machines`

**Attributes**:
- `model`: `Machine`
- `form_class`: `MachineForm`
- `template_name`: `'production/machine_form.html'`
- `success_url`: `reverse_lazy('production:machines')`
- `feature_code`: `'production.machines'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` از `object.company_id`

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `company_id` را از `self.object.company_id` اضافه می‌کند
3. kwargs را برمی‌گرداند

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `Machine.objects.none()` برمی‌گرداند
3. فیلتر: `Machine.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `form_valid(self, form: MachineForm) -> HttpResponseRedirect`

**توضیح**: Machine را ذخیره می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `MachineForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. تنظیم `form.instance.edited_by = request.user`
2. نمایش پیام موفقیت: "Machine updated successfully."
3. فراخوانی `super().form_valid(form)` (ذخیره و redirect)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module` و `form_title`

**Context Variables اضافه شده**:
- `form_title`: `_('Edit Machine')`
- `breadcrumbs`: لیست breadcrumbs برای navigation
- `cancel_url`: URL برای cancel button

**URL**: `/production/machines/<pk>/edit/`

---

## MachineDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `production:machines`

**Attributes**:
- `model`: `Machine`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:machines')`
- `feature_code`: `'production.machines'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `Machine.objects.none()` برمی‌گرداند
3. فیلتر: `Machine.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: Machine را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "Machine deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که Machine را حذف می‌کند و redirect می‌کند)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم برای generic template

**Context Variables اضافه شده**:
- `delete_title`: `_('Delete Machine')`
- `confirmation_message`: پیام تأیید حذف
- `object_details`: لیست جزئیات machine برای نمایش (code, name, type, work_center)
- `cancel_url`: URL برای cancel
- `breadcrumbs`: لیست breadcrumbs

**URL**: `/production/machines/<pk>/delete/`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Optional select_related**: `select_related('work_center')` با try-except برای جلوگیری از خطا
4. **Generic Templates**: تمام templates به generic templates منتقل شده‌اند:
   - Machine List از `shared/generic/generic_list.html` extends می‌کند
   - Machine Form از `shared/generic/generic_form.html` extends می‌کند
   - Machine Delete از `shared/generic/generic_confirm_delete.html` استفاده می‌کند

