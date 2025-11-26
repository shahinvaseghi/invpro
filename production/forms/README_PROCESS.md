# production/forms/process.py - Process Forms (Complete Documentation)

**هدف**: فرم‌های ماژول production برای مدیریت فرآیندهای تولید

این فایل شامل:
- ProcessForm: فرم ایجاد/ویرایش فرآیند تولید

---

## وابستگی‌ها

- `production.models`: `Process`, `BOM`, `WorkLine`
- `shared.models`: `UserCompanyAccess`, `AccessLevelPermission`
- `django.forms`
- `django.contrib.auth.get_user_model`
- `django.utils.translation.gettext_lazy`

---

## ProcessForm

### `ProcessForm(forms.ModelForm)`

**توضیح**: فرم ایجاد/ویرایش فرآیند تولید

**Model**: `Process`

**Fields**:
- `bom` (ModelChoiceField): فهرست مواد اولیه (BOM) - اختیاری
  - Widget: `Select`
  - Required: `False`
  - Label: `_('فهرست مواد اولیه (BOM)')`
  - Help Text: `_('Select the BOM for this process')`
- `work_lines` (ModelMultipleChoiceField): خطوط کاری (ManyToMany)
  - Widget: `SelectMultiple` با `size='10'`
  - Required: `False`
  - Label: `_('خطوط کاری')`
  - Help Text: `_('یک یا چند خط کاری را برای این فرایند انتخاب کنید')`
- `revision` (CharField): نسخه - اختیاری
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('نسخه')`
- `description` (CharField): توضیحات
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('توضیحات')`
- `is_primary` (PositiveSmallIntegerField): فرایند اصلی
  - Widget: `Select`
  - Required: `False`
  - Label: `_('فرایند اصلی')`
- `approved_by` (ModelChoiceField): تایید کننده (FK to User)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('تایید کننده')`
  - **نکته**: فقط کاربرانی که permission approve برای `production.processes` دارند نمایش داده می‌شوند
- `notes` (TextField): یادداشت‌ها
  - Widget: `Textarea` با `rows=3`
  - Required: `False`
  - Label: `_('یادداشت‌ها')`
- `is_enabled` (PositiveSmallIntegerField): وضعیت (فعال/غیرفعال)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('وضعیت')`
- `sort_order` (PositiveSmallIntegerField): ترتیب نمایش
  - Widget: `NumberInput`
  - Required: `False`
  - Label: `_('ترتیب نمایش')`

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
2. اگر `company_id` وجود دارد:
   - queryset `bom` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - `bom.required = False` تنظیم می‌کند
   - `revision.required = False` تنظیم می‌کند
   - `is_primary.required = False` تنظیم می‌کند
   - queryset `work_lines` را فیلتر می‌کند (بر اساس company و `is_enabled=1`)
   - queryset `approved_by` را فیلتر می‌کند:
     - Access levels با `can_approve=1` برای `production.processes` را پیدا می‌کند
     - User IDs با آن access levels را پیدا می‌کند
     - User queryset را فیلتر می‌کند
3. اگر `company_id` وجود ندارد:
   - تمام queryset ها را به `objects.none()` تنظیم می‌کند
4. اگر instance موجود است (edit mode):
   - `work_lines.initial` را از `instance.work_lines.all()` تنظیم می‌کند

---

#### `save(self, commit: bool = True) -> Process`

**توضیح**: instance را ذخیره می‌کند.

**پارامترهای ورودی**:
- `commit` (bool): آیا باید در database ذخیره شود (default: `True`)

**مقدار بازگشتی**:
- `Process`: instance ذخیره شده

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
   - `instance.work_lines.set(self.cleaned_data['work_lines'])` را فراخوانی می‌کند

**نکات مهم**:
- `work_lines` یک ManyToMany field است
- باید بعد از `save()` فراخوانی شود
- از `set()` برای replace کردن روابط استفاده می‌شود

---

## استفاده در پروژه

### در Views
```python
class ProcessCreateView(CreateView):
    model = Process
    form_class = ProcessForm
    template_name = 'production/process_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
```

---

## نکات مهم

### 1. BOM Field
- اختیاری است (`required=False`)
- اگر BOM انتخاب شود، `finished_item` به صورت خودکار از `BOM.finished_item` تنظیم می‌شود

### 2. Work Lines
- ManyToMany relationship با `WorkLine`
- می‌تواند چند خط کاری انتخاب کند
- در edit mode، initial values از `instance.work_lines.all()` تنظیم می‌شوند

### 3. Approved By Filtering
- فقط کاربرانی که permission approve برای `production.processes` دارند نمایش داده می‌شوند
- از `AccessLevelPermission` و `UserCompanyAccess` برای filtering استفاده می‌شود
- Superuser ها همیشه می‌توانند approve کنند (اگر در queryset باشند)

### 4. Company Filtering
- تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
- BOMs و WorkLines فقط از شرکت فعال نمایش داده می‌شوند

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
2. **Permission-based Filtering**: `approved_by` بر اساس permission filtering می‌شود
3. **ManyToMany Handling**: `work_lines` با `save_m2m()` و `set()` مدیریت می‌شود

