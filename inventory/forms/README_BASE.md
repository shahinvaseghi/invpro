# inventory/forms/base.py - Base Forms and Helper Functions (Complete Documentation)

**هدف**: کلاس‌های پایه و توابع کمکی برای فرم‌های ماژول inventory

این فایل شامل:
- Constants (UNIT_CHOICES)
- Helper functions (get_feature_approvers, generate_document_code, get_purchase_request_approvers)
- Base form classes (ReceiptBaseForm, IssueBaseForm, StocktakingBaseForm)
- Base formset class (BaseLineFormSet)

---

## Constants

### `UNIT_CHOICES`

**توضیح**: لیست انتخاب واحدهای اندازه‌گیری

**Type**: `list[tuple[str, str]]`

**محتوا**:
```python
[
    ("", _("--- انتخاب کنید ---")),
    ("EA", _("عدد (EA)")),
    ("KG", _("کیلوگرم (KG)")),
    ("G", _("گرم (G)")),
    ("TON", _("تن")),
    ("L", _("لیتر (L)")),
    ("ML", _("میلی‌لیتر (ML)")),
    ("M", _("متر (M)")),
    ("CM", _("سانتی‌متر (CM)")),
    ("MM", _("میلی‌متر (MM)")),
    ("M2", _("متر مربع (M²)")),
    ("M3", _("متر مکعب (M³)")),
    ("BOX", _("بسته (BOX)")),
    ("CARTON", _("کارتن")),
    ("PAIR", _("جفت")),
    ("ROLL", _("رول")),
    ("SET", _("ست")),
]
```

**استفاده**: در تمام فرم‌های receipt، issue، و stocktaking برای نمایش واحدهای اندازه‌گیری

---

## Helper Functions

### `get_feature_approvers(feature_code: str, company_id: Optional[int]) -> QuerySet[User]`

**توضیح**: لیست کاربرانی که می‌توانند یک feature خاص را approve کنند را برمی‌گرداند.

**پارامترهای ورودی**:
- `feature_code` (str): کد feature permission (مثلاً `"inventory.requests.purchase"`)
- `company_id` (Optional[int]): شناسه شرکت برای فیلتر کردن approvers

**مقدار بازگشتی**:
- `QuerySet[User]`: queryset کاربران با permission approve برای feature مشخص شده

**منطق**:
1. اگر `company_id` وجود ندارد، `User.objects.none()` برمی‌گرداند
2. کاربران را فیلتر می‌کند بر اساس:
   - `is_superuser=True` (superuser ها همیشه می‌توانند approve کنند)
   - یا `company_accesses` با `access_level.permissions` که `resource_code=feature_code` و `can_approve=1` دارد
   - یا `groups.profile.access_levels.permissions` که `resource_code=feature_code` و `can_approve=1` دارد
3. `distinct()` را اعمال می‌کند
4. بر اساس `username`, `first_name`, `last_name` مرتب می‌کند
5. queryset را برمی‌گرداند

**استفاده**:
- در فرم‌های purchase request برای فیلتر کردن `approved_by`
- در فرم‌های stocktaking برای فیلتر کردن `approver`

---

### `get_purchase_request_approvers(company_id: Optional[int]) -> QuerySet[User]`

**توضیح**: لیست کاربرانی که می‌توانند purchase request را approve کنند را برمی‌گرداند.

**پارامترهای ورودی**:
- `company_id` (Optional[int]): شناسه شرکت برای فیلتر کردن approvers

**مقدار بازگشتی**:
- `QuerySet[User]`: queryset کاربران با permission approve برای `inventory.requests.purchase`

**منطق**:
- `get_feature_approvers("inventory.requests.purchase", company_id)` را فراخوانی می‌کند

**استفاده**:
- در فرم‌های purchase request برای فیلتر کردن `approved_by`

---

### `generate_document_code(model: Any, company_id: int, prefix: str) -> str`

**توضیح**: کد سند sequential را برای یک مدل تولید می‌کند.

**فرمت**: `{PREFIX}-{YYYYMM}-{SEQUENCE}`
**مثال**: `PRM-202511-000001`

**پارامترهای ورودی**:
- `model` (Any): کلاس Django model
- `company_id` (int): شناسه شرکت
- `prefix` (str): پیشوند کد سند (مثلاً `"PRM"`, `"TMP"`)

**مقدار بازگشتی**:
- `str`: کد سند تولید شده

