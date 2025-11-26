# production/forms/performance_record.py - Performance Record Forms (Complete Documentation)

**هدف**: فرم‌های ماژول production برای مدیریت ثبت عملکرد تولید

این فایل شامل:
- PerformanceRecordForm: فرم header برای ثبت عملکرد
- PerformanceRecordMaterialForm: فرم خط مواد مصرف شده
- PerformanceRecordPersonForm: فرم خط پرسنل
- PerformanceRecordMachineForm: فرم خط ماشین‌آلات
- 3 Formset factories

---

## وابستگی‌ها

- `inventory.fields`: `JalaliDateField`
- `production.models`: `PerformanceRecord`, `PerformanceRecordMaterial`, `PerformanceRecordPerson`, `PerformanceRecordMachine`, `ProductOrder`, `TransferToLine`, `Person`, `Machine`, `WorkLine`, `Process`
- `django.forms`
- `django.forms.inlineformset_factory`
- `django.utils.translation.gettext_lazy`
- `decimal.Decimal`

---

## PerformanceRecordForm

### `PerformanceRecordForm(forms.ModelForm)`

**توضیح**: فرم ایجاد/ویرایش ثبت عملکرد تولید

**Model**: `PerformanceRecord`

**Fields**:
- `order` (ModelChoiceField): سفارش تولید (FK to ProductOrder)
  - Widget: `Select` با `id='id_order'`
  - Required: `True`
  - Label: `_('Product Order')`
  - Help Text: `_('Select the product order for this performance record')`
  - **نکته**: فقط سفارش‌های با process (`process__isnull=False`) نمایش داده می‌شوند
- `transfer` (ModelChoiceField): درخواست انتقال به خط - اختیاری (FK to TransferToLine)
  - Widget: `Select` با `id='id_transfer'`
  - Required: `False`
  - Label: `_('Transfer to Line (Optional)')`
  - Help Text: `_('Select the transfer document used (optional, will auto-populate materials if selected)')`
  - **نکته**: فقط transfer های approved (`status='approved'`) نمایش داده می‌شوند
- `performance_date` (JalaliDateField): تاریخ عملکرد
  - Widget: `JalaliDateInput`
  - Required: `True`
  - Label: `_('Performance Date')`
- `quantity_planned` (DecimalField): مقدار برنامه‌ریزی شده (read-only)
  - Widget: `NumberInput` با `readonly=True`
  - Required: `False`
  - Label: `_('Planned Quantity')`
  - Help Text: `_('Planned quantity from the order (read-only)')`
- `quantity_actual` (DecimalField): مقدار واقعی تولید شده
  - Widget: `NumberInput` با `step='0.000001'`, `min='0'`
  - Required: `False`
  - Label: `_('Actual Quantity Produced')`
  - Help Text: `_('Enter the actual quantity produced')`
- `approved_by` (ModelChoiceField): تایید کننده (FK to User)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Approver')`
  - Help Text: `_('Select the user who can approve this performance record')`
  - **نکته**: فقط کاربرانی که permission approve برای `production.performance_records` دارند نمایش داده می‌شوند
- `notes` (TextField): یادداشت‌ها
  - Widget: `Textarea` با `rows=3`
  - Required: `False`
  - Label: `_('Notes')`

**متدها**:

#### `__init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict) -> None`

