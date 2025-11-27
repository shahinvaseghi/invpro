# inventory app overview

The inventory module models master data, supplier relationships, transactions, and stock adjustments. This README documents each custom file and the classes/functions defined in it.

## models.py

Contains all inventory-related entities. Major groups:

- **Mixins**
  - `InventoryBaseModel`: extends shared mixins for timestamps, activation, metadata, and company scope.
  - `InventorySortableModel`: adds `sort_order` to the base.
  - `InventoryDocumentBase`: base for document-style models with `document_code`, `document_date`, `notes`, and `is_locked`.

- **Master Data**
  - `ItemType`, `ItemCategory`, `ItemSubcategory`: hierarchical classification with per-company uniqueness constraints.
  - `Warehouse`: physical storage locations, each scoped by company.
  - **Note**: `WorkLine` has been moved to the `production` module as it is primarily a production concept, though it can optionally be used in inventory consumption issues.

- **Item Definitions**
  - `Item`: central product/part definition. Automatically generates `item_code`, `sequence_segment`, and `batch_number` based on type/category/subcategory and current month. Supports optional `secondary_batch_number` (user-defined secondary batch number).
  - `ItemSpec`: JSON specification per item; caches `item_code`.
  - `ItemUnit`: unit conversions; caches `item_code`.
  - `ItemWarehouse`: mapping between items and warehouses (primary flag support).
  - `ItemSubstitute`: defines substitute relationships and quantities between items; caches both source and target codes.
  - `ItemLot`: traceability record for lot-controlled items; generates `LOT-MMYY-XXXXXX` format codes.
  - `ItemSerial`: per-unit tracking for serialised assets (current status, location, linked documents) with automatic creation when receipts are locked. Supports optional `secondary_serial_code` (user-defined secondary serial number).
  - `ItemSerialHistory`: immutable audit log documenting every serial event (reservation, release, issue, consumption, return).

- **Supplier Relations**
  - `Supplier`: supplier master data.
  - `SupplierCategory`, `SupplierSubcategory`, `SupplierItem`: link suppliers to categories, subcategories, and specific items with metadata such as MOQ, lead time, and primary flags.

- **Requests & Receipts**
  - `PurchaseRequest`: captures multi-line item requests with priority, status workflow, and references. Approved purchase requests can be used to directly create receipts (Temporary, Permanent, or Consignment) through intermediate selection pages.
  - `WarehouseRequest`: captures single-line internal material requests with priority, status workflow, and references. Approved warehouse requests can be used to directly create issues (Permanent, Consumption, or Consignment) through intermediate selection pages.
  - `ReceiptTemporary`: intake staging record (awaiting QC); caches item/warehouse codes and supplier code, tracks QC approval. Statuses include:
    - `DRAFT`: تازه ایجاد شده و هنوز برای QC ارسال نشده.
    - `AWAITING_INSPECTION`: پس از فشردن دکمه «ارسال به QC».
    - `APPROVED`: پس از تأیید QC (سند قفل می‌شود و آماده‌ی تبدیل است).
    - `CLOSED`: اسنادی که لغو یا توسط QC رد شده‌اند.
  - `ReceiptPermanent`: finalized receipt (optionally linked to temporary receipt and purchase request).
  - `ReceiptConsignment`: consignment handling with ownership status, conversion links, and optional temporary receipt reference.

- **Issues & Receipts (Multi-Line Support)**
  - `IssuePermanent`, `IssueConsumption`, `IssueConsignment`: outbound document variants برای حالات دائم، مصرفی و امانی. این مدل‌ها اکنون **header-only** هستند و فقط اطلاعات سربرگ سند (کد سند، تاریخ، واحد سازمانی مقصد، یادداشت‌ها) را نگه می‌دارند.
  - `ReceiptPermanent`, `ReceiptConsignment`: inbound document variants که اکنون **header-only** هستند و فقط اطلاعات سربرگ سند (کد سند، تاریخ، تأمین‌کننده، یادداشت‌ها) را نگه می‌دارند.
  - **Line Models**: هر نوع سند دارای مدل‌های Line مربوطه است:
    - `IssuePermanentLine`, `IssueConsumptionLine`, `IssueConsignmentLine`: ردیف‌های حواله که شامل کالا، انبار، مقدار، واحد و فیلدهای خاص هر نوع هستند:
      - **`IssuePermanentLine`**: فیلد `destination_type` به صورت اختیاری واحد کاری (`CompanyUnit`) را نگه می‌دارد.
      - **`IssueConsumptionLine`**: فیلد `consumption_type` می‌تواند واحد کاری (`company_unit`) یا خط کاری (`work_line`) باشد که از طریق `destination_type_choice` در فرم انتخاب می‌شود.
      - **`IssueConsignmentLine`**: فیلد `destination_type` به صورت اختیاری واحد کاری (`CompanyUnit`) را نگه می‌دارد.
    - `ReceiptPermanentLine`, `ReceiptConsignmentLine`: ردیف‌های رسید که شامل کالا، انبار، مقدار، واحد و اطلاعات قیمت‌گذاری هستند.
    - `ReceiptTemporaryLine`: ردیف‌های رسید موقت که فقط اطلاعات کالا، انبار، مقدار و واحد را ذخیره می‌کنند. اطلاعات تأمین‌کننده در سطح سربرگ (`ReceiptTemporary`) نگه‌داری می‌شود و این مدل عمداً فیلد `supplier` ندارد؛ هر کدی که به داده‌های تأمین‌کننده نیاز دارد باید از خود سند موقت استفاده کند.
  - هر Line می‌تواند **چندین سریال** داشته باشد (از طریق `ManyToManyField` به `ItemSerial`). سریال‌ها در سطح Line مدیریت می‌شوند، نه در سطح سند.
  - برای هر Line که کالای آن `has_lot_tracking=1` دارد، یک دکمه «Assign Serials» یا «Manage Serials» در فرم سند نمایش داده می‌شود که کاربر را به صفحه اختصاصی مدیریت سریال آن Line می‌برد.

