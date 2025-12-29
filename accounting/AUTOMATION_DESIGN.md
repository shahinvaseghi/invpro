# طراحی سیستم خودکارسازی اسناد حسابداری

## مقدمه

این سند شامل طراحی و ساختار سیستم خودکارسازی برای ایجاد خودکار اسناد حسابداری بر اساس رویدادهای مختلف در سیستم است.

## هدف

ایجاد یک فرایندساز (Process Builder) که به کاربران امکان تعریف فرایندهای خودکار را می‌دهد تا بر اساس رویدادهای مختلف (مثل ثبت فاکتور فروش، حواله انبار، دریافت خزانه و ...) به صورت خودکار اسناد حسابداری ایجاد شوند.

---

## ساختار کلی فرایند

### مرحله 1: انتخاب سند مبدأ (Trigger Document)

کاربر باید یک سند را از بین تمام اسناد موجود در ماژول‌های مختلف انتخاب کند:

**ماژول‌های قابل انتخاب:**
- **حسابداری**: اسناد حسابداری، دریافت/پرداخت خزانه، انتقال بین حساب‌ها
- **انبار**: حواله‌ها، رسیدها، تعدیلات
- **فروش**: فاکتورهای فروش
- **خرید**: سفارشات خرید، فاکتورهای خرید
- **تولید**: دستورات تولید
- **سایر ماژول‌ها**: بر اساس نیاز

**اطلاعات مورد نیاز:**
- نوع سند (Document Type)
- ماژول مربوطه
- مدل Django مربوطه

---

### مرحله 2: تعریف شرایط (Conditions/Filters)

کاربر باید مشخص کند که این فرایند روی چه اسنادی اعمال شود. شرایط به دو دسته تقسیم می‌شوند:

#### 2.1 فیلترهای عمومی (Global Filters)

این فیلترها برای تمام انواع اسناد قابل استفاده هستند:

1. **فیلتر بر اساس کاربر:**
   - اسناد ایجاد شده توسط کاربر خاص
   - عملگر: `==` (برابر با)
   - مقدار: شناسه کاربر یا لیست کاربران

2. **فیلتر بر اساس گروه کاربری:**
   - اسناد ایجاد شده توسط کاربران عضو یک گروه خاص
   - عملگر: `in` (عضو گروه)
   - مقدار: شناسه گروه یا لیست گروه‌ها

3. **فیلتر بر اساس تاریخ:**
   - **تاریخ خاص:** اسناد با تاریخ دقیق
     - عملگر: `==`
     - مقدار: تاریخ
   - **بازه تاریخی:** اسناد در بازه زمانی خاص
     - عملگر: `between` یا ترکیب `>=` و `<=`
     - مقدار: تاریخ شروع و تاریخ پایان

4. **فیلتر بر اساس وضعیت سند:**
   - اسناد با وضعیت خاص (مثلاً قطعی شده، باز، برگشتی)
   - عملگر: `==` یا `in`
   - مقدار: وضعیت یا لیست وضعیت‌ها

#### 2.2 فیلترهای خاص نوع سند (Document-Specific Filters)

این فیلترها بسته به نوع سند مبدأ متفاوت هستند و فیلدهای خاص آن نوع سند را هدف قرار می‌دهند:

**مثال‌ها برای انواع مختلف اسناد:**

1. **فاکتور فروش (Sales Invoice):**
   - **تفصیلی مشتری:** فیلتر بر اساس تفصیلی انتخاب شده به عنوان مشتری
     - عملگر: `==`, `in`, `hierarchy_level`, `hierarchy_parent`
     - مقدار: شناسه تفصیلی یا سطح سلسله مراتب
   - **مبلغ فاکتور:** فیلتر بر اساس مبلغ کل
     - عملگر: `>`, `<`, `>=`, `<=`, `==`
     - مقدار: مبلغ
   - **نوع پرداخت:** نقدی، چکی، نسیه
   - **وضعیت پرداخت:** پرداخت شده، پرداخت نشده

2. **حواله دائم (Permanent Issue):**
   - **انبار مبدأ:** فیلتر بر اساس انبار مبدأ
     - عملگر: `==`, `in`
     - مقدار: شناسه انبار یا لیست انبارها
   - **انبار مقصد:** فیلتر بر اساس انبار مقصد
   - **مرکز هزینه:** فیلتر بر اساس مرکز هزینه مرتبط
   - **نوع حواله:** مصرف، انتقال، و غیره

3. **رسید کالا (Receipt):**
   - **تامین‌کننده:** فیلتر بر اساس تامین‌کننده
     - عملگر: `==`, `in`
     - مقدار: شناسه تامین‌کننده یا لیست تامین‌کنندگان
   - **نوع رسید:** موقت، دائم، امانی
   - **انبار مقصد:** فیلتر بر اساس انبار دریافت

4. **سند حسابداری (Accounting Document):**
   
   **فیلترهای ستون بدهکار:**
   - **سطح تفصیلی:** فیلتر بر اساس یک سطح خاص از تفصیلی در ستون بدهکار
     - عملگر: `hierarchy_level`
     - مقدار: سطح تفصیلی (مثلاً سطح 2)
   - **تفصیلی مشخص:** فیلتر بر اساس یک تفصیلی خاص در ستون بدهکار
     - عملگر: `==`, `in`
     - مقدار: شناسه تفصیلی یا لیست تفصیلی‌ها
   - **معین:** فیلتر بر اساس یک معین خاص در ستون بدهکار
     - عملگر: `==`, `in`
     - مقدار: شناسه معین یا لیست معین‌ها
   - **سند کل:** فیلتر بر اساس یک سند کل خاص در ستون بدهکار
     - عملگر: `==`, `in`
     - مقدار: شناسه سند کل یا لیست سند کل‌ها
   
   **فیلترهای ستون بستانکار:**
   - **سطح تفصیلی:** فیلتر بر اساس یک سطح خاص از تفصیلی در ستون بستانکار
     - عملگر: `hierarchy_level`
     - مقدار: سطح تفصیلی (مثلاً سطح 2)
   - **تفصیلی مشخص:** فیلتر بر اساس یک تفصیلی خاص در ستون بستانکار
     - عملگر: `==`, `in`
     - مقدار: شناسه تفصیلی یا لیست تفصیلی‌ها
   - **معین:** فیلتر بر اساس یک معین خاص در ستون بستانکار
     - عملگر: `==`, `in`
     - مقدار: شناسه معین یا لیست معین‌ها
   - **سند کل:** فیلتر بر اساس یک سند کل خاص در ستون بستانکار
     - عملگر: `==`, `in`
     - مقدار: شناسه سند کل یا لیست سند کل‌ها
   
   **فیلترهای کاربر:**
   - **کاربر صادرکننده:** فیلتر بر اساس کاربری که سند را صادر کرده است
     - عملگر: `==`, `in`
     - مقدار: شناسه کاربر یا لیست کاربران
   - **گروه کاربری صادرکننده:** فیلتر بر اساس گروه کاربری صادرکننده سند
     - عملگر: `in`
     - مقدار: شناسه گروه یا لیست گروه‌های کاربری
   
   **فیلترهای تاریخ:**
   - **تاریخ خاص:** فیلتر بر اساس تاریخ دقیق سند
     - عملگر: `==`, `!=`
     - مقدار: تاریخ
   - **بازه تاریخی:** فیلتر بر اساس بازه زمانی
     - عملگر: `between`, `>=` و `<=`
     - مقدار: تاریخ شروع و تاریخ پایان

