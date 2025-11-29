# production/views/product_order.py - Product Order Views (Complete Documentation)

**هدف**: Views برای مدیریت سفارشات تولید در ماژول production

این فایل شامل views برای:
- ProductOrderListView: فهرست سفارشات
- ProductOrderCreateView: ایجاد سفارش جدید (با قابلیت ایجاد transfer request)
- ProductOrderUpdateView: ویرایش سفارش (با قابلیت ایجاد transfer request)
- ProductOrderDeleteView: حذف سفارش

---

## وابستگی‌ها

- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `shared.utils.permissions`: `get_user_feature_permissions`, `has_feature_permission`
- `inventory.utils.codes`: `generate_sequential_code`
- `production.forms`: `ProductOrderForm`, `TransferToLineItemFormSet`
- `production.models`: `ProductOrder`, `TransferToLine`, `TransferToLineItem`
- `django.views.generic`: `CreateView`, `DeleteView`, `ListView`, `UpdateView`
- `django.contrib.messages`
- `django.db.transaction`
- `django.http.HttpResponseRedirect`
- `django.urls.reverse_lazy`
- `django.utils.timezone`
- `django.utils.translation.gettext_lazy`

---

## ProductOrderListView

**Type**: `FeaturePermissionRequiredMixin, ListView`

**Template**: `production/product_orders.html`

**Attributes**:
- `model`: `ProductOrder`
- `template_name`: `'production/product_orders.html'`
- `context_object_name`: `'product_orders'`
- `paginate_by`: `50`
- `feature_code`: `'production.product_orders'`
- `required_action`: `'view_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering، select_related، و ordering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده با optimizations

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `ProductOrder.objects.none()` برمی‌گرداند
3. فیلتر: `ProductOrder.objects.filter(company_id=active_company_id)`
4. **select_related**: `'finished_item'`, `'bom'`, `'process'`, `'approved_by'`
5. مرتب‌سازی: `order_by('-order_date', 'order_code')` (جدیدترین اول)
6. queryset را برمی‌گرداند

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/product-orders/`

---

## ProductOrderCreateView

**Type**: `FeaturePermissionRequiredMixin, CreateView`

**Template**: `production/product_order_form.html`

**Form**: `ProductOrderForm`

**Success URL**: `production:product_orders`

**Attributes**:
- `model`: `ProductOrder`
- `form_class`: `ProductOrderForm`
- `template_name`: `'production/product_order_form.html'`
- `success_url`: `reverse_lazy('production:product_orders')`
- `feature_code`: `'production.product_orders'`
- `required_action`: `'create'`

**متدها**:

#### `get_form_kwargs() -> Dict[str, Any]`
- اضافه کردن `company_id` به form

#### `form_valid(self, form: ProductOrderForm) -> HttpResponseRedirect`

**توضیح**: ذخیره product order و (اختیاری) ایجاد transfer request.

**پارامترهای ورودی**:
- `form`: فرم معتبر `ProductOrderForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success URL

**منطق**:
1. بررسی `active_company_id` (اگر وجود نداشته باشد، error و `form_invalid` برمی‌گرداند)
2. تنظیم `form.instance.company_id` و `created_by`
3. اگر BOM انتخاب شده باشد:
   - تنظیم `finished_item` از `bom.finished_item`
   - تنظیم `finished_item_code` از `bom.finished_item.item_code`
   - تنظیم `bom_code` از `bom.bom_code`
4. تولید `order_code`:
   - اگر `order_code` وجود نداشته باشد:
     - استفاده از `generate_sequential_code()` با width `10`
5. تنظیم `unit`:
   - اگر `finished_item` موجود باشد و `unit` تنظیم نشده باشد:
     - تنظیم `unit` از `finished_item.primary_unit` یا `'pcs'` (fallback)
6. ذخیره product order با `super().form_valid(form)`
7. بررسی `create_transfer_request`:
   - اگر `create_transfer_request` checked باشد و `transfer_approved_by` انتخاب شده باشد:
     - بررسی permission با `has_feature_permission()` برای action `'create_transfer_from_order'`
     - اگر permission دارد:
       - ساخت `extra_items_formset` از POST data
       - فراخوانی `_create_transfer_request()`
       - نمایش پیام موفقیت (order + transfer)
     - اگر permission ندارد:
       - نمایش warning message
     - اگر exception رخ دهد:
       - نمایش warning message با error details
   - اگر `create_transfer_request` checked نباشد:
     - نمایش پیام موفقیت (فقط order)
8. بازگشت response

**نکات مهم**:
- از `@transaction.atomic` decorator استفاده می‌کند
- می‌تواند transfer request ایجاد کند (اگر permission داشته باشد)
- `order_code` به صورت خودکار تولید می‌شود
- اگر transfer request creation fail شود، order همچنان ذخیره می‌شود

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: اضافه کردن active module, form title, و extra items formset به context.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`, `form_title`, و `extra_items_formset`

