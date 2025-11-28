# ticketing/views/ - Views Documentation

این پوشه شامل تمام views ماژول ticketing است.

## فایل‌ها

### base.py
- **README**: [README_BASE.md](README_BASE.md)
- **توضیح**: کلاس‌های پایه (TicketingBaseView, TicketLockProtectedMixin)

### tickets.py
- **Views**: TicketListView, TicketCreateView, TicketEditView
- **توضیح**: Views برای مدیریت تیکت‌ها

### templates.py
- **Views**: TicketTemplateListView, TicketTemplateCreateView, TicketTemplateUpdateView, TicketTemplateDeleteView
- **توضیح**: CRUD views برای قالب‌های تیکت

### categories.py
- **Views**: TicketCategoryListView, TicketCategoryCreateView, TicketCategoryUpdateView, TicketCategoryDeleteView
- **توضیح**: CRUD views برای دسته‌بندی تیکت‌ها

### subcategories.py
- **Views**: TicketSubcategoryListView, TicketSubcategoryCreateView, TicketSubcategoryUpdateView, TicketSubcategoryDeleteView
- **توضیح**: CRUD views برای زیردسته‌بندی تیکت‌ها

### debug.py
- **README**: [README_DEBUG.md](README_DEBUG.md)
- **توضیح**: Views برای debugging (در development)

### entity_reference.py
- **توضیح**: Views مربوط به Entity Reference System

### placeholders.py
- **Views**: TicketRespondView, TemplateCreateView, CategoriesView, AutoResponseView
- **توضیح**: Views placeholder برای آینده

---

## الگوهای مشترک

تمام views از الگوهای مشترک زیر پیروی می‌کنند:

1. **Base Class**: از `TicketingBaseView` استفاده می‌کنند
2. **Company Filtering**: به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
3. **Lock Protection**: Update views از `TicketLockProtectedMixin` استفاده می‌کنند
4. **Permission Checking**: از `FeaturePermissionRequiredMixin` برای بررسی مجوزها استفاده می‌کنند

---

## مستندات کامل

برای جزئیات کامل هر view، به کد منبع مراجعه کنید.

