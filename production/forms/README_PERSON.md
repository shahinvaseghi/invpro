# production/forms/person.py - Person Forms (Complete Documentation)

**هدف**: فرم‌های ماژول production برای مدیریت پرسنل

این فایل شامل:
- PersonForm: فرم ایجاد/ویرایش پرسنل

---

## وابستگی‌ها

- `production.models`: `Person`
- `shared.models`: `CompanyUnit`
- `django.forms`
- `django.db.models.Q`
- `django.utils.translation.gettext_lazy`

---

## PersonForm

### `PersonForm(forms.ModelForm)`

**توضیح**: فرم ایجاد/ویرایش پرسنل

**Model**: `Person`

**Extra Fields**:
- `use_personnel_code_as_username` (BooleanField): استفاده از کد پرسنلی به عنوان username
  - Widget: `CheckboxInput` با `id='use_personnel_code'`
  - Required: `False`
  - Initial: `True`
  - Label: `_('Use Personnel Code as Username')`
  - Help Text: `_('If checked, username will be same as personnel code')`

**Fields**:
- `first_name` (CharField): نام
  - Widget: `TextInput`
  - Required: `True`
  - Label: `_('First Name')`
- `last_name` (CharField): نام خانوادگی
  - Widget: `TextInput`
  - Required: `True`
  - Label: `_('Last Name')`
- `first_name_en` (CharField): نام (انگلیسی)
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('First Name (English)')`
- `last_name_en` (CharField): نام خانوادگی (انگلیسی)
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Last Name (English)')`
- `national_id` (CharField): کد ملی
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('National ID')`
- `personnel_code` (CharField): کد پرسنلی
  - Widget: `TextInput` با `id='personnel_code_field'`
  - Required: `False`
  - Label: `_('Personnel Code')`
- `username` (CharField): نام کاربری
  - Widget: `TextInput` با `id='username_field'`
  - Required: `False` (اما در `clean()` validate می‌شود)
  - Label: `_('Username')`
- `phone_number` (CharField): شماره تلفن
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Phone')`
- `mobile_number` (CharField): شماره موبایل
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Mobile')`
- `email` (EmailField): ایمیل
  - Widget: `EmailInput`
  - Required: `False`
  - Label: `_('Email')`
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
- `company_units` (ModelMultipleChoiceField): واحدهای سازمانی (ManyToMany)
  - Widget: `CheckboxSelectMultiple`
  - Required: `False`
  - Label: `_('Company Units')`
  - Help Text: `_('Select one or more organizational units.')` (اگر company_id وجود دارد)

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
   - queryset `company_units` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - `help_text` را تنظیم می‌کند
4. اگر `company_id` وجود ندارد:
   - queryset `company_units` را به `objects.none()` تنظیم می‌کند
   - `help_text` را تنظیم می‌کند: "Please select a company first."
5. `company_units.required = False` تنظیم می‌کند
6. اگر instance موجود است (edit mode) و `username == personnel_code`:
   - `use_personnel_code_as_username.initial = True` تنظیم می‌کند

---

#### `clean(self) -> dict`

**توضیح**: داده‌های فرم را validate می‌کند و username را تنظیم می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `dict`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `use_personnel_code_as_username`, `personnel_code`, `username` را دریافت می‌کند
3. اگر checkbox checked است:
   - اگر `personnel_code` وجود ندارد:
     - `ValidationError` می‌اندازد: "Personnel Code is required when using it as username."
   - `cleaned_data['username'] = personnel_code` تنظیم می‌کند
4. اگر checkbox unchecked است:
   - اگر `username` وجود ندارد:
     - `ValidationError` می‌اندازد: "Username is required when not using personnel code."
5. اگر `company_id` وجود دارد:
   - `company_units` را دریافت می‌کند
   - بررسی می‌کند که تمام units متعلق به شرکت فعال باشند
   - اگر unit دیگری وجود دارد:
     - `ValidationError` می‌اندازد: "Selected units must belong to the active company."
6. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- اگر checkbox checked باشد، `username` به صورت خودکار از `personnel_code` تنظیم می‌شود
- اگر checkbox unchecked باشد، `username` باید به صورت دستی وارد شود
- تمام `company_units` باید متعلق به شرکت فعال باشند

---

## استفاده در پروژه

### در Views
```python
class PersonCreateView(CreateView):
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
```

---

## نکات مهم

### 1. Username Auto-generation
- اگر checkbox `use_personnel_code_as_username` checked باشد، `username` به صورت خودکار از `personnel_code` تنظیم می‌شود
- در edit mode، اگر `username == personnel_code` باشد، checkbox به صورت خودکار checked می‌شود

### 2. Company Units
- ManyToMany relationship با `CompanyUnit`
- می‌تواند چند واحد سازمانی انتخاب کند
- تمام units باید متعلق به شرکت فعال باشند

### 3. Company Filtering
- تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
- `company_units` فقط از شرکت فعال نمایش داده می‌شوند

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
2. **Auto-generation**: `username` می‌تواند از `personnel_code` auto-generate شود
3. **ManyToMany Validation**: `company_units` باید متعلق به شرکت فعال باشند

