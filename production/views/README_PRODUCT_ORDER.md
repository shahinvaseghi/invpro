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
- `get_queryset()`: فیلتر بر اساس company، `select_related('finished_item', 'bom', 'process', 'approved_by')`، مرتب بر اساس `-order_date`, `order_code`
- `get_context_data()`: اضافه کردن `active_module`

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

#### `form_valid(form: ProductOrderForm) -> HttpResponseRedirect`
**منطق**:
1. تنظیم `company_id`, `created_by`
2. تنظیم `finished_item`, `finished_item_code`, `bom_code` از BOM
3. تولید `order_code` اگر وجود ندارد
4. تنظیم `unit` از `finished_item.primary_unit`
5. ذخیره product order
6. اگر `create_transfer_request` checked باشد:
   - بررسی permission
   - ایجاد transfer request با `_create_transfer_request()`
   - ایجاد items از BOM
   - ذخیره extra items از formset

**نکات مهم**:
- از `@transaction.atomic` استفاده می‌کند
- می‌تواند transfer request ایجاد کند
- `order_code` به صورت خودکار تولید می‌شود

#### `get_context_data(**kwargs) -> Dict[str, Any]`
- اضافه کردن `active_module`, `form_title`
- اضافه کردن `extra_items_formset` (اگر permission دارد)

#### `_create_transfer_request(order, approved_by, company_id) -> TransferToLine`
**Helper Method**: ایجاد transfer request از product order

**منطق**:
1. ایجاد `TransferToLine` instance
2. تولید `transfer_code`
3. ایجاد items از BOM:
   - محاسبه `quantity_required = quantity_planned × quantity_per_unit`
   - پیدا کردن `source_warehouse` از `ItemWarehouse`
   - ایجاد `TransferToLineItem` برای هر BOM material
4. ذخیره extra items از formset

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
- `get_form_kwargs()`: اضافه کردن `company_id` از `object.company_id`
- `get_queryset()`: فیلتر بر اساس company
- `form_valid()`: مشابه `ProductOrderCreateView.form_valid()` اما با `edited_by`
- `get_context_data()`: مشابه `ProductOrderCreateView.get_context_data()`
- `_create_transfer_request()`: مشابه `ProductOrderCreateView._create_transfer_request()`

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
- `get_queryset()`: فیلتر بر اساس company
- `delete()`: نمایش پیام موفقیت و حذف
- `get_context_data()`: اضافه کردن `active_module`

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