**منطق**:
1. تاریخ امروز را از `timezone.now()` دریافت می‌کند
2. `month_year` را به فرمت `YYYYMM` با `strftime("%Y%m")` تولید می‌کند
3. `base` را به فرمت `{prefix}-{month_year}` تولید می‌کند (مثلاً `"PRM-202511"`)
4. آخرین کد سند با این `base` را از database دریافت می‌کند:
   - فیلتر: `company_id=company_id`, `document_code__startswith=base`
   - مرتب‌سازی: `-document_code` (descending)
   - دریافت: `values_list("document_code", flat=True).first()`
5. sequence را از آخرین کد استخراج می‌کند:
   - اگر `last_code` وجود دارد: `int(last_code.split("-")[-1])`
   - در غیر این صورت: `0`
   - اگر خطا در parsing رخ دهد (ValueError, IndexError): `0`
6. sequence را 1 افزایش می‌دهد
7. کد را به فرمت `{base}-{sequence + 1:06d}` برمی‌گرداند (6 رقم با leading zeros)
   - مثال: `"PRM-202511-000001"`, `"PRM-202511-000002"`

**استفاده**:
- در `ReceiptTemporary.save()` برای تولید `document_code`
- در `ReceiptPermanent.save()` برای تولید `document_code`
- در سایر مدل‌های document برای تولید کد sequential

---

## Base Form Classes

### `ReceiptBaseForm(forms.ModelForm)`

**توضیح**: کلاس پایه برای فرم‌های receipt با queryset های company-aware

**Inheritance**: `forms.ModelForm`

**Widgets**:
- `date_widget`: `JalaliDateInput` با `attrs={'class': 'form-control'}`
- `datetime_widget`: `forms.DateTimeInput` با `attrs={'class': 'form-control', 'type': 'datetime-local', 'step': 60}`

