# inventory/forms/ - Forms Documentation

این پوشه شامل تمام form classes و formsets ماژول inventory است.

## فایل‌ها

### base.py
- **README**: [README_BASE.md](README_BASE.md)
- **توضیح**: کلاس‌های پایه و helper functions مشترک برای forms

### master_data.py
- **README**: [README_MASTER_DATA.md](README_MASTER_DATA.md)
- **توضیح**: Forms برای داده‌های اصلی (Item Types, Categories, Items, Warehouses, Suppliers)

### receipt.py
- **README**: [README_RECEIPT.md](README_RECEIPT.md)
- **توضیح**: Forms برای رسیدها (Temporary, Permanent, Consignment) و line forms

### issue.py
- **README**: [README_ISSUE.md](README_ISSUE.md)
- **توضیح**: Forms برای حواله‌ها (Permanent, Consumption, Consignment) و line forms

### request.py
- **README**: [README_REQUEST.md](README_REQUEST.md)
- **توضیح**: Forms برای درخواست‌ها (Purchase Requests, Warehouse Requests) و line forms

### stocktaking.py
- **README**: [README_STOCKTAKING.md](README_STOCKTAKING.md)
- **توضیح**: Forms برای شمارش انبار (Deficit, Surplus, Record)

---

## الگوهای مشترک

تمام forms از الگوهای مشترک زیر پیروی می‌کنند:

1. **Company Scoping**: تمام forms به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
2. **Validation**: تمام forms validation مناسب دارند
3. **Multi-line Support**: Formsets برای اسناد multi-line استفاده می‌شوند
4. **Jalali Dates**: تمام forms از `JalaliDateField` و `JalaliDateInput` استفاده می‌کنند
5. **Unit Conversion**: Forms از گراف تبدیل واحد (`ItemUnit`) برای محاسبه ضرایب استفاده می‌کنند

---

## مستندات کامل

برای جزئیات کامل هر فایل، به README مربوطه مراجعه کنید.

