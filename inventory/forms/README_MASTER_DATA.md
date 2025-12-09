# inventory/forms/master_data.py - Master Data Forms (Complete Documentation)

**هدف**: Form classes برای داده‌های اصلی (master data) ماژول inventory

این فایل شامل forms برای:
- Item Types, Categories, Subcategories
- Warehouses
- Suppliers and Supplier Categories
- Items and Item Units

---

## Helper Classes

### `IntegerCheckboxField(forms.IntegerField)`

**توضیح**: فیلد Integer مخصوص checkbox values (0/1).

**متدها**:

#### `__init__(self, **kwargs)`

**توضیح**: فیلد را با `required=False` به صورت پیش‌فرض initialize می‌کند.

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های فیلد

**مقدار بازگشتی**: ندارد

---

#### `to_python(self, value) -> int`

**توضیح**: مقدار را به int تبدیل می‌کند، در صورت None یا خالی بودن 0 برمی‌گرداند.

**پارامترهای ورودی**:
- `value`: مقدار ورودی (می‌تواند None، string، int، یا 'on' باشد)

**مقدار بازگشتی**:
- `int`: مقدار عددی (0 یا 1)

**منطق**:
1. اگر `value` برابر `None` یا `''` باشد، `0` برمی‌گرداند
2. اگر `value` برابر `'on'` باشد (از checkbox checked)، `1` برمی‌گرداند
3. در غیر این صورت، سعی می‌کند به int تبدیل کند
4. در صورت خطا، `0` برمی‌گرداند

---

#### `clean(self, value) -> int`

**توضیح**: مقدار را به 0 یا 1 تبدیل می‌کند.

**پارامترهای ورودی**:
- `value`: مقدار ورودی

**مقدار بازگشتی**:
- `int`: `0` یا `1`

**منطق**:
1. `to_python()` را فراخوانی می‌کند
2. اگر نتیجه `1` باشد، `1` برمی‌گرداند
3. در غیر این صورت، `0` برمی‌گرداند

---

#### `has_changed(self, initial, data) -> bool`

**توضیح**: بررسی می‌کند که آیا مقدار تغییر کرده است یا نه.

**پارامترهای ورودی**:
- `initial`: مقدار اولیه
- `data`: مقدار جدید

**مقدار بازگشتی**:
- `bool`: `True` اگر تغییر کرده باشد، `False` در غیر این صورت

**منطق**:
1. هر دو مقدار را به int تبدیل می‌کند
2. مقایسه می‌کند

---

### `IntegerCheckboxInput(forms.CheckboxInput)`

**توضیح**: Widget checkbox که با IntegerField (0/1) کار می‌کند.

**متدها**:

#### `value_from_datadict(self, data, files, name) -> str`

**توضیح**: مقدار را از POST data استخراج می‌کند.

**پارامترهای ورودی**:
- `data`: QueryDict از POST
- `files`: فایل‌های آپلود شده
- `name`: نام فیلد

**مقدار بازگشتی**:
- `str`: `'1'` اگر checked باشد، `'0'` در غیر این صورت

**منطق**:
1. اگر `name` در `data` نباشد، `'0'` برمی‌گرداند (unchecked)
2. اگر `name` در `data` باشد، مقدار را می‌خواند
3. اگر مقدار `'1'`, `'on'`, یا `1` باشد، `'1'` برمی‌گرداند
4. در غیر این صورت، `'0'` برمی‌گرداند

---

#### `format_value(self, value) -> int`

**توضیح**: مقدار را برای rendering فرمت می‌کند.

**پارامترهای ورودی**:
- `value`: مقدار فیلد

**مقدار بازگشتی**:
- `int`: مقدار عددی (0 یا 1)

---

#### `value_omitted_from_data(self, data, files, name) -> bool`

**توضیح**: بررسی می‌کند که آیا مقدار از data حذف شده است یا نه.

**پارامترهای ورودی**:
- `data`: QueryDict
- `files`: فایل‌ها
- `name`: نام فیلد

**مقدار بازگشتی**:
- `bool`: `True` اگر `name` در `data` نباشد

