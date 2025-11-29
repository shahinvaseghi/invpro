# inventory/forms/issue.py - Issue Forms

**هدف**: Forms برای مدیریت حواله‌ها (Issues) در ماژول inventory

این فایل شامل forms برای:
- Permanent Issues (حواله‌های دائم)
- Consumption Issues (حواله‌های مصرف)
- Consignment Issues (حواله‌های امانی)
- Serial Assignment (اختصاص سریال)
- Line Forms و Formsets برای هر نوع حواله

---

## Header Forms (فرم‌های هدر)

### `IssuePermanentForm`

**توضیح**: فرم هدر برای حواله‌های دائم با پشتیبانی multi-line.

**Type**: `forms.ModelForm`

**Model**: `IssuePermanent`

**Fields**:
- `document_code`: کد سند (HiddenInput، auto-generated)
- `document_date`: تاریخ سند (HiddenInput، auto-generated)
- `department_unit`: واحد سازمانی (Select، اختیاری)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`
- **Parameters**: `company_id` برای فیلتر کردن querysets
- **Logic**:
  1. تنظیم `self.company_id` از parameter یا instance
  2. تنظیم `document_code` و `document_date` به hidden و not required
  3. تنظیم initial value برای `document_date` به امروز (اگر instance جدید باشد)
  4. فیلتر کردن `department_unit` queryset:
     - فقط واحدهای با `company_id` مطابق و `is_enabled=1`
     - مرتب‌سازی: `name`
     - تنظیم `label_from_instance` برای نمایش `public_code · name`

#### `clean_document_code(self) -> str`
- **Returns**: کد سند (خالی اگر باید auto-generate شود)
- **Logic**: اگر خالی باشد، در `save()` تولید می‌شود

#### `clean_document_date(self)`
- **Returns**: تاریخ سند (امروز به صورت پیش‌فرض)
- **Logic**: اگر خالی باشد، تاریخ امروز را برمی‌گرداند

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  1. فراخوانی `super().clean()`
  2. تنظیم `document_code` به خالی اگر وجود نداشته باشد
  3. تنظیم `document_date` به امروز اگر وجود نداشته باشد

#### `save(self, commit: bool = True)`
- **Returns**: instance ذخیره شده
- **Logic**:
  1. ذخیره instance با `super().save(commit=False)`
  2. تنظیم `company_id` از `self.company_id` اگر تنظیم نشده باشد
  3. تولید `document_code` با prefix "ISP" اگر خالی باشد (با `generate_document_code()`)
  4. تنظیم `document_date` به امروز اگر خالی باشد
  5. تنظیم `department_unit` و `department_unit_code`:
     - اگر `department_unit` انتخاب شده باشد: `department_unit_code = department_unit.public_code`
     - در غیر این صورت: `department_unit = None`, `department_unit_code = ''`
  6. اگر `commit=True`: ذخیره instance
  7. بازگشت instance

---

### `IssueConsumptionForm`

**توضیح**: فرم هدر برای حواله‌های مصرف با پشتیبانی multi-line.

**Type**: `forms.ModelForm`

**Model**: `IssueConsumption`

**Fields**:
- `document_code`: کد سند (HiddenInput، auto-generated)
- `document_date`: تاریخ سند (HiddenInput، auto-generated)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`
- **Parameters**: `company_id` برای تنظیم `self.company_id`
- **Logic**:
  1. تنظیم `self.company_id` از parameter یا instance
  2. تنظیم `document_code` و `document_date` به not required
  3. تنظیم initial value برای `document_date` به امروز (اگر instance جدید باشد)

#### `clean_document_date(self)`
- **Returns**: تاریخ سند (امروز به صورت پیش‌فرض)
- **Logic**: اگر خالی باشد، تاریخ امروز را برمی‌گرداند