5. **دریافت/پرداخت خزانه (Treasury Transaction):**
   - **حساب نقدی/بانکی:** فیلتر بر اساس حساب
   - **نوع تراکنش:** دریافت، پرداخت
   - **طرف حساب:** فیلتر بر اساس طرف حساب

**ساختار پیشنهادی برای فیلترها:**

```python
AutomationCondition:
  - id
  - process_id: فرایند مربوطه
  - filter_type: نوع فیلتر (global, document_specific)
  - filter_category: دسته فیلتر (user, user_group, date, date_range, status, document_field)
  - field_name: نام فیلد (برای فیلترهای document_specific)
  - field_type: نوع فیلد (string, number, date, foreign_key, many_to_many)
  - operator: عملگر (==, !=, >, <, >=, <=, in, not_in, contains, starts_with, ends_with, between, hierarchy_level, hierarchy_parent, hierarchy_descendant)
  - value: مقدار مقایسه (JSON - می‌تواند single value یا array باشد)
  - value_type: نوع مقدار (static, variable, calculated)
  - logical_operator: AND/OR (برای ترکیب با شرط بعدی)
  - order: ترتیب شرط
  - is_active: فعال/غیرفعال
```

**نکات مهم:**

1. **فیلترهای سلسله مراتبی تفصیلی:**
   - `hierarchy_level`: تفصیلی در سطح خاصی از سلسله مراتب
   - `hierarchy_parent`: تفصیلی زیرمجموعه یک تفصیلی والد
   - `hierarchy_descendant`: تفصیلی که زیرمجموعه (مستقیم یا غیرمستقیم) یک تفصیلی است

2. **فیلترهای ترکیبی:**
   - می‌توان چندین فیلتر را با AND/OR ترکیب کرد
   - ترتیب فیلترها مهم است (با `order` مشخص می‌شود)

3. **فیلترهای داینامیک:**
   - سیستم باید فیلدهای قابل فیلتر را بر اساس نوع سند مبدأ به صورت داینامیک نمایش دهد
   - باید validation برای هر نوع فیلد انجام شود

4. **UI پیشنهادی:**
   - بخش جداگانه برای فیلترهای عمومی
   - بخش جداگانه برای فیلترهای خاص نوع سند
   - امکان اضافه/حذف فیلترها
   - نمایش پیش‌نمایش شرط نهایی
   - امکان تست فیلتر روی یک سند نمونه

5. **شناسایی فیلدهای قابل فیلتر:**
   
   برای هر نوع سند، باید یک registry یا configuration وجود داشته باشد که فیلدهای قابل فیلتر را مشخص کند:
   
   ```python
   # مثال ساختار برای ثبت فیلدهای قابل فیلتر
   DOCUMENT_FILTERABLE_FIELDS = {
       'sales.Invoice': {
           'customer_tafsili': {
               'field_type': 'foreign_key',
               'model': 'accounting.TafsiliAccount',
               'label': 'تفصیلی مشتری',
               'operators': ['==', 'in', 'hierarchy_level', 'hierarchy_parent'],
               'hierarchy_support': True
           },
           'total_amount': {
               'field_type': 'number',
               'label': 'مبلغ کل فاکتور',
               'operators': ['==', '!=', '>', '<', '>=', '<=']
           },
           'payment_type': {
               'field_type': 'choice',
               'label': 'نوع پرداخت',
               'choices': ['cash', 'check', 'credit'],
               'operators': ['==', 'in']
           }
       },
       'inventory.PermanentIssue': {
           'source_warehouse': {
               'field_type': 'foreign_key',
               'model': 'inventory.Warehouse',
               'label': 'انبار مبدأ',
               'operators': ['==', 'in']
           },
           'cost_center': {
               'field_type': 'foreign_key',
               'model': 'accounting.CostCenter',
               'label': 'مرکز هزینه',
               'operators': ['==', 'in', 'is_null', 'is_not_null']
           }
       },
       'inventory.Receipt': {
           'supplier': {
               'field_type': 'foreign_key',
               'model': 'inventory.Supplier',
               'label': 'تامین‌کننده',
               'operators': ['==', 'in']
           },
           'receipt_type': {
               'field_type': 'choice',
               'label': 'نوع رسید',
               'choices': ['temporary', 'permanent', 'consignment'],
               'operators': ['==', 'in']
           }
       }
   }
   ```
   
   این ساختار باید:
   - به صورت داینامیک از مدل Django استخراج شود
   - یا به صورت دستی در یک فایل configuration تعریف شود
   - در UI به صورت dropdown یا autocomplete نمایش داده شود
   - عملگرهای مناسب برای هر نوع فیلد را پیشنهاد دهد

---

### مرحله 3: استخراج متغیرها (Variables/Parameters)

در این مرحله، کاربر باید فیلدهایی از سند مبدأ را انتخاب کند که به عنوان متغیر در مراحل بعدی (ایجاد اسناد) استفاده شوند.

#### 3.1 نمایش ساختار سند

سیستم باید ساختار کامل سند انتخاب شده در مرحله 1 را به صورت تعاملی نمایش دهد:

**بخش‌های قابل نمایش:**
1. **فیلدهای هدر سند (Header Fields):**
   - فیلدهای اصلی سند (مثل تاریخ، شماره، توضیحات)
   - فیلدهای ForeignKey (مثل مشتری، انبار، تامین‌کننده)
   - فیلدهای محاسباتی (مثل مبلغ کل)

2. **فیلدهای خطوط سند (Line Items):**
   - فیلدهای هر خط (مثل کالا، مقدار، قیمت، مبلغ)
   - امکان انتخاب فیلد از خطوط (مثلاً مجموع مبلغ تمام خطوط)

3. **فیلدهای مرتبط (Related Fields):**
   - فیلدهای مدل‌های مرتبط (مثلاً نام مشتری از طریق ForeignKey)
   - فیلدهای سلسله مراتبی (مثلاً تفصیلی والد)

#### 3.2 انتخاب فیلدها به عنوان متغیر

**روند کار:**
1. سیستم ساختار سند را به صورت درختی یا جدولی نمایش می‌دهد
2. کاربر روی هر فیلدی که می‌خواهد به عنوان متغیر استفاده کند کلیک می‌کند
3. با کلیک روی فیلد، یک متغیر جدید ایجاد می‌شود
4. کاربر می‌تواند نام متغیر را تعیین کند (یا از نام پیش‌فرض استفاده کند)

**نمایش پیشنهادی:**
```
┌─────────────────────────────────────┐
│ ساختار سند: فاکتور فروش             │
├─────────────────────────────────────┤
│ 📄 هدر سند                          │
│   ☐ تاریخ: 1403/10/15               │
│   ☐ شماره فاکتور: INV-001          │
│   ☑ مشتری: [مشتری A] ← متغیر: customer
│   ☐ مبلغ کل: 1,000,000              │
│   ☑ مبلغ کل: 1,000,000 ← متغیر: invoice_total
│                                     │
│ 📋 خطوط سند                         │
│   ┌─ خط 1                           │
│   │  ☐ کالا: کالای A                │
│   │  ☐ مقدار: 10                    │
│   │  ☐ قیمت: 100,000                │
│   │  ☑ مبلغ: 1,000,000 ← متغیر: line1_amount
│   └─────────────────────────────────│
│                                     │
│ 🔗 فیلدهای مرتبط                   │
│   ☑ نام مشتری ← متغیر: customer_name
│   ☑ تفصیلی مشتری ← متغیر: customer_tafsili
└─────────────────────────────────────┘

📌 متغیرهای انتخاب شده:
  • customer (تفصیلی مشتری)
  • invoice_total (مبلغ کل فاکتور)
  • line1_amount (مبلغ خط 1)
  • customer_name (نام مشتری)
  • customer_tafsili (تفصیلی مشتری)
```

