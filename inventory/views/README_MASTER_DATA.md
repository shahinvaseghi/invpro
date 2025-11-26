# inventory/views/master_data.py - Master Data Views (Complete Documentation)

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

**Attributes**:
- `model`: `models.ItemType`
- `template_name`: `'inventory/item_types.html'`
- `context_object_name`: `'item_types'`
- `paginate_by`: `50`

**Context Variables**:
- `item_types`: queryset انواع کالا (paginated)
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:
- هیچ متد سفارشی ندارد (از متدهای پیش‌فرض `ListView` و `InventoryBaseView` استفاده می‌کند)
  - `get_queryset()`: از `InventoryBaseView` - queryset را بر اساس `active_company_id` فیلتر می‌کند

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
3. پیام موفقیت را با `messages.success(self.request, _('Item Type created successfully.'))` نمایش می‌دهد
4. `super().form_valid(form)` را فراخوانی می‌کند که فرم را ذخیره می‌کند و redirect می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: `form_title` را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('Create Item Type')` اضافه شده

**Context Variables اضافه شده**:
- `form_title`: `_('Create Item Type')`
- `form`: instance فرم `ItemTypeForm`
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**URL**: `/inventory/item-types/create/`

---

### `ItemTypeUpdateView`

**توضیح**: ویرایش نوع کالا

**Type**: `InventoryBaseView, UpdateView`

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

**توضیح**: قبل از ذخیره، `edited_by` را تنظیم می‌کند و پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `ItemTypeForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.edited_by` را به `request.user` تنظیم می‌کند
2. پیام موفقیت را با `messages.success(self.request, _('Item Type updated successfully.'))` نمایش می‌دهد
3. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: `form_title` را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('Edit Item Type')` اضافه شده

**Context Variables اضافه شده**:
- `form_title`: `_('Edit Item Type')`
- `form`: instance فرم `ItemTypeForm`
- `object`: instance نوع کالا برای ویرایش
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**URL**: `/inventory/item-types/<pk>/edit/`

---

### `ItemTypeDeleteView`

**توضیح**: حذف نوع کالا

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/itemtype_confirm_delete.html`

**Success URL**: `inventory:item_types`

**Attributes**:
- `model`: `models.ItemType`
- `template_name`: `'inventory/itemtype_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:item_types')`

**متدها**:

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: بعد از حذف، پیام موفقیت نمایش می‌دهد.

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. پیام موفقیت را با `messages.success(self.request, _('Item Type deleted successfully.'))` نمایش می‌دهد
2. `super().delete(request, *args, **kwargs)` را فراخوانی می‌کند که object را حذف می‌کند و redirect می‌کند

**URL**: `/inventory/item-types/<pk>/delete/`

---

## Item Category Views

### `ItemCategoryListView`

**توضیح**: فهرست دسته‌های کالا

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/item_categories.html`

**Attributes**:
- `model`: `models.ItemCategory`
- `template_name`: `'inventory/item_categories.html'`
- `context_object_name`: `'item_categories'`
- `paginate_by`: `50`

**Context Variables**:
- `item_categories`: queryset دسته‌های کالا (paginated)
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:
- هیچ متد سفارشی ندارد

**URL**: `/inventory/item-categories/`

---

### `ItemCategoryCreateView`

**توضیح**: ایجاد دسته کالای جدید

**Type**: `InventoryBaseView, CreateView`

**Template**: `inventory/itemcategory_form.html`

**Form**: `ItemCategoryForm`

**Success URL**: `inventory:item_categories`

**Attributes**:
- `model`: `models.ItemCategory`
- `form_class`: `forms.ItemCategoryForm`
- `template_name`: `'inventory/itemcategory_form.html'`
- `success_url`: `reverse_lazy('inventory:item_categories')`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم معتبر `ItemCategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.company_id` را از `request.session.get('active_company_id')` تنظیم می‌کند
2. `form.instance.created_by` را به `request.user` تنظیم می‌کند
3. پیام موفقیت را نمایش می‌دهد
4. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('Create Item Category')` اضافه شده

**URL**: `/inventory/item-categories/create/`

---

### `ItemCategoryUpdateView`

**توضیح**: ویرایش دسته کالا

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/itemcategory_form.html`

**Form**: `ItemCategoryForm`

**Success URL**: `inventory:item_categories`

