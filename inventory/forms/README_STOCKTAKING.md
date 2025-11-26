# inventory/forms/stocktaking.py - Stocktaking Forms (Complete Documentation)

**هدف**: فرم‌های ماژول inventory برای مدیریت stocktaking (انبارگردانی)

این فایل شامل forms برای:
- Stocktaking Deficit (کسری انبارگردانی)
- Stocktaking Surplus (مازاد انبارگردانی)
- Stocktaking Record (سند انبارگردانی)

---

## وابستگی‌ها

- `inventory.models`: `StocktakingDeficit`, `StocktakingSurplus`, `StocktakingRecord`
- `inventory.forms.base`: `StocktakingBaseForm`, `generate_document_code`
- `django.forms`
- `django.utils.timezone`
- `django.utils.translation.gettext_lazy`

---

## Stocktaking Deficit Form

### `StocktakingDeficitForm(StocktakingBaseForm)`

**توضیح**: فرم ایجاد/ویرایش کسری انبارگردانی

**Model**: `StocktakingDeficit`

**Inheritance**: `StocktakingBaseForm`

**Fields**:
- `document_code` (HiddenInput): کد سند (auto-generated)
- `document_date` (HiddenInput): تاریخ سند (auto-generated)
- `stocktaking_session_id` (NumberInput): شناسه جلسه انبارگردانی
- `item` (ModelChoiceField): کالا (FK to Item)
- `warehouse` (ModelChoiceField): انبار (FK to Warehouse)
- `unit` (ChoiceField): واحد اندازه‌گیری (required)
- `quantity_expected` (NumberInput, step=0.001): مقدار مورد انتظار
- `quantity_counted` (NumberInput, step=0.001): مقدار شمارش شده
- `quantity_adjusted` (NumberInput, step=0.001, readonly): مقدار تعدیل شده (auto-calculated)
- `valuation_method` (TextInput): روش ارزش‌گذاری
- `unit_cost` (NumberInput, step=0.001): هزینه واحد
- `total_cost` (NumberInput, step=0.001): هزینه کل (auto-calculated)
- `reason_code` (TextInput): کد دلیل
- `investigation_reference` (TextInput): مرجع بررسی
- `adjustment_metadata` (HiddenInput): metadata تعدیل

**متدها**:

#### `clean(self) -> Dict[str, Any]`

**توضیح**: محاسبات مقدار را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `quantity_expected` و `quantity_counted` را دریافت می‌کند
3. اگر هر دو وجود دارند:
   - `quantity_adjusted = quantity_expected - quantity_counted` را محاسبه می‌کند
   - اگر `quantity_adjusted < 0`:
     - خطا اضافه می‌کند: "Counted quantity cannot exceed expected balance for a deficit document."
   - `cleaned_data['quantity_adjusted']` را تنظیم می‌کند
4. `unit_cost` و `quantity_adjusted` را دریافت می‌کند
5. اگر هر دو وجود دارند:
   - `total_cost = quantity_adjusted * unit_cost` را محاسبه می‌کند
   - `cleaned_data['total_cost']` را تنظیم می‌کند
6. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- `quantity_adjusted` به صورت خودکار محاسبه می‌شود
- `total_cost` به صورت خودکار محاسبه می‌شود
- برای deficit، `quantity_counted` باید کمتر از `quantity_expected` باشد

---

#### `save(self, commit: bool = True) -> StocktakingDeficit`

**توضیح**: instance را با کد سند auto-generated ذخیره می‌کند.

**پارامترهای ورودی**:
- `commit` (bool): آیا باید در database ذخیره شود (default: `True`)

**مقدار بازگشتی**:
- `StocktakingDeficit`: instance ذخیره شده

**منطق**:
1. `super().save(commit=False)` را فراخوانی می‌کند
2. اگر `document_code` وجود ندارد:
   - `generate_document_code(StocktakingDeficit, company_id, "STD")` را فراخوانی می‌کند
   - `instance.document_code` را تنظیم می‌کند
