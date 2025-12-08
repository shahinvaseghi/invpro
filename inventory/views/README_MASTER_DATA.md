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

**Template**: `inventory/item_types.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `models.ItemType`
- `template_name`: `'inventory/item_types.html'`
- `context_object_name`: `'object_list'` (برای consistency با generic template)
- `paginate_by`: `50`

**Context Variables**:
- `object_list`: queryset انواع کالا (paginated)
- `page_title`: `_('Item Types')`
- `breadcrumbs`: لیست breadcrumb items
- `create_url`: URL برای ایجاد Item Type جدید
- `create_button_text`: `_('Create Item Type')`
- `table_headers`: [] (overridden in template)
- `show_actions`: `True`
- `edit_url_name`: `'inventory:itemtype_edit'`
- `delete_url_name`: `'inventory:itemtype_delete'`
- `empty_state_title`: `_('No Item Types Found')`
- `empty_state_message`: `_('Start by creating your first item type.')`
- `empty_state_icon`: `'🏷️'`
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template اضافه می‌کند.

**Context Variables اضافه شده**: تمام متغیرهای ذکر شده در بالا

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

**توضیح**: context variables را برای generic form template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با متغیرهای لازم برای generic template

**Context Variables اضافه شده**:
- `form_title`: `_('Create Item Type')`
- `breadcrumbs`: لیست breadcrumb items (Inventory > Master Data > Item Types > Create)
- `cancel_url`: URL برای لغو (redirect به list)
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

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.master.item_types'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

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

**توضیح**: context variables را برای generic form template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با متغیرهای لازم برای generic template

**Context Variables اضافه شده**:
- `form_title`: `_('Edit Item Type')`
- `breadcrumbs`: لیست breadcrumb items (Inventory > Master Data > Item Types > Edit)
- `cancel_url`: URL برای لغو (redirect به list)
- `form`: instance فرم `ItemTypeForm`
- `object`: instance نوع کالا برای ویرایش
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**URL**: `/inventory/item-types/<pk>/edit/`

---

### `ItemTypeDeleteView`

**توضیح**: حذف نوع کالا

**Type**: `InventoryBaseView, DeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:item_types`

**Attributes**:
- `model`: `models.ItemType`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:item_types')`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: حذف را با مدیریت ProtectedError انجام می‌دهد.

**منطق**:
1. سعی می‌کند object را حذف کند
2. اگر موفق شد، پیام موفقیت نمایش می‌دهد
3. اگر ProtectedError رخ دهد، پیام خطای فارسی با جزئیات نمایش می‌دهد

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با متغیرهای لازم برای generic template

**Context Variables اضافه شده**:
- `delete_title`: `_('Delete Item Type')`
- `confirmation_message`: `_('Are you sure you want to delete this item type?')`
- `object_details`: لیست جزئیات object (Code, Name, Name EN)
- `cancel_url`: URL برای لغو (redirect به list)
- `breadcrumbs`: لیست breadcrumb items (Inventory > Master Data > Item Types > Delete)
- `object`: instance نوع کالا برای حذف
- `active_module`: `'inventory'` (از `InventoryBaseView`)

---

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: حذف را با مدیریت `ProtectedError` انجام می‌دهد.

**پارامترهای ورودی**:
- `form`: فرم معتبر `DeleteView` form

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. سعی می‌کند object را حذف کند
2. در صورت موفقیت، پیام موفقیت را نمایش می‌دهد و redirect می‌کند
3. در صورت `ProtectedError` (وقتی که object در جای دیگری استفاده شده):
   - مدل‌های محافظت شده را شناسایی می‌کند
   - نام‌های مدل را به فارسی تبدیل می‌کند
   - پیام خطای کاربرپسند نمایش می‌دهد: "نمی‌توان این نوع کالا را حذف کرد چون در ساختار {models} استفاده شده است."
   - به صفحه لیست redirect می‌کند

**URL**: `/inventory/item-types/<pk>/delete/`

---

## Item Category Views

### `ItemCategoryListView`

**توضیح**: فهرست دسته‌های کالا

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/item_categories.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `models.ItemCategory`
- `template_name`: `'inventory/item_categories.html'`
- `context_object_name`: `'object_list'` (برای consistency با generic template)
- `paginate_by`: `50`

