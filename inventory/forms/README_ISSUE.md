# inventory/forms/issue.py - Issue Forms

**هدف**: Forms برای مدیریت حواله‌ها (Issues) در ماژول inventory

این فایل شامل forms برای:
- Permanent Issues (حواله‌های دائم)
- Consumption Issues (حواله‌های مصرف)
- Consignment Issues (حواله‌های امانی)
- Warehouse Transfer Issues (حواله‌های انتقال بین انبار)
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
  1. تنظیم `self.line` و `self.company_id` از line
  2. اگر `line.item.has_lot_tracking == 1`:
     - ساخت base queryset: `ItemSerial.objects.filter(company_id=company_id, item=line.item, current_warehouse=line.warehouse)`
     - **فیلتر status**:
       - شامل: `AVAILABLE` یا `RESERVED` که متعلق به این line خاص باشد (`current_document_type=line_class_name`, `current_document_id=line_pk`)
       - حذف: `ISSUED`, `CONSUMED`, `DAMAGED`, `RETURNED`
       - حذف: `RESERVED` که متعلق به line های دیگر باشد
     - مرتب‌سازی: `serial_code`
     - تنظیم `initial['serials']` از `line.serials.values_list('pk', flat=True)`
     - محاسبه `required` از `int(Decimal(line.quantity))`
     - تنظیم `help_text` با تعداد مورد نیاز
  3. اگر `has_lot_tracking != 1`:
     - تنظیم `help_text` به "This item does not require serial tracking."
     - تبدیل widget به `HiddenInput`

#### `clean_serials(self) -> list`
- **Returns**: لیست سریال‌های اعتبارسنجی شده
- **Logic**:
  1. دریافت serials از `cleaned_data`
  2. بررسی `item.has_lot_tracking == 1`:
     - اگر نباشد، بازگشت `ItemSerial.objects.none()`
  3. **بررسی quantity**:
     - تبدیل `line.quantity` به `int(Decimal(quantity))`
     - اگر quantity عدد صحیح نباشد، ValidationError
     - بررسی `Decimal(quantity) == Decimal(int(quantity))` (باید دقیقاً عدد صحیح باشد)
  4. **بررسی تعداد serials**:
     - `required = int(Decimal(line.quantity))`
     - اگر `len(selected) != required`: ValidationError با پیام تعداد دقیق مورد نیاز
  5. **بررسی item consistency**:
     - بررسی اینکه تمام serials متعلق به همان item باشند (`serial.item_id == item.id`)
     - اگر serials متعلق به item دیگری باشند، ValidationError
  6. بازگشت serials

#### `save(self, user=None)`
- **Parameters**: `user` برای لاگ کردن تغییرات
- **Logic**:
  1. اگر `line.item.has_lot_tracking == 1`:
     - دریافت `previous_serial_ids` از `line.serials.values_list('id', flat=True)`
     - دریافت `selected_serials` از `cleaned_data.get('serials')`
     - تنظیم serials: `line.serials.set(selected_serials)`
     - فراخوانی `serial_service.sync_issue_line_serials(line, previous_serial_ids, user=user)` برای به‌روزرسانی وضعیت سریال‌ها
  2. اگر `has_lot_tracking != 1`:
     - پاک کردن serials: `line.serials.clear()`
  3. بازگشت line

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
  1. تنظیم `self.company_id` از parameter یا instance
  2. Initialize helper variables: `_unit_factor`, `_entered_unit_value`, `_entered_quantity_value`
  3. اگر `company_id` موجود باشد:
     - **فیلتر `item` queryset**:
       - Base: `Item.objects.filter(company_id=company_id, is_enabled=1)`
       - در حالت edit: اضافه کردن item فعلی حتی اگر disabled باشد (`Q(is_enabled=1) | Q(pk=instance.item_id)`)
       - مرتب‌سازی: `name`
       - تنظیم `label_from_instance`
     - **فیلتر `warehouse` queryset**:
       - تلاش برای دریافت item از instance
       - اگر item موجود باشد: استفاده از `_set_warehouse_queryset(item)` (بر اساس allowed warehouses)
       - در غیر این صورت: fallback به تمام warehouse های company (enabled)
       - در حالت edit: اضافه کردن warehouse فعلی حتی اگر disabled باشد
       - تنظیم `label_from_instance`
  4. **تنظیم unit choices**: فراخوانی `_set_unit_choices()` (قبل از restore values)
  5. **Restore entered values در حالت edit** (اگر form unbound باشد و instance دارای pk باشد):
     - دریافت item از `item_id` (با error handling برای جلوگیری از RelatedObjectDoesNotExist)
     - اگر item موجود باشد:
       - تنظیم unit choices بر اساس item: `_set_unit_choices(item=item)`
       - تنظیم warehouse queryset: `_set_warehouse_queryset(item=item)`
     - **Restore unit**:
       - دریافت `entry_unit` از `entered_unit` یا `unit` (اولویت با `entered_unit`)
       - اگر unit در choices موجود نباشد، اضافه کردن به choices
       - تنظیم `instance.unit = entry_unit` برای display (ذخیره original unit در `_original_unit`)
       - تنظیم `initial['unit'] = entry_unit`
     - **Restore quantity**:
       - اگر `entered_quantity` موجود باشد: `initial['quantity'] = entered_quantity`