**Attributes**:
- `model`: `models.ItemCategory`
- `form_class`: `forms.ItemCategoryForm`
- `template_name`: `'inventory/itemcategory_form.html'`
- `success_url`: `reverse_lazy('inventory:item_categories')`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم معتبر `ItemCategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.edited_by` را به `request.user` تنظیم می‌کند
2. پیام موفقیت را نمایش می‌دهد
3. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('Edit Item Category')` اضافه شده

**URL**: `/inventory/item-categories/<pk>/edit/`

---

### `ItemCategoryDeleteView`

**توضیح**: حذف دسته کالا

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/itemcategory_confirm_delete.html`

**Success URL**: `inventory:item_categories`

**Attributes**:
- `model`: `models.ItemCategory`
- `template_name`: `'inventory/itemcategory_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:item_categories')`

**متدها**:

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. پیام موفقیت را نمایش می‌دهد
2. `super().delete(request, *args, **kwargs)` را فراخوانی می‌کند

**URL**: `/inventory/item-categories/<pk>/delete/`

---

## Item Subcategory Views

### `ItemSubcategoryListView`

**توضیح**: فهرست زیردسته‌های کالا

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/item_subcategories.html`

**Attributes**:
- `model`: `models.ItemSubcategory`
- `template_name`: `'inventory/item_subcategories.html'`
- `context_object_name`: `'item_subcategories'`
- `paginate_by`: `50`

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

**Attributes**:
- `model`: `models.ItemSubcategory`
- `form_class`: `forms.ItemSubcategoryForm`
- `template_name`: `'inventory/itemsubcategory_form.html'`
- `success_url`: `reverse_lazy('inventory:item_subcategories')`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم معتبر `ItemSubcategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.company_id` را از `request.session.get('active_company_id')` تنظیم می‌کند
2. `form.instance.created_by` را به `request.user` تنظیم می‌کند
3. پیام موفقیت را نمایش می‌دهد
4. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('Create Item Subcategory')` اضافه شده

**URL**: `/inventory/item-subcategories/create/`

---

### `ItemSubcategoryUpdateView`

**توضیح**: ویرایش زیردسته کالا

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/itemsubcategory_form.html`

**Form**: `ItemSubcategoryForm`

**Success URL**: `inventory:item_subcategories`

**Attributes**:
- `model`: `models.ItemSubcategory`
- `form_class`: `forms.ItemSubcategoryForm`
- `template_name`: `'inventory/itemsubcategory_form.html'`
- `success_url`: `reverse_lazy('inventory:item_subcategories')`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم معتبر `ItemSubcategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.edited_by` را به `request.user` تنظیم می‌کند
2. پیام موفقیت را نمایش می‌دهد
3. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('Edit Item Subcategory')` اضافه شده

**URL**: `/inventory/item-subcategories/<pk>/edit/`

---

### `ItemSubcategoryDeleteView`

**توضیح**: حذف زیردسته کالا

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/itemsubcategory_confirm_delete.html`

**Success URL**: `inventory:item_subcategories`

**Attributes**:
- `model`: `models.ItemSubcategory`
- `template_name`: `'inventory/itemsubcategory_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:item_subcategories')`

**متدها**:

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. پیام موفقیت را نمایش می‌دهد
2. `super().delete(request, *args, **kwargs)` را فراخوانی می‌کند

**URL**: `/inventory/item-subcategories/<pk>/delete/`

---

## Item Views

### `ItemListView`

**توضیح**: فهرست کالاها با فیلترهای پیشرفته

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/items.html`

**Attributes**:
- `model`: `models.Item`
- `template_name`: `'inventory/items.html'`
- `context_object_name`: `'items'`
- `paginate_by`: `50`

**Context Variables**:
- `items`: queryset کالاها (paginated)
- `item_types`: لیست انواع کالا برای فیلتر dropdown
- `item_categories`: لیست دسته‌های کالا برای فیلتر dropdown
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با فیلترها و جستجو برمی‌گرداند، مرتب شده بر اساس جدیدترین.

