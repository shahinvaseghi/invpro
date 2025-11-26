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
1. `active_company_id` را از session دریافت می‌کند
2. اگر `active_company_id` وجود ندارد، خطا نمایش می‌دهد و `form_invalid` برمی‌گرداند
3. `form.instance.company_id` و `created_by` را تنظیم می‌کند
4. اگر `is_enabled` تنظیم نشده است، آن را به `1` تنظیم می‌کند
5. BOM را ذخیره می‌کند
6. formset را با instance می‌سازد
7. formset را validate می‌کند
8. اگر formset معتبر نیست:
   - BOM را حذف می‌کند
   - خطاهای formset را نمایش می‌دهد
   - response با form و formset برمی‌گرداند
9. formset را ذخیره می‌کند:
   - برای هر instance:
     - `line_number`, `company_id`, `created_by` را تنظیم می‌کند
     - `material_item_code` را از `material_item.item_code` auto-fill می‌کند
     - `material_type` را از `material_item.type` auto-set می‌کند (اگر تنظیم نشده باشد)
     - instance را ذخیره می‌کند
   - خطوط marked for deletion را حذف می‌کند
10. پیام موفقیت را نمایش می‌دهد
11. redirect می‌کند

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
1. formset را از context دریافت می‌کند
2. formset را validate می‌کند
3. اگر formset معتبر نیست:
   - خطاهای formset را نمایش می‌دهد
   - `form_invalid` برمی‌گرداند
4. `form.instance.edited_by` را تنظیم می‌کند
5. BOM را ذخیره می‌کند
6. formset را ذخیره می‌کند (مشابه `BOMCreateView`)
7. پیام موفقیت را نمایش می‌دهد
8. redirect می‌کند

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
- queryset را بر اساس `active_company_id` فیلتر می‌کند

---

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: BOM را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. پیام موفقیت را نمایش می‌دهد
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