#### `clean_item(self) -> Optional[Item]`
- **Returns**: Item اعتبارسنجی شده
- **Logic**:
  1. دریافت `item` از `cleaned_data`
  2. اگر item موجود باشد:
     - به‌روزرسانی unit choices: `_set_unit_choices(item=item)` (قبل از unit validation)
     - به‌روزرسانی warehouse queryset: `_set_warehouse_queryset(item=item)` (بر اساس allowed warehouses)
  3. بازگشت item

#### `clean_warehouse(self) -> Optional[Warehouse]`
- **Returns**: Warehouse اعتبارسنجی شده
- **Logic**:
  1. دریافت `warehouse` و `item` از `cleaned_data`
  2. اگر هر دو موجود باشند:
     - دریافت allowed warehouses از `_get_item_allowed_warehouses(item)`
     - اگر allowed warehouses موجود باشند:
       - بررسی اینکه `warehouse.id` در allowed warehouses باشد
       - اگر نباشد، ValidationError
     - اگر allowed warehouses موجود نباشند:
       - ValidationError (کالا باید حداقل یک انبار مجاز داشته باشد)
  3. بازگشت warehouse

#### `clean_unit(self) -> str`
- **Returns**: واحد اعتبارسنجی شده
- **Logic**:
  1. دریافت `unit` از `cleaned_data`
  2. دریافت `item` از `cleaned_data` (باید قبلاً در `clean_item` cleaned شده باشد)
  3. اگر item موجود نباشد، بازگشت unit (validation skip می‌شود)
  4. به‌روزرسانی unit choices: `_set_unit_choices(item=item)`
  5. دریافت allowed units از `_get_item_allowed_units(item)`
  6. اضافه کردن `item.default_unit` به allowed units
  7. اضافه کردن unit choices از field به allowed units
  8. اگر unit موجود باشد و در allowed units نباشد، ValidationError
  9. بازگشت unit

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  1. فراخوانی `super().clean()`
  2. **بررسی form empty** (برای inline formsets):
     - اگر `item` موجود نباشد، بازگشت `cleaned_data` (form خالی skip می‌شود)
  3. **اعتبارسنجی warehouse**:
     - دریافت `warehouse` و `item` از `cleaned_data`
     - اگر هر دو موجود باشند:
       - دریافت allowed warehouses از `_get_item_allowed_warehouses(item)`
       - اگر allowed warehouses موجود باشند:
         - بررسی اینکه `warehouse.id` در allowed warehouses باشد
         - اگر نباشد، ValidationError
       - اگر allowed warehouses موجود نباشند:
         - ValidationError (کالا باید حداقل یک انبار مجاز داشته باشد)
  4. **اعتبارسنجی و normalize واحد**: فراخوانی `_validate_unit(cleaned_data)`
  5. **Normalize quantity**: فراخوانی `_normalize_quantity(cleaned_data)`
  6. **اعتبارسنجی موجودی** (فقط برای issue line forms):
     - بررسی اینکه form برای issue line باشد (بررسی model class)
     - اگر `warehouse`, `item`, `company_id`, و `quantity` موجود باشند:
       - محاسبه موجودی فعلی با `inventory_balance.calculate_item_balance(company_id, warehouse_id, item_id, as_of_date=today)`
       - **در حالت edit**: اضافه کردن `old_quantity` به `current_balance` → `available_balance = current_balance + old_quantity`
       - **در حالت create**: `available_balance = current_balance`
       - بررسی `issue_quantity > available_balance`:
         - اگر بیشتر باشد، ValidationError با پیام موجودی ناکافی
     - اگر محاسبه موجودی خطا بدهد (مثلاً baseline موجود نباشد)، خطا ignore می‌شود
  7. بازگشت `cleaned_data`

