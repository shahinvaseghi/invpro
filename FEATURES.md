# Feature Documentation

This document provides a comprehensive overview of all implemented features in the invproj platform.

---

## 1. Multi-Company (Multi-Tenant) Support

### Overview
The platform supports multiple companies (tenants) with complete data isolation.

### Key Features
- **Session-Based Company Selection**: Active company stored in user session
- **Company Dropdown**: Header selector for switching between companies
- **Data Isolation**: All queries automatically filtered by company_id
- **Default Company**: Users can set a preferred default company
- **Access Control**: Users have explicit access to specific companies via `UserCompanyAccess`

### User Experience
1. User logs in
2. Default company auto-selected (or first accessible company)
3. User can switch companies via header dropdown
4. All data views automatically scope to active company
5. Forms auto-populate company_id from session

### Technical Implementation
```python
# Context processor provides active company
def active_company(request):
    active_company_id = request.session.get('active_company_id')
    if not active_company_id and request.user.default_company:
        active_company_id = request.user.default_company_id
        request.session['active_company_id'] = active_company_id
    
    return {
        'active_company': Company.objects.get(id=active_company_id),
        'user_companies': request.user accessible companies
    }

# Views auto-filter by company
class InventoryBaseView(LoginRequiredMixin):
    def get_queryset(self):
        company_id = self.request.session.get('active_company_id')
        return super().get_queryset().filter(company_id=company_id)
```

---

## 2. Internationalization (i18n)

### Supported Languages
- **Persian (Farsi)** - Primary language with full RTL support (default)
- **English** - Secondary language

### Features
- **Default Language**: Application opens in Persian by default (`LANGUAGE_CODE = 'fa'`)
- **Language Switcher**: Header dropdown for instant language switching
- **RTL/LTR Auto-Detection**: Layout automatically adjusts based on selected language
- **Font Optimization**: Vazir font for Persian, system fonts for English
- **Complete Translations**: All UI elements, messages, form labels, and error messages are fully translated to Persian
- **Translation Management**: Translation files in `locale/fa/LC_MESSAGES/django.po` with compiled `.mo` files
- **Form Labels**: All form fields have Persian/English labels
- **Error Messages**: Validation errors in user's language
- **UI Improvements**: 
  - Top menu buttons with flexible width (85-100px) and proper text wrapping for long labels
  - Enhanced dashboard design with modern, minimal styling and gradient backgrounds
  - Improved card layouts with hover animations and better spacing

## 2.1 Date Display (Jalali/Gregorian Conversion)

### Overview
The system displays dates in Jalali (Persian) format in the UI while storing them in Gregorian format in the database.

### Features
- **Storage**: All dates stored as Gregorian in database (`DateField`, `DateTimeField`)
- **Display**: Converted to Jalali format using template tags (`{{ date|jalali_date }}`)
- **Input**: Custom `JalaliDateInput` widget converts Jalali input to Gregorian before saving
- **Forms**: All document forms (`ReceiptPermanentForm`, `IssuePermanentForm`, etc.) use `JalaliDateField`
- **Benefits**: Users see familiar Jalali calendar, database maintains standard format, no dual date fields needed

### Technical Implementation
- Custom widget: `JalaliDateInput` (`inventory/widgets.py`)
- Custom field: `JalaliDateField` (`inventory/fields.py`)
- Template tags: `jalali_tags` (`inventory/templatetags/jalali_tags.py`)
- Utilities: `inventory/utils/jalali.py` for conversion functions

### Forms Using Jalali Dates
- Receipt forms: `ReceiptPermanentForm`, `ReceiptConsignmentForm`
- Issue forms: `IssuePermanentForm`, `IssueConsumptionForm`, `IssueConsignmentForm`
- Request forms: `PurchaseRequestForm`, `WarehouseRequestForm`

### Translation Coverage
- Navigation menus
- Page titles and headers
- Form labels and help text
- Button labels
- Status badges
- Empty states
- Success/error messages
- Breadcrumbs

### Technical Details
```bash
# Translation files
locale/fa/LC_MESSAGES/django.po  # Source translations
locale/fa/LC_MESSAGES/django.mo  # Compiled translations

# Compiling translations
python manage.py compilemessages -l fa

# Adding new translations
python manage.py makemessages -l fa
```

---

## 3. Inventory Master Data Management

### Item Types (انواع کالا)
**Purpose**: Highest-level categorization of items

