# production/forms/product_order.py - Product Order Forms (Complete Documentation)

**هدف**: فرم‌های ماژول production برای مدیریت سفارشات تولید

این فایل شامل:
- ProductOrderForm: فرم ایجاد/ویرایش سفارش تولید

---

## وابستگی‌ها

- `inventory.fields`: `JalaliDateField`
- `production.models`: `ProductOrder`, `BOM`, `Process`
- `shared.models`: `UserCompanyAccess`, `AccessLevelPermission`
- `django.forms`
- `django.contrib.auth.get_user_model`
- `django.utils.translation.gettext_lazy`

---

## ProductOrderForm

### `ProductOrderForm(forms.ModelForm)`

**توضیح**: فرم ایجاد/ویرایش سفارش تولید

**Model**: `ProductOrder`

**Extra Fields**:
- `create_transfer_request` (BooleanField): ایجاد درخواست انتقال از این سفارش
  - Widget: `CheckboxInput`
  - Required: `False`
  - Label: `_('Create Transfer Request')`
  - Help Text: `_('Check to create a transfer to line request from this order')`
- `transfer_approved_by` (ModelChoiceField): تایید کننده درخواست انتقال
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Transfer Request Approver')`
  - Help Text: `_('Select the user who can approve the transfer request')`
  - **نکته**: فقط زمانی نمایش داده می‌شود که `create_transfer_request` checked باشد
  - **نکته**: فقط کاربرانی که permission approve برای `production.transfer_requests` دارند نمایش داده می‌شوند
- `transfer_type` (ChoiceField): نوع انتقال
  - Widget: `RadioSelect` با `class='form-check-input'`
  - Required: `False`
  - Initial: `'full'`
  - Label: `_('نوع انتقال')`
  - Help Text: `_('انتخاب کنید که آیا همه مواد انتقال داده شوند یا مواد از عملیات خاص')`
  - Choices:
    - `'full'`: `_('انتقال همه مواد')`
    - `'operations'`: `_('انتقال عملیات انتخابی')`
- `selected_operations` (MultipleChoiceField): عملیات‌های انتخابی (برای `transfer_type='operations'`)
  - Widget: `CheckboxSelectMultiple` با `class='form-check-input'`
  - Required: `False`
  - Label: `_('انتخاب عملیات')`
  - Help Text: `_('عملیات‌هایی که مواد آنها باید انتقال داده شود را انتخاب کنید')`
  - **نکته**: choices از طریق JavaScript populate می‌شوند

**Fields**:
- `process` (ModelChoiceField): فرآیند تولید (FK to Process)
  - Widget: `Select` با `id='id_process'`
  - Required: `True`
  - Label: `_('Process (فرایند)')`
  - Help Text: `_('Select the process for this production order')`
- `quantity_planned` (DecimalField): مقدار برنامه‌ریزی شده
  - Widget: `NumberInput` با `step='0.000001'`, `min='0'`
  - Required: `True`
  - Label: `_('Quantity')`
  - Help Text: `_('Enter the planned quantity to produce')`
- `approved_by` (ModelChoiceField): تایید کننده (FK to User)
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Approver')`
  - Help Text: `_('Select the user who can approve this order')`
  - **نکته**: فقط کاربرانی که permission approve برای `production.product_orders` دارند نمایش داده می‌شوند
- `due_date` (JalaliDateField): تاریخ سررسید
  - Widget: `JalaliDateInput`
  - Required: `False`
  - Label: `_('Due Date')`
- `priority` (CharField): اولویت
  - Widget: `Select`
  - Required: `False`
  - Label: `_('Priority')`
- `customer_reference` (CharField): مرجع مشتری
  - Widget: `TextInput`
  - Required: `False`
  - Label: `_('Customer Reference')`
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
   - queryset `process` را فیلتر می‌کند (بر اساس company و `is_enabled=1`) با `select_related('finished_item', 'bom')` و مرتب‌سازی بر اساس `finished_item__item_code` و `revision`
   - queryset `approved_by` را فیلتر می‌کند (permission-based برای `production.product_orders`):
     - Access levels با `can_approve=1` برای `production.product_orders` را پیدا می‌کند
     - User IDs با آن access levels را پیدا می‌کند
     - User queryset را فیلتر می‌کند (شامل superusers)
   - queryset `transfer_approved_by` را فیلتر می‌کند (permission-based برای `production.transfer_requests`):
     - Access levels با `can_approve=1` برای `production.transfer_requests` را پیدا می‌کند
     - User IDs با آن access levels را پیدا می‌کند
     - User queryset را فیلتر می‌کند (شامل superusers)
