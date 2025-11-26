# inventory/forms/receipt.py - Receipt Forms

**هدف**: Forms برای مدیریت رسیدها (Receipts) در ماژول inventory

این فایل شامل forms برای:
- Temporary Receipts (رسیدهای موقت)
- Permanent Receipts (رسیدهای دائم)
- Consignment Receipts (رسیدهای امانی)
- Line Forms و Formsets برای هر نوع رسید

---

## Header Forms (فرم‌های هدر)

### `ReceiptTemporaryForm`

**توضیح**: فرم هدر برای رسیدهای موقت با پشتیبانی multi-line.

**Type**: `forms.ModelForm`

**Model**: `ReceiptTemporary`

**Fields**:
- `document_code`: کد سند (HiddenInput، auto-generated)
- `document_date`: تاریخ سند (HiddenInput، auto-generated)
- `expected_receipt_date`: تاریخ مورد انتظار تبدیل (JalaliDateInput)
- `supplier`: تامین‌کننده (Select)
- `source_document_type`: نوع سند مبدا (TextInput)
- `source_document_code`: کد سند مبدا (TextInput)
- `status`: وضعیت (HiddenInput)
- `qc_approval_notes`: یادداشت‌های تایید QC (Textarea)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال برای فیلتر کردن querysets
- **Logic**:
  - فیلتر کردن querysets بر اساس `company_id`
  - تنظیم `document_code` و `document_date` به صورت hidden و auto-generated
  - تنظیم `status` به `DRAFT` برای رسیدهای جدید

#### `_filter_company_scoped_fields(self) -> None`
- **Logic**: فیلتر کردن queryset `supplier` بر اساس `company_id`

#### `clean_document_code(self) -> str`
- **Returns**: کد سند (خالی اگر باید auto-generate شود)
- **Logic**: اگر کد سند خالی باشد، در `save()` تولید می‌شود

#### `clean_document_date(self)`
- **Returns**: تاریخ سند (امروز به صورت پیش‌فرض)
- **Logic**: اگر تاریخ خالی باشد، تاریخ امروز را برمی‌گرداند

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  - اطمینان از وجود `document_code` و `document_date`
  - بررسی تطابق `supplier` با `company_id`

#### `save(self, commit: bool = True)`
- **Parameters**:
  - `commit`: آیا instance ذخیره شود یا نه
- **Returns**: instance ذخیره شده
- **Logic**:
  - تولید `document_code` با prefix "TMP" اگر خالی باشد
  - تنظیم `document_date` به امروز اگر خالی باشد
  - تنظیم `status` به `DRAFT` اگر تنظیم نشده باشد

---

### `ReceiptPermanentForm`

**توضیح**: فرم هدر برای رسیدهای دائم با پشتیبانی multi-line.

**Type**: `forms.ModelForm`

**Model**: `ReceiptPermanent`

**Fields**:
- `document_code`: کد سند (HiddenInput، auto-generated)
- `document_date`: تاریخ سند (HiddenInput، auto-generated)
- `temporary_receipt`: رسید موقت مرتبط (Select، فقط رسیدهای QC-approved و unconverted)
- `purchase_request`: درخواست خرید مرتبط (Select)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال
- **Logic**:
  - فیلتر کردن `temporary_receipt` به فقط رسیدهای QC-approved و unconverted
  - فیلتر کردن `purchase_request` بر اساس `company_id`

#### `clean_document_code(self) -> str`
- **Returns**: کد سند (خالی اگر باید auto-generate شود)

#### `clean_document_date(self)`
- **Returns**: تاریخ سند (امروز به صورت پیش‌فرض)

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  - بررسی تطابق `temporary_receipt` و `purchase_request` با `company_id`

#### `save(self, commit: bool = True)`
- **Returns**: instance ذخیره شده
- **Logic**:
  - تولید `document_code` با prefix "PRM" اگر خالی باشد
  - تنظیم `requires_temporary_receipt` بر اساس انتخاب `temporary_receipt`
  - اگر `temporary_receipt` انتخاب شده باشد:
    - قفل کردن رسید موقت (`is_locked=1`)
    - علامت‌گذاری به عنوان تبدیل شده (`is_converted=1`)
    - تنظیم `converted_receipt` و `converted_receipt_code`

---

### `ReceiptConsignmentForm`

**توضیح**: فرم هدر برای رسیدهای امانی با پشتیبانی multi-line.

**Type**: `forms.ModelForm`

**Model**: `ReceiptConsignment`