- **Stocktaking**
  - `StocktakingDeficit`, `StocktakingSurplus`: adjustment documents capturing counted vs expected quantities, valuation, and posting info.
  - `StocktakingRecord`: final confirmation for a stocktaking session with references to variance documents.

Each model enforces unique constraints tailored to multi-company setups and uses `save()` overrides to populate cached fields or generate codes.

## views.py

مهم‌ترین ویوهای موجود:

- `ItemListView`, `ItemCreateView`, `ItemUpdateView`, `ItemDeleteView`: رابط کامل CRUD برای کالاها در رابط کاربری اصلی. `ItemCreateView` و `ItemUpdateView` علاوه بر فرم کالا، فرم‌ست واحدهای ثانویه (`ItemUnit`) را نیز پشتیبانی می‌کنند.
- `ItemSerialListView`: صفحه‌ی جدید «لیست سریال‌ها» که امکان جستجو بر اساس کد رسید، کد کالا یا خود سریال را می‌دهد و وضعیت فعلی، انبار، واحد سازمانی و کد لات هر سریال تولیدشده را نمایش می‌کند. دسترسی به این صفحه طی مجوز `inventory.master.item_serials` کنترل می‌شود.
- در همان ویوها انتخاب «انبارهای مجاز» نیز مدیریت می‌شود؛ بعد از ذخیره، جدول `ItemWarehouse` بر اساس انتخاب‌های کاربر همگام‌سازی و اولین انبار به عنوان انبار اصلی علامت‌گذاری می‌شود.
- `SupplierCategoryCreateView`, `SupplierCreateView` و ویوهای ویرایش/حذف متناظر: فرم‌های اختصاصی برای مدیریت تأمین‌کنندگان و دسته‌بندی‌های آنها (تبدیل از صفحات ادمین به UI داخلی).
- `ReceiptTemporaryCreateView`/`UpdateView`: فرم اختصاصی برای رسید موقت (هنوز single-item است).
- `ReceiptPermanentCreateView`/`UpdateView`, `ReceiptConsignmentCreateView`/`UpdateView`: فرم‌های اختصاصی برای ثبت رسیدهای دائم و امانی با **پشتیبانی چند ردیف**. این ویوها:
  - از `LineFormsetMixin` استفاده می‌کنند تا فرم‌ست ردیف‌ها را مدیریت کنند.
  - کد سند (PRM/CON-YYYYMM-XXXXXX)، تاریخ سند و وضعیت ابتدایی را به صورت خودکار تولید می‌کنند.
  - واحدهای انتخابی را با فهرست واحد اصلی و تبدیل‌های تعریف‌شده محدود می‌کنند و مقدار/قیمت را قبل از ذخیره به واحد اصلی کالا تبدیل می‌کنند.
  - در حالت ویرایش، سرآیند سند را به شکل فقط خواندنی نمایش می‌دهند.
  - برای هر ردیف که کالای آن `has_lot_tracking=1` دارد، دکمه «Manage Serials» نمایش داده می‌شود.
  - **Auto-Fill از Temporary Receipt**: در `ReceiptPermanentCreateView`، هنگام انتخاب `temporary_receipt` در dropdown، JavaScript به‌صورت خودکار خطوط را از temporary receipt populate می‌کند. Validation در `ReceiptPermanentLineForm.clean_item()` برای کالاهای `requires_temporary_receipt=1` را skip می‌کند اگر temporary receipt انتخاب شده باشد. اگر formset validation خطا بدهد، document delete می‌شود و formset با POST data دوباره ساخته می‌شود تا خطاهای validation حفظ شوند.