**Context Variables**:
- `object_list`: queryset دسته‌های کالا (paginated)
- `page_title`: `_('Item Categories')`
- `breadcrumbs`: لیست breadcrumb items
- `create_url`: URL برای ایجاد Item Category جدید
- `create_button_text`: `_('Create Item Category')`
- `table_headers`: [] (overridden in template)
- `show_actions`: `True`
- `edit_url_name`: `'inventory:itemcategory_edit'`
- `delete_url_name`: `'inventory:itemcategory_delete'`
- `empty_state_title`: `_('No Item Categories Found')`
- `empty_state_message`: `_('Start by creating your first item category.')`
- `empty_state_icon`: `'📦'`
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template اضافه می‌کند.

**Context Variables اضافه شده**: تمام متغیرهای ذکر شده در بالا

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

**توضیح**: context variables را برای generic form template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با متغیرهای لازم برای generic template

**Context Variables اضافه شده**:
- `form_title`: `_('Create Item Category')`
- `breadcrumbs`: لیست breadcrumb items (Inventory > Master Data > Item Categories > Create)
- `cancel_url`: URL برای لغو (redirect به list)
- `form`: instance فرم `ItemCategoryForm`
- `active_module`: `'inventory'` (از `InventoryBaseView`)

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

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.master.item_categories'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

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

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:item_categories`

**Attributes**:
- `model`: `models.ItemCategory`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:item_categories')`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند و `item_type` را select_related می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions با select_related('item_type')

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: حذف را با مدیریت `ProtectedError` انجام می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. سعی می‌کند object را حذف کند
2. در صورت موفقیت، پیام موفقیت را نمایش می‌دهد و redirect می‌کند
3. در صورت `ProtectedError` (وقتی که object در جای دیگری استفاده شده):
   - مدل‌های محافظت شده را شناسایی می‌کند
   - پیام خطای کاربرپسند نمایش می‌دهد: "Cannot delete this item category because it is used in {models}."
   - به صفحه لیست redirect می‌کند

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با متغیرهای لازم برای generic template

**Context Variables اضافه شده**:
- `delete_title`: `_('Delete Item Category')`
- `confirmation_message`: `_('Are you sure you want to delete this item category?')`
- `object_details`: لیست جزئیات object (Code, Name, Name EN, Item Type)
- `cancel_url`: URL برای لغو (redirect به list)
- `breadcrumbs`: لیست breadcrumb items (Inventory > Master Data > Item Categories > Delete)

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
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_select_related(self) -> List[str]`

**توضیح**: لیست فیلدهای related را برای select_related برمی‌گرداند.

**مقدار بازگشتی**:
- `List[str]`: لیست فیلدهای related (`['category']`)

**منطق**:
- `category` را برای بهینه‌سازی query با select_related اضافه می‌کند

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

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.master.item_subcategories'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

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

**Type**: `InventoryBaseView, BaseDeleteView`

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:item_subcategories`

**Attributes**:
- `model`: `models.ItemSubcategory`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:item_subcategories')`
- `feature_code`: `'inventory.master.item_subcategories'`
- `success_message`: `_('زیردسته کالا با موفقیت حذف شد.')`
- `owner_field`: `'created_by'`

**متدها**:

#### `dispatch(self, request, *args, **kwargs) -> HttpResponse`

