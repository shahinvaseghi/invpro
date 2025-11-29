# ticketing/views/templates.py - Ticket Template Views (Complete Documentation)

**هدف**: Views برای مدیریت ticket templates در ماژول ticketing

این فایل شامل views برای:
- TicketTemplateListView: فهرست templates
- TicketTemplateCreateView: ایجاد template جدید
- TicketTemplateUpdateView: ویرایش template
- TicketTemplateDeleteView: حذف template

---

## وابستگی‌ها

- `ticketing.models`: `TicketTemplate`, `TicketCategory`, `TicketPriority`
- `ticketing.forms.templates`: `TicketTemplateForm`, `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`
- `ticketing.views.base`: `TicketingBaseView`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.db.transaction`
- `django.db.models.Q`
- `django.urls.reverse_lazy`
- `django.utils.translation.gettext_lazy`

---

## TicketTemplateListView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, ListView`

**Template**: `ticketing/templates_list.html`

**Attributes**:
- `model`: `TicketTemplate`
- `template_name`: `'ticketing/templates_list.html'`
- `context_object_name`: `'templates'`
- `paginate_by`: `50`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'view_all'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، search، و category filtering برمی‌گرداند (با debug logging).

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. دریافت `company_id` از session
2. **Debug logging** (print statements):
   - Log company_id، user، session keys
   - Log تمام templates در database
   - Log templates برای company
3. **Company filtering**:
   - اگر `company_id` موجود است:
     - فیلتر: `TicketTemplate.objects.filter(company_id=company_id)`
   - در غیر این صورت:
     - `TicketTemplate.objects.none()`
4. **Search filtering** (اگر `search` در query parameter وجود دارد):
   - فیلتر با `Q(name__icontains=search) | Q(template_code__icontains=search) | Q(description__icontains=search)`
5. **Category filtering** (اگر `category` در query parameter وجود دارد):
   - فیلتر: `queryset.filter(category_id=category_id)`
6. مرتب‌سازی: `order_by('sort_order', 'template_code', 'name')`
7. **Debug logging**: Log final queryset count
8. queryset را برمی‌گرداند

**Query Parameters**:
- `search`: جستجو در name، template_code، description
- `category`: فیلتر بر اساس category ID

**نکات مهم**:
- شامل debug print statements برای troubleshooting است

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند (با debug logging).

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`, `categories`, `search_term`, `selected_category`

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `page_title = _('Ticket Templates')`
3. **Debug logging** (print statements):
   - Log context keys
   - Log templates در context (type، count، details)
   - Log pagination info
4. **دریافت categories برای filter dropdown**:
   - دریافت `company_id` از session
   - اگر `company_id` موجود است:
     - فیلتر: `TicketCategory.objects.filter(company_id=company_id, is_enabled=1)`
     - مرتب‌سازی: `order_by('name')`
     - اضافه کردن `categories` به context
5. اضافه کردن `search_term = request.GET.get('search', '')`
6. اضافه کردن `selected_category = request.GET.get('category', '')`
7. context را برمی‌گرداند

**Context Variables اضافه شده**:
- `page_title`: `_('Ticket Templates')`
- `categories`: QuerySet از categories (برای filter dropdown)
- `search_term`: مقدار `search` از query parameter
- `selected_category`: مقدار `category` از query parameter

**نکات مهم**:
- شامل debug print statements برای troubleshooting است

**Query Parameters**:
- `search`: جستجو در name, template_code, description
- `category`: فیلتر بر اساس category

**URL**: `/ticketing/templates/`

---

## TicketTemplateCreateView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, CreateView`

**Template**: `ticketing/template_form.html`

**Form**: `TicketTemplateForm`

**Formsets**: `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`

**Success URL**: `ticketing:templates`

**Attributes**:
- `model`: `TicketTemplate`
- `form_class`: `TicketTemplateForm`
- `template_name`: `'ticketing/template_form.html'`
- `success_url`: `reverse_lazy('ticketing:templates')`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `request` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `request` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. اضافه کردن `kwargs['request'] = self.request`
3. kwargs را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند (با 3 formsets).

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`, 3 formsets، `categories`, `priorities`

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `page_title = _('Create Template')`
3. **ساخت 3 formsets**:
   - دریافت `instance` (در CreateView، `self.object` ممکن است None باشد)
   - اگر `request.POST`: از POST data
   - در غیر این صورت: empty formsets
   - `field_formset`: `TicketTemplateFieldFormSet`
   - `permission_formset`: `TicketTemplatePermissionFormSet`
   - `event_formset`: `TicketTemplateEventFormSet`
4. اضافه کردن formsets به context
5. **دریافت categories و priorities**:
   - دریافت `company_id` از session
   - اگر `company_id` موجود است:
     - `categories`: `TicketCategory.objects.filter(company_id=company_id, is_enabled=1).order_by('name')`
     - `priorities`: `TicketPriority.objects.filter(company_id=company_id, is_enabled=1).order_by('priority_level')`
     - اضافه کردن به context
6. context را برمی‌گرداند

**Context Variables اضافه شده**:
- `page_title`: `_('Create Template')`
- `field_formset`: `TicketTemplateFieldFormSet`
- `permission_formset`: `TicketTemplatePermissionFormSet`
- `event_formset`: `TicketTemplateEventFormSet`
- `categories`: QuerySet از categories
- `priorities`: QuerySet از priorities

---

#### `form_valid(self, form: TicketTemplateForm) -> HttpResponseRedirect`

**توضیح**: Template و تمام formsets را ذخیره می‌کند (با debug logging).

**پارامترهای ورودی**:
- `form`: فرم معتبر `TicketTemplateForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**Decorator**: `@transaction.atomic` (تمام عملیات در یک transaction)

