# production/views/work_line.py - Work Line Views (Complete Documentation)

**هدف**: Views برای مدیریت خطوط کاری در ماژول production

این فایل شامل views برای:
- WorkLineListView: فهرست خطوط کاری
- WorkLineCreateView: ایجاد خط کاری جدید
- WorkLineUpdateView: ویرایش خط کاری
- WorkLineDeleteView: حذف خط کاری

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `WorkLineForm`
- `production.models`: `WorkLine`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## WorkLineListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/work_lines.html`

**Attributes**:
- `model`: `WorkLine`
- `template_name`: `'production/work_lines.html'`
- `context_object_name`: `'work_lines'`
- `paginate_by`: `50`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'view_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، optional select_related، و prefetch_related برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با optimizations

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `WorkLine.objects.none()` برمی‌گرداند
3. فیلتر: `WorkLine.objects.filter(company_id=active_company_id)`
4. **Optional select_related**:
   - تلاش برای `select_related('warehouse')` (با try-except برای جلوگیری از خطا در صورت عدم نصب inventory module)
   - اگر خطا رخ دهد، skip می‌کند
5. **prefetch_related**: `'personnel'`, `'machines'` (ManyToMany relationships)
6. مرتب‌سازی: `order_by('warehouse__name', 'sort_order', 'public_code')`
7. queryset را برمی‌گرداند

**نکات مهم**:
- `select_related('warehouse')` با try-except برای جلوگیری از خطا در صورت عدم نصب inventory module

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/work-lines/`

---

## WorkLineCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `production/work_line_form.html`

**Form**: `WorkLineForm`

**Success URL**: `production:work_lines`

**Attributes**:
- `model`: `WorkLine`
- `form_class`: `WorkLineForm`
- `template_name`: `'production/work_line_form.html'`
- `success_url`: `reverse_lazy('production:work_lines')`
- `feature_code`: `'production.work_lines'`
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

#### `form_valid(self, form: WorkLineForm) -> HttpResponseRedirect`

**توضیح**: WorkLine را ذخیره می‌کند، M2M relationships را ذخیره می‌کند، و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `WorkLineForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. تنظیم `form.instance.company_id = request.session.get('active_company_id')`
2. تنظیم `form.instance.created_by = request.user`
3. ذخیره WorkLine: `response = super().form_valid(form)`
4. **ذخیره M2M relationships**: `form.save_m2m()` (برای `personnel` و `machines`)
5. نمایش پیام موفقیت: "Work line created successfully."
6. بازگشت `response`

**نکات مهم**:
- `save_m2m()` برای ذخیره ManyToMany relationships (`personnel` و `machines`) فراخوانی می‌شود

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module` و `form_title`

**Context Variables اضافه شده**:
- `active_module`: `'production'`
- `form_title`: `_('Create Work Line')`

**نکات مهم**:
- `save_m2m()` برای ذخیره `personnel` و `machines` (ManyToMany) فراخوانی می‌شود

**URL**: `/production/work-lines/create/`

---

## WorkLineUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `production/work_line_form.html`

**Form**: `WorkLineForm`

**Success URL**: `production:work_lines`

**Attributes**:
- `model`: `WorkLine`
- `form_class`: `WorkLineForm`
- `template_name`: `'production/work_line_form.html'`
- `success_url`: `reverse_lazy('production:work_lines')`
- `feature_code`: `'production.work_lines'`
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
2. اگر `active_company_id` وجود ندارد، `WorkLine.objects.none()` برمی‌گرداند
3. فیلتر: `WorkLine.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `form_valid(self, form: WorkLineForm) -> HttpResponseRedirect`

**توضیح**: WorkLine را ذخیره می‌کند، M2M relationships را ذخیره می‌کند، و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `WorkLineForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. تنظیم `form.instance.edited_by = request.user`
2. ذخیره WorkLine: `response = super().form_valid(form)`
3. **ذخیره M2M relationships**: `form.save_m2m()` (برای `personnel` و `machines`)
4. نمایش پیام موفقیت: "Work line updated successfully."
5. بازگشت `response`

**نکات مهم**:
- `save_m2m()` برای ذخیره ManyToMany relationships (`personnel` و `machines`) فراخوانی می‌شود

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module` و `form_title`

**Context Variables اضافه شده**:
- `active_module`: `'production'`
- `form_title`: `_('Edit Work Line')`

**URL**: `/production/work-lines/<pk>/edit/`

---

## WorkLineDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `production/work_line_confirm_delete.html`

**Success URL**: `production:work_lines`

**Attributes**:
- `model`: `WorkLine`
- `template_name`: `'production/work_line_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:work_lines')`
- `feature_code`: `'production.work_lines'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `WorkLine.objects.none()` برمی‌گرداند
3. فیلتر: `WorkLine.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: WorkLine را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "Work line deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که WorkLine را حذف می‌کند و redirect می‌کند)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/work-lines/<pk>/delete/`

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **ManyToMany Handling**: `personnel` و `machines` با `save_m2m()` ذخیره می‌شوند
4. **Optional select_related**: `select_related('warehouse')` با try-except برای جلوگیری از خطا (اگر inventory module نصب نباشد)