**توضیح**: فرم را با company filtering و permission-based filtering initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.company_id` را از `company_id` یا `instance.company_id` تنظیم می‌کند
3. اگر `company_id` وجود دارد:
   - queryset `order` را فیلتر می‌کند (بر اساس company، `is_enabled=1`، و `process__isnull=False`)
   - queryset `transfer` را فیلتر می‌کند (بر اساس company، `is_enabled=1`، و `status='approved'`)
   - queryset `approved_by` را فیلتر می‌کند (permission-based)
4. اگر `company_id` وجود ندارد:
   - تمام queryset ها را به `objects.none()` تنظیم می‌کند
5. اگر instance موجود است و `is_locked=True`:
   - تمام فیلدها را به `readonly` و `disabled` تنظیم می‌کند (به جز `notes`)

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: داده‌های فرم را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `order`, `quantity_planned`, `quantity_actual` را دریافت می‌کند
3. اگر `order` انتخاب نشده است:
   - خطا اضافه می‌کند: "Please select a product order."
   - `cleaned_data` را برمی‌گرداند
4. اگر `order.process` وجود ندارد:
   - خطا اضافه می‌کند: "Selected order must have a process assigned."
   - `cleaned_data` را برمی‌گرداند
5. اگر `quantity_planned` تنظیم نشده است و `order` وجود دارد:
   - `cleaned_data['quantity_planned'] = order.quantity_planned` تنظیم می‌کند
6. اگر `quantity_actual` وجود دارد و `< 0` است:
   - خطا اضافه می‌کند: "Actual quantity cannot be negative."
7. اگر `transfer` انتخاب شده است:
   - بررسی می‌کند که `transfer.order_id == order.id`
   - اگر برابر نیست:
     - خطا اضافه می‌کند: "Selected transfer must belong to the selected order."
8. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- `order` باید انتخاب شود
- `order` باید process داشته باشد
- `transfer` باید متعلق به `order` باشد
- `quantity_actual` نمی‌تواند منفی باشد

---

## PerformanceRecordMaterialForm

### `PerformanceRecordMaterialForm(forms.ModelForm)`

**توضیح**: فرم خط مواد مصرف شده در ثبت عملکرد

**Model**: `PerformanceRecordMaterial`

**Fields**:
- `material_item` (ModelChoiceField): ماده اولیه (FK to Item)
  - Widget: `Select`
  - Required: `True`
  - Label: `_('Material Item')`
  - **نکته**: queryset به صورت dynamic بر اساس transfer تنظیم می‌شود
- `quantity_required` (DecimalField): مقدار مورد نیاز (read-only)
  - Widget: `NumberInput` با `readonly=True`
  - Required: `False`
  - Label: `_('Required Quantity')`
- `quantity_waste` (DecimalField): مقدار ضایعات
  - Widget: `NumberInput` با `step='0.000001'`, `min='0'`
  - Required: `False`
  - Label: `_('Waste Quantity')`
- `unit` (CharField): واحد اندازه‌گیری (read-only)
  - Widget: `TextInput` با `readonly=True`
  - Required: `False`
  - Label: `_('Unit')`
- `is_extra` (BooleanField): آیا ماده اضافی است (hidden)
  - Widget: `HiddenInput`
  - Required: `False`
  - **نکته**: به صورت خودکار مدیریت می‌شود
- `notes` (TextField): یادداشت‌ها
  - Widget: `Textarea` با `rows=2`
  - Required: `False`
  - Label: `_('Notes')`

**متدها**:

#### `__init__(self, *args: tuple, company_id: Optional[int] = None, **kwargs: dict) -> None`

**توضیح**: فرم را با company filtering initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.company_id` را تنظیم می‌کند
3. queryset `material_item` به صورت dynamic بر اساس transfer تنظیم می‌شود (در view)

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: داده‌های فرم را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `quantity_waste` و `quantity_required` را دریافت می‌کند
3. اگر `quantity_waste < 0`:
   - خطا اضافه می‌کند: "Waste quantity cannot be negative."
4. اگر `quantity_waste > quantity_required`:
   - خطا اضافه می‌کند: "Waste quantity cannot exceed required quantity."
5. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- `quantity_waste` نمی‌تواند منفی باشد
- `quantity_waste` نمی‌تواند بیشتر از `quantity_required` باشد

---

## PerformanceRecordPersonForm

### `PerformanceRecordPersonForm(forms.ModelForm)`

**توضیح**: فرم خط پرسنل در ثبت عملکرد

**Model**: `PerformanceRecordPerson`

**Fields**:
- `person` (ModelChoiceField): پرسنل (FK to Person)
  - Widget: `Select`
  - Required: `True`
  - Label: `_('Person')`
- `work_minutes` (DecimalField): دقایق کار
  - Widget: `NumberInput` با `step='0.01'`, `min='0'`
  - Required: `False`
  - Label: `_('Work Minutes')`
- `work_line` (ModelChoiceField): خط کاری (FK to WorkLine)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Work Line')`
  - **نکته**: اگر `process_id` ارائه شود، فقط خطوط کاری مربوط به آن process نمایش داده می‌شوند
- `notes` (TextField): یادداشت‌ها
  - Widget: `Textarea` با `rows=2`
  - Required: `False`
  - Label: `_('Notes')`

**متدها**:

#### `__init__(self, *args: tuple, company_id: Optional[int] = None, process_id: Optional[int] = None, **kwargs: dict) -> None`

**توضیح**: فرم را با company filtering و process filtering initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `process_id` (Optional[int]): شناسه process برای فیلتر کردن work lines
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().__init__()` را فراخوانی می‌کند
2. `self.company_id` را تنظیم می‌کند
3. اگر `company_id` وجود دارد:
   - queryset `person` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - queryset `work_line` را فیلتر می‌کند:
     - بر اساس company و `is_enabled=1`
     - اگر `process_id` ارائه شود، فقط خطوط کاری مربوط به آن process
4. اگر `company_id` وجود ندارد:
   - تمام queryset ها را به `objects.none()` تنظیم می‌کند

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: داده‌های فرم را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `work_minutes` را دریافت می‌کند
3. اگر `work_minutes < 0`:
   - خطا اضافه می‌کند: "Work minutes cannot be negative."
4. `cleaned_data` را برمی‌گرداند

---

## PerformanceRecordMachineForm

### `PerformanceRecordMachineForm(forms.ModelForm)`

**توضیح**: فرم خط ماشین‌آلات در ثبت عملکرد

**Model**: `PerformanceRecordMachine`

**Fields**:
- `machine` (ModelChoiceField): ماشین (FK to Machine)
  - Widget: `Select`
  - Required: `True`
  - Label: `_('Machine')`
- `work_minutes` (DecimalField): دقایق کار
  - Widget: `NumberInput` با `step='0.01'`, `min='0'`
  - Required: `False`
  - Label: `_('Work Minutes')`
- `work_line` (ModelChoiceField): خط کاری (FK to WorkLine)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Work Line')`
  - **نکته**: اگر `process_id` ارائه شود، فقط خطوط کاری مربوط به آن process نمایش داده می‌شوند
