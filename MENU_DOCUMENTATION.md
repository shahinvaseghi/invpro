# مستندات منوهای سیستم

این فایل شامل لیست کامل موارد منوی بالای صفحه و منوی کناری و صفحاتی که هر کدام باز می‌کنند می‌باشد.

## منوی بالای صفحه (Top Menu)

### 1. Dashboard
- **صفحه**: `ui:dashboard`
- **توضیحات**: صفحه اصلی داشبورد سیستم

### 2. ماژول‌ها (Modules)
این منو شامل تمام ماژول‌های سیستم می‌باشد که در یک منوی بزرگ (Mega Menu) نمایش داده می‌شوند:

#### 2.1. Shared (اشتراکی)
- **Companies**: `shared:companies` - مدیریت شرکت‌ها
- **Company Units**: `shared:company_units` - مدیریت واحدهای شرکت
- **SMTP Servers**: `shared:smtp_servers` - مدیریت سرورهای SMTP
- **Users** (زیرمنو):
  - **Users**: `shared:users` - مدیریت کاربران
  - **Groups**: `shared:groups` - مدیریت گروه‌ها
  - **Access Levels**: `shared:access_levels` - مدیریت سطوح دسترسی
- **Django Admin**: `admin_panel` - پنل مدیریت Django

#### 2.2. Inventory (انبار)
- **Items** (زیرمنو):
  - **Edit Items**: `inventory:items` - ویرایش کالاها
  - **Item Serials**: `inventory:item_serials` - سریال‌های کالا
  - **Inventory Balance**: `inventory:inventory_balance` - موجودی انبار
- **Warehouses**: `inventory:warehouses` - مدیریت انبارها
- **Suppliers** (زیرمنو):
  - **Supplier Categories**: `inventory:supplier_categories` - دسته‌بندی تامین‌کنندگان
  - **Supplier List**: `inventory:suppliers` - لیست تامین‌کنندگان
- **Receipts** (زیرمنو):
  - **Temporary Receipts**: `inventory:receipt_temporary` - رسیدهای موقت
  - **Permanent Receipts**: `inventory:receipt_permanent` - رسیدهای دائم
  - **Consignment Receipts**: `inventory:receipt_consignment` - رسیدهای امانی
- **Issues** (زیرمنو):
  - **Permanent Issues**: `inventory:issue_permanent` - حواله‌های دائم
  - **Consumption Issues**: `inventory:issue_consumption` - حواله‌های مصرف
  - **Consignment Issues**: `inventory:issue_consignment` - حواله‌های امانی
  - **حواله انتقال بین انبارها**: `inventory:issue_warehouse_transfer` - انتقال بین انبارها
- **Stocktaking** (زیرمنو):
  - **Deficit Records**: `inventory:stocktaking_deficit` - ثبت کسری
  - **Surplus Records**: `inventory:stocktaking_surplus` - ثبت اضافه
  - **Stocktaking Records**: `inventory:stocktaking_records` - سوابق انبارگردانی

#### 2.3. Production (تولید)
- **Personnel**: `production:personnel` - پرسنل تولید
- **Machines**: `production:machines` - ماشین‌آلات
- **Work Lines**: `production:work_lines` - خطوط تولید
- **BOM**: `production:bom_list` - لیست مواد اولیه
- **Processes**: `production:processes` - فرآیندها
- **Product Orders**: `production:product_orders` - سفارشات تولید
- **Transfer to Line Requests**: `production:transfer_requests` - درخواست‌های انتقال به خط
- **Performance Records**: `production:performance_records` - سوابق عملکرد
- **QC Operations**: `production:qc_operations` - عملیات کنترل کیفیت
- **Rework**: `production:rework_document_list` - بازکاری
- **شناسایی و ردیابی**: `production:tracking_identification` - ردیابی و شناسایی

#### 2.4. Quality Control (کنترل کیفیت)
- **Inspections**: `qc:temporary_receipts` - بازرسی‌ها
- **Serial Assignment**: `qc:serial_assignment_list` - تخصیص سریال
- **Batch Assignment**: `qc:batch_assignment_list` - تخصیص بچ

#### 2.5. Ticketing (تیکتینگ)
- **Create Ticket**: `ticketing:ticket_create` - ایجاد تیکت
- **Respond to Ticket**: `ticketing:ticket_respond` - پاسخ به تیکت
- **Templates**: `ticketing:templates` - قالب‌ها
- **Categories**: `ticketing:categories` - دسته‌بندی‌ها
- **Subcategories**: `ticketing:subcategories` - زیردسته‌بندی‌ها
- **Auto Response**: `ticketing:auto_response` - پاسخ خودکار

#### 2.6. Accounting (حسابداری)
- **تعاریف پایه** (زیرمنو):
  - **سال مالی**: `accounting:fiscal_years` - مدیریت سال مالی
  - **چارت حساب‌ها**: `accounting:accounts` - چارت حساب‌ها
  - **تعریف حساب کل**: `accounting:gl_accounts` - حساب کل
  - **تعریف حساب معین**: `accounting:sub_accounts` - حساب معین
  - **تعریف حساب تفصیلی**: `accounting:tafsili_accounts` - حساب تفصیلی
  - **اتصال سلسله مراتبی تفصیلی**: `accounting:hierarchical_tafsili_connection` - اتصال سلسله مراتبی تفصیلی
  - **انواع تفصیلی**: `accounting:tafsili_types` - انواع تفصیلی
  - **مراکز هزینه**: `accounting:cost_centers` - مراکز هزینه
  - **دسته‌بندی درآمد و هزینه**: `accounting:income_expense_categories` - دسته‌بندی درآمد و هزینه
  - **طرف حساب‌ها**: `accounting:parties` - طرف حساب‌ها
  - **حساب‌های نقدی و بانکی**: `accounting:treasury_accounts` - حساب‌های نقدی و بانکی
- **اسناد حسابداری** (زیرمنو):
  - **ثبت سند حسابداری**: `accounting:document_create` - ثبت سند
  - **لیست اسناد حسابداری**: `accounting:document_list` - لیست اسناد
  - **سندهای باز، قطعی، برگشتی**: `accounting:document_status` - وضعیت اسناد
  - **گردش حساب**: `accounting:report_account_movements` - گردش حساب
  - **گردش تفصیلی**: `accounting:tafsili_movements` - گردش تفصیلی
  - **تراز آزمایشی**: `accounting:report_trial_balance` - تراز آزمایشی
  - **ترازنامه**: `accounting:report_balance_sheet` - ترازنامه
  - **صورت سود و زیان**: `accounting:report_income_statement` - صورت سود و زیان