**منطق**:
1. دریافت context از `super().get_context_data()`
2. اضافه کردن `active_module = 'production'`
3. اضافه کردن `form_title = _('Create Product Order')`
4. بررسی permission برای `create_transfer_from_order`:
   - اگر permission دارد یا user superuser است:
     - ساخت `TransferToLineItemFormSet`:
       - اگر POST: از POST data
       - اگر GET: empty formset
       - استفاده از temporary `TransferToLine` instance
       - prefix: `'extra_items'`
     - اضافه کردن `extra_items_formset` به context
5. بازگشت context

#### `_create_transfer_request(self, order: ProductOrder, approved_by, company_id: int) -> TransferToLine`

**توضیح**: Helper method برای ایجاد transfer request از product order.

**پارامترهای ورودی**:
- `order` (ProductOrder): Product order instance
- `approved_by`: User برای approval
- `company_id` (int): شناسه شرکت

**مقدار بازگشتی**:
- `TransferToLine`: transfer request ایجاد شده

**منطق**:
1. بررسی اینکه order دارای BOM باشد (اگر نباشد، `ValueError` می‌دهد)
2. ایجاد `TransferToLine` instance:
   - تنظیم `company_id`, `order`, `order_code`, `transfer_date` (امروز)
   - تنظیم `status = PENDING_APPROVAL`
   - تنظیم `approved_by`, `created_by`
3. تولید `transfer_code`:
   - استفاده از `generate_sequential_code()` با prefix `'TR'` و width `8`
   - ذخیره با `save(update_fields=['transfer_code'])`
4. ایجاد items از BOM:
   - برای هر `BOMMaterial`:
     - محاسبه `quantity_required = quantity_planned × quantity_per_unit`
     - پیدا کردن `source_warehouse` از `ItemWarehouse` (اولین allowed warehouse)
     - اگر warehouse پیدا نشد، warning نمایش می‌دهد و item را skip می‌کند
     - تلاش برای پیدا کردن `destination_work_center` از process (فعلاً None)
     - ایجاد `TransferToLineItem`:
       - تنظیم `material_item`, `material_item_code`
       - تنظیم `quantity_required`, `unit`
       - تنظیم `source_warehouse`, `source_warehouse_code`
       - تنظیم `material_scrap_allowance` از BOM
       - تنظیم `is_extra = 0` (از BOM)
5. ذخیره extra items از formset:
   - اگر `extra_items_formset` موجود باشد و valid باشد:
     - برای هر item form:
       - اگر valid و not deleted باشد:
         - ذخیره با `commit=False`
         - تنظیم `transfer`, `company_id`, `is_extra = 1`, `created_by`
         - ذخیره item
6. بازگشت transfer instance

**نکات مهم**:
- اگر BOM نداشته باشد، `ValueError` می‌دهد
- اگر warehouse برای item پیدا نشد، warning نمایش می‌دهد و item را skip می‌کند
- Extra items با `is_extra = 1` علامت‌گذاری می‌شوند
- BOM items با `is_extra = 0` علامت‌گذاری می‌شوند

**URL**: `/production/product-orders/create/`

---

## ProductOrderUpdateView

**Type**: `FeaturePermissionRequiredMixin, UpdateView`

**Template**: `production/product_order_form.html`

**Form**: `ProductOrderForm`

**Success URL**: `production:product_orders`

**Attributes**:
- `model`: `ProductOrder`
- `form_class`: `ProductOrderForm`
- `template_name`: `'production/product_order_form.html'`
- `success_url`: `reverse_lazy('production:product_orders')`
- `feature_code`: `'production.product_orders'`
- `required_action`: `'edit_own'`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`
- اضافه کردن `company_id` از `object.company_id` به form

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `ProductOrder.objects.none()` برمی‌گرداند
3. فیلتر: `ProductOrder.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