**توضیح**: بررسی permissions قبل از اجازه دادن به حذف.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponse`: response از `super().dispatch()` یا `PermissionDenied` exception

**منطق**:
1. اگر کاربر superuser باشد، اجازه می‌دهد و `super().dispatch()` را فراخوانی می‌کند
2. object را با `self.get_object()` دریافت می‌کند
3. `company_id` را از session دریافت می‌کند
4. permissions کاربر را با `get_user_feature_permissions()` دریافت می‌کند
5. بررسی می‌کند که آیا کاربر owner است یا نه (`obj.created_by == request.user`)
6. بررسی می‌کند که آیا کاربر `delete_own` permission دارد (اگر owner است) یا `delete_other` permission دارد (اگر owner نیست)
7. اگر permission نداشته باشد، `PermissionDenied` exception می‌اندازد با پیام مناسب:
   - اگر owner است اما `delete_own` ندارد: "شما اجازه حذف اسناد خود را ندارید."
   - اگر owner نیست اما `delete_other` ندارد: "شما اجازه حذف اسناد سایر کاربران را ندارید."
8. اگر permission داشته باشد، `super().dispatch()` را فراخوانی می‌کند

**نکته**: این متد permission checking را قبل از `delete()` انجام می‌دهد تا اطمینان حاصل شود که کاربر فقط می‌تواند اسناد خود را حذف کند (اگر `delete_own` دارد) یا اسناد سایر کاربران را (اگر `delete_other` دارد).

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**Context Variables برای Generic Template**:
- `delete_title`: `_('Delete Item Subcategory')`
- `confirmation_message`: `_('Do you really want to delete this item subcategory?')`
- `object_details`: لیست جزئیات subcategory (Name, Category, Item Type)
- `cancel_url`: `reverse_lazy('inventory:item_subcategories')`
- `breadcrumbs`: لیست breadcrumbs برای navigation

---

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: حذف را با مدیریت `ProtectedError` انجام می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. اطلاعات subcategory را log می‌کند
2. سعی می‌کند object را حذف کند
3. اگر موفق شد:
   - پیام موفقیت را نمایش می‌دهد: "زیردسته کالا با موفقیت حذف شد."
   - redirect می‌کند
4. اگر `ProtectedError` رخ داد:
   - خطا را log می‌کند
   - مدل‌های محافظت شده را شناسایی می‌کند
   - نام‌های مدل را به فارسی map می‌کند (Item -> کالا، Items -> کالاها)
   - پیام خطای کاربرپسند می‌سازد: "نمی‌توان این زیر دسته‌بندی کالا را حذف کرد چون در ساختار {models} استفاده شده است."
   - پیام خطا را نمایش می‌دهد
   - redirect می‌کند

**URL**: `/inventory/item-subcategories/<pk>/delete/`

---

## Item Views

### `ItemListView`

**توضیح**: فهرست کالاها با فیلترهای پیشرفته

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/items.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/items.html` extends `shared/generic/generic_list.html`
  - Overrides: `page_title`, `breadcrumb_extra`, `page_actions`, `filter_fields`, `table_headers`, `table_rows`, `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `models.Item`
- `template_name`: `'inventory/items.html'`
- `context_object_name`: `'object_list'`
- `paginate_by`: `50`

**Context Variables برای Generic Template**:
- `object_list`: queryset کالاها (paginated)
- `page_title`: `_('Items')`
- `breadcrumbs`: لیست breadcrumb items
- `create_url`: URL برای ایجاد Item جدید
- `create_button_text`: `_('Create Item')`
- `show_filters`: `True`
- `show_actions`: `True`
- `edit_url_name`: `'inventory:item_edit'`
- `delete_url_name`: `'inventory:item_delete'`
- `empty_state_title`: `_('No Items Found')`
- `empty_state_message`: `_('Start by creating your first item.')`
- `empty_state_icon`: `'📦'`

**Context Variables برای Item-Specific Features**:
- `item_types`: لیست انواع کالا برای فیلتر dropdown
- `item_categories`: لیست دسته‌های کالا برای فیلتر dropdown
- `status_filter`: مقدار فعلی فیلتر status
- `user_feature_permissions`: permissions کاربر برای conditional rendering
- `extra_filter_fields`: فیلدهای اضافی فیلتر (Item Type, Category)

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

**توضیح**: context variables را برای generic list template آماده می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با تمام متغیرهای لازم برای generic template

**Context Variables اضافه شده**: تمام متغیرهای ذکر شده در بالا (Generic Template و Item-Specific Features)، شامل:
- `item_types`: queryset انواع کالا (فیلتر شده بر اساس company و `is_enabled=1`، مرتب شده بر اساس `name`)
- `item_categories`: queryset دسته‌های کالا (فیلتر شده بر اساس company و `is_enabled=1`، مرتب شده بر اساس `name`)
- `user_feature_permissions`: از `get_user_feature_permissions(request.user, company_id)` برای conditional rendering

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

**Template**: `inventory/item_form.html` (extends `shared/generic/generic_form.html`)

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
- `form_title`: `_('Create New Item')`
- `breadcrumbs`: لیست breadcrumb items (Inventory > Master Data > Items > Create)
- `cancel_url`: URL برای لغو (redirect به list)
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_form_kwargs(self) -> Dict[str, Any]`

**توضیح**: `company_id` را به form پاس می‌دهد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: kwargs با `company_id` اضافه شده

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic form template اضافه می‌کند و unit formset را build می‌کند.