**منطق**:
1. دریافت `company_id` از session
2. اگر `company_id` موجود است:
   - تنظیم `form.instance.company_id = company_id`
3. **Debug logging** (print statements):
   - Log company_id، user، template name/code، is_enabled
4. ذخیره template: `response = super().form_valid(form)`
5. **Debug logging** (print statements):
   - Log template ID، template_code، company_id بعد از save
   - Verify template در database
6. **ذخیره field formset**:
   - `TicketTemplateFieldFormSet(self.request.POST, instance=self.object)`
   - اگر valid:
     - `field_formset.save(commit=False)` (برای دریافت instances)
     - برای هر `field`:
       - تنظیم `field.company_id = company_id`
       - اگر `field.template` موجود است:
         - تنظیم `field.template_code = field.template.template_code`
       - `field.save()`
     - `field_formset.save()` (برای حذف deleted items)
   - اگر invalid: بازگشت `form_invalid(form)`
7. **ذخیره permission formset**:
   - `TicketTemplatePermissionFormSet(self.request.POST, instance=self.object)`
   - اگر valid:
     - `permission_formset.save(commit=False)` (برای دریافت instances)
     - برای هر `permission`:
       - تنظیم `permission.company_id = company_id`
       - اگر `permission.template` موجود است:
         - تنظیم `permission.template_code = permission.template.template_code`
       - `permission.save()`
     - `permission_formset.save()` (برای حذف deleted items)
   - اگر invalid: بازگشت `form_invalid(form)`
8. **ذخیره event formset**:
   - `TicketTemplateEventFormSet(self.request.POST, instance=self.object)`
   - اگر valid:
     - `event_formset.save(commit=False)` (برای دریافت instances)
     - برای هر `event`:
       - تنظیم `event.company_id = company_id`
       - اگر `event.template` موجود است:
         - تنظیم `event.template_code = event.template.template_code`
       - `event.save()`
     - `event_formset.save()` (برای حذف deleted items)
   - اگر invalid: بازگشت `form_invalid(form)`
9. نمایش پیام موفقیت: "Template created successfully."
10. بازگشت `response`

**نکات مهم**:
- تمام عملیات در یک `@transaction.atomic` انجام می‌شود
- اگر هر formset invalid باشد، کل transaction rollback می‌شود
- `template_code` برای fields، permissions، events به صورت خودکار تنظیم می‌شود
- شامل debug print statements برای troubleshooting است

**نکات مهم**:
- از `@transaction.atomic` استفاده می‌کند
- 3 formsets مدیریت می‌شوند: fields, permissions, events

**URL**: `/ticketing/templates/create/`

---

## TicketTemplateUpdateView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, UpdateView`

**Template**: `ticketing/template_form.html`

**Form**: `TicketTemplateForm`

**Formsets**: `TicketTemplateFieldFormSet`, `TicketTemplatePermissionFormSet`, `TicketTemplateEventFormSet`

**Success URL**: `ticketing:templates`

**Attributes**:
- `model`: `TicketTemplate`
- `form_class`: `TicketTemplateForm`
- `template_name`: `'ticketing/template_form.html'`
- `success_url`: `reverse_lazy('ticketing:templates')`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `request` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `request` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. اضافه کردن `kwargs['request'] = self.request`
3. kwargs را برمی‌گرداند