**Features**:
- 3-digit unique code per company
- Persian and English names
- Description and notes fields
- Sort order for custom ordering
- Active/Inactive status
- Full CRUD operations with dedicated UI

**Code Pattern**: `001`, `002`, `003`, ...

**Use Cases**:
- Raw Materials (مواد اولیه)
- Finished Goods (محصولات نهایی)
- Semi-Finished (نیمه ساخته)
- Packaging (بسته‌بندی)

---

### Item Categories (دسته‌بندی کالا)
**Purpose**: Mid-level categorization

**Features**:
- 3-digit unique code per company
- Persian and English names
- Independent of Item Types (no foreign key)
- Description and notes
- Sort order
- Active/Inactive status
- Full CRUD operations

**Code Pattern**: `001`, `002`, `003`, ...

**Use Cases**:
- Metals (فلزات)
- Plastics (پلاستیک‌ها)
- Electronics (الکترونیک)
- Chemicals (مواد شیمیایی)

---

### Item Subcategories (زیردسته‌بندی/کاتالوگ)
**Purpose**: Detailed categorization under categories

**Features**:
- 3-digit unique code per category
- Foreign key to ItemCategory
- Persian and English names
- Description and notes
- Sort order
- Active/Inactive status
- Category dropdown filtered by company
- Full CRUD operations
- هر کالا هنگام ایجاد/ویرایش همراه با لیست «انبارهای مجاز» ذخیره می‌شود تا از ورود کالا به انبارهای ناخواسته جلوگیری گردد.
- **Strict Warehouse Restrictions**: Items can ONLY be received/issued in warehouses explicitly configured in `ItemWarehouse` relationship. If no warehouses configured, item cannot be received/issued anywhere (error shown). Validation enforced in both server-side (Python) and client-side (JavaScript). Warehouse dropdown dynamically updates when item is selected.

**Code Pattern**: `001`, `002`, `003`, ... (within each category)

**Use Cases**:
- Steel Types under Metals
- ABS, PVC under Plastics
- Resistors, Capacitors under Electronics

---

### Warehouses (انبار)
**Purpose**: Physical storage locations

**Features**:
- 5-digit unique code per company
- Persian and English names
- Optional location label
- Description and notes
- Sort order
- Active/Inactive status
- Full CRUD operations

**Code Pattern**: `00001`, `00002`, ...

**Use Cases**:
- Main Warehouse (انبار اصلی)
- Production Warehouse (انبار تولید)
- Finished Goods Warehouse (انبار محصول)
- Quarantine Warehouse (انبار قرنطینه)

---

## 4. Company Management

### Company Management
**Features**:
- 3-digit unique company code
- Legal name and display name (Persian/English)
- Registration number and tax ID
- Contact information (phone, email, website)
- Full address (address, city, state, country)
- Active/Inactive status
- **Auto-Access Creation**: Creator automatically gets ADMIN access

**CRUD Operations**:
- Create: Dedicated form with validation
- Read: Filtered list of accessible companies
- Update: Edit all company details
- Delete: With confirmation page

**Access Control**:
- Users see only companies they have access to
- Company creation auto-creates `UserCompanyAccess` record
- Access level determines permissions (ADMIN, USER, etc.)

---

### Personnel Management (Production Module)
**Location**: `/production/personnel/`