**Attributes**:
- `company_id`: `Optional[int]` - شناسه شرکت فعال
- `_unit_factor`: `Decimal` - فاکتور تبدیل واحد (default: `Decimal('1')`)
- `_entered_unit_value`: `Optional[str]` - واحد وارد شده توسط کاربر
- `_entered_quantity_value`: `Optional[Decimal]` - مقدار وارد شده توسط کاربر
- `_entered_unit_price_value`: `Optional[Decimal]` - قیمت واحد وارد شده توسط کاربر

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs) -> None`

**توضیح**: فرم را با company filtering و تنظیمات اولیه initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `**kwargs`: آرگومان‌های keyword (مثلاً `instance`)

**مقدار بازگشتی**: ندارد

**منطق**:
1. `self.company_id` را از `company_id` یا `kwargs.get('instance').company_id` تنظیم می‌کند
2. متغیرهای instance را برای unit conversion تنظیم می‌کند:
   - `self._unit_factor = Decimal('1')`
   - `self._entered_unit_value = None`
   - `self._entered_quantity_value = None`
   - `self._entered_unit_price_value = None`
3. `super().__init__(*args, **kwargs)` را فراخوانی می‌کند
4. فیلد `currency` را تنظیم می‌کند (اگر وجود دارد):
   - widget را به `Select` با `attrs={'class': 'form-control'}` تغییر می‌دهد
   - choices را از `CURRENCY_CHOICES` با یک empty choice در ابتدا تنظیم می‌کند
   - `required=False` می‌کند
5. فیلد `document_date` را تنظیم می‌کند (اگر وجود دارد):
   - widget را به `self.date_widget` (JalaliDateInput) تنظیم می‌کند
   - `required=False` می‌کند
   - اگر instance جدید است (`not instance.pk`)، initial را به `timezone.now().date()` تنظیم می‌کند
   - سپس widget را به `HiddenInput` تغییر می‌دهد
6. فیلد `document_code` را تنظیم می‌کند (اگر وجود دارد):
   - widget را به `HiddenInput` تغییر می‌دهد
   - `required=False` می‌کند
7. اگر `company_id` وجود دارد، `_filter_company_scoped_fields()` را فراخوانی می‌کند
8. `_set_unit_choices()` را فراخوانی می‌کند (باید قبل از restore initial values انجام شود)
9. اگر instance موجود است و فرم bound نیست (`not self.is_bound and instance.pk`):
   - **Restore `entered_unit`**:
     - دریافت `entered_unit` یا `unit` از instance
     - اگر unit در choices نیست، آن را اضافه می‌کند
     - تنظیم `instance.unit = entered_unit` برای display
     - تنظیم `self.initial['unit'] = entered_unit`
   - **Restore `entered_quantity`**: `self.initial['quantity'] = instance.entered_quantity`
   - **Restore `entered_unit_price`**: 
     - `self.initial['unit_price'] = instance.entered_unit_price`
     - یا `self.initial['unit_price_estimate'] = instance.entered_unit_price`
10. فیلدهای تاریخ را تنظیم می‌کند:
    - `expected_return_date`: widget = `self.date_widget`
    - `expected_receipt_date`: widget = `self.date_widget`
    - `conversion_date`: widget = `self.date_widget`
11. دوباره `document_code` را به `HiddenInput` تنظیم می‌کند (برای اطمینان)

---

#### `_filter_company_scoped_fields(self) -> None`

**توضیح**: queryset های فیلدها را بر اساس شرکت فعال فیلتر می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
- برای هر فیلد که وجود دارد:
  - `item`: فیلتر بر اساس `company_id` و `is_enabled=1`، label: `"{name} · {item_code}"`
  - `warehouse`: فیلتر بر اساس `company_id` و `is_enabled=1`، label: `"{name} · {public_code}"`
  - `supplier`: فیلتر بر اساس `company_id` و `is_enabled=1`، label: `"{name} · {public_code}"`
  - `temporary_receipt`: فیلتر بر اساس `company_id`، label: `"{document_code} · {item.name}"`
  - `purchase_request`: فیلتر بر اساس `company_id` و `status=APPROVED`، label: `"{request_code} · {item.name}"`
  - `warehouse_request`: فیلتر بر اساس `company_id` و `request_status='approved'` و `is_locked=1`، label: `"{request_code} · {item.name}"`
  - `conversion_receipt`: فیلتر بر اساس `company_id`، label: `"{document_code} · {item.name}"`

---

#### `_clean_company_match(self, cleaned_data: Dict[str, Any], field_name: str, model_verbose: str) -> None`

**توضیح**: بررسی می‌کند که object انتخاب شده متعلق به شرکت فعال است.

**پارامترهای ورودی**:
- `cleaned_data` (Dict[str, Any]): داده‌های تمیز شده فرم
- `field_name` (str): نام فیلد برای بررسی
- `model_verbose` (str): نام verbose مدل برای پیام خطا

**مقدار بازگشتی**: ندارد

**منطق**:
1. object را از `cleaned_data.get(field_name)` دریافت می‌کند
2. اگر object وجود دارد و `company_id` آن با `self.company_id` برابر نیست:
   - خطا به فرم اضافه می‌کند: `'Selected {model} must belong to the active company.'`

---

#### `_get_item_allowed_units(self, item: Optional[Item]) -> List[Dict[str, str]]`

**توضیح**: لیست واحدهای مجاز برای یک کالا را برمی‌گرداند.

**پارامترهای ورودی**:
- `item` (Optional[Item]): instance کالا

**مقدار بازگشتی**:
- `List[Dict[str, str]]`: لیست dictionaries با `value` (کد واحد) و `label` (نام واحد)

**منطق**:
1. اگر `item` وجود ندارد، لیست خالی برمی‌گرداند
2. لیست کدهای واحد را جمع‌آوری می‌کند:
   - `item.default_unit`
   - `item.primary_unit`
   - `from_unit` و `to_unit` از تمام `ItemUnit` های مربوط به کالا
3. اگر هیچ واحدی پیدا نشد، `'EA'` را به عنوان fallback اضافه می‌کند
4. label ها را از `UNIT_CHOICES` map می‌کند
5. لیست dictionaries را برمی‌گرداند

---

#### `_resolve_item(self, candidate: Any = None) -> Optional[Item]`

**توضیح**: کالا را از داده‌های فرم یا instance resolve می‌کند.

**پارامترهای ورودی**:
- `candidate` (Any, optional): کالای candidate (می‌تواند Item instance یا ID باشد)

**مقدار بازگشتی**:
- `Optional[Item]`: instance کالا یا `None`

**منطق**:
1. اگر `candidate` یک `Item` instance است، آن را برمی‌گرداند
2. اگر `candidate` وجود دارد، سعی می‌کند از database دریافت کند
3. اگر `self.data.get('item')` وجود دارد، سعی می‌کند از database دریافت کند
4. اگر `self.instance.item_id` وجود دارد، `self.instance.item` را برمی‌گرداند
5. اگر `self.initial.get('item')` وجود دارد، سعی می‌کند از database دریافت کند
6. در غیر این صورت `None` برمی‌گرداند

---

#### `_set_unit_choices(self) -> None`

**توضیح**: choices فیلد `unit` را بر اساس کالای انتخاب شده تنظیم می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. فیلد `unit` را از `self.fields.get('unit')` دریافت می‌کند
2. اگر فیلد وجود ندارد، return می‌کند
3. کالا را با `_resolve_item()` دریافت می‌کند
4. اگر کالا وجود دارد:
   - واحدهای مجاز را با `_get_item_allowed_units()` دریافت می‌کند
   - اگر `entered_unit` در instance وجود دارد و در لیست مجاز نیست، آن را اضافه می‌کند
   - choices را تنظیم می‌کند: `[placeholder] + allowed`
5. اگر کالا وجود ندارد:
   - choices را به `[placeholder]` تنظیم می‌کند

---

#### `_get_unit_factor(self, item: Item, unit_code: str) -> Decimal`

**توضیح**: فاکتور تبدیل از `unit_code` به `item.default_unit` را محاسبه می‌کند.

**پارامترهای ورودی**:
- `item` (Item): instance کالا
- `unit_code` (str): کد واحد برای تبدیل

**مقدار بازگشتی**:
- `Decimal`: فاکتور تبدیل (1 اگر تبدیل لازم نباشد)

**منطق**:
1. اگر `unit_code` خالی است یا برابر با `item.default_unit` است، `Decimal('1')` برمی‌گرداند
2. یک graph از تبدیل‌های واحد می‌سازد (از `ItemUnit` objects)
3. از BFS (Breadth-First Search) برای پیدا کردن مسیر تبدیل استفاده می‌کند
4. فاکتور تبدیل را محاسبه و برمی‌گرداند
5. اگر مسیری پیدا نشد، `Decimal('1')` برمی‌گرداند

**الگوریتم**:
- از `collections.deque` برای queue استفاده می‌کند
- graph را از `ItemUnit` objects می‌سازد (bidirectional)
- از BFS برای پیدا کردن shortest path استفاده می‌کند

---

#### `_validate_unit(self, cleaned_data: Dict[str, Any]) -> None`

**توضیح**: واحد را validate می‌کند و فاکتور تبدیل را محاسبه می‌کند.

**پارامترهای ورودی**:
- `cleaned_data` (Dict[str, Any]): داده‌های تمیز شده فرم

**مقدار بازگشتی**: ندارد

**منطق**:
1. `_unit_factor` را به `Decimal('1')` تنظیم می‌کند
2. اگر فیلد `unit` وجود ندارد، return می‌کند
3. کالا را با `_resolve_item()` دریافت می‌کند
4. اگر کالا وجود ندارد، return می‌کند
5. واحد را از `cleaned_data.get('unit')` یا `item.default_unit` دریافت می‌کند
6. واحدهای مجاز را با `_get_item_allowed_units()` دریافت می‌کند
7. اگر واحد در لیست مجاز نیست، خطا اضافه می‌کند
8. فاکتور تبدیل را با `_get_unit_factor()` محاسبه می‌کند
9. `_unit_factor` و `_entered_unit_value` را تنظیم می‌کند
10. `cleaned_data['unit']` را به `item.default_unit` تغییر می‌دهد (normalize)

---

#### `_normalize_quantity(self, cleaned_data: Dict[str, Any]) -> None`

**توضیح**: مقدار را به واحد پایه normalize می‌کند و مقدار وارد شده را ذخیره می‌کند.

**پارامترهای ورودی**:
- `cleaned_data` (Dict[str, Any]): داده‌های تمیز شده فرم

**مقدار بازگشتی**: ندارد

**منطق**:
1. اگر فیلد `unit` وجود ندارد، return می‌کند
2. کالا و مقدار را دریافت می‌کند
3. اگر کالا یا مقدار وجود ندارد، return می‌کند
4. مقدار وارد شده را در `_entered_quantity_value` ذخیره می‌کند
5. مقدار را با فاکتور تبدیل ضرب می‌کند: `quantity * factor`
6. `cleaned_data['quantity']` را به مقدار normalize شده تغییر می‌دهد
7. `cleaned_data['unit']` را به `item.default_unit` تغییر می‌دهد
8. `self.instance.unit` و `self.instance.quantity` را تنظیم می‌کند

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: داده‌های فرم را validate و normalize می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده و normalize شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `_validate_unit()` را فراخوانی می‌کند
3. `_normalize_quantity()` را فراخوانی می‌کند
4. `cleaned_data` را برمی‌گرداند

---

### `IssueBaseForm(ReceiptBaseForm)`

**توضیح**: کلاس پایه برای فرم‌های issue

**Inheritance**: `ReceiptBaseForm`

**Attributes**:
- `_serial_item`: `Optional[Item]` - کالای مربوط به serial field

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs) -> None`

