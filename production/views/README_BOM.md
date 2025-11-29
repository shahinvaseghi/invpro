# production/views/bom.py - BOM Views (Complete Documentation)

**هدف**: Views برای مدیریت BOM (Bill of Materials) در ماژول production

این فایل شامل views برای:
- BOMListView: فهرست BOM ها
- BOMCreateView: ایجاد BOM جدید
- BOMUpdateView: ویرایش BOM
- BOMDeleteView: حذف BOM

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `production.forms`: `BOMForm`, `BOMMaterialLineFormSet`
- `production.models`: `BOM`, `BOMMaterial`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.http.HttpResponseRedirect`
- `django.shortcuts.redirect`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## BOMListView

### `BOMListView`

**توضیح**: فهرست تمام BOM های شرکت فعال

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/bom_list.html`

**Attributes**:
- `model`: `BOM`
- `template_name`: `'production/bom_list.html'`
- `context_object_name`: `'boms'`
- `paginate_by`: `50`
- `feature_code`: `'production.bom'`

**Context Variables**:
- `boms`: queryset BOM ها (paginated)
- `active_module`: `'production'`
- `finished_items`: لیست محصولات نهایی برای فیلتر dropdown

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering و optional finished_item filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. `active_company_id` را از session دریافت می‌کند
2. اگر `active_company_id` وجود ندارد، `BOM.objects.none()` برمی‌گرداند
3. queryset را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
4. `select_related('finished_item', 'company')` و `prefetch_related('materials')` را اعمال می‌کند
5. مرتب می‌کند بر اساس `finished_item__item_code`, `-version`
6. اگر `finished_item` در query parameter وجود دارد، فیلتر می‌کند
7. queryset را برمی‌گرداند

**Query Parameters**:
- `finished_item`: فیلتر بر اساس محصول نهایی

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم

**Context Variables اضافه شده**:
- `active_module`: `'production'`
- `finished_items`: لیست dictionaries با `id`, `code`, `name` برای فیلتر dropdown

**URL**: `/production/bom/`

---

## BOMCreateView

### `BOMCreateView`

**توضیح**: ایجاد BOM جدید با مواد اولیه (multi-line)

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `production/bom_form.html`

**Form**: `BOMForm`

**Formset**: `BOMMaterialLineFormSet`

**Success URL**: `production:bom_list`

**Attributes**:
- `model`: `BOM`
- `form_class`: `BOMForm`
- `template_name`: `'production/bom_form.html'`
- `success_url`: `reverse_lazy('production:bom_list')`
- `feature_code`: `'production.bom'`
- `required_action`: `'create'`

**Context Variables**:
- `form`: instance فرم `BOMForm`
- `formset`: instance formset `BOMMaterialLineFormSet`
- `active_module`: `'production'`
- `form_title`: `_('Create BOM')`

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

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: formset را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `formset` اضافه شده

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. `active_module` و `form_title` را اضافه می‌کند
3. اگر `request.POST` وجود دارد:
   - formset را از POST data می‌سازد (بدون instance)
   - اگر form خطا دارد، خطاها را نمایش می‌دهد
4. اگر `request.POST` وجود ندارد:
   - formset خالی می‌سازد
5. context را برمی‌گرداند

---

#### `form_valid(self, form: BOMForm) -> HttpResponseRedirect`

**توضیح**: BOM و خطوط مواد را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `BOMForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد:
   - خطا: "Please select a company first."
   - `form_invalid()` برمی‌گرداند
3. تنظیم `form.instance.company_id = active_company_id`
4. تنظیم `form.instance.created_by = request.user`
5. تنظیم `form.instance.is_enabled = 1` (اگر تنظیم نشده باشد)
6. **ذخیره BOM**:
   - `self.object = form.save()` (با error handling)
   - اگر خطا رخ دهد، خطا نمایش می‌دهد و `form_invalid()` برمی‌گرداند
7. **ساخت formset با instance**:
   - `BOMMaterialLineFormSet(self.request.POST, instance=self.object, prefix='materials', form_kwargs={'company_id': active_company_id})`
8. **Validate formset**:
   - `is_valid = formset.is_valid()`
   - اگر معتبر نیست:
     - **حذف BOM**: `self.object.delete()` (چون formset معتبر نیست)
     - **نمایش خطاها**:
       - خطاهای `non_form_errors()` را نمایش می‌دهد
       - برای هر form در formset: خطاهای هر field را با label نمایش می‌دهد (format: "❌ ردیف {i+1} - {field_label}: {error}")
       - اگر هیچ خطای خاصی نیست: "Please fill in all required fields in the material lines."
     - **بازگشت response**: `render_to_response(context)` با form و formset
9. **ذخیره formset**:
   - `instances = formset.save(commit=False)`
   - برای هر `line_instance`:
     - **Validation**: بررسی `material_item` و `unit` (اگر وجود ندارد، skip)
     - تنظیم `line_instance.bom = self.object`
     - تنظیم `line_instance.line_number = line_number` (sequential از 1)
     - تنظیم `line_instance.company_id = active_company_id`
     - تنظیم `line_instance.created_by = request.user`
     - **Auto-fill `material_item_code`**: `line_instance.material_item_code = line_instance.material_item.item_code`
     - **Auto-set `material_type`**: اگر تنظیم نشده باشد، از `line_instance.material_item.type` (اگر type وجود ندارد، خطا و skip)
     - ذخیره `line_instance.save()` (با error handling)
     - افزایش `line_number` و `saved_count`
   - **حذف خطوط**: `formset.deleted_objects` را حذف می‌کند
   - اگر خطا در save رخ دهد: BOM را حذف می‌کند و response با errors برمی‌گرداند
10. **پیام‌ها**:
    - اگر `saved_count == 0`: warning: "BOM created but no material lines were saved."
    - در غیر این صورت: success: "BOM created successfully with {count} material line(s)."
11. Redirect به `success_url`

**نکات مهم**:
- اگر formset معتبر نیست، BOM حذف می‌شود
- `line_number` به صورت sequential تنظیم می‌شود
- `material_item_code` و `material_type` به صورت خودکار populate می‌شوند

**URL**: `/production/bom/create/`

---

## BOMUpdateView

### `BOMUpdateView`

**توضیح**: ویرایش BOM موجود

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `production/bom_form.html`

**Form**: `BOMForm`

**Formset**: `BOMMaterialLineFormSet`

**Success URL**: `production:bom_list`

**Attributes**:
- `model`: `BOM`
- `form_class`: `BOMForm`
- `template_name`: `'production/bom_form.html'`
- `success_url`: `reverse_lazy('production:bom_list')`
- `feature_code`: `'production.bom'`
- `required_action`: `'edit_own'`

**Context Variables**:
- مشابه `BOMCreateView` اما با `form_title = _('Edit BOM')` و `object`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` از `object.company_id`