4. اگر `company_id` وجود ندارد:
   - تمام queryset ها را به `objects.none()` تنظیم می‌کند
5. `selected_operations.choices` را به empty list تنظیم می‌کند (از طریق JavaScript populate می‌شود)

---

#### `clean(self) -> dict`

**توضیح**: داده‌های فرم را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `dict`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `process`, `quantity_planned`, `create_transfer_request`, `transfer_approved_by`, `transfer_type`, `selected_operations` را دریافت می‌کند
3. اگر `process` انتخاب نشده است:
   - `ValidationError` می‌اندازد: "Process is required."
4. اگر `quantity_planned` وجود دارد و `<= 0` است:
   - `ValidationError` می‌اندازد: "Quantity must be greater than zero."
5. اگر `create_transfer_request` checked است و `transfer_approved_by` انتخاب نشده است:
   - `ValidationError` می‌اندازد: "Transfer Request Approver is required when creating a transfer request."
6. اگر `create_transfer_request` checked است و `transfer_type == 'operations'` و `selected_operations` خالی است:
   - `ValidationError` می‌اندازد (field-specific): "Please select at least one operation when transferring specific operations."
7. اگر `process` انتخاب شده است:
   - اگر `instance.finished_item_id` تنظیم نشده است:
     - `instance.finished_item = process.finished_item` تنظیم می‌کند (auto-set)
   - اگر `process.bom` وجود دارد و `instance.bom_id` تنظیم نشده است:
     - `instance.bom = process.bom` تنظیم می‌کند (auto-set)
8. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- `process` باید انتخاب شود
- `quantity_planned` باید بیشتر از صفر باشد
- اگر `create_transfer_request` checked باشد، `transfer_approved_by` باید انتخاب شود
- اگر `transfer_type == 'operations'` باشد، حداقل یک عملیات باید انتخاب شود
- `finished_item` به صورت خودکار از `process.finished_item` تنظیم می‌شود
- `bom` به صورت خودکار از `process.bom` تنظیم می‌شود (اگر وجود داشته باشد)

---

## استفاده در پروژه

### در Views
```python
class ProductOrderCreateView(CreateView):
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'production/product_order_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        
        # Handle transfer request creation if checkbox is checked
        if form.cleaned_data.get('create_transfer_request'):
            # Create transfer request logic here
            pass
        
        return super().form_valid(form)
```

---

## نکات مهم

### 1. Process Selection
- `process` باید انتخاب شود
- `finished_item` به صورت خودکار از `process.finished_item` تنظیم می‌شود
- `bom` به صورت خودکار از `process.bom` تنظیم می‌شود (اگر وجود داشته باشد)

### 2. Transfer Request Creation
- اگر checkbox `create_transfer_request` checked باشد، می‌تواند درخواست انتقال ایجاد کند
- در این صورت، `transfer_approved_by` باید انتخاب شود
- `transfer_type` می‌تواند `'full'` (همه مواد) یا `'operations'` (عملیات انتخابی) باشد
- اگر `transfer_type == 'operations'` باشد، `selected_operations` باید حداقل یک عملیات داشته باشد

### 3. Permission-based Filtering
- `approved_by`: فقط کاربرانی که permission approve برای `production.product_orders` دارند
- `transfer_approved_by`: فقط کاربرانی که permission approve برای `production.transfer_requests` دارند

### 4. Company Filtering
- تمام queryset ها بر اساس `company_id` فیلتر می‌شوند

---

## الگوهای مشترک

1. **Company Filtering**: تمام queryset ها بر اساس `company_id` فیلتر می‌شوند
2. **Permission-based Filtering**: `approved_by` و `transfer_approved_by` بر اساس permission filtering می‌شوند
3. **Auto-set Fields**: `finished_item` به صورت خودکار از `process.finished_item` و `bom` از `process.bom` تنظیم می‌شوند
4. **Transfer Type**: می‌تواند `'full'` (همه مواد) یا `'operations'` (عملیات انتخابی) باشد
5. **Selected Operations**: choices از طریق JavaScript populate می‌شوند و فقط زمانی required است که `transfer_type == 'operations'` باشد