---

#### `get_context(self, name, value, attrs) -> Dict`

**توضیح**: Context را برای template rendering آماده می‌کند.

**پارامترهای ورودی**:
- `name`: نام فیلد
- `value`: مقدار فیلد
- `attrs`: attributes HTML

**مقدار بازگشتی**:
- `Dict`: context با `checked` attribute و `value="1"` تنظیم شده

**منطق**:
1. مقدار را با `format_value()` فرمت می‌کند و به int تبدیل می‌کند
2. **همیشه** `value="1"` را در attrs تنظیم می‌کند (نه "0")
3. اگر مقدار `1` باشد، `checked` attribute را اضافه می‌کند
4. اگر مقدار `0` باشد، `checked` attribute را حذف می‌کند
5. context را از `super().get_context()` دریافت می‌کند
6. `value="1"` را در widget context هم تنظیم می‌کند
7. context را برمی‌گرداند

**نکات مهم**:
- **همیشه** `value="1"` در HTML تنظیم می‌شود (نه "0")
- وضعیت checked/unchecked با attribute `checked` کنترل می‌شود
- وقتی checkbox checked است، POST شامل `field_name="1"` می‌شود
- وقتی checkbox unchecked است، فیلد در POST نیست

---

## Form Classes

### `ItemTypeForm(forms.ModelForm)`

**توضیح**: Form برای ایجاد/ویرایش نوع کالا

**Model**: `ItemType`

**Fields**:
- `name` (CharField): نام فارسی
- `name_en` (CharField): نام انگلیسی
- `description` (CharField): توضیحات
- `notes` (TextField): یادداشت‌ها
- `sort_order` (IntegerField): ترتیب نمایش
- `is_enabled` (PositiveSmallIntegerField): وضعیت (0 یا 1)

**Widgets**:
- `name`: `TextInput` با `class='form-control'`
- `name_en`: `TextInput` با `class='form-control'`
- `description`: `TextInput` با `class='form-control'`
- `notes`: `Textarea` با `class='form-control'` و `rows=3`
- `sort_order`: `NumberInput` با `class='form-control'`
- `is_enabled`: `Select` با `class='form-control'`

**Labels**:
- `name`: 'Name (Persian)'
- `name_en`: 'Name (English)'
- `description`: 'Description'
- `notes`: 'Notes'
- `sort_order`: 'Sort Order'
- `is_enabled`: 'Status'

**متدها**:
- هیچ متد سفارشی ندارد (از `ModelForm` استفاده می‌کند)

---

### `ItemCategoryForm(forms.ModelForm)`

**توضیح**: Form برای ایجاد/ویرایش دسته کالا

**Model**: `ItemCategory`

**Fields**:
- `name` (CharField): نام فارسی
- `name_en` (CharField): نام انگلیسی
- `description` (CharField): توضیحات
- `notes` (TextField): یادداشت‌ها
- `sort_order` (IntegerField): ترتیب نمایش
- `is_enabled` (PositiveSmallIntegerField): وضعیت

**Widgets**: مشابه `ItemTypeForm`

**Labels**: مشابه `ItemTypeForm`

**متدها**:
- هیچ متد سفارشی ندارد

---

### `ItemSubcategoryForm(forms.ModelForm)`

**توضیح**: Form برای ایجاد/ویرایش زیردسته کالا

**Model**: `ItemSubcategory`

**Fields**:
- `category` (ForeignKey): دسته کالا (required)
- `name` (CharField): نام فارسی
- `name_en` (CharField): نام انگلیسی
- `description` (CharField): توضیحات
- `notes` (TextField): یادداشت‌ها
- `sort_order` (IntegerField): ترتیب نمایش
- `is_enabled` (PositiveSmallIntegerField): وضعیت

**Widgets**:
- `category`: `Select` با `class='form-control'`
- سایر فیلدها: مشابه `ItemTypeForm`

**Labels**:
- `category`: 'Item Category'
- سایر labels: مشابه `ItemTypeForm`

**متدها**:
- هیچ متد سفارشی ندارد

---

### `WarehouseForm(forms.ModelForm)`