**توضیح**: فرم issue را initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `_serial_item` را با `_resolve_item()` تنظیم می‌کند
3. `_configure_serial_field()` را فراخوانی می‌کند

---

#### `_filter_company_scoped_fields(self) -> None`

**توضیح**: queryset های فیلدها را بر اساس شرکت فعال فیلتر می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super()._filter_company_scoped_fields()` را فراخوانی می‌کند
2. فیلدهای اضافی issue را فیلتر می‌کند:
   - `department_unit`: فیلتر بر اساس `company_id` و `is_enabled=1`، label: `"{public_code} - {name}"`، `required=False`
   - `work_line`: فیلتر بر اساس `company_id` و `is_enabled=1` (اگر production module نصب باشد)، label: `"{public_code} - {name}"`، `required=False`
   - `consignment_receipt`: فیلتر بر اساس `company_id`، label: `"{document_code} · {item.name}"`

---

#### `_configure_serial_field(self) -> None`

**توضیح**: فیلد `serials` را بر اساس کالا configure می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. فیلد `serials` را از `self.fields.get('serials')` دریافت می‌کند
2. اگر فیلد وجود ندارد، return می‌کند
3. اگر کالا وجود ندارد یا `has_lot_tracking != 1`:
   - فیلد `serials` را از `self.fields` حذف می‌کند
   - return می‌کند
4. queryset را فیلتر می‌کند:
   - `company_id` و `item` را فیلتر می‌کند
   - status را فیلتر می‌کند: `AVAILABLE` یا `RESERVED` برای این document
5. `required=False` تنظیم می‌کند
6. `help_text` را تنظیم می‌کند
7. اگر instance موجود است، `initial` را از `instance.serials` تنظیم می‌کند

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: داده‌های فرم را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. اگر `company_id` وجود دارد:
   - `department_unit`, `work_line`, `consignment_receipt` را validate می‌کند (company match)
   - اگر `warehouse` و `work_line` هر دو انتخاب شده‌اند، بررسی می‌کند که `work_line.warehouse_id == warehouse.id`
3. `_validate_serials()` را فراخوانی می‌کند
4. `cleaned_data` را برمی‌گرداند

---

#### `_validate_serials(self, cleaned_data: Dict[str, Any]) -> None`

**توضیح**: سریال‌ها را validate می‌کند.

**پارامترهای ورودی**:
- `cleaned_data` (Dict[str, Any]): داده‌های تمیز شده فرم

**مقدار بازگشتی**: ندارد

**منطق**:
1. اگر فیلد `serials` وجود ندارد، return می‌کند
2. اگر کالا وجود ندارد یا `has_lot_tracking != 1`، return می‌کند
3. سریال‌های انتخاب شده و مقدار را دریافت می‌کند
4. مقدار را به عدد صحیح تبدیل می‌کند
5. اگر مقدار عدد صحیح نیست، خطا اضافه می‌کند
6. اگر تعداد سریال‌ها با مقدار برابر نیست، خطا اضافه می‌کند
7. اگر سریال‌هایی که به کالای دیگری تعلق دارند انتخاب شده‌اند، خطا اضافه می‌کند

---

### `StocktakingBaseForm(forms.ModelForm)`

**توضیح**: کلاس پایه برای فرم‌های stocktaking

**Inheritance**: `forms.ModelForm`

**Attributes**:
- `unit_placeholder`: `str` - placeholder برای فیلد unit
- `company_id`: `Optional[int]` - شناسه شرکت فعال
- `user`: `Optional[Any]` - کاربر برای permission checks
- `date_widget`: `JalaliDateInput` - widget برای فیلدهای تاریخ
- `datetime_widget`: `forms.DateTimeInput` - widget برای فیلدهای datetime

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, user: Optional[Any] = None, **kwargs) -> None`