- **خزانه‌داری** (زیرمنو):
  - **دریافت**: `accounting:treasury_receive` - دریافت
  - **پرداخت**: `accounting:treasury_pay` - پرداخت
  - **تراکنش‌های خزانه**: `accounting:treasury_transactions` - تراکنش‌ها
  - **انتقال بین حساب‌ها**: `accounting:treasury_transfer` - انتقال
  - **حساب‌های نقدی و بانکی**: `accounting:treasury_accounts` - حساب‌های نقدی و بانکی
  - **مدیریت چک‌ها**: `accounting:treasury_checks` - مدیریت چک
  - **تطبیق بانکی**: `accounting:treasury_reconciliation` - تطبیق بانکی
  - **گزارش وجوه نقد و بانک‌ها**: `accounting:treasury_cash_report` - گزارش نقد و بانک
  - **درخواست‌های پرداخت**: `accounting:payment_requests` - درخواست‌های پرداخت
  - **تخصیص مرکز هزینه**: `accounting:cost_allocation` - تخصیص مرکز هزینه
  - **گزارش درآمد**: `accounting:income_report` - گزارش درآمد
  - **گزارش هزینه**: `accounting:expense_report` - گزارش هزینه
  - **گزارش مراکز هزینه**: `accounting:cost_center_report` - گزارش مراکز هزینه
- **طرف حساب‌ها** (زیرمنو):
  - **لیست طرف حساب‌ها**: `accounting:parties` - لیست طرف حساب
  - **گردش طرف حساب**: `accounting:party_movements` - گردش طرف حساب
  - **گزارش مانده طرف حساب‌ها**: `accounting:party_balance_report` - گزارش مانده
- **حقوق و دستمزد** (زیرمنو):
  - **پرداخت حقوق و دستمزد**: `accounting:payroll_payment` - پرداخت حقوق
  - **تنظیمات بیمه و مالیات**: `accounting:payroll_insurance_tax` - تنظیمات بیمه و مالیات
  - **بارگذاری اسناد حقوق و دستمزد**: `accounting:payroll_document` - بارگذاری اسناد
  - **خروجی حقوق و دستمزد برای بانک**: `accounting:payroll_bank_transfer` - خروجی بانک
- **مالیات و مقررات** (زیرمنو):
  - **مدیریت VAT**: `accounting:tax_vat` - مدیریت VAT
  - **تنظیمات سامانه مودیان**: `accounting:tax_moadian_settings` - تنظیمات مودیان
  - **گزارش VAT**: `accounting:report_vat` - گزارش VAT
  - **گزارش فصلی (TTMS / ماده 169)**: `accounting:tax_seasonal` - گزارش فصلی
  - **اعتبارسنجی اسناد برای ارسال به سامانه مودیان**: `accounting:tax_validation` - اعتبارسنجی
  - **گزارش مغایرت مالیاتی**: `accounting:tax_discrepancy_report` - گزارش مغایرت
- **گزارشات مالی** (زیرمنو):
  - **تراز آزمایشی**: `accounting:report_trial_balance` - تراز آزمایشی
  - **ترازنامه**: `accounting:report_balance_sheet` - ترازنامه
  - **سود و زیان**: `accounting:report_income_statement` - سود و زیان
  - **جریان وجوه نقد**: `accounting:report_cash_flow` - جریان وجوه نقد
  - **گزارش حساب‌ها**: `accounting:report_account_movements` - گزارش حساب
  - **گزارش تفصیلی و مراکز هزینه**: `accounting:report_tafsili_cost_center` - گزارش تفصیلی
  - **گزارش چک‌ها**: `accounting:report_checks` - گزارش چک
  - **گزارش خزانه**: `accounting:report_treasury` - گزارش خزانه
  - **گزارش طرف حساب**: `accounting:report_party_statement` - گزارش طرف حساب
  - **گزارش VAT**: `accounting:report_vat` - گزارش VAT
  - **گزارش عملیات ماهانه**: `accounting:report_monthly` - گزارش ماهانه
  - **مرور حساب‌ها**: `accounting:report_account_browser` - مرور حساب‌ها
- **اسناد و فایل‌ها** (زیرمنو):
  - **بارگذاری اسناد**: `accounting:attachment_upload` - بارگذاری
  - **مدیریت اسناد پیوست**: `accounting:attachment_list` - مدیریت پیوست
  - **پیوست به سند**: `accounting:attachment_attach` - پیوست
- **خودکارسازی** (زیرمنو):
  - **فرایندهای خودکار**: `accounting:automation_processes` - فرایندهای خودکار
  - **لاگ اجرا**: `accounting:automation_execution_logs` - لاگ اجرا
- **ابزارها و عملیات تکمیلی** (زیرمنو):
  - **بستن حساب‌های موقت**: `accounting:close_temp_accounts` - بستن حساب موقت
  - **افتتاحیه خودکار**: `accounting:opening_entry` - افتتاحیه
  - **اختتامیه**: `accounting:closing_entry` - اختتامیه
  - **یکپارچه‌سازی اطلاعات**: `accounting:integration` - یکپارچه‌سازی
  - **پشتیبان‌گیری و بازیابی**: `accounting:backup_restore` - پشتیبان‌گیری
- **حسابداری انبار** (زیرمنو):
  - **سند هزینه انبار**: `accounting:warehouse_expense` - سند هزینه
  - **سند درآمد انبار**: `accounting:warehouse_income` - سند درآمد
  - **افتتاحیه و اختتامیه**: `accounting:warehouse_opening_closing` - افتتاحیه و اختتامیه
  - **تنظیمات حسابداری انبار**: `accounting:warehouse_settings` - تنظیمات
- **تنظیمات** (زیرمنو):
  - **تنظیمات حسابداری**: `accounting:settings` - تنظیمات حسابداری
  - **تنظیمات خزانه**: `accounting:settings_treasury` - تنظیمات خزانه
  - **تنظیمات مالیات**: `accounting:settings_tax` - تنظیمات مالیات

#### 2.7. Sales (فروش)
- **Dashboard**: `sales:dashboard` - داشبورد فروش
- **Item Price Cards**: `sales:price_card_list` - کارت‌های قیمت کالا
- **Sales Invoice**: `sales:invoice_create` - صدور فاکتور فروش
- **مشتریان**: `sales:customers` - مدیریت مشتریان
- **محل دریافت درآمد**: `sales:income_receipt_location_list` - محل دریافت درآمد
- **تنظیمات**: `sales:settings` - تنظیمات فروش