**پارامترهای ورودی**: ندارد (از `self.request` استفاده می‌کند)

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده و مرتب شده

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند (از `InventoryBaseView` - فیلتر شده بر اساس company)
2. `select_related('type', 'category', 'subcategory')` را برای بهینه‌سازی query اعمال می‌کند
3. جستجو در `item_code`, `name`, `name_en` را انجام می‌دهد (از query parameter `search`)
4. فیلتر بر اساس `type_id` (از query parameter `type`)
5. فیلتر بر اساس `category_id` (از query parameter `category`)
6. فیلتر بر اساس `is_enabled` (از query parameter `status`: '1' یا '0')
7. مرتب می‌کند بر اساس `-created_at, -id` (جدیدترین اول)

**Query Parameters**:
- `search`: جستجو در کد و نام کالا
- `type`: فیلتر بر اساس نوع کالا
- `category`: فیلتر بر اساس دسته کالا
- `status`: فیلتر بر اساس وضعیت ('1' برای فعال، '0' برای غیرفعال)

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: فیلترهای context را برای template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `item_types` و `item_categories` اضافه شده

**Context Variables اضافه شده**:
- `item_types`: queryset انواع کالا (فیلتر شده بر اساس company و `is_enabled=1`، مرتب شده بر اساس `name`)
- `item_categories`: queryset دسته‌های کالا (فیلتر شده بر اساس company و `is_enabled=1`، مرتب شده بر اساس `name`)

**URL**: `/inventory/items/`

---

### `ItemSerialListView`

**توضیح**: فهرست سریال‌های کالا

**Type**: `FeaturePermissionRequiredMixin, InventoryBaseView, ListView`

**Template**: `inventory/item_serials.html`

**Attributes**:
- `feature_code`: `'inventory.master.item_serials'`
- `model`: `models.ItemSerial`
- `template_name`: `'inventory/item_serials.html'`
- `context_object_name`: `'serials'`
- `paginate_by`: `100`

**Permission**: نیاز به `inventory.master.item_serials` permission

**Context Variables**:
- `serials`: queryset سریال‌ها (paginated)
- `receipt_code`: کد رسید برای فیلتر (از query parameter)
- `item_code`: کد کالا برای فیلتر (از query parameter)
- `serial_code`: کد سریال برای فیلتر (از query parameter)
- `status`: وضعیت سریال برای فیلتر (از query parameter)
- `status_choices`: لیست انتخاب‌های وضعیت (`ItemSerial.Status.choices`)
- `has_filters`: `bool` - آیا فیلتری اعمال شده است یا نه

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را با فیلترها و جستجو برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**منطق**:
1. queryset را از `super().get_queryset()` دریافت می‌کند
2. `select_related('item', 'receipt_document', 'current_warehouse')` را برای بهینه‌سازی query اعمال می‌کند
3. فیلتر بر اساس `receipt_document_code` (از query parameter `receipt_code`)
4. فیلتر بر اساس `item__item_code` (از query parameter `item_code`)
5. فیلتر بر اساس `serial_code` (از query parameter `serial_code`)
6. فیلتر بر اساس `current_status` (از query parameter `status`)
7. مرتب می‌کند بر اساس `-created_at, -id`

**Query Parameters**:
- `receipt_code`: فیلتر بر اساس کد رسید
- `item_code`: فیلتر بر اساس کد کالا
- `serial_code`: فیلتر بر اساس کد سریال
- `status`: فیلتر بر اساس وضعیت

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: فیلترهای جستجو را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با فیلترها و `status_choices` اضافه شده

**Context Variables اضافه شده**:
- `receipt_code`: مقدار فیلتر کد رسید
- `item_code`: مقدار فیلتر کد کالا
- `serial_code`: مقدار فیلتر کد سریال
- `status`: مقدار فیلتر وضعیت
- `status_choices`: `models.ItemSerial.Status.choices`
- `has_filters`: `bool` - آیا حداقل یک فیلتر اعمال شده است

**URL**: `/inventory/item-serials/`

---

### `ItemCreateView`

**توضیح**: ایجاد کالای جدید با unit formset

**Type**: `ItemUnitFormsetMixin, InventoryBaseView, CreateView`

**Template**: `inventory/item_form.html`

**Form**: `ItemForm`

**Formset**: `ItemUnitFormSet` (از `ItemUnitFormsetMixin`)

**Success URL**: `inventory:items`

**Attributes**:
- `model`: `models.Item`
- `form_class`: `forms.ItemForm`
- `template_name`: `'inventory/item_form.html'`
- `success_url`: `reverse_lazy('inventory:items')`

