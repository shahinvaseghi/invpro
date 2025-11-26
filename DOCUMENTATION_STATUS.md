# وضعیت مستندسازی پروژه (Documentation Status)

## ⚠️ تذکر بسیار مهم

**از این به بعد، هر فایل جدیدی که در برنامه ساخته می‌شود، باید یک فایل README.md کامل داشته باشد که شامل موارد زیر باشد:**

1. **هدف فایل**: توضیح کلی از اینکه فایل چه کاری انجام می‌دهد
2. **تمام کلاس‌ها**: لیست تمام کلاس‌های موجود در فایل
3. **تمام متدها**: برای هر کلاس، تمام متدها با جزئیات کامل:
   - نام متد
   - پارامترهای ورودی (با نوع و توضیح)
   - مقدار بازگشتی (با نوع و توضیح)
   - منطق و نحوه کارکرد
4. **تمام فیلدها**: برای forms، تمام فیلدها با:
   - نوع فیلد
   - widget
   - label
   - help_text (در صورت وجود)
   - validation rules
5. **وابستگی‌ها**: تمام import ها و وابستگی‌های فایل
6. **استفاده در پروژه**: نحوه استفاده از فایل در پروژه
7. **نکات مهم**: نکات و الگوهای خاص

**این مستندسازی باید به صورت کامل و جامع باشد و هیچ جزئیاتی از قلم نیفتد.**

---

## خلاصه کارهای انجام شده

در این پروژه، یک سیستم مستندسازی کامل برای تمام فایل‌های مهم برنامه ایجاد شده است. هر فایل README شامل:

- توضیح کامل هدف فایل
- لیست تمام کلاس‌ها و توابع
- جزئیات کامل هر متد (پارامترها، return values، منطق)
- جزئیات کامل هر فیلد (برای forms)
- وابستگی‌ها و نحوه استفاده
- نکات مهم و الگوهای خاص

---

## فایل‌های مستندسازی شده (کامل)

### Views

#### ✅ `inventory/views/master_data.py`
- **فایل README**: `inventory/views/README_MASTER_DATA.md`
- **وضعیت**: ✅ کامل
- **توضیحات**: 
  - تمام 27 کلاس view مستندسازی شده
  - تمام متدها با پارامترها و return values
  - تمام context variables
  - تمام URL patterns
  - منطق کامل هر متد

**کلاس‌های مستندسازی شده**:
- `ItemTypeListView`, `ItemTypeCreateView`, `ItemTypeUpdateView`, `ItemTypeDeleteView`
- `ItemCategoryListView`, `ItemCategoryCreateView`, `ItemCategoryUpdateView`, `ItemCategoryDeleteView`
- `ItemSubcategoryListView`, `ItemSubcategoryCreateView`, `ItemSubcategoryUpdateView`, `ItemSubcategoryDeleteView`
- `ItemListView`, `ItemSerialListView`, `ItemCreateView`, `ItemUpdateView`, `ItemDeleteView`
- `WarehouseListView`, `WarehouseCreateView`, `WarehouseUpdateView`, `WarehouseDeleteView`
- `SupplierCategoryListView`, `SupplierCategoryCreateView`, `SupplierCategoryUpdateView`, `SupplierCategoryDeleteView`
- `SupplierListView`, `SupplierCreateView`, `SupplierUpdateView`, `SupplierDeleteView`

---

### Forms

