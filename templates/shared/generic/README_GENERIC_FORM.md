# templates/shared/generic/generic_form.html - Generic Form Template

**هدف**: این template یک صفحه فرم قابل استفاده مجدد برای ایجاد و ویرایش اشیاء با پشتیبانی از fieldsets، validation، و error handling است.

این template برای کاهش تکرار کد در صفحات فرم مختلف برنامه طراحی شده و می‌تواند برای هر نوع entity استفاده شود.

---

## ساختار Template

این template از `base.html` extend می‌کند و شامل بخش‌های زیر است:

1. **Header Section**: Breadcrumb navigation + Page title
2. **Messages Section**: نمایش پیام‌های Django messages
3. **Info Banner**: نمایش کد شیء (در حالت ویرایش)
4. **Form Container**: فرم اصلی با فیلدها
5. **Form Actions**: دکمه‌های Save و Cancel

---

## Context Variables

### الزامی

#### `form`
- **Type**: `django.forms.Form` یا `django.forms.ModelForm`
- **توضیح**: Django Form instance که باید render شود
- **مثال**: `ItemForm(instance=item)`

### اختیاری

#### `form_title`
- **Type**: `str`
- **Default**: `"Form"`
- **توضیح**: عنوان فرم که در `<h1>` و `<title>` نمایش داده می‌شود
- **مثال**: `"تعریف کالای جدید"` یا `"ویرایش کالا"`

#### `breadcrumbs`
- **Type**: `list[dict]`
- **Default**: `[]`
- **توضیح**: لیست breadcrumb برای navigation
- **ساختار هر breadcrumb**:
  ```python
  {
      'label': 'نام',      # الزامی
      'url': 'url_path',   # اختیاری
  }
  ```
- **مثال**:
  ```python
  breadcrumbs = [
      {'label': 'انبار', 'url': reverse('inventory:items')},
      {'label': 'کالاها', 'url': reverse('inventory:items')},
      {'label': 'ایجاد'},
  ]
  ```

#### `cancel_url`
- **Type**: `str` (URL)
- **Default**: `request.META.HTTP_REFERER` یا `'/'`
- **توضیح**: URL برای دکمه Cancel. اگر تعریف نشود، از HTTP_REFERER استفاده می‌شود
- **مثال**: `reverse('inventory:items')`

#### `form_id`
- **Type**: `str`
- **Default**: `None`
- **توضیح**: ID برای فرم (برای استفاده در JavaScript)
- **مثال**: `"item-form"`

#### `enctype`
- **Type**: `str`
- **Default**: `None`
- **توضیح**: enctype برای فرم (برای file upload باید `"multipart/form-data"` باشد)
- **مثال**: `"multipart/form-data"`

#### `fieldsets`
- **Type**: `list[tuple]`
- **Default**: `None`
- **توضیح**: گروه‌بندی فیلدها در sections مختلف
- **ساختار**:
  ```python
  [
      ('عنوان بخش', [form['field1'], form['field2']]),
      ('عنوان بخش دیگر', [form['field3'], form['field4']]),
  ]
  ```
- **مثال**:
  ```python
  fieldsets = [
      ('اطلاعات اولیه', [
          form['name'],
          form['code'],
          form['type'],
      ]),
      ('اطلاعات تکمیلی', [
          form['description'],
          form['notes'],
      ]),
  ]
  ```
- **نکته**: اگر `fieldsets` تعریف شود، فیلدهای `form.visible_fields` به صورت خودکار استفاده نمی‌شوند

---

## Blocks قابل Override

### `breadcrumb_extra`
- **موقعیت**: بعد از breadcrumb اصلی
- **استفاده**: اضافه کردن breadcrumb اضافی
- **مثال**:
  ```django
  {% block breadcrumb_extra %}
  <span class="separator">/</span>
  <span>زیرمجموعه</span>
  {% endblock %}
  ```

### `info_banner_extra`
- **موقعیت**: داخل info banner (کنار کد)
- **استفاده**: اضافه کردن اطلاعات اضافی در banner
- **مثال**:
  ```django
  {% block info_banner_extra %}
  <div><strong>تاریخ ایجاد:</strong> {{ form.instance.created_at|date:"Y-m-d" }}</div>
  {% endblock %}
  ```