#### 2.8. Human Resources (منابع انسانی)
- **Dashboard**: `hr:dashboard` - داشبورد منابع انسانی
- **Personnel** (زیرمنو):
  - **Create Personnel**: `hr:personnel_create` - ایجاد پرسنل
  - **Assign Decree**: `hr:personnel_decree_assignment` - تخصیص حکم
  - **Personnel Form**: `hr:personnel_form_create` - فرم پرسنل
  - **Form Groups**: `hr:personnel_form_groups` - گروه‌های فرم
  - **Form Subgroups**: `hr:personnel_form_subgroups` - زیرگروه‌های فرم
- **حکم‌های حقوق و دستمزد** (زیرمنو):
  - **حکم‌ها**: `hr:payroll_decrees` - حکم‌های حقوق
  - **گروه‌بندی حکم‌ها**: `hr:payroll_decree_groups` - گروه‌بندی حکم
  - **زیر گروه‌بندی حکم‌ها**: `hr:payroll_decree_subgroups` - زیرگروه‌بندی حکم
- **Loans** (زیرمنو):
  - **Loan Management**: `hr:loans_management` - مدیریت وام
  - **Scheduling**: `hr:loans_scheduling` - زمان‌بندی وام
  - **Savings Fund**: `hr:loans_savings_fund` - صندوق پس‌انداز

#### 2.9. Requests (درخواست‌ها)
- **Purchase Request**: `inventory:purchase_requests` - درخواست خرید
- **Warehouse Request**: `inventory:warehouse_requests` - درخواست انبار
- **Service Request**: `procurement:service_requests` - درخواست خدمات
- **Transfer to Line Requests**: `production:transfer_requests` - درخواست انتقال به خط
- **Leave Request**: `hr:requests_leave` - درخواست مرخصی
- **Sick Leave Request**: `hr:requests_sick_leave` - درخواست مرخصی استعلاجی
- **Loan Request**: `hr:requests_loan` - درخواست وام

#### 2.10. Office Automation (اتوماسیون اداری)
- **Dashboard**: `office_automation:dashboard` - داشبورد اتوماسیون
- **Inbox** (زیرمنو):
  - **Incoming Letters**: `office_automation:inbox_incoming` - نامه‌های ورودی
  - **Write Letter**: `office_automation:inbox_write` - نوشتن نامه
  - **Fill Form**: `office_automation:inbox_fill_form` - پر کردن فرم
- **Processes** (زیرمنو):
  - **Process Engine**: `office_automation:processes_engine` - موتور فرآیند
  - **Process-Form Connection**: `office_automation:processes_form_connection` - اتصال فرآیند به فرم
- **Forms** (زیرمنو):
  - **Form Builder**: `office_automation:forms_builder` - سازنده فرم

#### 2.11. Transportation (حمل و نقل)
- **Dashboard**: `transportation:dashboard` - داشبورد حمل و نقل

#### 2.12. Procurement (تدارکات)
- **Dashboard**: `procurement:dashboard` - داشبورد تدارکات
- **Purchase** (زیرمنو):
  - **Purchase Orders**: `procurement:purchase_orders` - سفارشات خرید
  - **Purchase Invoices**: `procurement:purchase_invoices` - فاکتورهای خرید
- **Services** (زیرمنو):
  - **Service Requests**: `procurement:service_requests` - درخواست‌های خدمات
  - **Service Invoices**: `procurement:service_invoices` - فاکتورهای خدمات
- **Buyers** (زیرمنو):
  - **Buyers List**: `procurement:buyers` - لیست خریداران
  - **Create Buyer**: `procurement:buyer_create` - ایجاد خریدار
  - **Buyer Assignment**: `procurement:buyer_assignment` - تخصیص خریدار

### 3. منوی بالای صفحه - سمت راست (Top Nav)
- **Notifications**: نمایش اعلان‌ها
- **Company Selector**: انتخاب شرکت فعال
- **Fiscal Year Selector**: انتخاب سال مالی فعال
- **User Info**: اطلاعات کاربر و دکمه خروج (`logout`)

---

## منوی کناری (Sidebar Menu)

### 1. Shared (اشتراکی)
- **Dashboard**: `ui:dashboard` - داشبورد
- **Companies**: `shared:companies` - شرکت‌ها
- **Company Units**: `shared:company_units` - واحدهای شرکت
- **SMTP Servers**: `shared:smtp_servers` - سرورهای SMTP
- **Django Admin**: `admin_panel` - پنل مدیریت Django
- **Users** (گروه):
  - **Users**: `shared:users` - کاربران
  - **Groups**: `shared:groups` - گروه‌ها
  - **Access Levels**: `shared:access_levels` - سطوح دسترسی

### 2. Inventory (انبار)
- **Warehouses**: `inventory:warehouses` - انبارها
- **Items** (گروه):
  - **Edit Items**: `inventory:items` - ویرایش کالاها
  - **Item Serials**: `inventory:item_serials` - سریال‌های کالا
  - **Inventory Balance**: `inventory:inventory_balance` - موجودی انبار
- **Suppliers** (گروه):
  - **Supplier Categories**: `inventory:supplier_categories` - دسته‌بندی تامین‌کنندگان
  - **Supplier List**: `inventory:suppliers` - لیست تامین‌کنندگان
- **Receipts** (گروه):
  - **Temporary Receipts**: `inventory:receipt_temporary` - رسیدهای موقت
  - **Permanent Receipts**: `inventory:receipt_permanent` - رسیدهای دائم
  - **Consignment Receipts**: `inventory:receipt_consignment` - رسیدهای امانی
- **Issues** (گروه):
  - **Permanent Issues**: `inventory:issue_permanent` - حواله‌های دائم
  - **Consumption Issues**: `inventory:issue_consumption` - حواله‌های مصرف
  - **Consignment Issues**: `inventory:issue_consignment` - حواله‌های امانی
  - **حواله انتقال بین انبارها**: `inventory:issue_warehouse_transfer` - انتقال بین انبارها
- **Stocktaking** (گروه):
  - **Deficit Records**: `inventory:stocktaking_deficit` - ثبت کسری
  - **Surplus Records**: `inventory:stocktaking_surplus` - ثبت اضافه
  - **Stocktaking Records**: `inventory:stocktaking_records` - سوابق انبارگردانی

