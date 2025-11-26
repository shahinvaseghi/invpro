# production/forms/machine.py - Machine Forms (Complete Documentation)

**هدف**: فرم‌های ماژول production برای مدیریت ماشین‌آلات

این فایل شامل:
- MachineForm: فرم ایجاد/ویرایش ماشین

---

## وابستگی‌ها

- `production.models`: `Machine`, `WorkCenter`
- `django.forms`
- `django.utils.translation.gettext_lazy`

---

## MachineForm

### `MachineForm(forms.ModelForm)`

**توضیح**: فرم ایجاد/ویرایش ماشین

**Model**: `Machine`

**Fields**:
- `name` (CharField): نام (فارسی)
  - Widget: `TextInput`
  - Required: `True`
  - Label: `_('Name')`
- `name_en` (CharField): نام (انگلیسی)
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Name (English)')`
- `machine_type` (CharField): نوع ماشین
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Machine Type')`
- `work_center` (ModelChoiceField): مرکز کاری (FK to WorkCenter)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Work Center')`
- `manufacturer` (CharField): سازنده
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Manufacturer')`
- `model_number` (CharField): شماره مدل
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Model Number')`
- `serial_number` (CharField): شماره سریال
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Serial Number')`
- `purchase_date` (DateField): تاریخ خرید
  - Widget: `DateInput` با `type='date'`
  - Required: `False`
  - Label: `_('Purchase Date')`
- `installation_date` (DateField): تاریخ نصب
  - Widget: `DateInput` با `type='date'`
  - Required: `False`
  - Label: `_('Installation Date')`
- `capacity_specs` (TextField): مشخصات ظرفیت
  - Widget: `Textarea` با `rows=3`
  - Required: `False`
  - Label: `_('Capacity Specifications')`
- `maintenance_schedule` (TextField): برنامه نگهداری
  - Widget: `Textarea` با `rows=3`
  - Required: `False`
  - Label: `_('Maintenance Schedule')`
- `last_maintenance_date` (DateField): تاریخ آخرین نگهداری
  - Widget: `DateInput` با `type='date'`
  - Required: `False`
  - Label: `_('Last Maintenance Date')`
- `next_maintenance_date` (DateField): تاریخ نگهداری بعدی
  - Widget: `DateInput` با `type='date'`
  - Required: `False`
  - Label: `_('Next Maintenance Date')`
- `status` (CharField): وضعیت
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Status')`
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
2. `self.company_id` را از `company_id` یا `instance.company_id` تنظیم می‌کند
3. اگر `company_id` وجود دارد:
   - queryset `work_center` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
4. اگر `company_id` وجود ندارد:
   - queryset `work_center` را به `objects.none()` تنظیم می‌کند

---

## استفاده در پروژه

### در Views
```python
class MachineCreateView(CreateView):
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
```

---

## نکات مهم

### 1. Work Center Filtering
- `work_center` queryset بر اساس `company_id` فیلتر می‌شود
- فقط WorkCenter های فعال (`is_enabled=1`) نمایش داده می‌شوند

### 2. Company Filtering
- تمام queryset ها بر اساس `company_id` فیلتر می‌شوند

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `company_id` فیلتر می‌شوند