#### ✅ `inventory/forms/master_data.py`
- **فایل README**: `inventory/forms/README_MASTER_DATA.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام helper classes مستندسازی شده (`IntegerCheckboxField`, `IntegerCheckboxInput`)
  - تمام form classes با جزئیات کامل
  - تمام فیلدها با نوع، widget، label
  - تمام متدها (`__init__`, `clean`, etc.)
  - FormSet factory documentation

**کلاس‌های مستندسازی شده**:
- `IntegerCheckboxField` (تمام متدها)
- `IntegerCheckboxInput` (تمام متدها)
- `ItemTypeForm`
- `ItemCategoryForm`
- `ItemSubcategoryForm`
- `WarehouseForm`
- `SupplierForm`
- `SupplierCategoryForm` (با تمام متدهای پیچیده)
- `ItemForm` (با تمام فیلدها و validation)
- `ItemUnitForm`
- `ItemUnitFormSet`

#### ✅ `inventory/forms/receipt.py`
- **فایل README**: `inventory/forms/README_RECEIPT.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام header forms مستندسازی شده (`ReceiptTemporaryForm`, `ReceiptPermanentForm`, `ReceiptConsignmentForm`)
  - تمام line forms با جزئیات کامل (`ReceiptLineBaseForm`, `ReceiptPermanentLineForm`, `ReceiptConsignmentLineForm`, `ReceiptTemporaryLineForm`)
  - تمام متدها با پارامترها و return values
  - تمام فیلدها با نوع، widget، label
  - Formsets documentation
  - Unit conversion logic
  - Price normalization logic
  - Item filtering and search support

**کلاس‌های مستندسازی شده**:
- `ReceiptTemporaryForm` (تمام متدها)
- `ReceiptPermanentForm` (تمام متدها)
- `ReceiptConsignmentForm` (تمام متدها)
- `ReceiptLineBaseForm` (تمام helper methods)
- `ReceiptPermanentLineForm`
- `ReceiptConsignmentLineForm`
- `ReceiptTemporaryLineForm`
- `ReceiptPermanentLineFormSet`
- `ReceiptConsignmentLineFormSet`
- `ReceiptTemporaryLineFormSet`

#### ✅ `inventory/forms/issue.py`
- **فایل README**: `inventory/forms/README_ISSUE.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام header forms مستندسازی شده (`IssuePermanentForm`, `IssueConsumptionForm`, `IssueConsignmentForm`)
  - تمام line forms با جزئیات کامل (`IssueLineBaseForm`, `IssuePermanentLineForm`, `IssueConsumptionLineForm`, `IssueConsignmentLineForm`)
  - Serial assignment form (`IssueLineSerialAssignmentForm`)
  - تمام متدها با پارامترها و return values
  - Inventory balance validation
  - Destination handling logic
  - Production module integration
  - Item filtering and search support

**کلاس‌های مستندسازی شده**:
- `IssuePermanentForm` (تمام متدها)
- `IssueConsumptionForm` (تمام متدها)
- `IssueConsignmentForm` (تمام متدها)
- `IssueLineSerialAssignmentForm` (تمام متدها)
- `IssueLineBaseForm` (تمام helper methods)
- `IssuePermanentLineForm` (با destination handling)
- `IssueConsumptionLineForm` (با destination type choice)
- `IssueConsignmentLineForm` (با consignment receipt)
- `IssuePermanentLineFormSet`
- `IssueConsumptionLineFormSet`
- `IssueConsignmentLineFormSet`

#### ✅ `inventory/forms/request.py`
- **فایل README**: `inventory/forms/README_REQUEST.md`
- **وضعیت**: ✅ کامل
- **توضیحات**:
  - تمام forms مستندسازی شده (`PurchaseRequestForm`, `PurchaseRequestLineForm`, `WarehouseRequestForm`)
  - تمام متدها با پارامترها و return values
  - تمام فیلدها با نوع، widget، label
  - Item filtering and search support (بر اساس `request.GET`)
  - Approver validation
  - Unit conversion logic

**کلاس‌های مستندسازی شده**:
- `PurchaseRequestForm` (تمام متدها)
- `PurchaseRequestLineForm` (با item filtering)
- `PurchaseRequestLineFormSet`
- `WarehouseRequestForm` (تمام متدها با item filtering)

---

## فایل‌های مستندسازی شده (ناقص - نیاز به تکمیل)

### Views

#### ⚠️ `inventory/views/receipts.py`
- **فایل README**: `inventory/views/README_RECEIPTS.md`
- **وضعیت**: ⚠️ ناقص (خلاصه با به‌روزرسانی‌های اخیر)
- **توضیحات**: 
  - فایل README موجود است و شامل خلاصه تمام کلاس‌ها است
  - به‌روزرسانی شده با تغییرات اخیر (Item Filtering and Search)
  - نیاز به تکمیل کامل با تمام متدها و جزئیات (پارامترها، return values، منطق کامل)
  - 27 کلاس view در این فایل وجود دارد که نیاز به مستندسازی کامل دارند

**کلاس‌های موجود (نیاز به مستندسازی کامل)**:
- Base Classes:
  - `DocumentDeleteViewBase` (نیاز به تکمیل)
  - `ReceiptFormMixin` (نیاز به تکمیل)
- Temporary Receipt Views:
  - `ReceiptTemporaryListView`
  - `ReceiptTemporaryCreateView`
  - `ReceiptTemporaryUpdateView`
  - `ReceiptTemporaryDeleteView`
  - `ReceiptTemporaryLockView`
  - `ReceiptTemporarySendToQCView`
  - `ReceiptTemporaryCreateFromPurchaseRequestView`
- Permanent Receipt Views:
  - `ReceiptPermanentListView`
  - `ReceiptPermanentCreateView`
  - `ReceiptPermanentUpdateView`
  - `ReceiptPermanentDeleteView`
  - `ReceiptPermanentLockView`
  - `ReceiptPermanentCreateFromPurchaseRequestView`
- Consignment Receipt Views:
  - `ReceiptConsignmentListView`
  - `ReceiptConsignmentCreateView`
  - `ReceiptConsignmentUpdateView`
  - `ReceiptConsignmentDeleteView`
  - `ReceiptConsignmentLockView`
  - `ReceiptConsignmentCreateFromPurchaseRequestView`
- Serial Assignment Views:
  - `ReceiptSerialAssignmentBaseView`
  - `ReceiptPermanentSerialAssignmentView`
  - `ReceiptConsignmentSerialAssignmentView`
  - `ReceiptLineSerialAssignmentBaseView`
  - `ReceiptPermanentLineSerialAssignmentView`
  - `ReceiptConsignmentLineSerialAssignmentView`

---

## فایل‌های نیازمند مستندسازی (باقی‌مانده)

### Views

#### ❌ `inventory/views/issues.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `inventory/views/README_ISSUES.md` (نیاز به بررسی و تکمیل)

