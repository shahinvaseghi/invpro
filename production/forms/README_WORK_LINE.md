# production/forms/work_line.py - Work Line Forms (Complete Documentation)

**هدف**: فرم‌های ماژول production برای مدیریت خطوط کاری

این فایل شامل:
- WorkLineForm: فرم ایجاد/ویرایش خط کاری

---

## وابستگی‌ها

- `production.models`: `WorkLine`, `Person`, `Machine`
- `inventory.models`: `Warehouse` (optional - فقط اگر ماژول inventory نصب باشد)
- `django.forms`
- `django.utils.translation.gettext_lazy`

---

## WorkLineForm

### `WorkLineForm(forms.ModelForm)`

**توضیح**: فرم ایجاد/ویرایش خط کاری

**Model**: `WorkLine`

**Fields**:
- `warehouse` (ModelChoiceField): انبار - اختیاری (FK to Warehouse)
  - Widget: `Select` (یا `HiddenInput` اگر inventory module نصب نباشد)
  - Required: `False`
  - Label: `_('انبار (اختیاری)')`
  - **نکته**: فقط اگر ماژول inventory نصب باشد نمایش داده می‌شود
- `name` (CharField): نام (فارسی)
  - Widget: `TextInput`
  - Required: `True`
  - Label: `_('نام (فارسی)')`
- `name_en` (CharField): نام (انگلیسی)
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('نام (انگلیسی)')`
- `description` (CharField): توضیحات
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('توضیحات')`
- `notes` (TextField): یادداشت‌ها
  - Widget: `Textarea` با `rows=3`
  - Required: `False`
  - Label: `_('یادداشت‌ها')`
- `sort_order` (PositiveSmallIntegerField): ترتیب نمایش
  - Widget: `NumberInput`
  - Required: `False`
  - Label: `_('ترتیب نمایش')`
- `is_enabled` (PositiveSmallIntegerField): وضعیت (فعال/غیرفعال)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('وضعیت')`
- `personnel` (ModelMultipleChoiceField): پرسنل (ManyToMany)
  - Widget: `SelectMultiple` با `size='10'`
  - Required: `False`
  - Label: `_('پرسنل')`
  - Help Text: `_('یک یا چند پرسنل را برای این خط کاری انتخاب کنید')`
- `machines` (ModelMultipleChoiceField): ماشین‌ها (ManyToMany)
  - Widget: `SelectMultiple` با `size='10'`
  - Required: `False`
  - Label: `_('ماشین‌ها')`
  - Help Text: `_('یک یا چند ماشین را برای این خط کاری انتخاب کنید')`

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
2. اگر `company_id` وجود دارد:
   - اگر `Warehouse` موجود است (inventory module نصب است):
     - queryset `warehouse` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - اگر `Warehouse` موجود نیست:
     - `warehouse.widget = HiddenInput()` تنظیم می‌کند
     - `warehouse.required = False` تنظیم می‌کند
   - queryset `personnel` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - queryset `machines` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
3. اگر `company_id` وجود ندارد:
   - تمام queryset ها را به `objects.none()` تنظیم می‌کند
   - اگر `Warehouse` موجود نیست، `warehouse.widget = HiddenInput()` تنظیم می‌کند
4. اگر instance موجود است (edit mode):
   - `personnel.initial = instance.personnel.all()` تنظیم می‌کند
   - `machines.initial = instance.machines.all()` تنظیم می‌کند

---

#### `save(self, commit: bool = True) -> WorkLine`

**توضیح**: instance را ذخیره می‌کند.

**پارامترهای ورودی**:
- `commit` (bool): آیا باید در database ذخیره شود (default: `True`)

**مقدار بازگشتی**:
- `WorkLine`: instance ذخیره شده

**منطق**:
1. `super().save(commit=False)` را فراخوانی می‌کند
2. اگر `commit=True`:
   - `instance.save()` را فراخوانی می‌کند
   - `self.save_m2m()` را فراخوانی می‌کند
3. instance را برمی‌گرداند

---

#### `save_m2m(self) -> None`

**توضیح**: روابط ManyToMany را ذخیره می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().save_m2m()` را فراخوانی می‌کند
2. اگر `instance.pk` وجود دارد:
   - `instance.personnel.set(self.cleaned_data['personnel'])` را فراخوانی می‌کند
   - `instance.machines.set(self.cleaned_data['machines'])` را فراخوانی می‌کند

**نکات مهم**:
- `personnel` و `machines` ManyToMany fields هستند
- باید بعد از `save()` فراخوانی شود
- از `set()` برای replace کردن روابط استفاده می‌شود

---

## استفاده در پروژه

### در Views
```python
class WorkLineCreateView(CreateView):
    model = WorkLine
    form_class = WorkLineForm
    template_name = 'production/work_line_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
```

---

## نکات مهم

### 1. Warehouse Field
- اختیاری است (`required=False`)
- فقط اگر ماژول inventory نصب باشد نمایش داده می‌شود
- اگر inventory module نصب نباشد، به `HiddenInput` تبدیل می‌شود

### 2. Personnel and Machines
- ManyToMany relationships با `Person` و `Machine`
- می‌تواند چند پرسنل و ماشین انتخاب کند
- در edit mode، initial values از `instance.personnel.all()` و `instance.machines.all()` تنظیم می‌شوند

### 3. Company Filtering
- تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
- Personnel و Machines فقط از شرکت فعال نمایش داده می‌شوند

### 4. Optional Dependency
- `Warehouse` یک optional dependency است
- اگر inventory module نصب نباشد، `ImportError` catch می‌شود و `Warehouse = None` تنظیم می‌شود

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
2. **ManyToMany Handling**: `personnel` و `machines` با `save_m2m()` و `set()` مدیریت می‌شوند
3. **Optional Dependency**: `Warehouse` یک optional dependency است