- `IssuePermanentCreateView`/`UpdateView`, `IssueConsumptionCreateView`/`UpdateView`, `IssueConsignmentCreateView`/`UpdateView`: صفحات اختصاصی برای ایجاد/ویرایش حواله‌ها با **پشتیبانی چند ردیف**. این ویوها:
  - از `LineFormsetMixin` استفاده می‌کنند تا فرم‌ست ردیف‌ها را مدیریت کنند.
  - امکان انتخاب واحد سازمانی مقصد (و برای حواله مصرف، خط تولید) را در سطح سند فراهم می‌کنند.
  - همان منطق انتخاب واحد کالا را به کار می‌گیرند.
  - **اعتبارسنجی موجودی**: قبل از ذخیره، موجودی فعلی هر کالا در انبار انتخاب شده بررسی می‌شود و در صورت ناکافی بودن موجودی، خطا نمایش داده می‌شود. در حالت ویرایش، مقدار قبلی به موجودی اضافه می‌شود تا امکان تغییر مقدار وجود داشته باشد.
  - برای هر ردیف که کالای آن `has_lot_tracking=1` دارد، دکمه «Assign Serials» (یا «View Serials» برای سند قفل‌شده) نمایش داده می‌شود.
  - دکمه‌ی «قفل» روی سند امکان جلوگیری از ویرایش یا حذف بعد از نهایی‌سازی را می‌دهد و قبل از قفل، تمام ردیف‌های سریال‌دار را از نظر تطابق تعداد سریال با مقدار بررسی می‌کند.
- `IssueLineSerialAssignmentBaseView` و کلاس‌های مشتق (`IssuePermanentLineSerialAssignmentView`, `IssueConsumptionLineSerialAssignmentView`, `IssueConsignmentLineSerialAssignmentView`): ویوهای اختصاصی برای مدیریت سریال‌های هر ردیف حواله. هر Line می‌تواند صفحه اختصاصی خود را داشته باشد.
- `ReceiptLineSerialAssignmentBaseView` و کلاس‌های مشتق (`ReceiptPermanentLineSerialAssignmentView`, `ReceiptConsignmentLineSerialAssignmentView`): ویوهای اختصاصی برای مدیریت سریال‌های هر ردیف رسید.
- `StocktakingDeficitCreateView`/`UpdateView`, `StocktakingSurplusCreateView`/`UpdateView`, `StocktakingRecordCreateView`/`UpdateView`: فرم‌های اختصاصی برای اسناد شمارش موجودی که کد سند (STD/STS/STR-YYYYMM-XXXXXX) را تولید کرده، واحدهای مجاز و انبارهای مجاز را بر اساس تنظیمات کالا محدود می‌کنند و امکان قفل کردن سند را پس از نهایی‌سازی فراهم می‌سازند.
- **Request Views**: 
  - `PurchaseRequestListView`, `PurchaseRequestCreateView`, `PurchaseRequestUpdateView`, `PurchaseRequestApproveView`: مدیریت درخواست‌های خرید با workflow تأیید
  - `WarehouseRequestListView`, `WarehouseRequestCreateView`, `WarehouseRequestUpdateView`, `WarehouseRequestApproveView`: مدیریت درخواست‌های انبار با workflow تأیید
  - **Create Receipt from Purchase Request Views**: ویوهای واسط برای ایجاد رسید از درخواست خرید:
    - `CreateTemporaryReceiptFromPurchaseRequestView`, `CreatePermanentReceiptFromPurchaseRequestView`, `CreateConsignmentReceiptFromPurchaseRequestView`: صفحات انتخاب خطوط و مقدار از درخواست خرید
    - `ReceiptTemporaryCreateFromPurchaseRequestView`, `ReceiptPermanentCreateFromPurchaseRequestView`, `ReceiptConsignmentCreateFromPurchaseRequestView`: ویوهای ایجاد رسید که داده‌ها را از session دریافت می‌کنند
    - کاربران می‌توانند خطوط مورد نظر را انتخاب کرده، مقدار را تنظیم کنند و سپس رسید ایجاد کنند
  - **Create Issue from Warehouse Request Views**: ویوهای واسط برای ایجاد حواله از درخواست انبار:
    - `CreatePermanentIssueFromWarehouseRequestView`, `CreateConsumptionIssueFromWarehouseRequestView`, `CreateConsignmentIssueFromWarehouseRequestView`: صفحات انتخاب مقدار از درخواست انبار
    - `IssuePermanentCreateFromWarehouseRequestView`, `IssueConsumptionCreateFromWarehouseRequestView`, `IssueConsignmentCreateFromWarehouseRequestView`: ویوهای ایجاد حواله که داده‌ها را از session دریافت می‌کنند
    - کاربران می‌توانند مقدار را تنظیم کرده و سپس حواله ایجاد کنند