#### ⚠️ `inventory/views/requests.py`
- **وضعیت**: ⚠️ ناقص (خلاصه با به‌روزرسانی‌های اخیر)
- **فایل README موجود**: `inventory/views/README_REQUESTS.md`
- **توضیحات**:
  - فایل README موجود است و شامل خلاصه تمام کلاس‌ها است
  - به‌روزرسانی شده با تغییرات اخیر (Item Filtering and Search)
  - شامل توضیحات Base Mixins (`PurchaseRequestFormMixin`, `WarehouseRequestFormMixin`)
  - نیاز به تکمیل کامل با تمام متدها و جزئیات (پارامترها، return values، منطق کامل)

#### ❌ `inventory/views/stocktaking.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `inventory/views/README_STOCKTAKING.md` (نیاز به بررسی و تکمیل)

#### ❌ `inventory/views/balance.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `inventory/views/README_BALANCE.md` (نیاز به بررسی و تکمیل)

#### ❌ `inventory/views/api.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `inventory/views/README_API.md` (نیاز به بررسی و تکمیل)

#### ❌ `inventory/views/base.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `inventory/views/README_BASE.md` (نیاز به بررسی و تکمیل)

#### ❌ سایر view files
- `inventory/views/item_import.py` → `README_ITEM_IMPORT.md`
- `inventory/views/create_issue_from_warehouse_request.py` → `README_CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.md`
- `inventory/views/issues_from_warehouse_request.py` → `README_ISSUES_FROM_WAREHOUSE_REQUEST.md`

---

### Forms

#### ✅ `inventory/forms/receipt.py`
- **وضعیت**: ✅ کامل (به بخش بالا مراجعه کنید)

#### ✅ `inventory/forms/issue.py`
- **وضعیت**: ✅ کامل (به بخش بالا مراجعه کنید)