**Context Variables**:
- `form`: instance فرم `ItemForm`
- `units_formset`: instance formset `ItemUnitFormSet` (از `ItemUnitFormsetMixin`)
- `form_title`: `_('تعریف کالای جدید')`
- `active_module`: `'inventory'` (از `InventoryBaseView`)

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

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: کالا و unit formset را ذخیره می‌کند و warehouse relationships را sync می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `ItemForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `company_id` را از session دریافت می‌کند
2. `form.instance.company_id`, `created_by`, `edited_by` را تنظیم می‌کند
3. یک instance موقت برای build کردن formset ایجاد می‌کند
4. formset را با `build_unit_formset()` می‌سازد
5. بررسی می‌کند که آیا formset داده دارد یا نه
6. اگر formset داده دارد، آن را validate می‌کند
7. مقادیر checkbox fields (`is_sellable`, `has_lot_tracking`, `requires_temporary_receipt`, `is_enabled`) را به صورت صریح تنظیم می‌کند (0 یا 1)
8. کالا را ذخیره می‌کند
9. اگر formset معتبر است، آن را ذخیره می‌کند
10. warehouse relationships را با `_sync_item_warehouses()` sync می‌کند
11. پیام موفقیت را نمایش می‌دهد
12. redirect می‌کند

**نکات مهم**:
- Checkbox fields به صورت صریح به 0 یا 1 تبدیل می‌شوند
- Unit formset اختیاری است (اگر داده نداشته باشد، validate نمی‌شود)
- Warehouse relationships به صورت خودکار sync می‌شوند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: unit formset را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `units_formset` و `form_title` اضافه شده

**Context Variables اضافه شده**:
- `form_title`: `_('تعریف کالای جدید')`
- `units_formset`: instance formset `ItemUnitFormSet` (از `ItemUnitFormsetMixin.get_context_data()`)

**URL**: `/inventory/items/create/`

---

### `ItemUpdateView`

**توضیح**: ویرایش کالا با unit formset

**Type**: `ItemUnitFormsetMixin, InventoryBaseView, UpdateView`

**Template**: `inventory/item_form.html`

**Form**: `ItemForm`

**Formset**: `ItemUnitFormSet` (از `ItemUnitFormsetMixin`)

**Success URL**: `inventory:items`

**Attributes**:
- `model`: `models.Item`
- `form_class`: `forms.ItemForm`
- `template_name`: `'inventory/item_form.html'`
- `success_url`: `reverse_lazy('inventory:items')`

**Context Variables**:
- `form`: instance فرم `ItemForm`
- `units_formset`: instance formset `ItemUnitFormSet`
- `form_title`: `_('ویرایش کالا')`
- `object`: instance کالا برای ویرایش
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` اضافه شده

**منطق**:
1. kwargs را از `super().get_form_kwargs()` دریافت می‌کند
2. `instance` را از kwargs می‌خواند
3. `company_id` را از `instance.company_id` یا `request.session.get('active_company_id')` دریافت می‌کند
4. kwargs را با `company_id` برمی‌گرداند

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: کالا و unit formset را ذخیره می‌کند و warehouse relationships را sync می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `ItemForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `company_id` را از `form.instance.company_id` دریافت می‌کند
2. formset را با `build_unit_formset()` می‌سازد
3. اگر formset معتبر نیست، response با form و formset برمی‌گرداند
4. `form.instance.edited_by` را تنظیم می‌کند
5. مقادیر checkbox fields را به صورت صریح تنظیم می‌کند
6. کالا را ذخیره می‌کند
7. formset را ذخیره می‌کند
8. warehouse relationships را sync می‌کند
9. پیام موفقیت را نمایش می‌دهد
10. redirect می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: unit formset را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `units_formset` و `form_title` اضافه شده

**Context Variables اضافه شده**:
- `form_title`: `_('ویرایش کالا')`
- `units_formset`: instance formset `ItemUnitFormSet`

**URL**: `/inventory/items/<pk>/edit/`

---

### `ItemDeleteView`

**توضیح**: حذف کالا با handling خطای ProtectedError

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/item_confirm_delete.html`

**Success URL**: `inventory:items`

**Attributes**:
- `model`: `models.Item`
- `template_name`: `'inventory/item_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:items')`

**Context Variables**:
- `object`: instance کالا برای حذف
- `model_verbose_name`: نام verbose مدل (`Item._meta.verbose_name`)
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: `model_verbose_name` را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `model_verbose_name` اضافه شده

