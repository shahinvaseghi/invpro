# inventory/forms/ - Forms Documentation

این پوشه شامل تمام form classes و formsets ماژول inventory است.

## فایل‌ها

### base.py
- **توضیح**: کلاس‌های پایه و helper functions مشترک برای forms

### master_data.py
- **Forms**: 
  - ItemTypeForm
  - ItemCategoryForm
  - ItemSubcategoryForm
  - ItemForm
  - WarehouseForm
  - SupplierForm
  - SupplierCategoryForm
- **Formsets**: 
  - ItemUnitFormSet
- **توضیح**: Forms برای داده‌های اصلی (master data)

### receipt.py
- **Forms**: 
  - ReceiptTemporaryForm
  - ReceiptPermanentForm
  - ReceiptConsignmentForm
- **Formsets**: 
  - ReceiptTemporaryLineFormSet
  - ReceiptPermanentLineFormSet
  - ReceiptConsignmentLineFormSet
- **توضیح**: Forms برای رسیدها (temporary, permanent, consignment)

### issue.py
- **Forms**: 
  - IssuePermanentForm
  - IssueConsumptionForm
  - IssueConsignmentForm
- **Formsets**: 
  - IssuePermanentLineFormSet
  - IssueConsumptionLineFormSet
  - IssueConsignmentLineFormSet
- **توضیح**: Forms برای حواله‌ها (permanent, consumption, consignment)

### request.py
- **Forms**: 
  - PurchaseRequestForm
  - WarehouseRequestForm
- **Formsets**: 
  - PurchaseRequestLineFormSet
- **توضیح**: Forms برای درخواست‌ها (purchase, warehouse)

### stocktaking.py
- **Forms**: 
  - StocktakingDeficitForm
  - StocktakingSurplusForm
  - StocktakingRecordForm
- **توضیح**: Forms برای شمارش انبار

---

## الگوهای مشترک

تمام forms از الگوهای مشترک زیر پیروی می‌کنند:

1. **Company Scoping**: تمام forms به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
2. **Dynamic Unit Selection**: Forms با فیلد unit از API برای دریافت واحدهای مجاز استفاده می‌کنند
3. **Validation**: تمام forms validation مناسب دارند
4. **Multi-line Support**: Formsets برای اسناد multi-line استفاده می‌شوند

---

## مستندات کامل

برای جزئیات کامل هر form، به `inventory/README_FORMS.md` مراجعه کنید.