#### `save(self, commit: bool = True)`
- **Returns**: instance ذخیره شده
- **Logic**:
  1. فراخوانی `super().save(commit=False)`
  2. **ذخیره entered_unit**:
     - اولویت: `_entered_unit_value` → `instance.entered_unit` → `instance.unit`
     - تنظیم `instance.entered_unit`
  3. **ذخیره entered_quantity**:
     - اگر `_entered_quantity_value` موجود باشد: `instance.entered_quantity = _entered_quantity_value`
     - در غیر این صورت، اگر `entered_quantity` None باشد: `instance.entered_quantity = instance.quantity`
  4. اگر `commit=True`: ذخیره instance و `save_m2m()`
  5. بازگشت instance

**Helper Methods**:

#### `_get_item_allowed_warehouses(self, item: Optional[Item]) -> list`
- **Returns**: لیست dicts با `{'value': warehouse_id, 'label': 'code - name'}`
- **Logic**:
  - دریافت relations از `item.warehouses.select_related('warehouse')`
  - فیلتر فقط warehouse های enabled
  - **نکته مهم**: اگر هیچ warehouse تنظیم نشده باشد، لیست خالی برمی‌گرداند (strict enforcement - کالا نمی‌تواند در هیچ انباری باشد)

#### `_set_warehouse_queryset(self, item: Optional[Item] = None) -> None`
- **Logic**:
  1. اگر item موجود نباشد، از `_resolve_item()` استفاده می‌کند
  2. اگر item موجود باشد:
     - دریافت allowed warehouse IDs از `_get_item_allowed_warehouses(item)`
     - اگر allowed IDs موجود باشند:
       - فیلتر queryset به فقط allowed warehouses (enabled)
       - در حالت edit: اضافه کردن warehouse فعلی حتی اگر disabled باشد
     - اگر allowed IDs موجود نباشند:
       - در حالت edit: فقط warehouse فعلی
       - در غیر این صورت: queryset خالی
  3. Fallback (اگر item موجود نباشد):
     - تمام warehouse های company (enabled)
     - در حالت edit: اضافه کردن warehouse فعلی حتی اگر disabled باشد

#### `_resolve_item(self, candidate: Any = None) -> Optional[Item]`
- **Returns**: Item instance یا None
- **Logic** (اولویت):
  1. اگر `candidate` یک Item instance باشد، بازگشت آن
  2. اگر `candidate` یک ID باشد، دریافت از database
  3. بررسی form data (POST) برای key با suffix `-item`
  4. بررسی instance (برای edit mode): `instance.item_id`
  5. بررسی initial data (برای new forms با pre-selected item)
  6. در غیر این صورت، None

#### `_get_item_allowed_units(self, item: Optional[Item]) -> list`
- **Returns**: لیست dicts با `{'value': unit_code, 'label': unit_label}`
- **Logic**:
  1. اگر item موجود نباشد، لیست خالی
  2. اضافه کردن `item.default_unit` و `item.primary_unit`
  3. اضافه کردن units از `ItemUnit` conversions (`from_unit`, `to_unit`)
  4. Mapping به labels از `UNIT_CHOICES`
  5. بازگشت لیست unique units

#### `_set_unit_choices(self, item: Optional[Item] = None) -> None`
- **Logic**:
  1. اگر item موجود نباشد، از `_resolve_item()` استفاده می‌کند
  2. دریافت current unit از instance (در edit mode) یا cleaned_data
  3. اگر item موجود باشد:
     - دریافت allowed units از `_get_item_allowed_units(item)`
     - اگر current unit در allowed units نباشد، اضافه کردن به choices
     - اگر هیچ unit موجود نباشد، اضافه کردن `default_unit` به عنوان fallback
     - تنظیم choices: `[placeholder] + allowed`
  4. اگر item موجود نباشد:
     - اگر current unit موجود باشد، اضافه کردن به choices
     - در غیر این صورت، فقط placeholder

