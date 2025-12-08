# production/utils/transfer.py - Transfer Utility Functions

**هدف**: مستندات توابع کمکی برای درخواست‌های Transfer to Line

**وضعیت**: ⏳ **نیاز به تکمیل**

این فایل شامل توابع کمکی زیر است:
- `generate_transfer_code()` - تولید کد متوالی برای transfer
- `get_transferred_materials_for_order()` - دریافت مواد منتقل شده برای یک order
- `get_transferred_operations_for_order()` - دریافت عملیات‌های منتقل شده برای یک order
- `is_full_order_transferred()` - بررسی اینکه آیا تمام مواد BOM برای order منتقل شده‌اند
- `get_available_operations_for_order()` - دریافت لیست عملیات‌های در دسترس برای order
- `select_source_warehouse_by_priority()` - انتخاب انبار منبع بر اساس اولویت و موجودی
- `create_warehouse_transfer_for_transfer_to_line()` - ایجاد سند حواله انبار برای transfer request

---

## ⚠️ نیاز به تکمیل

این فایل README نیاز به تکمیل دارد. لطفاً مستندات کامل را اضافه کنید.
