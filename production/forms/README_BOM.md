# production/forms/bom.py - BOM Forms (Complete Documentation)

**هدف**: فرم‌های ماژول production برای مدیریت BOM (Bill of Materials)

این فایل شامل:
- BOMForm: فرم header برای محصول نهایی
- BOMMaterialLineForm: فرم خط مواد اولیه
- BOMMaterialLineFormSetBase: Formset base class با validation
- BOMMaterialLineFormSet: Formset factory
- BOMMaterialAlternativeForm: فرم جایگزین ماده اولیه
- BOMMaterialAlternativeFormSetBase: Formset base class برای جایگزین‌ها با validation
- BOMMaterialAlternativeFormSet: Formset factory برای جایگزین‌ها

---

## وابستگی‌ها

- `inventory.models`: `ItemType`, `ItemCategory`, `ItemSubcategory`, `Item`, `ItemUnit`, `ItemWarehouse`
- `production.models`: `BOM`, `BOMMaterial`, `BOMMaterialAlternative`
- `django.forms`
- `django.utils.translation.gettext_lazy`

---

## BOMForm

### `BOMForm(forms.ModelForm)`

**توضیح**: فرم ایجاد/ویرایش BOM Header (محصول نهایی)

**Model**: `BOM`

**Fields**:
- `finished_item` (ModelChoiceField): محصول نهایی (FK to Item)
  - Widget: `Select` با `id='id_finished_item'`
  - Required: `True`
  - Label: `_('Finished Product')`
- `version` (CharField): نسخه BOM
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Version')`
- `description` (CharField): توضیحات
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Description')`
- `notes` (TextField): یادداشت‌ها
  - Widget: `Textarea` با `rows=3`
  - Required: `False`
  - Label: `_('Notes')`
- `is_enabled` (PositiveSmallIntegerField): وضعیت (فعال/غیرفعال)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Status')`
  - Initial: `1` (برای BOM جدید)

**Extra Filter Fields (not saved to DB)**:
- `item_type` (ModelChoiceField): فیلتر نوع کالا (cascading)
  - Widget: `Select` با `id='id_item_type'`
  - Required: `False`
  - Label: `_('Item Type')`
- `item_category` (ModelChoiceField): فیلتر دسته کالا (cascading)
  - Widget: `Select` با `id='id_item_category'`
  - Required: `False`
  - Label: `_('Category')`
- `item_subcategory` (ModelChoiceField): فیلتر زیردسته کالا (cascading)
  - Widget: `Select` با `id='id_item_subcategory'`
  - Required: `False`
  - Label: `_('Subcategory')`

**متدها**:

#### `__init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict) -> None`