- **Document Delete Views**: کلاس پایه `DocumentDeleteViewBase` و کلاس‌های مشتق آن (`ReceiptTemporaryDeleteView`, `ReceiptPermanentDeleteView`, `ReceiptConsignmentDeleteView`, `IssuePermanentDeleteView`, `IssueConsumptionDeleteView`, `IssueConsignmentDeleteView`, `StocktakingDeficitDeleteView`, `StocktakingSurplusDeleteView`, `StocktakingRecordDeleteView`) برای حذف اسناد با بررسی دسترسی (`DELETE_OWN` و `DELETE_OTHER`) و محافظت از اسناد قفل‌شده. دکمه‌های حذف در لیست‌ها به صورت شرطی بر اساس دسترسی کاربر نمایش داده می‌شوند.

## templates

- `inventory/item_form.html`: تمپلیت اختصاصی برای تعریف/ویرایش کالا که علاوه بر فیلدهای اصلی، فرم‌ست تبدیل واحد را نمایش می‌دهد.
- `inventory/item_serials.html`: نمای جدولی سریال‌ها به همراه فرم فیلتر (کد رسید، کد کالا، کد سریال، وضعیت) و برچسب‌های وضعیت.
- `inventory/receipt_form.html`: قالب پایه‌ی جدید برای فرم رسیدها و حواله‌ها که بخش‌های اطلاعات سند، سربرگ وضعیت، و اسکریپت جاوااسکریپت جهت به‌روزرسانی پویا‌ی واحد را فراهم می‌کند. این قالب اکنون از **فرم‌ست ردیف‌ها** پشتیبانی می‌کند و برای هر ردیف که کالای آن `has_lot_tracking=1` دارد، دکمه‌های «Manage Serials» یا «Assign Serials» را نمایش می‌دهد.
- `inventory/issue_serial_assignment.html`: قالب اختصاصی برای انتخاب سریال‌های یک ردیف حواله. این صفحه لیست سریال‌های موجود را به صورت checkbox نمایش می‌دهد و کاربر می‌تواند تعداد مورد نیاز را انتخاب کند.
- `inventory/receipt_serial_assignment.html`: قالب اختصاصی برای مدیریت سریال‌های یک ردیف رسید. این صفحه امکان مشاهده و تولید سریال‌ها را فراهم می‌کند.
- `receipt_temporary.html`, `receipt_permanent.html`, `receipt_consignment.html`: صفحات لیست رسیدها که به مسیرهای ایجاد/ویرایش داخلی متصل شده‌اند و پیام‌های خالی/آمار را بر اساس نوع سند نمایش می‌دهند. تاریخ‌های سند با template tag `jalali_date` به صورت Jalali نمایش داده می‌شوند.
- `purchase_requests.html`: صفحه لیست درخواست‌های خرید که دکمه‌های ایجاد رسید (Temporary, Permanent, Consignment) را برای درخواست‌های تأیید شده نمایش می‌دهد.
- `warehouse_requests.html`: صفحه لیست درخواست‌های انبار که دکمه‌های ایجاد حواله (Permanent, Consumption, Consignment) را برای درخواست‌های تأیید شده نمایش می‌دهد.
- `create_receipt_from_purchase_request.html`: صفحه واسط انتخاب خطوط و مقدار برای ایجاد رسید از درخواست خرید.
- `create_issue_from_warehouse_request.html`: صفحه واسط انتخاب مقدار برای ایجاد حواله از درخواست انبار.
- `inventory/stocktaking_form.html`: قالب مشترک فرم‌های شمارش موجودی به همراه اسکریپت‌های پویا برای به‌روزرسانی واحد و انبار مجاز بر اساس انتخاب کالا.
- `inventory/receipt_form.html`: قالب پایه برای فرم‌های رسید و حواله که شامل JavaScript برای به‌روزرسانی پویای dropdown های واحد و انبار بر اساس انتخاب کالا است. تابع `updateUnitChoices()` واحدها را به‌روزرسانی می‌کند و تابع `updateWarehouseChoices()` انبارهای مجاز را به‌روزرسانی می‌کند.
- `stocktaking_deficit.html`, `stocktaking_surplus.html`, `stocktaking_records.html`: صفحات لیست سندهای شمارش که اکنون دکمه «ایجاد» و لینک ویرایش/حذف/مشاهده به ویوهای جدید دارند و وضعیت قفل سند را نمایش می‌دهند. دکمه‌های حذف به صورت شرطی بر اساس دسترسی کاربر نمایش داده می‌شوند.
- `*_confirm_delete.html`: تمپلیت‌های تأیید حذف برای تمام انواع اسناد (رسیدها، حواله‌ها، شمارش موجودی) که جزئیات سند را نمایش داده و از کاربر تأیید می‌گیرند.