**Context Variables اضافه شده**: تمام متغیرهای ذکر شده در بالا، شامل `units_formset`

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
4. formset را با `build_unit_formset()` می‌سازد (از `ItemUnitFormsetMixin`)
5. بررسی می‌کند که آیا formset داده دارد یا نه (با چک کردن فیلدهای visible در POST)
6. اگر formset داده دارد، آن را validate می‌کند
7. اگر formset معتبر نباشد، response با form و formset برمی‌گرداند
8. مقادیر checkbox fields (`is_sellable`, `has_lot_tracking`, `requires_temporary_receipt`, `is_enabled`) را به صورت صریح تنظیم می‌کند (0 یا 1)
   - ابتدا از `form.cleaned_data` می‌خواند
   - اگر موجود نبود، از `request.POST` می‌خواند
   - مقدار را به 0 یا 1 تبدیل می‌کند
9. کالا را ذخیره می‌کند
10. اگر formset داده دارد، آن را دوباره با instance ذخیره شده build می‌کند و ذخیره می‌کند (با `_save_unit_formset()`)
11. warehouse relationships را با `_get_ordered_warehouses()` و `_sync_item_warehouses()` sync می‌کند (از `ItemUnitFormsetMixin`)
12. پیام موفقیت را نمایش می‌دهد
13. redirect می‌کند

**نکات مهم**:
- Checkbox fields به صورت صریح به 0 یا 1 تبدیل می‌شوند (از `IntegerCheckboxField` استفاده می‌شود)
- Unit formset اختیاری است (اگر داده نداشته باشد، validate نمی‌شود)
- Warehouse relationships به صورت خودکار sync می‌شوند (از متدهای `ItemUnitFormsetMixin`)
- متدهای `build_unit_formset()`, `_save_unit_formset()`, `_get_ordered_warehouses()`, و `_sync_item_warehouses()` از `ItemUnitFormsetMixin` در `inventory.views.base` می‌آیند

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

**Type**: `EditLockProtectedMixin, ItemUnitFormsetMixin, InventoryBaseView, UpdateView`

**Template**: `inventory/item_form.html` (extends `shared/generic/generic_form.html`)

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
- `form_title`: `_('Edit Item')`
- `breadcrumbs`: لیست breadcrumb items (Inventory > Master Data > Items > Edit)
- `cancel_url`: URL برای لغو (redirect به list)
- `object`: instance کالا برای ویرایش
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic form template اضافه می‌کند و unit formset را build می‌کند.

**Context Variables اضافه شده**: تمام متغیرهای ذکر شده در بالا، شامل `units_formset`

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.master.items'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

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
2. formset را با `build_unit_formset()` می‌سازد (از `ItemUnitFormsetMixin`)
3. اگر formset معتبر نیست، response با form و formset برمی‌گرداند
4. `form.instance.edited_by` را تنظیم می‌کند
5. مقادیر checkbox fields (`is_sellable`, `has_lot_tracking`, `requires_temporary_receipt`, `is_enabled`) را به صورت صریح تنظیم می‌کند (0 یا 1)
   - ابتدا از `form.cleaned_data` می‌خواند
   - اگر موجود نبود، از `request.POST` می‌خواند
   - مقدار را به 0 یا 1 تبدیل می‌کند
6. کالا را ذخیره می‌کند
7. formset را با `_save_unit_formset()` ذخیره می‌کند (از `ItemUnitFormsetMixin`)
8. warehouse relationships را با `_get_ordered_warehouses()` و `_sync_item_warehouses()` sync می‌کند (از `ItemUnitFormsetMixin`)
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

**Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:items`

**Attributes**:
- `model`: `models.Item`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:items')`

**Context Variables**:
- `delete_title`: `_('Delete Item')`
- `confirmation_message`: `_('Are you sure you want to delete this item?')`
- `object_details`: لیست جزئیات object (Item Code, Name, Name EN, Type, Category)
- `cancel_url`: URL برای لغو (redirect به list)
- `breadcrumbs`: لیست breadcrumb items (Inventory > Master Data > Items > Delete)
- `object`: instance کالا برای حذف
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند و `type`, `category`, `subcategory` را select_related می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions با select_related

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**توضیح**: حذف را با handling خطای ProtectedError انجام می‌دهد.

