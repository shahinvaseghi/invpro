# qc/views/ - Views Documentation

این پوشه شامل تمام views ماژول QC است.

## فایل‌ها

### base.py
- **README**: [README_BASE.md](README_BASE.md)
- **توضیح**: کلاس پایه (QCBaseView)

### inspections.py
- **Views**: 
  - TemporaryReceiptQCListView: فهرست رسیدهای موقت در انتظار بازرسی
  - TemporaryReceiptQCApproveView: تایید بازرسی رسید موقت
  - TemporaryReceiptQCRejectView: رد بازرسی رسید موقت
- **توضیح**: Views برای مدیریت بازرسی‌های QC

---

## الگوهای مشترک

تمام views از الگوهای مشترک زیر پیروی می‌کنند:

1. **Base Class**: از `QCBaseView` استفاده می‌کنند
2. **Company Filtering**: به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
3. **Permission Checking**: از `FeaturePermissionRequiredMixin` برای بررسی مجوزها استفاده می‌کنند
4. **Workflow**: Approve/Reject views workflow تایید/رد دارند

---

## مستندات کامل

برای جزئیات کامل هر view، به کد منبع مراجعه کنید.