**توضیح**: فرم stocktaking را initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `user` (Optional[Any]): کاربر برای permission checks
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `self.company_id` و `self.user` را تنظیم می‌کند
2. widgets را تنظیم می‌کند
3. `super().__init__()` را فراخوانی می‌کند
4. فیلدهای hidden را تنظیم می‌کند:
   - `document_date`: `HiddenInput`، initial: `timezone.now().date()` (اگر instance جدید)
   - `inventory_snapshot_time`: `HiddenInput`، initial: `timezone.now()` (اگر instance جدید)
   - `document_code`: `HiddenInput`
   - `adjustment_metadata`, `variance_document_ids`, `variance_document_codes`, `record_metadata`: `HiddenInput`
5. فیلد `notes` را تنظیم می‌کند: `Textarea` با `rows=3`
6. فیلد `quantity_adjusted` را `readonly` می‌کند
7. اگر `company_id` وجود دارد، `_filter_company_scoped_fields()` را فراخوانی می‌کند
8. `_set_unit_choices()` و `_set_warehouse_queryset()` را فراخوانی می‌کند

---

#### `_filter_company_scoped_fields(self) -> None`

**توضیح**: queryset های فیلدها را بر اساس شرکت فعال فیلتر می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
- برای هر فیلد که وجود دارد:
  - `item`: فیلتر بر اساس `company_id` و `is_enabled=1`، label: `"{name} · {item_code}"`
  - `warehouse`: فیلتر بر اساس `company_id` و `is_enabled=1`، label: `"{public_code} - {name}"`، `empty_label`: `"--- انتخاب کنید ---"`
  - `confirmed_by`: فیلتر بر اساس `company_accesses` با `company_id` و `is_enabled=1` و `is_active=True`، label: `"{username} - {full_name}"`
  - `approver`: فیلتر بر اساس `get_feature_approvers("inventory.stocktaking.records", company_id)`، label: `"{username} - {full_name}"`، `empty_label`: `"--- انتخاب کنید ---"`

