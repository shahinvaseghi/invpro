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
- **Persian (Farsi)** - Primary language with full RTL support
- **English** - Secondary language

### Features
- **Language Switcher**: Header dropdown for instant language switching
- **RTL/LTR Auto-Detection**: Layout automatically adjusts
- **Font Optimization**: Vazir font for Persian, system fonts for English
- **Complete Translation**: All UI strings translated
- **Form Labels**: All form fields have Persian/English labels
- **Error Messages**: Validation errors in user's language

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

## 4. Personnel & Company Management

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

### Personnel Management
**Features**:
- 8-digit unique person code
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
- **Action Columns**: Edit and Delete buttons for each row
- **Status Badges**: Color-coded Active/Inactive indicators
- **Pagination**: 50 items per page
- **Empty States**: User-friendly messages with create buttons
- **Create Button**: Prominent "+ Create X" button at top
- **Breadcrumbs**: Navigation path
- **Company Filtering**: Auto-filtered by active company

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
- Personnel

---

## 7. Receipt Capture & Unit Normalisation

### Highlights
- **فرم‌های اختصاصی رسید**: برای رسیدهای موقت، دائم و امانی مسیرهای ایجاد/ویرایش مستقلی پیاده‌سازی شده است؛ کاربر دیگر به پنل ادمین ارجاع داده نمی‌شود.
- **تولید خودکار متادیتا**: هنگام ایجاد سند، کد منحصربه‌فرد با الگوی `TMP|PRM|CON-YYYYMM-XXXXXX`، تاریخ روز و وضعیت اولیه (`Draft` برای رسید موقت) بدون دخالت کاربر ثبت می‌شود.
- **واحدهای قابل انتخاب محدود**: فیلد واحد صرفاً واحد اصلی کالا و تبدیل‌های تعریف‌شده در `ItemUnit` را نمایش می‌دهد. اسکریپت پویا در قالب HTML در زمان تغییر کالا، فهرست واحدها را تازه‌سازی می‌کند.
- **یکسان‌سازی مقدار و قیمت**: پیش از ذخیره، مقدار (`quantity`) و قیمت (`unit_price` و `unit_price_estimate`) بر اساس ضرایب تبدیل واحد به واحد اصلی کالا تبدیل و در پایگاه‌داده ذخیره می‌شود. به این ترتیب موجودی مالی و تعدادی همیشه با یک واحد پایه محاسبه می‌شود.
- **الزام مقدار صحیح برای سریال‌ها**: اگر کالای انتخابی رهگیری سریال داشته باشد، فرم‌های رسید و حواله تنها مقادیر صحیح (پس از تبدیل واحد) را می‌پذیرند و در صورت مشاهده مقدار اعشاری خطا نمایش داده می‌شود.
- **نمایش اطلاعات مرجع**: در حالت ویرایش، بنر بالای فرم کد سند، تاریخ و وضعیت فعلی را به صورت فقط‌خواندنی نشان می‌دهد تا کاربر از داده‌های قطعی مطلع باشد.
- **حواله‌های اختصاصی**: برای حواله‌های دائم، مصرف و امانی نیز صفحات ایجاد/ویرایش مشابه رسیدها پیاده‌سازی شده و کد سند با الگوهای `ISP-`, `ISU-`, `ICN-` تولید می‌شود. کاربر می‌تواند واحد سازمانی مقصد (و برای مصرف، خط تولید مرتبط) را انتخاب کند و پس از قفل‌کردن سند دیگر امکان ویرایش/حذف وجود ندارد.
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
Real-time calculation of item quantities in warehouses

### Calculation Logic
1. **Baseline**: Last stocktaking record for item/warehouse
2. **Receipts**: Add permanent, temporary, consignment receipts
3. **Issues**: Subtract permanent, consumption, consignment issues
4. **Adjustments**: Apply stocktaking deficits (subtract) and surpluses (add)

### Features
- Company-scoped calculations
- Warehouse filtering
- Item type/category filtering
- As-of-date calculations
- JSON API endpoint for AJAX queries

### Performance Considerations
- Indexes on (company_id, warehouse_id, item_id, document_date)
- Efficient query aggregation
- Caching planned for future versions

---

## 10. Procurement Requests

### Purchase Requests

#### Purpose
- Manage demand for externally sourced items with routing to authorized approvers.

#### Features
- Auto-generated codes following `PRQ-YYYYMM-XXXXXX`.
- Dedicated create/edit forms with item-aware unit dropdown (default unit + defined conversions).
- Approver selection restricted to personnel granted the purchase-request approval permission.
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
  - Viewing own records vs. all records
  - Creating, editing, deleting, locking/unlocking (own vs. دیگران)
  - Approve / Reject / Cancel flows برای گردش کارهای دارای تأیید
- Dedicated Shared module UI برای مدیریت کاربران، گروه‌ها و سطوح دسترسی:
  - فرم‌های ایجاد/ویرایش کاربر همراه با تعیین رمز، گروه‌ها و دسترسی شرکت‌ها
  - قالب‌های گروه برای نگاشت اعضا و سطوح دسترسی (پشتیبانی از `GroupProfile`)
  - ماتریس انتخاب اکشن‌ها برای هر Access Level بر اساس `FEATURE_PERMISSION_MAP`

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