#### 3.3 انواع متغیرها

**1. متغیرهای مستقیم از فیلدهای سند:**
- فیلدهای هدر: `date`, `number`, `total_amount`
- فیلدهای خطوط: `line.quantity`, `line.price`, `line.amount`
- مثال: انتخاب فیلد "مشتری" از هدر فاکتور فروش → متغیر `customer`

**2. متغیرهای از فیلدهای مرتبط (Related):**
- فیلدهای مدل‌های ForeignKey
- مثال: انتخاب "نام مشتری" از طریق ForeignKey مشتری → متغیر `customer_name`
- مثال: انتخاب "تفصیلی مشتری" از طریق ForeignKey مشتری → متغیر `customer_tafsili`

**3. متغیرهای محاسباتی (Aggregated):**
- مجموع یک فیلد از تمام خطوط: `sum(line.amount)`
- تعداد خطوط: `count(lines)`
- میانگین: `avg(line.price)`
- حداکثر/حداقل: `max(line.amount)`, `min(line.amount)`
- مثال: مجموع مبلغ تمام خطوط فاکتور → متغیر `total_lines_amount`

**4. متغیرهای ترکیبی (Computed):**
- ترکیب چند فیلد: `{customer_name} - {invoice_number}`
- محاسبات: `{total_amount} * 0.09` (برای محاسبه VAT)
- مثال: ترکیب نام مشتری و شماره فاکتور → متغیر `description`

#### 3.4 نام‌گذاری متغیرها

**قوانین نام‌گذاری:**
- نام متغیر باید یکتا باشد (در محدوده فرایند)
- می‌تواند فارسی یا انگلیسی باشد
- پیشنهاد: استفاده از نام انگلیسی برای سازگاری با کد
- سیستم می‌تواند نام پیش‌فرض پیشنهاد دهد بر اساس نام فیلد

**مثال‌ها:**
- فیلد "مشتری" → نام پیش‌فرض: `customer` یا `customer_tafsili`
- فیلد "مبلغ کل" → نام پیش‌فرض: `total_amount` یا `invoice_total`
- فیلد "نام کالا" از خط → نام پیش‌فرض: `item_name` یا `product_name`

#### 3.5 ساختار پیشنهادی

```python
AutomationVariable:
  - id
  - process_id: فرایند مربوطه (ForeignKey)
  - name: نام متغیر (برای استفاده در مراحل بعدی) - CharField, unique per process
  - display_name: نام نمایشی (فارسی) - CharField
  - source_type: نوع منبع (field, related_field, aggregated, computed) - CharField
  - field_path: مسیر فیلد (مثلاً "customer" یا "customer.name" یا "lines.amount") - CharField
  - field_type: نوع فیلد در سند (header_field, line_field, related_field) - CharField
  - aggregation_type: نوع تجمیع (sum, count, avg, max, min) - CharField, nullable
  - computation_expression: عبارت محاسباتی (برای computed) - TextField, nullable
  - data_type: نوع داده (string, number, date, boolean, foreign_key) - CharField
  - related_model: مدل مرتبط (اگر related_field باشد) - CharField, nullable
  - default_value: مقدار پیش‌فرض (اختیاری) - JSONField, nullable
  - description: توضیحات متغیر - TextField, nullable
  - order: ترتیب نمایش - IntegerField
  - is_active: فعال/غیرفعال - BooleanField, default=True
  - created_at, updated_at
  - created_by, updated_by
```

#### 3.6 UI پیشنهادی

**صفحه انتخاب متغیرها:**

1. **بخش نمایش ساختار سند:**
   - نمایش درختی یا جدولی از فیلدهای سند
   - امکان expand/collapse برای بخش‌های مختلف
   - نمایش نوع هر فیلد (string, number, date, foreign_key)
   - نمایش فیلدهای انتخاب شده با رنگ متفاوت

2. **بخش متغیرهای انتخاب شده:**
   - لیست متغیرهای انتخاب شده
   - امکان ویرایش نام متغیر
   - امکان حذف متغیر
   - نمایش پیش‌نمایش مقدار (با استفاده از یک سند نمونه)

3. **قابلیت‌های اضافی:**
   - امکان drag & drop برای تغییر ترتیب
   - امکان گروه‌بندی متغیرها
   - امکان تست متغیرها روی یک سند نمونه
   - نمایش پیش‌نمایش مقدار متغیرها

#### 3.7 مثال‌های کاربردی

**مثال 1: فاکتور فروش**

ساختار سند:
- هدر: تاریخ، شماره، مشتری (ForeignKey)، مبلغ کل
- خطوط: کالا، مقدار، قیمت، مبلغ

متغیرهای انتخاب شده:
- `customer` ← فیلد "مشتری" از هدر (نوع: ForeignKey → TafsiliAccount)
- `customer_name` ← فیلد "نام" از مدل مرتبط مشتری
- `invoice_total` ← فیلد "مبلغ کل" از هدر
- `invoice_date` ← فیلد "تاریخ" از هدر
- `invoice_number` ← فیلد "شماره فاکتور" از هدر
- `total_lines_amount` ← مجموع فیلد "مبلغ" از تمام خطوط

**مثال 2: رسید کالا**

ساختار سند:
- هدر: تاریخ، شماره، تامین‌کننده (ForeignKey)، انبار (ForeignKey)
- خطوط: کالا (ForeignKey)، مقدار، قیمت، مبلغ

متغیرهای انتخاب شده:
- `supplier` ← فیلد "تامین‌کننده" از هدر
- `supplier_name` ← فیلد "نام" از مدل مرتبط تامین‌کننده
- `warehouse` ← فیلد "انبار" از هدر
- `item_name` ← فیلد "نام کالا" از خط اول (برای استفاده در سند هزینه)
- `receipt_total` ← فیلد "مبلغ کل" از هدر
- `line_items` ← تمام خطوط (برای استفاده در سند حسابداری)

**مثال 3: حواله انبار**

ساختار سند:
- هدر: تاریخ، شماره، انبار مبدأ، انبار مقصد، مرکز هزینه (ForeignKey)
- خطوط: کالا، مقدار، قیمت، مبلغ

متغیرهای انتخاب شده:
- `source_warehouse` ← فیلد "انبار مبدأ" از هدر
- `cost_center` ← فیلد "مرکز هزینه" از هدر
- `issue_total` ← مجموع فیلد "مبلغ" از تمام خطوط
- `item_count` ← تعداد خطوط (برای استفاده در توضیحات)

#### 3.8 شناسایی فیلدهای قابل استخراج

برای هر نوع سند، باید یک registry یا configuration وجود داشته باشد که فیلدهای قابل استخراج را مشخص کند:

