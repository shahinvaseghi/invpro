# BOM (Bill of Materials) Documentation

## فهرست مواد اولیه - مستندات کامل

---

## فهرست مطالب

1. [معرفی](#معرفی)
2. [معماری Database](#معماری-database)
3. [مدل‌ها](#مدلها)
4. [فرم‌ها](#فرمها)
5. [Views](#views)
6. [URLs](#urls)
7. [Templates](#templates)
8. [JavaScript](#javascript)
9. [Permissions](#permissions)
10. [نحوه استفاده](#نحوه-استفاده)
11. [مثال‌های کاربردی](#مثالهای-کاربردی)

---

## معرفی

**BOM (Bill of Materials)** یا **فهرست مواد اولیه** سندی است که مشخص می‌کند برای تولید یک واحد از محصول نهایی، چه مقداری از کدام مواد اولیه نیاز است.

### ویژگی‌های کلیدی:
- ✅ **ساختار Header-Line**: یک BOM (سند اصلی) و چندین BOMMaterial (خطوط)
- ✅ **Version Control**: هر محصول می‌تواند چندین نسخه BOM داشته باشد
- ✅ **Multi-line Form**: فرم چند خطی با قابلیت افزودن/حذف ردیف
- ✅ **Cascading Filters**: فیلترهای زنجیره‌ای برای انتخاب آسان کالا
- ✅ **Material Types**: دسته‌بندی مواد (خام، نیمه‌ساخته، قطعه، بسته‌بندی)
- ✅ **Scrap Allowance**: محاسبه درصد ضایعات
- ✅ **Optional Materials**: امکان تعریف مواد اختیاری

---

## معماری Database

### رابطه جداول

```
┌─────────────────────────────────────────┐
│              BOM (Header)               │
│  - bom_code (PK, auto-generated)       │
│  - finished_item_id (FK → Item)        │
│  - company_id (FK → Company)           │
│  - version                              │
│  - is_active                            │
│  - effective_date / expiry_date        │
└────────────────┬────────────────────────┘
                 │ 1
                 │
                 │ N
┌────────────────┴────────────────────────┐
│         BOMMaterial (Lines)             │
│  - id (PK)                              │
│  - bom_id (FK → BOM) CASCADE           │
│  - material_item_id (FK → Item)        │
│  - company_id (FK → Company)           │
│  - material_type                        │
│  - quantity_per_unit                    │
│  - unit                                 │
│  - scrap_allowance                      │
│  - line_number                          │
│  - is_optional                          │
└─────────────────────────────────────────┘

Constraints:
  - UniqueConstraint(company, finished_item, version)
  - UniqueConstraint(bom, material_item)
  - UniqueConstraint(bom, line_number)
```

---

## مدل‌ها

### 1. مدل `BOM` (سند اصلی)

```python
class BOM(ProductionBaseModel):
    """
    Bill of Materials Header - سند فهرست مواد اولیه
    """
    bom_code = models.CharField(max_length=16, unique=True)
    finished_item = models.ForeignKey('inventory.Item', on_delete=models.PROTECT)
    finished_item_code = models.CharField(max_length=16)
    version = models.CharField(max_length=10, default="1.0")
    is_active = models.PositiveSmallIntegerField(default=1)
    effective_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
```

#### فیلدها:
- **bom_code**: کد منحصربفرد BOM (16 رقمی، خودکار)
- **finished_item**: محصول نهایی (FK به جدول Item)
- **finished_item_code**: کد محصول (redundant برای performance)
- **version**: نسخه BOM (مثال: "1.0", "2.0")
- **is_active**: فعال/غیرفعال (0 یا 1)
- **effective_date**: تاریخ شروع اعتبار
- **expiry_date**: تاریخ پایان اعتبار
- **description**: توضیحات مختصر
- **notes**: یادداشت‌های تکمیلی

#### متدها:
- **save()**: تولید خودکار `bom_code` و پر کردن `finished_item_code`
- **__str__()**: بازگشت `bom_code · finished_item`

---

### 2. مدل `BOMMaterial` (خطوط سند)

```python
class BOMMaterial(ProductionBaseModel):
    """
    BOM Material Line - خط فهرست مواد اولیه
    """
    bom = models.ForeignKey(BOM, on_delete=models.CASCADE, related_name="materials")
    material_item = models.ForeignKey('inventory.Item', on_delete=models.PROTECT)
    material_item_code = models.CharField(max_length=16)
    material_type = models.ForeignKey('inventory.ItemType', on_delete=models.PROTECT)
    quantity_per_unit = models.DecimalField(max_digits=18, decimal_places=6)
    unit = models.CharField(max_length=30)  # Stores primary_unit or conversion unit name
    scrap_allowance = models.DecimalField(max_digits=5, decimal_places=2)
    line_number = models.PositiveSmallIntegerField(default=1)
    is_optional = models.PositiveSmallIntegerField(default=0)
```

#### فیلدها:
- **bom**: ارجاع به BOM والد (CASCADE delete)
- **material_item**: کالای موردنیاز (FK به جدول Item)
- **material_item_code**: کد کالا (redundant برای performance)
- **material_type**: نوع ماده (FK به inventory.ItemType - انواع اقلام تعریف شده توسط کاربر)
- **quantity_per_unit**: مقدار موردنیاز به ازای هر واحد محصول
- **unit**: واحد اندازه‌گیری (CharField - می‌تواند primary_unit یا نام واحد تبدیل باشد)
- **scrap_allowance**: درصد ضایعات (0-100)
- **line_number**: شماره ردیف (مرتب‌سازی)
- **is_optional**: اختیاری (0) یا الزامی (1)

#### متدها:
- **save()**: پر کردن خودکار `material_item_code` و `company_id`
- **get_material_type_display()**: نام فارسی نوع ماده

---

## فرم‌ها

### 1. `BOMForm` (فرم اصلی)

فرم انتخاب محصول نهایی و مشخصات کلی BOM.

```python
class BOMForm(forms.ModelForm):
    # Extra fields for cascading filters
    item_type = forms.ChoiceField(required=False)
    item_category = forms.ChoiceField(required=False)
    
    class Meta:
        model = BOM
        fields = ['finished_item', 'version', 'is_active', 
                  'effective_date', 'expiry_date', 'description', 'notes']
```

**ویژگی‌ها:**
- فیلترهای cascading برای انتخاب محصول (Type → Category → Item)
- Auto-populate کردن گزینه‌ها بر اساس company فعال
- Validation برای تطبیق company

---

### 2. `BOMMaterialLineForm` (فرم هر ردیف)

فرم برای هر خط ماده اولیه با فیلترهای cascading.

```python
class BOMMaterialLineForm(forms.ModelForm):
    # Cascading filter fields (not saved to DB)
    material_category_filter = forms.ModelChoiceField(
        queryset=ItemCategory.objects.none(),
        required=False,
        label=_('Category')
    )
    material_subcategory_filter = forms.ModelChoiceField(
        queryset=ItemSubcategory.objects.none(),
        required=False,
        label=_('Subcategory')
    )
    
    # Actual fields that will be saved
    material_type = forms.ModelChoiceField(
        queryset=ItemType.objects.none(),
        required=True,
        label=_('Material Type')
    )
    material_item = forms.ModelChoiceField(
        queryset=Item.objects.none(),
        required=True,
        label=_('Material Item')
    )
    unit = forms.ChoiceField(
        choices=[('', _('Select Unit'))],
        required=True,
        label=_('Unit')
    )
    
    class Meta:
        model = BOMMaterial
        fields = ['material_type', 'material_item', 'quantity_per_unit',
                  'unit', 'scrap_allowance', 'is_optional', 'description']
```

**ویژگی‌های خاص:**
- **material_type**: ModelChoiceField که از ItemType پر می‌شود (نوع کالاهای تعریف شده توسط کاربر)
- **material_category_filter**: فیلتر کمکی برای Category (فقط در UI، ذخیره نمی‌شود)
- **material_subcategory_filter**: فیلتر کمکی برای Subcategory (فقط در UI، ذخیره نمی‌شود)
- **unit**: ChoiceField که از API `get_item_units` پر می‌شود (شامل primary_unit + conversion units)

---

### 3. `BOMMaterialLineFormSet`

```python
BOMMaterialLineFormSet = forms.inlineformset_factory(
    BOM,
    BOMMaterial,
    form=BOMMaterialLineForm,
    extra=3,         # 3 ردیف خالی اولیه
    can_delete=True, # قابلیت حذف
    min_num=1,       # حداقل 1 ردیف الزامی
    validate_min=True
)
```

---

## Views

### 1. `BOMListView`

**URL**: `/production/bom/`

لیست تمام BOM های company فعال.

```python
class BOMListView(FeaturePermissionRequiredMixin, ListView):
    model = BOM
    template_name = 'production/bom_list.html'
    context_object_name = 'boms'
    feature_code = 'production.bom'
    paginate_by = 50
```

**Context Variables:**
- `boms`: لیست BOM ها
- `finished_items`: لیست محصولات برای فیلتر

**Filters:**
- `?finished_item=<id>`: فیلتر بر اساس محصول نهایی

---

### 2. `BOMCreateView`

**URL**: `/production/bom/create/`

ایجاد BOM جدید با مواد اولیه.

```python
class BOMCreateView(FeaturePermissionRequiredMixin, CreateView):
    model = BOM
    form_class = BOMForm
    template_name = 'production/bom_form.html'
    feature_code = 'production.bom'
    required_action = 'create'
```

**Context Variables:**
- `form`: BOMForm
- `formset`: BOMMaterialLineFormSet
- `form_title`: "ایجاد BOM"

**Process:**
1. Validate BOMForm
2. Validate BOMMaterialLineFormSet
3. Save BOM header
4. Save material lines با شماره‌گذاری خودکار

---

### 3. `BOMUpdateView`

**URL**: `/production/bom/<id>/edit/`

ویرایش BOM موجود.

```python
class BOMUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    model = BOM
    form_class = BOMForm
    template_name = 'production/bom_form.html'
    feature_code = 'production.bom'
    required_action = 'edit_own'
```

**قابلیت‌ها:**
- ویرایش مشخصات BOM
- افزودن/حذف/ویرایش خطوط ماده
- حفظ line_number ها

---

### 4. `BOMDeleteView`

**URL**: `/production/bom/<id>/delete/`

حذف BOM و تمام خطوطش (CASCADE).

```python
class BOMDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    model = BOM
    template_name = 'production/bom_confirm_delete.html'
    feature_code = 'production.bom'
    required_action = 'delete_own'
```

---

## URLs

```python
# production/urls.py
urlpatterns = [
    path('bom/', views.BOMListView.as_view(), name='bom_list'),
    path('bom/create/', views.BOMCreateView.as_view(), name='bom_create'),
    path('bom/<int:pk>/edit/', views.BOMUpdateView.as_view(), name='bom_edit'),
    path('bom/<int:pk>/delete/', views.BOMDeleteView.as_view(), name='bom_delete'),
]
```

---

## API Endpoints

برای پشتیبانی از فیلترهای cascading، API های زیر در `inventory/views.py` اضافه شده‌اند:

### 1. `get_filtered_categories`

**URL**: `/inventory/api/filtered-categories/`  
**Method**: GET  
**Parameters**:
- `type_id` (optional): فیلتر بر اساس ItemType

**Response**:
```json
{
  "categories": [
    {"value": "1", "label": "الکترونیک"},
    {"value": "2", "label": "مکانیک"}
  ]
}
```

**کاربرد**: بازگشت دسته‌بندی‌هایی که حداقل یک کالای enabled با `type_id` مشخص شده دارند.

---

### 2. `get_filtered_subcategories`

**URL**: `/inventory/api/filtered-subcategories/`  
**Method**: GET  
**Parameters**:
- `type_id` (optional): فیلتر بر اساس ItemType
- `category_id` (optional): فیلتر بر اساس ItemCategory

**Response**:
```json
{
  "subcategories": [
    {"value": "1", "label": "مقاومت"},
    {"value": "2", "label": "خازن"}
  ]
}
```

**کاربرد**: بازگشت زیر دسته‌بندی‌هایی که حداقل یک کالای enabled با `type_id` و `category_id` مشخص شده دارند.

---

### 3. `get_filtered_items`

**URL**: `/inventory/api/filtered-items/`  
**Method**: GET  
**Parameters**:
- `type_id` (optional): فیلتر بر اساس ItemType
- `category_id` (optional): فیلتر بر اساس ItemCategory
- `subcategory_id` (optional): فیلتر بر اساس ItemSubcategory

**Response**:
```json
{
  "items": [
    {"value": "1", "label": "1000001 - مقاومت 1K اهم"},
    {"value": "2", "label": "1000002 - مقاومت 10K اهم"}
  ]
}
```

**کاربرد**: بازگشت کالاهایی که با فیلترهای مشخص شده مطابقت دارند.

---

### 4. `get_item_units`

**URL**: `/inventory/api/item-units/`  
**Method**: GET  
**Parameters**:
- `item_id` (required): شناسه Item

**Response**:
```json
{
  "units": [
    {
      "value": "base_kg",
      "label": "کیلوگرم (واحد اصلی)",
      "is_base": true,
      "unit_name": "کیلوگرم"
    },
    {
      "value": "gram",
      "label": "گرم (1 کیلوگرم = 1000 گرم)"
    }
  ]
}
```

**کاربرد**: بازگشت واحد اصلی (primary_unit) و تمام واحدهای تبدیل (conversion units) یک کالا.

**نکته مهم**: واحد اصلی با prefix `base_` ذخیره می‌شود تا از واحدهای تبدیل قابل تشخیص باشد.

---

## Templates

### 1. `bom_list.html`

**ویژگی‌ها:**
- جدول لیست BOM ها
- دکمه Expand/Collapse برای نمایش مواد
- فیلتر بر اساس محصول
- Pagination
- Badge های رنگی برای نوع مواد

**Expand/Collapse:**
```javascript
function toggleMaterials(button, bomId) {
  // نمایش/مخفی کردن ردیف جزئیات
}
```

**Material Type Badges:**
- 🔵 Raw Material (ماده خام)
- 🟡 Semi-Finished (نیمه‌ساخته)
- 🟢 Component (قطعه)
- 🔴 Packaging (بسته‌بندی)

---

### 2. `bom_form.html`

فرم چند بخشی با JavaScript پیشرفته.

**بخش 1: انتخاب محصول نهایی**
- فیلترهای Cascading (Type → Category → Item)
- مشخصات کلی BOM

**بخش 2: جدول مواد اولیه**
- جدول با ردیف‌های قابل افزودن/حذف
- دکمه "➕ افزودن ردیف ماده"
- دکمه "×" برای حذف هر ردیف
- شماره‌گذاری خودکار

**Validation:**
- حداقل 1 ردیف ماده الزامی
- هشدار فارسی در صورت خطا

---

### 3. `bom_confirm_delete.html`

صفحه تأیید حذف با اطلاعات کامل BOM.

---

## JavaScript

### 1. Cascading Dropdowns for Finished Item

```javascript
// فیلتر کردن Categories بر اساس Type
itemTypeSelect.addEventListener('change', function() {
  // فیلتر categories
  // پاک کردن finished_item
});

// فیلتر کردن Items بر اساس Category
itemCategorySelect.addEventListener('change', function() {
  // فیلتر items
});
```

---

### 2. Cascading Filters for Material Lines

هر ردیف material دارای فیلترهای cascading مستقل است:

```javascript
// فیلتر Categories بر اساس Material Type
function filterCategories(typeSelect, idx) {
  const typeId = typeSelect.value;
  if (!typeId) return;
  
  fetch(`/inventory/api/filtered-categories/?type_id=${typeId}`)
    .then(response => response.json())
    .then(data => {
      // پر کردن category dropdown برای ردیف idx
      populateSelect(categorySelect, data.categories);
    });
}

// فیلتر Subcategories بر اساس Type + Category
function filterSubcategories(categorySelect, idx) {
  const typeId = getTypeId(idx);
  const categoryId = categorySelect.value;
  
  fetch(`/inventory/api/filtered-subcategories/?type_id=${typeId}&category_id=${categoryId}`)
    .then(response => response.json())
    .then(data => {
      populateSelect(subcategorySelect, data.subcategories);
    });
}

// فیلتر Items بر اساس Type + Category + Subcategory
function filterItems(subcategorySelect, idx) {
  const typeId = getTypeId(idx);
  const categoryId = getCategoryId(idx);
  const subcategoryId = subcategorySelect.value;
  
  fetch(`/inventory/api/filtered-items/?type_id=${typeId}&category_id=${categoryId}&subcategory_id=${subcategoryId}`)
    .then(response => response.json())
    .then(data => {
      populateSelect(itemSelect, data.items);
    });
}

// بارگذاری واحدها بر اساس Item انتخاب شده
function loadItemUnits(itemSelect, idx) {
  const itemId = itemSelect.value;
  if (!itemId) return;
  
  fetch(`/inventory/api/item-units/?item_id=${itemId}`)
    .then(response => response.json())
    .then(data => {
      // data.units شامل primary_unit + conversion units
      populateSelect(unitSelect, data.units);
      unitSelect.disabled = false;
    });
}
```

**ویژگی‌های مهم:**
- هر ردیف مستقل است (با idx متفاوت)
- فقط categories/subcategories که حاوی item با type انتخابی هستند نمایش داده می‌شوند
- واحد اصلی (primary_unit) اولین گزینه در dropdown است
- واحدهای تبدیل (conversion units) به همراه نسبت تبدیل نمایش داده می‌شوند

---

### 3. Dynamic Formset Management

#### افزودن ردیف جدید:
```javascript
addLineBtn.addEventListener('click', function() {
  1. Clone آخرین ردیف
  2. Update کردن indices (materials-0 → materials-N)
  3. پاک کردن values
  4. Update line_number
  5. افزودن به جدول
  6. Attach event listeners برای cascading filters
  7. Update TOTAL_FORMS
});
```

#### حذف ردیف:
```javascript
function removeLine(button) {
  1. حذف ردیف (با چک حداقل 1)
  2. Update line numbers
  3. Update TOTAL_FORMS (اگر ردیف جدید بود)
}
```

---

### 4. Form Validation

```javascript
form.addEventListener('submit', function(e) {
  // چک کردن حداقل 1 ردیف با material
  // نمایش هشدار فارسی
});
```

---

## Permissions

```python
# shared/permissions.py
"production.bom": FeaturePermission(
    code="production.bom",
    label=_("BOM (Bill of Materials)"),
    actions=[
        PermissionAction.VIEW_OWN,
        PermissionAction.VIEW_ALL,
        PermissionAction.CREATE,
        PermissionAction.EDIT_OWN,
        PermissionAction.DELETE_OWN,
    ],
)
```

**استفاده در Views:**
```python
class BOMListView(FeaturePermissionRequiredMixin, ListView):
    feature_code = 'production.bom'
    # اگر کاربر دسترسی نداشته باشد → 403 Forbidden
```

---

## نحوه استفاده

### گام 1: دسترسی به BOM List

1. ورود به سیستم
2. انتخاب Company فعال
3. رفتن به منوی **Production → BOM**
4. مشاهده لیست BOM ها

### گام 2: ایجاد BOM جدید

1. کلیک دکمه **"ایجاد BOM +"**
2. در بخش محصول نهایی:
   - انتخاب نوع کالا (اختیاری، برای فیلتر)
   - انتخاب دسته‌بندی (اختیاری، برای فیلتر)
   - انتخاب محصول نهایی (الزامی)
   - وارد کردن نسخه (پیش‌فرض: 1.0)
3. در بخش مواد اولیه:
   - پر کردن ردیف‌های موجود (3 ردیف)
   - کلیک "➕" برای افزودن ردیف بیشتر
4. کلیک **"Save"**

### گام 3: مشاهده جزئیات

1. در صفحه لیست، کلیک دکمه **▶** در کنار هر BOM
2. مشاهده تمام مواد اولیه با جزئیات کامل

### گام 4: ویرایش BOM

1. کلیک دکمه **"Edit"**
2. تغییر اطلاعات یا مواد
3. افزودن/حذف ردیف‌های ماده
4. ذخیره

### گام 5: حذف BOM

1. کلیک دکمه **"Delete"**
2. تأیید حذف
3. BOM و تمام materials آن حذف می‌شوند (CASCADE)

---

## مثال‌های کاربردی

### مثال 1: BOM برای صندلی اداری

```
محصول نهایی: صندلی اداری چرخدار (کد: 10010001)
نسخه: 1.0

مواد:
┌────┬──────────────┬─────────┬────────┬──────┬─────────┐
│ ردیف│ ماده         │ نوع     │ مقدار  │ واحد │ ضایعات  │
├────┼──────────────┼─────────┼────────┼──────┼─────────┤
│ 1  │ پارچه        │ خام     │ 1.5    │ متر  │ 5%      │
│ 2  │ فوم          │ خام     │ 0.5    │ کیلو │ 3%      │
│ 3  │ چرخ          │ قطعه    │ 5      │ عدد  │ 0%      │
│ 4  │ پایه فلزی    │ قطعه    │ 1      │ عدد  │ 0%      │
│ 5  │ پیچ و مهره   │ قطعه    │ 20     │ عدد  │ 2%      │
└────┴──────────────┴─────────┴────────┴──────┴─────────┘
```

---

### مثال 2: BOM برای میز کامپیوتر

```
محصول نهایی: میز کامپیوتر ال‌شکل (کد: 10010005)
نسخه: 2.0

مواد:
┌────┬──────────────────┬─────────┬────────┬──────┬─────────┐
│ ردیف│ ماده             │ نوع     │ مقدار  │ واحد │ ضایعات  │
├────┼──────────────────┼─────────┼────────┼──────┼─────────┤
│ 1  │ صفحه MDF         │ خام     │ 2      │ عدد  │ 0%      │
│ 2  │ نوار کناری PVC   │ خام     │ 8      │ متر  │ 10%     │
│ 3  │ پایه استیل       │ قطعه    │ 4      │ عدد  │ 0%      │
│ 4  │ پیچ کج‌پیچ       │ قطعه    │ 50     │ عدد  │ 5%      │
│ 5  │ چسب صنعتی        │ خام     │ 0.2    │ کیلو │ 0%      │
│ 6  │ جای کیس (اختیاری)│ قطعه    │ 1      │ عدد  │ 0%      │
└────┴──────────────────┴─────────┴────────┴──────┴─────────┘
```

---

### مثال 3: محاسبه نیاز مواد برای 10 واحد

اگر بخواهیم **10 عدد صندلی اداری** تولید کنیم:

```python
# محاسبه خودکار توسط سیستم:

پارچه: 10 × 1.5 × (1 + 0.05) = 15.75 متر
فوم: 10 × 0.5 × (1 + 0.03) = 5.15 کیلو
چرخ: 10 × 5 × (1 + 0) = 50 عدد
پایه فلزی: 10 × 1 × (1 + 0) = 10 عدد
پیچ و مهره: 10 × 20 × (1 + 0.02) = 204 عدد
```

---

## یادداشت‌های مهم

### ⚠️ نکات امنیتی:
- همه Queryها بر اساس `company_id` فیلتر می‌شوند
- فقط کاربران با permission مناسب دسترسی دارند
- CASCADE delete برای خطوط BOM

### ⚙️ نکات Performance:
- استفاده از `select_related` و `prefetch_related`
- Index روی `(company, finished_item, version)`
- Pagination در لیست

### 🔄 Version Control:
- هر محصول می‌تواند چندین نسخه BOM داشته باشد
- فقط یک BOM می‌تواند `is_active=1` باشد (توصیه)
- استفاده از `effective_date` و `expiry_date` برای مدیریت زمانی

### 📊 گزارش‌گیری:
- لیست تمام مواد یک محصول
- محاسبه نیاز کل مواد برای تعداد مشخص
- تحلیل هزینه تمام‌شده

---

## Migrations

```bash
# Migration های مرتبط با BOM:
0006_bom_restructure.py          # ساخت جداول اصلی
0007_*.py                        # اضافه کردن فیلدهای ProductionBaseModel
0008_alter_bommaterial_material_type.py  # اضافه کردن choices
```

---

## Admin Panel

```python
@admin.register(BOM)
class BOMAdmin(admin.ModelAdmin):
    list_display = ("bom_code", "company", "finished_item_code", 
                    "version", "is_active", "is_enabled")
    list_filter = ("company", "is_active", "is_enabled")
    search_fields = ("bom_code", "finished_item_code")

@admin.register(BOMMaterial)
class BOMMaterialAdmin(admin.ModelAdmin):
    list_display = ("company", "bom", "material_item_code", 
                    "quantity_per_unit", "unit", "line_number")
    list_filter = ("company", "material_type")
    search_fields = ("bom__bom_code", "material_item_code")
```

---

## TODO / آینده

- [ ] API endpoints برای دریافت BOM
- [ ] Export به Excel/PDF
- [ ] محاسبه خودکار هزینه تمام‌شده
- [ ] نمایش BOM Tree (ساختار درختی)
- [ ] Copy BOM برای ایجاد نسخه جدید
- [ ] Bulk Import از Excel
- [ ] History و Change Log

---

**نویسنده**: Auto-generated Documentation  
**تاریخ**: 2025-11-20  
**نسخه**: 1.0  