## urls.py

- مسیرهای جدید برای کالا: `/inventory/items/create/`, `/inventory/items/<pk>/edit/`, `/inventory/items/<pk>/delete/`
- مسیر مشاهده سریال‌ها: `/inventory/item-serials/` که به ویوی `ItemSerialListView` متصل است و فقط در صورت داشتن مجوز مرتبط در منوی کالا نمایش داده می‌شود.
- مسیرهای مخصوص رسیدها: `/inventory/receipts/<type>/create|<pk>/edit/` که به ویوهای اختصاصی متصل شده‌اند.
- مسیرهای مدیریت سریال ردیف‌ها:
  - `/inventory/receipts/permanent/<pk>/lines/<line_id>/serials/` برای مدیریت سریال‌های ردیف رسید دائم
  - `/inventory/receipts/consignment/<pk>/lines/<line_id>/serials/` برای مدیریت سریال‌های ردیف رسید امانی
  - `/inventory/issues/permanent/<pk>/lines/<line_id>/serials/` برای اختصاص سریال‌های ردیف حواله دائم
  - `/inventory/issues/consumption/<pk>/lines/<line_id>/serials/` برای اختصاص سریال‌های ردیف حواله مصرفی
  - `/inventory/issues/consignment/<pk>/lines/<line_id>/serials/` برای اختصاص سریال‌های ردیف حواله امانی
- مسیرهای مربوط به تأمین‌کنندگان و دسته‌بندی‌های تأمین‌کننده نیز کامل شده‌اند.
- مسیرهای درخواست‌های خرید: `/inventory/purchase-requests/` برای لیست، `/inventory/purchase-requests/create/` برای ایجاد، `/inventory/purchase-requests/<pk>/edit/` برای ویرایش، `/inventory/purchase-requests/<pk>/approve/` برای تأیید
  - مسیرهای ایجاد رسید از درخواست خرید:
    - `/inventory/purchase-requests/<pk>/create-temporary-receipt/` برای صفحه انتخاب خطوط و ایجاد رسید موقت
    - `/inventory/purchase-requests/<pk>/create-permanent-receipt/` برای صفحه انتخاب خطوط و ایجاد رسید دائم
    - `/inventory/purchase-requests/<pk>/create-consignment-receipt/` برای صفحه انتخاب خطوط و ایجاد رسید امانی
- مسیرهای درخواست‌های انبار: `/inventory/warehouse-requests/` برای لیست، `/inventory/warehouse-requests/create/` برای ایجاد، `/inventory/warehouse-requests/<pk>/edit/` برای ویرایش، `/inventory/warehouse-requests/<pk>/approve/` برای تأیید
  - مسیرهای ایجاد حواله از درخواست انبار:
    - `/inventory/warehouse-requests/<pk>/create-permanent-issue/` برای صفحه انتخاب مقدار و ایجاد حواله دائم
    - `/inventory/warehouse-requests/<pk>/create-consumption-issue/` برای صفحه انتخاب مقدار و ایجاد حواله مصرف
    - `/inventory/warehouse-requests/<pk>/create-consignment-issue/` برای صفحه انتخاب مقدار و ایجاد حواله امانی
- مسیرهای شمارش موجودی: `/inventory/stocktaking/deficit|surplus|records/(create|<pk>/edit/)` به همراه مسیرهای قفل، همگی به ویوهای اختصاصی جدید متصل هستند.
- مسیرهای حذف اسناد:
  - `/inventory/receipts/temporary/<pk>/delete/` برای حذف رسید موقت
  - `/inventory/receipts/permanent/<pk>/delete/` برای حذف رسید دائم
  - `/inventory/receipts/consignment/<pk>/delete/` برای حذف رسید امانی
  - `/inventory/issues/permanent/<pk>/delete/` برای حذف حواله دائم
  - `/inventory/issues/consumption/<pk>/delete/` برای حذف حواله مصرف
  - `/inventory/issues/consignment/<pk>/delete/` برای حذف حواله امانی
  - `/inventory/stocktaking/deficit/<pk>/delete/` برای حذف سند کسری
  - `/inventory/stocktaking/surplus/<pk>/delete/` برای حذف سند مازاد
  - `/inventory/stocktaking/records/<pk>/delete/` برای حذف سند شمارش موجودی

## forms.py

