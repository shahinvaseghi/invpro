# Inventory Forms Documentation

## Overview
This document describes the forms used in the inventory module for creating and editing master data entities.

## Form Classes

### 1. ItemTypeForm
**Purpose:** Create and edit item types (categories at the highest level)

**Model:** `ItemType`

**Fields:**
- `public_code` (3 digits) - Unique code for the item type
- `name` - Persian name
- `name_en` - English name
- `description` - Brief description
- `notes` - Detailed notes
- `sort_order` - Display order
- `is_enabled` - Active/Inactive status

**Validation:**
- Code must be unique per company
- Names (FA and EN) must be unique per company

**Example:**
```python
form = ItemTypeForm(data={
    'public_code': '001',
    'name': 'مواد اولیه',
    'name_en': 'Raw Materials',
    'sort_order': 10,
    'is_enabled': 1
})
```

---

### 2. ItemCategoryForm
**Purpose:** Create and edit item categories

**Model:** `ItemCategory`

**Fields:**
- `public_code` (3 digits) - Unique code within company
- `name` - Persian name
- `name_en` - English name
- `description` - Brief description
- `notes` - Detailed notes
- `sort_order` - Display order
- `is_enabled` - Active/Inactive status

**Note:** ItemCategory is independent and does NOT have a foreign key to ItemType in the current schema.

---

### 3. ItemSubcategoryForm
**Purpose:** Create and edit item subcategories (catalog level)

**Model:** `ItemSubcategory`

**Fields:**
- `category` - Foreign key to ItemCategory
- `public_code` (3 digits) - Unique code within category
- `name` - Persian name
- `name_en` - English name
- `description` - Brief description
- `notes` - Detailed notes
- `sort_order` - Display order
- `is_enabled` - Active/Inactive status

**Validation:**
- Code must be unique per company and category
- Category dropdown is filtered by active company

**Dynamic Field Filtering:**
The form automatically filters available categories based on the user's active company in the `get_form()` method of the view.

---

### 4. WarehouseForm
**Purpose:** Create and edit warehouse locations

**Model:** `Warehouse`

**Fields:**
- `public_code` (5 digits) - Unique warehouse code
- `name` - Persian name
- `name_en` - English name
- `description` - Brief description
- `notes` - Detailed notes
- `sort_order` - Display order
- `is_enabled` - Active/Inactive status

**Validation:**
- Code must be unique per company
- Names must be unique per company

---

### 5. ItemForm
**Purpose:** ایجاد و ویرایش کالاها از طریق رابط اختصاصی (بدون مراجعه به Django Admin)

**Model:** `Item`

**Fields (نمایان شده):**
- `type`, `category`, `subcategory` (لیست‌های فیلتر شده بر اساس شرکت فعال)
- `user_segment` (دقیقاً دو رقم عددی)
- `name`, `name_en`
- سه فلگ `is_sellable`, `has_lot_tracking`, `requires_temporary_receipt`
- `tax_id`, `tax_title`, `min_stock`
- `default_unit`, `primary_unit` (از `UNIT_CHOICES` انتخاب می‌شوند، آماده برای متر/کیلو/عدد/بسته و …)
- `allowed_warehouses` (چندانتخابی): انبارهایی که کالا مجاز است در آن‌ها دریافت/نگهداری شود؛ نخستین انتخاب به عنوان انبار اصلی ثبت می‌شود.
- `description`, `notes`
- `sort_order`, `is_enabled`

**Validation:**
- نوع، دسته و زیردسته باید متعلق به شرکت یکسان باشند و `subcategory` با `category` همخوانی داشته باشد.
- `user_segment` باید فقط عدد و دقیقاً دو رقم باشد.
- حداقل یک انبار باید انتخاب شود و همه‌ی انبارها باید برای همان شرکت فعال باشند.

**ویژگی‌ها:**
- فرم، فرم‌ست واحدهای ثانویه را نیز مدیریت می‌کند تا تبدیل واحد تعریف شود (مثال: ۲ متر = ۲۰ کیلوگرم).
- لیست واحدهای قابل انتخاب در ثابت `UNIT_CHOICES` نگه‌داری می‌شود.

---

### 6. ItemUnitForm و ItemUnitFormSet
**Purpose:** تعریف تبدیل واحد برای هر کالا (اختیاری)

**Model:** `ItemUnit`

**Fields:** `from_unit`, `from_quantity`, `to_unit`, `to_quantity`, `description`, `notes`

**ویژگی‌ها:**
- فیلدهای واحد از `UNIT_CHOICES` رندر می‌شوند (نیازی به تایپ دستی نیست).
- کد عمومی (`public_code`) به صورت خودکار تولید می‌شود؛ کاربر می‌تواند تبدیل‌ها را حذف/افزود کند.
- فرم‌ست با پیشوند `units-` در `item_form.html` نمایش داده می‌شود و در هنگام ذخیره کالا، تبدیل‌ها نیز ذخیره یا حذف می‌شوند.

---

