# مستندات Refactoring سیستم قفل ویرایش (Edit Lock)

**تاریخ ایجاد**: 1404/09/15  
**وضعیت**: 🔴 **اولویت اول - باید قبل از ادامه Refactoring تکمیل شود**  
**هدف**: حذف کد تکراری `EditLockProtectedMixin` از UpdateViewها و استفاده از Base Classes

---

## ⚠️ اهمیت این Refactoring

این refactoring **اولویت اول** است و باید **قبل از ادامه** refactoring سایر viewها تکمیل شود. دلیل:

1. **Base Classes آماده هستند**: `BaseUpdateView` و `BaseFormsetUpdateView` از `EditLockProtectedMixin` استفاده می‌کنند
2. **کد تکراری زیاد**: 13 UpdateView هنوز `EditLockProtectedMixin` را به صورت تکراری دارند
3. **وابستگی**: سایر refactoringها ممکن است به این تغییرات وابسته باشند

**نکته**: بعد از تکمیل این refactoring، می‌توانید ادامه refactoring سایر viewها را از فایل [`REFACTORING_PROGRESS_SUMMARY.md`](REFACTORING_PROGRESS_SUMMARY.md) از سر بگیرید.

---

## 📋 فهرست مطالب

1. [مقدمه](#مقدمه)
2. [سیستم قفل ویرایش چیست؟](#سیستم-قفل-ویرایش-چیست)
3. [وضعیت فعلی](#وضعیت-فعلی)
4. [کارهای انجام شده](#کارهای-انجام-شده)
5. [کارهای باقی‌مانده](#کارهای-باقی‌مانده)
6. [راهنمای Refactoring](#راهنمای-refactoring)
7. [مثال‌های Refactoring](#مثال‌های-refactoring)
8. [نکات مهم](#نکات-مهم)
9. [چک‌لیست Refactoring](#چک‌لیست-refactoring)

---

## مقدمه

در پروژه Django ما، سیستم قفل ویرایش (Edit Lock) برای جلوگیری از ویرایش همزمان یک رکورد توسط چند کاربر استفاده می‌شود. این سیستم از `EditLockProtectedMixin` استفاده می‌کند که در بسیاری از UpdateViewها به صورت تکراری اضافه شده است.

**هدف این refactoring:**
- حذف کد تکراری `EditLockProtectedMixin` از UpdateViewها
- استفاده از Base Classes که به صورت خودکار Edit Lock را فراهم می‌کنند
- کاهش کد و بهبود maintainability

---

## سیستم قفل ویرایش چیست؟

### 1. EditableModel

`EditableModel` یک abstract model است که در `shared/models.py` تعریف شده و شامل فیلدهای زیر است:

```python
class EditableModel(models.Model):
    editing_by = models.ForeignKey(User, ...)  # کاربری که در حال ویرایش است
    editing_started_at = models.DateTimeField(...)  # زمان شروع ویرایش
    editing_session_key = models.CharField(...)  # Session key کاربر
```

**متدهای مهم:**
- `clear_edit_lock()`: پاک کردن قفل ویرایش
- `is_being_edited_by(user, session_key)`: بررسی اینکه آیا توسط کاربر دیگری در حال ویرایش است

### 2. EditLockProtectedMixin

`EditLockProtectedMixin` در `shared/views/base.py` تعریف شده و کارهای زیر را انجام می‌دهد:

**در GET request (باز کردن فرم):**
1. بررسی می‌کند که آیا رکورد توسط کاربر دیگری در حال ویرایش است
2. اگر lock قدیمی است (بیشتر از 5 دقیقه)، آن را clear می‌کند
3. اگر توسط کاربر دیگری در حال ویرایش است، خطا می‌دهد و redirect می‌کند
4. در غیر این صورت، edit lock را برای کاربر فعلی set می‌کند

**در POST request (ذخیره):**
- بعد از `form_valid`: lock را clear می‌کند
- در `form_invalid`: lock را نگه می‌دارد (کاربر هنوز در حال ویرایش است)

### 3. BaseUpdateView

`BaseUpdateView` در `shared/views/base.py` تعریف شده و **به صورت خودکار** از `EditLockProtectedMixin` استفاده می‌کند:

```python
class BaseUpdateView(
    EditLockProtectedMixin,  # ← به صورت خودکار
    FeaturePermissionRequiredMixin,
    AutoSetFieldsMixin,
    SuccessMessageMixin,
    CompanyScopedViewMixin,
    UpdateView
):
    ...
```

**نتیجه:** هر UpdateView که از `BaseUpdateView` استفاده کند، به صورت خودکار Edit Lock را دارد!

---

## وضعیت فعلی

### آمار کلی

- **کل UpdateViewها در inventory**: 18 view
- **Refactor شده**: 5 view (28%)
- **باقی‌مانده**: 13 view (72%)

### دسته‌بندی UpdateViewها

1. **UpdateViewهای ساده** (بدون formset): 5 view ✅
2. **UpdateViewهای با Formset**: 8 view ❌
3. **UpdateViewهای با DocumentLockProtectedMixin**: 10 view ❌

---

## کارهای انجام شده

### ✅ master_data.py (7 view)

1. **ItemTypeUpdateView**
   - قبل: `EditLockProtectedMixin, InventoryBaseView, UpdateView`
   - بعد: `InventoryBaseView, BaseUpdateView`
   - تغییرات: استفاده از hook methods (`get_form_title`, `get_breadcrumbs`, `get_cancel_url`)

2. **ItemCategoryUpdateView**
   - قبل: `EditLockProtectedMixin, InventoryBaseView, UpdateView`
   - بعد: `InventoryBaseView, BaseUpdateView`
   - تغییرات: مشابه ItemTypeUpdateView

3. **ItemSubcategoryUpdateView**
   - قبل: `EditLockProtectedMixin, InventoryBaseView, UpdateView`
   - بعد: `InventoryBaseView, BaseUpdateView`
   - تغییرات: مشابه ItemTypeUpdateView

4. **WarehouseUpdateView**
   - قبل: `EditLockProtectedMixin, InventoryBaseView, UpdateView`
   - بعد: `InventoryBaseView, BaseUpdateView`
   - تغییرات: مشابه ItemTypeUpdateView

5. **SupplierUpdateView**
   - قبل: `EditLockProtectedMixin, InventoryBaseView, UpdateView`
   - بعد: `InventoryBaseView, BaseUpdateView`
   - تغییرات: مشابه ItemTypeUpdateView

6. **ItemUpdateView** ✅
   - قبل: `EditLockProtectedMixin, ItemUnitFormsetMixin, InventoryBaseView, UpdateView`
   - بعد: `ItemUnitFormsetMixin, InventoryBaseView, BaseFormsetUpdateView`
   - تغییرات: 
     - استفاده از `BaseFormsetUpdateView` به جای `UpdateView`
     - حفظ `ItemUnitFormsetMixin` برای مدیریت unit formset
     - حفظ logic خاص برای checkbox fields در `form_valid`
     - اضافه کردن `formset_class` و `formset_prefix`
     - استفاده از hook methods برای breadcrumbs و form title

7. **SupplierCategoryUpdateView** ✅
   - قبل: `EditLockProtectedMixin, InventoryBaseView, UpdateView`
   - بعد: `InventoryBaseView, BaseUpdateView`
   - تغییرات:
     - استفاده از `BaseUpdateView`
     - حفظ logic خاص `_sync_supplier_links` در `form_valid`
     - استفاده از hook methods (`get_form_title`, `get_breadcrumbs`, `get_cancel_url`)
     - اضافه کردن `feature_code` و `success_message`

**کاهش کد:**
- حذف `EditLockProtectedMixin` تکراری از 7 view
- حذف `form_valid` تکراری (auto-set توسط `AutoSetFieldsMixin`)
- حذف `get_context_data` تکراری (استفاده از hook methods)

---

### ✅ requests.py (1 view)

8. **PurchaseRequestUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, PurchaseRequestFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, PurchaseRequestFormMixin, BaseFormsetUpdateView`
   - تغییرات:
     - استفاده از `BaseFormsetUpdateView` به جای `UpdateView`
     - حفظ `LineFormsetMixin` برای مدیریت line formset
     - حفظ logic خاص برای legacy fields (`quantity_requested`) در `form_valid`
     - اضافه کردن `formset_class`, `formset_prefix`, `feature_code`, `success_message`
     - حفظ `get_object` برای بررسی draft status و permissions

---

### ✅ receipts.py (3 view)

9. **ReceiptTemporaryUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView`
   - تغییرات:
     - استفاده از `BaseDocumentUpdateView` به جای `UpdateView`
     - حفظ `DocumentLockProtectedMixin` (برای قفل document بعد از QC)
     - حفظ `LineFormsetMixin` برای مدیریت line formset
     - اضافه کردن `formset_class`, `formset_prefix`, `feature_code`, `success_message`
     - حفظ logic خاص برای formset validation در `form_valid`

10. **ReceiptPermanentUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView`
   - تغییرات: مشابه ReceiptTemporaryUpdateView

11. **ReceiptConsignmentUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView`
   - تغییرات: مشابه ReceiptTemporaryUpdateView

---

### ✅ issues.py (4 view)

12. **IssuePermanentUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView`
   - تغییرات:
     - استفاده از `BaseDocumentUpdateView` به جای `UpdateView`
     - حفظ `DocumentLockProtectedMixin`
     - حفظ `LineFormsetMixin` برای مدیریت line formset
     - اضافه کردن `formset_class`, `formset_prefix`, `feature_code`, `success_message`
     - حفظ logic خاص برای formset validation در `form_valid`

13. **IssueConsumptionUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView`
   - تغییرات: مشابه IssuePermanentUpdateView

14. **IssueConsignmentUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView`
   - تغییرات: مشابه IssuePermanentUpdateView

15. **IssueWarehouseTransferUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView`
   - تغییرات: مشابه IssuePermanentUpdateView

---

### ✅ stocktaking.py (3 view)

16. **StocktakingDeficitUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, BaseDocumentUpdateView`
   - تغییرات:
     - استفاده از `BaseDocumentUpdateView` به جای `UpdateView`
     - حفظ `DocumentLockProtectedMixin`
     - حفظ `LineFormsetMixin` برای مدیریت line formset
     - اضافه کردن `formset_class`, `formset_prefix`, `feature_code`, `success_message`

17. **StocktakingSurplusUpdateView** ✅
   - قبل: `EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`
   - بعد: `LineFormsetMixin, DocumentLockProtectedMixin, StocktakingFormMixin, BaseDocumentUpdateView`
   - تغییرات: مشابه StocktakingDeficitUpdateView

18. **StocktakingRecordUpdateView** ✅
   - قبل: `EditLockProtectedMixin, DocumentLockProtectedMixin, StocktakingFormMixin, UpdateView`
   - بعد: `DocumentLockProtectedMixin, StocktakingFormMixin, BaseUpdateView`
   - تغییرات:
     - استفاده از `BaseUpdateView` به جای `UpdateView` (چون formset ندارد)
     - حفظ `DocumentLockProtectedMixin`
     - اضافه کردن `feature_code`, `success_message`

---

## کارهای باقی‌مانده

✅ **همه viewها refactor شدند!** (18/18 - 100%)

---

## راهنمای Refactoring

### مرحله 1: UpdateView ساده (بدون formset)

**قبل:**
```python
class ItemTypeUpdateView(EditLockProtectedMixin, InventoryBaseView, UpdateView):
    model = models.ItemType
    form_class = forms.ItemTypeForm
    success_url = reverse_lazy('inventory:item_types')
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Item Type updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Item Type')
        context['breadcrumbs'] = [...]
        context['cancel_url'] = reverse_lazy('inventory:item_types')
        return context
```

**بعد:**
```python
class ItemTypeUpdateView(InventoryBaseView, BaseUpdateView):
    model = models.ItemType
    form_class = forms.ItemTypeForm
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item Type updated successfully.')
    
    def get_form_title(self) -> str:
        return _('Edit Item Type')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        return reverse_lazy('inventory:item_types')
```

**تغییرات:**
1. حذف `EditLockProtectedMixin` (حالا در `BaseUpdateView` است)
2. حذف `UpdateView` (استفاده از `BaseUpdateView`)
3. اضافه کردن `feature_code` و `success_message` attributes
4. تبدیل `form_valid` به `success_message` attribute
5. تبدیل `get_context_data` به hook methods (`get_form_title`, `get_breadcrumbs`, `get_cancel_url`)

---

### مرحله 2: UpdateView با Formset

**قبل:**
```python
class ItemUpdateView(EditLockProtectedMixin, ItemUnitFormsetMixin, InventoryBaseView, UpdateView):
    model = models.Item
    form_class = forms.ItemForm
    formset_class = forms.ItemUnitFormSet
    success_url = reverse_lazy('inventory:items')
    
    def form_valid(self, form):
        # Save item
        self.object = form.save()
        # Save formset
        formset = self.build_unit_formset(...)
        if formset.is_valid():
            formset.save()
        return super().form_valid(form)
```

**بعد (پیشنهادی):**
```python
class ItemUpdateView(ItemUnitFormsetMixin, InventoryBaseView, BaseFormsetUpdateView):
    model = models.Item
    form_class = forms.ItemForm
    formset_class = forms.ItemUnitFormSet
    formset_prefix = 'units'  # اگر نیاز باشد
    success_url = reverse_lazy('inventory:items')
    feature_code = 'inventory.master.items'
    success_message = _('Item updated successfully.')
    
    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        kwargs = super().get_formset_kwargs()
        # Add custom kwargs if needed
        return kwargs
    
    def form_valid(self, form):
        """Override if custom logic needed."""
        # BaseFormsetUpdateView handles formset automatically
        # But we can override for custom logic
        response = super().form_valid(form)
        # Custom logic here if needed
        return response
```

**تغییرات:**
1. حذف `EditLockProtectedMixin` (حالا در `BaseFormsetUpdateView` است)
2. حذف `UpdateView` (استفاده از `BaseFormsetUpdateView`)
3. `BaseFormsetUpdateView` به صورت خودکار formset را handle می‌کند
4. اگر logic خاص نیاز باشد، می‌توان `form_valid` را override کرد

**نکته:** باید بررسی شود که آیا `ItemUnitFormsetMixin` با `BaseFormsetUpdateView` سازگار است یا نه.

---

### مرحله 3: UpdateView با DocumentLockProtectedMixin

**قبل:**
```python
class ReceiptTemporaryUpdateView(EditLockProtectedMixin, LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, UpdateView):
    model = models.ReceiptTemporary
    form_class = forms.ReceiptTemporaryForm
    formset_class = forms.ReceiptTemporaryLineFormSet
    success_url = reverse_lazy('inventory:receipt_temporary')
```

**بعد (پیشنهادی):**
```python
class ReceiptTemporaryUpdateView(LineFormsetMixin, DocumentLockProtectedMixin, ReceiptFormMixin, BaseDocumentUpdateView):
    model = models.ReceiptTemporary
    form_class = forms.ReceiptTemporaryForm
    formset_class = forms.ReceiptTemporaryLineFormSet
    success_url = reverse_lazy('inventory:receipt_temporary')
    feature_code = 'inventory.receipts.temporary'
    success_message = _('Temporary receipt updated successfully.')
```

**تغییرات:**
1. حذف `EditLockProtectedMixin` (حالا در `BaseDocumentUpdateView` است)
2. حذف `UpdateView` (استفاده از `BaseDocumentUpdateView`)
3. حفظ `DocumentLockProtectedMixin` (برای قفل document)
4. `BaseDocumentUpdateView` به صورت خودکار formset را handle می‌کند

**نکته:** `DocumentLockProtectedMixin` باید حفظ شود چون برای قفل document است (بعد از QC)، نه edit lock.

---

## مثال‌های Refactoring

### مثال 1: UpdateView ساده

**قبل:**
```python
class WarehouseUpdateView(EditLockProtectedMixin, InventoryBaseView, UpdateView):
    model = models.Warehouse
    form_class = forms.WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouses')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.warehouses', 'created_by')
        return queryset
    
    def form_valid(self, form):
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Warehouse updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Warehouse')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Warehouses'), 'url': reverse_lazy('inventory:warehouses')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('inventory:warehouses')
        return context
```

**بعد:**
```python
class WarehouseUpdateView(InventoryBaseView, BaseUpdateView):
    model = models.Warehouse
    form_class = forms.WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouses')
    feature_code = 'inventory.master.warehouses'
    success_message = _('Warehouse updated successfully.')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.warehouses', 'created_by')
        return queryset
    
    def get_form_title(self) -> str:
        return _('Edit Warehouse')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Warehouses'), 'url': reverse_lazy('inventory:warehouses')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        return reverse_lazy('inventory:warehouses')
```

**مزایا:**
- ✅ حذف `EditLockProtectedMixin` تکراری
- ✅ حذف `form_valid` تکراری (auto-set توسط `AutoSetFieldsMixin`)
- ✅ استفاده از hook methods برای customization
- ✅ کد واضح‌تر و قابل خواندن‌تر

---

## نکات مهم

### 1. ترتیب Mixins

**مهم:** ترتیب mixins در MRO (Method Resolution Order) مهم است!

**صحیح:**
```python
class MyUpdateView(InventoryBaseView, BaseUpdateView):
    # InventoryBaseView اول (برای get_queryset)
    # BaseUpdateView دوم (برای EditLockProtectedMixin)
```

**غلط:**
```python
class MyUpdateView(BaseUpdateView, InventoryBaseView):
    # ممکن است مشکلات MRO ایجاد کند
```

### 2. DocumentLockProtectedMixin vs EditLockProtectedMixin

**تفاوت:**
- `EditLockProtectedMixin`: جلوگیری از ویرایش همزمان (temporary lock)
- `DocumentLockProtectedMixin`: جلوگیری از ویرایش document قفل شده (permanent lock)

**نتیجه:** `DocumentLockProtectedMixin` باید حفظ شود!

### 3. Formset Mixins

**مشکل:** بعضی از viewها از mixins custom استفاده می‌کنند:
- `ItemUnitFormsetMixin`
- `LineFormsetMixin`

**راه‌حل:** باید بررسی شود که آیا این mixins با `BaseFormsetUpdateView` سازگار هستند یا نه.

### 4. Custom Logic

**مشکل:** بعضی از viewها logic خاص دارند:
- `SupplierCategoryUpdateView._sync_supplier_links`
- `PurchaseRequestUpdateView` legacy fields sync

**راه‌حل:** می‌توان `form_valid` را override کرد:

```python
def form_valid(self, form):
    response = super().form_valid(form)  # BaseFormsetUpdateView handles formset
    # Custom logic here
    self._sync_supplier_links(form)
    return response
```

### 5. Permission Filtering

**مهم:** `get_queryset` باید permission filtering را انجام دهد:

```python
def get_queryset(self):
    queryset = super().get_queryset()
    queryset = self.filter_queryset_by_permissions(queryset, 'feature.code', 'owner_field')
    return queryset
```

---

## چک‌لیست Refactoring

برای هر UpdateView، این چک‌لیست را دنبال کنید:

### ✅ قبل از Refactoring

- [ ] بررسی کنید که view از `EditLockProtectedMixin` استفاده می‌کند
- [ ] بررسی کنید که آیا formset دارد یا نه
- [ ] بررسی کنید که آیا `DocumentLockProtectedMixin` دارد یا نه
- [ ] بررسی کنید که آیا logic خاص دارد یا نه

### ✅ Refactoring

- [ ] حذف `EditLockProtectedMixin` از class definition
- [ ] تغییر `UpdateView` به `BaseUpdateView` یا `BaseFormsetUpdateView` یا `BaseDocumentUpdateView`
- [ ] اضافه کردن `feature_code` attribute
- [ ] تبدیل `form_valid` به `success_message` attribute (اگر ساده است)
- [ ] تبدیل `get_context_data` به hook methods (`get_form_title`, `get_breadcrumbs`, `get_cancel_url`)
- [ ] حفظ `get_queryset` برای permission filtering
- [ ] حفظ `DocumentLockProtectedMixin` (اگر وجود دارد)

### ✅ بعد از Refactoring

- [ ] تست کنید که edit lock کار می‌کند
- [ ] تست کنید که formset کار می‌کند (اگر وجود دارد)
- [ ] تست کنید که permission filtering کار می‌کند
- [ ] تست کنید که custom logic کار می‌کند (اگر وجود دارد)
- [ ] بررسی کنید که هیچ خطای linter وجود ندارد

---

## آمار پیشرفت

### کارهای انجام شده: 18/18 (100%) ✅

✅ **master_data.py**: 7 view
- ItemTypeUpdateView
- ItemCategoryUpdateView
- ItemSubcategoryUpdateView
- WarehouseUpdateView
- SupplierUpdateView
- ItemUpdateView ✅
- SupplierCategoryUpdateView ✅

✅ **requests.py**: 1 view
- PurchaseRequestUpdateView ✅

✅ **receipts.py**: 3 view
- ReceiptTemporaryUpdateView ✅
- ReceiptPermanentUpdateView ✅
- ReceiptConsignmentUpdateView ✅

✅ **issues.py**: 4 view
- IssuePermanentUpdateView ✅
- IssueConsumptionUpdateView ✅
- IssueConsignmentUpdateView ✅
- IssueWarehouseTransferUpdateView ✅

✅ **stocktaking.py**: 3 view
- StocktakingDeficitUpdateView ✅
- StocktakingSurplusUpdateView ✅
- StocktakingRecordUpdateView ✅

### کارهای باقی‌مانده: 0/18 (0%) ✅

✅ **همه viewها refactor شدند!**

---

## دستورالعمل پیاده‌سازی

### مرحله 1: آماده‌سازی

1. **خواندن مستندات**: این فایل را کامل بخوانید
2. **بررسی Base Classes**: مطمئن شوید که `BaseUpdateView`, `BaseFormsetUpdateView`, `BaseDocumentUpdateView` را می‌شناسید
3. **بررسی وضعیت فعلی**: لیست 13 view باقی‌مانده را بررسی کنید

### مرحله 2: Refactoring گام‌به‌گام

برای هر view، این مراحل را دنبال کنید:

#### 2.1. انتخاب View

از لیست "کارهای باقی‌مانده" یک view انتخاب کنید. پیشنهاد: از ساده‌ترین شروع کنید.

#### 2.2. بررسی View فعلی

```bash
# بررسی view در فایل مربوطه
grep -A 50 "class.*UpdateView" inventory/views/[file].py
```

**چک کنید:**
- آیا `EditLockProtectedMixin` دارد؟
- آیا formset دارد؟
- آیا `DocumentLockProtectedMixin` دارد؟
- آیا logic خاص دارد؟

#### 2.3. انتخاب Base Class مناسب

- **بدون formset**: `BaseUpdateView`
- **با formset**: `BaseFormsetUpdateView`
- **با DocumentLockProtectedMixin**: `BaseDocumentUpdateView`

#### 2.4. Refactoring

از "راهنمای Refactoring" در این فایل استفاده کنید:
- [مرحله 1: UpdateView ساده](#مرحله-1-updateview-ساده-بدون-formset)
- [مرحله 2: UpdateView با Formset](#مرحله-2-updateview-با-formset)
- [مرحله 3: UpdateView با DocumentLockProtectedMixin](#مرحله-3-updateview-با-documentlockprotectedmixin)

#### 2.5. تست

از "چک‌لیست Refactoring" استفاده کنید:
- [ ] Edit lock کار می‌کند؟
- [ ] Formset کار می‌کند؟ (اگر وجود دارد)
- [ ] Permission filtering کار می‌کند؟
- [ ] Custom logic کار می‌کند؟ (اگر وجود دارد)
- [ ] هیچ خطای linter وجود ندارد؟

#### 2.6. به‌روزرسانی مستندات

بعد از تکمیل هر view:
1. در این فایل (`REFACTORING_EDIT_LOCK.md`) در بخش "کارهای باقی‌مانده" آن را حذف کنید
2. در بخش "کارهای انجام شده" اضافه کنید
3. آمار پیشرفت را به‌روزرسانی کنید

### مرحله 3: تکمیل و ادامه

بعد از تکمیل **همه 13 view**:

1. ✅ بررسی نهایی: مطمئن شوید که هیچ `EditLockProtectedMixin` تکراری باقی نمانده:
   ```bash
   grep -r "EditLockProtectedMixin.*UpdateView\|UpdateView.*EditLockProtectedMixin" inventory/views/
   ```

2. ✅ به‌روزرسانی `REFACTORING_PROGRESS_SUMMARY.md`:
   - بخش "توقف موقت" را حذف کنید
   - بخش "Refactoring قفل ویرایش" را به "کارهای تکمیل شده" منتقل کنید
   - وضعیت را به "در حال انجام" تغییر دهید

3. ✅ ادامه Refactoring: می‌توانید از `REFACTORING_PROGRESS_SUMMARY.md` ادامه دهید

---

## نتیجه‌گیری

این refactoring باعث می‌شود که:
- ✅ کد تکراری حذف شود
- ✅ Edit Lock به صورت خودکار در همه UpdateViewها فعال شود
- ✅ کد واضح‌تر و قابل خواندن‌تر شود
- ✅ Maintainability بهبود یابد

**اولویت‌بندی:**
1. **اولویت بالا**: UpdateViewهای ساده (master_data.py) - 2 view
2. **اولویت متوسط**: UpdateViewهای با formset (requests.py) - 1 view
3. **اولویت پایین**: UpdateViewهای با DocumentLockProtectedMixin (receipts, issues, stocktaking) - 10 view

**نکته مهم**: این refactoring باید **قبل از ادامه** refactoring سایر viewها تکمیل شود!

---

**آخرین به‌روزرسانی**: 1404/09/15  
**نویسنده**: AI Assistant  
**وضعیت**: ✅ تکمیل شده - 18/18 view تکمیل شده (100%)