```python
# مثال ساختار برای ثبت فیلدهای قابل استخراج
DOCUMENT_EXTRACTABLE_FIELDS = {
    'sales.Invoice': {
        'header_fields': {
            'date': {
                'field_type': 'date',
                'label': 'تاریخ فاکتور',
                'data_type': 'date',
                'extractable': True
            },
            'number': {
                'field_type': 'string',
                'label': 'شماره فاکتور',
                'data_type': 'string',
                'extractable': True
            },
            'customer': {
                'field_type': 'foreign_key',
                'model': 'accounting.TafsiliAccount',
                'label': 'مشتری',
                'data_type': 'foreign_key',
                'extractable': True,
                'related_fields': {
                    'name': {'label': 'نام مشتری', 'data_type': 'string'},
                    'code': {'label': 'کد مشتری', 'data_type': 'string'},
                    'tafsili': {'label': 'تفصیلی مشتری', 'data_type': 'foreign_key'}
                }
            },
            'total_amount': {
                'field_type': 'number',
                'label': 'مبلغ کل فاکتور',
                'data_type': 'number',
                'extractable': True
            }
        },
        'line_fields': {
            'item': {
                'field_type': 'foreign_key',
                'model': 'inventory.Item',
                'label': 'کالا',
                'data_type': 'foreign_key',
                'extractable': True,
                'related_fields': {
                    'name': {'label': 'نام کالا', 'data_type': 'string'},
                    'code': {'label': 'کد کالا', 'data_type': 'string'}
                },
                'aggregatable': False
            },
            'quantity': {
                'field_type': 'number',
                'label': 'مقدار',
                'data_type': 'number',
                'extractable': True,
                'aggregatable': True,
                'aggregation_types': ['sum', 'count', 'avg']
            },
            'price': {
                'field_type': 'number',
                'label': 'قیمت',
                'data_type': 'number',
                'extractable': True,
                'aggregatable': True,
                'aggregation_types': ['sum', 'avg', 'max', 'min']
            },
            'amount': {
                'field_type': 'number',
                'label': 'مبلغ',
                'data_type': 'number',
                'extractable': True,
                'aggregatable': True,
                'aggregation_types': ['sum', 'avg', 'max', 'min']
            }
        }
    },
    'inventory.Receipt': {
        'header_fields': {
            'date': {'field_type': 'date', 'label': 'تاریخ رسید', 'extractable': True},
            'supplier': {
                'field_type': 'foreign_key',
                'model': 'inventory.Supplier',
                'label': 'تامین‌کننده',
                'extractable': True,
                'related_fields': {
                    'name': {'label': 'نام تامین‌کننده'},
                    'code': {'label': 'کد تامین‌کننده'}
                }
            },
            'warehouse': {
                'field_type': 'foreign_key',
                'model': 'inventory.Warehouse',
                'label': 'انبار',
                'extractable': True
            }
        },
        'line_fields': {
            'item': {
                'field_type': 'foreign_key',
                'model': 'inventory.Item',
                'label': 'کالا',
                'extractable': True,
                'related_fields': {
                    'name': {'label': 'نام کالا'}
                }
            },
            'quantity': {'field_type': 'number', 'label': 'مقدار', 'extractable': True, 'aggregatable': True},
            'amount': {'field_type': 'number', 'label': 'مبلغ', 'extractable': True, 'aggregatable': True}
        }
    }
}
```

**نکات مهم:**
- این ساختار باید به صورت داینامیک از مدل Django استخراج شود
- یا به صورت دستی در یک فایل configuration تعریف شود
- در UI به صورت درختی یا جدولی نمایش داده شود
- فیلدهای ForeignKey باید امکان استخراج فیلدهای مرتبط را داشته باشند
- فیلدهای خطوط باید امکان aggregation داشته باشند

---

### مرحله 4 به بعد: ایجاد اسناد زنجیره‌ای (Document Chain)

در این مرحله، کاربر می‌تواند به صورت مرحله‌ای سندهای جدید را تعریف کند که به صورت خودکار ایجاد شوند. هر سند می‌تواند از متغیرهای تعریف شده در مرحله 3 استفاده کند.

#### 4.1 ساختار کلی

هر فرایند می‌تواند شامل چندین سند باشد که به ترتیب ایجاد می‌شوند. هر سند شامل:

1. **اطلاعات کلی سند:**
   - نوع سند (مثلاً سند حسابداری، سند هزینه انبار، دریافت خزانه)
   - شماره مرحله (ترتیب اجرا)
   - شرط اجرا (اختیاری)
   - نیاز به تایید (اختیاری)

2. **فیلدهای هدر سند:**
   - تاریخ، شماره، توضیحات و سایر فیلدهای هدر
   - می‌توانند از متغیرها استفاده کنند یا استاتیک باشند

3. **خطوط سند:**
   - هر خط شامل حساب بدهکار، حساب بستانکار، مبلغ، تفصیلی و سایر فیلدها
   - می‌توانند از متغیرها استفاده کنند یا استاتیک باشند

#### 4.2 استفاده از متغیرها

در تمام بخش‌های سند می‌توان از متغیرهای تعریف شده در مرحله 3 استفاده کرد:

**نحوه استفاده:**
- `{variable: variable_name}` - استفاده از متغیر
- `{variable: variable_name | default: "مقدار پیش‌فرض"}` - استفاده با مقدار پیش‌فرض
- `"متن استاتیک {variable: variable_name}"` - ترکیب متن و متغیر

**مثال:**
```
توضیحات: "سند خودکار برای فاکتور {variable: invoice_number} - مشتری: {variable: customer_name}"
مبلغ: {variable: invoice_total}
تفصیلی: {variable: customer_tafsili}
```

#### 4.3 شرط اجرا (Execution Condition)

هر سند می‌تواند یک شرط اجرا داشته باشد. اگر شرط برقرار نباشد، آن سند ایجاد نمی‌شود:

**انواع شرط:**
- شرط بر اساس متغیر: `{variable: payment_method} == "نقدی"`
- شرط بر اساس مقدار: `{variable: invoice_total} > 1000000`
- شرط ترکیبی: `{variable: payment_method} == "نقدی" AND {variable: invoice_total} > 500000`

**مثال:**
```
سند 2: سند دریافت وجه
شرط اجرا: {variable: payment_method} == "نقدی"
→ فقط اگر روش پرداخت نقدی باشد، این سند ایجاد می‌شود
```

#### 4.4 تاییدیه بین اسناد (Approval Chain)

می‌توان تعیین کرد که یک سند باید تایید شود تا سند بعدی ایجاد شود:

**انواع تاییدیه:**
1. **تایید خودکار:** سند به صورت خودکار تایید می‌شود و سند بعدی بلافاصله ایجاد می‌شود
2. **تایید دستی:** سند ایجاد می‌شود اما باید توسط کاربر تایید شود تا سند بعدی ایجاد شود
3. **بدون تایید:** سند ایجاد می‌شود و سند بعدی بلافاصله ایجاد می‌شود (بدون نیاز به تایید)

**مثال:**
```
سند 1: سند حسابداری فروش
  → نیاز به تایید: دستی
  → بعد از تایید: سند 2 ایجاد می‌شود

سند 2: سند دریافت وجه
  → نیاز به تایید: خودکار
  → بلافاصله ایجاد می‌شود
```

#### 4.5 ساختار فیلدهای هدر

فیلدهای هدر هر سند می‌توانند:

1. **استاتیک باشند:**
   - مقدار ثابت (مثلاً حساب خاصی)
   - مثال: `حساب بدهکار: حساب بانک (استاتیک)`