### 3. Production (تولید)
- **Personnel**: `production:personnel` - پرسنل
- **Machines**: `production:machines` - ماشین‌آلات
- **Work Lines**: `production:work_lines` - خطوط تولید
- **BOM**: `production:bom_list` - لیست مواد اولیه
- **Processes**: `production:processes` - فرآیندها
- **Product Orders**: `production:product_orders` - سفارشات تولید
- **Transfer to Line Requests**: `production:transfer_requests` - درخواست‌های انتقال به خط
- **Performance Records**: `production:performance_records` - سوابق عملکرد
- **QC Operations**: `production:qc_operations` - عملیات کنترل کیفیت
- **Rework**: `production:rework_document_list` - بازکاری
- **شناسایی و ردیابی**: `production:tracking_identification` - ردیابی و شناسایی

### 4. Quality Control (کنترل کیفیت)
- **Temporary Receipts**: `qc:temporary_receipts` - رسیدهای موقت
- **Serial Assignment**: `qc:serial_assignment_list` - تخصیص سریال
- **Batch Assignment**: `qc:batch_assignment_list` - تخصیص بچ

### 5. Ticketing (تیکتینگ)
- **Tickets** (گروه):
  - **Create Ticket**: `ticketing:ticket_create` - ایجاد تیکت
  - **Respond to Ticket**: `ticketing:ticket_respond` - پاسخ به تیکت
- **Templates** (گروه):
  - **Templates**: `ticketing:templates` - قالب‌ها
  - **Categories**: `ticketing:categories` - دسته‌بندی‌ها
  - **Subcategories**: `ticketing:subcategories` - زیردسته‌بندی‌ها
- **Automation** (گروه):
  - **Auto Response**: `ticketing:auto_response` - پاسخ خودکار

### 6. Accounting (حسابداری)
- **تعاریف پایه** (گروه):
  - **سال مالی**: `accounting:fiscal_years` - سال مالی
  - **چارت حساب‌ها**: `accounting:accounts` - چارت حساب
  - **تعریف حساب کل**: `accounting:gl_accounts` - حساب کل
  - **تعریف حساب معین**: `accounting:sub_accounts` - حساب معین
  - **تعریف حساب تفصیلی**: `accounting:tafsili_accounts` - حساب تفصیلی
  - **اتصال سلسله مراتبی تفصیلی**: `accounting:hierarchical_tafsili_connection` - اتصال سلسله مراتبی تفصیلی
  - **انواع تفصیلی**: `accounting:tafsili_types` - انواع تفصیلی
  - **مراکز هزینه**: `accounting:cost_centers` - مراکز هزینه
  - **دسته‌بندی درآمد و هزینه**: `accounting:income_expense_categories` - دسته‌بندی
  - **طرف حساب‌ها**: `accounting:parties` - طرف حساب
  - **حساب‌های نقدی و بانکی**: `accounting:treasury_accounts` - حساب نقدی و بانکی
- **اسناد حسابداری** (گروه):
  - **ثبت سند حسابداری**: `accounting:document_create` - ثبت سند
  - **لیست اسناد حسابداری**: `accounting:document_list` - لیست اسناد
  - **سندهای باز، قطعی، برگشتی**: `accounting:document_status` - وضعیت اسناد
  - **گردش حساب**: `accounting:report_account_movements` - گردش حساب
  - **گردش تفصیلی**: `accounting:tafsili_movements` - گردش تفصیلی
  - **تراز آزمایشی**: `accounting:report_trial_balance` - تراز آزمایشی
  - **ترازنامه**: `accounting:report_balance_sheet` - ترازنامه
  - **صورت سود و زیان**: `accounting:report_income_statement` - صورت سود و زیان
- **خزانه‌داری** (گروه):
  - **دریافت**: `accounting:treasury_receive` - دریافت
  - **پرداخت**: `accounting:treasury_pay` - پرداخت
  - **تراکنش‌های خزانه**: `accounting:treasury_transactions` - تراکنش‌ها
  - **انتقال بین حساب‌ها**: `accounting:treasury_transfer` - انتقال
  - **حساب‌های نقدی و بانکی**: `accounting:treasury_accounts` - حساب نقدی و بانکی
  - **مدیریت چک‌ها**: `accounting:treasury_checks` - مدیریت چک
  - **تطبیق بانکی**: `accounting:treasury_reconciliation` - تطبیق بانکی
  - **گزارش وجوه نقد و بانک‌ها**: `accounting:treasury_cash_report` - گزارش نقد و بانک
  - **درخواست‌های پرداخت**: `accounting:payment_requests` - درخواست پرداخت
  - **تخصیص مرکز هزینه**: `accounting:cost_allocation` - تخصیص مرکز هزینه
  - **گزارش درآمد**: `accounting:income_report` - گزارش درآمد
  - **گزارش هزینه**: `accounting:expense_report` - گزارش هزینه
  - **گزارش مراکز هزینه**: `accounting:cost_center_report` - گزارش مراکز هزینه
- **طرف حساب‌ها** (گروه):
  - **لیست طرف حساب‌ها**: `accounting:parties` - لیست طرف حساب
  - **گردش طرف حساب**: `accounting:party_movements` - گردش طرف حساب
  - **گزارش مانده طرف حساب‌ها**: `accounting:party_balance_report` - گزارش مانده
- **حقوق و دستمزد** (گروه):
  - **پرداخت حقوق و دستمزد**: `accounting:payroll_payment` - پرداخت حقوق
  - **تنظیمات بیمه و مالیات**: `accounting:payroll_insurance_tax` - تنظیمات
  - **بارگذاری اسناد حقوق و دستمزد**: `accounting:payroll_document` - بارگذاری
  - **خروجی حقوق و دستمزد برای بانک**: `accounting:payroll_bank_transfer` - خروجی بانک
- **مالیات و مقررات** (گروه):
  - **مدیریت VAT**: `accounting:tax_vat` - مدیریت VAT
  - **تنظیمات سامانه مودیان**: `accounting:tax_moadian_settings` - تنظیمات مودیان
  - **گزارش VAT**: `accounting:report_vat` - گزارش VAT
  - **گزارش فصلی (TTMS / ماده 169)**: `accounting:tax_seasonal` - گزارش فصلی
  - **اعتبارسنجی اسناد برای ارسال به سامانه مودیان**: `accounting:tax_validation` - اعتبارسنجی
  - **گزارش مغایرت مالیاتی**: `accounting:tax_discrepancy_report` - گزارش مغایرت