**توضیح**: Form برای ایجاد/ویرایش انبار

**Model**: `Warehouse`

**Fields**:
- `name` (CharField): نام فارسی
- `name_en` (CharField): نام انگلیسی
- `description` (CharField): توضیحات
- `notes` (TextField): یادداشت‌ها
- `sort_order` (IntegerField): ترتیب نمایش
- `is_enabled` (PositiveSmallIntegerField): وضعیت

**Widgets**: مشابه `ItemTypeForm`

**Labels**: مشابه `ItemTypeForm`

**متدها**:
- هیچ متد سفارشی ندارد

---

### `SupplierForm(forms.ModelForm)`

**توضیح**: Form برای ایجاد/ویرایش تامین‌کننده

**Model**: `Supplier`

**Fields**:
- `name` (CharField): نام فارسی
- `name_en` (CharField): نام انگلیسی
- `phone_number` (CharField): شماره تلفن
- `mobile_number` (CharField): شماره موبایل
- `email` (EmailField): ایمیل
- `address` (TextField): آدرس
- `city` (CharField): شهر
- `state` (CharField): استان
- `country` (CharField): کد کشور (3 کاراکتر)
- `tax_id` (CharField): شناسه مالیاتی
- `description` (CharField): توضیحات
- `sort_order` (IntegerField): ترتیب نمایش
- `is_enabled` (PositiveSmallIntegerField): وضعیت

**Widgets**:
- `name`, `name_en`, `phone_number`, `mobile_number`, `city`, `state`, `tax_id`, `description`: `TextInput` با `class='form-control'`
- `email`: `EmailInput` با `class='form-control'`
- `address`: `Textarea` با `class='form-control'` و `rows=3`
- `country`: `TextInput` با `class='form-control'` و `maxlength='3'`
- `sort_order`: `NumberInput` با `class='form-control'`
- `is_enabled`: `Select` با `class='form-control'`

**Labels**:
- `name`: 'Name (Persian)'
- `name_en`: 'Name (English)'
- `phone_number`: 'Phone Number'
- `mobile_number`: 'Mobile Number'
- `email`: 'Email'
- `address`: 'Address'
- `city`: 'City'
- `state`: 'State/Province'
- `country`: 'Country Code'
- `tax_id`: 'Tax ID'
- `description`: 'Description'
- `sort_order`: 'Sort Order'
- `is_enabled`: 'Status'

**متدها**:
- هیچ متد سفارشی ندارد

---

### `SupplierCategoryForm(forms.ModelForm)`

**توضیح**: Form برای ایجاد/ویرایش دسته تامین‌کننده با زیردسته‌ها و کالاهای اختیاری

**Model**: `SupplierCategory`

**Fields**:

#### Fields از Model:
- `supplier` (ForeignKey): تامین‌کننده (required)
- `category` (ForeignKey): دسته کالا (required)
- `notes` (TextField): یادداشت‌ها

#### Fields اضافی:
- `is_primary` (BooleanField): دسته اصلی (required=False)
- `subcategories` (ModelMultipleChoiceField): زیردسته‌های قابل تامین (required=False)
- `items` (ModelMultipleChoiceField): کالاهای قابل تامین (required=False)

**Widgets**:
- `supplier`: `Select` با `class='form-control'`
- `category`: `Select` با `class='form-control'`
- `is_primary`: `CheckboxInput` با `class='form-check-input'`
- `subcategories`: `CheckboxSelectMultiple` با `class='checkbox-grid'`
- `items`: `CheckboxSelectMultiple` با `class='checkbox-grid'`
- `notes`: `Textarea` با `class='form-control'` و `rows=3`

**Labels**:
- `supplier`: 'تأمین‌کننده'
- `category`: 'دسته‌بندی کالا'
- `is_primary`: 'دستهٔ اصلی'
- `subcategories`: 'زیردسته‌های قابل تأمین'
- `items`: 'کالاهای قابل تأمین'
- `notes`: 'یادداشت‌ها'

