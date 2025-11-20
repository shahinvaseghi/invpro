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
- `secondary_batch_number` (اختیاری): بچ نامبر ثانویه که کاربر می‌تواند به صورت دستی وارد کند (علاوه بر بچ نامبر خودکار تولید شده توسط سیستم)
- `allowed_warehouses` (چندانتخابی): انبارهایی که کالا مجاز است در آن‌ها دریافت/نگهداری شود؛ نخستین انتخاب به عنوان انبار اصلی ثبت می‌شود. **مهم**: اگر کالا هیچ انبار مجازی نداشته باشد، نمی‌تواند در هیچ انباری رسید یا حواله شود (validation سخت).
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

- `document_code`, `document_date` و `status` در رابط کاربری نمایش داده نمی‌شوند؛ هنگام ایجاد رکورد جدید، کد با الگو `TMP-YYYYMM-XXXXXX`، تاریخ روز (با `JalaliDateField`) و وضعیت پیش‌فرض `Draft` به‌صورت خودکار تولید و ذخیره می‌شوند.
- فیلد `unit` تنها واحد اصلی کالا و تبدیل‌های تعریف‌شده در `ItemUnit` را نمایش می‌دهد. اگر کاربر واحد جایگزین را انتخاب کند مقدار (`quantity`) و واحد قبل از ذخیره به واحد اصلی تبدیل می‌شود.
- فیلد `warehouse` **فقط انبارهای مجاز** کالای انتخاب شده را نمایش می‌دهد (filtered by `ItemWarehouse`). اگر کالا انبار مجاز نداشته باشد، خطا داده می‌شود.
- برای کالاهایی که `has_lot_tracking=1` دارند، فرم بررسی می‌کند مقدار پس از تبدیل واحد دقیقاً عدد صحیح باشد؛ در صورت وارد کردن مقدار اعشاری پیام خطا نمایش داده می‌شود و ذخیره انجام نمی‌شود.
- فیلدهایی مانند `item`, `warehouse`, `supplier` بر اساس شرکت فعال فیلتر می‌شوند.
- در حالت ویرایش، فرم اطلاعات سند (کد، تاریخ، وضعیت) را در بالای صفحه به صورت فقط خواندنی نشان می‌دهد.

---

### 8. ReceiptPermanentForm
**Purpose:** ثبت رسید دائمی و تبدیل موجودی موقت به قطعی  
**Model:** `ReceiptPermanent` (header-only) + `ReceiptPermanentLine` (lines)

- کد سند با الگو `PRM-YYYYMM-XXXXXX` و تاریخ روز (با `JalaliDateField`) هنگام ایجاد به شکل خودکار تعیین می‌شود؛ وضعیت، فیلدهای قفل و ثبت حسابداری در بخش «Controls» فرم نمایش داده می‌شوند.
- **پشتیبانی چند ردیف**: از `ReceiptPermanentLineFormSet` استفاده می‌کند. حداقل 1 ردیف الزامی است. هر ردیف می‌تواند کالا، انبار، مقدار، واحد و قیمت جداگانه داشته باشد.
- در هر ردیف، `unit` فقط واحدهای مجاز کالای انتخاب شده را لیست می‌کند و مقدار و واحد نهایی همیشه با واحد اصلی کالا ذخیره می‌شود.
- در هر ردیف، `warehouse` **فقط انبارهای مجاز** کالای انتخاب شده را نمایش می‌دهد (filtered by `ItemWarehouse`). اگر کالا انبار مجاز نداشته باشد، خطا داده می‌شود.
- فیلد `unit_price` می‌تواند بر اساس واحد جایگزین (`entered_price_unit`) وارد شود؛ فرم در مرحله‌ی ذخیره آن را به قیمت هر واحد اصلی تبدیل می‌کند تا موجودی مالی با واحد پایه ثبت شود.
- اگر کالای انتخابی سریال‌دار باشد، مقدار باید عدد صحیح باشد (پس از تبدیل واحد). فرم خطای متنی برمی‌گرداند و از ذخیره جلوگیری می‌کند.
- ارتباط با رسید موقت (`temporary_receipt`) و درخواست خرید (`purchase_request`) به‌صورت خودکار فیلتر می‌شود.
- برای هر ردیف که کالای آن `has_lot_tracking=1` دارد، دکمه «Manage Serials» نمایش داده می‌شود.

---

### 9. ReceiptConsignmentForm
**Purpose:** مدیریت رسیدهای امانی و مالکیت کالاهای در اختیار تأمین‌کننده  
**Model:** `ReceiptConsignment`