- **گزارشات مالی** (گروه):
  - **تراز آزمایشی**: `accounting:report_trial_balance` - تراز آزمایشی
  - **ترازنامه**: `accounting:report_balance_sheet` - ترازنامه
  - **سود و زیان**: `accounting:report_income_statement` - سود و زیان
  - **جریان وجوه نقد**: `accounting:report_cash_flow` - جریان وجوه نقد
  - **گزارش حساب‌ها**: `accounting:report_account_movements` - گزارش حساب
  - **گزارش تفصیلی و مراکز هزینه**: `accounting:report_tafsili_cost_center` - گزارش تفصیلی
  - **گزارش چک‌ها**: `accounting:report_checks` - گزارش چک
  - **گزارش خزانه**: `accounting:report_treasury` - گزارش خزانه
  - **گزارش طرف حساب**: `accounting:report_party_statement` - گزارش طرف حساب
  - **گزارش VAT**: `accounting:report_vat` - گزارش VAT
  - **گزارش عملیات ماهانه**: `accounting:report_monthly` - گزارش ماهانه
- **اسناد و فایل‌ها** (گروه):
  - **بارگذاری اسناد**: `accounting:attachment_upload` - بارگذاری
  - **مدیریت اسناد پیوست**: `accounting:attachment_list` - مدیریت پیوست
  - **پیوست به سند**: `accounting:attachment_attach` - پیوست
- **ابزارها و عملیات تکمیلی** (گروه):
  - **بستن حساب‌های موقت**: `accounting:close_temp_accounts` - بستن حساب موقت
  - **افتتاحیه خودکار**: `accounting:opening_entry` - افتتاحیه
  - **اختتامیه**: `accounting:closing_entry` - اختتامیه
  - **یکپارچه‌سازی اطلاعات**: `accounting:integration` - یکپارچه‌سازی
  - **پشتیبان‌گیری و بازیابی**: `accounting:backup_restore` - پشتیبان‌گیری
- **حسابداری انبار** (گروه):
  - **سند هزینه انبار**: `accounting:warehouse_expense` - سند هزینه
  - **سند درآمد انبار**: `accounting:warehouse_income` - سند درآمد
  - **افتتاحیه و اختتامیه**: `accounting:warehouse_opening_closing` - افتتاحیه و اختتامیه
  - **تنظیمات حسابداری انبار**: `accounting:warehouse_settings` - تنظیمات
- **تنظیمات** (گروه):
  - **تنظیمات حسابداری**: `accounting:settings` - تنظیمات حسابداری
  - **تنظیمات خزانه**: `accounting:settings_treasury` - تنظیمات خزانه
  - **تنظیمات مالیات**: `accounting:settings_tax` - تنظیمات مالیات

### 7. Sales (فروش)
- **Dashboard**: `sales:dashboard` - داشبورد فروش
- **Item Price Cards**: `sales:price_card_list` - کارت‌های قیمت
- **صدور فاکتور**: `sales:invoice_create` - صدور فاکتور
- **مشتریان**: `sales:customers` - مشتریان
- **محل دریافت درآمد**: `sales:income_receipt_location_list` - محل دریافت درآمد
- **تنظیمات**: `sales:settings` - تنظیمات

### 8. Human Resources (منابع انسانی)
- **Dashboard**: `hr:dashboard` - داشبورد منابع انسانی
- **Personnel** (گروه):
  - **Create Personnel**: `hr:personnel_create` - ایجاد پرسنل
  - **Decree Assignment**: `hr:personnel_decree_assignment` - تخصیص حکم
  - **Create Personnel Form**: `hr:personnel_form_create` - ایجاد فرم پرسنل
  - **Personnel Form Groups**: `hr:personnel_form_groups` - گروه‌های فرم
  - **Personnel Form Sub-Groups**: `hr:personnel_form_subgroups` - زیرگروه‌های فرم
- **حکم‌های حقوق و دستمزد** (گروه):
  - **حکم‌ها**: `hr:payroll_decrees` - حکم‌ها
  - **گروه‌بندی حکم‌ها**: `hr:payroll_decree_groups` - گروه‌بندی
  - **زیر گروه‌بندی حکم‌ها**: `hr:payroll_decree_subgroups` - زیرگروه‌بندی
- **Loans** (گروه):
  - **Loan Management**: `hr:loans_management` - مدیریت وام
  - **Loan Scheduling**: `hr:loans_scheduling` - زمان‌بندی وام
  - **Savings Fund**: `hr:loans_savings_fund` - صندوق پس‌انداز

### 9. Requests (درخواست‌ها)
- **Purchase Request**: `inventory:purchase_requests` - درخواست خرید
- **Service Request**: `procurement:service_requests` - درخواست خدمات
- **Warehouse Request**: `inventory:warehouse_requests` - درخواست انبار
- **Transfer to Line Requests**: `production:transfer_requests` - درخواست انتقال به خط
- **Leave Request**: `hr:requests_leave` - درخواست مرخصی
- **Sick Leave Request**: `hr:requests_sick_leave` - درخواست مرخصی استعلاجی
- **Loan Request**: `hr:requests_loan` - درخواست وام

### 10. Office Automation (اتوماسیون اداری)
- **Dashboard**: `office_automation:dashboard` - داشبورد
- **Inbox** (گروه):
  - **Incoming Letters**: `office_automation:inbox_incoming` - نامه‌های ورودی
  - **Write Letter**: `office_automation:inbox_write` - نوشتن نامه
  - **Fill Form**: `office_automation:inbox_fill_form` - پر کردن فرم
- **Processes** (گروه):
  - **Process Engine**: `office_automation:processes_engine` - موتور فرآیند
  - **Process-Form Connection**: `office_automation:processes_form_connection` - اتصال فرآیند به فرم
- **Forms** (گروه):
  - **Form Builder**: `office_automation:forms_builder` - سازنده فرم

### 11. Transportation (حمل و نقل)
- **Dashboard**: `transportation:dashboard` - داشبورد حمل و نقل

### 12. Procurement (تدارکات)
- **Dashboard**: `procurement:dashboard` - داشبورد تدارکات
- **Purchase** (گروه):
  - **Purchase Orders**: `procurement:purchase_orders` - سفارشات خرید
  - **Purchase Invoices**: `procurement:purchase_invoices` - فاکتورهای خرید
- **Services** (گروه):
  - **Service Requests**: `procurement:service_requests` - درخواست‌های خدمات
  - **Service Invoices**: `procurement:service_invoices` - فاکتورهای خدمات
- **Buyers** (گروه):
  - **Buyers List**: `procurement:buyers` - لیست خریداران
  - **Create Buyer**: `procurement:buyer_create` - ایجاد خریدار
  - **Buyer Assignment**: `procurement:buyer_assignment` - تخصیص خریدار

---

## لیست یونیک کامل تمام صفحات (Unique List of All Pages)

این لیست شامل تمام URL های منوی بالای صفحه و منوی کناری به صورت یکجا و بدون تکرار می‌باشد:

### UI & Shared
- `ui:dashboard` - داشبورد اصلی
  - **مسیر**: `/`
- `admin_panel` - پنل مدیریت Django
  - **مسیر**: `/admin-panel/`
- `shared:companies` - مدیریت شرکت‌ها
  - **مسیر**: `/shared/companies/`
- `shared:company_units` - مدیریت واحدهای شرکت
  - **مسیر**: `/shared/units/`
- `shared:smtp_servers` - مدیریت سرورهای SMTP
  - **مسیر**: `/shared/smtp-servers/`
- `shared:users` - مدیریت کاربران
  - **مسیر**: `/shared/users/`
- `shared:groups` - مدیریت گروه‌ها
  - **مسیر**: `/shared/groups/`
- `shared:access_levels` - مدیریت سطوح دسترسی
  - **مسیر**: `/shared/access-levels/`
- `logout` - خروج از سیستم
  - **مسیر**: `/logout/`

### Inventory (انبار)
- `inventory:warehouses` - مدیریت انبارها
  - **مسیر**: `/inventory/warehouses/`
- `inventory:items` - ویرایش کالاها
  - **مسیر**: `/inventory/items/`
- `inventory:item_serials` - سریال‌های کالا
  - **مسیر**: `/inventory/item-serials/`
- `inventory:inventory_balance` - موجودی انبار
  - **مسیر**: `/inventory/balance/`
- `inventory:supplier_categories` - دسته‌بندی تامین‌کنندگان
  - **مسیر**: `/inventory/supplier-categories/`
- `inventory:suppliers` - لیست تامین‌کنندگان
  - **مسیر**: `/inventory/suppliers/`
- `inventory:receipt_temporary` - رسیدهای موقت
  - **مسیر**: `/inventory/receipts/temporary/`
- `inventory:receipt_permanent` - رسیدهای دائم
  - **مسیر**: `/inventory/receipts/permanent/`
- `inventory:receipt_consignment` - رسیدهای امانی
  - **مسیر**: `/inventory/receipts/consignment/`
- `inventory:issue_permanent` - حواله‌های دائم
  - **مسیر**: `/inventory/issues/permanent/`
- `inventory:issue_consumption` - حواله‌های مصرف
  - **مسیر**: `/inventory/issues/consumption/`
- `inventory:issue_consignment` - حواله‌های امانی
  - **مسیر**: `/inventory/issues/consignment/`
- `inventory:issue_warehouse_transfer` - حواله انتقال بین انبارها
  - **مسیر**: `/inventory/issues/warehouse-transfer/`
- `inventory:stocktaking_deficit` - ثبت کسری
  - **مسیر**: `/inventory/stocktaking/deficit/`
- `inventory:stocktaking_surplus` - ثبت اضافه
  - **مسیر**: `/inventory/stocktaking/surplus/`
- `inventory:stocktaking_records` - سوابق انبارگردانی
  - **مسیر**: `/inventory/stocktaking/records/`
- `inventory:purchase_requests` - درخواست خرید
  - **مسیر**: `/inventory/purchase-requests/`
- `inventory:warehouse_requests` - درخواست انبار
  - **مسیر**: `/inventory/warehouse-requests/`

### Production (تولید)
- `production:personnel` - پرسنل تولید
  - **مسیر**: `/production/personnel/`
- `production:machines` - ماشین‌آلات
  - **مسیر**: `/production/machines/`
- `production:work_lines` - خطوط تولید
  - **مسیر**: `/production/work-lines/`
- `production:bom_list` - لیست مواد اولیه
  - **مسیر**: `/production/bom/`
- `production:processes` - فرآیندها
  - **مسیر**: `/production/processes/`
- `production:product_orders` - سفارشات تولید
  - **مسیر**: `/production/product-orders/`
- `production:transfer_requests` - درخواست‌های انتقال به خط
  - **مسیر**: `/production/transfer-requests/`
- `production:performance_records` - سوابق عملکرد
  - **مسیر**: `/production/performance-records/`
- `production:qc_operations` - عملیات کنترل کیفیت
  - **مسیر**: `/production/qc-operations/`
- `production:rework_document_list` - بازکاری
  - **مسیر**: `/production/rework/`
- `production:tracking_identification` - شناسایی و ردیابی
  - **مسیر**: `/production/tracking-identification/`

### Quality Control (کنترل کیفیت)
- `qc:temporary_receipts` - بازرسی‌ها / رسیدهای موقت
  - **مسیر**: `/qc/temporary-receipts/`
- `qc:serial_assignment_list` - تخصیص سریال
  - **مسیر**: `/qc/serial-assignment/`
- `qc:batch_assignment_list` - تخصیص بچ
  - **مسیر**: `/qc/batch-assignment/`

### Ticketing (تیکتینگ)
- `ticketing:ticket_create` - ایجاد تیکت
  - **مسیر**: `/ticketing/tickets/create/`
- `ticketing:ticket_respond` - پاسخ به تیکت
  - **مسیر**: `/ticketing/tickets/respond/`
- `ticketing:templates` - قالب‌ها
  - **مسیر**: `/ticketing/management/templates/`
- `ticketing:categories` - دسته‌بندی‌ها
  - **مسیر**: `/ticketing/management/categories/`
- `ticketing:subcategories` - زیردسته‌بندی‌ها
  - **مسیر**: `/ticketing/management/subcategories/`
- `ticketing:auto_response` - پاسخ خودکار
  - **مسیر**: `/ticketing/auto-response/`

### Accounting (حسابداری)
- `accounting:fiscal_years` - سال مالی
  - **مسیر**: `/accounting/fiscal-years/`
- `accounting:accounts` - چارت حساب‌ها
  - **مسیر**: `/accounting/accounts/`
- `accounting:gl_accounts` - تعریف حساب کل
  - **مسیر**: `/accounting/gl-accounts/`
- `accounting:sub_accounts` - تعریف حساب معین
  - **مسیر**: `/accounting/sub-accounts/`
- `accounting:tafsili_accounts` - تعریف حساب تفصیلی
  - **مسیر**: `/accounting/tafsili-accounts/`
- `accounting:hierarchical_tafsili_connection` - اتصال سلسله مراتبی تفصیلی
  - **مسیر**: `/accounting/hierarchical-tafsili-connection/`
- `accounting:cost_centers` - مراکز هزینه
  - **مسیر**: `/accounting/income-expense/cost-centers/`
- `accounting:income_expense_categories` - دسته‌بندی درآمد و هزینه
  - **مسیر**: `/accounting/income-expense/categories/`
