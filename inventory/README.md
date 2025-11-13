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
  - `Warehouse`, `WorkLine`: physical storage and work areas, each scoped by company.

- **Item Definitions**
  - `Item`: central product/part definition. Automatically generates `item_code`, `sequence_segment`, and `batch_number` based on type/category/subcategory and current month.
  - `ItemSpec`: JSON specification per item; caches `item_code`.
  - `ItemUnit`: unit conversions; caches `item_code`.
  - `ItemWarehouse`: mapping between items and warehouses (primary flag support).
  - `ItemSubstitute`: defines substitute relationships and quantities between items; caches both source and target codes.
  - `ItemLot`: traceability record for lot-controlled items; generates `LOT-MMYY-XXXXXX` format codes.
  - `ItemSerial`: per-unit tracking for serialised assets (current status, location, linked documents) with automatic creation when receipts are locked.
  - `ItemSerialHistory`: immutable audit log documenting every serial event (reservation, release, issue, consumption, return).

- **Supplier Relations**
  - `Supplier`: supplier master data.
  - `SupplierCategory`, `SupplierSubcategory`, `SupplierItem`: link suppliers to categories, subcategories, and specific items with metadata such as MOQ, lead time, and primary flags.

- **Requests & Receipts**
  - `PurchaseRequest`: captures item requests with priority, status workflow, and references.
  - `ReceiptTemporary`: intake staging record (awaiting QC); caches item/warehouse codes and supplier code, tracks QC approval.
  - `ReceiptPermanent`: finalized receipt (optionally linked to temporary receipt and purchase request).
  - `ReceiptConsignment`: consignment handling with ownership status, conversion links, and optional temporary receipt reference.

- **Issues**
  - `IssuePermanent`, `IssueConsumption`, `IssueConsignment`: outbound document variants برای حالات دائم، مصرفی و امانی. علاوه بر ذخیره کد کالا/انبار و وضعیت ارسال، امکان ثبت واحد سازمانی مقصد و برای حالت مصرف، خط تولید مربوطه نیز فراهم شده است تا رهگیری مقصد مواد دقیق‌تر انجام شود. این مدل‌ها اکنون با `ItemSerial` ادغام شده‌اند: زمان ایجاد یا ویرایش، سریال‌های انتخاب‌شده رزرو می‌شوند و با قفل سند وضعیتشان به `issued` یا `consumed` تغییر پیدا می‌کند.

- **Stocktaking**
  - `StocktakingDeficit`, `StocktakingSurplus`: adjustment documents capturing counted vs expected quantities, valuation, and posting info.
  - `StocktakingRecord`: final confirmation for a stocktaking session with references to variance documents.

Each model enforces unique constraints tailored to multi-company setups and uses `save()` overrides to populate cached fields or generate codes.

## views.py

مهم‌ترین ویوهای موجود:

- `ItemListView`, `ItemCreateView`, `ItemUpdateView`, `ItemDeleteView`: رابط کامل CRUD برای کالاها در رابط کاربری اصلی. `ItemCreateView` و `ItemUpdateView` علاوه بر فرم کالا، فرم‌ست واحدهای ثانویه (`ItemUnit`) را نیز پشتیبانی می‌کنند.
- در همان ویوها انتخاب «انبارهای مجاز» نیز مدیریت می‌شود؛ بعد از ذخیره، جدول `ItemWarehouse` بر اساس انتخاب‌های کاربر همگام‌سازی و اولین انبار به عنوان انبار اصلی علامت‌گذاری می‌شود.
- `SupplierCategoryCreateView`, `SupplierCreateView` و ویوهای ویرایش/حذف متناظر: فرم‌های اختصاصی برای مدیریت تأمین‌کنندگان و دسته‌بندی‌های آنها (تبدیل از صفحات ادمین به UI داخلی).
- `ReceiptTemporaryCreateView`/`UpdateView`, `ReceiptPermanentCreateView`/`UpdateView`, `ReceiptConsignmentCreateView`/`UpdateView`: فرم‌های اختصاصی برای ثبت رسیدها. این ویوها:
  - کد سند (TMP/PRM/CON-YYYYMM-XXXXXX)، تاریخ سند و وضعیت ابتدایی را به صورت خودکار تولید می‌کنند.
  - واحدهای انتخابی را با فهرست واحد اصلی و تبدیل‌های تعریف‌شده محدود می‌کنند و مقدار/قیمت را قبل از ذخیره به واحد اصلی کالا تبدیل می‌کنند.
  - در حالت ویرایش، سرآیند سند را به شکل فقط خواندنی نمایش می‌دهند.
- `IssuePermanentCreateView`/`UpdateView`, `IssueConsumptionCreateView`/`UpdateView`, `IssueConsignmentCreateView`/`UpdateView`: صفحات اختصاصی برای ایجاد/ویرایش حواله‌ها که امکان انتخاب واحد سازمانی مقصد (و برای حواله مصرف، خط تولید) را فراهم می‌کنند و همان منطق انتخاب واحد کالا را به کار می‌گیرند. دکمه‌ی «قفل» روی سند امکان جلوگیری از ویرایش یا حذف بعد از نهایی‌سازی را می‌دهد.
- `StocktakingDeficitCreateView`/`UpdateView`, `StocktakingSurplusCreateView`/`UpdateView`, `StocktakingRecordCreateView`/`UpdateView`: فرم‌های اختصاصی برای اسناد شمارش موجودی که کد سند (STD/STS/STR-YYYYMM-XXXXXX) را تولید کرده، واحدهای مجاز و انبارهای مجاز را بر اساس تنظیمات کالا محدود می‌کنند و امکان قفل کردن سند را پس از نهایی‌سازی فراهم می‌سازند.

