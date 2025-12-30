# production/forms/process_operations.py - Process Operations Forms

**هدف**: فرم‌های عملیات فرایند (Process Operations) برای مدیریت عملیات و مواد استفاده شده در عملیات

این فایل شامل فرم‌های زیر است:
- `ProcessOperationMaterialForm` - فرم برای مواد استفاده شده در عملیات
- `ProcessOperationMaterialFormSetBase` - Base formset برای مواد عملیات
- `ProcessOperationMaterialFormSet` - Formset factory برای مواد عملیات
- `ProcessOperationForm` - فرم برای عملیات فرایند
- `ProcessOperationFormSetBase` - Base formset برای عملیات
- `ProcessOperationFormSet` - Formset factory برای عملیات

---

## کلاس‌ها

### `ProcessOperationMaterialForm`

**توضیح**: فرم برای مواد استفاده شده در یک عملیات (Process Operation Material)

**Type**: `forms.ModelForm`

**Model**: `ProcessOperationMaterial`

**Fields**:
- `bom_material` (ModelChoiceField): انتخاب ماده از BOM
  - Widget: `forms.Select` با class `'form-control operation-material-bom-material'`
  - Label: `_('Material from BOM')`
  - Required: `True`
  - Queryset: بر اساس BOM ID فیلتر می‌شود (در `__init__` تنظیم می‌شود)
- `quantity_used` (DecimalField): مقدار استفاده شده
  - Widget: `forms.NumberInput` با class `'form-control operation-material-quantity'`, `step='0.000001'`, `min='0'`
  - Label: `_('Quantity Used')`
  - Required: `True`

**متدها**:

#### `__init__(self, *args: tuple, bom_id: Optional[int] = None, process_id: Optional[int] = None, **kwargs: dict)`

**توضیح**: مقداردهی اولیه form با فیلتر BOM از Process یا BOM ID مستقیم

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `bom_id`: BOM ID (اختیاری)
- `process_id`: Process ID (اختیاری)
- `**kwargs`: آرگومان‌های keyword

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `final_bom_id` را از `bom_id` تنظیم می‌کند
3. اگر `final_bom_id` وجود نداشته باشد و instance دارای `operation_id` باشد:
   - operation را از instance دریافت می‌کند
   - اگر operation دارای `process_id` و process دارای `bom_id` باشد، `final_bom_id` را تنظیم می‌کند
4. اگر `final_bom_id` وجود نداشته باشد و `process_id` ارائه شده باشد:
   - Process را پیدا می‌کند
   - اگر process دارای `bom_id` باشد، `final_bom_id` را تنظیم می‌کند
5. اگر `final_bom_id` وجود داشته باشد:
   - `bom_material` queryset را فیلتر می‌کند: `BOMMaterial.objects.filter(bom_id=final_bom_id, is_enabled=1).select_related('material_item').order_by('line_number')`
6. در غیر این صورت، queryset را `BOMMaterial.objects.none()` تنظیم می‌کند

#### `clean(self) -> Dict[str, Any]`

**توضیح**: اعتبارسنجی داده‌های form

**مقدار بازگشتی**:
- `Dict[str, Any]`: cleaned_data

**منطق**:
1. `cleaned_data` پایه را از `super().clean()` دریافت می‌کند
2. `bom_material` و `quantity_used` را از cleaned_data دریافت می‌کند
3. اگر `bom_material` انتخاب شده باشد اما `quantity_used` ارائه نشده باشد:
   - خطای validation برای `quantity_used` اضافه می‌کند: `_('Quantity is required when material is selected.')`
4. cleaned_data را برمی‌گرداند

---

### `ProcessOperationMaterialFormSetBase`

**توضیح**: Formset پایه با اعتبارسنجی برای مواد عملیات

**Type**: `forms.BaseInlineFormSet`

**متدها**:

#### `__init__(self, *args, process_id: Optional[int] = None, **kwargs)`

