# inventory/forms/request.py - Request Forms

**هدف**: Forms برای مدیریت درخواست‌ها (Requests) در ماژول inventory

این فایل شامل forms برای:
- Purchase Requests (درخواست‌های خرید)
- Warehouse Requests (درخواست‌های انبار)

---

## Purchase Request Forms

### `PurchaseRequestForm`

**توضیح**: فرم هدر برای درخواست‌های خرید با پشتیبانی multi-line.

**Type**: `BaseModelForm` (از `shared.forms.base`)

**Model**: `PurchaseRequest`

**نکته**: این form از `BaseModelForm` استفاده می‌کند که به صورت خودکار کلاس `form-control` را به widget ها اضافه می‌کند.

**Fields**:
- `needed_by_date`: تاریخ مورد نیاز (JalaliDateInput)
- `priority`: اولویت (Select)
- `reason_code`: کد دلیل / یادداشت‌ها (Textarea، اختیاری)
- `approver`: تاییدکننده (Select)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, request_user: Optional[Any] = None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال
  - `request_user`: کاربر درخواست‌دهنده
- **Logic**:
  1. تنظیم `self.company_id` و `self.request_user`
  2. تنظیم `reason_code` به `required=False`
  3. اگر `company_id` موجود باشد:
     - دریافت approvers از `get_feature_approvers("inventory.requests.purchase", company_id)`
     - تنظیم `approver` queryset
     - تنظیم `empty_label` و `label_from_instance` برای approver
  4. تنظیم `approver` به `required=True`

#### `clean_approver(self) -> Any`
- **Returns**: User اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه approver دسترسی به شرکت فعال داشته باشد
  - بررسی از طریق `UserCompanyAccess`

---

### `PurchaseRequestLineForm`

**توضیح**: فرم برای ردیف‌های درخواست خرید.

**Type**: `forms.ModelForm`

**Model**: `PurchaseRequestLine`

**Custom Fields**:
- `unit`: واحد اندازه‌گیری (ChoiceField)

**Fields**:
- `item`: کالا (Select)
- `unit`: واحد (Select)
- `quantity_requested`: مقدار درخواستی (NumberInput)
- `line_notes`: یادداشت‌ها (Textarea، اختیاری)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, request=None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال
  - `request`: request object برای فیلتر کردن item بر اساس `request.GET`
- **Logic**:
  1. تنظیم `self.company_id` از parameter یا instance
  2. تنظیم `self.request` برای استفاده در فیلترها
  3. اگر `company_id` موجود باشد:
     - ساخت base queryset: `Item.objects.filter(company_id=company_id, is_enabled=1)`
     - **اعمال فیلترهای اختیاری از `request.GET` یا `request.POST`**:
       - `item_type`: از `request.GET.get('item_type')` یا `request.POST.get('item_type')` - فیلتر بر اساس `type_id`
       - `category`: از `request.GET.get('category')` یا `request.POST.get('category')` - فیلتر بر اساس `category_id`
       - `subcategory`: از `request.GET.get('subcategory')` یا `request.POST.get('subcategory')` - فیلتر بر اساس `subcategory_id`
       - `item_search`: از `request.GET.get('item_search')` یا `request.POST.get('item_search')` - جستجو در `name`, `item_code`, و `full_item_code` با استفاده از `Q` objects و `icontains`
     - **اگر در حالت edit و instance دارای item باشد**: اضافه کردن item به queryset حتی اگر disabled باشد (با استفاده از `Q(pk=instance_item_id)`)
     - تنظیم queryset نهایی و `label_from_instance` برای item
  4. تنظیم unit choices به `UNIT_CHOICES`
  5. **Restore unit value در حالت edit**:
     - اگر form unbound باشد و instance دارای pk باشد
     - اگر unit value در choices موجود نباشد، به choices اضافه می‌شود
     - تنظیم `initial['unit']` به unit value

#### `_resolve_item(self, candidate: Any = None) -> Optional[Item]`
- **Returns**: Item instance یا None
- **Logic**: resolve کردن کالا از form data یا instance