#### `_get_unit_factor(self, item: Item, unit_code: str) -> Decimal`
- **Returns**: فاکتور تبدیل از `unit_code` به `item.default_unit`
- **Logic** (BFS):
  1. اگر `unit_code == default_unit`، بازگشت `1`
  2. ساخت graph از `ItemUnit` conversions (bidirectional)
  3. BFS از `unit_code` به `default_unit`
  4. محاسبه cumulative factor
  5. اگر path پیدا نشود، بازگشت `1`

#### `_validate_unit(self, cleaned_data: Dict[str, Any]) -> None`
- **Logic**:
  1. Initialize `_unit_factor = 1`
  2. دریافت item از `_resolve_item()`
  3. دریافت unit از `cleaned_data` یا `item.default_unit`
  4. دریافت allowed units و اضافه کردن `default_unit`
  5. اگر unit در allowed units نباشد، ValidationError
  6. محاسبه factor: `_get_unit_factor(item, unit)`
  7. ذخیره `_entered_unit_value = unit`
  8. تنظیم `cleaned_data['unit'] = item.default_unit` (normalize به base unit)

#### `_normalize_quantity(self, cleaned_data: Dict[str, Any]) -> None`
- **Logic**:
  1. دریافت item و quantity از `cleaned_data`
  2. اگر item یا quantity موجود نباشد، return
  3. دریافت `_unit_factor` از `_validate_unit()`
  4. تبدیل quantity به Decimal
  5. ذخیره `_entered_quantity_value = quantity` (original value)
  6. محاسبه normalized quantity: `quantity * factor`
  7. تنظیم `cleaned_data['quantity'] = normalized_quantity` (به base unit)

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

### `IssueWarehouseTransferForm`

**توضیح**: فرم هدر برای حواله‌های انتقال بین انبار با پشتیبانی multi-line.

**Type**: `forms.ModelForm`

**Model**: `IssueWarehouseTransfer`

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
  2. تولید `document_code` با prefix "IWT" اگر خالی باشد (با `generate_document_code()`)
  3. تنظیم `document_date` به امروز اگر خالی باشد
  4. اگر `commit=True`: ذخیره instance
  5. بازگشت instance

---

### `IssueWarehouseTransferLineForm`

**توضیح**: فرم برای ردیف‌های حواله انتقال بین انبار.

**Type**: `IssueLineBaseForm`

**Model**: `IssueWarehouseTransferLine`

**Custom Fields**:
- `source_warehouse`: انبار مبدأ (ModelChoiceField)
- `destination_warehouse`: انبار مقصد (ModelChoiceField)