**پارامترهای ورودی**:
- `request`: HTTP request
- `*args`, `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به `success_url`

**منطق**:
1. اطلاعات کالا را log می‌کند
2. سعی می‌کند کالا را حذف کند
3. اگر موفق شد:
   - پیام موفقیت را نمایش می‌دهد: "Item deleted successfully."
   - redirect می‌کند
4. اگر `ProtectedError` رخ داد:
   - خطا را log می‌کند
   - نام مدل‌های protected را استخراج می‌کند
   - پیام خطای user-friendly می‌سازد: "Cannot delete this item because it is used in {models}."
   - پیام خطا را نمایش می‌دهد
   - redirect می‌کند

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template اضافه می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با متغیرهای لازم برای generic template

**Context Variables اضافه شده**: تمام متغیرهای ذکر شده در بالا

**Error Handling**:
- `ProtectedError`: اگر کالا در استفاده باشد (مثلاً در رسیدها یا حواله‌ها)، خطا catch می‌شود و پیام مناسب نمایش داده می‌شود

**URL**: `/inventory/items/<pk>/delete/`

---

## Warehouse Views

### `WarehouseListView`

**توضیح**: فهرست انبارها

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/warehouses.html` (extends `shared/generic/generic_list.html`)

**Attributes**:
- `model`: `models.Warehouse`
- `template_name`: `'inventory/warehouses.html'`
- `context_object_name`: `'object_list'` (برای consistency با generic template)
- `paginate_by`: `50`

**Context Variables**:
- `object_list`: queryset انبارها (paginated)
- `page_title`: `_('Warehouses')`
- `breadcrumbs`: لیست breadcrumb items
- `create_url`: URL برای ایجاد Warehouse جدید
- `create_button_text`: `_('Create Warehouse')`
- `table_headers`: [] (overridden in template)
- `show_actions`: `True`
- `edit_url_name`: `'inventory:warehouse_edit'`
- `delete_url_name`: `'inventory:warehouse_delete'`
- `empty_state_title`: `_('No Warehouses Found')`
- `empty_state_message`: `_('Start by creating your first warehouse.')`
- `empty_state_icon`: `'🏬'`
- `active_module`: `'inventory'` (از `InventoryBaseView`)

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.master.warehouses'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template اضافه می‌کند.

**Context Variables اضافه شده**: تمام متغیرهای ذکر شده در بالا

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

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.master.warehouses'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

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

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:warehouses`

**Attributes**:
- `model`: `models.Warehouse`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:warehouses')`

**Context Variables برای Generic Template**:
- `delete_title`: `_('Delete Warehouse')`
- `confirmation_message`: `_('Are you sure you want to delete this warehouse?')`
- `object_details`: لیست جزئیات warehouse (Code, Name, Name EN)
- `cancel_url`: URL برای لغو (redirect به list)
- `breadcrumbs`: لیست breadcrumb items

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با متغیرهای لازم برای generic template

**Context Variables برای Generic Template**:
- `delete_title`: `_('Delete Warehouse')`
- `confirmation_message`: `_('Are you sure you want to delete this warehouse?')`
- `object_details`: لیست جزئیات warehouse (Code, Name, Name EN)
- `cancel_url`: URL برای لغو (redirect به list)
- `breadcrumbs`: لیست breadcrumb items

---

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

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
- `ProtectedError`: اگر انبار در استفاده باشد (مثلاً در رسیدها یا حواله‌ها)، خطا catch می‌شود و پیام مناسب نمایش داده می‌شود

**URL**: `/inventory/warehouses/<pk>/delete/`

---

## Supplier Category Views

### `SupplierCategoryListView`

**توضیح**: فهرست دسته‌های تامین‌کنندگان

**Type**: `InventoryBaseView, ListView`

**Template**: `inventory/supplier_categories.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/supplier_categories.html` extends `shared/generic/generic_list.html`
  - Overrides: `page_title`, `breadcrumb_extra`, `page_actions`, `table_headers`, `table_rows`, `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `models.SupplierCategory`
- `template_name`: `'inventory/supplier_categories.html'`
- `context_object_name`: `'object_list'` (برای consistency با generic template)
- `paginate_by`: `50`

**Context Variables برای Generic Template**:
- `object_list`: queryset دسته‌های تامین‌کنندگان (paginated)
- `page_title`: `_('Supplier Categories')`
- `breadcrumbs`: لیست breadcrumb items
- `create_url`: URL برای ایجاد Supplier Category جدید
- `create_button_text`: `_('Create Supplier Category')`
- `show_actions`: `True`
- `edit_url_name`: `'inventory:suppliercategory_edit'`
- `delete_url_name`: `'inventory:suppliercategory_delete'`
- `empty_state_title`: `_('No Supplier Categories Found')`
- `empty_state_message`: `_('Start by creating your first supplier category.')`
- `empty_state_icon`: `'🏷️'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.suppliers.categories'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template اضافه می‌کند.