#### `_get_item_allowed_units(self, item: Optional[Item]) -> list`
- **Returns**: لیست دیکشنری‌های `{'value': unit_code, 'label': unit_label}`
- **Logic**: دریافت واحدهای مجاز از `item.default_unit`, `item.primary_unit`, و `ItemUnit` conversions

#### `_set_unit_choices_for_item(self, item: Optional[Item]) -> None`
- **Logic**: تنظیم unit choices بر اساس کالای انتخاب شده

#### `clean_unit(self) -> str`
- **Returns**: واحد اعتبارسنجی شده
- **Logic**:
  1. دریافت unit از `cleaned_data`
  2. دریافت item از `_resolve_item()`
  3. اگر item موجود باشد:
     - دریافت allowed units از `_get_item_allowed_units(item)`
     - بررسی اینکه unit در allowed units باشد
     - اگر unit موجود نباشد و unit خالی نباشد، ValidationError
  4. بازگشت unit

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  1. فراخوانی `super().clean()`
  2. دریافت item از `_resolve_item()`
  3. اگر item موجود باشد و field `unit` وجود داشته باشد:
     - تنظیم unit choices بر اساس item با `_set_unit_choices_for_item(item)`
  4. بازگشت `cleaned_data`

---

### `PurchaseRequestLineFormSet`

**توضیح**: Formset برای مدیریت چند خط درخواست خرید.

**Type**: `inlineformset_factory`

**Base Form**: `PurchaseRequestLineForm`

**Base FormSet**: `BaseLineFormSet`

**Options**:
- `extra`: `1` (یک فرم خالی برای اضافه کردن خط جدید)
- `can_delete`: `True` (امکان حذف خطوط)
- `min_num`: `1` (حداقل یک خط الزامی است)
- `validate_min`: `True` (اعتبارسنجی حداقل تعداد خطوط)

---

## Warehouse Request Forms

### `WarehouseRequestForm`

**توضیح**: فرم هدر برای درخواست‌های انبار با پشتیبانی multi-line.

**Type**: `forms.ModelForm`

**Model**: `WarehouseRequest`

**Fields**:
- `department_unit`: واحد سازمانی (Select، اختیاری)
- `needed_by_date`: تاریخ مورد نیاز (JalaliDateInput)
- `priority`: اولویت (Select)
- `purpose`: هدف / یادداشت‌ها (Textarea، اختیاری)
- `approver`: تاییدکننده (Select)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, request_user: Optional[Any] = None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال
  - `request_user`: کاربر درخواست‌دهنده
- **Logic**:
  1. تنظیم `self.company_id` و `self.request_user`
  2. تنظیم `purpose` و `department_unit` به `required=False`
  3. اگر `company_id` موجود باشد:
     - فیلتر کردن `department_unit` queryset بر اساس `company_id` و `is_enabled=1`
     - تنظیم `label_from_instance` و `empty_label` برای department_unit
     - دریافت approvers از `get_feature_approvers("inventory.requests.warehouse", company_id)`
     - تنظیم `approver` queryset و `empty_label`
  4. تنظیم `approver` به `required=True`

#### `clean_approver(self) -> Any`
- **Returns**: User اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه approver دسترسی به شرکت فعال داشته باشد
  - بررسی از طریق `UserCompanyAccess`

---

### `WarehouseRequestLineForm`

**توضیح**: فرم برای ردیف‌های درخواست انبار.

**Type**: `forms.ModelForm`

**Model**: `WarehouseRequestLine`

**Custom Fields**:
- `unit`: واحد اندازه‌گیری (ChoiceField)

**Fields**:
- `item`: کالا (Select)
- `unit`: واحد (Select)
- `quantity_requested`: مقدار درخواستی (NumberInput)
- `warehouse`: انبار (Select)
- `line_notes`: یادداشت‌ها (Textarea، اختیاری)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, request=None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال
  - `request`: request object برای فیلتر کردن item بر اساس `request.GET`