- `accounting:parties` - طرف حساب‌ها
  - **مسیر**: `/accounting/parties/`
- `accounting:treasury_accounts` - حساب‌های نقدی و بانکی
  - **مسیر**: `/accounting/treasury/accounts/`
- `accounting:document_create` - ثبت سند حسابداری
  - **مسیر**: `/accounting/documents/create/`
- `accounting:document_list` - لیست اسناد حسابداری
  - **مسیر**: `/accounting/documents/list/`
- `accounting:document_status` - سندهای باز، قطعی، برگشتی
  - **مسیر**: `/accounting/documents/status/`
- `accounting:report_account_movements` - گردش حساب / گزارش حساب‌ها
  - **مسیر**: `/accounting/reports/account-movements/`
- `accounting:tafsili_movements` - گردش تفصیلی
  - **مسیر**: `/accounting/tafsili-movements/`
- `accounting:report_trial_balance` - تراز آزمایشی
  - **مسیر**: `/accounting/reports/trial-balance/`
- `accounting:report_balance_sheet` - ترازنامه
  - **مسیر**: `/accounting/reports/balance-sheet/`
- `accounting:report_income_statement` - صورت سود و زیان / سود و زیان
  - **مسیر**: `/accounting/reports/income-statement/`
- `accounting:treasury_receive` - دریافت
  - **مسیر**: `/accounting/treasury/receive/`
- `accounting:treasury_pay` - پرداخت
  - **مسیر**: `/accounting/treasury/pay/`
- `accounting:treasury_transactions` - تراکنش‌های خزانه
  - **مسیر**: `/accounting/treasury/transactions/`
- `accounting:treasury_transfer` - انتقال بین حساب‌ها
  - **مسیر**: `/accounting/treasury/transfer/`
- `accounting:treasury_checks` - مدیریت چک‌ها
  - **مسیر**: `/accounting/treasury/checks/`
- `accounting:treasury_reconciliation` - تطبیق بانکی
  - **مسیر**: `/accounting/treasury/reconciliation/`
- `accounting:treasury_cash_report` - گزارش وجوه نقد و بانک‌ها
  - **مسیر**: `/accounting/treasury/cash-report/`
- `accounting:payment_requests` - درخواست‌های پرداخت
  - **مسیر**: `/accounting/treasury/payment-requests/`
- `accounting:cost_allocation` - تخصیص مرکز هزینه
  - **مسیر**: `/accounting/income-expense/cost-allocation/`
- `accounting:income_report` - گزارش درآمد
  - **مسیر**: `/accounting/income-expense/income-report/`
- `accounting:expense_report` - گزارش هزینه
  - **مسیر**: `/accounting/income-expense/expense-report/`
- `accounting:cost_center_report` - گزارش مراکز هزینه
  - **مسیر**: `/accounting/income-expense/cost-center-report/`
- `accounting:party_movements` - گردش طرف حساب
  - **مسیر**: `/accounting/parties/movements/`
- `accounting:party_balance_report` - گزارش مانده طرف حساب‌ها
  - **مسیر**: `/accounting/parties/balance-report/`
- `accounting:payroll_payment` - پرداخت حقوق و دستمزد
  - **مسیر**: `/accounting/payroll/payment/`
- `accounting:payroll_insurance_tax` - تنظیمات بیمه و مالیات
  - **مسیر**: `/accounting/payroll/insurance-tax/`
- `accounting:payroll_document` - بارگذاری اسناد حقوق و دستمزد
  - **مسیر**: `/accounting/payroll/document/`
- `accounting:payroll_bank_transfer` - خروجی حقوق و دستمزد برای بانک
  - **مسیر**: `/accounting/payroll/bank-transfer/`
- `accounting:tax_vat` - مدیریت VAT
  - **مسیر**: `/accounting/tax/vat/`
- `accounting:tax_moadian_settings` - تنظیمات سامانه مودیان
  - **مسیر**: `/accounting/tax/moadian-settings/`
- `accounting:report_vat` - گزارش VAT
  - **مسیر**: `/accounting/reports/vat/`
- `accounting:tax_seasonal` - گزارش فصلی (TTMS / ماده 169)
  - **مسیر**: `/accounting/tax/seasonal/`
- `accounting:tax_validation` - اعتبارسنجی اسناد برای ارسال به سامانه مودیان
  - **مسیر**: `/accounting/tax/validation/`
- `accounting:tax_discrepancy_report` - گزارش مغایرت مالیاتی
  - **مسیر**: `/accounting/tax/discrepancy-report/`
- `accounting:report_cash_flow` - جریان وجوه نقد
  - **مسیر**: `/accounting/reports/cash-flow/`
- `accounting:report_tafsili_cost_center` - گزارش تفصیلی و مراکز هزینه
  - **مسیر**: `/accounting/reports/tafsili-cost-center/`
- `accounting:report_checks` - گزارش چک‌ها
  - **مسیر**: `/accounting/reports/checks/`
- `accounting:report_treasury` - گزارش خزانه
  - **مسیر**: `/accounting/reports/treasury/`
- `accounting:report_party_statement` - گزارش طرف حساب
  - **مسیر**: `/accounting/reports/party-statement/`
- `accounting:report_monthly` - گزارش عملیات ماهانه
  - **مسیر**: `/accounting/reports/monthly/`
- `accounting:report_account_browser` - مرور حساب‌ها
  - **مسیر**: `/accounting/reports/account-browser/`
- `accounting:attachment_upload` - بارگذاری اسناد
  - **مسیر**: `/accounting/attachments/upload/`
- `accounting:attachment_list` - مدیریت اسناد پیوست
  - **مسیر**: `/accounting/attachments/list/`
- `accounting:attachment_attach` - پیوست به سند
  - **مسیر**: `/accounting/attachments/attach/`
- `accounting:automation_processes` - فرایندهای خودکار
  - **مسیر**: `/accounting/automation/processes/`
- `accounting:automation_execution_logs` - لاگ اجرا
  - **مسیر**: `/accounting/automation/logs/`
- `accounting:close_temp_accounts` - بستن حساب‌های موقت
  - **مسیر**: `/accounting/utils/close-temp-accounts/`
- `accounting:opening_entry` - افتتاحیه خودکار
  - **مسیر**: `/accounting/utils/opening-entry/`
- `accounting:closing_entry` - اختتامیه
  - **مسیر**: `/accounting/utils/closing-entry/`
- `accounting:integration` - یکپارچه‌سازی اطلاعات
  - **مسیر**: `/accounting/utils/integration/`
- `accounting:backup_restore` - پشتیبان‌گیری و بازیابی
  - **مسیر**: `/accounting/utils/backup-restore/`