#### ✅ `inventory/forms/request.py`
- **وضعیت**: ✅ کامل (به بخش بالا مراجعه کنید)

#### ❌ `inventory/forms/stocktaking.py`
- **وضعیت**: ❌ نیاز به مستندسازی

#### ❌ `inventory/forms/base.py`
- **وضعیت**: ❌ نیاز به مستندسازی

---

### Other Modules

#### ❌ `production/views/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `production/views/README.md` (نیاز به بررسی و تکمیل)

#### ❌ `production/forms/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `production/forms/README.md` (نیاز به بررسی و تکمیل)

#### ❌ `qc/views/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `qc/views/README.md`, `qc/views/README_BASE.md` (نیاز به بررسی و تکمیل)

#### ❌ `ticketing/views/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی

#### ❌ `ticketing/forms/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی

#### ❌ `shared/views/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `shared/views/README.md` (نیاز به بررسی و تکمیل)

#### ❌ `shared/forms/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `shared/forms/README.md` (نیاز به بررسی و تکمیل)

---

### Utilities

#### ❌ `inventory/utils/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل‌های موجود**:
  - `codes.py` (نیاز به README)
  - `jalali.py` (نیاز به README)
  - `serials.py` (نیاز به README)

#### ❌ `shared/utils/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل‌های موجود**:
  - `modules.py` (نیاز به README)
  - `permissions.py` (نیاز به README)
  - `email.py` (نیاز به README)

#### ❌ `ticketing/utils/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل‌های موجود**:
  - `codes.py` (نیاز به README)

---

### Services

#### ❌ `inventory/services/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل‌های موجود**:
  - `serials.py` (نیاز به README)

---

### Template Tags

#### ❌ `inventory/templatetags/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل‌های موجود**:
  - `jalali_tags.py` (نیاز به README)

#### ❌ `shared/templatetags/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل‌های موجود**:
  - `access_tags.py` (نیاز به README)
  - `json_filters.py` (نیاز به README)

---

### Context Processors

#### ❌ `shared/context_processors.py`
- **وضعیت**: ❌ نیاز به مستندسازی

#### ❌ `ui/context_processors.py`
- **وضعیت**: ❌ نیاز به مستندسازی

---

### Management Commands

#### ❌ `inventory/management/commands/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل‌های موجود**:
  - `cleanup_test_receipts.py` (نیاز به README)

---

### Migrations

#### ❌ `*/migrations/*.py`
- **وضعیت**: ❌ نیاز به مستندسازی
- **فایل README موجود**: `production/migrations/README.md` (نیاز به بررسی و تکمیل)
- **توضیحات**: تمام migration files نیاز به README دارند

---

## آمار کلی

### ✅ کامل شده
- **Views**: 1 فایل (`master_data.py`)
- **Forms**: 4 فایل (`master_data.py`, `receipt.py`, `issue.py`, `request.py`)
- **جمع**: 5 فایل کامل

### ⚠️ ناقص (نیاز به تکمیل)
- **Views**: 2 فایل (`receipts.py`, `requests.py`)

### ❌ نیازمند مستندسازی
- **Views**: ~15+ فایل
- **Forms**: ~10+ فایل
- **Utils**: ~10+ فایل
- **Services**: ~5+ فایل
- **Template Tags**: ~5+ فایل
- **Context Processors**: ~2 فایل
- **Management Commands**: ~5+ فایل
- **Migrations**: ~50+ فایل

**جمع کل**: ~100+ فایل نیازمند مستندسازی

---

## استاندارد مستندسازی

هر فایل README باید شامل موارد زیر باشد:

### 1. Header
```markdown
# [module]/[type]/[filename].py - [Description]

**هدف**: [توضیح کلی]

این فایل شامل [توضیح محتوا]:
- [Item 1]
- [Item 2]
```