- مشابه دریافت دائمی، کد سند با الگو `CON-YYYYMM-XXXXXX` و تاریخ روز به شکل خودکار تعیین می‌شود.
- `unit` و `quantity` به واحد اصلی کالا نگاشت می‌شوند و فیلد `unit_price_estimate` نیز در صورت استفاده از واحد جایگزین به قیمت بر مبنای واحد اصلی تبدیل و ذخیره می‌شود.
- امکان ثبت اطلاعات قرارداد امانی، سررسید بازگشت، و ارتباط با رسید موقت/رسید تبدیل دائمی وجود دارد.
- برای کالاهای سریال‌دار، مقدار فقط در صورت صحیح بودن (پس از تبدیل واحد) پذیرفته می‌شود.

---

### 10. IssuePermanentForm
**Purpose:** ثبت و ویرایش حواله‌های دائم در رابط اختصاصی

**Model:** `IssuePermanent` (header-only) + `IssuePermanentLine` (lines)

- **پشتیبانی چند ردیف**: از `IssuePermanentLineFormSet` استفاده می‌کند. حداقل 1 ردیف الزامی است. هر ردیف می‌تواند کالا، انبار، مقدار، واحد و مقصد جداگانه داشته باشد.
- در هر ردیف، فیلدهای اصلی: `item`, `warehouse`, `unit`, `quantity`
- در هر ردیف، مقصد: `destination_type` (اختیاری، `CompanyUnit`) و `destination_id`/`destination_code` برای تعیین واحد کاری مقصد. این فیلد از `WorkLine` به `CompanyUnit` تغییر یافته است.
- بخش مالی شامل `unit_price`, `currency`, `tax_amount`, `discount_amount`, `total_amount` است؛ فیلد `currency` اکنون یک لیست انتخابی با گزینه‌های محدود (`IRT` = تومان، `IRR` = ریال، `USD` = دلار) است تا ورود مقادیر متفرقه جلوگیری شود.
- کد سند و تاریخ (با `JalaliDateField`) به صورت خودکار تولید می‌شود و فیلدها در فرم مخفی هستند.
- در هر ردیف، انتخاب واحد کالا مانند فرم‌های رسید محدود به واحدهای تعریف‌شده‌ی همان کالا است.
- در هر ردیف، `warehouse` **فقط انبارهای مجاز** کالای انتخاب شده را نمایش می‌دهد (filtered by `ItemWarehouse`). اگر کالا انبار مجاز نداشته باشد، خطا داده می‌شود.
- اگر کالا سریال‌دار باشد، فرم علاوه بر الزام انتخاب تعداد سریال برابر با مقدار، بررسی می‌کند مقدار واردشده پس از تبدیل واحد عدد صحیح باشد.
- عملیات انتخاب سریال به جای همین فرم، از طریق دکمه «Assign Serials» برای هر ردیف انجام می‌شود؛ فرم همچنان داده‌های موجود را نمایش/ذخیره می‌کند ولی الزامی برای پر کردن فیلد در همین صفحه وجود ندارد.

---

### 11. IssueConsumptionForm
**Purpose:** ثبت حواله‌های مصرف (مصرف داخلی/خط تولید)

**Model:** `IssueConsumption` (header-only) + `IssueConsumptionLine` (lines)

- **پشتیبانی چند ردیف**: از `IssueConsumptionLineFormSet` استفاده می‌کند. حداقل 1 ردیف الزامی است.
- در هر ردیف، علاوه بر فیلدهای پایه (کالا، انبار، واحد، مقدار)، می‌توان مقصد را انتخاب کرد:
  - ابتدا `destination_type_choice` انتخاب می‌شود: "Company Unit" یا "Work Line"
  - سپس بر اساس انتخاب، `destination_company_unit` یا `destination_work_line` نمایش داده می‌شود
- در هر ردیف، `warehouse` **فقط انبارهای مجاز** کالای انتخاب شده را نمایش می‌دهد (filtered by `ItemWarehouse`). اگر کالا انبار مجاز نداشته باشد، خطا داده می‌شود.
- فیلدهای مرجع شامل `reference_document_*` و `production_transfer_*` هستند.
- هزینه‌ی واحد و مجموع هزینه قابل ثبت است؛ سیستم کد سند و تاریخ (با `JalaliDateField`) را به صورت خودکار مقداردهی می‌کند و واحد کالا را با منطق تبدیل واحد نرمال می‌نماید.
- مقدار حواله برای کالاهای سریال‌دار باید عدد صحیح باشد؛ فرم قبل از ذخیره این موضوع را بررسی می‌کند.
- انتخاب سریال‌ها از طریق صفحه‌ی اختصاصی «Assign Serials» برای هر ردیف انجام می‌شود.

---

### 12. IssueConsignmentForm
**Purpose:** مدیریت حواله‌های امانی که از موجودی امانی خارج می‌شوند

**Model:** `IssueConsignment` (header-only) + `IssueConsignmentLine` (lines)

