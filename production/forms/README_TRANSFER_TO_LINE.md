# production/forms/transfer_to_line.py - Transfer to Line Forms (Complete Documentation)

**هدف**: فرم‌های ماژول production برای مدیریت درخواست‌های انتقال به خط تولید

این فایل شامل:
- TransferToLineForm: فرم header برای درخواست انتقال
- TransferToLineItemForm: فرم خط مواد اضافی (extra requests)
- TransferToLineItemFormSet: Formset factory

---

## وابستگی‌ها

- `inventory.models`: `Item`, `Warehouse`, `ItemType`, `ItemCategory`, `ItemSubcategory`
- `inventory.fields`: `JalaliDateField`
- `production.models`: `TransferToLine`, `TransferToLineItem`, `ProductOrder`, `WorkCenter`
- `django.forms`
- `django.forms.inlineformset_factory`
- `django.utils.translation.gettext_lazy`

---

## TransferToLineForm

### `TransferToLineForm(forms.ModelForm)`

**توضیح**: فرم ایجاد/ویرایش درخواست انتقال به خط تولید

**Model**: `TransferToLine`

**Fields**:
- `order` (ModelChoiceField): سفارش تولید (FK to ProductOrder)
  - Widget: `Select`
  - Required: `True`
  - Label: `_('Product Order')`
  - Help Text: `_('Select the product order for this transfer request')`
  - **نکته**: فقط سفارش‌های approved نمایش داده می‌شوند
- `transfer_date` (JalaliDateField): تاریخ انتقال
  - Widget: `JalaliDateInput`
  - Required: `True`
  - Label: `_('Transfer Date')`
- `approved_by` (ModelChoiceField): تایید کننده (FK to User)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Approver')`
  - Help Text: `_('Select the user who can approve this transfer request')`
  - **نکته**: فقط کاربرانی که permission approve برای `production.transfer_requests` دارند نمایش داده می‌شوند
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
   - queryset `order` را فیلتر می‌کند (بر اساس company، `is_enabled=1`، و `status='approved'`)
   - queryset `approved_by` را فیلتر می‌کند:
     - Access levels با `can_approve=1` برای `production.transfer_requests` را پیدا می‌کند
     - User IDs با آن access levels را پیدا می‌کند
     - User queryset را فیلتر می‌کند
4. اگر `company_id` وجود ندارد:
   - تمام queryset ها را به `objects.none()` تنظیم می‌کند

---

#### `clean(self) -> dict`

**توضیح**: داده‌های فرم را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `dict`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `order` را دریافت می‌کند
3. اگر `order` انتخاب نشده است:
   - `ValidationError` می‌اندازد: "Product Order is required."
4. اگر `order` انتخاب شده و `order.bom` وجود ندارد:
   - `ValidationError` می‌اندازد: "Selected product order must have a BOM."
5. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- `order` باید انتخاب شود
- `order` باید BOM داشته باشد

---

## TransferToLineItemForm

### `TransferToLineItemForm(forms.ModelForm)`

**توضیح**: فرم خط مواد اضافی (extra requests) برای درخواست انتقال

**Model**: `TransferToLineItem`

**Extra Filter Fields (not saved to DB)**:
- `material_type` (ModelChoiceField): فیلتر نوع ماده
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Material Type')`
  - Help Text: `_('Filter materials by type')`
- `material_category_filter` (ModelChoiceField): فیلتر دسته ماده
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Category')`
  - Help Text: `_('Filter materials by category')`
- `material_subcategory_filter` (ModelChoiceField): فیلتر زیردسته ماده
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Subcategory')`
  - Help Text: `_('Filter materials by subcategory')`

**Fields**:
- `material_item` (ModelChoiceField): ماده اولیه (FK to Item)
  - Widget: `Select`
  - Required: `True`
  - Label: `_('Material Item')`
- `quantity_required` (DecimalField): مقدار مورد نیاز
  - Widget: `NumberInput` با `step='0.000001'`, `min='0'`
  - Required: `True`
  - Label: `_('Quantity Required')`
- `unit` (CharField): واحد اندازه‌گیری
  - Widget: `Select` (disabled تا item انتخاب شود)
  - Required: `True`
  - Label: `_('Unit')`
