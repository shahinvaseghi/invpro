# Batch & Serial Tracking Implementation Plan
## طرح پیاده‌سازی ردیابی Batch و Serial

### 📋 **مقدمه**
این سند شامل تمام تغییرات مورد نیاز برای پیاده‌سازی کامل سیستم ردیابی Batch و Serial در ماژول‌های QC و Inventory می‌باشد.

---

## 🎯 **بخش ۱: Batch Tracking در Issues (حواله‌ها)**

### **مشکل فعلی:**
- حواله‌ها هیچ batch tracking ندارند
- هنگام ثبت حواله، batch انتخاب نمی‌شود
- موجودی batchها مدیریت نمی‌شود

### **تغییرات مورد نیاز:**

#### **۱.۱ افزودن فیلد batch به Issue Line Models**
**فایل‌های مورد تغییر:**
- `inventory/models.py`: افزودن فیلد batch به `IssuePermanentLine`, `IssueConsumptionLine`, `IssueConsignmentLine`, `IssueWarehouseTransferLine`

**کد:**
```python
# افزودن به تمام Issue Line models
batch = models.ForeignKey(
    "qc.ItemBatch",  # از QC module
    on_delete=models.PROTECT,
    related_name="issue_lines",
    null=True,
    blank=True,
    help_text=_("Batch to issue from")
)
batch_number = models.CharField(max_length=30, blank=True)  # cached
```

#### **۱.۲ ایجاد Migration**
**فایل جدید:** `inventory/migrations/XXXX_add_batch_to_issue_lines.py`

#### **۱.۳ تغییرات در Forms**
**فایل‌های مورد تغییر:**
- `inventory/forms/issue.py`: افزودن فیلد batch به تمام Issue Line forms

**کد:**
```python
# در تمام IssueLineForm classes
batch = forms.ModelChoiceField(
    queryset=qc_models.ItemBatch.objects.none(),
    required=False,
    label=_('Batch'),
    widget=forms.Select(attrs={'class': 'form-control'}),
)
```

#### **۱.۴ تغییرات در Form Logic**
**فایل‌های مورد تغییر:**
- `inventory/forms/issue.py`: اضافه کردن `__init__` method برای فیلتر batchها

**کد:**
```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if 'batch' in self.fields:
        # فقط batchهایی که در warehouse مربوطه موجودی دارند نمایش داده شوند
        # نیاز به ایجاد BatchWarehouse model (بخش ۱.۶)
        pass
```

#### **۱.۵ تغییرات در Views**
**فایل‌های مورد تغییر:**
- `inventory/views/issues.py`: اضافه کردن validation موجودی batch

#### **۱.۶ ایجاد BatchWarehouse Model (موجودی Batch در Warehouse)**
**فایل‌های مورد تغییر:**
- `inventory/models.py`: افزودن model جدید

**کد:**
```python
class BatchWarehouse(InventoryBaseModel):
    """موجودی هر batch در هر warehouse"""
    batch = models.ForeignKey(
        "qc.ItemBatch",
        on_delete=models.CASCADE,
        related_name="warehouse_inventory"
    )
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="batch_inventory"
    )
    quantity = models.DecimalField(
        max_digits=18,
        decimal_places=6,
        default=Decimal("0")
    )
    unit = models.CharField(max_length=30)

    class Meta:
        unique_together = ('batch', 'warehouse')
        verbose_name = _("Batch Warehouse Inventory")
        verbose_name_plural = _("Batch Warehouse Inventories")
```

#### **۱.۷ ایجاد Migration برای BatchWarehouse**
**فایل جدید:** `inventory/migrations/XXXX_create_batch_warehouse.py`

#### **۱.۸ تغییرات در Templateها**
**فایل‌های مورد تغییر:**
- `inventory/templates/issue_*.html`: افزودن dropdown batch selection

#### **۱.۹ تغییرات در URLها**
**فایل‌های مورد تغییر:**
- `inventory/urls.py`: اگر نیاز به API endpoints جدید باشد

---

## 🎯 **بخش ۲: Serial Tracking در Issues (حواله‌ها)**