- `accounting:warehouse_expense` - سند هزینه انبار
  - **مسیر**: `/accounting/warehouse/expense/`
- `accounting:warehouse_income` - سند درآمد انبار
  - **مسیر**: `/accounting/warehouse/income/`
- `accounting:warehouse_opening_closing` - افتتاحیه و اختتامیه
  - **مسیر**: `/accounting/warehouse/opening-closing/`
- `accounting:warehouse_settings` - تنظیمات حسابداری انبار
  - **مسیر**: `/accounting/warehouse/settings/`
- `accounting:settings` - تنظیمات حسابداری
  - **مسیر**: `/accounting/settings/`
- `accounting:settings_treasury` - تنظیمات خزانه
  - **مسیر**: `/accounting/settings/treasury/`
- `accounting:settings_tax` - تنظیمات مالیات
  - **مسیر**: `/accounting/settings/tax/`

### Sales (فروش)
- `sales:dashboard` - داشبورد فروش
  - **مسیر**: `/sales/`
- `sales:price_card_list` - کارت‌های قیمت کالا
  - **مسیر**: `/sales/price-card/`
- `sales:invoice_create` - صدور فاکتور فروش
  - **مسیر**: `/sales/invoice/create/`
- `sales:customers` - مدیریت مشتریان
  - **مسیر**: `/sales/customers/`
- `sales:income_receipt_location_list` - محل دریافت درآمد
  - **مسیر**: `/sales/income-receipt-location/`
- `sales:settings` - تنظیمات فروش
  - **مسیر**: `/sales/settings/`

### Human Resources (منابع انسانی)
- `hr:dashboard` - داشبورد منابع انسانی
  - **مسیر**: `/hr/`
- `hr:personnel_create` - ایجاد پرسنل
  - **مسیر**: `/hr/personnel/create/`
- `hr:personnel_decree_assignment` - تخصیص حکم
  - **مسیر**: `/hr/personnel/decree-assignment/`
- `hr:personnel_form_create` - فرم پرسنل / ایجاد فرم پرسنل
  - **مسیر**: `/hr/personnel/form/create/`
- `hr:personnel_form_groups` - گروه‌های فرم / Personnel Form Groups
  - **مسیر**: `/hr/personnel/form-groups/`
- `hr:personnel_form_subgroups` - زیرگروه‌های فرم / Personnel Form Sub-Groups
  - **مسیر**: `/hr/personnel/form-subgroups/`
- `hr:payroll_decrees` - حکم‌های حقوق و دستمزد
  - **مسیر**: `/hr/payroll/decrees/`
- `hr:payroll_decree_groups` - گروه‌بندی حکم‌ها
  - **مسیر**: `/hr/payroll/decree-groups/`
- `hr:payroll_decree_subgroups` - زیر گروه‌بندی حکم‌ها
  - **مسیر**: `/hr/payroll/decree-subgroups/`
- `hr:loans_management` - مدیریت وام
  - **مسیر**: `/hr/loans/management/`
- `hr:loans_scheduling` - زمان‌بندی وام / Loan Scheduling
  - **مسیر**: `/hr/loans/scheduling/`
- `hr:loans_savings_fund` - صندوق پس‌انداز
  - **مسیر**: `/hr/loans/savings-fund/`
- `hr:requests_leave` - درخواست مرخصی
  - **مسیر**: `/hr/requests/leave/`
- `hr:requests_sick_leave` - درخواست مرخصی استعلاجی
  - **مسیر**: `/hr/requests/sick-leave/`
- `hr:requests_loan` - درخواست وام
  - **مسیر**: `/hr/requests/loan/`

### Office Automation (اتوماسیون اداری)
- `office_automation:dashboard` - داشبورد اتوماسیون
  - **مسیر**: `/office-automation/`
- `office_automation:inbox_incoming` - نامه‌های ورودی
  - **مسیر**: `/office-automation/inbox/incoming/`
- `office_automation:inbox_write` - نوشتن نامه
  - **مسیر**: `/office-automation/inbox/write/`
- `office_automation:inbox_fill_form` - پر کردن فرم
  - **مسیر**: `/office-automation/inbox/fill-form/`
- `office_automation:processes_engine` - موتور فرآیند
  - **مسیر**: `/office-automation/processes/engine/`
- `office_automation:processes_form_connection` - اتصال فرآیند به فرم
  - **مسیر**: `/office-automation/processes/form-connection/`
- `office_automation:forms_builder` - سازنده فرم
  - **مسیر**: `/office-automation/forms/builder/`

### Transportation (حمل و نقل)
- `transportation:dashboard` - داشبورد حمل و نقل
  - **مسیر**: `/transportation/`

### Procurement (تدارکات)
- `procurement:dashboard` - داشبورد تدارکات
  - **مسیر**: `/procurement/`
- `procurement:purchase_orders` - سفارشات خرید
  - **مسیر**: `/procurement/purchase-orders/`
- `procurement:purchase_invoices` - فاکتورهای خرید
  - **مسیر**: `/procurement/purchase-invoices/`
- `procurement:service_requests` - درخواست‌های خدمات / درخواست خدمات
  - **مسیر**: `/procurement/service-requests/`
- `procurement:service_invoices` - فاکتورهای خدمات
  - **مسیر**: `/procurement/service-invoices/`
- `procurement:buyers` - لیست خریداران
  - **مسیر**: `/procurement/buyers/`
- `procurement:buyer_create` - ایجاد خریدار
  - **مسیر**: `/procurement/buyers/create/`
- `procurement:buyer_assignment` - تخصیص خریدار
  - **مسیر**: `/procurement/buyers/assignment/`

---

## نکات مهم

1. **دسترسی‌ها**: نمایش بسیاری از موارد منو به دسترسی‌های کاربر (feature permissions) بستگی دارد.
2. **Superuser**: برخی موارد فقط برای superuser قابل مشاهده هستند.
3. **منوی بالای صفحه**: شامل Dashboard و ماژول‌ها در یک منوی بزرگ (Mega Menu) می‌باشد.
4. **منوی کناری**: شامل تمام بخش‌ها به صورت دسته‌بندی شده با قابلیت باز و بسته شدن (collapsible) می‌باشد.
5. **URL Names**: تمام URL ها به صورت name space استفاده می‌کنند (مثلاً `ui:dashboard`، `shared:companies` و غیره).
6. **تعداد کل صفحات**: در مجموع **۱۵۰+** صفحه منحصر به فرد در سیستم وجود دارد که در منوهای بالای صفحه و کناری قابل دسترسی هستند.