- `source_warehouse` (ModelChoiceField): انبار مبدا (FK to Warehouse)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Source Warehouse')`
- `destination_work_center` (ModelChoiceField): مرکز کاری مقصد (FK to WorkCenter)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Destination Work Center')`
- `material_scrap_allowance` (DecimalField): درصد ضایعات (0-100)
  - Widget: `NumberInput` با `step='0.01'`, `min='0'`, `max='100'`
  - Required: `False`
  - Label: `_('Scrap Allowance (%)')`
- `notes` (TextField): یادداشت‌ها
  - Widget: `Textarea` با `rows=2`
  - Required: `False`
  - Label: `_('Notes')`

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
   - queryset `material_type` را فیلتر می‌کند
   - queryset های `material_category_filter` و `material_subcategory_filter` را به `objects.none()` تنظیم می‌کند (populated via JavaScript)
   - queryset `material_item` را فیلتر می‌کند
   - queryset `source_warehouse` را فیلتر می‌کند
   - queryset `destination_work_center` را فیلتر می‌کند
   - `unit.widget.attrs['disabled'] = True` تنظیم می‌کند (populated via JavaScript)
   - اگر instance موجود است (edit mode):
     - filter fields را از `material_item` populate می‌کند
4. اگر `company_id` وجود ندارد:
   - تمام queryset ها را به `objects.none()` تنظیم می‌کند

---

#### `clean(self) -> dict`

**توضیح**: داده‌های فرم را validate می‌کند و filter fields را از `cleaned_data` حذف می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `dict`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. Filter fields را از `cleaned_data` حذف می‌کند
3. `material_item`, `quantity_required`, `unit` را دریافت می‌کند
4. اگر `material_item` انتخاب نشده است:
   - `ValidationError` می‌اندازد: "Material item is required."
5. اگر `quantity_required` وجود دارد و `<= 0` است:
   - `ValidationError` می‌اندازد: "Quantity must be greater than zero."
6. اگر `material_item` انتخاب شده و `unit` وجود ندارد:
   - `ValidationError` می‌اندازد: "Unit is required for the selected material."
7. `cleaned_data` را برمی‌گرداند

---

#### `full_clean(self) -> None`

**توضیح**: Filter fields را از validation حذف می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**: ندارد

**منطق**:
- مشابه `BOMMaterialLineForm.full_clean()`

---

## TransferToLineItemFormSet

### `TransferToLineItemFormSet`

**توضیح**: Formset factory برای extra request items

**Factory**: `forms.inlineformset_factory`

**پارامترها**:
- `parent_model`: `TransferToLine`
- `model`: `TransferToLineItem`
- `form`: `TransferToLineItemForm`
- `extra`: `1` (شروع با 1 خط خالی)
- `can_delete`: `True` (نمایش checkbox DELETE)
- `min_num`: `0` (می‌تواند صفر باشد - همه مواد می‌توانند از BOM بیایند)
- `validate_min`: `False` (validation minimum انجام نمی‌شود)

**استفاده**:
```python
formset = TransferToLineItemFormSet(
    data=request.POST,
    instance=transfer_instance,
    form_kwargs={'company_id': company_id}
)
```

---

## استفاده در پروژه

### در Views
```python
class TransferToLineCreateView(CreateView):
    model = TransferToLine
    form_class = TransferToLineForm
    template_name = 'production/transfer_to_line_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = TransferToLineItemFormSet(
                self.request.POST,
                instance=self.object,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        else:
            context['formset'] = TransferToLineItemFormSet(
                instance=self.object,
                form_kwargs={'company_id': self.request.session.get('active_company_id')}
            )
        return context
```

---

## نکات مهم

### 1. Product Order Filtering
- فقط سفارش‌های approved (`status='approved'`) نمایش داده می‌شوند
- `order` باید BOM داشته باشد

### 2. Extra Request Items
- این items مواد اضافی هستند که در BOM نیستند
- می‌تواند صفر باشد (همه مواد از BOM می‌آیند)
- Filter fields برای cascading dropdowns استفاده می‌شوند

### 3. Unit Selection
- `unit` تا زمانی که `material_item` انتخاب نشود disabled است
- از API endpoint `/inventory/api/item-units/?item_id=<id>` populate می‌شود

### 4. Company Filtering
- تمام queryset ها بر اساس `company_id` فیلتر می‌شوند

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
2. **Permission-based Filtering**: `approved_by` بر اساس permission filtering می‌شود
3. **Filter Fields Removal**: Filter fields از `cleaned_data` حذف می‌شوند
4. **Cascading Filters**: Filter fields برای cascading dropdowns استفاده می‌شوند