- `notes` (TextField): یادداشت‌ها
  - Widget: `Textarea` با `rows=2`
  - Required: `False`
  - Label: `_('Notes')`

**متدها**:

#### `__init__(self, *args: tuple, company_id: Optional[int] = None, process_id: Optional[int] = None, **kwargs: dict) -> None`

**توضیح**: فرم را با company filtering و process filtering initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `company_id` (Optional[int]): شناسه شرکت فعال
- `process_id` (Optional[int]): شناسه process برای فیلتر کردن work lines
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
- مشابه `PerformanceRecordPersonForm.__init__()` اما برای `Machine` و `WorkLine`

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: داده‌های فرم را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
- مشابه `PerformanceRecordPersonForm.clean()`

---

## Formset Factories

### `PerformanceRecordMaterialFormSet`

**توضیح**: Formset factory برای مواد مصرف شده

**Factory**: `forms.inlineformset_factory`

**پارامترها**:
- `parent_model`: `PerformanceRecord`
- `model`: `PerformanceRecordMaterial`
- `form`: `PerformanceRecordMaterialForm`
- `extra`: `0` (مواد از transfer auto-populate می‌شوند)
- `can_delete`: `True`
- `min_num`: `0`
- `validate_min`: `False`

---

### `PerformanceRecordPersonFormSet`

**توضیح**: Formset factory برای پرسنل

**Factory**: `forms.inlineformset_factory`

**پارامترها**:
- `parent_model`: `PerformanceRecord`
- `model`: `PerformanceRecordPerson`
- `form`: `PerformanceRecordPersonForm`
- `extra`: `1` (شروع با 1 خط خالی)
- `can_delete`: `True`
- `min_num`: `0`
- `validate_min`: `False`

---

### `PerformanceRecordMachineFormSet`

**توضیح**: Formset factory برای ماشین‌آلات

**Factory**: `forms.inlineformset_factory`

**پارامترها**:
- `parent_model`: `PerformanceRecord`
- `model`: `PerformanceRecordMachine`
- `form`: `PerformanceRecordMachineForm`
- `extra`: `1` (شروع با 1 خط خالی)
- `can_delete`: `True`
- `min_num`: `0`
- `validate_min`: `False`

---

## استفاده در پروژه

### در Views
```python
class PerformanceRecordCreateView(CreateView):
    model = PerformanceRecord
    form_class = PerformanceRecordForm
    template_name = 'production/performance_record_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add formsets with process_id for filtering work lines
        process_id = None
        if self.object and self.object.order and self.object.order.process:
            process_id = self.object.order.process.pk
        
        context['material_formset'] = PerformanceRecordMaterialFormSet(
            instance=self.object,
            form_kwargs={'company_id': self.request.session.get('active_company_id')}
        )
        context['person_formset'] = PerformanceRecordPersonFormSet(
            instance=self.object,
            form_kwargs={
                'company_id': self.request.session.get('active_company_id'),
                'process_id': process_id
            }
        )
        context['machine_formset'] = PerformanceRecordMachineFormSet(
            instance=self.object,
            form_kwargs={
                'company_id': self.request.session.get('active_company_id'),
                'process_id': process_id
            }
        )
        return context
```

---

## نکات مهم

### 1. Order Filtering
- فقط سفارش‌های با process (`process__isnull=False`) نمایش داده می‌شوند
- `order` باید process داشته باشد

### 2. Transfer Auto-population
- اگر `transfer` انتخاب شود، مواد از transfer auto-populate می‌شوند
- `transfer` باید متعلق به `order` باشد

### 3. Locked Records
- اگر record قفل شده باشد (`is_locked=True`)، تمام فیلدها readonly می‌شوند (به جز `notes`)

### 4. Work Line Filtering
- در `PerformanceRecordPersonForm` و `PerformanceRecordMachineForm`، اگر `process_id` ارائه شود، فقط خطوط کاری مربوط به آن process نمایش داده می‌شوند

### 5. Quantity Validation
- `quantity_actual` نمی‌تواند منفی باشد
- `quantity_waste` نمی‌تواند منفی باشد و نمی‌تواند بیشتر از `quantity_required` باشد
- `work_minutes` نمی‌تواند منفی باشد

### 6. Company Filtering
- تمام queryset ها بر اساس `company_id` فیلتر می‌شوند

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
2. **Permission-based Filtering**: `approved_by` بر اساس permission filtering می‌شود
3. **Process-based Filtering**: `work_line` می‌تواند بر اساس `process_id` فیلتر شود
4. **Read-only Fields**: `quantity_planned` و `unit` read-only هستند
5. **Negative Value Validation**: تمام quantity و time fields نمی‌توانند منفی باشند