### `form_sections`
- **موقعیت**: بخش اصلی فرم
- **استفاده**: سفارشی‌سازی کامل بخش‌های فرم
- **نکته**: اگر override شود، منطق پیش‌فرض (fieldsets یا visible_fields) استفاده نمی‌شود
- **مثال**:
  ```django
  {% block form_sections %}
  <div class="form-section">
    <h3>اطلاعات اولیه</h3>
    <div class="form-row">
      <div class="form-field">
        {{ form.name.label_tag }}
        {{ form.name }}
        {{ form.name.errors }}
      </div>
    </div>
  </div>
  {% endblock %}
  ```

### `form_extra`
- **موقعیت**: بعد از فیلدهای فرم، قبل از form actions
- **استفاده**: اضافه کردن محتوای اضافی به فرم (مثل formsets، JavaScript widgets، و غیره)
- **مثال**:
  ```django
  {% block form_extra %}
  <div class="form-section">
    <h3>واحدهای ثانویه</h3>
    {{ units_formset.management_form }}
    <div id="unit-formset">
      {% for unit_form in units_formset %}
        <!-- form fields -->
      {% endfor %}
    </div>
  </div>
  {% endblock %}
  ```

### `form_actions_extra`
- **موقعیت**: در بخش form actions، بعد از دکمه‌های Save و Cancel
- **استفاده**: اضافه کردن دکمه‌های اضافی
- **مثال**:
  ```django
  {% block form_actions_extra %}
  {% if form.instance.pk %}
    <a href="{% url 'inventory:item_delete' form.instance.pk %}" class="btn btn-danger">
      حذف
    </a>
  {% endif %}
  {% endblock %}
  ```

### `form_scripts`
- **موقعیت**: در انتهای template، قبل از `{% endblock %}`
- **استفاده**: اضافه کردن JavaScript برای فرم
- **مثال**:
  ```django
  {% block form_scripts %}
  <script>
    document.getElementById('id_category').addEventListener('change', function() {
      // Load subcategories
    });
  </script>
  {% endblock %}
  ```

---

## مثال استفاده در View

### مثال 1: فرم ساده بدون fieldsets

```python
from django.shortcuts import render, redirect
from django.urls import reverse
from inventory.forms import ItemForm
from inventory.models import Item

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'کالا با موفقیت ایجاد شد.')
            return redirect('inventory:items')
    else:
        form = ItemForm()
    
    context = {
        'form': form,
        'form_title': 'تعریف کالای جدید',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها', 'url': reverse('inventory:items')},
            {'label': 'ایجاد'},
        ],
        'cancel_url': reverse('inventory:items'),
    }
    return render(request, 'shared/generic/generic_form.html', context)

def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'کالا با موفقیت به‌روزرسانی شد.')
            return redirect('inventory:items')
    else:
        form = ItemForm(instance=item)
    
    context = {
        'form': form,
        'form_title': f'ویرایش کالا: {item.name}',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها', 'url': reverse('inventory:items')},
            {'label': 'ویرایش'},
        ],
        'cancel_url': reverse('inventory:items'),
    }
    return render(request, 'shared/generic/generic_form.html', context)
```

### مثال 2: فرم با fieldsets

```python
from django.shortcuts import render, redirect
from django.urls import reverse
from inventory.forms import WarehouseForm
from inventory.models import Warehouse

def warehouse_create(request):
    if request.method == 'POST':
        form = WarehouseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:warehouses')
    else:
        form = WarehouseForm()
    
    # آماده‌سازی fieldsets
    fieldsets = [
        ('اطلاعات اولیه', [
            form['name'],
            form['name_en'],
        ]),
        ('اطلاعات تکمیلی', [
            form['description'],
            form['notes'],
        ]),
        ('تنظیمات', [
            form['display_order'],
            form['status'],
        ]),
    ]
    
    context = {
        'form': form,
        'fieldsets': fieldsets,
        'form_title': 'ایجاد انبار',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:warehouses')},
            {'label': 'ایجاد'},
        ],
        'cancel_url': reverse('inventory:warehouses'),
    }
    return render(request, 'shared/generic/generic_form.html', context)
```

### مثال 3: فرم با file upload

```python
from django.shortcuts import render, redirect
from django.urls import reverse
from inventory.forms import ItemForm

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)  # FILES برای upload
        if form.is_valid():
            form.save()
            return redirect('inventory:items')
    else:
        form = ItemForm()
    
    context = {
        'form': form,
        'form_title': 'تعریف کالای جدید',
        'enctype': 'multipart/form-data',  # برای file upload
        'form_id': 'item-form',
        'breadcrumbs': [
            {'label': 'انبار', 'url': reverse('inventory:items')},
            {'label': 'کالاها', 'url': reverse('inventory:items')},
            {'label': 'ایجاد'},
        ],
        'cancel_url': reverse('inventory:items'),
    }
    return render(request, 'shared/generic/generic_form.html', context)
```