**Context Variables اضافه شده**: تمام متغیرهای ذکر شده در بالا (Generic Template)

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

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.suppliers.categories'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

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

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:supplier_categories`

**Attributes**:
- `model`: `models.SupplierCategory`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:supplier_categories')`

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**Context Variables برای Generic Template**:
- `delete_title`: `_('Delete Supplier Category')`
- `confirmation_message`: `_('Are you sure you want to delete this supplier category?')`
- `object_details`: لیست جزئیات supplier category (Supplier, Category, Is Primary)
- `cancel_url`: URL برای لغو (redirect به list)
- `breadcrumbs`: لیست breadcrumb items

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

**Template**: `inventory/suppliers.html` (extends `shared/generic/generic_list.html`)

**Generic Templates**:
- **List Template**: `inventory/suppliers.html` extends `shared/generic/generic_list.html`
  - Overrides: `page_title`, `breadcrumb_extra`, `page_actions`, `table_headers`, `table_rows`, `empty_state_title`, `empty_state_message`, `empty_state_icon`

**Attributes**:
- `model`: `models.Supplier`
- `template_name`: `'inventory/suppliers.html'`
- `context_object_name`: `'object_list'` (برای consistency با generic template)
- `paginate_by`: `50`

**Context Variables برای Generic Template**:
- `object_list`: queryset تامین‌کنندگان (paginated)
- `page_title`: `_('Suppliers')`
- `breadcrumbs`: لیست breadcrumb items
- `create_url`: URL برای ایجاد Supplier جدید
- `create_button_text`: `_('Create Supplier')`
- `show_actions`: `True`
- `edit_url_name`: `'inventory:supplier_edit'`
- `delete_url_name`: `'inventory:supplier_delete'`
- `empty_state_title`: `_('No Suppliers Found')`
- `empty_state_message`: `_('Start by creating your first supplier.')`
- `empty_state_icon`: `'🏢'`

**متدها**:

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.suppliers.list'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic list template اضافه می‌کند.

**Context Variables اضافه شده**: تمام متغیرهای ذکر شده در بالا (Generic Template)

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

#### `get_queryset(self) -> QuerySet`

**توضیح**: queryset را بر اساس permissions کاربر فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس permissions

**منطق**:
1. ابتدا `super().get_queryset()` را فراخوانی می‌کند که queryset را بر اساس `active_company_id` فیلتر می‌کند
2. سپس `self.filter_queryset_by_permissions()` را با feature code `'inventory.suppliers.list'` و owner field `'created_by'` فراخوانی می‌کند
3. نتیجه فیلتر شده را برمی‌گرداند

**نکته**: این متد از `filter_queryset_by_permissions` در `InventoryBaseView` استفاده می‌کند که بر اساس permissions کاربر (view_all, view_own) queryset را فیلتر می‌کند.

---

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

**Template**: `shared/generic/generic_confirm_delete.html`

**Generic Templates**:
- **Delete Template**: `shared/generic/generic_confirm_delete.html`

**Success URL**: `inventory:suppliers`

**Attributes**:
- `model`: `models.Supplier`
- `template_name`: `'shared/generic/generic_confirm_delete.html'`
- `success_url`: `reverse_lazy('inventory:suppliers')`

**متدها**:

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: context variables را برای generic delete template آماده می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: متغیرهای context اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context با متغیرهای لازم برای generic template

**Context Variables برای Generic Template**:
- `delete_title`: `_('Delete Supplier')`
- `confirmation_message`: `_('Are you sure you want to delete this supplier?')`
- `object_details`: لیست جزئیات supplier (Code, Name, City)
- `cancel_url`: URL برای لغو (redirect به list)
- `breadcrumbs`: لیست breadcrumb items

---

#### `delete(self, request, *args, **kwargs) -> HttpResponseRedirect`

**پارامترهای ورودی**:
- `request`: درخواست HTTP
- `*args, **kwargs`: آرگومان‌های اضافی

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
- `ProtectedError`: اگر تامین‌کننده در استفاده باشد (مثلاً در رسیدهای امانی)، خطا catch می‌شود و پیام مناسب نمایش داده می‌شود