- **Logic**:
  1. تنظیم `self.company_id` از parameter یا instance
  2. تنظیم `self.request` برای استفاده در فیلترها
  3. اگر `company_id` موجود باشد:
     - **فیلتر کردن `item` queryset**:
       - ساخت base queryset: `Item.objects.filter(company_id=company_id, is_enabled=1)`
       - **اعمال فیلترهای اختیاری از `request.GET` یا `request.POST`**:
         - `item_type`: از `request.GET.get('item_type')` یا `request.POST.get('item_type')` - فیلتر بر اساس `type_id`
         - `category`: از `request.GET.get('category')` یا `request.POST.get('category')` - فیلتر بر اساس `category_id`
         - `subcategory`: از `request.GET.get('subcategory')` یا `request.POST.get('subcategory')` - فیلتر بر اساس `subcategory_id`
         - `item_search`: از `request.GET.get('item_search')` یا `request.POST.get('item_search')` - جستجو در `name`, `item_code`, و `full_item_code` با استفاده از `Q` objects و `icontains`
       - **اگر در حالت edit و instance دارای item باشد**: اضافه کردن item به queryset حتی اگر disabled باشد (با استفاده از `Q(pk=instance_item_id)`)
       - تنظیم queryset نهایی و `label_from_instance` برای item
     - **فیلتر کردن `warehouse` queryset**:
       - `Warehouse.objects.filter(company_id=company_id, is_enabled=1).order_by('name')`
       - تنظیم `label_from_instance` برای warehouse
  4. تنظیم unit choices به `UNIT_CHOICES`
  5. **Restore unit value در حالت edit**:
     - اگر form unbound باشد و instance دارای pk باشد
     - اگر unit value در choices موجود نباشد، به choices اضافه می‌شود
     - تنظیم `initial['unit']` به unit value

#### `_resolve_item(self, candidate: Any = None) -> Optional[Item]`
- **Returns**: Item instance یا None
- **Logic**: resolve کردن کالا از form data یا instance

#### `_get_item_allowed_units(self, item: Optional[Item]) -> list`
- **Returns**: لیست دیکشنری‌های `{'value': unit_code, 'label': unit_label}`
- **Logic**: دریافت واحدهای مجاز از `item.default_unit`, `item.primary_unit`, و `ItemUnit` conversions

#### `_set_unit_choices_for_item(self, item: Optional[Item]) -> None`
- **Logic**: تنظیم unit choices بر اساس کالای انتخاب شده

#### `clean_unit(self) -> str`
- **Returns**: واحد اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه واحد در لیست واحدهای مجاز کالا باشد

#### `clean_warehouse(self) -> Warehouse`
- **Returns**: Warehouse اعتبارسنجی شده
- **Logic**:
  1. دریافت warehouse از `cleaned_data`
  2. دریافت item از `_resolve_item()`
  3. اگر item و warehouse موجود باشند:
     - دریافت allowed warehouses از `item.warehouses.select_related('warehouse').filter(warehouse__company_id=company_id, warehouse__is_enabled=1)`
     - استخراج `allowed_warehouse_ids` از relations
     - **اگر هیچ warehouse مجاز تنظیم نشده باشد**:
       - بررسی اینکه warehouse متعلق به company باشد و enabled باشد
       - اگر نباشد، ValidationError
     - **اگر warehouse های مجاز وجود داشته باشند**:
       - بررسی اینکه warehouse.id در `allowed_warehouse_ids` باشد
       - اگر نباشد، ValidationError
  4. بازگشت warehouse

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  1. فراخوانی `super().clean()`
  2. دریافت item از `_resolve_item()`
  3. اگر item موجود باشد و field `unit` وجود داشته باشد:
     - تنظیم unit choices بر اساس item با `_set_unit_choices_for_item(item)`
  4. بازگشت `cleaned_data`

---

### `WarehouseRequestLineFormSet`

**توضیح**: Formset برای مدیریت چند خط درخواست انبار.