#### `clean_document_code(self) -> str`
- **Returns**: کد سند (خالی اگر باید auto-generate شود)
- **Logic**: اگر خالی باشد، در `save()` تولید می‌شود

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  1. فراخوانی `super().clean()`
  2. تنظیم `document_code` به خالی اگر وجود نداشته باشد
  3. تنظیم `document_date` به امروز اگر وجود نداشته باشد

#### `save(self, commit: bool = True)`
- **Returns**: instance ذخیره شده
- **Logic**:
  1. ذخیره instance با `super().save(commit=False)`
  2. تولید `document_code` با prefix "ISU" اگر خالی باشد (با `generate_document_code()`)
  3. تنظیم `document_date` به امروز اگر خالی باشد
  4. اگر `commit=True`: ذخیره instance
  5. بازگشت instance

---

### `IssueConsignmentForm`

**توضیح**: فرم هدر برای حواله‌های امانی با پشتیبانی multi-line.

**Type**: `forms.ModelForm`

**Model**: `IssueConsignment`

**Fields**:
- `document_code`: کد سند (HiddenInput، auto-generated)
- `document_date`: تاریخ سند (HiddenInput، auto-generated)
- `department_unit`: واحد سازمانی (Select، اختیاری)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`
- **Parameters**: `company_id` برای فیلتر کردن querysets
- **Logic**:
  1. تنظیم `self.company_id` از parameter یا instance
  2. تنظیم `document_code` و `document_date` به not required
  3. تنظیم initial value برای `document_date` به امروز (اگر instance جدید باشد)
  4. فیلتر کردن `department_unit` queryset:
     - فقط واحدهای با `company_id` مطابق و `is_enabled=1`
     - مرتب‌سازی: `name`
     - تنظیم `label_from_instance` برای نمایش `public_code · name`

#### `clean_document_date(self)`
- **Returns**: تاریخ سند (امروز به صورت پیش‌فرض)
- **Logic**: اگر خالی باشد، تاریخ امروز را برمی‌گرداند

#### `clean_document_code(self) -> str`
- **Returns**: کد سند (خالی اگر باید auto-generate شود)
- **Logic**: اگر خالی باشد، در `save()` تولید می‌شود

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  1. فراخوانی `super().clean()`
  2. تنظیم `document_code` به خالی اگر وجود نداشته باشد
  3. تنظیم `document_date` به امروز اگر وجود نداشته باشد

#### `save(self, commit: bool = True)`
- **Returns**: instance ذخیره شده
- **Logic**:
  1. ذخیره instance با `super().save(commit=False)`
  2. تولید `document_code` با prefix "ICN" اگر خالی باشد (با `generate_document_code()`)
  3. تنظیم `document_date` به امروز اگر خالی باشد
  4. تنظیم `department_unit` و `department_unit_code`:
     - اگر `department_unit` انتخاب شده باشد: `department_unit_code = department_unit.public_code`
     - در غیر این صورت: `department_unit = None`, `department_unit_code = ''`
  5. اگر `commit=True`: ذخیره instance
  6. بازگشت instance

---

## Serial Assignment Form

### `IssueLineSerialAssignmentForm`

**توضیح**: فرم برای اختصاص سریال به یک ردیف حواله.

**Type**: `forms.Form`

**Fields**:
- `serials`: سریال‌های انتخاب شده (ModelMultipleChoiceField، CheckboxSelectMultiple)

**متدها**:

#### `__init__(self, line, *args, **kwargs)`
- **Parameters**:
  - `line`: ردیف حواله که سریال‌ها به آن اختصاص می‌یابند
- **Logic**:
  - فیلتر کردن queryset به فقط سریال‌های AVAILABLE یا RESERVED برای این ردیف
  - حذف سریال‌های ISSUED, CONSUMED, DAMAGED, RETURNED
  - نمایش help_text با تعداد سریال‌های مورد نیاز

#### `clean_serials(self) -> list`
- **Returns**: لیست سریال‌های اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه تعداد سریال‌های انتخاب شده برابر با `quantity` باشد
  - بررسی اینکه تمام سریال‌ها متعلق به همان کالا باشند

#### `save(self, user=None)`
- **Parameters**: `user` برای لاگ کردن تغییرات
- **Logic**:
  - تنظیم سریال‌ها در `line.serials`
  - فراخوانی `serial_service.sync_issue_line_serials()` برای به‌روزرسانی وضعیت سریال‌ها

---

## Base Line Form

### `IssueLineBaseForm`

**توضیح**: کلاس پایه برای فرم‌های خطی حواله‌ها.

**Type**: `forms.ModelForm` (abstract)

**Custom Fields**:
- `unit`: واحد اندازه‌گیری (ChoiceField)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`
- **Logic**:
  - فیلتر کردن querysets برای `item`, `warehouse` بر اساس `company_id`
  - تنظیم unit choices
  - بازیابی مقادیر `entered_unit`, `entered_quantity` در حالت edit