- علاوه بر فرم‌های قبلی، مجموعه‌ی زیر فرم‌ها برای سندهای انبار پیاده‌سازی شده‌اند:
  - **فرم‌های سربرگ سند**: `ReceiptTemporaryForm`, `ReceiptPermanentForm`, `ReceiptConsignmentForm`, `IssuePermanentForm`, `IssueConsumptionForm`, `IssueConsignmentForm` که مسئول تولید خودکار کد/تاریخ سند هستند، فیلد وضعیت را پنهان می‌کنند و فقط اطلاعات سربرگ سند را مدیریت می‌کنند.
  - **فرم‌های ردیف**: `IssuePermanentLineForm`, `IssueConsumptionLineForm`, `IssueConsignmentLineForm`, `ReceiptPermanentLineForm`, `ReceiptConsignmentLineForm` که فیلدهای هر ردیف (کالا، انبار، مقدار، واحد، قیمت و غیره) را مدیریت می‌کنند:
    - **`IssuePermanentLineForm`**: فیلد `destination_type` به صورت اختیاری واحد کاری (`CompanyUnit`) را می‌پذیرد. این فیلد از `WorkLine` به `CompanyUnit` تغییر یافته است.
    - **`IssueConsumptionLineForm`**: فیلد `destination_type_choice` امکان انتخاب بین واحد کاری (`company_unit`) یا خط کاری (`work_line`) را فراهم می‌کند. فیلدهای `destination_company_unit` و `destination_work_line` به صورت پویا نمایش داده می‌شوند. **نکته**: `WorkLine` از ماژول `production` استفاده می‌شود (اختیاری - فقط در صورت نصب ماژول production).
    - **`IssueConsignmentLineForm`**: فیلد `destination_type` به صورت اختیاری واحد کاری (`CompanyUnit`) را می‌پذیرد. این فیلد از `WorkLine` به `CompanyUnit` تغییر یافته است.
    - **اعتبارسنجی موجودی**: تمام فرم‌های ردیف حواله (`IssuePermanentLineForm`, `IssueConsumptionLineForm`, `IssueConsignmentLineForm`) اکنون قبل از ذخیره، موجودی فعلی کالا در انبار انتخاب شده را بررسی می‌کنند. در صورت ناکافی بودن موجودی، خطا نمایش داده می‌شود. در حالت ویرایش، مقدار قبلی به موجودی اضافه می‌شود تا امکان تغییر مقدار وجود داشته باشد.
  - **فرم‌ست‌های ردیف**: `IssuePermanentLineFormSet`, `IssueConsumptionLineFormSet`, `IssueConsignmentLineFormSet`, `ReceiptPermanentLineFormSet`, `ReceiptConsignmentLineFormSet` که چندین ردیف را در یک فرم مدیریت می‌کنند.
  - **فرم اختصاص سریال**: `IssueLineSerialAssignmentForm` که برای انتخاب سریال‌های یک ردیف حواله استفاده می‌شود و لیست سریال‌های موجود را به صورت checkbox نمایش می‌دهد.
  - برای کالاهای دارای سریال (lot tracking)، فرم‌های ردیف بررسی می‌کنند که مقدار پس از تبدیل واحد دقیقاً عدد صحیح باشد؛ در غیر این صورت پیام خطا نشان داده می‌شود و ذخیره انجام نمی‌شود.
  - منطق داخلی فرم‌ها از گراف تبدیل واحد (`ItemUnit`) برای محاسبه‌ی ضرایب استفاده می‌کند تا قیمت‌های واردشده با واحد جایگزین به قیمت واحد اصلی تبدیل شود.
  - `BaseLineFormSet`: کلاس پایه برای فرم‌ست‌های ردیف که `company_id` را به درستی به فرم‌های داخلی منتقل می‌کند و متد `_update_destination_type_queryset()` را برای به‌روزرسانی queryset واحدهای کاری فراخوانی می‌کند.
- فرم‌های جدید `StocktakingDeficitForm`, `StocktakingSurplusForm`, `StocktakingRecordForm` کد سند را با پیشوند `STD/STS/STR` تولید کرده، واحدهای مجاز کالا، انبارهای مجاز و فیلدهای JSON مخفی (متادیتا/مستندات) را مدیریت می‌کنند و اختلاف مقدار/ارزش را به‌صورت خودکار محاسبه می‌کنند.
- `ItemForm`, `ItemUnitForm` و `ItemUnitFormSet` همچنان برای مدیریت کالا و تبدیل واحدهای آن استفاده می‌شوند و `ItemForm` اکنون فیلد چندانتخابی «انبارهای مجاز» دارد که بعد از ذخیره، رکوردهای `ItemWarehouse` را ایجاد/به‌روزرسانی و اولین انتخاب را به عنوان `is_primary=1` تنظیم می‌کند.
- **Validation انبارهای مجاز**: همه فرم‌های رسید و حواله (`ReceiptLineBaseForm`, `IssueLineBaseForm`) اکنون validation انبارهای مجاز را اعمال می‌کنند. اگر کالا انبار مجاز نداشته باشد، خطا داده می‌شود. اگر انبار انتخاب شده در لیست انبارهای مجاز نباشد، خطا داده می‌شود. این validation در سمت سرور (Python) و سمت کلاینت (JavaScript) اعمال می‌شود.
- **تاریخ‌های Jalali**: همه فرم‌های سند از `JalaliDateField` و `JalaliDateInput` استفاده می‌کنند که تاریخ‌ها را به صورت Jalali نمایش می‌دهند اما در دیتابیس به صورت Gregorian ذخیره می‌کنند. Template tags `jalali_tags` برای نمایش تاریخ‌ها در templates استفاده می‌شوند.