---

#### `_resolve_item(self, candidate: Any = None) -> Optional[Item]`

**توضیح**: کالا را از داده‌های فرم یا instance resolve می‌کند.

**پارامترهای ورودی**:
- `candidate` (Any, optional): کالای candidate

**مقدار بازگشتی**:
- `Optional[Item]`: instance کالا یا `None`

**منطق**:
- مشابه `ReceiptBaseForm._resolve_item()`

---

#### `_get_item_allowed_units(self, item: Optional[Item]) -> List[Dict[str, str]]`

**توضیح**: لیست واحدهای مجاز برای یک کالا را برمی‌گرداند.

**پارامترهای ورودی**:
- `item` (Optional[Item]): instance کالا

**مقدار بازگشتی**:
- `List[Dict[str, str]]`: لیست dictionaries با `value` و `label`

**منطق**:
- مشابه `ReceiptBaseForm._get_item_allowed_units()`

---

#### `_get_item_allowed_warehouses(self, item: Optional[Item]) -> List[Dict[str, str]]`

**توضیح**: لیست انبارهای مجاز برای یک کالا را برمی‌گرداند.

**پارامترهای ورودی**:
- `item` (Optional[Item]): instance کالا

**مقدار بازگشتی**:
- `List[Dict[str, str]]`: لیست dictionaries با `value` (warehouse ID) و `label` (warehouse name)

**منطق**:
1. اگر `item` وجود ندارد، لیست خالی برمی‌گرداند
2. روابط `item.warehouses` را دریافت می‌کند
3. انبارهای فعال را فیلتر می‌کند
4. اگر هیچ انباری پیدا نشد، تمام انبارهای شرکت را برمی‌گرداند
5. لیست dictionaries را برمی‌گرداند

---

#### `_set_unit_choices(self) -> None`

**توضیح**: choices فیلد `unit` را بر اساس کالای انتخاب شده تنظیم می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. فیلد `unit` را دریافت می‌کند
2. اگر فیلد وجود ندارد، return می‌کند
3. کالا را با `_resolve_item()` دریافت می‌کند
4. اگر کالا وجود دارد:
   - واحدهای مجاز را دریافت می‌کند
   - اگر `current` unit در instance وجود دارد و در لیست مجاز نیست، آن را اضافه می‌کند
   - widget را به `Select` تنظیم می‌کند
   - choices را تنظیم می‌کند
5. اگر کالا وجود ندارد:
   - widget را به `Select` تنظیم می‌کند
   - choices را به `[placeholder]` تنظیم می‌کند

---

#### `_set_warehouse_queryset(self) -> None`

**توضیح**: queryset فیلد `warehouse` را بر اساس کالای انتخاب شده تنظیم می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. فیلد `warehouse` را دریافت می‌کند
2. اگر فیلد وجود ندارد، return می‌کند
3. کالا را با `_resolve_item()` دریافت می‌کند
4. اگر کالا وجود دارد:
   - انبارهای مجاز را با `_get_item_allowed_warehouses()` دریافت می‌کند
   - اگر انبارهای مجاز وجود دارند، queryset را فیلتر می‌کند
