# production/views/ - Views Documentation

این پوشه شامل تمام views ماژول production است.

## فایل‌ها

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

## Template Migration Status

### ✅ **منتقل شده (23 template) - 100%**
- **BOM**: List ✅, Form ✅, Delete ✅
- **Machine**: List ✅, Form ✅, Delete ✅
- **Performance Record**: List ✅, Form ✅, Delete ✅
- **Personnel**: List ✅, Form ✅, Delete ✅
- **Process**: List ✅, Form ✅, Delete ✅
- **Product Order**: List ✅, Form ✅, Delete ✅
- **Transfer to Line**: List ✅, Form ✅, Delete ✅
- **Work Line**: List ✅, Form ✅, Delete ✅

**پیشرفت کلی: 23 / 23 (100%)** 🎉

تمام template های منتقل شده از generic templates استفاده می‌کنند:
- List templates: `shared/generic/generic_list.html`
- Form templates: `shared/generic/generic_form.html`
- Delete templates: `shared/generic/generic_confirm_delete.html`

برای جزئیات بیشتر، به `docs/TEMPLATE_MIGRATION_CHECKLIST_PRODUCTION.md` مراجعه کنید.

---

## مستندات کامل

برای جزئیات کامل هر view، به کد منبع مراجعه کنید.