2. **از متغیر استفاده کنند:**
   - استفاده مستقیم از متغیر
   - مثال: `تاریخ: {variable: invoice_date}`

3. **محاسباتی باشند:**
   - ترکیب چند متغیر یا محاسبه
   - مثال: `توضیحات: "فاکتور {variable: invoice_number} - مبلغ: {variable: invoice_total}"`

#### 4.6 ساختار خطوط سند

هر سند می‌تواند شامل یک یا چند خط باشد. هر خط شامل:

**فیلدهای اصلی:**
- **حساب بدهکار:** می‌تواند استاتیک باشد یا از متغیر استفاده کند
- **حساب بستانکار:** می‌تواند استاتیک باشد یا از متغیر استفاده کند
- **مبلغ:** معمولاً از متغیر استفاده می‌کند
- **تفصیلی:** می‌تواند از متغیر استفاده کند (مثلاً تفصیلی مشتری)
- **مرکز هزینه:** می‌تواند از متغیر استفاده کند
- **توضیحات:** می‌تواند ترکیبی از متن و متغیر باشد

**مثال ساختار خط:**
```
خط 1:
  - حساب بدهکار: {variable: sales_person_tafsili} (از متغیر)
  - حساب بستانکار: {variable: customer_tafsili} (از متغیر)
  - مبلغ: {variable: invoice_total} (از متغیر)
  - تفصیلی بدهکار: {variable: sales_person_tafsili}
  - تفصیلی بستانکار: {variable: customer_tafsili}
  - توضیحات: "فروش کالا - فاکتور {variable: invoice_number}"
```

#### 4.7 ترتیب اجرا

اسناد به ترتیب `step_number` اجرا می‌شوند:

1. سند 1 ایجاد می‌شود
2. اگر نیاز به تایید دارد، منتظر تایید می‌ماند
3. بعد از تایید (یا اگر تایید خودکار است)، شرط اجرای سند 2 بررسی می‌شود
4. اگر شرط برقرار بود، سند 2 ایجاد می‌شود
5. این روند ادامه می‌یابد تا تمام اسناد ایجاد شوند

#### 4.8 مثال‌های کاربردی

**مثال 1: فاکتور فروش → سند حسابداری فروش**

**متغیرها:**
- `customer_tafsili`: تفصیلی مشتری
- `invoice_total`: مبلغ کل فاکتور
- `invoice_date`: تاریخ فاکتور
- `invoice_number`: شماره فاکتور
- `sales_person`: کاربر صادرکننده فاکتور

**سند 1: سند حسابداری فروش**
```
نوع سند: سند حسابداری
شماره مرحله: 1
نیاز به تایید: خودکار

هدر:
  - تاریخ: {variable: invoice_date}
  - توضیحات: "سند خودکار فروش - فاکتور {variable: invoice_number}"

خط 1:
  - حساب بدهکار: تفصیلی {variable: sales_person} (نیروی فروش)
  - حساب بستانکار: تفصیلی {variable: customer_tafsili} (مشتری)
  - مبلغ: {variable: invoice_total}
  - توضیحات: "فروش کالا - فاکتور {variable: invoice_number}"
```

---

**مثال 2: رسید کالا → سند حسابداری خرید**

**متغیرها:**
- `supplier_tafsili`: تفصیلی تامین‌کننده
- `receipt_total`: مبلغ کل رسید
- `receipt_date`: تاریخ رسید
- `supplier_name`: نام تامین‌کننده

**سند 1: سند حسابداری خرید**
```
نوع سند: سند حسابداری
شماره مرحله: 1
نیاز به تایید: خودکار

هدر:
  - تاریخ: {variable: receipt_date}
  - توضیحات: "خرید کالا از {variable: supplier_name}"

خط 1:
  - حساب بدهکار: حساب موجودی کالا (استاتیک)
  - حساب بستانکار: تفصیلی {variable: supplier_tafsili}
  - مبلغ: {variable: receipt_total}
  - توضیحات: "خرید کالا - تاریخ {variable: receipt_date}"
```

---

**مثال 3: حواله دائم انبار → سند هزینه انبار**

**متغیرها:**
- `cost_center`: مرکز هزینه
- `issue_total`: مجموع مبلغ خطوط
- `source_warehouse`: انبار مبدأ
- `item_count`: تعداد اقلام

**سند 1: سند هزینه انبار**
```
نوع سند: سند هزینه انبار
شماره مرحله: 1
نیاز به تایید: خودکار

هدر:
  - تاریخ: {variable: issue_date}
  - مرکز هزینه: {variable: cost_center}
  - توضیحات: "حواله انبار - {variable: item_count} قلم کالا"

خط 1:
  - حساب بدهکار: حساب هزینه انبار (استاتیک)
  - حساب بستانکار: حساب موجودی کالا (استاتیک)
  - مبلغ: {variable: issue_total}
  - مرکز هزینه: {variable: cost_center}
```

---

**مثال 4: فاکتور فروش → سند حسابداری + سند دریافت وجه (زنجیره‌ای)**

**متغیرها:**
- `customer_tafsili`: تفصیلی مشتری
- `invoice_total`: مبلغ کل فاکتور
- `payment_method`: روش دریافت وجه
- `sales_person`: کاربر صادرکننده

**سند 1: سند حسابداری فروش**
```
نوع سند: سند حسابداری
شماره مرحله: 1
نیاز به تایید: دستی (باید تایید شود تا سند 2 ایجاد شود)

هدر:
  - تاریخ: {variable: invoice_date}
  - توضیحات: "فروش کالا - فاکتور {variable: invoice_number}"

خط 1:
  - حساب بدهکار: تفصیلی {variable: sales_person}
  - حساب بستانکار: تفصیلی {variable: customer_tafsili}
  - مبلغ: {variable: invoice_total}
```

**سند 2: سند دریافت وجه**
```
نوع سند: دریافت خزانه
شماره مرحله: 2
شرط اجرا: {variable: payment_method} == "نقدی"
نیاز به تایید: خودکار

هدر:
  - تاریخ: {variable: invoice_date}
  - حساب: حساب صندوق (استاتیک)
  - طرف حساب: تفصیلی {variable: customer_tafsili}
  - مبلغ: {variable: invoice_total}
  - توضیحات: "دریافت وجه فاکتور {variable: invoice_number}"
```

→ این سند فقط اگر `payment_method` برابر با "نقدی" باشد ایجاد می‌شود و فقط بعد از تایید سند 1 ایجاد می‌شود.

---

**مثال 5: حواله مصرف → سند هزینه + سند تخصیص مرکز هزینه**

**متغیرها:**
- `cost_center`: مرکز هزینه
- `consumption_total`: مجموع مبلغ مصرف
- `department`: بخش مصرف کننده

**سند 1: سند هزینه مصرف**
```
نوع سند: سند حسابداری
شماره مرحله: 1
نیاز به تایید: دستی

خط 1:
  - حساب بدهکار: حساب هزینه مصرف (استاتیک)
  - حساب بستانکار: حساب موجودی کالا (استاتیک)
  - مبلغ: {variable: consumption_total}
  - مرکز هزینه: {variable: cost_center}
```

**سند 2: سند تخصیص مرکز هزینه**
```
نوع سند: سند حسابداری
شماره مرحله: 2
نیاز به تایید: خودکار

خط 1:
  - حساب بدهکار: مرکز هزینه {variable: cost_center}
  - حساب بستانکار: حساب هزینه مصرف (استاتیک)
  - مبلغ: {variable: consumption_total}
```