**توضیح**: مقداردهی اولیه formset با process_id برای ارسال به forms

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `process_id`: Process ID (اختیاری)
- `**kwargs`: آرگومان‌های keyword

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.process_id` را تنظیم می‌کند
3. اگر `process_id` وجود داشته باشد، آن را به `form_kwargs` اضافه می‌کند تا به تمام forms در formset ارسال شود

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی که مواد تکراری نیستند

**منطق**:
1. اگر formset دارای خطا باشد، return می‌کند
2. لیست `bom_materials` را ایجاد می‌کند
3. برای هر form در formset:
   - اگر form معتبر باشد و حذف نشده باشد (`DELETE=False`):
     - `bom_material` را از cleaned_data دریافت می‌کند
     - اگر `bom_material` وجود داشته باشد:
       - اگر `bom_material` قبلاً در لیست باشد، خطای validation اضافه می‌کند: `_('Each material can only be selected once per operation.')`
       - در غیر این صورت، به لیست اضافه می‌کند

---

### `ProcessOperationMaterialFormSet`

**توضیح**: Formset factory برای مواد عملیات

**Type**: `forms.inlineformset_factory`

**Configuration**:
- `model`: `ProcessOperation`
- `form`: `ProcessOperationMaterialForm`
- `formset`: `ProcessOperationMaterialFormSetBase`
- `extra`: `1`
- `can_delete`: `True`
- `min_num`: `0`
- `validate_min`: `False`

---

### `ProcessOperationForm`

**توضیح**: فرم برای عملیات فرایند (Process Operation)

**Type**: `forms.ModelForm`

**Model**: `ProcessOperation`

**Fields**:
- `name` (CharField): نام عملیات
  - Widget: `forms.TextInput` با class `'form-control operation-name'`
  - Label: `_('Operation Name')`
  - Required: `True`
- `description` (CharField): توضیحات
  - Widget: `forms.TextInput` با class `'form-control operation-description'`
  - Label: `_('Description')`
  - Required: `False`
- `sequence_order` (IntegerField): ترتیب توالی
  - Widget: `forms.NumberInput` با class `'form-control operation-sequence'`, `min='1'`
  - Label: `_('Sequence Order')`
  - Required: `True`
- `labor_minutes_per_unit` (DecimalField): دقیقه کارگر برای هر واحد
  - Widget: `forms.NumberInput` با class `'form-control operation-labor-minutes'`, `step='0.000001'`, `min='0'`
  - Label: `_('Labor Minutes per Unit')`
  - Required: `False`
- `machine_minutes_per_unit` (DecimalField): دقیقه ماشین برای هر واحد
  - Widget: `forms.NumberInput` با class `'form-control operation-machine-minutes'`, `step='0.000001'`, `min='0'`
  - Label: `_('Machine Minutes per Unit')`
  - Required: `False`
- `work_line` (ModelChoiceField): خط کار
  - Widget: `forms.Select` با class `'form-control operation-work-line'`
  - Label: `_('Work Line (خط کاری)')`
  - Required: `False`
  - Queryset: بر اساس company_id فیلتر می‌شود (در `__init__` تنظیم می‌شود)
- `requires_qc` (BooleanField): نیاز به QC (override شده از IntegerField)
  - Widget: `forms.CheckboxInput` با class `'form-check-input operation-requires-qc'`
  - Label: `_('نیاز به QC')`
  - Required: `False`
  - Initial: `False`
- `notes` (CharField): یادداشت‌ها
  - Widget: `forms.Textarea` با class `'form-control operation-notes'`, `rows=2`
  - Label: `_('Notes')`
  - Required: `False`

**متدها**:

#### `clean_requires_qc(self) -> int`

**توضیح**: تبدیل مقدار Boolean checkbox به integer (0 یا 1) برای ذخیره در دیتابیس

**مقدار بازگشتی**:
- `int`: `1` اگر True باشد، در غیر این صورت `0`

**منطق**:
1. `requires_qc` را از cleaned_data دریافت می‌کند
2. اگر `True` باشد، `1` برمی‌گرداند
3. در غیر این صورت، `0` برمی‌گرداند

#### `__init__(self, *args: tuple, bom_id: Optional[int] = None, company_id: Optional[int] = None, **kwargs: dict)`

**توضیح**: مقداردهی اولیه form با BOM ID و company ID برای formset تو در تو و فیلتر خط کار

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `bom_id`: BOM ID (اختیاری)
- `company_id`: Company ID (اختیاری)
- `**kwargs`: آرگومان‌های keyword

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.bom_id` را تنظیم می‌کند
3. اگر `company_id` وجود داشته باشد:
   - `work_line` queryset را فیلتر می‌کند: `WorkLine.objects.filter(company_id=company_id, is_enabled=1).order_by('name')`