### 7. ReceiptTemporaryForm
**Purpose:** ایجاد/ویرایش رسیدهای موقت (ثبت ورود کالا پیش از تأیید QC)  
**Model:** `ReceiptTemporary`

- `document_code`, `document_date` و `status` در رابط کاربری نمایش داده نمی‌شوند؛ هنگام ایجاد رکورد جدید، کد با الگو `TMP-YYYYMM-XXXXXX`، تاریخ روز و وضعیت پیش‌فرض `Draft` به‌صورت خودکار تولید و ذخیره می‌شوند.
- فیلد `unit` تنها واحد اصلی کالا و تبدیل‌های تعریف‌شده در `ItemUnit` را نمایش می‌دهد. اگر کاربر واحد جایگزین را انتخاب کند مقدار (`quantity`) و واحد قبل از ذخیره به واحد اصلی تبدیل می‌شود.
- فیلدهایی مانند `item`, `warehouse`, `supplier` بر اساس شرکت فعال فیلتر می‌شوند.
- در حالت ویرایش، فرم اطلاعات سند (کد، تاریخ، وضعیت) را در بالای صفحه به صورت فقط خواندنی نشان می‌دهد.

---

### 8. ReceiptPermanentForm
**Purpose:** ثبت رسید دائمی و تبدیل موجودی موقت به قطعی  
**Model:** `ReceiptPermanent`

- کد سند با الگو `PRM-YYYYMM-XXXXXX` و تاریخ روز هنگام ایجاد به شکل خودکار تعیین می‌شود؛ وضعیت، فیلدهای قفل و ثبت حسابداری در بخش «Controls» فرم نمایش داده می‌شوند.
- `unit` فقط واحدهای مجاز را لیست می‌کند و مقدار و واحد نهایی همیشه با واحد اصلی کالا ذخیره می‌شود.
- فیلد `unit_price` می‌تواند بر اساس واحد جایگزین وارد شود؛ فرم در مرحله‌ی ذخیره آن را به قیمت هر واحد اصلی تبدیل می‌کند تا موجودی مالی با واحد پایه ثبت شود.
- ارتباط با رسید موقت (`temporary_receipt`) و درخواست خرید (`purchase_request`) به‌صورت خودکار فیلتر می‌شود.

---

### 9. ReceiptConsignmentForm
**Purpose:** مدیریت رسیدهای امانی و مالکیت کالاهای در اختیار تأمین‌کننده  
**Model:** `ReceiptConsignment`

- مشابه دریافت دائمی، کد سند با الگو `CON-YYYYMM-XXXXXX` و تاریخ روز به شکل خودکار تعیین می‌شود.
- `unit` و `quantity` به واحد اصلی کالا نگاشت می‌شوند و فیلد `unit_price_estimate` نیز در صورت استفاده از واحد جایگزین به قیمت بر مبنای واحد اصلی تبدیل و ذخیره می‌شود.
- امکان ثبت اطلاعات قرارداد امانی، سررسید بازگشت، و ارتباط با رسید موقت/رسید تبدیل دائمی وجود دارد.

---

### 10. IssuePermanentForm
**Purpose:** ثبت و ویرایش حواله‌های دائم در رابط اختصاصی

**Model:** `IssuePermanent`

- فیلدهای اصلی: `item`, `warehouse`, `unit`, `quantity`
- مقصد: `destination_type/destination_id/destination_code` و همچنین فیلد انتخابی `department_unit` برای تعیین واحد سازمانی دریافت‌کننده
- بخش مالی شامل `unit_price`, `currency`, `tax_amount`, `discount_amount`, `total_amount` است؛ فیلد `currency` اکنون یک لیست انتخابی با گزینه‌های محدود (`IRT` = تومان، `IRR` = ریال، `USD` = دلار) است تا ورود مقادیر متفرقه جلوگیری شود.
- کد سند و تاریخ به صورت خودکار تولید می‌شود و فیلدها در فرم مخفی هستند.
- انتخاب واحد کالا مانند فرم‌های رسید محدود به واحدهای تعریف‌شده‌ی همان کالا است.

---

### 11. IssueConsumptionForm
**Purpose:** ثبت حواله‌های مصرف (مصرف داخلی/خط تولید)

**Model:** `IssueConsumption`

- علاوه بر فیلدهای پایه (کالا، انبار، واحد، مقدار)، می‌توان به صورت انتخابی واحد سازمانی (`department_unit`) و خط کاری (`work_line`) را مشخص کرد.
- فیلدهای مرجع شامل `reference_document_*` و `production_transfer_*` هستند.
- هزینه‌ی واحد و مجموع هزینه قابل ثبت است؛ سیستم کد سند و تاریخ را به صورت خودکار مقداردهی می‌کند و واحد کالا را با منطق تبدیل واحد نرمال می‌نماید.

---

### 12. IssueConsignmentForm
**Purpose:** مدیریت حواله‌های امانی که از موجودی امانی خارج می‌شوند

**Model:** `IssueConsignment`