#### `clean_item(self) -> Optional[Item]`
- **Logic**: به‌روزرسانی unit و warehouse choices بر اساس کالای انتخاب شده

#### `clean_warehouse(self) -> Optional[Warehouse]`
- **Logic**: بررسی اینکه انبار در لیست انبارهای مجاز کالا باشد

#### `clean_unit(self) -> str`
- **Logic**: بررسی اینکه واحد در لیست واحدهای مجاز کالا باشد

#### `clean(self) -> Dict[str, Any]`
- **Logic**:
  - اعتبارسنجی انبار
  - اعتبارسنجی و normalize کردن واحد
  - **اعتبارسنجی موجودی**: بررسی اینکه موجودی کافی برای حواله وجود دارد
    - محاسبه موجودی فعلی با `inventory_balance.calculate_item_balance()`
    - در حالت edit، اضافه کردن quantity قدیمی به موجودی
    - اگر `issue_quantity > available_balance`، خطا می‌دهد

#### `save(self, commit: bool = True)`
- **Logic**: ذخیره `entered_unit` و `entered_quantity`

**Helper Methods** (مشابه `ReceiptLineBaseForm`):
- `_get_item_allowed_warehouses()`: دریافت انبارهای مجاز کالا
- `_set_warehouse_queryset()`: تنظیم warehouse queryset
- `_resolve_item()`: resolve کردن کالا از form data یا instance
- `_get_item_allowed_units()`: دریافت واحدهای مجاز کالا
- `_set_unit_choices()`: تنظیم unit choices
- `_get_unit_factor()`: محاسبه فاکتور تبدیل واحد (BFS)
- `_validate_unit()`: اعتبارسنجی واحد و محاسبه فاکتور
- `_normalize_quantity()`: تبدیل quantity به واحد پایه

---

## Line Forms (فرم‌های خطی)

### `IssuePermanentLineForm`

**توضیح**: فرم برای ردیف‌های حواله دائم.

**Type**: `IssueLineBaseForm`

**Model**: `IssuePermanentLine`

**Custom Fields**:
- `destination_type`: واحد کاری مقصد (ModelChoiceField، CompanyUnit)

**Fields**:
- تمام fields از `IssueLineBaseForm`
- `destination_type`, `destination_id`, `destination_code`, `reason_code`
- `unit_price`, `currency`, `tax_amount`, `discount_amount`, `total_amount`
- `line_notes`

**متدها**:

#### `_update_destination_type_queryset(self) -> None`
- **Logic**:
  - تنظیم queryset `destination_type` بر اساس `company_id`
  - در حالت edit، تلاش برای پیدا کردن CompanyUnit از `destination_id` یا `destination_code`

#### `clean_destination_type(self) -> Optional[CompanyUnit]`
- **Returns**: CompanyUnit اعتبارسنجی شده
- **Logic**: ذخیره CompanyUnit برای استفاده در `save()`