---

## مثال استفاده در Template (Override)

```django
{% extends "shared/generic/generic_form.html" %}
{% load i18n %}

{% block form_title %}تعریف کالای جدید{% endblock %}

{% block info_banner_extra %}
{% if form.instance.pk %}
<div><strong>تاریخ ایجاد:</strong> {{ form.instance.created_at|date:"Y-m-d H:i" }}</div>
<div><strong>ایجاد کننده:</strong> {{ form.instance.created_by.username }}</div>
{% endif %}
{% endblock %}

{% block form_extra %}
<div class="form-section">
  <h3>واحدهای ثانویه</h3>
  {{ units_formset.management_form }}
  <div id="unit-formset">
    {% for unit_form in units_formset %}
      <div class="unit-form">
        {{ unit_form.from_quantity.label_tag }}
        {{ unit_form.from_quantity }}
        {{ unit_form.from_quantity.errors }}
        <!-- سایر فیلدها -->
      </div>
    {% endfor %}
  </div>
  <button type="button" id="add-unit-row" class="btn btn-secondary">
    + افزودن واحد
  </button>
</div>
{% endblock %}

{% block form_scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
  // Category/Subcategory cascading
  const categorySelect = document.getElementById('id_category');
  const subcategorySelect = document.getElementById('id_subcategory');
  
  if (categorySelect) {
    categorySelect.addEventListener('change', function() {
      const categoryId = this.value;
      // Load subcategories via AJAX
      loadSubcategories(categoryId);
    });
  }
  
  // Unit formset handling
  const addButton = document.getElementById('add-unit-row');
  if (addButton) {
    addButton.addEventListener('click', function() {
      // Add new unit form row
    });
  }
});
</script>
{% endblock %}
```

---

## وابستگی‌ها

### Template Tags
- `{% load i18n %}`: برای ترجمه

### Base Template
- `base.html`: template اصلی که این template از آن extend می‌کند

### CSS Classes
Template از کلاس‌های CSS زیر استفاده می‌کند:
- `.inventory-module`
- `.module-header`
- `.breadcrumb`
- `.page-title`
- `.form-container`
- `.info-banner`
- `.entity-form`
- `.form-section`
- `.form-row`
- `.form-field`
- `.form-control`
- `.form-text`
- `.error`
- `.form-actions`
- `.btn`, `.btn-primary`, `.btn-secondary`
- `.alert`, `.alert-success`, `.alert-error`, `.alert-warning`, `.alert-info`

---

## نکات مهم

1. **Form Instance**: اگر `form.instance.pk` وجود داشته باشد، info banner نمایش داده می‌شود و کد شیء نمایش داده می‌شود.

2. **Fieldsets**: اگر `fieldsets` تعریف شود، فیلدهای `form.visible_fields` به صورت خودکار استفاده نمی‌شوند. باید تمام فیلدها را در fieldsets قرار دهید.

3. **Full-width Fields**: برای فیلدهایی که باید full-width باشند، می‌توانید در widget از `attrs={'class': 'full-width'}` استفاده کنید:
   ```python
   description = forms.CharField(
       widget=forms.Textarea(attrs={'class': 'full-width'}),
   )
   ```

4. **Error Handling**: خطاهای فیلدها و non-field errors به صورت خودکار نمایش داده می‌شوند.

5. **Hidden Fields**: فیلدهای hidden به صورت خودکار render می‌شوند.

6. **Help Text**: اگر فیلد `help_text` داشته باشد، به صورت خودکار نمایش داده می‌شود.

7. **Required Fields**: فیلدهای required با علامت `*` نمایش داده می‌شوند.

8. **Cancel URL**: اگر `cancel_url` تعریف نشود، از `request.META.HTTP_REFERER` استفاده می‌شود. اگر آن هم موجود نباشد، به `/` redirect می‌شود.

---

## استفاده در پروژه

این template برای تمام صفحات فرم در برنامه قابل استفاده است:
- فرم ایجاد/ویرایش کالا (`inventory/item_form.html`)
- فرم ایجاد/ویرایش انبار (`inventory/warehouse_form.html`)
- فرم ایجاد/ویرایش پرسنل (`production/person_form.html`)
- و سایر صفحات فرم

با استفاده از این template، کد تکراری کاهش می‌یابد و نگهداری آسان‌تر می‌شود.

