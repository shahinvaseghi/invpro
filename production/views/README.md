# production/views/ - Views Documentation

این پوشه شامل تمام views ماژول production است.

## فایل‌ها

### base.py
- **توضیح**: کلاس‌های پایه (در `shared/views/base.py` استفاده می‌شود)

### bom.py
- **Views**: BOMListView, BOMCreateView, BOMUpdateView, BOMDeleteView
- **توضیح**: CRUD views برای Bill of Materials (BOM)

### process.py
- **Views**: ProcessListView, ProcessCreateView, ProcessUpdateView, ProcessDeleteView
- **توضیح**: CRUD views برای فرآیندهای تولید

### product_order.py
- **Views**: ProductOrderListView, ProductOrderCreateView, ProductOrderUpdateView, ProductOrderDeleteView
- **توضیح**: CRUD views برای سفارشات تولید

### work_line.py
- **Views**: WorkLineListView, WorkLineCreateView, WorkLineUpdateView, WorkLineDeleteView
- **توضیح**: CRUD views برای خطوط کاری

### personnel.py
- **Views**: PersonnelListView, PersonCreateView, PersonUpdateView, PersonDeleteView
- **توضیح**: CRUD views برای پرسنل

### machine.py
- **Views**: MachineListView, MachineCreateView, MachineUpdateView, MachineDeleteView
- **توضیح**: CRUD views برای ماشین‌آلات

### transfer_to_line.py
- **Views**: TransferToLineListView, TransferToLineCreateView, TransferToLineUpdateView, TransferToLineDeleteView, TransferToLineApproveView, TransferToLineRejectView
- **توضیح**: Views برای انتقال به خط تولید با workflow تایید/رد

### performance_record.py
- **Views**: PerformanceRecordListView, PerformanceRecordCreateView, PerformanceRecordUpdateView, PerformanceRecordDeleteView, PerformanceRecordApproveView, PerformanceRecordRejectView, PerformanceRecordCreateReceiptView
- **توضیح**: Views برای ثبت عملکرد تولید با workflow تایید/رد و ایجاد رسید

### placeholders.py
- **Views**: TransferToLineRequestListView, PerformanceRecordListView (placeholder)
- **توضیح**: Views placeholder برای آینده

---

## الگوهای مشترک

تمام views از الگوهای مشترک زیر پیروی می‌کنند:

1. **Permission Checking**: از `FeaturePermissionRequiredMixin` استفاده می‌کنند
2. **Company Filtering**: به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
3. **Approval Workflow**: برخی views (TransferToLine, PerformanceRecord) workflow تایید/رد دارند

---

## مستندات کامل

برای جزئیات کامل هر view، به کد منبع مراجعه کنید.