- انتخاب کالا/انبار و مقدار مشابه سایر فرم‌ها انجام می‌شود.
- کاربر باید رسید امانی مبنا (`consignment_receipt`) را انتخاب کند؛ کد آن به صورت خودکار در مدل ذخیره می‌شود.
- می‌توان واحد سازمانی مقصد (`department_unit`) و اطلاعات مقصد (`destination_type`, `destination_id`, `destination_code`) را وارد کرد.
- کد سند و تاریخ به شکل خودکار ساخته می‌شود و واحد کالا محدود به واحدهای تعریف‌شده است.

---

### 13. SupplierForm
**Purpose:** تعریف و ویرایش اطلاعات تأمین‌کننده در رابط اختصاصی

**Model:** `Supplier`

**Fields:** `public_code`, `name`, `name_en`, اطلاعات تماس (تلفن/موبایل/ایمیل), آدرس کامل, `tax_id`, `description`, `sort_order`, `is_enabled`

**ویژگی‌ها:**
- تمام فیلدها براساس شرکت فعال فیلتر می‌شوند و ثبت همزمان `company_id` و `created_by` در ویو انجام می‌شود.
- فرم به صورت symlink به `generic_form.html` رندر می‌شود.

### 14. SupplierCategoryForm
**Purpose:** اتصال یک تأمین‌کننده به دسته‌بندی کالا با قابلیت تعریف «دستهٔ اصلی»

**Model:** `SupplierCategory`

**Fields:** `supplier`, `category`, `is_primary`, `notes`

**Validation:**
- تأمین‌کننده و دسته‌بندی باید متعلق به همان شرکت فعال باشند.
- ترکیب تأمین‌کننده/دسته‌ی تکراری کنترل می‌شود و پیام خطا قبل از رسیدن به پایگاه داده نمایش داده می‌شود.

**ویژگی‌ها:**
- انتخاب‌های `supplier` و `category` براساس شرکت فعال فیلتر می‌شوند.
- فیلد `is_primary` به صورت `BooleanField` نمایش داده می‌شود و مقدار صحیح/غلط را مستقیماً ذخیره می‌کند.

---

## Form Features

### Auto-populated Fields
The following fields are automatically set by views and should NOT be included in forms:
- `company_id` - Set from active session company
- `created_by` - Set from request.user on creation
- `edited_by` - Set from request.user on update
- `created_at` - Auto timestamp on creation
- `updated_at` - Auto timestamp on update

### CSS Classes
All form fields use Bootstrap-compatible CSS classes:
- `form-control` - For inputs, selects, textareas
- Error messages use `error` class
- Help text uses `form-text` class

### Widget Configuration
```python
widgets = {
    'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
    'name': forms.TextInput(attrs={'class': 'form-control'}),
    'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    'sort_order': forms.NumberInput(attrs={'class': 'form-control'}),
    'is_enabled': forms.Select(attrs={'class': 'form-control'}),
}
```

---

## Usage in Views

### Create View Example
```python
class ItemTypeCreateView(InventoryBaseView, CreateView):
    model = models.ItemType
    form_class = forms.ItemTypeForm
    template_name = 'inventory/itemtype_form.html'
    success_url = reverse_lazy('inventory:item_types')
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Item Type created successfully.'))
        return super().form_valid(form)
```

### Update View Example
```python
class ItemTypeUpdateView(InventoryBaseView, UpdateView):
    model = models.ItemType
    form_class = forms.ItemTypeForm
    template_name = 'inventory/itemtype_form.html'
    success_url = reverse_lazy('inventory:item_types')
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Item Type updated successfully.'))
        return super().form_valid(form)
```

---

## Templates

### Generic Form Template
All forms use the generic template: `templates/inventory/generic_form.html`

Symlinks are created for specific forms:
- `itemtype_form.html` → `generic_form.html`
- `itemcategory_form.html` → `generic_form.html`
- `itemsubcategory_form.html` → `generic_form.html`
- `warehouse_form.html` → `generic_form.html`
- `item_form.html` فرم سفارشی کالا است که علاوه بر فیلدهای اصلی، فرم‌ست واحدهای ثانویه را نیز نمایش می‌دهد.
- `item_confirm_delete.html`, `supplier_form.html`, `suppliercategory_form.html` و سایر فرم‌های CRUD جدید به قالب جنریک متصل شده‌اند.

This approach ensures consistency and reduces code duplication.

---

## Internationalization

All form labels and help text are wrapped with `gettext_lazy()` for translation support:

```python
labels = {
    'public_code': _('Code'),
    'name': _('Name (Persian)'),
    'name_en': _('Name (English)'),
}
```

---

## Error Handling

Forms display validation errors inline:
- Required field errors
- Unique constraint violations
- Format validation errors

All error messages are translated to Persian when `LANGUAGE_CODE='fa'`.

---

## Future Enhancements

1. Add AJAX-based category filtering for subcategories
2. Implement bulk import from Excel
3. Add image upload for item types
4. Implement form wizards for complex multi-step data entry