#### `save(self, commit: bool = True)`
- **Logic**:
  - تنظیم `destination_type = 'company_unit'`
  - تنظیم `destination_id` و `destination_code` از CompanyUnit

---

### `IssueConsumptionLineForm`

**توضیح**: فرم برای ردیف‌های حواله مصرف.

**Type**: `IssueLineBaseForm`

**Model**: `IssueConsumptionLine`

**Custom Fields**:
- `destination_type_choice`: نوع مقصد (ChoiceField: 'company_unit' یا 'work_line')
- `destination_company_unit`: واحد کاری مقصد (ModelChoiceField)
- `destination_work_line`: خط کاری مقصد (ModelChoiceField، فقط اگر production module نصب باشد)
- `work_line`: خط کاری (ModelChoiceField، فقط اگر production module نصب باشد)

**Fields**:
- تمام fields از `IssueLineBaseForm`
- `destination_type_choice`, `destination_company_unit`, `destination_work_line`
- `consumption_type` (HiddenInput، تنظیم خودکار)
- `work_line`
- `reference_document_type`, `reference_document_id`, `reference_document_code`
- `production_transfer_id`, `production_transfer_code`
- `unit_cost`, `total_cost`, `cost_center_code` (HiddenInput، برای ذخیره company_unit code)
- `line_notes`

**متدها**:

#### `_update_querysets_after_company_id(self) -> None`
- **Logic**:
  - اضافه کردن گزینه 'work_line' به `destination_type_choice` اگر production module نصب باشد
  - تنظیم querysets برای `work_line`, `destination_company_unit`, `destination_work_line`
  - در حالت edit، بازیابی مقادیر از `consumption_type` و `cost_center_code`

#### `clean(self) -> Dict[str, Any]`
- **Logic**:
  - فراخوانی `super().clean()`
  - بررسی اینکه `destination_type_choice` انتخاب شده باشد
  - اعتبارسنجی بر اساس نوع مقصد:
    - اگر 'company_unit': بررسی `destination_company_unit`
    - اگر 'work_line': بررسی `destination_work_line` و نصب بودن production module

#### `save(self, commit: bool = True)`
- **Logic**:
  - اگر `destination_type_choice == 'company_unit'`:
    - تنظیم `consumption_type = 'company_unit'`
    - ذخیره `public_code` در `cost_center_code`
    - تنظیم `work_line = None`
  - اگر `destination_type_choice == 'work_line'`:
    - تنظیم `consumption_type = 'work_line'`
    - تنظیم `work_line = destination_work_line`
    - پاک کردن `cost_center_code` اگر قبلاً برای company_unit استفاده شده بود

---

### `IssueConsignmentLineForm`

**توضیح**: فرم برای ردیف‌های حواله امانی.

**Type**: `IssueLineBaseForm`

**Model**: `IssueConsignmentLine`

**Custom Fields**:
- `consignment_receipt`: رسید امانی مرتبط (ModelChoiceField، اختیاری)
- `destination_type`: واحد کاری مقصد (ModelChoiceField، CompanyUnit)

**Fields**:
- تمام fields از `IssueLineBaseForm`
- `consignment_receipt`
- `destination_type`, `destination_id`, `destination_code`, `reason_code`
- `line_notes`

**متدها**:

#### `_update_destination_type_queryset(self) -> None`
- **Logic**:
  - تنظیم queryset `consignment_receipt` بر اساس `company_id`
  - تنظیم queryset `destination_type` بر اساس `company_id`
  - در حالت edit، تلاش برای پیدا کردن CompanyUnit

#### `clean_destination_type(self) -> Optional[CompanyUnit]`
- **Returns**: CompanyUnit اعتبارسنجی شده

#### `save(self, commit: bool = True)`
- **Logic**:
  - تنظیم `destination_type = 'company_unit'`
  - تنظیم `destination_id` و `destination_code` از CompanyUnit

---

## Formsets

### `IssuePermanentLineFormSet`