**توضیح**: فرم را با company filtering و cascading filters initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `**kwargs`: آرگومان‌های keyword (مثلاً `instance`)

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.company_id` را از `company_id` یا `instance.company_id` تنظیم می‌کند
3. اگر instance جدید است و `is_enabled` وجود دارد، initial را به `1` تنظیم می‌کند
4. اگر `company_id` وجود دارد:
   - queryset های `item_type`, `item_category`, `item_subcategory` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - queryset `finished_item` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - اگر instance موجود است (edit mode):
     - `item_type.initial` را از `instance.finished_item.type` تنظیم می‌کند
     - `item_category.initial` را از `instance.finished_item.category` تنظیم می‌کند
     - `item_subcategory.initial` را از `instance.finished_item.subcategory` تنظیم می‌کند
5. اگر `company_id` وجود ندارد:
   - تمام queryset ها را به `objects.none()` تنظیم می‌کند

**نکات مهم**:
- Filter fields (`item_type`, `item_category`, `item_subcategory`) در database ذخیره نمی‌شوند
- این فیلدها برای cascading dropdowns در frontend استفاده می‌شوند
- در edit mode، filter fields از `finished_item` populate می‌شوند

---

## BOMMaterialLineForm

### `BOMMaterialLineForm(forms.ModelForm)`

**توضیح**: فرم خط مواد اولیه BOM (استفاده در formset)

**Model**: `BOMMaterial`

**Fields**:
- `material_type` (ModelChoiceField): نوع ماده اولیه (FK to ItemType)
  - Widget: `Select` با `class='material-type'`
  - Required: `True`
  - Label: `_('Material Type')`
- `material_item` (ModelChoiceField): ماده اولیه/کامپوننت (FK to Item)
  - Widget: `Select` با `class='material-item'`
  - Required: `True`
  - Label: `_('Material/Component')`
- `quantity_per_unit` (DecimalField): مقدار مورد نیاز برای هر واحد محصول نهایی
  - Widget: `NumberInput` با `step='0.000001'`, `min='0'`
  - Required: `True`
  - Label: `_('Quantity')`
- `unit` (CharField): واحد اندازه‌گیری
  - Widget: `Select` با `class='material-unit'`
  - Required: `False` (اما در `clean()` validate می‌شود اگر `material_item` انتخاب شده باشد)
  - Label: `_('Unit')`
- `scrap_allowance` (DecimalField): درصد ضایعات (0-100)
  - Widget: `NumberInput` با `step='0.01'`, `min='0'`, `max='100'`
  - Required: `False`
  - Label: `_('Scrap %')`
- `is_optional` (BooleanField): آیا ماده اختیاری است
  - Widget: `CheckboxInput` با `class='form-check-input'`
  - Required: `False`
  - Initial: `False`
  - Label: `_('Optional')`
  - **نکته**: در database به صورت `PositiveSmallIntegerField` (0/1) ذخیره می‌شود
- `description` (CharField): توضیحات
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Description')`

**Extra Filter Fields (not saved to DB)**:
- `material_category_filter` (ChoiceField): فیلتر دسته ماده (cascading)
  - Widget: `Select` با `class='material-category-filter'`
  - Required: `False`
  - Label: `_('Material Category')`
- `material_subcategory_filter` (ChoiceField): فیلتر زیردسته ماده (cascading)
  - Widget: `Select` با `class='material-subcategory-filter'`
  - Required: `False`
  - Label: `_('Material Subcategory')`

**متدها**:

#### `__init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict) -> None`