**Fields**:
- `document_code`: کد سند (HiddenInput، auto-generated)
- `document_date`: تاریخ سند (HiddenInput، auto-generated)
- `consignment_contract_code`: کد قرارداد امانی (TextInput)
- `expected_return_date`: تاریخ مورد انتظار برگشت (JalaliDateInput)
- `valuation_method`: روش ارزش‌گذاری (TextInput)
- `requires_temporary_receipt`: نیاز به رسید موقت (CheckboxInput)
- `temporary_receipt`: رسید موقت مرتبط (Select)
- `purchase_request`: درخواست خرید مرتبط (Select)
- `warehouse_request`: درخواست انبار مرتبط (Select)
- `ownership_status`: وضعیت مالکیت (TextInput)
- `conversion_receipt`: رسید تبدیل مرتبط (Select)
- `conversion_date`: تاریخ تبدیل (JalaliDateInput)
- `return_document_id`: شناسه سند برگشت (NumberInput)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال
- **Logic**:
  - فیلتر کردن تمام foreign key fields بر اساس `company_id`
  - تنظیم `requires_temporary_receipt` از instance اگر در حالت edit باشد

#### `clean_document_code(self) -> str`
- **Returns**: کد سند (خالی اگر باید auto-generate شود)

#### `clean_document_date(self)`
- **Returns**: تاریخ سند (امروز به صورت پیش‌فرض)

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی شده
- **Logic**:
  - بررسی تطابق تمام foreign key fields با `company_id`

#### `save(self, commit: bool = True)`
- **Returns**: instance ذخیره شده
- **Logic**:
  - تولید `document_code` با prefix "CNG" اگر خالی باشد

---

## Base Line Form

### `ReceiptLineBaseForm`

**توضیح**: کلاس پایه برای فرم‌های خطی رسیدها.

**Type**: `forms.ModelForm` (abstract)