5. اگر کالا وجود ندارد و `company_id` وجود دارد:
   - queryset را به تمام انبارهای شرکت فیلتر می‌کند

---

#### `_validate_unit(self, cleaned_data: Dict[str, Any]) -> None`

**توضیح**: واحد را validate می‌کند.

**پارامترهای ورودی**:
- `cleaned_data` (Dict[str, Any]): داده‌های تمیز شده فرم

**مقدار بازگشتی**: ندارد

**منطق**:
1. فیلد `unit` را دریافت می‌کند
2. اگر فیلد وجود ندارد، return می‌کند
3. کالا و واحد را دریافت می‌کند
4. اگر کالا یا واحد وجود ندارد، return می‌کند
5. واحدهای مجاز را دریافت می‌کند
6. اگر واحد در لیست مجاز نیست، خطا اضافه می‌کند

---

#### `_validate_warehouse(self, cleaned_data: Dict[str, Any]) -> None`

**توضیح**: انبار را بر اساس انبارهای مجاز کالا validate می‌کند.

**پارامترهای ورودی**:
- `cleaned_data` (Dict[str, Any]): داده‌های تمیز شده فرم

**مقدار بازگشتی**: ندارد

**منطق**:
1. فیلد `warehouse` را دریافت می‌کند
2. اگر فیلد وجود ندارد، return می‌کند
3. کالا و انبار را دریافت می‌کند
4. اگر کالا و انبار وجود دارند:
   - انبارهای مجاز را با `_get_item_allowed_warehouses()` دریافت می‌کند
   - اگر انبارهای مجاز وجود دارند:
     - اگر انبار انتخاب شده در لیست مجاز نیست، خطا اضافه می‌کند
   - اگر انبارهای مجاز وجود ندارند:
     - خطا اضافه می‌کند: "این کالا هیچ انبار مجازی ندارد"

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: داده‌های فرم را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `_validate_unit()` را فراخوانی می‌کند
3. `_validate_warehouse()` را فراخوانی می‌کند
4. `cleaned_data` را برمی‌گرداند

---

## Base Formset Class

### `BaseLineFormSet(forms.BaseInlineFormSet)`

**توضیح**: کلاس پایه برای formsets خطوط با پشتیبانی از `company_id` و `request`

**Inheritance**: `forms.BaseInlineFormSet`

**Attributes**:
- `company_id`: `Optional[int]` - شناسه شرکت فعال
- `request`: `Optional[HttpRequest]` - درخواست HTTP

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, request=None, **kwargs) -> None`

**توضیح**: formset را با `company_id` و `request` initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `request` (Optional[HttpRequest]): درخواست HTTP
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `self.company_id` و `self.request` را تنظیم می‌کند
2. `super().__init__()` را فراخوانی می‌کند
3. برای هر form در formset:
   - `form.company_id` و `form.request` را تنظیم می‌کند
   - اگر form متد `_update_querysets_after_company_id` دارد، آن را فراخوانی می‌کند
   - اگر form متد `_update_destination_type_queryset` دارد، آن را فراخوانی می‌کند

---

#### `_construct_form(self, i, **kwargs) -> Form`

**توضیح**: یک form را با `company_id` و `request` می‌سازد.

**پارامترهای ورودی**:
- `i`: index form در formset
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**:
- `Form`: instance form ساخته شده

**منطق**:
1. `super()._construct_form()` را فراخوانی می‌کند
2. `form.company_id` و `form.request` را تنظیم می‌کند
3. اگر form متدهای update دارد، آن‌ها را فراخوانی می‌کند
4. form را برمی‌گرداند

---

#### `empty_form` (property)

**توضیح**: form خالی را با `company_id` و `request` برمی‌گرداند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Form`: instance form خالی

**منطق**:
1. form را با `_construct_form('__prefix__')` می‌سازد
2. `form.company_id` و `form.request` را تنظیم می‌کند
3. اگر form متدهای update دارد، آن‌ها را فراخوانی می‌کند
4. form را برمی‌گرداند

---

#### `clean(self) -> None`

**توضیح**: formset را validate می‌کند و بررسی می‌کند که حداقل یک خط با کالا وجود دارد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. اگر formset خطا دارد، return می‌کند
2. تعداد خطوط غیرخالی (با کالا) را شمارش می‌کند
3. اگر `min_num` تنظیم شده و تعداد خطوط کمتر از `min_num` است:
   - `ValidationError` می‌اندازد

---

## وابستگی‌ها

