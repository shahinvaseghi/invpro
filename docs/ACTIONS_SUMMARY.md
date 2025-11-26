# خلاصه Actions موجود در Entity Reference System

این فایل خلاصه کاملی از تمام actions تعریف شده برای هر section را نمایش می‌دهد.

## تعداد کل Actions: 50

---

## 1. Users (010301) - 5 Actions

1. `show` - مشاهده کاربران (پارامتر: `gp`)
2. `showown` - مشاهده پروفایل خود
3. `add` - ایجاد کاربر جدید
4. `edit` - ویرایش کاربر (پارامتر: `id`, `code`)
5. `delete` - حذف کاربر (پارامتر: `id`, `code`)

---

## 2. Purchase Requests (020400) - 5 Actions

1. `show` - مشاهده درخواست‌های خرید
2. `add` - ایجاد درخواست خرید جدید
3. `edit` - ویرایش درخواست خرید (پارامتر: `id`, `code`)
4. `approve` - تایید درخواست خرید (پارامتر: `id`, `code`)
5. `create_receipt_from` - ایجاد رسید از درخواست تایید شده (پارامتر: `id`, `type`)

---

## 3. Warehouse Requests (020500) - 5 Actions

1. `show` - مشاهده درخواست‌های انبار
2. `add` - ایجاد درخواست انبار جدید
3. `edit` - ویرایش درخواست انبار (پارامتر: `id`, `code`)
4. `approve` - تایید درخواست انبار (پارامتر: `id`, `code`)
5. `create_issue_from` - ایجاد حواله از درخواست تایید شده (پارامتر: `id`, `type`)

---

## 4. Receipts - Temporary (020601) - 6 Actions

1. `show` - مشاهده رسیدهای موقت
2. `add` - ایجاد رسید موقت جدید
3. `edit` - ویرایش رسید موقت (پارامتر: `id`, `code`)
4. `delete` - حذف رسید موقت (پارامتر: `id`, `code`)
5. `lock` - قفل کردن رسید موقت (پارامتر: `id`, `code`)
6. `send_to_qc` - ارسال به QC برای بازرسی (پارامتر: `id`, `code`)

---

## 5. Receipts - Permanent (020602) - 5 Actions

1. `show` - مشاهده رسیدهای دائم
2. `add` - ایجاد رسید دائم جدید
3. `edit` - ویرایش رسید دائم (پارامتر: `id`, `code`)
4. `delete` - حذف رسید دائم (پارامتر: `id`, `code`)
5. `lock` - قفل کردن رسید دائم (پارامتر: `id`, `code`)

---

## 6. Receipts - Consignment (020603) - 5 Actions

1. `show` - مشاهده رسیدهای امانی
2. `add` - ایجاد رسید امانی جدید
3. `edit` - ویرایش رسید امانی (پارامتر: `id`, `code`)
4. `delete` - حذف رسید امانی (پارامتر: `id`, `code`)
5. `lock` - قفل کردن رسید امانی (پارامتر: `id`, `code`)

---

## 7. Issues - Permanent (020701) - 5 Actions

1. `show` - مشاهده حواله‌های دائم
2. `add` - ایجاد حواله دائم جدید
3. `edit` - ویرایش حواله دائم (پارامتر: `id`, `code`)
4. `delete` - حذف حواله دائم (پارامتر: `id`, `code`)
5. `lock` - قفل کردن حواله دائم (پارامتر: `id`, `code`)

---

## 8. Issues - Consumption (020702) - 5 Actions

1. `show` - مشاهده حواله‌های مصرف
2. `add` - ایجاد حواله مصرف جدید
3. `edit` - ویرایش حواله مصرف (پارامتر: `id`, `code`)
4. `delete` - حذف حواله مصرف (پارامتر: `id`, `code`)
5. `lock` - قفل کردن حواله مصرف (پارامتر: `id`, `code`)

---

## 9. Issues - Consignment (020703) - 5 Actions

1. `show` - مشاهده حواله‌های امانی
2. `add` - ایجاد حواله امانی جدید
3. `edit` - ویرایش حواله امانی (پارامتر: `id`, `code`)
4. `delete` - حذف حواله امانی (پارامتر: `id`, `code`)
5. `lock` - قفل کردن حواله امانی (پارامتر: `id`, `code`)

---

## 10. Inspections (041000) - 4 Actions

1. `show` - مشاهده بازرسی‌ها
2. `showown` - مشاهده بازرسی‌های خود
3. `approve` - تایید بازرسی (پارامتر: `id`, `code`)
4. `reject` - رد بازرسی (پارامتر: `id`, `code`)

---

## Actions بدون پارامتر

- `show` (بدون فیلتر) - 9 sections
- `add` - 10 sections
- `showown` - 2 sections (users, inspections)

## Actions با پارامتر `id` (و `code` اختیاری)

- `edit` - 9 sections
- `delete` - 6 sections
- `lock` - 6 sections
- `approve` - 3 sections (purchase_requests, warehouse_requests, inspections)
- `reject` - 1 section (inspections)
- `send_to_qc` - 1 section (receipt_temporary)

## Actions با پارامترهای خاص

- `show` (users) - پارامتر: `gp=<group_name>`
- `create_receipt_from` - پارامتر: `id`, `type`
- `create_issue_from` - پارامتر: `id`, `type`

---

## Actions نیازمند به افزودن پارامتر `code`:

تمام actions زیر باید پارامتر `code` به عنوان جایگزین `id` داشته باشند:

1. **Users**: `edit`, `delete`
2. **Purchase Requests**: `edit`
3. **Warehouse Requests**: `edit`
4. **Receipts (همه انواع)**: `edit`, `delete`, `lock`, `send_to_qc`
5. **Issues (همه انواع)**: `edit`, `delete`, `lock`

---

## Actions نیازمند به افزودن پارامترهای فیلتر:

تمام `show` actions زیر باید پارامترهای فیلتر استاندارد داشته باشند:

1. **Purchase Requests**: `show`
2. **Warehouse Requests**: `show`
3. **Receipts (همه انواع)**: `show`
4. **Issues (همه انواع)**: `show`
5. **Inspections**: `show`

---

## Sections بدون Actions:

بسیاری از sections هنوز actions ندارند و باید اضافه شوند:

### Inventory Master Data:
- `item_types` (020101)
- `item_categories` (020102)
- `item_subcategories` (020103)
- `warehouses` (020104)
- `items` (020202)
- `supplier_categories` (020301)
- `suppliers` (020302)

### Inventory Stocktaking:
- `stocktaking_deficit` (020801)
- `stocktaking_surplus` (020802)
- `stocktaking_records` (020803)

### Production:
- `personnel` (030000)
- `machines` (030100)
- `work_lines` (030200)
- `bom` (030300)
- `processes` (030400)
- `product_orders` (036000)
- `transfer_requests` (036100)
- `performance_records` (036800)

### Shared:
- `companies` (010000)
- `company_units` (010100)
- `smtp_servers` (010200)
- `groups` (010302)
- `access_levels` (010303)