**توضیح**: Formset برای ردیف‌های حواله دائم.

**Type**: `inlineformset_factory(IssuePermanent, IssuePermanentLine, ...)`

**Configuration**:
- `form`: `IssuePermanentLineForm`
- `formset`: `BaseLineFormSet`
- `extra`: 1
- `can_delete`: True
- `min_num`: 1
- `validate_min`: True

---

### `IssueConsumptionLineFormSet`

**توضیح**: Formset برای ردیف‌های حواله مصرف.

**Type**: `inlineformset_factory(IssueConsumption, IssueConsumptionLine, ...)`

**Configuration**:
- `form`: `IssueConsumptionLineForm`
- `formset`: `BaseLineFormSet`
- `extra`: 1
- `can_delete`: True
- `min_num`: 1
- `validate_min`: True

---

### `IssueConsignmentLineFormSet`

**توضیح**: Formset برای ردیف‌های حواله امانی.

**Type**: `inlineformset_factory(IssueConsignment, IssueConsignmentLine, ...)`

**Configuration**:
- `form`: `IssueConsignmentLineForm`
- `formset`: `BaseLineFormSet`
- `extra`: 1
- `can_delete`: True
- `min_num`: 1
- `validate_min`: True

---

## وابستگی‌ها

- `inventory.models`: تمام مدل‌های issue و line
- `inventory.forms.base`: `IssueBaseForm`, `BaseLineFormSet`, `UNIT_CHOICES`, `generate_document_code`
- `inventory.services.serials`: `serial_service` برای مدیریت سریال‌ها
- `inventory.inventory_balance`: برای محاسبه موجودی
- `shared.models`: `CompanyUnit`
- `shared.utils.modules`: `get_work_line_model()` برای production module
- `decimal.Decimal`: برای محاسبات دقیق
- `collections.deque`: برای BFS در محاسبه unit factor

---

## استفاده در پروژه

این forms در views ماژول inventory استفاده می‌شوند:
- `IssuePermanentCreateView`, `IssuePermanentUpdateView`
- `IssueConsumptionCreateView`, `IssueConsumptionUpdateView`
- `IssueConsignmentCreateView`, `IssueConsignmentUpdateView`
- Serial assignment views

---

## نکات مهم

1. **Inventory Balance Validation**: تمام issue line forms موجودی را قبل از حواله بررسی می‌کنند
2. **Unit Conversion**: تمام forms از `_get_unit_factor()` برای تبدیل واحد استفاده می‌کنند
3. **Entered Values**: مقادیر وارد شده (`entered_unit`, `entered_quantity`) حفظ می‌شوند
4. **Warehouse Validation**: انبار باید در لیست انبارهای مجاز کالا باشد
5. **Destination Handling**: 
   - `IssuePermanentLineForm`: فقط CompanyUnit
   - `IssueConsumptionLineForm`: CompanyUnit یا WorkLine (اگر production module نصب باشد)
   - `IssueConsignmentLineForm`: فقط CompanyUnit
6. **Serial Assignment**: فقط برای کالاهای با `has_lot_tracking=1`
7. **Company Filtering**: تمام querysets بر اساس `company_id` فیلتر می‌شوند
8. **Production Module Integration**: `IssueConsumptionLineForm` از `WorkLine` استفاده می‌کند اگر production module نصب باشد
9. **Item Filtering and Search**: تمام issue line forms از فیلتر و جستجوی کالا پشتیبانی می‌کنند:
   - فیلتر بر اساس نوع کالا (`item_type`)
   - فیلتر بر اساس دسته‌بندی (`category`)
   - فیلتر بر اساس زیر دسته‌بندی (`subcategory`)
   - جستجو در نام و کد کالا (`item_search`)
   - فیلترها و جستجو از طریق API endpoint `/inventory/api/filtered-items/` در template اعمال می‌شوند
   - فیلترها اختیاری هستند و می‌توانند به صورت ترکیبی استفاده شوند