### 2. برای هر کلاس/تابع
```markdown
### `ClassName`

**توضیح**: [توضیح کامل]

**Type**: `[Base Classes]`

**Attributes**:
- `attr1`: [توضیح]

**متدها**:

#### `method_name(self, param1: Type) -> ReturnType`

**توضیح**: [توضیح کامل]

**پارامترهای ورودی**:
- `param1` (Type): [توضیح]

**مقدار بازگشتی**:
- `ReturnType`: [توضیح]

**منطق**:
1. [Step 1]
2. [Step 2]
```

### 3. برای Forms
```markdown
### `FormName(forms.ModelForm)`

**توضیح**: [توضیح]

**Model**: `ModelName`

**Fields**:
- `field_name` (FieldType): [توضیح]
  - Widget: `WidgetType`
  - Label: `'Label'`
  - Required: `True/False`

**متدها**:
[مشابه بالا]
```

### 4. وابستگی‌ها
```markdown
## وابستگی‌ها

- `module.class`: `ClassName`
- `django.module`: `Item`
```

### 5. استفاده در پروژه
```markdown
## استفاده در پروژه

[توضیح نحوه استفاده]
```

### 6. نکات مهم
```markdown
## نکات مهم

1. **نکته 1**: [توضیح]
2. **نکته 2**: [توضیح]
```

---

## اولویت‌بندی

### اولویت بالا (باید زودتر انجام شود)
1. ✅ `inventory/views/master_data.py` - **کامل شده**
2. ✅ `inventory/forms/master_data.py` - **کامل شده**
3. ✅ `inventory/forms/receipt.py` - **کامل شده**
4. ✅ `inventory/forms/issue.py` - **کامل شده**
5. ✅ `inventory/forms/request.py` - **کامل شده**
6. ⚠️ `inventory/views/receipts.py` - **ناقص (نیاز به تکمیل کامل)**
7. ⚠️ `inventory/views/requests.py` - **ناقص (نیاز به تکمیل کامل)**
8. ❌ `inventory/views/issues.py` - **بعدی**

### اولویت متوسط
9. ❌ `inventory/views/stocktaking.py`
10. ❌ `inventory/forms/stocktaking.py`
11. ❌ `inventory/forms/base.py`

### اولویت پایین
12. ❌ Utility files
13. ❌ Service files
14. ❌ Template tags
15. ❌ Context processors
16. ❌ Management commands
17. ❌ Migrations

---

## نحوه کار

برای تکمیل مستندسازی:

1. **خواندن فایل**: ابتدا فایل را به صورت کامل می‌خوانیم
2. **تحلیل ساختار**: کلاس‌ها، متدها، و توابع را شناسایی می‌کنیم
3. **مستندسازی**: برای هر بخش README کامل می‌نویسیم
4. **بررسی**: مطمئن می‌شویم که هیچ جزئیاتی از قلم نیفتاده

---

## آخرین به‌روزرسانی

**تاریخ**: 26 نوامبر 2024
**وضعیت**: در حال پیشرفت
**پیشرفت**: 5 فایل کامل (Views: 1, Forms: 4)، 2 فایل ناقص (Views: 2)، ~95+ فایل باقی‌مانده

**تغییرات اخیر**:
- ✅ تکمیل `inventory/forms/receipt.py` - README کامل با تمام کلاس‌ها و متدها
- ✅ تکمیل `inventory/forms/issue.py` - README کامل با تمام کلاس‌ها و متدها
- ✅ تکمیل `inventory/forms/request.py` - README کامل با تمام کلاس‌ها و متدها
- ⚠️ به‌روزرسانی `inventory/views/receipts.py` - اضافه شدن توضیحات Item Filtering and Search
- ⚠️ به‌روزرسانی `inventory/views/requests.py` - اضافه شدن توضیحات Base Mixins و Item Filtering and Search

---

## یادداشت‌ها

- تمام مستندسازی‌ها به زبان فارسی نوشته می‌شوند (به جز کد و نام کلاس‌ها)
- کدها و نام کلاس‌ها به زبان انگلیسی باقی می‌مانند
- مستندسازی باید کامل و جامع باشد
- هیچ جزئیاتی نباید از قلم بیفتد