→ سند 2 فقط بعد از تایید سند 1 ایجاد می‌شود.

---

**مثال 6: دریافت خزانه → سند حسابداری**

**متغیرها:**
- `treasury_account`: حساب نقدی/بانکی
- `amount`: مبلغ دریافت
- `party_tafsili`: تفصیلی طرف حساب
- `description`: توضیحات

**سند 1: سند حسابداری دریافت**
```
نوع سند: سند حسابداری
شماره مرحله: 1
نیاز به تایید: خودکار

خط 1:
  - حساب بدهکار: حساب {variable: treasury_account}
  - حساب بستانکار: تفصیلی {variable: party_tafsili}
  - مبلغ: {variable: amount}
  - توضیحات: {variable: description}
```

#### 4.9 UI پیشنهادی

**صفحه ایجاد/ویرایش سند:**

1. **بخش اطلاعات کلی:**
   - انتخاب نوع سند (dropdown)
   - شماره مرحله (auto-increment)
   - checkbox برای نیاز به تایید
   - فیلد شرط اجرا (اختیاری)

2. **بخش فیلدهای هدر:**
   - نمایش فیلدهای قابل تنظیم برای نوع سند انتخاب شده
   - امکان استفاده از متغیرها (dropdown متغیرهای موجود)
   - امکان وارد کردن مقدار استاتیک
   - امکان ترکیب متن و متغیر

3. **بخش خطوط سند:**
   - دکمه "افزودن خط جدید"
   - برای هر خط:
     - انتخاب حساب بدهکار (از متغیر یا استاتیک)
     - انتخاب حساب بستانکار (از متغیر یا استاتیک)
     - وارد کردن مبلغ (از متغیر یا استاتیک)
     - انتخاب تفصیلی (از متغیر یا استاتیک)
     - انتخاب مرکز هزینه (از متغیر یا استاتیک)
     - وارد کردن توضیحات (متن + متغیر)

4. **بخش پیش‌نمایش:**
   - نمایش پیش‌نمایش سند با استفاده از یک سند نمونه
   - نمایش مقادیر متغیرها

5. **قابلیت‌های اضافی:**
   - امکان drag & drop برای تغییر ترتیب خطوط
   - امکان کپی کردن خط
   - امکان حذف خط
   - امکان تست سند روی یک سند نمونه

---

## مدل‌های داده پیشنهادی

### 1. AutomationProcess (فرایند خودکار)

```python
class AutomationProcess:
    - id
    - name: نام فرایند
    - description: توضیحات
    - is_active: فعال/غیرفعال
    - trigger_module: ماژول سند مبدأ
    - trigger_document_type: نوع سند مبدأ
    - trigger_model: مدل Django مربوطه
    - company_id: شرکت
    - created_at, updated_at
    - created_by, updated_by
```

### 2. AutomationCondition (شرایط)

```python
class AutomationCondition:
    - id
    - process_id: فرایند مربوطه (ForeignKey)
    - filter_type: نوع فیلتر (global, document_specific) - CharField
    - filter_category: دسته فیلتر (user, user_group, date, date_range, status, document_field) - CharField
    - field_name: نام فیلد (برای فیلترهای document_specific) - CharField, nullable
    - field_type: نوع فیلد (string, number, date, foreign_key, many_to_many) - CharField
    - operator: عملگر (==, !=, >, <, >=, <=, in, not_in, contains, starts_with, ends_with, between, hierarchy_level, hierarchy_parent, hierarchy_descendant) - CharField
    - value: مقدار مقایسه (JSONField - می‌تواند single value یا array باشد)
    - value_type: نوع مقدار (static, variable, calculated) - CharField
    - logical_operator: AND/OR (برای ترکیب با شرط بعدی) - CharField, default='AND'
    - order: ترتیب شرط - IntegerField
    - is_active: فعال/غیرفعال - BooleanField, default=True
    - created_at, updated_at
    - created_by, updated_by
```

### 3. AutomationVariable (متغیرها)

```python
class AutomationVariable:
    - id
    - process_id: فرایند مربوطه (ForeignKey)
    - name: نام متغیر (برای استفاده در مراحل بعدی) - CharField, unique per process
    - display_name: نام نمایشی (فارسی) - CharField
    - source_type: نوع منبع (field, related_field, aggregated, computed) - CharField
    - field_path: مسیر فیلد (مثلاً "customer" یا "customer.name" یا "lines.amount") - CharField
    - field_type: نوع فیلد در سند (header_field, line_field, related_field) - CharField
    - aggregation_type: نوع تجمیع (sum, count, avg, max, min) - CharField, nullable
    - computation_expression: عبارت محاسباتی (برای computed) - TextField, nullable
    - data_type: نوع داده (string, number, date, boolean, foreign_key) - CharField
    - related_model: مدل مرتبط (اگر related_field باشد) - CharField, nullable
    - default_value: مقدار پیش‌فرض (اختیاری) - JSONField, nullable
    - description: توضیحات متغیر - TextField, nullable
    - order: ترتیب نمایش - IntegerField
    - is_active: فعال/غیرفعال - BooleanField, default=True
    - created_at, updated_at
    - created_by, updated_by
```

### 4. AutomationDocumentStep (مراحل ایجاد سند)

```python
class AutomationDocumentStep:
    - id
    - process_id: فرایند مربوطه (ForeignKey)
    - step_number: شماره مرحله (ترتیب اجرا) - IntegerField
    - document_type: نوع سند (accounting_document, warehouse_expense, treasury_receive, treasury_pay, ...) - CharField
    - document_template_id: الگوی سند (اختیاری) - ForeignKey, nullable
    - execution_condition: شرط اجرا (JSONField - شرطی که باید برقرار باشد تا این سند ایجاد شود) - JSONField, nullable
    - requires_approval: نیاز به تایید (auto, manual, none) - CharField, default='auto'
    - wait_for_previous_approval: منتظر تایید سند قبلی (BooleanField, default=False)
    - header_config: تنظیمات هدر (JSONField - شامل فیلدهای هدر با مقادیر استاتیک یا متغیر) - JSONField
    - is_active: فعال/غیرفعال - BooleanField, default=True
    - order: ترتیب نمایش - IntegerField
    - created_at, updated_at
    - created_by, updated_by
```

**ساختار header_config:**
```json
{
  "date": {
    "type": "variable",
    "value": "invoice_date"
  },
  "description": {
    "type": "computed",
    "value": "سند خودکار برای فاکتور {variable: invoice_number}"
  },
  "cost_center": {
    "type": "variable",
    "value": "cost_center"
  }
}
```

### 5. AutomationDocumentLine (خطوط سند)

