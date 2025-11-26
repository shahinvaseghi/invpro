# inventory/views/master_data.py - Master Data Views

**هدف**: CRUD views برای داده‌های اصلی (master data) ماژول inventory

این فایل شامل views برای مدیریت:
- Item Types (نوع کالا)
- Item Categories (دسته کالا)
- Item Subcategories (زیردسته کالا)
- Items (کالاها)
- Warehouses (انبارها)
- Suppliers (تامین‌کنندگان)
- Supplier Categories (دسته تامین‌کنندگان)

---

## Item Type Views

### `ItemTypeListView`

**توضیح**: فهرست انواع کالا

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/item_types.html`

**Context Variables**:
- `item_types`: queryset انواع کالا (paginated)

**Attributes**:
- `model`: `models.ItemType`
- `template_name`: `'inventory/item_types.html'`
- `context_object_name`: `'item_types'`
- `paginate_by`: `50`

**متدها**:
- هیچ متد سفارشی ندارد (از متدهای پیش‌فرض `ListView` و `InventoryBaseView` استفاده می‌کند)

**URL**: `/inventory/item-types/`

---

### `ItemTypeCreateView`

**توضیح**: ایجاد نوع کالای جدید

**Type**: `InventoryBaseView, CreateView`

**Template**: `inventory/itemtype_form.html`

**Form**: `ItemTypeForm`

**Success URL**: `inventory:item_types`

**Attributes**:
- `model`: `models.ItemType`
- `form_class`: `forms.ItemTypeForm`
- `template_name`: `'inventory/itemtype_form.html'`
- `success_url`: `reverse_lazy('inventory:item_types')`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: قبل از ذخیره، `company_id` و `created_by` را تنظیم می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `ItemTypeForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.company_id` را از `request.session.get('active_company_id')` تنظیم می‌کند
2. `form.instance.created_by` را به `request.user` تنظیم می‌کند
3. پیام موفقیت را با `messages.success()` نمایش می‌دهد
4. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: `form_title` را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = 'Create Item Type'` اضافه شده

**URL**: `/inventory/item-types/create/`

---

### `ItemTypeUpdateView`

**توضیح**: ویرایش نوع کالا

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/itemtype_form.html`

**Form**: `ItemTypeForm`

**Success URL**: `inventory:item_types`

**متدها**:
- `form_valid(form)`: `edited_by` را تنظیم می‌کند
- `get_context_data(**kwargs)`: `form_title` را اضافه می‌کند

**URL**: `/inventory/item-types/<pk>/edit/`

---

### `ItemTypeDeleteView`

**توضیح**: حذف نوع کالا

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/itemtype_confirm_delete.html`

**Success URL**: `inventory:item_types`

**متدها**:
- `delete(request, *args, **kwargs)`: پیام موفقیت نمایش می‌دهد

**URL**: `/inventory/item-types/<pk>/delete/`

---

## Item Category Views

### `ItemCategoryListView`

**توضیح**: فهرست دسته‌های کالا

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/item_categories.html`

**Context Variables**:
- `item_categories`: queryset دسته‌های کالا (paginated)

**URL**: `/inventory/item-categories/`

---

### `ItemCategoryCreateView`

**توضیح**: ایجاد دسته کالای جدید

**Type**: `InventoryBaseView, CreateView`

**Template**: `inventory/itemcategory_form.html`

**Form**: `ItemCategoryForm`

**Success URL**: `inventory:item_categories`

**متدها**:
- `form_valid(form)`: `company_id` و `created_by` را تنظیم می‌کند
- `get_context_data(**kwargs)`: `form_title` را اضافه می‌کند

**URL**: `/inventory/item-categories/create/`

---

### `ItemCategoryUpdateView`

**توضیح**: ویرایش دسته کالا

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/itemcategory_form.html`

**Form**: `ItemCategoryForm`

**Success URL**: `inventory:item_categories`

**متدها**:
- `form_valid(form)`: `edited_by` را تنظیم می‌کند
- `get_context_data(**kwargs)`: `form_title` را اضافه می‌کند

**URL**: `/inventory/item-categories/<pk>/edit/`

---

### `ItemCategoryDeleteView`

**توضیح**: حذف دسته کالا

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/itemcategory_confirm_delete.html`

**Success URL**: `inventory:item_categories`

**متدها**:
- `delete(request, *args, **kwargs)`: پیام موفقیت نمایش می‌دهد

**URL**: `/inventory/item-categories/<pk>/delete/`

---

## Item Subcategory Views

### `ItemSubcategoryListView`

**توضیح**: فهرست زیردسته‌های کالا

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/item_subcategories.html`

**Context Variables**:
- `item_subcategories`: queryset زیردسته‌های کالا (paginated)

**URL**: `/inventory/item-subcategories/`

---