**Custom Fields**:
- `unit`: واحد اندازه‌گیری (ChoiceField)
- `entered_price_unit`: واحد قیمت وارد شده (CharField، اختیاری)

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`
- **Parameters**:
  - `company_id`: شناسه شرکت فعال
- **Logic**:
  - فیلتر کردن querysets برای `item`, `warehouse`, `supplier` بر اساس `company_id`
  - تنظیم unit choices از `UNIT_CHOICES`
  - بازیابی مقادیر `entered_unit`, `entered_quantity`, `entered_unit_price` در حالت edit

#### `_set_unit_choices_for_item(self, item: Optional[Item]) -> None`
- **Parameters**:
  - `item`: کالای انتخاب شده
- **Logic**:
  - تنظیم unit choices بر اساس واحدهای مجاز کالا
  - اضافه کردن واحد فعلی به choices اگر وجود نداشته باشد

#### `clean_item(self) -> Optional[Item]`
- **Returns**: کالای اعتبارسنجی شده
- **Logic**:
  - به‌روزرسانی warehouse queryset بر اساس انبارهای مجاز کالا

#### `clean_warehouse(self) -> Optional[Warehouse]`
- **Returns**: انبار اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه انبار انتخاب شده در لیست انبارهای مجاز کالا باشد
  - اگر کالا هیچ انبار مجازی نداشته باشد، خطا می‌دهد

#### `clean_unit(self) -> str`
- **Returns**: واحد اعتبارسنجی شده
- **Logic**:
  - بررسی اینکه واحد انتخاب شده در لیست واحدهای مجاز کالا باشد

#### `_get_item_allowed_warehouses(self, item: Optional[Item]) -> list`
- **Parameters**:
  - `item`: کالا
- **Returns**: لیست دیکشنری‌های `{'value': warehouse_id, 'label': warehouse_name}`
- **Logic**:
  - دریافت انبارهای مجاز کالا از رابطه `item.warehouses`
  - اگر هیچ انباری تنظیم نشده باشد، لیست خالی برمی‌گرداند (کالا نمی‌تواند دریافت شود)

#### `_set_warehouse_queryset(self, item: Optional[Item] = None) -> None`
- **Parameters**:
  - `item`: کالا (اگر None باشد، از `_resolve_item()` دریافت می‌شود)
- **Logic**:
  - تنظیم warehouse queryset بر اساس انبارهای مجاز کالا
  - اگر کالا هیچ انبار مجازی نداشته باشد، queryset خالی می‌شود

#### `_resolve_item(self, candidate: Any = None) -> Optional[Item]`
- **Parameters**:
  - `candidate`: کاندید کالا (می‌تواند Item instance، ID، یا None باشد)
- **Returns**: Item instance یا None
- **Logic**:
  - تلاش برای resolve کردن کالا از:
    1. `candidate` (اگر Item instance باشد)
    2. `candidate` (اگر ID باشد)
    3. POST data (از form data)
    4. instance (در حالت edit)
    5. initial data (در حالت create با pre-selected item)

#### `_get_item_allowed_units(self, item: Optional[Item]) -> list`
- **Parameters**:
  - `item`: کالا
- **Returns**: لیست دیکشنری‌های `{'value': unit_code, 'label': unit_label}`
- **Logic**:
  - جمع‌آوری واحدهای مجاز از:
    - `item.default_unit`
    - `item.primary_unit`
    - واحدهای از `ItemUnit` conversions (`from_unit`, `to_unit`)

#### `_get_unit_factor(self, item: Item, unit_code: str) -> Decimal`
- **Parameters**:
  - `item`: کالا
  - `unit_code`: کد واحد
- **Returns**: فاکتور تبدیل از `unit_code` به `item.default_unit`
- **Logic**:
  - استفاده از BFS (Breadth-First Search) برای پیدا کردن مسیر تبدیل واحد
  - ساخت graph از `ItemUnit` conversions
  - محاسبه فاکتور تبدیل با ضرب فاکتورهای مسیر

#### `_validate_unit(self, cleaned_data: Dict[str, Any]) -> None`
- **Parameters**:
  - `cleaned_data`: داده‌های تمیز شده
- **Logic**:
  - بررسی اینکه واحد انتخاب شده در لیست واحدهای مجاز باشد
  - محاسبه `_unit_factor` برای تبدیل واحد
  - ذخیره `_entered_unit_value`
  - تنظیم `cleaned_data['unit']` به `item.default_unit`

#### `_normalize_quantity(self, cleaned_data: Dict[str, Any]) -> None`
- **Parameters**:
  - `cleaned_data`: داده‌های تمیز شده
- **Logic**:
  - تبدیل quantity از واحد وارد شده به `item.default_unit`
  - ذخیره `_entered_quantity_value` (مقدار وارد شده)
  - تنظیم `cleaned_data['quantity']` به مقدار normalized
  - تنظیم `cleaned_data['unit']` و `instance.unit` به `item.default_unit`

#### `_normalize_price(self, cleaned_data: Dict[str, Any]) -> None`
- **Parameters**:
  - `cleaned_data`: داده‌های تمیز شده
- **Logic**:
  - تبدیل قیمت از واحد وارد شده (`entered_price_unit` یا `entered_unit`) به `item.default_unit`
  - **مهم**: برای قیمت، از معکوس فاکتور quantity استفاده می‌شود
  - مثال: اگر 1 BOX = 1000 EA، قیمت 100000 per BOX = 100 per EA (تقسیم بر 1000)
  - ذخیره `_entered_unit_price_value`
  - تنظیم `cleaned_data['unit_price']` و `cleaned_data['unit_price_estimate']` به مقادیر normalized

#### `clean_entered_price_unit(self) -> str`
- **Returns**: واحد قیمت وارد شده
- **Logic**:
  - بررسی اینکه `entered_price_unit` در لیست واحدهای مجاز باشد (اختیاری)

#### `clean(self) -> Dict[str, Any]`
- **Returns**: `cleaned_data` اعتبارسنجی و normalized شده
- **Logic**:
  - فراخوانی `_validate_unit()`
  - فراخوانی `_normalize_quantity()`
  - فراخوانی `_normalize_price()`

#### `save(self, commit: bool = True)`
- **Parameters**:
  - `commit`: آیا instance ذخیره شود یا نه
- **Returns**: instance ذخیره شده
- **Logic**:
  - ذخیره `entered_unit`, `entered_quantity`, `entered_unit_price`, `entered_price_unit` در instance
  - اگر `entered_price_unit` خالی باشد، از `entered_unit` استفاده می‌شود

---

## Line Forms (فرم‌های خطی)

### `ReceiptPermanentLineForm`

**توضیح**: فرم برای ردیف‌های رسید دائم.

**Type**: `ReceiptLineBaseForm`

**Model**: `ReceiptPermanentLine`

**Fields**:
- تمام fields از `ReceiptLineBaseForm`
- `supplier`: تامین‌کننده (Select)
- `unit_price`: قیمت واحد (NumberInput)
- `currency`: ارز (Select)
- `tax_amount`: مبلغ مالیات (NumberInput)
- `discount_amount`: مبلغ تخفیف (NumberInput)
- `total_amount`: مبلغ کل (NumberInput)
- `line_notes`: یادداشت‌های خط (Textarea)

**متدها**:

#### `clean_item(self) -> Optional[Item]`
- **Returns**: کالای اعتبارسنجی شده
- **Logic**:
  - فراخوانی `super().clean_item()`
  - بررسی اینکه کالا نیاز به رسید موقت نداشته باشد (`requires_temporary_receipt != 1`)
  - اگر نیاز به رسید موقت داشته باشد، خطا می‌دهد

---

### `ReceiptConsignmentLineForm`

**توضیح**: فرم برای ردیف‌های رسید امانی.

**Type**: `ReceiptLineBaseForm`

**Model**: `ReceiptConsignmentLine`

**Fields**:
- تمام fields از `ReceiptLineBaseForm`
- `supplier`: تامین‌کننده (Select)
- `unit_price_estimate`: قیمت واحد تخمینی (NumberInput)
- `currency`: ارز (Select)
- `line_notes`: یادداشت‌های خط (Textarea)

---

### `ReceiptTemporaryLineForm`

**توضیح**: فرم برای ردیف‌های رسید موقت.

**Type**: `ReceiptLineBaseForm`

**Model**: `ReceiptTemporaryLine`

**Fields**:
- تمام fields از `ReceiptLineBaseForm`
- `expected_receipt_date`: تاریخ مورد انتظار تبدیل (JalaliDateInput)
- `line_notes`: یادداشت‌های خط (Textarea)

---

## Formsets

### `ReceiptPermanentLineFormSet`

**توضیح**: Formset برای ردیف‌های رسید دائم.

**Type**: `inlineformset_factory(ReceiptPermanent, ReceiptPermanentLine, ...)`

**Configuration**:
- `form`: `ReceiptPermanentLineForm`
- `formset`: `BaseLineFormSet`
- `extra`: 1
- `can_delete`: True
- `min_num`: 1
- `validate_min`: True

---

### `ReceiptConsignmentLineFormSet`

**توضیح**: Formset برای ردیف‌های رسید امانی.

**Type**: `inlineformset_factory(ReceiptConsignment, ReceiptConsignmentLine, ...)`

**Configuration**:
- `form`: `ReceiptConsignmentLineForm`
- `formset`: `BaseLineFormSet`
- `extra`: 1
- `can_delete`: True
- `min_num`: 1
- `validate_min`: True

---

### `ReceiptTemporaryLineFormSet`

**توضیح**: Formset برای ردیف‌های رسید موقت.

**Type**: `inlineformset_factory(ReceiptTemporary, ReceiptTemporaryLine, ...)`

**Configuration**:
- `form`: `ReceiptTemporaryLineForm`
- `formset`: `BaseLineFormSet`
- `extra`: 1
- `can_delete`: True
- `min_num`: 1
- `validate_min`: True

---

## وابستگی‌ها

- `inventory.models`: تمام مدل‌های receipt و line
- `inventory.forms.base`: `ReceiptBaseForm`, `BaseLineFormSet`, `UNIT_CHOICES`, `generate_document_code`
- `inventory.widgets`: `JalaliDateInput`
- `decimal.Decimal`: برای محاسبات دقیق
- `collections.deque`: برای BFS در محاسبه unit factor

---

## استفاده در پروژه

این forms در views ماژول inventory استفاده می‌شوند:
- `ReceiptTemporaryCreateView`, `ReceiptTemporaryUpdateView`
- `ReceiptPermanentCreateView`, `ReceiptPermanentUpdateView`
- `ReceiptConsignmentCreateView`, `ReceiptConsignmentUpdateView`

---

## نکات مهم

1. **Unit Conversion**: تمام forms از `_get_unit_factor()` برای تبدیل واحد استفاده می‌کنند
2. **Price Normalization**: قیمت با معکوس فاکتور quantity تبدیل می‌شود (تقسیم به جای ضرب)
3. **Entered Values**: مقادیر وارد شده (`entered_unit`, `entered_quantity`, `entered_unit_price`) حفظ می‌شوند
4. **Warehouse Validation**: انبار باید در لیست انبارهای مجاز کالا باشد
5. **Temporary Receipt Requirement**: کالاهای با `requires_temporary_receipt=1` نمی‌توانند مستقیماً در رسید دائم اضافه شوند
6. **Company Filtering**: تمام querysets بر اساس `company_id` فیلتر می‌شوند
7. **Item Filtering and Search**: تمام receipt line forms از فیلتر و جستجوی کالا پشتیبانی می‌کنند:
   - فیلتر بر اساس نوع کالا (`item_type`)
   - فیلتر بر اساس دسته‌بندی (`category`)
   - فیلتر بر اساس زیر دسته‌بندی (`subcategory`)
   - جستجو در نام و کد کالا (`item_search`)
   - فیلترها و جستجو از طریق API endpoint `/inventory/api/filtered-items/` در template اعمال می‌شوند
   - فیلترها اختیاری هستند و می‌توانند به صورت ترکیبی استفاده شوند

