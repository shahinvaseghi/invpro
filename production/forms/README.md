# production/forms/ - Forms Documentation

این پوشه شامل تمام form classes ماژول production است.

## فایل‌ها

### bom.py
- **Forms**: BOMForm, BOMMaterialForm
- **Formsets**: BOMMaterialFormSet
- **توضیح**: Forms برای Bill of Materials

### process.py
- **Forms**: ProcessForm, ProcessStepForm
- **Formsets**: ProcessStepFormSet
- **توضیح**: Forms برای فرآیندهای تولید

### product_order.py
- **Forms**: ProductOrderForm
- **توضیح**: Forms برای سفارشات تولید

### work_line.py
- **Forms**: WorkLineForm
- **توضیح**: Forms برای خطوط کاری

### person.py
- **Forms**: PersonForm
- **توضیح**: Forms برای پرسنل

### machine.py
- **Forms**: MachineForm
- **توضیح**: Forms برای ماشین‌آلات

### transfer_to_line.py
- **Forms**: TransferToLineForm
- **توضیح**: Forms برای انتقال به خط تولید

### performance_record.py
- **Forms**: PerformanceRecordForm, PerformanceRecordPersonForm
- **Formsets**: PerformanceRecordPersonFormSet
- **توضیح**: Forms برای ثبت عملکرد تولید

---

## الگوهای مشترک

تمام forms از الگوهای مشترک زیر پیروی می‌کنند:

1. **Company Scoping**: تمام forms به صورت خودکار بر اساس `active_company_id` فیلتر می‌شوند
2. **Validation**: تمام forms validation مناسب دارند
3. **Multi-line Support**: Formsets برای اسناد multi-line استفاده می‌شوند

---

## مستندات کامل

برای جزئیات کامل هر form، به `production/README_FORMS.md` مراجعه کنید.