### **مشکل فعلی:**
- Serial assignment وجود دارد اما با batch مرتبط نیست
- هنگام انتخاب serial، batch انتخاب شده در نظر گرفته نمی‌شود

### **تغییرات مورد نیاز:**

#### **۲.۱ تغییرات در IssueLineSerialAssignmentForm**
**فایل‌های مورد تغییر:**
- `inventory/forms/issue.py`: تغییر logic فیلتر serialها

**کد:**
```python
def __init__(self, line, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # ... کد موجود ...

    # اگر batch انتخاب شده، فقط serialهای آن batch نمایش داده شوند
    if hasattr(line, 'batch') and line.batch:
        lots_in_batch = ItemLot.objects.filter(
            item=line.item,
            batch_number=line.batch.batch_number,
            # warehouse logic هم اضافه شود
        )
        queryset = queryset.filter(lot__in=lots_in_batch)
```

#### **۲.۲ تغییرات در Serial Validation**
**فایل‌های مورد تغییر:**
- `inventory/forms/issue.py`: اطمینان از اینکه serialها متعلق به batch انتخاب شده باشند

---

## 🎯 **بخش ۳: Warehouse Transfer Logic**

### **مشکل فعلی:**
- انتقال بین warehouseها batch tracking ندارد

### **تغییرات مورد نیاز:**

#### **۳.۱ تغییرات در IssueWarehouseTransfer Logic**
**فایل‌های مورد تغییر:**
- `inventory/views/issues.py`: اضافه کردن logic انتقال batch بین warehouse

**منطق:**
- هنگام ثبت `IssueWarehouseTransfer`:
  - موجودی batch در source warehouse کاهش یابد
  - موجودی batch در destination warehouse افزایش یابد
  - batch number ثابت بماند

#### **۳.۲ تغییرات در BatchWarehouse Management**
**فایل‌های مورد تغییر:**
- `inventory/services/batch_tracking.py` (فایل جدید): service برای مدیریت batch warehouse inventory

---

## 🎯 **بخش ۴: تغییرات در QC Module**

### **تغییرات مورد نیاز:**

#### **۴.۱ اطمینان از BatchWarehouse Creation**
**فایل‌های مورد تغییر:**
- `qc/views/batches.py`: هنگام ایجاد batch، موجودی در warehouse مربوطه ایجاد شود

---

## 🎯 **بخش ۵: Testing & Validation**

### **تست‌های مورد نیاز:**
- Batch selection در حواله‌ها
- Serial filtering بر اساس batch
- Warehouse transfer batch logic
- موجودی validation

---

## 📅 **برنامه اجرایی:**

### **مرحله ۱: Infrastructure (۱ هفته)**
- [ ] ایجاد BatchWarehouse model
- [ ] Migrationها
- [ ] افزودن فیلد batch به issue lines
- [ ] تغییرات پایه forms

### **مرحله ۲: Core Logic (۲ هفته)**
- [ ] Batch selection در forms
- [ ] Serial filtering logic
- [ ] Warehouse transfer logic
- [ ] موجودی validation

### **مرحله ۳: UI & Testing (۱ هفته)**
- [ ] تغییرات templateها
- [ ] تست‌های کامل
- [ ] bug fixing

### **مرحله ۴: Optimization (۱ هفته)**
- [ ] Performance optimization
- [ ] API endpoints اگر نیاز باشد
- [ ] Documentation

---

## ⚠️ **نکات مهم:**

۱. **Backward Compatibility**: تغییرات باید با داده‌های موجود سازگار باشند
۲. **Performance**: Queryهای batch warehouse باید بهینه باشند
۳. **Validation**: تمام validationهای موجودی باید دقیق باشند
۴. **Testing**: تست‌های کاملی برای تمام سناریوها

---

## 🔗 **وابستگی‌ها:**

- QC Module (برای ItemBatch)
- Inventory Module (برای ItemSerial, ItemLot)
- Shared models

---

## 📝 **یادداشت‌ها:**

- تمام تغییرات باید با معماری موجود سازگار باشند
- از migrationهای safe استفاده شود
- تست‌های unit و integration کامل باشند
- مستندسازی کامل انجام شود