**Context Variables اضافه شده**:
- `model_verbose_name`: `self.model._meta.verbose_name`

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: حذف را با handling خطای ProtectedError انجام می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم (در DeleteView استفاده نمی‌شود اما signature لازم است)

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. اطلاعات کالا را log می‌کند
2. سعی می‌کند کالا را حذف کند
3. اگر موفق شد:
   - پیام موفقیت را نمایش می‌دهد
   - redirect می‌کند
4. اگر `ProtectedError` رخ داد:
   - خطا را log می‌کند
   - نام مدل‌های protected را استخراج می‌کند
   - پیام خطای user-friendly می‌سازد (فارسی)
   - پیام خطا را نمایش می‌دهد
   - redirect می‌کند

**Error Handling**:
- `ProtectedError`: اگر کالا در استفاده باشد (مثلاً در رسیدها یا حواله‌ها)، خطا catch می‌شود و پیام مناسب نمایش داده می‌شود

**URL**: `/inventory/items/<pk>/delete/`

---

## Warehouse Views

### `WarehouseListView`

**توضیح**: فهرست انبارها

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/warehouses.html`

**Attributes**:
- `model`: `models.Warehouse`
- `template_name`: `'inventory/warehouses.html'`
- `context_object_name`: `'warehouses'`
- `paginate_by`: `50`

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

**Attributes**:
- `model`: `models.Warehouse`
- `form_class`: `forms.WarehouseForm`
- `template_name`: `'inventory/warehouse_form.html'`
- `success_url`: `reverse_lazy('inventory:warehouses')`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم معتبر `WarehouseForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.company_id` را از `request.session.get('active_company_id')` تنظیم می‌کند
2. `form.instance.created_by` را به `request.user` تنظیم می‌کند
3. پیام موفقیت را نمایش می‌دهد
4. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('Create Warehouse')` اضافه شده

**URL**: `/inventory/warehouses/create/`

---

### `WarehouseUpdateView`

**توضیح**: ویرایش انبار

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/warehouse_form.html`

**Form**: `WarehouseForm`

**Success URL**: `inventory:warehouses`

**Attributes**:
- `model`: `models.Warehouse`
- `form_class`: `forms.WarehouseForm`
- `template_name`: `'inventory/warehouse_form.html'`
- `success_url`: `reverse_lazy('inventory:warehouses')`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم معتبر `WarehouseForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.edited_by` را به `request.user` تنظیم می‌کند
2. پیام موفقیت را نمایش می‌دهد
3. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('Edit Warehouse')` اضافه شده

**URL**: `/inventory/warehouses/<pk>/edit/`

---

### `WarehouseDeleteView`

**توضیح**: حذف انبار با handling خطای ProtectedError

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/warehouse_confirm_delete.html`

**Success URL**: `inventory:warehouses`

**Attributes**:
- `model`: `models.Warehouse`
- `template_name`: `'inventory/warehouse_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:warehouses')`

**Context Variables**:
- `object`: instance انبار برای حذف
- `model_verbose_name`: نام verbose مدل

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `model_verbose_name` اضافه شده

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. اطلاعات انبار را log می‌کند
2. سعی می‌کند انبار را حذف کند
3. اگر موفق شد:
   - پیام موفقیت را نمایش می‌دهد
   - redirect می‌کند
4. اگر `ProtectedError` رخ داد:
   - خطا را log می‌کند
   - نام مدل‌های protected را به فارسی map می‌کند
   - پیام خطای user-friendly می‌سازد
   - پیام خطا را نمایش می‌دهد
   - redirect می‌کند

**Error Handling**:
- `ProtectedError`: اگر انبار در استفاده باشد (مثلاً در رسیدها یا حواله‌ها)، خطا catch می‌شود

**URL**: `/inventory/warehouses/<pk>/delete/`

---

## Supplier Category Views

### `SupplierCategoryListView`

**توضیح**: فهرست دسته‌های تامین‌کنندگان

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/supplier_categories.html`

**Attributes**:
- `model`: `models.SupplierCategory`
- `template_name`: `'inventory/supplier_categories.html'`
- `context_object_name`: `'supplier_categories'`
- `paginate_by`: `50`

**URL**: `/inventory/supplier-categories/`

---

### `SupplierCategoryCreateView`