```python
class AutomationDocumentLine:
    - id
    - step_id: مرحله مربوطه (ForeignKey)
    - line_number: شماره خط (ترتیب در سند) - IntegerField
    - debit_account_type: نوع حساب بدهکار (static, variable) - CharField
    - debit_account_id: شناسه حساب بدهکار (اگر استاتیک باشد) - ForeignKey, nullable
    - debit_account_variable: نام متغیر حساب بدهکار (اگر از متغیر باشد) - CharField, nullable
    - debit_tafsili_type: نوع تفصیلی بدهکار (static, variable, none) - CharField, default='none'
    - debit_tafsili_id: شناسه تفصیلی بدهکار (اگر استاتیک باشد) - ForeignKey, nullable
    - debit_tafsili_variable: نام متغیر تفصیلی بدهکار (اگر از متغیر باشد) - CharField, nullable
    - credit_account_type: نوع حساب بستانکار (static, variable) - CharField
    - credit_account_id: شناسه حساب بستانکار (اگر استاتیک باشد) - ForeignKey, nullable
    - credit_account_variable: نام متغیر حساب بستانکار (اگر از متغیر باشد) - CharField, nullable
    - credit_tafsili_type: نوع تفصیلی بستانکار (static, variable, none) - CharField, default='none'
    - credit_tafsili_id: شناسه تفصیلی بستانکار (اگر استاتیک باشد) - ForeignKey, nullable
    - credit_tafsili_variable: نام متغیر تفصیلی بستانکار (اگر از متغیر باشد) - CharField, nullable
    - amount_type: نوع مبلغ (static, variable, computed) - CharField
    - amount_value: مقدار مبلغ (اگر استاتیک باشد) - DecimalField, nullable
    - amount_variable: نام متغیر مبلغ (اگر از متغیر باشد) - CharField, nullable
    - amount_expression: عبارت محاسباتی مبلغ (اگر computed باشد) - TextField, nullable
    - cost_center_type: نوع مرکز هزینه (static, variable, none) - CharField, default='none'
    - cost_center_id: شناسه مرکز هزینه (اگر استاتیک باشد) - ForeignKey, nullable
    - cost_center_variable: نام متغیر مرکز هزینه (اگر از متغیر باشد) - CharField, nullable
    - description_type: نوع توضیحات (static, computed) - CharField
    - description_value: مقدار توضیحات (اگر استاتیک باشد) - TextField, nullable
    - description_expression: عبارت توضیحات (اگر computed باشد - می‌تواند شامل متغیرها باشد) - TextField, nullable
    - execution_condition: شرط اجرای این خط (اختیاری - اگر شرط برقرار نبود این خط ایجاد نمی‌شود) - JSONField, nullable
    - is_active: فعال/غیرفعال - BooleanField, default=True
    - order: ترتیب نمایش - IntegerField
    - created_at, updated_at
    - created_by, updated_by
```

**مثال ساختار execution_condition برای خط:**
```json
{
  "operator": "AND",
  "conditions": [
    {
      "variable": "payment_method",
      "operator": "==",
      "value": "نقدی"
    },
    {
      "variable": "invoice_total",
      "operator": ">",
      "value": 1000000
    }
  ]
}
```

### 6. AutomationExecutionLog (لاگ اجرا)

```python
class AutomationExecutionLog:
    - id
    - process_id: فرایند مربوطه (ForeignKey)
    - trigger_document_id: شناسه سند مبدأ - IntegerField
    - trigger_document_type: نوع سند مبدأ - CharField
    - status: وضعیت کلی (pending, in_progress, success, failed, partial, cancelled) - CharField
    - executed_at: زمان شروع اجرا - DateTimeField
    - completed_at: زمان پایان اجرا - DateTimeField, nullable
    - error_message: پیام خطا (در صورت وجود) - TextField, nullable
    - execution_data: داده‌های اجرا شامل متغیرهای استخراج شده (JSONField)
    - created_documents: لیست اسناد ایجاد شده (JSONField)
    - approval_status: وضعیت تاییدیه (pending, approved, rejected) - CharField, nullable
    - approved_by: کاربر تاییدکننده - ForeignKey, nullable
    - approved_at: زمان تایید - DateTimeField, nullable
    - company_id: شرکت - ForeignKey
    - created_at, updated_at
    - created_by, updated_by
```

**ساختار created_documents:**
```json
[
  {
    "step_id": 1,
    "step_number": 1,
    "document_type": "accounting_document",
    "document_id": 123,
    "status": "created",
    "requires_approval": "manual",
    "approval_status": "pending",
    "created_at": "2025-01-15T10:30:00Z"
  },
  {
    "step_id": 2,
    "step_number": 2,
    "document_type": "treasury_receive",
    "document_id": 124,
    "status": "pending",
    "waiting_for_previous_approval": true,
    "created_at": null
  }
]
```

**ساختار execution_data:**
```json
{
  "variables": {
    "customer_tafsili": 45,
    "invoice_total": 1000000,
    "invoice_date": "2025-01-15",
    "invoice_number": "INV-001"
  },
  "conditions_evaluated": {
    "condition_1": true,
    "condition_2": true
  }
}
```

### 7. AutomationDocumentApproval (تاییدیه اسناد)

```python
class AutomationDocumentApproval:
    - id
    - execution_log_id: لاگ اجرا مربوطه (ForeignKey)
    - step_id: مرحله مربوطه (ForeignKey)
    - document_id: شناسه سند ایجاد شده - IntegerField
    - document_type: نوع سند - CharField
    - status: وضعیت تایید (pending, approved, rejected) - CharField, default='pending'
    - approved_by: کاربر تاییدکننده - ForeignKey, nullable
    - approved_at: زمان تایید - DateTimeField, nullable
    - rejection_reason: دلیل رد (در صورت رد) - TextField, nullable
    - created_at, updated_at
```

---

## فلوچارت اجرای فرایند

```
1. رویداد رخ می‌دهد (مثلاً ثبت فاکتور فروش)
   ↓
2. بررسی فرایندهای فعال که trigger آنها این نوع سند است
   ↓
3. برای هر فرایند:
   ↓
4. بررسی شرایط (Conditions)
   ↓
5. اگر شرایط برقرار بود:
   ↓
6. استخراج متغیرها از سند مبدأ
   ↓
7. ایجاد لاگ اجرا (status: in_progress)
   ↓
8. اجرای مراحل ایجاد سند (Document Steps) به ترتیب step_number:
   ↓
   برای هر مرحله:
   ├─ بررسی شرط اجرای مرحله (execution_condition)
   │  ↓
   ├─ اگر شرط برقرار بود:
   │  ↓
   ├─ بررسی نیاز به تایید سند قبلی (wait_for_previous_approval)
   │  ↓
   ├─ اگر نیاز به تایید بود:
   │  ├─ بررسی وضعیت تایید سند قبلی
   │  ├─ اگر تایید نشده: منتظر بمان (status: pending)
   │  └─ اگر تایید شد: ادامه
   │  ↓
   ├─ ایجاد سند با استفاده از متغیرها و مقادیر استاتیک
   │  ├─ تنظیم فیلدهای هدر (header_config)
   │  └─ ایجاد خطوط سند (Document Lines)
   │     ├─ برای هر خط:
   │     ├─ بررسی شرط اجرای خط (execution_condition)
   │     ├─ اگر شرط برقرار بود:
   │     ├─ محاسبه مقادیر (از متغیر یا استاتیک)
   │     └─ ایجاد خط سند
   │  ↓
   ├─ بررسی نیاز به تایید (requires_approval)
   │  ├─ اگر auto: سند به صورت خودکار تایید می‌شود
   │  ├─ اگر manual: سند ایجاد می‌شود و منتظر تایید می‌ماند
   │  └─ اگر none: سند ایجاد می‌شود بدون نیاز به تایید
   │  ↓
   └─ ثبت اطلاعات سند در لاگ اجرا
   ↓
9. به‌روزرسانی وضعیت لاگ اجرا:
   ├─ اگر همه اسناد ایجاد شدند: status = success
   ├─ اگر بعضی اسناد ایجاد نشدند: status = partial
   └─ اگر خطا رخ داد: status = failed
   ↓
10. پایان
```