3. اگر `document_date` وجود ندارد:
   - `instance.document_date = timezone.now().date()` را تنظیم می‌کند
4. `instance.item_code` را از `instance.item.item_code` تنظیم می‌کند (cache)
5. `instance.warehouse_code` را از `instance.warehouse.public_code` تنظیم می‌کند (cache)
6. اگر `commit=True`:
   - `instance.save()` را فراخوانی می‌کند
   - `self.save_m2m()` را فراخوانی می‌کند
7. instance را برمی‌گرداند

**Document Code Format**: `STD-{YYYYMM}-{SEQUENCE}` (مثلاً `STD-202511-000001`)

---

## Stocktaking Surplus Form

### `StocktakingSurplusForm(StocktakingBaseForm)`

**توضیح**: فرم ایجاد/ویرایش مازاد انبارگردانی

**Model**: `StocktakingSurplus`

**Inheritance**: `StocktakingBaseForm`

**Fields**:
- مشابه `StocktakingDeficitForm` اما با منطق متفاوت برای `quantity_adjusted`

**متدها**:

#### `clean(self) -> Dict[str, Any]`

**توضیح**: محاسبات مقدار را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. `quantity_expected` و `quantity_counted` را دریافت می‌کند
3. اگر هر دو وجود دارند:
   - `quantity_adjusted = quantity_counted - quantity_expected` را محاسبه می‌کند
   - اگر `quantity_adjusted < 0`:
     - خطا اضافه می‌کند: "Counted quantity cannot be less than expected for a surplus document."
   - `cleaned_data['quantity_adjusted']` را تنظیم می‌کند
4. `unit_cost` و `quantity_adjusted` را دریافت می‌کند
5. اگر هر دو وجود دارند:
   - `total_cost = quantity_adjusted * unit_cost` را محاسبه می‌کند
   - `cleaned_data['total_cost']` را تنظیم می‌کند
6. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- برای surplus، `quantity_counted` باید بیشتر از `quantity_expected` باشد
- فرمول: `quantity_adjusted = quantity_counted - quantity_expected` (برعکس deficit)

---

#### `save(self, commit: bool = True) -> StocktakingSurplus`

**توضیح**: instance را با کد سند auto-generated ذخیره می‌کند.

**پارامترهای ورودی**:
- `commit` (bool): آیا باید در database ذخیره شود (default: `True`)

**مقدار بازگشتی**:
- `StocktakingSurplus`: instance ذخیره شده

**منطق**:
- مشابه `StocktakingDeficitForm.save()` اما با prefix `"STS"`

**Document Code Format**: `STS-{YYYYMM}-{SEQUENCE}` (مثلاً `STS-202511-000001`)

---

## Stocktaking Record Form

### `StocktakingRecordForm(StocktakingBaseForm)`

**توضیح**: فرم ایجاد/ویرایش سند انبارگردانی

**Model**: `StocktakingRecord`

**Inheritance**: `StocktakingBaseForm`

**Constants**:
- `APPROVAL_STATUS_CHOICES`: لیست انتخاب وضعیت تایید
  - `'pending'`: در انتظار تایید
  - `'approved'`: تایید شده
  - `'rejected'`: رد شده

**Fields**:
- `document_code` (HiddenInput): کد سند (auto-generated)
- `document_date` (HiddenInput): تاریخ سند (auto-generated)
- `stocktaking_session_id` (NumberInput): شناسه جلسه انبارگردانی
- `inventory_snapshot_time` (HiddenInput): زمان snapshot موجودی (auto-generated)
- `confirmed_by` (ModelChoiceField): کاربر تاییدکننده (FK to User)
- `confirmation_notes` (Textarea, rows=3): یادداشت‌های تایید
- `variance_document_ids` (HiddenInput): شناسه‌های اسناد variance (JSON array)
- `variance_document_codes` (HiddenInput): کدهای اسناد variance (JSON array)
- `final_inventory_value` (NumberInput, step=0.01): ارزش نهایی موجودی
- `approver` (ModelChoiceField): کاربر تاییدکننده (FK to User, filtered by permission)
- `approval_status` (ChoiceField): وضعیت تایید (pending/approved/rejected)
- `approved_at` (HiddenInput): زمان تایید (auto-set when status=approved)
- `approver_notes` (Textarea, rows=3): یادداشت‌های تاییدکننده
- `record_metadata` (HiddenInput): metadata سند (JSON object)