**Features**:
- Auto-generated 8-digit unique person code (not user-editable)
- Persian and English names
- National ID and personnel code
- **Smart Username**: Checkbox to auto-sync with personnel code
- Contact information (phone, mobile, email)
- Description and notes
- Active/Inactive status
- Company-scoped (users see only their company's personnel)
- عضویت در چند واحد سازمانی با انتخاب چندگانه و نمایش واحدها در لیست پرسنل

**Username Sync Feature**:
- ☑️ **Checked**: Username automatically matches personnel code
  - Username field becomes read-only
  - Changes to personnel code auto-update username
  - Reduces data entry errors
- ☐ **Unchecked**: User can enter custom username
  - Username field is editable
  - Allows non-standard usernames

**CRUD Operations**:
- Create: With company auto-assigned from session
- Read: Filtered list by active company
- Update: All personnel details
- Delete: With confirmation page
- تخصیص/حذف واحدهای سازمانی از طریق فرم و نمایش آنی در جدول فهرست

**Note**: Personnel management was moved from the Shared module to the Production module to better align with production workflows and resource management.

### Machine Management (Production Module)
**Location**: `/production/machines/`

**Features**:
- Auto-generated 10-digit machine code (not user-editable)
- Machine name (Persian/English)
- Machine type classification (CNC, lathe, milling, assembly, packaging, etc.)
- Work center assignment
- Manufacturer and model information
- Serial number tracking
- Purchase and installation dates
- Capacity specifications (JSON field for technical specs)
- Maintenance schedule and tracking
- Machine status (operational, maintenance, idle, broken, retired)
- Active/Inactive status
- Company-scoped (users see only their company's machines)

**CRUD Operations**:
- Create: Add new machines with specifications
- Read: Filtered list by active company and work center
- Update: Machine details, maintenance schedules, status
- Delete: With confirmation page

---

## 5. Form Features

### Common Features Across All Forms
1. **Auto-Population**:
   - `company_id` from active session
   - `created_by` from request.user
   - `edited_by` from request.user
   - Timestamps (created_at, updated_at)

2. **Validation**:
   - Required fields marked with `*`
   - Unique constraints enforced
   - Format validation (codes, emails, URLs)
   - Inline error messages

3. **User Experience**:
   - Consistent styling with Bootstrap-compatible classes
   - Help text for complex fields
   - Success/error messages
   - Breadcrumb navigation
   - Cancel button returns to list
   - Responsive layout

4. **Internationalization**:
   - All labels translated
   - All help text translated
   - All error messages translated
   - RTL support for Persian

---

## 6. List Views

### Common Features
- **Data Tables**: Clean, sortable tables
- **Action Columns**: Edit, Delete, and Lock buttons for each row
- **Delete Functionality**: 
  - Delete buttons conditionally displayed based on user permissions
  - `DELETE_OWN` permission allows users to delete their own documents
  - `DELETE_OTHER` permission allows users to delete documents created by other users
  - Superusers can delete any document without explicit permission
  - Locked documents cannot be deleted (protected by `DocumentLockProtectedMixin`)
  - Confirmation pages with document details before deletion
  - Available for all document types: Receipts (Temporary, Permanent, Consignment), Issues (Permanent, Consumption, Consignment), Stocktaking (Deficit, Surplus, Records)
- **Status Badges**: Color-coded Active/Inactive indicators
- **Pagination**: 50 items per page
- **Empty States**: User-friendly messages with create buttons
- **Create Button**: Prominent "+ Create X" button at top
- **Breadcrumbs**: Navigation path
- **Company Filtering**: Auto-filtered by active company
- **Document Sorting**: Issue and Stocktaking document lists (`IssueConsumptionListView`, `IssueConsignmentListView`, `IssuePermanentListView`, `StocktakingRecordListView`) are sorted by newest first (`ordering = ['-id']`)

### Available List Views
- Item Types
- Item Categories
- Item Subcategories
- Items
- Item Serials
- Warehouses
- Suppliers
- Supplier Categories
- Purchase Requests
- Receipts (Temporary, Permanent, Consignment)
- Issues (Permanent, Consumption, Consignment)
- Stocktaking (Deficit, Surplus, Records)
- Warehouse Requests
- Companies
- Personnel (Production Module)
- Machines (Production Module)

---

## 7. Multi-Line Document Support & Line-Based Serial Assignment

### Overview
The inventory system now supports **multi-line documents** for both receipts and issues, allowing users to add multiple items to a single document. Each line item can have its own item, quantity, warehouse, and pricing information. Additionally, **serial number assignment** is now managed at the line level, providing granular control over serial tracking for lot-controlled items.

### Key Features

#### Multi-Line Document Architecture
- **Header-Only Documents**: Issue and Receipt documents (`IssuePermanent`, `IssueConsumption`, `IssueConsignment`, `ReceiptPermanent`, `ReceiptConsignment`) now store only header-level information (document code, date, supplier, notes, etc.)
- **Line Item Models**: Each document type has corresponding line models:
  - `IssuePermanentLine`, `IssueConsumptionLine`, `IssueConsignmentLine` for issues
  - `ReceiptPermanentLine`, `ReceiptConsignmentLine` for receipts
- **Line Item Fields**: Each line contains:
  - Item reference and cached item code
  - Warehouse reference and cached warehouse code
  - Unit of measure (normalized to base unit)
  - Quantity (normalized to base unit)
  - Entered unit and entered quantity (preserved user input)
  - Line-specific notes
  - Sort order for custom ordering
  - Type-specific fields (e.g., `destination_type`, `consumption_type`, `consignment_receipt` (optional) for issues; `unit_price`, `unit_cost` for receipts)

#### Line-Based Serial Assignment
- **Per-Line Serial Management**: Serial numbers are now assigned and tracked at the line item level, not the document level
- **Serial Assignment Pages**: Each line item with a lot-tracked item has a dedicated serial assignment page accessible via a button in the document form
- **Serial Generation**: For receipt lines, serials are generated when the document is locked, with the format `{DOC_CODE}-L{LINE_ID}-{SEQUENCE:04d}`
- **Serial Reservation**: For issue lines, selected serials are reserved (`RESERVED` status) when assigned, and finalized (`ISSUED` or `CONSUMED`) when the document is locked
- **Validation**: Before locking a document, the system validates that:
  - For lot-tracked items, quantity must be a whole number
  - The number of assigned serials must exactly match the line quantity
  - All serials belong to the correct item and warehouse

### User Experience

#### Creating Multi-Line Documents
1. User creates a new receipt or issue document
2. Document header form is displayed (document code, date, supplier, etc.)
3. User can add multiple line items using the line formset
4. For each line:
   - Select item (filtered by company)
   - Select warehouse (filtered by item's allowed warehouses)
   - Enter quantity and select unit (limited to item's allowed units)
   - Enter pricing information (for receipts)
   - Add line-specific notes
5. User can add/remove lines dynamically
6. User saves the document

#### Serial Assignment Workflow

**For Receipt Lines:**
1. User creates/edits a receipt document
2. User adds a line item with a lot-tracked item
3. User saves the document
4. A "Manage Serials" button appears next to the line item
5. User clicks the button to open the serial management page
6. User can generate serials manually or they are auto-generated when the document is locked
7. Serial count is displayed next to the button

**For Issue Lines:**
1. User creates/edits an issue document
2. User adds a line item with a lot-tracked item
3. User saves the document
4. An "Assign Serials" button appears next to the line item (or "View Serials" if document is locked)
5. User clicks the button to open the serial assignment page
6. User selects the required number of serials from available serials
7. Selected serials are reserved for this line
8. Serial count (assigned/required) is displayed next to the button
9. When the document is locked, reserved serials are finalized to `ISSUED` or `CONSUMED` status

### Technical Implementation

#### Models
```python
# Base line model
class IssueLineBase(InventoryBaseModel, SortableModel):
    document = ForeignKey(...)  # Parent document
    item = ForeignKey(Item, ...)
    warehouse = ForeignKey(Warehouse, ...)
    unit = CharField(...)  # Normalized to base unit
    quantity = DecimalField(...)  # Normalized to base unit
    entered_unit = CharField(...)  # User's original input
    entered_quantity = DecimalField(...)  # User's original input
    serials = ManyToManyField(ItemSerial, ...)  # Assigned serials
    line_notes = TextField(...)

# Concrete line models
class IssuePermanentLine(IssueLineBase):
    document = ForeignKey(IssuePermanent, ...)
    destination_type = CharField(...)
    # ... other fields

class ReceiptPermanentLine(ReceiptLineBase):
    document = ForeignKey(ReceiptPermanent, ...)
    unit_price = DecimalField(...)
    # ... other fields
```

#### Forms and Formsets
- **Line Forms**: `IssuePermanentLineForm`, `IssueConsumptionLineForm`, etc. handle individual line item fields
- **Line Formsets**: `IssuePermanentLineFormSet`, `ReceiptPermanentLineFormSet`, etc. manage multiple lines
- **LineFormsetMixin**: Reusable mixin for views to handle line formset creation, validation, and saving

#### Views
- **LineFormsetMixin**: Provides `build_line_formset()`, `get_line_formset()`, and `_save_line_formset()` methods
- **Serial Assignment Views**: 
  - `IssueLineSerialAssignmentBaseView` for issue lines
  - `ReceiptLineSerialAssignmentBaseView` for receipt lines
- **Document Lock Views**: Updated to validate and finalize serials for all lines before/after locking

#### Services
- **`generate_receipt_line_serials()`**: Generates serials for a receipt line
- **`sync_issue_line_serials()`**: Reserves/releases serials for an issue line
- **`finalize_issue_line_serials()`**: Finalizes serials when an issue document is locked
- **Helper functions**: `_reserve_line_serials()`, `_release_line_serials()`, `_determine_final_status_for_line()`

### Benefits
- **Flexibility**: Users can add multiple items to a single document, reducing data entry time
- **Accuracy**: Serial tracking at the line level ensures precise traceability
- **Scalability**: Architecture supports future enhancements (e.g., line-level approvals, pricing variations)
- **User Experience**: Intuitive interface with clear visual indicators for serial assignment status

---

## 8. Receipt Capture & Unit Normalisation

### Highlights
- **فرم‌های اختصاصی رسید**: برای رسیدهای موقت، دائم و امانی مسیرهای ایجاد/ویرایش مستقلی پیاده‌سازی شده است؛ کاربر دیگر به پنل ادمین ارجاع داده نمی‌شود.
- **تولید خودکار متادیتا**: هنگام ایجاد سند، کد منحصربه‌فرد با الگوی `TMP|PRM|CON-YYYYMM-XXXXXX`، تاریخ روز و وضعیت اولیه (`Draft` برای رسید موقت) بدون دخالت کاربر ثبت می‌شود.
- **Auto-population of document_date and document_code**: All Issue and Receipt forms (`IssueConsumptionForm`, `IssueConsignmentForm`, `IssuePermanentForm`, etc.) automatically populate `document_date` and `document_code` fields using `clean_document_date()` and `clean_document_code()` methods. This prevents form submission failures due to missing auto-generated fields.
- **Multi-Line Support**: رسیدهای دائم و امانی اکنون از چند ردیف پشتیبانی می‌کنند؛ هر ردیف می‌تواند کالا، مقدار، انبار و قیمت مستقل داشته باشد.
- **واحدهای قابل انتخاب محدود**: فیلد واحد صرفاً واحد اصلی کالا و تبدیل‌های تعریف‌شده در `ItemUnit` را نمایش می‌دهد. اسکریپت پویا در قالب HTML در زمان تغییر کالا، فهرست واحدها را تازه‌سازی می‌کند.
- **یکسان‌سازی مقدار و قیمت**: پیش از ذخیره، مقدار (`quantity`) و قیمت (`unit_price` و `unit_price_estimate`) بر اساس ضرایب تبدیل واحد به واحد اصلی کالا تبدیل و در پایگاه‌داده ذخیره می‌شود. به این ترتیب موجودی مالی و تعدادی همیشه با یک واحد پایه محاسبه می‌شود.
- **الزام مقدار صحیح برای سریال‌ها**: اگر کالای انتخابی رهگیری سریال داشته باشد، فرم‌های رسید و حواله تنها مقادیر صحیح (پس از تبدیل واحد) را می‌پذیرند و در صورت مشاهده مقدار اعشاری خطا نمایش داده می‌شود.
- **نمایش اطلاعات مرجع**: در حالت ویرایش، بنر بالای فرم کد سند، تاریخ و وضعیت فعلی را به صورت فقط‌خواندنی نشان می‌دهد تا کاربر از داده‌های قطعی مطلع باشد.
- **حواله‌های اختصاصی**: برای حواله‌های دائم، مصرف و امانی نیز صفحات ایجاد/ویرایش مشابه رسیدها پیاده‌سازی شده و کد سند با الگوهای `ISP-`, `ISU-`, `ICN-` تولید می‌شود. کاربر می‌تواند واحد سازمانی مقصد (و برای مصرف، خط تولید مرتبط) را انتخاب کند و پس از قفل‌کردن سند دیگر امکان ویرایش/حذف وجود ندارد.
- **Consignment Receipt Optional**: In `IssueConsignmentLine`, the `consignment_receipt` and `consignment_receipt_code` fields are now optional (`null=True, blank=True`). Consignment issues can be created independently without requiring a consignment receipt, allowing more flexible workflow management.
- **شمارش موجودی اختصاصی**: اسناد کسری (`STD-`), مازاد (`STS-`) و ثبت نهایی (`STR-`) دارای صفحات ایجاد/ویرایش اختصاصی هستند؛ واحد و انبار مجاز بر اساس تنظیمات کالا محدود می‌شود، اختلاف مقدار و ارزش به صورت خودکار محاسبه می‌گردد و پس از قفل کردن سند فقط قابل مشاهده خواهد بود.

### Implementation Notes
- کلاس پایه‌ی `ReceiptBaseForm` متدهای `_get_item_allowed_units` و `_get_unit_factor` را ارائه می‌کند تا گراف تبدیل واحدها ساخته و ضریب تبدیل به واحد اصلی محاسبه شود.
- متد `_normalize_quantity` مقدار واردشده توسط کاربر را به واحد اصلی کالا تبدیل و با همان واحد در مدل ذخیره می‌کند.
- برای کالاهای دارای سریال، همین متد پس از تبدیل واحد بررسی می‌کند که مقدار نهایی عدد صحیح باشد و در غیر این صورت خطای کاربری برمی‌گرداند.
- فرم‌های `ReceiptPermanentForm` و `ReceiptConsignmentForm` علاوه بر مقدار، قیمت واحد را نیز به کمک ضریب محاسبه‌شده به قیمت واحد اصلی تبدیل می‌کنند.
- قالب `inventory/receipt_form.html` شامل بنر اطلاعات سند و اسکریپت جاوااسکریپت برای به‌روزرسانی پویا‌ی گزینه‌های واحد است.
- کلاس `StocktakingBaseForm` منطق مشترک فرم‌های کسری/مازاد/ثبت نهایی را مدیریت می‌کند (تولید کد سند، محدودسازی واحد و انبار مجاز، فیلدهای JSON پنهان و محاسبه خودکار اختلاف مقدار/ارزش) و قالب `inventory/stocktaking_form.html` همان تجربه کاربری رسیدها را برای شمارش موجودی به ارمغان می‌آورد.

---

## 8. Delete Functionality

### Features
- **Confirmation Page**: Prevents accidental deletions
- **Item Details Display**: Shows what will be deleted
- **Warning Message**: "This action cannot be undone"
- **Two-Button Choice**: "Yes, Delete" (red) or "Cancel"
- **Success Message**: Confirmation after deletion
- **Return Navigation**: Redirects to list view

### Implementation
Generic delete template used via symlinks for consistency.

---

## 9. Inventory Balance Calculation

### Purpose
Real-time calculation of item quantities in warehouses based on stocktaking baselines and subsequent document movements.

### Calculation Logic
1. **Baseline Detection**:
   - First checks for `StocktakingSurplus`/`StocktakingDeficit` documents linked to a stocktaking record
   - If not found, uses the latest approved and locked `StocktakingRecord` as baseline (with quantity 0)
   - Baseline date is the date of the stocktaking record
2. **Receipts**: Sum of all permanent receipts and consignment receipts from baseline date
3. **Issues**: Sum of all permanent issues, consumption issues, and consignment issues from baseline date
4. **Adjustments**: Apply stocktaking surpluses (add) and deficits (subtract)

### Features
- **Company-scoped calculations**: All queries filtered by active company
- **Warehouse filtering**: Calculate balance for specific warehouse
- **Item type/category filtering**: Filter by item type and category
- **As-of-date calculations**: Calculate balance as of any date (default: today)
- **Automatic date handling**: "As of Date" field is hidden and automatically set to today
- **Line-based queries**: Queries line item models (`ReceiptPermanentLine`, `IssueConsumptionLine`, etc.) instead of header models
- **Transaction inclusion**: Includes items with actual transactions, not just explicit warehouse assignments
- **Details page**: Click "Details" button to view complete transaction history for an item
  - Shows all receipts and issues from baseline date to selected date
  - Displays running balance calculation for each transaction
  - Accessible via `/inventory/balance/details/<item_id>/<warehouse_id>/`
- **JSON API endpoint**: `/inventory/api/balance/` for AJAX queries

### Technical Implementation
- **Module**: `inventory/inventory_balance.py`
- **Main Functions**:
  - `get_last_stocktaking_baseline()`: Retrieves baseline from stocktaking records
  - `calculate_movements_after_baseline()`: Calculates receipts and issues after baseline
  - `calculate_item_balance()`: Complete balance for a single item
  - `calculate_warehouse_balances()`: Bulk calculation for all items in warehouse
- **View**: `InventoryBalanceView` and `InventoryBalanceDetailsView`
- **Template**: `templates/inventory/inventory_balance.html` and `templates/inventory/inventory_balance_details.html`

### Important Notes
- Only enabled documents are included (`document__is_enabled=1`)
- Consignment receipts/issues are included in calculations
- Baseline uses approved and locked `StocktakingRecord` when surplus/deficit documents don't exist
- Date display: Baseline date shown in Jalali format using `|jalali_date` filter

### Performance Considerations
- Indexes on (company_id, warehouse_id, item_id, document_date)
- Efficient query aggregation using line item models
- N+1 pattern in `calculate_warehouse_balances()` (one query per item)
- Caching planned for future versions

---

## 9.1 Stocktaking Approval Workflow

### Overview
Stocktaking records now support a formal approval workflow with designated approvers and approval status tracking.

### Key Features

#### Approval Status
- **Three Status Options**:
  - `pending`: Initial status, awaiting approval
  - `approved`: Approved by designated approver
  - `rejected`: Rejected by designated approver
- **Automatic Timestamp**: `approved_at` field automatically set when status changes to `approved`, cleared when changed to `pending` or `rejected`

#### Approver Management
- **User-Based Approvers**: `confirmed_by` and `approver` fields changed from `Person` to `User` model
- **Company Scoping**: Approvers filtered by company access (`UserCompanyAccess`)
- **Field Display**: Approver fields show `username - Full Name` or just `username` if no full name
- **Permission Enforcement**: Only the designated `approver` can change `approval_status`
  - Client-side: `approval_status` field disabled if current user is not the selected approver
  - Server-side: `clean()` method validates that only the approver can change status

#### Form Structure
- **Field Order**: `approver` field appears before `approval_status` in the form
- **Dynamic Behavior**: Form automatically enables/disables `approval_status` based on current user
- **Validation**: Server-side validation ensures only approver can modify approval status

### Technical Implementation
- **Model**: `StocktakingRecord` in `inventory/models.py`
  - `confirmed_by`: ForeignKey to `User` (was `Person`)
  - `approver`: ForeignKey to `User` (was `Person`)
  - `approval_status`: CharField with choices (pending, approved, rejected)
  - `approved_at`: DateTimeField (auto-set/cleared)
- **Form**: `StocktakingRecordForm` in `inventory/forms.py`
  - `approval_status`: ChoiceField with three options
  - `__init__`: Disables `approval_status` if user is not the approver
  - `clean()`: Server-side permission check
  - `save()`: Auto-sets/clears `approved_at` based on status
- **Migration**: `0020_change_stocktaking_users.py` updates foreign keys from `Person` to `User`

### Use Cases
- Formal approval process for stocktaking records
- Audit trail of who approved/rejected stocktaking
- Integration with inventory balance calculation (only approved records used as baseline)

---

## 10. Procurement Requests

### Purchase Requests

#### Purpose
- Manage demand for externally sourced items with routing to authorized approvers.

#### Features
- Auto-generated codes following `PRQ-YYYYMM-XXXXXX`.
- Dedicated create/edit forms with item-aware unit dropdown (default unit + defined conversions).
- Approver selection restricted to personnel (from production module) granted the purchase-request approval permission.
- Approval action locks the request (`is_locked=1`), records timestamp, and exposes it to permanent/consignment receipt forms.
- Receipt forms validate that the selected request matches both item and company before updating fulfillment quantities.
- User-entered unit/quantity/price values are preserved for display while normalized values are stored for calculation.

#### Use Cases
- Procurement of raw materials, packaging, services, or maintenance spares that require managerial approval prior to receipt.

### Warehouse Requests

#### Purpose
Internal material requisition workflow

#### Features
- **Request Code**: Auto-generated `WRQ-YYYYMM-XXXXXX`
- **Item Selection**: From company's item catalog
- **Quantity Request**: With unit of measure restricted to the item's primary/alternate units
- **Priority**: Low, Normal, High, Urgent
- **Requester**: Linked to Person
- **Approver**: Optional designated approver filtered by warehouse-request approval permission
- **Department**: Requesting unit/department
- **Approval Workflow**:
  1. Draft
  2. Submitted
  3. Approved (by authorized person)
  4. Issued (linked to actual issue document)
  5. Cancelled (if rejected)
- **Locking & Linking**: Once approved the request is locked (`is_locked=1`) and becomes selectable in permanent/consignment receipt forms; forms validate item/warehouse alignment before accepting the link.

#### Use Cases
- Production line requesting materials
- Department requesting supplies
- Maintenance requesting spare parts
- Quality control requesting samples

---

## 11. UI/UX Features

### Navigation
- **Sidebar**: Hierarchical menu with module grouping
- **Expandable Submenus**: Click to expand/collapse
- **Active Indicators**: Current page highlighted
- **Module Icons**: Visual distinction between modules

### Header
- **Company Selector**: Dropdown with logo/icon
- **Language Switcher**: Instant language change
- **User Menu**: Welcome message and logout
- **Breadcrumbs**: Contextual navigation path

### Styling
- **Consistent Colors**:
  - Primary: Blue (#3b82f6)
  - Success: Green (#10b981)
  - Danger: Red (#dc2626)
  - Warning: Yellow (#f59e0b)
- **Status Badges**:
  - Active: Green background
  - Inactive: Gray background
- **Buttons**:
  - Primary: Blue
  - Secondary: Gray
  - Danger: Red

### Responsive Design
- Mobile-friendly tables
- Collapsible sidebar
- Touch-friendly buttons
- Readable font sizes

---

## 12. Security Features

### Authentication
- Django session-based authentication
- Login required for all views
- Secure password hashing

### Authorization
- Company-based data isolation
- Users see only authorized companies
- QuerySet filtering by company_id
- Session-based company context
- Centralised permission catalogue (`shared/permissions.py`) with actions for:
  - Viewing own records vs. all records (`VIEW_OWN`, `VIEW_ALL`)
  - Creating, editing, deleting (`CREATE`, `EDIT_OWN`, `EDIT_OTHER`, `DELETE_OWN`, `DELETE_OTHER`)
  - Locking/unlocking own or other users' documents (`LOCK_OWN`, `LOCK_OTHER`, `UNLOCK_OWN`, `UNLOCK_OTHER`)
  - Approve / Reject / Cancel flows برای گردش کارهای دارای تأیید (`APPROVE`, `REJECT`, `CANCEL`)
  - **نکته**: `DELETE_OTHER` به تمام اسناد (receipts، issues، requests، stocktaking) اضافه شده است تا امکان حذف اسناد سایر کاربران برای کاربران با دسترسی مناسب فراهم شود.
  - `APPROVE` برای stocktaking records نیز پشتیبانی می‌شود.
- Dedicated Shared module UI برای مدیریت کاربران، گروه‌ها و سطوح دسترسی:
  - **User Management**:
    - فرم‌های ایجاد/ویرایش کاربر همراه با تعیین رمز، گروه‌ها و دسترسی شرکت‌ها
    - `groups` field uses `CheckboxSelectMultiple` widget for intuitive multi-selection
    - Users can be assigned to multiple groups simultaneously
  - **Group Management**:
    - `members` field removed from Group form (membership now managed via User form)
    - `access_levels` field uses `CheckboxSelectMultiple` widget for intuitive multi-selection
    - Groups can be assigned multiple access levels simultaneously
    - Supports `GroupProfile` model with description and enabled flag
  - **Access Level Management**:
    - ماتریس انتخاب اکشن‌ها برای هر Access Level بر اساس `FEATURE_PERMISSION_MAP`
    - **Quick Action Buttons**: دکمه‌های "همه" و "هیچکدام" برای هر Feature (ردیف) و کل صفحه برای انتخاب/لغو انتخاب گروهی permissions

### Data Protection
- CSRF protection on all forms
- SQL injection prevention (ORM)
- XSS prevention (template auto-escaping)
- Secure session cookies

### Audit Trail
- created_at / updated_at timestamps
- created_by / edited_by user tracking
- Metadata JSON field for extensibility
- Future: Full audit log table planned

---

## 13. Code Generation

### Patterns
- **Company**: `CCC` (3 digits)
- **Person**: `CCCCCCCC` (8 digits)
- **ItemType**: `TTT` (3 digits)
- **ItemCategory**: `CCC` (3 digits)
- **ItemSubcategory**: `SSS` (3 digits)
- **Item**: `UUSSSSS` (7 digits: User 2 + Sequence 5)
- **Item Full Code**: `TTTCCCSSSUUSSSSS` (16 digits)
- **Warehouse**: `WWWWW` (5 digits)
- **Warehouse Request**: `WRQ-YYYYMM-XXXXXX`

### Auto-Generation
- Codes auto-increment within scope
- Unique constraints enforced at database level
- User segment manually entered, sequence auto-generated
- Zero-padded for consistent length

---

## 14. Developer Experience

### Code Organization
- Clear module separation
- Reusable base classes
- DRY principle (Don't Repeat Yourself)
- Generic templates via symlinks
- Consistent naming conventions

### Documentation
- Comprehensive README files per module
- Form documentation
- Balance calculation documentation
- Inline code comments
- Docstrings for all functions

### Testing Support
- Test-friendly architecture
- Fixtures for test data
- Factory functions planned
- CI/CD ready

---

## 15. Future Features

See CHANGELOG.md and README.md Roadmap section for planned features.