**توضیح**: فرم را با company filtering و filter fields initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.company_id` را تنظیم می‌کند
3. اگر `company_id` وجود دارد:
   - queryset `material_type` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - choices `material_category_filter` را populate می‌کند
   - choices `material_subcategory_filter` را populate می‌کند
   - queryset `material_item` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - widget `material_item` را با `class='material-item'` تنظیم می‌کند
4. اگر `company_id` وجود ندارد:
   - تمام queryset ها و choices را به empty تنظیم می‌کند

---

#### `clean_is_optional(self) -> int`

**توضیح**: مقدار Boolean checkbox را به integer (0 یا 1) برای ذخیره در database تبدیل می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `int`: `1` اگر checkbox checked باشد، `0` در غیر این صورت

**منطق**:
1. `cleaned_data.get('is_optional')` را دریافت می‌کند
2. اگر `True` است، `1` برمی‌گرداند
3. در غیر این صورت `0` برمی‌گرداند

**نکات مهم**:
- `BooleanField` در form به صورت checkbox نمایش داده می‌شود
- در database به صورت `PositiveSmallIntegerField` (0/1) ذخیره می‌شود
- `0` = Required (پیش‌فرض)
- `1` = Optional

---

#### `clean(self) -> dict`

**توضیح**: داده‌های فرم را validate می‌کند و filter fields را از `cleaned_data` حذف می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `dict`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. Filter fields (`material_category_filter`, `material_subcategory_filter`) را از `cleaned_data` حذف می‌کند
3. `material_item`, `unit`, `material_type` را دریافت می‌کند
4. اگر `material_item` انتخاب شده و `material_type` وجود ندارد:
   - `material_type` را از `material_item.type` auto-set می‌کند
5. اگر `material_item` انتخاب شده و `unit` وجود ندارد:
   - خطا اضافه می‌کند: "Please select a unit for the selected material."
6. اگر `is_optional` تنظیم نشده است، آن را به `0` تنظیم می‌کند
7. اگر `material_item` انتخاب نشده است:
   - فیلدهای required را به `None` تنظیم می‌کند (برای empty forms)
8. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- Filter fields در database ذخیره نمی‌شوند
- `material_type` به صورت خودکار از `material_item` استخراج می‌شود
- `unit` required است اگر `material_item` انتخاب شده باشد

---

#### `full_clean(self) -> None`

**توضیح**: Filter fields را از validation حذف می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. Filter fields را از `self.fields` حذف می‌کند (موقتاً)
2. `super().full_clean()` را فراخوانی می‌کند
3. Filter fields را دوباره به `self.fields` اضافه می‌کند

**نکات مهم**:
- این متد برای جلوگیری از validation error برای filter fields استفاده می‌شود
- Filter fields فقط برای UI هستند و در database ذخیره نمی‌شوند

---

## BOMMaterialLineFormSetBase

### `BOMMaterialLineFormSetBase(forms.BaseInlineFormSet)`

**توضیح**: Formset base class با validation برای BOM materials

**Inheritance**: `forms.BaseInlineFormSet`

**متدها**:

#### `clean(self) -> None`

**توضیح**: بررسی می‌کند که حداقل یک خط کامل (با `material_item`) وجود دارد.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. اگر formset خطا دارد، return می‌کند
2. تعداد خطوط غیرخالی (با `material_item` انتخاب شده) را شمارش می‌کند
3. برای هر form:
   - بررسی می‌کند که `cleaned_data` وجود دارد
   - بررسی می‌کند که `DELETE` نشده است
   - بررسی می‌کند که `material_item` انتخاب شده است
4. اگر تعداد خطوط غیرخالی `0` است:
   - `ValidationError` می‌اندازد: "At least one material line with a selected material is required."

**نکات مهم**:
- این validation در formset level انجام می‌شود
- حداقل یک خط کامل (با `material_item`) لازم است

---

## BOMMaterialLineFormSet

### `BOMMaterialLineFormSet`

**توضیح**: Formset factory برای BOM materials

**Factory**: `forms.inlineformset_factory`

**پارامترها**:
- `parent_model`: `BOM`
- `model`: `BOMMaterial`
- `form`: `BOMMaterialLineForm`
- `formset`: `BOMMaterialLineFormSetBase`
- `extra`: `1` (شروع با 1 خط خالی)
- `can_delete`: `True` (نمایش checkbox DELETE)
- `min_num`: `0` (validation در `clean()` انجام می‌شود)
- `validate_min`: `False` (validation در `clean()` انجام می‌شود)

**استفاده**:
```python
formset = BOMMaterialLineFormSet(
    data=request.POST,
    instance=bom_instance,
    form_kwargs={'company_id': company_id}
)
```

---

## استفاده در پروژه

### در Views
```python
class BOMCreateView(CreateView):
    model = BOM
    form_class = BOMForm
    template_name = 'production/bom_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = BOMMaterialLineFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        else:
            context['formset'] = BOMMaterialLineFormSet(
                instance=self.object,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        return context
```

---

## نکات مهم

### 1. Cascading Filters
- `BOMForm` از cascading filters برای `finished_item` استفاده می‌کند
- `BOMMaterialLineForm` از cascading filters برای `material_item` استفاده می‌کند
- Filter fields در database ذخیره نمی‌شوند

### 2. Item Filtering and Search
- `finished_item` در `BOMForm` با search و filter پشتیبانی می‌شود
- `material_item` در `BOMMaterialLineForm` با search و filter پشتیبانی می‌شود
- API endpoint: `/inventory/api/filtered-items/?type_id=<id>&category_id=<id>&subcategory_id=<id>&search=<term>`

### 3. Unit Selection
- `unit` در `BOMMaterialLineForm` از API endpoint `/inventory/api/item-units/?item_id=<id>` populate می‌شود
- شامل `primary_unit` و `conversion_units` است

### 4. is_optional Field
- در form به صورت `BooleanField` (checkbox) است
- در database به صورت `PositiveSmallIntegerField` (0/1) ذخیره می‌شود
- تبدیل در `clean_is_optional()` انجام می‌شود

### 5. Auto-set material_type
- اگر `material_item` انتخاب شده و `material_type` وجود ندارد، به صورت خودکار از `material_item.type` استخراج می‌شود

### 6. Formset Validation
- حداقل یک خط کامل (با `material_item`) لازم است
- Validation در `BOMMaterialLineFormSetBase.clean()` انجام می‌شود

---

## BOMMaterialAlternativeForm

### `BOMMaterialAlternativeForm(forms.ModelForm)`

**توضیح**: فرم جایگزین ماده اولیه BOM (استفاده در formset)

**Model**: `BOMMaterialAlternative`

**Fields**:
- `alternative_item` (ModelChoiceField): کالای جایگزین (FK to Item)
  - Widget: `Select` با `class='form-control alternative-item'`
  - Required: `True` (اگر form کامل باشد)
  - Label: `_('Alternative Item')`
- `quantity` (DecimalField): مقدار جایگزین
  - Widget: `NumberInput` با `step='0.000001'`, `min='0'`
  - Required: `True` (اگر `alternative_item` انتخاب شده باشد)
  - Label: `_('Quantity')`
- `unit` (CharField): واحد اندازه‌گیری
  - Widget: `Select` با `class='form-control alternative-unit'`
  - Required: `False` (اما در `clean()` validate می‌شود اگر `alternative_item` انتخاب شده باشد)
  - Label: `_('Unit')`
- `priority` (PositiveSmallIntegerField): اولویت (1-10)
  - Widget: `NumberInput` با `min='1'`, `max='10'`
  - Required: `True` (اگر `alternative_item` انتخاب شده باشد)
  - Label: `_('Priority')`
  - Help Text: `_('Priority order (1 = highest, must be unique)')`
- `source_warehouses` (ManyToManyField): انبارهای منبع (1-5 انبار)
  - Widget: `HiddenInput` (از طریق JavaScript populate می‌شود)
  - Required: `False`
  - Label: `_('Source Warehouses')`
  - Help Text: `_('Select 1 to 5 source warehouses with priorities')`
- `is_combinable` (BooleanField): آیا قابل ترکیب است
  - Widget: `CheckboxInput` با `class='form-check-input'`
  - Required: `False`
  - Initial: `False`
  - Label: `_('Combinable')`
  - **نکته**: در database به صورت `PositiveSmallIntegerField` (0/1) ذخیره می‌شود
- `description` (CharField): توضیحات
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Description')`

**Extra Filter Fields (not saved to DB)**:
- `alternative_category_filter` (ChoiceField): فیلتر دسته جایگزین (cascading)
  - Widget: `Select` با `class='form-control alternative-category-filter'`
  - Required: `False`
  - Label: `_('Category')`
- `alternative_subcategory_filter` (ChoiceField): فیلتر زیردسته جایگزین (cascading)
  - Widget: `Select` با `class='form-control alternative-subcategory-filter'`
  - Required: `False`
  - Label: `_('Subcategory')`

**متدها**:

#### `__init__(self, *args: tuple, company_id: Optional[int] = None, bom_material_id: Optional[int] = None, **kwargs: dict) -> None`

**توضیح**: فرم را با company filtering و filter fields initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `bom_material_id` (Optional[int]): شناسه BOM material (برای context)
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.company_id` و `self.bom_material_id` را تنظیم می‌کند
3. اگر `company_id` وجود دارد:
   - choices `alternative_category_filter` را populate می‌کند (بر اساس company و `is_enabled=1`)
   - choices `alternative_subcategory_filter` را populate می‌کند (بر اساس company و `is_enabled=1`)
   - queryset `alternative_item` را فیلتر می‌کند (بر اساس company و `is_enabled=1`) با `select_related('type', 'category', 'subcategory')`
   - widget `alternative_item` را با `class='form-control alternative-item'` تنظیم می‌کند
4. اگر `company_id` وجود ندارد:
   - تمام queryset ها و choices را به empty تنظیم می‌کند

---

#### `clean_is_combinable(self) -> int`

**توضیح**: مقدار Boolean checkbox را به integer (0 یا 1) برای ذخیره در database تبدیل می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `int`: `1` اگر checkbox checked باشد، `0` در غیر این صورت

**منطق**:
1. `cleaned_data.get('is_combinable')` را دریافت می‌کند
2. اگر `True` است، `1` برمی‌گرداند
3. در غیر این صورت `0` برمی‌گرداند

**نکات مهم**:
- `BooleanField` در form به صورت checkbox نمایش داده می‌شود
- در database به صورت `PositiveSmallIntegerField` (0/1) ذخیره می‌شود
- `0` = Not combinable (پیش‌فرض)
- `1` = Combinable

---

#### `clean(self) -> dict`

**توضیح**: داده‌های فرم را validate می‌کند و filter fields را از `cleaned_data` حذف می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `dict`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. Filter fields (`alternative_category_filter`, `alternative_subcategory_filter`) را از `cleaned_data` حذف می‌کند
3. `alternative_item`, `unit`, `priority`, `source_warehouses` را دریافت می‌کند
4. اگر `alternative_item` انتخاب شده و `unit` وجود ندارد:
   - خطا اضافه می‌کند: "Please select a unit for the selected alternative item."
5. اگر `alternative_item` و `unit` وجود دارند:
   - تمام units مجاز برای این item را از `ItemUnit` (from_unit, to_unit) و `primary_unit`, `default_unit` استخراج می‌کند
   - بررسی می‌کند که `unit` در allowed units باشد
   - اگر نیست، خطا اضافه می‌کند: "Selected unit is not valid for this alternative item."
6. اگر `priority` وجود دارد:
   - بررسی می‌کند که بین 1 و 10 باشد
   - اگر نیست، خطا اضافه می‌کند: "Priority must be between 1 and 10."
7. اگر `source_warehouses` وجود دارد:
   - بررسی می‌کند که حداکثر 5 انبار باشد
   - اگر بیش از 5 است، خطا اضافه می‌کند: "Maximum 5 source warehouses allowed."
   - اگر `alternative_item` انتخاب شده است:
     - تمام انبارهای مجاز برای این item را از `ItemWarehouse` استخراج می‌کند
     - بررسی می‌کند که تمام انبارهای انتخاب شده در allowed warehouses باشند
     - اگر نیستند، خطا اضافه می‌کند: "One or more selected warehouses are not valid for this alternative item."
8. اگر `is_combinable` تنظیم نشده است، آن را به `0` تنظیم می‌کند
9. اگر `alternative_item` انتخاب نشده است:
   - فیلدهای required را به `None` تنظیم می‌کند (برای empty forms)
10. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- Filter fields در database ذخیره نمی‌شوند
- `unit` required است اگر `alternative_item` انتخاب شده باشد
- `priority` باید بین 1 و 10 باشد و unique باشد (validation در formset)
- `source_warehouses` حداکثر 5 انبار می‌تواند داشته باشد
- انبارها باید در `ItemWarehouse` برای این item تعریف شده باشند

---

#### `full_clean(self) -> None`

**توضیح**: Filter fields را از validation حذف می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. Filter fields را از `self.fields` حذف می‌کند (موقتاً)
2. `super().full_clean()` را فراخوانی می‌کند
3. Filter fields را دوباره به `self.fields` اضافه می‌کند

**نکات مهم**:
- این متد برای جلوگیری از validation error برای filter fields استفاده می‌شود
- Filter fields فقط برای UI هستند و در database ذخیره نمی‌شوند

---

## BOMMaterialAlternativeFormSetBase

### `BOMMaterialAlternativeFormSetBase(forms.BaseInlineFormSet)`

**توضیح**: Formset base class با validation برای BOM material alternatives

**Inheritance**: `forms.BaseInlineFormSet`

**متدها**:

#### `clean(self) -> None`

**توضیح**: بررسی می‌کند که:
- حداکثر 10 جایگزین وجود دارد
- اولویت‌ها unique هستند
- کالاهای جایگزین unique هستند (هر کالا فقط یک‌بار می‌تواند اضافه شود)

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. اگر formset خطا دارد، return می‌کند
2. برای هر form:
   - بررسی می‌کند که `cleaned_data` وجود دارد
   - بررسی می‌کند که `DELETE` نشده است
   - بررسی می‌کند که `alternative_item` انتخاب شده است
   - اگر `alternative_item` وجود دارد:
     - `priority` را دریافت می‌کند
     - بررسی می‌کند که `priority` در `priorities` set نیست (unique)
     - اگر duplicate است، `ValidationError` می‌اندازد: "Priority values must be unique. Duplicate priority: {priority}"
     - `priority` را به `priorities` set اضافه می‌کند
     - بررسی می‌کند که `alternative_item` در `items` set نیست (unique)
     - اگر duplicate است، `ValidationError` می‌اندازد: "Each alternative item can only be added once per BOM material line."
     - `alternative_item` را به `items` set اضافه می‌کند
     - form را به `alternatives` list اضافه می‌کند
3. بررسی می‌کند که تعداد جایگزین‌ها حداکثر 10 است
4. اگر بیش از 10 است، `ValidationError` می‌اندازد: "Maximum 10 alternative items allowed per BOM material line."

**نکات مهم**:
- این validation در formset level انجام می‌شود
- حداکثر 10 جایگزین مجاز است
- اولویت‌ها باید unique باشند
- کالاهای جایگزین باید unique باشند (هر کالا فقط یک‌بار)

---

## BOMMaterialAlternativeFormSet

### `BOMMaterialAlternativeFormSet`

**توضیح**: Formset factory برای BOM material alternatives

**Factory**: `forms.inlineformset_factory`

**پارامترها**:
- `parent_model`: `BOMMaterial`
- `model`: `BOMMaterialAlternative`
- `form`: `BOMMaterialAlternativeForm`
- `formset`: `BOMMaterialAlternativeFormSetBase`
- `extra`: `1` (شروع با 1 خط خالی برای template)
- `can_delete`: `True` (نمایش checkbox DELETE)
- `min_num`: `0` (validation در `clean()` انجام می‌شود)
- `validate_min`: `False` (validation در `clean()` انجام می‌شود)

**استفاده**:
```python
formset = BOMMaterialAlternativeFormSet(
    data=request.POST,
    instance=bom_material_instance,
    form_kwargs={'company_id': company_id, 'bom_material_id': bom_material_id}
)
```

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
2. **Cascading Filters**: Filter fields برای cascading dropdowns استفاده می‌شوند
3. **Filter Fields Removal**: Filter fields از `cleaned_data` حذف می‌شوند
4. **Auto-population**: در edit mode، filter fields از instance populate می‌شوند
5. **Boolean to Integer Conversion**: `is_optional` و `is_combinable` از BooleanField به integer (0/1) تبدیل می‌شوند
6. **Unit Validation**: واحدها باید در allowed units برای item باشند
7. **Warehouse Validation**: انبارها باید در `ItemWarehouse` برای item تعریف شده باشند
8. **Priority Validation**: اولویت‌ها باید unique باشند و بین 1 و 10 باشند
9. **Maximum Limits**: حداکثر 10 جایگزین برای هر BOM material line
10. **Unique Items**: هر کالای جایگزین فقط یک‌بار می‌تواند اضافه شود