---

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `company_id` از session
2. فیلتر: `TicketTemplate.objects.filter(company_id=company_id)`
3. queryset را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند (با 3 formsets و debug logging).

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`, 3 formsets، `categories`, `priorities`

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `page_title = _('Edit Template')`
3. **ساخت 3 formsets**:
   - اگر `request.POST`: از POST data
   - در غیر این صورت: از instance
   - `field_formset`: `TicketTemplateFieldFormSet`
   - `permission_formset`: `TicketTemplatePermissionFormSet`
   - `event_formset`: `TicketTemplateEventFormSet`
4. **Debug logging** (فقط در GET mode):
   - Log template ID
   - برای هر field: Log field_key، field_type، field_config (type و value)
   - اگر field_config dict است: Log as JSON string
5. اضافه کردن formsets به context
6. **دریافت categories و priorities**:
   - دریافت `company_id` از session
   - اگر `company_id` موجود است:
     - `categories`: `TicketCategory.objects.filter(company_id=company_id, is_enabled=1).order_by('name')`
     - `priorities`: `TicketPriority.objects.filter(company_id=company_id, is_enabled=1).order_by('priority_level')`
     - اضافه کردن به context
7. context را برمی‌گرداند

**Context Variables اضافه شده**:
- `page_title`: `_('Edit Template')`
- `field_formset`: `TicketTemplateFieldFormSet`
- `permission_formset`: `TicketTemplatePermissionFormSet`
- `event_formset`: `TicketTemplateEventFormSet`
- `categories`: QuerySet از categories
- `priorities`: QuerySet از priorities

**نکات مهم**:
- شامل debug print statements برای troubleshooting field_config است

---

#### `form_valid(self, form: TicketTemplateForm) -> HttpResponseRedirect`

**توضیح**: Template و تمام formsets را ذخیره می‌کند (با debug logging).

**پارامترهای ورودی**:
- `form`: فرم معتبر `TicketTemplateForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**Decorator**: `@transaction.atomic` (تمام عملیات در یک transaction)

**منطق**:
1. ذخیره template: `response = super().form_valid(form)`
2. دریافت `company_id` از session
3. **ذخیره field formset**:
   - `TicketTemplateFieldFormSet(self.request.POST, instance=self.object)`
   - **Debug logging**: Log field_config values از POST data
   - اگر valid:
     - `field_formset.save(commit=False)` (برای دریافت instances)
     - برای هر `field` (با index):
       - **Debug logging**: Log field_key، field_type، field_config (before save)
       - تنظیم `field.company_id = company_id`
       - اگر `field.template` موجود است:
         - تنظیم `field.template_code = field.template.template_code`
       - `field.save()`
       - **Debug logging**: Log field_config (after save)
     - `field_formset.save()` (برای حذف deleted items)
   - اگر invalid:
     - **Debug logging**: Log errors
     - بازگشت `form_invalid(form)`
4. **ذخیره permission formset**:
   - `TicketTemplatePermissionFormSet(self.request.POST, instance=self.object)`
   - اگر valid:
     - `permission_formset.save(commit=False)` (برای دریافت instances)
     - برای هر `permission`:
       - تنظیم `permission.company_id = company_id`
       - اگر `permission.template` موجود است:
         - تنظیم `permission.template_code = permission.template.template_code`
       - `permission.save()`
     - `permission_formset.save()` (برای حذف deleted items)
   - اگر invalid: بازگشت `form_invalid(form)`
5. **ذخیره event formset**:
   - `TicketTemplateEventFormSet(self.request.POST, instance=self.object)`
   - اگر valid:
     - `event_formset.save(commit=False)` (برای دریافت instances)
     - برای هر `event`:
       - تنظیم `event.company_id = company_id`
       - اگر `event.template` موجود است:
         - تنظیم `event.template_code = event.template.template_code`
       - `event.save()`
     - `event_formset.save()` (برای حذف deleted items)
   - اگر invalid: بازگشت `form_invalid(form)`
6. نمایش پیام موفقیت: "Template updated successfully."
7. بازگشت `response`

**نکات مهم**:
- تمام عملیات در یک `@transaction.atomic` انجام می‌شود
- اگر هر formset invalid باشد، کل transaction rollback می‌شود
- `template_code` برای fields، permissions، events به صورت خودکار تنظیم می‌شود
- شامل debug print statements برای troubleshooting field_config است

**نکات مهم**:
- Debug logging برای `field_config` در edit mode
- از `@transaction.atomic` استفاده می‌کند

**URL**: `/ticketing/templates/<pk>/edit/`

---

## TicketTemplateDeleteView

**Type**: `FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView`

**Template**: `ticketing/template_confirm_delete.html`

**Success URL**: `ticketing:templates`

**Attributes**:
- `model`: `TicketTemplate`
- `template_name`: `'ticketing/template_confirm_delete.html'`
- `success_url`: `reverse_lazy('ticketing:templates')`
- `feature_code`: `'ticketing.management.templates'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `company_id` از session
2. فیلتر: `TicketTemplate.objects.filter(company_id=company_id)`
3. queryset را برمی‌گرداند

---

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: TicketTemplate را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "Template deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که TicketTemplate را حذف می‌کند و redirect می‌کند)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `page_title`

**Context Variables اضافه شده**:
- `page_title`: `_('Delete Template')`

**URL**: `/ticketing/templates/<pk>/delete/`

---

## نکات مهم

1. **Multi-formset Management**: 3 formsets مدیریت می‌شوند (fields, permissions, events)
2. **Template Code**: `template_code` برای fields, permissions, events به صورت خودکار تنظیم می‌شود
3. **Transaction Management**: از `@transaction.atomic` استفاده می‌شود
4. **Debug Logging**: در UpdateView برای `field_config` debug logging وجود دارد

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Formset Management**: 3 formsets در create و update views مدیریت می‌شوند