**فلوچارت تاییدیه:**

```
1. کاربر به صفحه تاییدیه اسناد می‌رود
   ↓
2. نمایش لیست اسناد در انتظار تایید
   ↓
3. کاربر سند را بررسی می‌کند
   ↓
4. کاربر تصمیم می‌گیرد:
   ├─ تایید (Approved)
   │  ↓
   │  ├─ ثبت تایید در AutomationDocumentApproval
   │  ├─ به‌روزرسانی وضعیت سند
   │  └─ بررسی سند بعدی در زنجیره
   │     ├─ اگر wait_for_previous_approval = True
   │     └─ ایجاد سند بعدی
   │
   └─ رد (Rejected)
      ↓
      ├─ ثبت رد در AutomationDocumentApproval
      ├─ ثبت دلیل رد
      └─ توقف ایجاد اسناد بعدی
```

---

## نکات مهم طراحی

### 1. ترتیب اجرا
- مراحل باید به ترتیب step_number اجرا شوند
- اگر یک مرحله خطا دهد، می‌توان ادامه داد یا متوقف کرد (قابل تنظیم)

### 2. مدیریت خطا
- باید لاگ کامل از اجرا نگه داشته شود
- در صورت خطا، باید امکان بازگشت (rollback) وجود داشته باشد
- باید امکان اجرای مجدد (retry) وجود داشته باشد

### 3. کارایی
- فرایندها باید به صورت async اجرا شوند
- باید از cache برای بهبود کارایی استفاده شود
- باید از queue برای مدیریت ترافیک استفاده شود

### 4. امنیت
- هر فرایند باید به شرکت خاصی تعلق داشته باشد
- باید permission check برای ایجاد اسناد انجام شود
- باید validation کامل روی داده‌ها انجام شود

### 5. انعطاف‌پذیری
- باید امکان استفاده از expression در محاسبات وجود داشته باشد
- باید امکان استفاده از template در توضیحات وجود داشته باشد
- باید امکان شرطی کردن خطوط و مراحل وجود داشته باشد

---

## مراحل پیاده‌سازی پیشنهادی

### فاز 1: ساختار پایه
- [ ] مدل‌های داده
- [ ] فرم‌های ایجاد/ویرایش فرایند
- [ ] View های CRUD پایه

### فاز 2: انتخاب سند مبدأ
- [ ] لیست اسناد قابل انتخاب
- [ ] انتخاب سند و ذخیره

### فاز 3: تعریف شرایط
- [ ] UI برای تعریف شرایط
- [ ] اعتبارسنجی شرایط
- [ ] تست شرایط

### فاز 4: استخراج متغیرها
- [ ] UI برای انتخاب متغیرها
- [ ] نمایش پیش‌نمایش متغیرها
- [ ] تست استخراج

### فاز 5: ایجاد اسناد
- [ ] UI برای تعریف مراحل
- [ ] UI برای تعریف خطوط
- [ ] پیش‌نمایش سند ایجاد شده

### فاز 6: موتور اجرا
- [ ] Signal handler برای رویدادها
- [ ] موتور اجرای فرایند
- [ ] مدیریت خطا و rollback

### فاز 7: لاگ و مانیتورینگ
- [ ] ثبت لاگ اجرا
- [ ] نمایش تاریخچه اجرا
- [ ] گزارش‌گیری

---

## سوالات و نکات برای بررسی

1. آیا باید امکان ویرایش فرایندهای فعال وجود داشته باشد؟
2. آیا باید versioning برای فرایندها وجود داشته باشد؟
3. آیا باید امکان تست فرایند روی یک سند خاص وجود داشته باشد؟
4. آیا باید امکان schedule کردن اجرای فرایند وجود داشته باشد؟
5. آیا باید امکان pause/resume فرایند وجود داشته باشد؟
6. آیا باید امکان duplicate کردن فرایند وجود داشته باشد؟
7. آیا باید template برای فرایندهای رایج وجود داشته باشد؟

---

## مثال‌های کاربردی

### مثال 1: خودکارسازی سند حسابداری برای فاکتور فروش

**Trigger:** فاکتور فروش قطعی می‌شود

**Conditions:**
1. **فیلتر عمومی - تاریخ:** بازه تاریخی (از 1403/01/01 تا 1403/12/29)
2. **فیلتر عمومی - کاربر:** اسناد ایجاد شده توسط کاربران عضو گروه "فروش"
3. **فیلتر خاص سند - تفصیلی مشتری:** تفصیلی مشتری در سطح 2 از سلسله مراتب تفصیلی "مشتریان" باشد
4. **فیلتر خاص سند - مبلغ:** مبلغ فاکتور بیشتر از 1,000,000 تومان

**Variables:**
- `invoice_total`: مبلغ کل فاکتور
- `customer_tafsili`: تفصیلی مشتری
- `invoice_date`: تاریخ فاکتور
- `invoice_number`: شماره فاکتور

**Document Step 1:**
- سند حسابداری
- خط 1:
  - بدهکار: حساب بانک
  - بستانکار: حساب درآمد فروش
  - مبلغ: `{invoice_total}`
  - تفصیلی: `{customer_tafsili}`

---

### مثال 2: خودکارسازی سند هزینه انبار

**Trigger:** حواله دائم انبار قطعی می‌شود

**Conditions:**
1. **فیلتر عمومی - تاریخ:** بازه تاریخی (ماه جاری)
2. **فیلتر خاص سند - انبار مبدأ:** انبار مبدأ برابر با "انبار اصلی" باشد
3. **فیلتر خاص سند - مرکز هزینه:** مرکز هزینه موجود باشد

**Variables:**
- `issue_total`: مجموع مبلغ خطوط حواله
- `cost_center`: مرکز هزینه
- `warehouse`: انبار مبدأ
- `issue_date`: تاریخ حواله

**Document Step 1:**
- سند هزینه انبار
- خط 1:
  - بدهکار: حساب هزینه انبار
  - بستانکار: حساب موجودی کالا
  - مبلغ: `{issue_total}`
  - مرکز هزینه: `{cost_center}`

---

### مثال 3: خودکارسازی سند حسابداری برای رسید کالا

**Trigger:** رسید دائم کالا قطعی می‌شود

**Conditions:**
1. **فیلتر عمومی - کاربر:** اسناد ایجاد شده توسط کاربر خاص (ID: 5)
2. **فیلتر خاص سند - تامین‌کننده:** تامین‌کننده در لیست [تامین‌کننده A, تامین‌کننده B] باشد
3. **فیلتر خاص سند - نوع رسید:** نوع رسید برابر با "دائم" باشد

**Variables:**
- `receipt_total`: مجموع مبلغ خطوط رسید
- `supplier`: تامین‌کننده
- `warehouse`: انبار مقصد
- `receipt_date`: تاریخ رسید

**Document Step 1:**
- سند حسابداری
- خط 1:
  - بدهکار: حساب موجودی کالا
  - بستانکار: حساب بستانکار تامین‌کننده
  - مبلغ: `{receipt_total}`
  - تفصیلی: تفصیلی تامین‌کننده از `{supplier}`

---

**تاریخ ایجاد:** 2025  
**وضعیت:** در حال طراحی  
**نسخه:** 0.1