## admin.py

Registers all models with meaningful list displays, filters, and search fields to expedite data entry and verification in the admin panel. (با وجود رابط‌های اختصاصی برای کالا و تأمین‌کننده، ثبت‌های ادمین نیز فعال و قابل استفاده هستند.)

## migrations/
- `0001_initial.py`: creates every table outlined in `inventory_module_db_design_plan.md`. Whenever model changes occur, generate new migrations so the schema stays aligned with the design.

## apps.py
- No custom logic yet; use it as the entry point if signals or ready-time configuration are introduced later.

## tests.py

Provides unit tests that:
- Confirm `Item` auto-generates codes/batches.
- Validate `PurchaseRequest` caches item and requester codes.
- Confirm receipts populate cached references.
- Ensure `ItemLot` generates sequential lot codes linked to receipt documents.
- Add coverage for serial lifecycle (receipt generation, reservation on issues, finalisation on lock).

Executed via `python manage.py test inventory`.

## management/commands/

### cleanup_test_receipts.py

**Purpose**: Management command for cleaning up test data or inspecting receipt data.

**Command Name**: `cleanup_test_receipts`

**Usage**:
```bash
# Delete all test receipts and their lines
python manage.py cleanup_test_receipts

# Show receipt data instead of deleting
python manage.py cleanup_test_receipts --show
```

**Options**:
- `--show`: Display receipt data instead of deleting (useful for debugging)

**What It Does**:

1. **Delete Mode** (default):
   - Deletes all `ReceiptPermanentLine` records
   - Deletes all `ReceiptPermanent` records
   - Shows success message with counts

2. **Show Mode** (`--show` flag):
   - Displays recent receipts (last 20) with their details
   - Shows receipt lines (last 30) with item and quantity information
   - Shows recent receipts with their associated lines
   - Useful for debugging data issues

**Example Output** (show mode):
```
================================================================================
RECEIPTPERMANENT TABLE
================================================================================
Total receipts: 150

ID: 123
  Code: PRM-202511-000001
  Date: 2025-11-15
  Company ID: 1
  Created By: 5
  Lines Count: 3

================================================================================
RECEIPTPERMANENTLINE TABLE
================================================================================
Total lines: 450

ID: 456
  Receipt ID: 123
  Receipt Code: PRM-202511-000001
  Item ID: 789
  Item Name: Sample Item
  Quantity: 10.000000
  Unit: EA
  Entered Quantity: 10.000000
  Entered Unit: EA
  Warehouse ID: 1
```

**Use Cases**:
- Clean up test data after development/testing
- Inspect receipt data structure
- Debug data integrity issues
- Verify line relationships

**Warning**: The delete mode permanently removes all receipt data. Use with caution in production!

---

## views/base.py

**Purpose**: Base views and mixins for inventory module that provide common functionality.

### Base Classes

#### `InventoryBaseView`

**Type**: `LoginRequiredMixin` subclass

**Purpose**: Base view with common context for all inventory views.

**Features**:
- Automatic company filtering via `get_queryset()`
- Adds `active_module = 'inventory'` to context
- Helper method for delete permission checks

**Methods**:
- `get_queryset()`: Filters queryset by `active_company_id` from session
- `get_context_data(**kwargs)`: Adds `active_module` to context
- `add_delete_permissions_to_context(context, feature_code)`: Adds `can_delete_own` and `can_delete_other` to context

**Usage**:
```python
class ItemListView(InventoryBaseView, ListView):
    model = Item
    # Automatically filters by active company
    # Context includes active_module='inventory'
```

---

#### `DocumentLockProtectedMixin`

**Purpose**: Prevents modifying locked inventory documents.

**Features**:
- Blocks GET, POST, PUT, PATCH, DELETE methods on locked documents
- Optional owner check (only creator can edit)
- Customizable error messages and redirect URLs

**Attributes**:
- `lock_redirect_url_name`: URL name to redirect to when document is locked
- `lock_error_message`: Error message for locked documents
- `owner_field`: Field name for document owner (default: `'created_by'`)
- `owner_error_message`: Error message for owner mismatch
- `protected_methods`: List of HTTP methods to protect (default: all)

**Usage**:
```python
class ReceiptUpdateView(DocumentLockProtectedMixin, UpdateView):
    model = ReceiptPermanent
    lock_redirect_url_name = 'inventory:receipt_permanent_list'
    
    # Automatically blocks editing if is_locked=1
    # Redirects to list view with error message
```

