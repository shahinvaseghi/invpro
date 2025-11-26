# inventory/forms/request.py - Request Forms

**هدف**: Forms برای مدیریت درخواست‌ها (Requests) در ماژول inventory

این فایل شامل forms برای:
- Purchase Requests (درخواست‌های خرید)
- Warehouse Requests (درخواست‌های انبار)

---

## Purchase Request Forms

### `PurchaseRequestForm`

**توضیح**: فرم هدر برای درخواست‌های خرید با پشتیبانی multi-line.

**Type**: `forms.ModelForm`

**Model**: `PurchaseRequest`

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
  - فیلتر کردن `approver` queryset با `get_feature_approvers("inventory.requests.purchase", company_id)`
  - فقط نمایش کاربرانی که مجوز approve دارند

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
- `quantity_fulfilled`: مقدار تحویل شده (NumberInput، readonly)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, request=None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال
  - `request`: request object برای فیلتر کردن item بر اساس `request.GET`
- **Logic**:
  - فیلتر کردن `item` queryset بر اساس:
    - `company_id` و `is_enabled=1`
    - **فیلترهای اختیاری از `request.GET`**:
      - `item_type` از `request.GET.get('item_type')` - فیلتر بر اساس نوع کالا
      - `category` از `request.GET.get('category')` - فیلتر بر اساس دسته‌بندی
      - `subcategory` از `request.GET.get('subcategory')` - فیلتر بر اساس زیر دسته‌بندی
      - `item_search` از `request.GET.get('item_search')` - جستجو در `name` و `item_code` با استفاده از `Q` objects و `icontains`
  - اگر کالایی در حالت edit انتخاب شده باشد، حتی اگر disabled باشد، در queryset قرار می‌گیرد
  - تنظیم unit choices بر اساس کالای انتخاب شده
  - در حالت edit، بازیابی unit از `entered_unit` یا `unit`

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
  - اگر واحد خالی باشد، از `item.default_unit` استفاده می‌شود

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه کالا انتخاب شده باشد
  - بررسی اینکه واحد مجاز باشد

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
  - فیلتر کردن `department_unit` و `approver` بر اساس `company_id`
  - تنظیم `approver` queryset با `get_feature_approvers("inventory.requests.warehouse", company_id)`

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
  - فیلتر کردن `item` queryset بر اساس:
    - `company_id` و `is_enabled=1`
    - **فیلترهای اختیاری از `request.GET`**:
      - `item_type` از `request.GET.get('item_type')` - فیلتر بر اساس نوع کالا
      - `category` از `request.GET.get('category')` - فیلتر بر اساس دسته‌بندی
      - `subcategory` از `request.GET.get('subcategory')` - فیلتر بر اساس زیر دسته‌بندی
      - `item_search` از `request.GET.get('item_search')` - جستجو در `name` و `item_code` با استفاده از `Q` objects و `icontains`
  - فیلتر کردن `warehouse` queryset بر اساس `company_id` و `is_enabled=1`
  - اگر کالایی در حالت edit انتخاب شده باشد، حتی اگر disabled باشد، در queryset قرار می‌گیرد
  - تنظیم unit choices بر اساس کالای انتخاب شده

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
  - بررسی اینکه انبار در لیست انبارهای مجاز کالا باشد
  - استفاده از `item.allowed_warehouses`

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه کالا انتخاب شده باشد
  - بررسی اینکه واحد مجاز باشد
  - بررسی اینکه انبار مجاز باشد

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
   - **فیلترها**:
     - `item_type`: فیلتر بر اساس نوع کالا
     - `category`: فیلتر بر اساس دسته‌بندی
     - `subcategory`: فیلتر بر اساس زیر دسته‌بندی
     - `item_search`: جستجو در `name` و `item_code` با استفاده از `Q` objects و `icontains`
   - فیلترها و جستجو از طریق API endpoint `/inventory/api/filtered-items/` در template اعمال می‌شوند
   - فیلترها اختیاری هستند و می‌توانند به صورت ترکیبی استفاده شوند
   - جستجو می‌تواند بدون اعمال فیلترها استفاده شود
2. **Unit Conversion**: تمام forms از `_get_item_allowed_units()` برای دریافت واحدهای مجاز استفاده می‌کنند
3. **Warehouse Validation**: در `WarehouseRequestLineForm`، انبار باید در لیست انبارهای مجاز کالا باشد (`item.allowed_warehouses`)
4. **Approver Validation**: approver باید دسترسی به شرکت فعال داشته باشد
5. **Company Filtering**: تمام querysets بر اساس `company_id` فیلتر می‌شوند
6. **Multi-line Support**: 
   - `PurchaseRequestForm` از formset (`PurchaseRequestLineFormSet`) برای پشتیبانی multi-line استفاده می‌کند
   - `WarehouseRequestForm` از formset (`WarehouseRequestLineFormSet`) برای پشتیبانی multi-line استفاده می‌کند
7. **Header-only Forms**: 
   - `PurchaseRequestForm` و `WarehouseRequestForm` فقط فیلدهای هدر را دارند
   - تمام فیلدهای item در line forms قرار دارند

