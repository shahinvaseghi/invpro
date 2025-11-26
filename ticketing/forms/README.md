# ticketing/forms/ - Forms Documentation

این پوشه شامل تمام form classes ماژول ticketing است.

## فایل‌ها

### base.py
- **توضیح**: کلاس‌های پایه و helper functions مشترک برای forms

### tickets.py
- **Forms**: TicketForm
- **توضیح**: Forms برای تیکت‌ها

### templates.py
- **Forms**: TicketTemplateForm
- **توضیح**: Forms برای قالب‌های تیکت

### categories.py
- **Forms**: TicketCategoryForm
- **توضیح**: Forms برای دسته‌بندی تیکت‌ها

---

## الگوهای مشترک

تمام forms از الگوهای مشترک زیر پیروی می‌کنند:

1. **Company Scoping**: تمام forms به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
2. **Dynamic Fields**: Forms از field settings برای ایجاد فیلدهای دینامیک استفاده می‌کنند
3. **Validation**: تمام forms validation مناسب دارند

---

## مستندات کامل

برای جزئیات کامل هر form، به کد منبع مراجعه کنید.