#### `form_valid(self, form: ProductOrderForm) -> HttpResponseRedirect`
- مشابه `ProductOrderCreateView.form_valid()` اما:
  - تنظیم `edited_by` به جای `created_by`
  - به‌روزرسانی `finished_item` و `bom_code` فقط اگر BOM تغییر کرده باشد
  - استفاده از `self.object.company_id` به جای `active_company_id` از session
  - پیام موفقیت: "Product order updated and transfer request created successfully." یا "Product order updated successfully."

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`, `form_title`, و `extra_items_formset`

**منطق**:
1. context را از `super().get_context_data()` دریافت می‌کند
2. اضافه کردن `active_module = 'production'`
3. اضافه کردن `form_title = _('Edit Product Order')`
4. بررسی permission برای `create_transfer_from_order`:
   - اگر `self.object` و `self.object.company_id` موجود است:
     - بررسی permission با `has_feature_permission()` برای action `'create_transfer_from_order'`
     - اگر permission دارد یا user superuser است:
       - ساخت `TransferToLineItemFormSet`:
         - اگر POST: از POST data
         - اگر GET: empty formset
         - استفاده از temporary `TransferToLine` instance
         - `form_kwargs={'company_id': self.object.company_id}`
         - prefix: `'extra_items'`
       - اضافه کردن `extra_items_formset` به context
5. بازگشت context

#### `_create_transfer_request(self, order, approved_by, company_id) -> TransferToLine`
- مشابه `ProductOrderCreateView._create_transfer_request()`

**URL**: `/production/product-orders/<pk>/edit/`

---

## ProductOrderDeleteView

**Type**: `FeaturePermissionRequiredMixin, DeleteView`

**Template**: `production/product_order_confirm_delete.html`

**Success URL**: `production:product_orders`

**Attributes**:
- `model`: `ProductOrder`
- `template_name`: `'production/product_order_confirm_delete.html'`
- `success_url`: `reverse_lazy('production:product_orders')`
- `feature_code`: `'production.product_orders'`
- `required_action`: `'delete_own'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با company filtering برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس company

**منطق**:
1. دریافت `active_company_id` از session
2. اگر `active_company_id` وجود ندارد، `ProductOrder.objects.none()` برمی‌گرداند
3. فیلتر: `ProductOrder.objects.filter(company_id=active_company_id)`
4. queryset را برمی‌گرداند

---

#### `delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect`

**توضیح**: Product Order را حذف می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. نمایش پیام موفقیت: "Product order deleted successfully."
2. فراخوانی `super().delete(request, *args, **kwargs)` (که Product Order را حذف می‌کند و redirect می‌کند)

---

#### `get_context_data(self, **kwargs: Any) -> Dict[str, Any]`

**توضیح**: context variables را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `active_module`

**Context Variables اضافه شده**:
- `active_module`: `'production'`

**URL**: `/production/product-orders/<pk>/delete/`

---

## نکات مهم

### 1. Transfer Request Creation
- می‌تواند از product order یک transfer request ایجاد کند
- نیاز به permission `create_transfer_from_order` دارد
- Items از BOM به صورت خودکار ایجاد می‌شوند
- Extra items از formset ذخیره می‌شوند

### 2. Code Generation
- `order_code` به صورت خودکار با `generate_sequential_code()` تولید می‌شود
- `transfer_code` به صورت خودکار با prefix `'TR'` تولید می‌شود

### 3. Quantity Calculation
- `quantity_required = quantity_planned × quantity_per_unit` برای هر BOM material

### 4. Warehouse Selection
- `source_warehouse` از `ItemWarehouse` (اولین allowed warehouse) انتخاب می‌شود

### 5. Transaction Management
- از `@transaction.atomic` استفاده می‌کند برای atomic operations

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `active_company_id` فیلتر می‌شوند
2. **Permission Checking**: تمام views از `FeaturePermissionRequiredMixin` استفاده می‌کنند
3. **Auto-population**: `finished_item`, `finished_item_code`, `bom_code` از BOM تنظیم می‌شوند
4. **Code Generation**: `order_code` و `transfer_code` به صورت خودکار تولید می‌شوند