### `ItemSubcategoryCreateView`

**توضیح**: ایجاد زیردسته کالای جدید

**Type**: `InventoryBaseView, CreateView`

**Template**: `inventory/itemsubcategory_form.html`

**Form**: `ItemSubcategoryForm`

**Success URL**: `inventory:item_subcategories`

**متدها**:
- `form_valid(form)`: `company_id` و `created_by` را تنظیم می‌کند
- `get_context_data(**kwargs)`: `form_title` را اضافه می‌کند

**URL**: `/inventory/item-subcategories/create/`

---

### `ItemSubcategoryUpdateView`

**توضیح**: ویرایش زیردسته کالا

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/itemsubcategory_form.html`

**Form**: `ItemSubcategoryForm`

**Success URL**: `inventory:item_subcategories`

**متدها**:
- `form_valid(form)`: `edited_by` را تنظیم می‌کند
- `get_context_data(**kwargs)`: `form_title` را اضافه می‌کند

**URL**: `/inventory/item-subcategories/<pk>/edit/`

---

### `ItemSubcategoryDeleteView`

**توضیح**: حذف زیردسته کالا

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/itemsubcategory_confirm_delete.html`

**Success URL**: `inventory:item_subcategories`

**متدها**:
- `delete(request, *args, **kwargs)`: پیام موفقیت نمایش می‌دهد

**URL**: `/inventory/item-subcategories/<pk>/delete/`

---

## Item Views

### `ItemListView`

**توضیح**: فهرست کالاها با فیلترهای پیشرفته

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/items.html`

**Context Variables**:
- `items`: queryset کالاها (paginated)
- فیلترهای اعمال شده

**فیلترها**:
- `type_id`: فیلتر بر اساس نوع
- `category_id`: فیلتر بر اساس دسته
- `subcategory_id`: فیلتر بر اساس زیردسته
- `search`: جستجو در کد و نام کالا

**URL**: `/inventory/items/`

---

### `ItemSerialListView`

**توضیح**: فهرست سریال‌های کالا

**Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, ListView`

**Template**: `inventory/item_serials.html`

**Context Variables**:
- `serials`: queryset سریال‌ها (paginated)

**Permission**: نیاز به `inventory.master.item_serials` permission

**URL**: `/inventory/item-serials/`

---

### `ItemCreateView`

**توضیح**: ایجاد کالای جدید با unit formset

**Type**: `ItemUnitFormsetMixin, InventoryBaseView, CreateView`

**Template**: `inventory/item_form.html`

**Form**: `ItemForm`

**Formset**: `ItemUnitFormSet`

**Success URL**: `inventory:items`

**متدها**:
- `form_valid(form)`: 
  - `company_id` و `created_by` را تنظیم می‌کند
  - unit formset را ذخیره می‌کند
  - warehouse relationships را sync می‌کند
- `get_context_data(**kwargs)`: unit formset را اضافه می‌کند

**URL**: `/inventory/items/create/`

---

### `ItemUpdateView`

**توضیح**: ویرایش کالا با unit formset

**Type**: `ItemUnitFormsetMixin, InventoryBaseView, UpdateView`

**Template**: `inventory/item_form.html`

**Form**: `ItemForm`

**Formset**: `ItemUnitFormSet`

**Success URL**: `inventory:items`

**متدها**:
- `form_valid(form)`: 
  - `edited_by` را تنظیم می‌کند
  - unit formset را ذخیره می‌کند
  - warehouse relationships را sync می‌کند
- `get_context_data(**kwargs)`: unit formset را اضافه می‌کند

**URL**: `/inventory/items/<pk>/edit/`

---

### `ItemDeleteView`

**توضیح**: حذف کالا

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/item_confirm_delete.html`

**Success URL**: `inventory:items`

**متدها**:
- `delete(request, *args, **kwargs)`: 
  - پیام موفقیت نمایش می‌دهد
  - `ProtectedError` را handle می‌کند (اگر کالا در استفاده باشد)

**URL**: `/inventory/items/<pk>/delete/`

---

## Warehouse Views

### `WarehouseListView`

**توضیح**: فهرست انبارها

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/warehouses.html`

**Context Variables**:
- `warehouses`: queryset انبارها (paginated)

**URL**: `/inventory/warehouses/`

---

### `WarehouseCreateView`

**توضیح**: ایجاد انبار جدید

**Type**: `InventoryBaseView, CreateView`

**Template**: `inventory/warehouse_form.html`

**Form**: `WarehouseForm`

**Success URL**: `inventory:warehouses`

**متدها**:
- `form_valid(form)`: `company_id` و `created_by` را تنظیم می‌کند

**URL**: `/inventory/warehouses/create/`

---

### `WarehouseUpdateView`