**URL**: `/inventory/suppliers/<pk>/delete/`

---

## Generic Templates

تمام template های Item Types به generic templates منتقل شده‌اند:

### Item Types List
- **Template**: `inventory/item_types.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `table_headers`: Code, Name (FA), Name (EN), Sort Order, Status
  - `table_rows`: نمایش item types با تمام فیلدها
  - `empty_state_title`, `empty_state_message`, `empty_state_icon`: override برای empty state
- **Context Variables**: تمام متغیرهای لازم در `get_context_data` تنظیم شده‌اند

### Item Types Form
- **Template**: `inventory/itemtype_form.html` extends `shared/generic/generic_form.html`
- **Blocks Overridden**: 
  - `breadcrumb_extra`: مسیر breadcrumb اختصاصی
  - `before_form`: Info banner برای نمایش code (در edit mode)
  - `form_sections`: فیلدهای form
- **Context Variables**: 
  - `form_title`: "Create Item Type" یا "Edit Item Type"
  - `breadcrumbs`: لیست breadcrumb items
  - `cancel_url`: URL برای لغو

### Item Types Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات item type (Code, Name, Name EN)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

### Item Categories List
- **Template**: `inventory/item_categories.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `table_headers`: Code, Name (FA), Name (EN), Item Type, Sort Order, Status
  - `table_rows`: نمایش item categories با تمام فیلدها
  - `empty_state_title`, `empty_state_message`, `empty_state_icon`: override برای empty state
- **Context Variables**: تمام متغیرهای لازم در `get_context_data` تنظیم شده‌اند

### Item Categories Form
- **Template**: `inventory/itemcategory_form.html` extends `shared/generic/generic_form.html`
- **Blocks Overridden**: 
  - `breadcrumb_extra`: مسیر breadcrumb اختصاصی
  - `before_form`: Info banner برای نمایش code (در edit mode)
  - `form_sections`: فیلدهای form
- **Context Variables**: 
  - `form_title`: "Create Item Category" یا "Edit Item Category"
  - `breadcrumbs`: لیست breadcrumb items
  - `cancel_url`: URL برای لغو

### Item Categories Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات item category (Code, Name, Name EN, Item Type)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

### Item Subcategories List
- **Template**: `inventory/item_subcategories.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `table_headers`: Code, Name (FA), Name (EN), Item Type, Category, Sort Order, Status
  - `table_rows`: نمایش item subcategories با تمام فیلدها
  - `empty_state_title`, `empty_state_message`, `empty_state_icon`: override برای empty state
- **Context Variables**: تمام متغیرهای لازم در `get_context_data` تنظیم شده‌اند

### Item Subcategories Form
- **Template**: `inventory/itemsubcategory_form.html` extends `shared/generic/generic_form.html`
- **Blocks Overridden**: 
  - `breadcrumb_extra`: مسیر breadcrumb اختصاصی
  - `before_form`: Info banner برای نمایش code (در edit mode)
  - `form_sections`: فیلدهای form
- **Context Variables**: 
  - `form_title`: "Create Item Subcategory" یا "Edit Item Subcategory"
  - `breadcrumbs`: لیست breadcrumb items
  - `cancel_url`: URL برای لغو

### Item Subcategories Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات item subcategory (Code, Name, Name EN, Item Type, Category)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

### Warehouses List
- **Template**: `inventory/warehouses.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `table_headers`: Code, Name (FA), Name (EN), Sort Order, Status
  - `table_rows`: نمایش warehouses با تمام فیلدها
  - `empty_state_title`, `empty_state_message`, `empty_state_icon`: override برای empty state
- **Context Variables**: تمام متغیرهای لازم در `get_context_data` تنظیم شده‌اند

### Warehouses Form
- **Template**: `inventory/warehouse_form.html` extends `shared/generic/generic_form.html`
- **Blocks Overridden**: 
  - `breadcrumb_extra`: مسیر breadcrumb اختصاصی
  - `before_form`: Info banner برای نمایش code (در edit mode)
  - `form_sections`: فیلدهای form
- **Context Variables**: 
  - `form_title`: "Create Warehouse" یا "Edit Warehouse"
  - `breadcrumbs`: لیست breadcrumb items
  - `cancel_url`: URL برای لغو