**Help Text**:
- `subcategories`: 'در صورت نیاز، زیردسته‌های مربوط به این تأمین‌کننده را انتخاب کنید.'
- `items`: 'کالاهای موجود در همان دسته‌بندی (و زیردسته‌های انتخابی) را می‌توانید انتخاب کنید.'

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: Form را با فیلتر company initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `**kwargs`: آرگومان‌های keyword (شامل `company_id`)

**مقدار بازگشتی**: ندارد

**منطق**:
1. `company_id` را از kwargs استخراج می‌کند
2. `super().__init__()` را فراخوانی می‌کند
3. اگر `company_id` وجود داشته باشد:
   - queryset `supplier` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - queryset `category` را فیلتر می‌کند
   - `category_id` را از data یا instance resolve می‌کند
   - queryset `subcategories` را فیلتر می‌کند (بر اساس company و category)
   - queryset `items` را فیلتر می‌کند (بر اساس company، category، و subcategories انتخاب شده)
4. `label_from_instance` را برای تمام فیلدهای ForeignKey تنظیم می‌کند
5. اگر instance موجود باشد (edit mode):
   - `subcategories` و `items` را از روابط موجود pre-fill می‌کند

---

#### `_resolve_category_id(self) -> Optional[int]`

**توضیح**: شناسه category فعلی را از data، instance، یا initial resolve می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Optional[int]`: شناسه category یا None

**منطق**:
1. اگر form bound باشد، از `self.data.get('category')` می‌خواند
2. در غیر این صورت، از `self.initial.get('category')` یا `self.instance.category_id` می‌خواند
3. به int تبدیل می‌کند و برمی‌گرداند
4. در صورت خطا، None برمی‌گرداند

---

#### `_selected_subcategory_ids(self) -> list`

**توضیح**: شناسه‌های زیردسته‌های انتخاب شده را از form data استخراج می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `list[int]`: لیست شناسه‌های زیردسته‌ها

**منطق**:
1. اگر form bound باشد، از `self.data.getlist('subcategories')` می‌خواند
2. در غیر این صورت، از `self.initial.get('subcategories')` می‌خواند
3. به لیست int تبدیل می‌کند و برمی‌گرداند

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: داده‌های form را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `supplier`, `category`, `subcategories`, `items` را از cleaned_data می‌خواند
3. بررسی می‌کند که `supplier` و `category` متعلق به همان company باشند
4. بررسی می‌کند که برای این supplier و category قبلاً ثبت نشده باشد
5. بررسی می‌کند که `subcategories` متعلق به همان `category` باشند
6. بررسی می‌کند که `items` متعلق به همان `category` و `subcategories` انتخاب شده باشند
7. در صورت خطا، error اضافه می‌کند
8. cleaned_data را برمی‌گرداند

**Validation Errors**:
- اگر supplier و category متعلق به شرکت‌های متفاوت باشند: `ValidationError`
- اگر برای این supplier و category قبلاً ثبت شده باشد: `ValidationError`
- اگر زیردسته‌ها متعلق به دسته نباشند: error روی فیلد `subcategories`
- اگر کالاها متعلق به دسته یا زیردسته‌های انتخاب شده نباشند: error روی فیلد `items`

---

### `ItemForm(forms.ModelForm)`

**توضیح**: Form برای ایجاد/ویرایش کالا

**Model**: `Item`

**Fields**:

#### Fields از Model:
- `type` (ForeignKey): نوع کالا (required)
- `category` (ForeignKey): دسته کالا (required)
- `subcategory` (ForeignKey): زیردسته کالا (optional)
- `user_segment` (CharField): کد کاربری (2 رقم)
- `name` (CharField): نام فارسی
- `name_en` (CharField): نام انگلیسی
- `secondary_batch_number` (CharField): بچ نامبر ثانویه (max 50 کاراکتر)
- `tax_id` (CharField): شناسه مالیاتی
- `tax_title` (CharField): عنوان مالیاتی
- `supply_type` (CharField): نوع تامین
- `planning_type` (CharField): نوع برنامه ریزی
- `lead_time` (IntegerField): زمان تامین (روز)
- `min_stock` (DecimalField): حداقل موجودی
- `description` (CharField): توضیح کوتاه
- `notes` (TextField): یادداشت‌ها
- `sort_order` (IntegerField): ترتیب نمایش

#### Fields اضافی (با IntegerCheckboxField):
- `is_sellable` (IntegerCheckboxField): قابل فروش است (0 یا 1)
- `has_lot_tracking` (IntegerCheckboxField): نیاز به رهگیری لات دارد (0 یا 1)
- `requires_temporary_receipt` (IntegerCheckboxField): ورود از طریق رسید موقت (0 یا 1)
- `serial_in_qc` (IntegerCheckboxField): سریال در QC (0 یا 1)
- `is_enabled` (IntegerCheckboxField): فعال باشد (0 یا 1، initial=1)

#### Fields اضافی:
- `default_unit` (ChoiceField): واحد اصلی (از `UNIT_CHOICES`)
- `primary_unit` (ChoiceField): واحد گزارش (از `UNIT_CHOICES`)
- `allowed_warehouses` (ModelMultipleChoiceField): انبارهای مجاز (required=True)

**Widgets**:
- `type`, `category`, `subcategory`: `Select` با `class='form-control'`
- `user_segment`: `TextInput` با `class='form-control'` و `maxlength='2'`
- `name`, `name_en`, `secondary_batch_number`, `tax_id`, `tax_title`, `description`: `TextInput` با `class='form-control'`
- `min_stock`: `NumberInput` با `class='form-control'` و `step='0.001'`
- `notes`: `Textarea` با `class='form-control'` و `rows=3`
- `sort_order`: `NumberInput` با `class='form-control'`
- `is_sellable`, `has_lot_tracking`, `requires_temporary_receipt`, `serial_in_qc`, `is_enabled`: `IntegerCheckboxInput` با `class='form-check-input'`
- `lead_time`: `NumberInput` با `class='form-control'` و `min='0'`, `step='1'`
- `default_unit`, `primary_unit`: `Select` با `class='form-control'`
- `allowed_warehouses`: `CheckboxSelectMultiple` با `class='checkbox-grid'`

**Labels**:
- `type`: 'نوع کالا'
- `category`: 'دسته‌بندی'
- `subcategory`: 'زیردسته'
- `user_segment`: 'کد کاربری (۲ رقم)'
- `name`: 'نام (فارسی)'
- `name_en`: 'نام (English)'
- `secondary_batch_number`: 'بچ نامبر ثانویه'
- `tax_id`: 'شناسه مالیاتی'
- `tax_title`: 'عنوان مالیاتی'
- `supply_type`: 'نوع تامین'
- `planning_type`: 'نوع برنامه ریزی'
- `lead_time`: 'زمان تامین (روز)'
- `min_stock`: 'حداقل موجودی'
- `description`: 'توضیح کوتاه'
- `notes`: 'یادداشت‌ها'
- `sort_order`: 'ترتیب نمایش'
- `is_sellable`: 'قابل فروش است'
- `has_lot_tracking`: 'نیاز به رهگیری لات دارد'
- `requires_temporary_receipt`: 'ورود از طریق رسید موقت'
- `serial_in_qc`: 'سریال در QC'
- `is_enabled`: 'فعال باشد'
- `default_unit`: 'واحد اصلی'
- `primary_unit`: 'واحد گزارش (برای گزارش‌گیری)'
- `allowed_warehouses`: 'انبارهای مجاز'

**Help Text**:
- `allowed_warehouses`: 'حداقل یک انبار انتخاب کنید؛ اولین مورد به عنوان انبار اصلی ذخیره می‌شود.'

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: Form را با فیلتر company initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `**kwargs`: آرگومان‌های keyword (شامل `company_id`)

**مقدار بازگشتی**: ندارد

**منطق**:
1. `company_id` را از kwargs استخراج می‌کند
2. `super().__init__()` را فراخوانی می‌کند
3. اگر `company_id` وجود داشته باشد:
   - queryset `type` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - queryset `category` را فیلتر می‌کند
   - queryset `subcategory` را فیلتر می‌کند
   - queryset `allowed_warehouses` را فیلتر می‌کند
4. اگر instance موجود باشد (edit mode):
   - `allowed_warehouses` را از `instance.warehouses` pre-fill می‌کند
   - مقادیر checkbox fields را از instance تنظیم می‌کند
5. `label_from_instance` را برای فیلدهای ForeignKey تنظیم می‌کند

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: داده‌های form را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `item_type`, `category`, `subcategory`, `user_segment`, `warehouses` را از cleaned_data می‌خواند
3. بررسی می‌کند که `item_type` و `category` متعلق به همان company باشند
4. بررسی می‌کند که `subcategory` متعلق به `category` باشد
5. بررسی می‌کند که `user_segment` دقیقاً 2 رقم باشد و فقط عدد باشد
6. بررسی می‌کند که حداقل یک `warehouse` انتخاب شده باشد
7. بررسی می‌کند که `warehouses` متعلق به همان company باشند
8. checkbox fields را به 0 یا 1 تبدیل می‌کند (اگر در cleaned_data نباشند، 0 تنظیم می‌شود)
9. در صورت خطا، error اضافه می‌کند
10. cleaned_data را برمی‌گرداند

**Validation Errors**:
- اگر type و category متعلق به شرکت‌های متفاوت باشند: `ValidationError`
- اگر subcategory متعلق به category نباشد: `ValidationError`
- اگر user_segment معتبر نباشد: error روی فیلد `user_segment`
- اگر هیچ warehouse انتخاب نشده باشد: error روی فیلد `allowed_warehouses`
- اگر warehouses متعلق به شرکت متفاوت باشند: error روی فیلد `allowed_warehouses`

---

### `ItemUnitForm(forms.ModelForm)`

**توضیح**: Form برای تعریف تبدیل واحد برای یک کالا

**Model**: `ItemUnit`

**Fields**:
- `id` (HiddenInput): شناسه (برای formsets)
- `public_code` (HiddenInput): کد عمومی (اختیاری)
- `from_unit` (ChoiceField): واحد مبنا (از `UNIT_CHOICES`)
- `from_quantity` (DecimalField): مقدار مبنا
- `to_unit` (ChoiceField): واحد تبدیل (از `UNIT_CHOICES`)
- `to_quantity` (DecimalField): مقدار معادل
- `description` (CharField): توضیح
- `notes` (TextField): یادداشت‌ها

**Widgets**:
- `public_code`: `HiddenInput`
- `from_unit`, `to_unit`: `Select` با `class='form-control'`
- `from_quantity`, `to_quantity`: `NumberInput` با `class='form-control'` و `step='0.001'`
- `description`: `TextInput` با `class='form-control'`
- `notes`: `Textarea` با `class='form-control'` و `rows=2`

**Labels**:
- `from_quantity`: 'مقدار مبنا'
- `to_quantity`: 'مقدار معادل'
- `description`: 'توضیح'
- `notes`: 'یادداشت‌ها'

**متدها**:

#### `__init__(self, *args, **kwargs)`

**توضیح**: Form را initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `public_code` را به `required=False` تنظیم می‌کند
3. اگر فیلد `DELETE` وجود داشته باشد، label آن را تنظیم می‌کند

---

#### `set_company_id(self, company_id: Optional[int]) -> None`

**توضیح**: `company_id` را برای form تنظیم می‌کند.

**پارامترهای ورودی**:
- `company_id` (Optional[int]): شناسه شرکت

**مقدار بازگشتی**: ندارد

---

### `ItemUnitFormSet(forms.BaseInlineFormSet)`

**توضیح**: FormSet برای مدیریت تبدیل واحدهای کالا

**Base**: `forms.BaseInlineFormSet`

**Attributes**:
- `company_id` (Optional[int]): شناسه شرکت

**متدها**:

#### `__init__(self, *args, company_id: Optional[int] = None, **kwargs)`

**توضیح**: FormSet را با `company_id` initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `company_id` را ذخیره می‌کند
2. `super().__init__()` را فراخوانی می‌کند
3. برای هر form در formset، `set_company_id()` را فراخوانی می‌کند

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: FormSet را validate می‌کند و فرم‌های کاملاً خالی را ignore می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. برای هر form:
   - اگر form cleaned_data داشته باشد:
     - بررسی می‌کند که آیا form کاملاً خالی است (فقط DELETE checkbox)
     - اگر خالی باشد، errors را clear می‌کند
3. cleaned_data را برمی‌گرداند

---

#### `is_valid(self) -> bool`

**توضیح**: بررسی می‌کند که آیا formset معتبر است یا نه.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `bool`: `True` اگر معتبر باشد، `False` در غیر این صورت

**منطق**:
1. اگر formset کاملاً خالی باشد (هیچ formی ندارد)، `True` برمی‌گرداند
2. `super().is_valid()` را فراخوانی می‌کند
3. اگر validation ناموفق باشد:
   - بررسی می‌کند که آیا تمام forms خالی هستند یا نه
   - اگر همه خالی باشند، errors را clear می‌کند و `True` برمی‌گرداند
4. نتیجه را برمی‌گرداند

**نکات مهم**:
- Formset می‌تواند کاملاً خالی باشد (units اختیاری هستند)
- فقط forms با داده validate می‌شوند

---

## FormSet Factory

### `ItemUnitFormSet`

**توضیح**: FormSet ایجاد شده با `inlineformset_factory` برای `Item` و `ItemUnit`

**Factory Call**:
```python
ItemUnitFormSet = inlineformset_factory(
    Item,
    ItemUnit,
    form=ItemUnitForm,
    formset=_ItemUnitFormSetBase,
    extra=0,  # No empty rows by default
    can_delete=True,
)
```

**پارامترها**:
- `Item`: مدل parent
- `ItemUnit`: مدل child
- `form`: `ItemUnitForm`
- `formset`: `ItemUnitFormSet` (base class)
- `extra`: `0` (هیچ ردیف خالی به صورت پیش‌فرض)
- `can_delete`: `True` (امکان حذف)

**استفاده**:
```python
formset = ItemUnitFormSet(
    data=request.POST,
    instance=item,
    company_id=company_id
)
```

---

## وابستگی‌ها

- `django.forms`: `ModelForm`, `BaseInlineFormSet`, `inlineformset_factory`
- `django.db.models`: `Q`
- `django.utils.translation`: `gettext_lazy as _`
- `inventory.models`: تمام مدل‌های master data
- `inventory.forms.base`: `UNIT_CHOICES`

---

## استفاده در پروژه

این forms در views ماژول inventory استفاده می‌شوند:
- `ItemTypeForm`: در `ItemTypeCreateView` و `ItemTypeUpdateView`
- `ItemCategoryForm`: در `ItemCategoryCreateView` و `ItemCategoryUpdateView`
- `ItemSubcategoryForm`: در `ItemSubcategoryCreateView` و `ItemSubcategoryUpdateView`
- `WarehouseForm`: در `WarehouseCreateView` و `WarehouseUpdateView`
- `SupplierForm`: در `SupplierCreateView` و `SupplierUpdateView`
- `SupplierCategoryForm`: در `SupplierCategoryCreateView` و `SupplierCategoryUpdateView`
- `ItemForm`: در `ItemCreateView` و `ItemUpdateView`
- `ItemUnitFormSet`: در `ItemCreateView` و `ItemUpdateView` (از طریق `ItemUnitFormsetMixin`)

---

## نکات مهم

1. **Company Filtering**: تمام forms با `company_id` فیلتر می‌شوند
2. **Checkbox Fields**: از `IntegerCheckboxField` و `IntegerCheckboxInput` برای checkbox fields استفاده می‌شود (0/1 به جای True/False)
3. **Dynamic Querysets**: Queryset های ForeignKey به صورت دینامیک بر اساس `company_id` فیلتر می‌شوند
4. **Validation**: تمام forms validation مناسب دارند
5. **Optional Formset**: `ItemUnitFormSet` اختیاری است (می‌تواند خالی باشد)
6. **Supplier Links**: `SupplierCategoryForm` روابط supplier-subcategory و supplier-item را مدیریت می‌کند