4. در غیر این صورت، queryset را `WorkLine.objects.none()` تنظیم می‌کند
5. اگر instance دارای `pk` باشد:
   - مقدار اولیه `requires_qc` را از instance تنظیم می‌کند: `bool(self.instance.requires_qc == 1)`

---

### `ProcessOperationFormSetBase`

**توضیح**: Formset پایه با اعتبارسنجی برای عملیات فرایند

**Type**: `forms.BaseFormSet`

**متدها**:

#### `clean(self) -> None`

**توضیح**: اعتبارسنجی که حداقل یک عملیات وجود دارد

**منطق**:
1. اگر formset دارای خطا باشد، return می‌کند
2. تعداد فرم‌های غیر خالی را شمارش می‌کند
3. برای هر form در formset:
   - اگر form معتبر باشد و حذف نشده باشد (`DELETE=False`):
     - `name` یا `sequence_order` را از cleaned_data دریافت می‌کند
     - اگر حداقل یکی از آن‌ها وجود داشته باشد، شمارنده را افزایش می‌دهد
4. **نکته**: عملیات خالی مجاز است (فیلتر می‌شوند)، اما هر عملیات باید حداقل `name` یا `sequence_order` داشته باشد

---

### `ProcessOperationFormSet`

**توضیح**: Formset factory برای عملیات

**Type**: `forms.formset_factory`

**Configuration**:
- `form`: `ProcessOperationForm`
- `formset`: `ProcessOperationFormSetBase`
- `extra`: `1`
- `can_delete`: `True`
- `min_num`: `0`
- `validate_min`: `False`

---

## وابستگی‌ها

- `django.forms`: `forms.ModelForm`, `forms.Form`, `forms.BaseInlineFormSet`, `forms.BaseFormSet`, `forms.inlineformset_factory`, `forms.formset_factory`
- `production.models`: `ProcessOperation`, `ProcessOperationMaterial`, `BOMMaterial`, `WorkLine`

---

## استفاده در پروژه

### استفاده در Process Views

```python
from production.forms.process_operations import (
    ProcessOperationFormSet,
    ProcessOperationMaterialFormSet,
)

class ProcessCreateView(BaseCreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Process operations formset
        if self.request.method == 'POST':
            context['operations_formset'] = ProcessOperationFormSet(
                self.request.POST,
                prefix='operations',
            )
        else:
            context['operations_formset'] = ProcessOperationFormSet(
                prefix='operations',
            )
        
        return context
```

---

## نکات مهم

1. **BOM Filtering**: `ProcessOperationMaterialForm` مواد را بر اساس BOM ID فیلتر می‌کند. BOM ID می‌تواند از `bom_id` parameter، `process_id` parameter، یا از instance's operation's process دریافت شود

2. **Company Scoping**: `ProcessOperationForm` خط کار را بر اساس `company_id` فیلتر می‌کند

3. **Boolean to Integer Conversion**: فیلد `requires_qc` در model به صورت integer ذخیره می‌شود (0 یا 1)، اما در form به صورت BooleanField (checkbox) نمایش داده می‌شود. متد `clean_requires_qc()` تبدیل را انجام می‌دهد

4. **Material Uniqueness**: `ProcessOperationMaterialFormSetBase` اطمینان می‌دهد که هر ماده فقط یک بار در هر عملیات انتخاب شود

5. **Empty Operations**: `ProcessOperationFormSetBase` اجازه می‌دهد عملیات خالی وجود داشته باشد (فیلتر می‌شوند)، اما هر عملیات باید حداقل `name` یا `sequence_order` داشته باشد

6. **Nested Formsets**: این formsets برای استفاده در Process views طراحی شده‌اند که عملیات و مواد را به صورت تو در تو مدیریت می‌کنند

7. **Formset Prefixes**: هنگام استفاده از چند formset در یک view، باید prefixهای مختلف استفاده شود (مثلاً `'operations'` و `'materials'`)

8. **Validation Order**: اعتبارسنجی formset بعد از اعتبارسنجی forms انجام می‌شود