- **پشتیبانی چند ردیف**: از `IssueConsignmentLineFormSet` استفاده می‌کند. حداقل 1 ردیف الزامی است.
- در هر ردیف، انتخاب کالا/انبار و مقدار مشابه سایر فرم‌ها انجام می‌شود.
- در هر ردیف، `warehouse` **فقط انبارهای مجاز** کالای انتخاب شده را نمایش می‌دهد (filtered by `ItemWarehouse`). اگر کالا انبار مجاز نداشته باشد، خطا داده می‌شود.
- کاربر باید رسید امانی مبنا (`consignment_receipt`) را انتخاب کند؛ کد آن به صورت خودکار در مدل ذخیره می‌شود.
- در هر ردیف، مقصد: `destination_type` (اختیاری، `CompanyUnit`) و `destination_id`/`destination_code` برای تعیین واحد کاری مقصد. این فیلد از `WorkLine` به `CompanyUnit` تغییر یافته است.
- کد سند و تاریخ (با `JalaliDateField`) به شکل خودکار ساخته می‌شود و واحد کالا محدود به واحدهای تعریف‌شده است.
- برای کالاهای دارای سریال، مقدار باید به صورت عدد صحیح ثبت شود و فرم در غیر این صورت خطا برمی‌گرداند.
- فیلد سریال در این فرم اختیاری است؛ مدیریت انتخاب/رزرو سریال از طریق دکمه‌ی «Assign Serials» برای هر ردیف انجام می‌شود.

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

**Fields:** `supplier`, `category`, `is_primary`, `subcategories`, `items`, `notes`

**Validation:**
- تأمین‌کننده و دسته‌بندی باید متعلق به همان شرکت فعال باشند.
- ترکیب تأمین‌کننده/دسته‌ی تکراری کنترل می‌شود و پیام خطا قبل از رسیدن به پایگاه داده نمایش داده می‌شود.

**ویژگی‌ها:**
- انتخاب‌های `supplier` و `category` براساس شرکت فعال فیلتر می‌شوند.
- فیلد `is_primary` به صورت `BooleanField` نمایش داده می‌شود و مقدار صحیح/غلط را مستقیماً ذخیره می‌کند.
- فیلدهای چندانتخابی `subcategories` و `items` امکان می‌دهند زیردسته‌ها و کالاهای قابل تأمین از همان دسته انتخاب شوند. انتخاب‌ها به همان شرکت فعال محدود شده‌اند و در زمان ذخیره، جداول `SupplierSubcategory` و `SupplierItem` به‌صورت خودکار همگام می‌شوند (حذف موارد برداشته‌شده و ایجاد موارد جدید).
- کدهای `public_code` برای انواع، دسته‌ها، زیردسته‌ها، انبارها و تأمین‌کنندگان در زمان ذخیره به‌صورت خودکار و متوالی تولید می‌شود؛ فرم‌های رابط کاربری دیگر نیاز به ورود دستی این کدها ندارند.

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

---

## Warehouse Restrictions (Allowed Warehouses)

All receipt and issue line forms enforce strict warehouse restrictions:

**Implementation**:
- Forms: `ReceiptLineBaseForm`, `IssueLineBaseForm` both implement:
  - `_get_item_allowed_warehouses()`: Returns only explicitly configured warehouses
  - `_set_warehouse_queryset()`: Filters warehouse dropdown dynamically
  - `clean_warehouse()`: Validates selected warehouse is in allowed list
  
**Validation Rules**:
- If item has no warehouses configured → Error: "این کالا هیچ انبار مجازی ندارد"
- If warehouse selected not in allowed list → Error: "انبار انتخاب شده برای این کالا مجاز نیست"
- No fallback to all warehouses (strict restriction)

**Client-Side (JavaScript)**:
- `updateWarehouseChoices()` function dynamically updates warehouse dropdown when item changes
- API endpoint: `/inventory/api/item-allowed-warehouses/?item_id=X`
- Applied to both single-line forms (`ReceiptTemporary`) and multi-line forms (all receipt/issue formsets)

**Example**:
- Item: "Monitor" - Allowed Warehouses: Only "003 - IT"
- User tries to receive in "002 - Facilities" → **Error**: Warehouse not allowed

---

## Date Handling (Jalali/Gregorian)

All document forms use `JalaliDateField` and `JalaliDateInput` widget:
- Dates displayed in Jalali (Persian) format in UI
- Dates stored in Gregorian format in database
- Automatic conversion on input/output
- Forms using Jalali dates:
  - `ReceiptPermanentForm`, `ReceiptConsignmentForm`
  - `IssuePermanentForm`, `IssueConsumptionForm`, `IssueConsignmentForm`
  - `PurchaseRequestForm`, `WarehouseRequestForm`

For details, see `inventory/fields.py`, `inventory/widgets.py`, and `inventory/templatetags/jalali_tags.py`.