## templates

- `inventory/item_form.html`: تمپلیت اختصاصی برای تعریف/ویرایش کالا که علاوه بر فیلدهای اصلی، فرم‌ست تبدیل واحد را نمایش می‌دهد.
- `inventory/receipt_form.html`: قالب پایه‌ی جدید برای فرم رسیدها که بخش‌های اطلاعات سند، سربرگ وضعیت، و اسکریپت جاوااسکریپت جهت به‌روزرسانی پویا‌ی واحد را فراهم می‌کند.
- `receipt_temporary.html`, `receipt_permanent.html`, `receipt_consignment.html`: صفحات لیست رسیدها که به مسیرهای ایجاد/ویرایش داخلی متصل شده‌اند و پیام‌های خالی/آمار را بر اساس نوع سند نمایش می‌دهند.
- `inventory/stocktaking_form.html`: قالب مشترک فرم‌های شمارش موجودی به همراه اسکریپت‌های پویا برای به‌روزرسانی واحد و انبار مجاز بر اساس انتخاب کالا.
- `stocktaking_deficit.html`, `stocktaking_surplus.html`, `stocktaking_records.html`: صفحات لیست سندهای شمارش که اکنون دکمه «ایجاد» و لینک ویرایش/مشاهده به ویوهای جدید دارند و وضعیت قفل سند را نمایش می‌دهند.

## urls.py

- مسیرهای جدید برای کالا: `/inventory/items/create/`, `/inventory/items/<pk>/edit/`, `/inventory/items/<pk>/delete/`
- مسیرهای مخصوص رسیدها: `/inventory/receipts/<type>/create|<pk>/edit/` که به ویوهای اختصاصی متصل شده‌اند.
- مسیرهای مربوط به تأمین‌کنندگان و دسته‌بندی‌های تأمین‌کننده نیز کامل شده‌اند.
- مسیرهای شمارش موجودی: `/inventory/stocktaking/deficit|surplus|records/(create|<pk>/edit/)` به همراه مسیرهای قفل، همگی به ویوهای اختصاصی جدید متصل هستند.

## forms.py

- علاوه بر فرم‌های قبلی، مجموعه‌ی زیر فرم‌ها برای سندهای انبار پیاده‌سازی شده‌اند:
  - `ReceiptTemporaryForm`, `ReceiptPermanentForm`, `ReceiptConsignmentForm` که مسئول تولید خودکار کد/تاریخ سند هستند، فیلد وضعیت را پنهان می‌کنند، واحدهای مجاز را محدود می‌کنند و مقدار و قیمت را با واحد اصلی کالا همگام می‌سازند.
  - منطق داخلی فرم‌ها از گراف تبدیل واحد (`ItemUnit`) برای محاسبه‌ی ضرایب استفاده می‌کند تا قیمت‌های واردشده با واحد جایگزین به قیمت واحد اصلی تبدیل شود.
- فرم‌های `IssuePermanentForm`, `IssueConsumptionForm`, `IssueConsignmentForm` نیز افزوده شده‌اند که ضمن محدود کردن واحد کالا، انتخاب اختیاری واحد سازمانی و (برای مصرف) خط تولید را ممکن می‌کنند و کد سند را با الگوهای `ISP-`, `ISU-`, `ICN-` تولید می‌کنند. برای کالاهای دارای سریال، این فرم‌ها لیست سریال‌های قابل انتخاب را نمایش می‌دهند، تعداد انتخاب را با مقدار سند تطبیق می‌دهند و سریال‌ها را تا لحظه قفل در وضعیت `reserved` نگه می‌دارند.
- فرم‌های جدید `StocktakingDeficitForm`, `StocktakingSurplusForm`, `StocktakingRecordForm` کد سند را با پیشوند `STD/STS/STR` تولید کرده، واحدهای مجاز کالا، انبارهای مجاز و فیلدهای JSON مخفی (متادیتا/مستندات) را مدیریت می‌کنند و اختلاف مقدار/ارزش را به‌صورت خودکار محاسبه می‌کنند.
- `ItemForm`, `ItemUnitForm` و `ItemUnitFormSet` همچنان برای مدیریت کالا و تبدیل واحدهای آن استفاده می‌شوند و `ItemForm` اکنون فیلد چندانتخابی «انبارهای مجاز» دارد که بعد از ذخیره، رکوردهای `ItemWarehouse` را ایجاد/به‌روزرسانی و اولین انتخاب را به عنوان `is_primary=1` تنظیم می‌کند.

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

## Future Work / Notes
- When adding new document types or extending workflows (e.g., returns), update both the models and admin registration and reflect changes in the design plan markdown.
- Consider adding signals/services for stock level updates when production or QC modules consume items.
- Add API serializers/views (e.g., DRF) as part of future integration tasks; document them here once they exist.