---

#### `DocumentLockView`

**Type**: `LoginRequiredMixin, View`

**Purpose**: Generic view to lock inventory documents.

**Features**:
- Sets `is_locked = 1` on document
- Updates `locked_at` and `locked_by` fields
- Hooks for before/after lock actions

**Attributes**:
- `model`: Model class to lock
- `success_url_name`: URL name to redirect to after locking
- `success_message`: Success message
- `already_locked_message`: Message if document already locked
- `lock_field`: Field name for lock status (default: `'is_locked'`)

**Methods**:
- `before_lock(obj, request)`: Hook executed before locking (return `False` to cancel)
- `after_lock(obj, request)`: Hook executed after locking

**Usage**:
```python
class ReceiptLockView(DocumentLockView):
    model = ReceiptPermanent
    success_url_name = 'inventory:receipt_permanent_list'
    
    def after_lock(self, obj, request):
        # Generate serials when receipt is locked
        generate_receipt_serials(obj, user=request.user)
```

---

### Mixins

#### `LineFormsetMixin`

**Purpose**: Handles line formset creation and saving for multi-line documents.

**Features**:
- Automatic formset building from request data
- Line formset saving with document association
- Serial assignment handling for issue lines

**Attributes**:
- `formset_class`: Formset class to use (must be set)
- `formset_prefix`: Prefix for formset fields (default: `'lines'`)

**Methods**:
- `build_line_formset(data, instance, company_id)`: Builds formset with given parameters
- `get_line_formset(data)`: Gets formset for current request
- `get_context_data(**kwargs)`: Adds `lines_formset` to context
- `form_invalid(form)`: Handles invalid form with formset
- `_save_line_formset(formset)`: Saves formset instances and handles serials

**Usage**:
```python
class ReceiptCreateView(LineFormsetMixin, CreateView):
    model = ReceiptPermanent
    formset_class = ReceiptPermanentLineFormSet
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self._save_line_formset(self.get_context_data()['lines_formset'])
        return response
```

**Serial Handling**:
- Automatically assigns serials to issue lines from POST data
- Reserves serials when issue line is saved
- Filters serials by item, warehouse, and status

---

#### `ItemUnitFormsetMixin`

**Purpose**: Handles item unit formset creation and saving.

**Features**:
- Automatic unit formset building
- Unit code generation
- Item-warehouse relationship syncing

**Attributes**:
- `formset_prefix`: Prefix for formset fields (default: `'units'`)

**Methods**:
- `build_unit_formset(data, instance, company_id)`: Builds unit formset
- `get_unit_formset(data)`: Gets unit formset for current request
- `get_context_data(**kwargs)`: Adds `units_formset` and `units_formset_empty` to context
- `form_invalid(form)`: Handles invalid form with unit formset
- `_generate_unit_code(company)`: Generates sequential unit code
- `_save_unit_formset(formset)`: Saves unit formset instances
- `_sync_item_warehouses(item, warehouses, user)`: Syncs item-warehouse relationships
- `_get_ordered_warehouses(form)`: Gets warehouses in selection order

**Usage**:
```python
class ItemCreateView(ItemUnitFormsetMixin, CreateView):
    model = Item
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self._save_unit_formset(self.get_context_data()['units_formset'])
        warehouses = self._get_ordered_warehouses(form)
        self._sync_item_warehouses(self.object, warehouses, self.request.user)
        return response
```

---

## views/api.py

**Purpose**: JSON API endpoints for dynamic form interactions and data filtering.

**All endpoints require**:
- User authentication (`@login_required`)
- Active company in session (`active_company_id`)

**Endpoints**:
- `get_item_allowed_units`: Get allowed units for an item
- `get_filtered_categories`: Get categories filtered by type
- `get_filtered_subcategories`: Get subcategories filtered by category
- `get_filtered_items`: Get items filtered by type/category/subcategory
- `get_item_units`: Get detailed unit information for an item
- `get_item_allowed_warehouses`: Get allowed warehouses for an item
- `get_temporary_receipt_data`: Get temporary receipt data for auto-filling
- `get_item_available_serials`: Get available serials for an item in warehouse
- `update_serial_secondary_code`: Update secondary serial code
- `get_warehouse_work_lines`: Get work lines for a warehouse

**See**: [API Documentation](../docs/API_DOCUMENTATION.md) for complete endpoint documentation.

---

## Future Work / Notes
- When adding new document types or extending workflows (e.g., returns), update both the models and admin registration and reflect changes in the design plan markdown.
- Consider adding signals/services for stock level updates when production or QC modules consume items.
- Add API serializers/views (e.g., DRF) as part of future integration tasks; document them here once they exist.

