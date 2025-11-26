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

## Warehouse Request Form

### `WarehouseRequestForm`

**توضیح**: فرم برای درخواست انبار (single-item).

**Type**: `forms.ModelForm`

**Model**: `WarehouseRequest`

**Custom Fields**:
- `unit`: واحد اندازه‌گیری (ChoiceField)
- `approver`: تاییدکننده (ModelChoiceField)

**Fields**:
- `item`: کالا (Select)
- `unit`: واحد (Select)
- `quantity_requested`: مقدار درخواستی (NumberInput)
- `warehouse`: انبار (Select)
- `department_unit`: واحد سازمانی (Select، اختیاری)
- `needed_by_date`: تاریخ مورد نیاز (JalaliDateInput)
- `reason_code`: کد دلیل / یادداشت‌ها (Textarea، اختیاری)
- `approver`: تاییدکننده (Select)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, request_user: Optional[Any] = None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال
  - `request_user`: کاربر درخواست‌دهنده
- **Logic**:
  - فراخوانی `_setup_item_queryset()` برای فیلتر کردن item
  - تنظیم unit choices
  - فیلتر کردن `warehouse`, `department_unit`, `approver` بر اساس `company_id`
  - در حالت edit، بازیابی unit از `entered_unit` یا `unit`

#### `_setup_item_queryset(self) -> None`
- **Logic**:
  - فیلتر کردن `item` queryset بر اساس:
    - `company_id` و `is_enabled=1`
    - **فیلترهای اختیاری از `request.GET`** (اگر `request` موجود باشد):
      - `item_type` - فیلتر بر اساس نوع کالا
      - `category` - فیلتر بر اساس دسته‌بندی
      - `subcategory` - فیلتر بر اساس زیر دسته‌بندی
      - `item_search` - جستجو در `name` و `item_code` با استفاده از `Q` objects و `icontains`
    - اگر کالایی در حالت edit انتخاب شده باشد، حتی اگر disabled باشد، در queryset قرار می‌گیرد

#### `_resolve_item(self, candidate: Any = None) -> Optional[Item]`
- **Returns**: Item instance یا None
- **Logic**: resolve کردن کالا از form data یا instance

#### `_get_item_allowed_units(self, item: Optional[Item]) -> list`
- **Returns**: لیست دیکشنری‌های `{'value': unit_code, 'label': unit_label}`
- **Logic**: دریافت واحدهای مجاز کالا

#### `_get_item_allowed_warehouses(self, item: Optional[Item]) -> list`
- **Returns**: لیست دیکشنری‌های `{'value': warehouse_id, 'label': warehouse_name}`
- **Logic**: دریافت انبارهای مجاز کالا از `item.warehouses`

#### `_set_unit_choices(self) -> None`
- **Logic**: تنظیم unit choices بر اساس کالای انتخاب شده

#### `clean_unit(self) -> str`
- **Returns**: واحد اعتبارسنجی شده
- **Logic**: بررسی اینکه واحد در لیست واحدهای مجاز کالا باشد

#### `clean_warehouse(self) -> Any`
- **Returns**: Warehouse اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه انبار در لیست انبارهای مجاز کالا باشد
  - اگر کالا هیچ انبار مجازی نداشته باشد، خطا می‌دهد

#### `clean_approver(self) -> Any`
- **Returns**: User اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه approver دسترسی به شرکت فعال داشته باشد
  - بررسی از طریق `UserCompanyAccess`

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  - اعتبارسنجی واحد
  - اعتبارسنجی انبار
  - اعتبارسنجی approver

---

## وابستگی‌ها

- `inventory.models`: `PurchaseRequest`, `PurchaseRequestLine`, `WarehouseRequest`, `Item`, `ItemUnit`, `Warehouse`
- `inventory.forms.base`: `UNIT_CHOICES`, `get_feature_approvers`, `BaseLineFormSet`
- `inventory.widgets`: `JalaliDateInput`
- `shared.models`: `CompanyUnit`
- `django.db.models.Q`: برای جستجو در `name` و `item_code`

---

## استفاده در پروژه

این forms در views ماژول inventory استفاده می‌شوند:
- `PurchaseRequestCreateView`, `PurchaseRequestUpdateView`
- `WarehouseRequestCreateView`, `WarehouseRequestUpdateView`

---

## نکات مهم

1. **Item Filtering and Search**: 
   - `PurchaseRequestLineForm` و `WarehouseRequestForm` از `request.GET` برای فیلتر کردن item استفاده می‌کنند
   - **فیلترها**:
     - `item_type`: فیلتر بر اساس نوع کالا
     - `category`: فیلتر بر اساس دسته‌بندی
     - `subcategory`: فیلتر بر اساس زیر دسته‌بندی
     - `item_search`: جستجو در `name` و `item_code` با استفاده از `Q` objects و `icontains`
   - فیلترها و جستجو از طریق API endpoint `/inventory/api/filtered-items/` در template اعمال می‌شوند
   - فیلترها اختیاری هستند و می‌توانند به صورت ترکیبی استفاده شوند
   - جستجو می‌تواند بدون اعمال فیلترها استفاده شود
2. **Unit Conversion**: تمام forms از `_get_item_allowed_units()` برای دریافت واحدهای مجاز استفاده می‌کنند
3. **Entered Values**: مقادیر وارد شده (`entered_unit`) حفظ می‌شوند
4. **Warehouse Validation**: در `WarehouseRequestForm`، انبار باید در لیست انبارهای مجاز کالا باشد
5. **Approver Validation**: approver باید دسترسی به شرکت فعال داشته باشد
6. **Company Filtering**: تمام querysets بر اساس `company_id` فیلتر می‌شوند
7. **Multi-line Support**: `PurchaseRequestForm` از formset (`PurchaseRequestLineFormSet`) برای پشتیبانی multi-line استفاده می‌کند
8. **Single-item Support**: `WarehouseRequestForm` یک فرم single-item است (نه formset)