**توضیح**: ویرایش انبار

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/warehouse_form.html`

**Form**: `WarehouseForm`

**Success URL**: `inventory:warehouses`

**متدها**:
- `form_valid(form)`: `edited_by` را تنظیم می‌کند

**URL**: `/inventory/warehouses/<pk>/edit/`

---

### `WarehouseDeleteView`

**توضیح**: حذف انبار

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/warehouse_confirm_delete.html`

**Success URL**: `inventory:warehouses`

**متدها**:
- `delete(request, *args, **kwargs)`: 
  - پیام موفقیت نمایش می‌دهد
  - `ProtectedError` را handle می‌کند

**URL**: `/inventory/warehouses/<pk>/delete/`

---

## Supplier Views

### `SupplierListView`

**توضیح**: فهرست تامین‌کنندگان

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/suppliers.html`

**Context Variables**:
- `suppliers`: queryset تامین‌کنندگان (paginated)

**URL**: `/inventory/suppliers/`

---

### `SupplierCreateView`

**توضیح**: ایجاد تامین‌کننده جدید

**Type**: `InventoryBaseView, CreateView`

**Template**: `inventory/supplier_form.html`

**Form**: `SupplierForm`

**Success URL**: `inventory:suppliers`

**متدها**:
- `form_valid(form)`: `company_id` و `created_by` را تنظیم می‌کند

**URL**: `/inventory/suppliers/create/`

---

### `SupplierUpdateView`

**توضیح**: ویرایش تامین‌کننده

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/supplier_form.html`

**Form**: `SupplierForm`

**Success URL**: `inventory:suppliers`

**متدها**:
- `form_valid(form)`: `edited_by` را تنظیم می‌کند

**URL**: `/inventory/suppliers/<pk>/edit/`

---

### `SupplierDeleteView`

**توضیح**: حذف تامین‌کننده

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/supplier_confirm_delete.html`

**Success URL**: `inventory:suppliers`

**متدها**:
- `delete(request, *args, **kwargs)`: پیام موفقیت نمایش می‌دهد

**URL**: `/inventory/suppliers/<pk>/delete/`

---

## Supplier Category Views

### `SupplierCategoryListView`

**توضیح**: فهرست دسته‌های تامین‌کنندگان

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/supplier_categories.html`

**Context Variables**:
- `supplier_categories`: queryset دسته‌های تامین‌کنندگان (paginated)

**URL**: `/inventory/supplier-categories/`

---

### `SupplierCategoryCreateView`

**توضیح**: ایجاد دسته تامین‌کننده جدید

**Type**: `InventoryBaseView, CreateView`

**Template**: `inventory/suppliercategory_form.html`

**Form**: `SupplierCategoryForm`

**Success URL**: `inventory:supplier_categories`

**متدها**:
- `form_valid(form)`: `company_id` و `created_by` را تنظیم می‌کند

**URL**: `/inventory/supplier-categories/create/`

---

### `SupplierCategoryUpdateView`

**توضیح**: ویرایش دسته تامین‌کننده

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/suppliercategory_form.html`

**Form**: `SupplierCategoryForm`

**Success URL**: `inventory:supplier_categories`

**متدها**:
- `form_valid(form)`: `edited_by` را تنظیم می‌کند

**URL**: `/inventory/supplier-categories/<pk>/edit/`

---

### `SupplierCategoryDeleteView`

**توضیح**: حذف دسته تامین‌کننده

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/suppliercategory_confirm_delete.html`

**Success URL**: `inventory:supplier_categories`

**متدها**:
- `delete(request, *args, **kwargs)`: پیام موفقیت نمایش می‌دهد

**URL**: `/inventory/supplier-categories/<pk>/delete/`

---

## الگوهای مشترک

تمام views از الگوهای مشترک زیر پیروی می‌کنند:

1. **Company Filtering**: به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
2. **Pagination**: List views از `paginate_by = 50` استفاده می‌کنند
3. **Success Messages**: تمام create/update/delete operations پیام موفقیت نمایش می‌دهند
4. **Audit Fields**: `created_by`, `edited_by` به صورت خودکار تنظیم می‌شوند
5. **Error Handling**: Delete views `ProtectedError` را handle می‌کنند

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`, `ItemUnitFormsetMixin`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `inventory.models`: تمام مدل‌های master data
- `inventory.forms`: تمام form classes

---

## استفاده در پروژه

این views در URLs ماژول inventory ثبت شده‌اند و از طریق sidebar navigation قابل دسترسی هستند.

---

## نکات مهم

1. **Item Views**: از `ItemUnitFormsetMixin` برای مدیریت واحدهای کالا استفاده می‌کنند
2. **Warehouse Sync**: Item views warehouse relationships را به صورت خودکار sync می‌کنند
3. **Protected Deletion**: Delete views بررسی می‌کنند که آیا رکورد در استفاده است یا نه