**Type**: `inlineformset_factory`

**Base Form**: `WarehouseRequestLineForm`

**Base FormSet**: `BaseLineFormSet`

**Options**:
- `extra`: `1` (یک فرم خالی برای اضافه کردن خط جدید)
- `can_delete`: `True` (امکان حذف خطوط)
- `min_num`: `1` (حداقل یک خط الزامی است)
- `validate_min`: `True` (اعتبارسنجی حداقل تعداد خطوط)

---

## وابستگی‌ها

- `inventory.models`: `PurchaseRequest`, `PurchaseRequestLine`, `WarehouseRequest`, `WarehouseRequestLine`, `Item`, `ItemUnit`, `Warehouse`
- `inventory.forms.base`: `UNIT_CHOICES`, `get_feature_approvers`, `BaseLineFormSet`
- `inventory.widgets`: `JalaliDateInput`
- `shared.models`: `CompanyUnit`
- `django.db.models.Q`: برای جستجو در `name` و `item_code`

---

## استفاده در پروژه

این forms در views ماژول inventory استفاده می‌شوند:
- `PurchaseRequestCreateView`, `PurchaseRequestUpdateView` (با `PurchaseRequestLineFormSet`)
- `WarehouseRequestCreateView`, `WarehouseRequestUpdateView` (با `WarehouseRequestLineFormSet`)

---

## نکات مهم

1. **Item Filtering and Search**: 
   - `PurchaseRequestLineForm` و `WarehouseRequestLineForm` از `request.GET` برای فیلتر کردن item استفاده می‌کنند
   - **فیلترها** (از `request.GET` یا `request.POST`):
     - `item_type`: فیلتر بر اساس نوع کالا (`type_id`)
     - `category`: فیلتر بر اساس دسته‌بندی (`category_id`)
     - `subcategory`: فیلتر بر اساس زیر دسته‌بندی (`subcategory_id`)
     - `item_search`: جستجو در `name`, `item_code`, و `full_item_code` با استفاده از `Q` objects و `icontains`
   - فیلترها و جستجو از طریق API endpoint `/inventory/api/filtered-items/` در template اعمال می‌شوند
   - فیلترها اختیاری هستند و می‌توانند به صورت ترکیبی استفاده شوند
   - جستجو می‌تواند بدون اعمال فیلترها استفاده شود
2. **Unit Conversion**: تمام forms از `_get_item_allowed_units()` برای دریافت واحدهای مجاز استفاده می‌کنند
3. **Warehouse Validation**: در `WarehouseRequestLineForm`:
   - اگر کالا دارای warehouse های مجاز تنظیم شده باشد (`item.warehouses`)، فقط آن warehouse ها مجاز هستند
   - اگر هیچ warehouse مجاز تنظیم نشده باشد، تمام warehouse های company (enabled) مجاز هستند
   - انبار باید متعلق به company باشد و enabled باشد
4. **Approver Validation**: approver باید دسترسی به شرکت فعال داشته باشد
5. **Company Filtering**: تمام querysets بر اساس `company_id` فیلتر می‌شوند
6. **Multi-line Support**: 
   - `PurchaseRequestForm` از formset (`PurchaseRequestLineFormSet`) برای پشتیبانی multi-line استفاده می‌کند
   - `WarehouseRequestForm` از formset (`WarehouseRequestLineFormSet`) برای پشتیبانی multi-line استفاده می‌کند
7. **Header-only Forms**: 
   - `PurchaseRequestForm` و `WarehouseRequestForm` فقط فیلدهای هدر را دارند
   - تمام فیلدهای item در line forms قرار دارند
8. **Unit Restore Logic**: در حالت edit، اگر unit value در choices موجود نباشد، به choices اضافه می‌شود تا value حفظ شود
9. **Form Inheritance**: `PurchaseRequestForm` از `BaseModelForm` استفاده می‌کند (automatic widget styling)، اما `WarehouseRequestForm` از `forms.ModelForm` استفاده می‌کند