**متدها**:

#### `__init__(self, *args, user=None, **kwargs) -> None`

**توضیح**: فرم را با user برای permission checks initialize می‌کند.

**پارامترهای ورودی**:
- `*args`: آرگومان‌های positional
- `user` (Optional[User]): کاربر برای permission checks
- `**kwargs`: آرگومان‌های keyword

**مقدار بازگشتی**: ندارد

**منطق**:
1. `super().__init__(user=user, **kwargs)` را فراخوانی می‌کند
2. اگر instance جدید است:
   - `approval_status.initial = 'pending'` را تنظیم می‌کند
3. فیلد `approved_at` را به `HiddenInput` تغییر می‌دهد
4. اگر instance موجود است و `approval_status` وجود دارد:
   - اگر `user` و `instance.approver_id` وجود دارند:
     - اگر `user.id != instance.approver_id`:
       - `approval_status.widget.attrs['disabled'] = 'disabled'` را تنظیم می‌کند
       - `help_text` را تنظیم می‌کند: "فقط تأییدکننده انتخاب شده می‌تواند وضعیت را تغییر دهد"
5. فیلدهای JSON را initialize می‌کند:
   - `variance_document_ids`: `[]` (اگر وجود ندارد)
   - `variance_document_codes`: `[]` (اگر وجود ندارد)
   - `record_metadata`: `{}` (اگر وجود ندارد)
6. اگر instance جدید است:
   - `document_date.initial = timezone.now().date()` را تنظیم می‌کند
   - `inventory_snapshot_time.initial = timezone.now()` را تنظیم می‌کند

**نکات مهم**:
- فقط approver انتخاب شده می‌تواند `approval_status` را تغییر دهد
- اگر approver انتخاب نشده باشد، هر کسی می‌تواند status را تغییر دهد

---

#### `clean(self) -> Dict[str, Any]`

**توضیح**: تغییرات وضعیت تایید را validate می‌کند.

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `Dict[str, Any]`: داده‌های تمیز شده

**منطق**:
1. `super().clean()` را فراخوانی می‌کند
2. اگر instance موجود است و `approval_status` در `cleaned_data` وجود دارد:
   - اگر `user` و `instance.approver_id` وجود دارند:
     - اگر `user.id != instance.approver_id`:
       - اگر `approval_status` تغییر کرده است:
         - خطا اضافه می‌کند: "فقط تأییدکننده انتخاب شده می‌تواند وضعیت را تغییر دهد"
         - `cleaned_data['approval_status']` را به مقدار قبلی بازمی‌گرداند
3. `cleaned_data` را برمی‌گرداند

**نکات مهم**:
- Server-side permission check برای جلوگیری از تغییر غیرمجاز `approval_status`
- اگر کاربر approver نیست، status به مقدار قبلی بازمی‌گردد

---

#### `save(self, commit: bool = True) -> StocktakingRecord`

**توضیح**: instance را با کد سند auto-generated و approval handling ذخیره می‌کند.

**پارامترهای ورودی**:
- `commit` (bool): آیا باید در database ذخیره شود (default: `True`)

**مقدار بازگشتی**:
- `StocktakingRecord`: instance ذخیره شده

**منطق**:
1. `super().save(commit=False)` را فراخوانی می‌کند
2. اگر `document_code` وجود ندارد:
   - `generate_document_code(StocktakingRecord, company_id, "STR")` را فراخوانی می‌کند
   - `instance.document_code` را تنظیم می‌کند
3. اگر `document_date` وجود ندارد:
   - `instance.document_date = timezone.now().date()` را تنظیم می‌کند
4. اگر `inventory_snapshot_time` وجود ندارد:
   - `instance.inventory_snapshot_time = timezone.now()` را تنظیم می‌کند