**توضیح**: ایجاد دسته تامین‌کننده جدید

**Type**: `InventoryBaseView, CreateView`

**Template**: `inventory/suppliercategory_form.html`

**Form**: `SupplierCategoryForm`

**Success URL**: `inventory:supplier_categories`

**Attributes**:
- `model`: `models.SupplierCategory`
- `form_class`: `forms.SupplierCategoryForm`
- `template_name`: `'inventory/suppliercategory_form.html'`
- `success_url`: `reverse_lazy('inventory:supplier_categories')`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` اضافه شده

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: دسته تامین‌کننده را ذخیره می‌کند و supplier links را sync می‌کند.

**پارامترهای ورودی**:
- `form`: فرم معتبر `SupplierCategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `company_id` را از session دریافت می‌کند
2. `form.instance.company_id`, `created_by`, `edited_by` را تنظیم می‌کند
3. کالا را ذخیره می‌کند
4. `_sync_supplier_links()` را فراخوانی می‌کند
5. پیام موفقیت را نمایش می‌دهد
6. redirect می‌کند

---

#### `_sync_supplier_links(self, form) -> None`

**توضیح**: روابط supplier-subcategory و supplier-item را sync می‌کند.

**پارامترهای ورودی**:
- `form`: فرم `SupplierCategoryForm`

**مقدار بازگشتی**: ندارد

**منطق**:
1. `supplier`, `company`, `category` را از `self.object` دریافت می‌کند
2. `subcategories` و `items` را از `form.cleaned_data` دریافت می‌کند
3. `SupplierSubcategory` های قدیمی را حذف می‌کند (که در انتخاب جدید نیستند)
4. `SupplierSubcategory` های جدید را ایجاد می‌کند
5. `SupplierItem` های قدیمی را حذف می‌کند
6. `SupplierItem` های جدید را ایجاد می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('ایجاد دسته‌بندی تأمین‌کننده')` اضافه شده

**URL**: `/inventory/supplier-categories/create/`

---

### `SupplierCategoryUpdateView`

**توضیح**: ویرایش دسته تامین‌کننده

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/suppliercategory_form.html`

**Form**: `SupplierCategoryForm`

**Success URL**: `inventory:supplier_categories`

**Attributes**:
- `model`: `models.SupplierCategory`
- `form_class`: `forms.SupplierCategoryForm`
- `template_name`: `'inventory/suppliercategory_form.html'`
- `success_url`: `reverse_lazy('inventory:supplier_categories')`

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` اضافه شده

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم معتبر `SupplierCategoryForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.edited_by` را تنظیم می‌کند
2. کالا را ذخیره می‌کند
3. `_sync_supplier_links()` را فراخوانی می‌کند
4. پیام موفقیت را نمایش می‌دهد
5. redirect می‌کند

---

#### `_sync_supplier_links(self, form) -> None`

**پارامترهای ورودی**:
- `form`: فرم `SupplierCategoryForm`

**مقدار بازگشتی**: ندارد

**منطق**: مشابه `SupplierCategoryCreateView._sync_supplier_links()`

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('ویرایش دسته‌بندی تأمین‌کننده')` اضافه شده

**URL**: `/inventory/supplier-categories/<pk>/edit/`

---

### `SupplierCategoryDeleteView`

**توضیح**: حذف دسته تامین‌کننده

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/suppliercategory_confirm_delete.html`

**Success URL**: `inventory:supplier_categories`

**Attributes**:
- `model`: `models.SupplierCategory`
- `template_name`: `'inventory/suppliercategory_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:supplier_categories')`

**متدها**:

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. پیام موفقیت را نمایش می‌دهد
2. `super().delete(request, *args, **kwargs)` را فراخوانی می‌کند

**URL**: `/inventory/supplier-categories/<pk>/delete/`

---

## Supplier Views

### `SupplierListView`

**توضیح**: فهرست تامین‌کنندگان

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/suppliers.html`

**Attributes**:
- `model`: `models.Supplier`
- `template_name`: `'inventory/suppliers.html'`
- `context_object_name`: `'suppliers'`
- `paginate_by`: `50`

**URL**: `/inventory/suppliers/`

---

### `SupplierCreateView`

**توضیح**: ایجاد تامین‌کننده جدید

**Type**: `InventoryBaseView, CreateView`

**Template**: `inventory/supplier_form.html`