### Warehouses Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات warehouse (Code, Name, Name EN)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

### Suppliers List
- **Template**: `inventory/suppliers.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `table_headers`: Code, Name, Contact Info, City, Status
  - `table_rows`: نمایش suppliers با تمام فیلدها
  - `empty_state_title`, `empty_state_message`, `empty_state_icon`: override برای empty state
- **Context Variables**: تمام متغیرهای لازم در `get_context_data` تنظیم شده‌اند

### Suppliers Form
- **Template**: `inventory/supplier_form.html` extends `shared/generic/generic_form.html`
- **Blocks Overridden**: 
  - `breadcrumb_extra`: مسیر breadcrumb اختصاصی
  - `before_form`: Info banner برای نمایش code (در edit mode)
  - `form_sections`: فیلدهای form
- **Context Variables**: 
  - `form_title`: "Create Supplier" یا "Edit Supplier"
  - `breadcrumbs`: لیست breadcrumb items
  - `cancel_url`: URL برای لغو

### Suppliers Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات supplier (Code, Name, City)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

### Supplier Categories List
- **Template**: `inventory/supplier_categories.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `table_headers`: Supplier, Category, Is Primary?, Notes
  - `table_rows`: نمایش supplier categories با تمام فیلدها
  - `empty_state_title`, `empty_state_message`, `empty_state_icon`: override برای empty state
- **Context Variables**: تمام متغیرهای لازم در `get_context_data` تنظیم شده‌اند

### Supplier Categories Form
- **Template**: `inventory/suppliercategory_form.html` extends `shared/generic/generic_form.html`
- **Blocks Overridden**: 
  - `breadcrumb_extra`: مسیر breadcrumb اختصاصی
  - `form_sections`: فیلدهای form (شامل subcategories و items که باید sync شوند)
- **Context Variables**: 
  - `form_title`: "Create Supplier Category" یا "Edit Supplier Category"
  - `breadcrumbs`: لیست breadcrumb items
  - `cancel_url`: URL برای لغو

### Supplier Categories Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات supplier category (Supplier, Category, Is Primary)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

### Items List
- **Template**: `inventory/items.html` extends `shared/generic/generic_list.html`
- **Blocks Overridden**: 
  - `page_actions`: شامل Excel template download, Excel import button, Print button, و links به Item Types/Categories/Subcategories
  - `filter_fields`: Search, Item Type, Category filters
  - `table_headers`: Item Code, Item Name, Type, Category, Batch Number, Lot Tracking, Status
  - `table_rows`: نمایش items با تمام فیلدها
  - `empty_state_title`, `empty_state_message`, `empty_state_icon`: override برای empty state
- **Context Variables**: تمام متغیرهای لازم در `get_context_data` تنظیم شده‌اند، شامل `user_feature_permissions` برای conditional rendering
- **Special Features**: Excel import form, conditional action buttons based on feature permissions

### Items Form
- **Template**: `inventory/item_form.html` extends `shared/generic/generic_form.html`
- **Blocks Overridden**: 
  - `breadcrumb_extra`: مسیر breadcrumb اختصاصی
  - `form_sections`: فیلدهای form (شامل allowed_warehouses checkbox grid)
  - `form_extra`: Unit conversions formset
  - `extra_styles`: CSS برای checkbox grid و unit formset
  - `form_scripts`: JavaScript برای formset management و cascading dropdowns (Type -> Category -> Subcategory)
- **Context Variables**: 
  - `form_title`: "Create New Item" یا "Edit Item"
  - `breadcrumbs`: لیست breadcrumb items
  - `cancel_url`: URL برای لغو
  - `units_formset`: instance از ItemUnitFormSet برای مدیریت واحدهای تبدیل
- **Complexity**: شامل formset برای unit conversions و cascading dropdowns

### Items Delete
- **Template**: `shared/generic/generic_confirm_delete.html`
- **Context Variables**:
  - `delete_title`: عنوان حذف
  - `confirmation_message`: پیام تایید
  - `object_details`: جزئیات item (Item Code, Name, Name EN, Type, Category)
  - `cancel_url`: URL برای لغو
  - `breadcrumbs`: مسیر breadcrumb

**نکته**: تمام Master Data templates (Item Types, Item Categories, Item Subcategories, Items, Warehouses, Suppliers, Supplier Categories) به generic templates منتقل شده‌اند و از context variables استاندارد استفاده می‌کنند.

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