**Fields**:
- تمام fields از `IssueLineBaseForm` (به جز `warehouse` که حذف می‌شود)
- `source_warehouse`, `destination_warehouse`
- `item`, `unit`, `quantity`
- `entered_unit`, `entered_quantity`
- `line_notes`

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`
- **Parameters**: `company_id` برای فیلتر کردن querysets
- **Logic**:
  1. فراخوانی `super().__init__()` با `company_id`
  2. **حذف field `warehouse`** از parent (از `source_warehouse` و `destination_warehouse` استفاده می‌شود)
  3. اگر `company_id` موجود باشد:
     - **تنظیم `source_warehouse` queryset**:
       - اگر item موجود باشد: فیلتر بر اساس `item.allowed_warehouses`
       - در غیر این صورت: تمام warehouse های company (enabled)
       - در حالت edit: اضافه کردن warehouse فعلی حتی اگر disabled باشد
     - **تنظیم `destination_warehouse` queryset**:
       - مشابه `source_warehouse` (بر اساس `item.allowed_warehouses`)
       - در حالت edit: اضافه کردن warehouse فعلی حتی اگر disabled باشد
     - تنظیم `label_from_instance` برای هر دو warehouse

#### `clean_source_warehouse(self) -> Optional[Warehouse]`
- **Returns**: Warehouse اعتبارسنجی شده
- **Logic**:
  1. دریافت `source_warehouse` و `item` از `cleaned_data`
  2. اگر هر دو موجود باشند:
     - دریافت allowed warehouses از `_get_item_allowed_warehouses(item)`
     - اگر allowed warehouses موجود باشند:
       - بررسی اینکه `source_warehouse.id` در allowed warehouses باشد
       - اگر نباشد، ValidationError
     - اگر allowed warehouses موجود نباشند، ValidationError (کالا باید حداقل یک انبار مجاز داشته باشد)
  3. بازگشت `source_warehouse`

#### `clean_destination_warehouse(self) -> Optional[Warehouse]`
- **Returns**: Warehouse اعتبارسنجی شده
- **Logic**:
  1. دریافت `destination_warehouse` و `item` از `cleaned_data`
  2. اگر هر دو موجود باشند:
     - دریافت allowed warehouses از `_get_item_allowed_warehouses(item)`
     - اگر allowed warehouses موجود باشند:
       - بررسی اینکه `destination_warehouse.id` در allowed warehouses باشد
       - اگر نباشد، ValidationError
     - اگر allowed warehouses موجود نباشند، ValidationError (کالا باید حداقل یک انبار مجاز داشته باشد)
  3. بازگشت `destination_warehouse`

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  1. فراخوانی `super().clean()` (که موجودی را بررسی می‌کند)
  2. اگر form خالی باشد (برای inline formsets)، بازگشت `cleaned_data`
  3. دریافت `item`, `source_warehouse`, `destination_warehouse` از `cleaned_data`
  4. **بررسی اینکه source و destination متفاوت باشند**:
     - اگر `source_warehouse.id == destination_warehouse.id`: ValidationError
  5. **اعتبارسنجی destination warehouse**:
     - بررسی اینکه در allowed warehouses باشد
     - اگر نباشد، ValidationError
  6. **اعتبارسنجی موجودی در source warehouse**:
     - محاسبه موجودی با `inventory_balance.calculate_item_balance()` برای `source_warehouse`
     - در حالت edit: اضافه کردن quantity قدیمی به موجودی
     - اگر `issue_quantity > available_balance`: ValidationError با پیام موجودی ناکافی
  7. بازگشت `cleaned_data`

#### `save(self, commit: bool = True)`
- **Returns**: instance ذخیره شده
- **Logic**:
  1. فراخوانی `super().save(commit=False)`
  2. **تنظیم `warehouse` به `source_warehouse`** (برای compatibility با `IssueLineBase`):
     - `instance.warehouse = source_warehouse`
     - `instance.warehouse_code = source_warehouse.public_code`
  3. **تنظیم `source_warehouse`**:
     - `instance.source_warehouse = source_warehouse`
     - `instance.source_warehouse_code = source_warehouse.public_code`
  4. **تنظیم `destination_warehouse`**:
     - `instance.destination_warehouse = destination_warehouse`
     - `instance.destination_warehouse_code = destination_warehouse.public_code`
  5. **ذخیره entered values**:
     - `entered_unit` از `_entered_unit_value` یا instance
     - `entered_quantity` از `_entered_quantity_value` یا instance
  6. اگر `commit=True`: ذخیره instance و `save_m2m()`
  7. بازگشت instance

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

### `IssueWarehouseTransferLineFormSet`

**توضیح**: Formset برای ردیف‌های حواله انتقال بین انبار.

**Type**: `inlineformset_factory(IssueWarehouseTransfer, IssueWarehouseTransferLine, ...)`

**Configuration**:
- `form`: `IssueWarehouseTransferLineForm`
- `formset`: `BaseLineFormSet`
- `extra`: 1
- `can_delete`: True
- `min_num`: 1
- `validate_min`: True

---

## وابستگی‌ها

- `inventory.models`: تمام مدل‌های issue و line (`IssuePermanent`, `IssueConsumption`, `IssueConsignment`, `IssueWarehouseTransfer`, و line models مربوطه)
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
- `IssueWarehouseTransferCreateView`, `IssueWarehouseTransferUpdateView`
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
   - `IssueWarehouseTransferLineForm`: دو انبار (source_warehouse و destination_warehouse) - source و destination باید متفاوت باشند
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