**Form**: `SupplierForm`

**Success URL**: `inventory:suppliers`

**Attributes**:
- `model`: `models.Supplier`
- `form_class`: `forms.SupplierForm`
- `template_name`: `'inventory/supplier_form.html'`
- `success_url`: `reverse_lazy('inventory:suppliers')`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم معتبر `SupplierForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.company_id` را از session تنظیم می‌کند
2. `form.instance.created_by` و `edited_by` را به `request.user` تنظیم می‌کند
3. پیام موفقیت را نمایش می‌دهد
4. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('ایجاد تأمین‌کننده')` اضافه شده

**URL**: `/inventory/suppliers/create/`

---

### `SupplierUpdateView`

**توضیح**: ویرایش تامین‌کننده

**Type**: `InventoryBaseView, UpdateView`

**Template**: `inventory/supplier_form.html`

**Form**: `SupplierForm`

**Success URL**: `inventory:suppliers`

**Attributes**:
- `model`: `models.Supplier`
- `form_class`: `forms.SupplierForm`
- `template_name`: `'inventory/supplier_form.html'`
- `success_url`: `reverse_lazy('inventory:suppliers')`

**متدها**:

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم معتبر `SupplierForm`

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. `form.instance.edited_by` را به `request.user` تنظیم می‌کند
2. پیام موفقیت را نمایش می‌دهد
3. `super().form_valid(form)` را فراخوانی می‌کند

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `form_title = _('ویرایش تأمین‌کننده')` اضافه شده

**URL**: `/inventory/suppliers/<pk>/edit/`

---

### `SupplierDeleteView`

**توضیح**: حذف تامین‌کننده با handling خطای ProtectedError

**Type**: `InventoryBaseView, DeleteView`

**Template**: `inventory/supplier_confirm_delete.html`

**Success URL**: `inventory:suppliers`

**Attributes**:
- `model`: `models.Supplier`
- `template_name`: `'inventory/supplier_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:suppliers')`

**Context Variables**:
- `object`: instance تامین‌کننده برای حذف
- `model_verbose_name`: نام verbose مدل

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با `model_verbose_name` اضافه شده

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `form`: فرم

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. اطلاعات تامین‌کننده را log می‌کند
2. سعی می‌کند تامین‌کننده را حذف کند
3. اگر موفق شد:
   - پیام موفقیت را نمایش می‌دهد
   - redirect می‌کند
4. اگر `ProtectedError` رخ داد:
   - خطا را log می‌کند
   - نام مدل‌های protected را به فارسی map می‌کند
   - پیام خطای user-friendly می‌سازد
   - پیام خطا را نمایش می‌دهد
   - redirect می‌کند

**Error Handling**:
- `ProtectedError`: اگر تامین‌کننده در استفاده باشد (مثلاً در رسیدهای امانی)، خطا catch می‌شود

**URL**: `/inventory/suppliers/<pk>/delete/`

---

## وابستگی‌ها

- `inventory.views.base`: `InventoryBaseView`, `ItemUnitFormsetMixin`
- `shared.mixins`: `FeaturePermissionRequiredMixin`
- `inventory.models`: تمام مدل‌های master data
- `inventory.forms`: تمام form classes
- `django.contrib`: `messages`
- `django.db.models.deletion`: `ProtectedError`
- `django.views.generic`: `ListView`, `CreateView`, `UpdateView`, `DeleteView`
- `django.urls`: `reverse_lazy`
- `django.utils.translation`: `gettext_lazy as _`

---

## استفاده در پروژه

این views در URLs ماژول inventory ثبت شده‌اند و از طریق sidebar navigation قابل دسترسی هستند.

---

## نکات مهم

1. **Company Filtering**: تمام views به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
2. **Audit Fields**: `created_by`, `edited_by` به صورت خودکار تنظیم می‌شوند
3. **Protected Deletion**: Delete views برای Item, Warehouse, Supplier از `ProtectedError` handling استفاده می‌کنند
4. **Unit Formset**: Item views از `ItemUnitFormsetMixin` برای مدیریت واحدهای کالا استفاده می‌کنند
5. **Warehouse Sync**: Item views warehouse relationships را به صورت خودکار sync می‌کنند
6. **Supplier Links Sync**: SupplierCategory views روابط supplier-subcategory و supplier-item را sync می‌کنند