**منطق**:
- `company_id` را از `self.object.company_id` اضافه می‌کند

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
- queryset را بر اساس `active_company_id` فیلتر می‌کند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: formset را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `formset` اضافه شده

**منطق**:
- مشابه `BOMCreateView.get_context_data()` اما با instance موجود

---

#### `form_valid(self, form: BOMForm) -> HttpResponseRedirect`

**توضیح**: BOM و خطوط مواد را ذخیره می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `BOMForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. دریافت formset از `self.get_context_data()['formset']`
2. **Validate formset**:
   - `is_valid = formset.is_valid()`
   - اگر معتبر نیست:
     - **نمایش خطاها**:
       - خطاهای `non_form_errors()` را نمایش می‌دهد
       - برای هر form در formset: خطاهای هر field را با label نمایش می‌دهد (format: "❌ ردیف {i+1} - {field_label}: {error}")
     - `form_invalid()` برمی‌گرداند
3. تنظیم `form.instance.edited_by = request.user`
4. **ذخیره BOM**:
   - `self.object = form.save()` (با error handling)
   - اگر خطا رخ دهد، خطا نمایش می‌دهد و `form_invalid()` برمی‌گرداند
5. **ذخیره formset**:
   - `instances = formset.save(commit=False)`
   - برای هر `line_instance`:
     - **Validation**: بررسی `material_item` و `unit` (اگر وجود ندارد، skip)
     - تنظیم `line_instance.bom = self.object`
     - تنظیم `line_instance.line_number = line_number` (sequential از 1)
     - تنظیم `line_instance.edited_by = request.user`
     - **Auto-fill `material_item_code`**: `line_instance.material_item_code = line_instance.material_item.item_code`
     - **Auto-set `material_type`**: اگر تنظیم نشده باشد، از `line_instance.material_item.type` (اگر type وجود ندارد، خطا و skip)
     - ذخیره `line_instance.save()` (با error handling)
     - افزایش `line_number`
   - **حذف خطوط**: `formset.deleted_objects` را حذف می‌کند
   - اگر خطا در save رخ دهد، خطا نمایش می‌دهد و `form_invalid()` برمی‌گرداند
6. پیام موفقیت: "BOM updated successfully."
7. `super().form_valid(form)` را فراخوانی می‌کند (redirect)

**نکات مهم**:
- `line_number` به صورت sequential تنظیم می‌شود
- خطوط marked for deletion حذف می‌شوند

**URL**: `/production/bom/<pk>/edit/`

---

## BOMDeleteView

### `BOMDeleteView`

**توضیح**: حذف BOM

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `production/bom_confirm_delete.html`

**Success URL**: `production:bom_list`

**Attributes**:
- `model`: `BOM`
- `template_name`: `'production/bom_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:bom_list')`
- `feature_code`: `'production.bom'`
- `required_action`: `'delete_own'`

**Context Variables**:
- `object`: instance BOM برای حذف
- `active_module`: `'production'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `BOM.objects.none()` برمی‌گرداند
3. فیلتر: `BOM.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: BOM را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "BOM deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که BOM را حذف می‌کند و redirect می‌کند)
2. `super().delete()` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: `active_module` را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module` اضافه شده

**URL**: `/production/bom/<pk>/delete/`

---

## استفاده در پروژه

### URL Patterns
```python
path('bom/', BOMListView.as_view(), name='bom_list'),
path('bom/create/', BOMCreateView.as_view(), name='bom_create'),
path('bom/<int:pk>/edit/', BOMUpdateView.as_view(), name='bom_edit'),
path('bom/<int:pk>/delete/', BOMDeleteView.as_view(), name='bom_delete'),
```

---

## نکات مهم

### 1. Formset Handling
- در `BOMCreateView`، اگر formset معتبر نیست، BOM حذف می‌شود
- در `BOMUpdateView`، خطوط marked for deletion حذف می‌شوند

### 2. Line Number Management
- `line_number` به صورت sequential (1, 2, 3, ...) تنظیم می‌شود
- برای هر خط معتبر (با `material_item`) تنظیم می‌شود

### 3. Auto-population
- `material_item_code` از `material_item.item_code` auto-fill می‌شود
- `material_type` از `material_item.type` auto-set می‌شود (اگر تنظیم نشده باشد)

### 4. Error Handling
- خطاهای formset به صورت prominent نمایش داده می‌شوند
- خطاهای هر خط به صورت جداگانه نمایش داده می‌شوند (با شماره خط)

### 5. Company Filtering
- تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Formset Management**: Create و Update views از formset برای مدیریت خطوط استفاده می‌کنند
4. **Error Display**: خطاها به صورت user-friendly نمایش داده می‌شوند