### Models
- `inventory.models.Item`
- `inventory.models.ItemUnit`
- `inventory.models.Warehouse`
- `inventory.models.Supplier`
- `inventory.models.ReceiptTemporary`
- `inventory.models.ReceiptPermanent`
- `inventory.models.PurchaseRequest`
- `inventory.models.WarehouseRequest`
- `inventory.models.ReceiptConsignment`
- `inventory.models.ItemSerial`
- `inventory.models.CURRENCY_CHOICES`
- `shared.models.CompanyUnit`
- `production.models.WorkLine` (optional, via `get_work_line_model()`)

### Fields and Widgets
- `inventory.fields.JalaliDateField`
- `inventory.widgets.JalaliDateInput`

### Utils
- `shared.utils.modules.get_work_line_model()`

### Django
- `django.forms`
- `django.contrib.auth.get_user_model()`
- `django.db.models.Q`
- `django.utils.timezone`
- `django.utils.translation.gettext_lazy`

---

## استفاده در پروژه

### در Forms
```python
class ReceiptTemporaryForm(ReceiptBaseForm):
    class Meta:
        model = ReceiptTemporary
        fields = ['document_code', 'document_date', 'supplier', ...]
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, company_id=company_id, **kwargs)
        # ReceiptBaseForm automatically handles:
        # - Company filtering
        # - Unit conversion
        # - Quantity normalization
```

### در Formsets
```python
ReceiptTemporaryLineFormSet = inlineformset_factory(
    ReceiptTemporary,
    ReceiptTemporaryLine,
    form=ReceiptTemporaryLineForm,
    formset=BaseLineFormSet,  # Use BaseLineFormSet for company_id and request support
    extra=1,
    can_delete=True,
)

# In view:
formset = ReceiptTemporaryLineFormSet(
    data=request.POST,
    instance=receipt,
    company_id=company_id,
    request=request,  # Pass request for item filtering
)
```

---

## نکات مهم

### 1. Unit Conversion
- `ReceiptBaseForm` و `IssueBaseForm` از unit conversion استفاده می‌کنند
- مقدار وارد شده توسط کاربر در `_entered_quantity_value` ذخیره می‌شود
- مقدار normalize شده (به واحد پایه) در `cleaned_data['quantity']` ذخیره می‌شود
- واحد normalize شده (واحد پایه) در `cleaned_data['unit']` ذخیره می‌شود

### 2. Company Filtering
- تمام base forms از `_filter_company_scoped_fields()` برای فیلتر کردن queryset ها استفاده می‌کنند
- تمام objects باید متعلق به شرکت فعال باشند

### 3. Item-Warehouse Compatibility
- `StocktakingBaseForm` بررسی می‌کند که انبار انتخاب شده در لیست انبارهای مجاز کالا باشد
- اگر کالا هیچ انبار مجازی نداشته باشد، خطا نمایش داده می‌شود

### 4. Serial Management
- `IssueBaseForm` فیلد `serials` را بر اساس `has_lot_tracking` configure می‌کند
- اگر کالا نیاز به serial tracking ندارد، فیلد `serials` حذف می‌شود
- Validation بررسی می‌کند که تعداد سریال‌ها با `quantity` برابر باشد

### 5. Request Passing
- `BaseLineFormSet` `request` را به تمام forms پاس می‌دهد
- این برای item filtering و search در line forms استفاده می‌شود

### 6. Document Code Generation
- `generate_document_code()` کد sequential را به فرمت `{PREFIX}-{YYYYMM}-{SEQUENCE}` تولید می‌کند
- Sequence از آخرین کد در همان ماه استخراج می‌شود

### 7. Approver Filtering
- `get_feature_approvers()` کاربران با permission approve را فیلتر می‌کند
- از `company_accesses` و `groups.profile.access_levels` استفاده می‌کند
- Superuser ها همیشه می‌توانند approve کنند

---

## الگوهای مشترک

1. **Company Filtering**: تمام base forms queryset ها را بر اساس `company_id` فیلتر می‌کنند
2. **Unit Conversion**: `ReceiptBaseForm` و `IssueBaseForm` از unit conversion graph استفاده می‌کنند
3. **Quantity Normalization**: مقدار وارد شده به واحد پایه normalize می‌شود
4. **Item Resolution**: تمام base forms از `_resolve_item()` برای پیدا کردن کالا استفاده می‌کنند
5. **Allowed Units**: واحدهای مجاز از `Item.default_unit`, `Item.primary_unit`, و `ItemUnit` objects استخراج می‌شوند