5. اگر `confirmed_by_id` وجود دارد:
   - `instance.confirmed_by_code = instance.confirmed_by.username` را تنظیم می‌کند (cache)
6. اگر `approver_id` وجود دارد:
   - `instance.approver_notes = instance.approver_notes or ''` را تنظیم می‌کند
7. اگر `approval_status == 'approved'` و `approved_at` وجود ندارد:
   - `instance.approved_at = timezone.now()` را تنظیم می‌کند
8. اگر `approval_status` در `('pending', 'rejected')` است:
   - `instance.approved_at = None` را تنظیم می‌کند
9. اگر `commit=True`:
   - `instance.save()` را فراخوانی می‌کند
   - `self.save_m2m()` را فراخوانی می‌کند
10. instance را برمی‌گرداند

**Document Code Format**: `STR-{YYYYMM}-{SEQUENCE}` (مثلاً `STR-202511-000001`)

**نکات مهم**:
- `approved_at` به صورت خودکار تنظیم می‌شود وقتی `approval_status` به `'approved'` تغییر می‌کند
- `approved_at` پاک می‌شود وقتی `approval_status` به `'pending'` یا `'rejected'` تغییر می‌کند

---

## استفاده در پروژه

### در Views
```python
class StocktakingDeficitCreateView(CreateView):
    model = StocktakingDeficit
    form_class = StocktakingDeficitForm
    template_name = 'inventory/stocktaking_deficit_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        return super().form_valid(form)
```

### در Templates
```html
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">ذخیره</button>
</form>
```

---

## نکات مهم

### 1. Quantity Calculations
- **Deficit**: `quantity_adjusted = quantity_expected - quantity_counted`
  - `quantity_counted` باید کمتر از `quantity_expected` باشد
- **Surplus**: `quantity_adjusted = quantity_counted - quantity_expected`
  - `quantity_counted` باید بیشتر از `quantity_expected` باشد

### 2. Cost Calculations
- `total_cost = quantity_adjusted * unit_cost`
- به صورت خودکار در `clean()` محاسبه می‌شود

### 3. Document Code Generation
- **Deficit**: `STD-{YYYYMM}-{SEQUENCE}`
- **Surplus**: `STS-{YYYYMM}-{SEQUENCE}`
- **Record**: `STR-{YYYYMM}-{SEQUENCE}`

### 4. Approval Workflow
- فقط approver انتخاب شده می‌تواند `approval_status` را تغییر دهد
- `approved_at` به صورت خودکار تنظیم می‌شود
- Server-side و client-side validation برای permission checking

### 5. Company Filtering
- تمام forms از `StocktakingBaseForm` استفاده می‌کنند که company filtering دارد
- `item` و `warehouse` queryset ها بر اساس `company_id` فیلتر می‌شوند

### 6. Unit Validation
- `unit` باید در لیست واحدهای مجاز کالا باشد
- از `StocktakingBaseForm._validate_unit()` استفاده می‌شود

### 7. Warehouse Validation
- `warehouse` باید در لیست انبارهای مجاز کالا باشد
- از `StocktakingBaseForm._validate_warehouse()` استفاده می‌شود

### 8. Cached Fields
- `item_code` از `item.item_code` cache می‌شود
- `warehouse_code` از `warehouse.public_code` cache می‌شود
- `confirmed_by_code` از `confirmed_by.username` cache می‌شود

---

## الگوهای مشترک

1. **Auto-generated Fields**: تمام forms کد سند و تاریخ را به صورت خودکار تولید می‌کنند
2. **Company Filtering**: تمام forms از `StocktakingBaseForm` استفاده می‌کنند که company filtering دارد
3. **Unit Validation**: تمام forms unit را validate می‌کنند
4. **Warehouse Validation**: تمام forms warehouse را validate می‌کنند
5. **Cost Calculation**: Deficit و Surplus forms هزینه کل را به صورت خودکار محاسبه می‌کنند
6. **Cached Fields**: تمام forms فیلدهای cache شده را تنظیم می‌کنند

