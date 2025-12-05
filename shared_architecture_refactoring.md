# سند فنی – معماری مشترک لیست‌ها و فرم‌ها در ERP

## Description
This document describes the motivation, goals, and implementation plan for standardizing list views, forms, and action buttons across the entire ERP system. The goal is to reduce code duplication, improve maintainability, and accelerate development of new features.

**نکته مهم**: این پروژه به صورت **ماژولار** توسعه داده شده است. هر ماژول (inventory, production, accounting, etc.) مستقل است و Base classes در ماژول `shared` قرار می‌گیرند که تمام ماژول‌ها از آن استفاده می‌کنند.

---

## ۱. مشکل فعلی (Current Problems)

### ۱.۱ تکرار کد در View Layer

در حال حاضر، **هر ListView** به صورت مستقل پیاده‌سازی شده است:

**مثال ۱: ItemTypeListView**
```python
class ItemTypeListView(InventoryBaseView, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Item Types')
        context['breadcrumbs'] = [...]
        context['create_url'] = reverse_lazy('inventory:itemtype_create')
        context['table_headers'] = []
        context['show_actions'] = True
        # ... 15+ خط کد تکراری
```

**مثال ۲: ProductOrderListView**
```python
class ProductOrderListView(FeaturePermissionRequiredMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Product Orders')
        context['breadcrumbs'] = [...]
        context['create_url'] = reverse_lazy('production:product_order_create')
        # ... همان کد تکراری
```

**نتیجه**: بیش از **236 view** وجود دارد که هر کدام همین منطق را تکرار می‌کنند.

---

### ۱.۲ منطق فیلتر و سرچ پراکنده

**مثال: AccountListView**
```python
def get_queryset(self):
    queryset = super().get_queryset()
    search = self.request.GET.get('search', '').strip()
    status = self.request.GET.get('status', '')
    
    if search:
        queryset = queryset.filter(
            Q(account_code__icontains=search) |
            Q(account_name__icontains=search)
        )
    
    if status in ('0', '1'):
        queryset = queryset.filter(is_enabled=int(status))
    
    return queryset.order_by('account_code')
```

**مشکل**: این منطق در **هر view** جداگانه نوشته شده است. اگر بخواهیم:
- الگوی سرچ را تغییر دهیم
- فیلتر جدید اضافه کنیم
- Performance را بهبود دهیم

باید **236 جا** را تغییر دهیم!

---

### ۱.۳ عدم یکپارچگی در Actions

دکمه‌های View/Edit/Delete در template تعریف شده‌اند، اما:
- منطق permission در viewها پراکنده است
- هر ماژول روش خودش را دارد
- اضافه کردن action جدید نیاز به تغییر چندین فایل دارد

---

### ۱.۴ آمار تکرار

بررسی کد فعلی نشان می‌دهد:
- **236 ListView/CreateView/UpdateView** در پروژه
- **~40+ template** که از `generic_list.html` استفاده می‌کنند (خوب!)
- **~200+ view** که منطق context setting را تکرار می‌کنند
- **~150+ view** که منطق search/filter را تکرار می‌کنند

**تخمین تکرار کد**: حدود **50-70%** از کد viewها تکراری است.

---

## ۲. راه‌حل پیشنهادی (Proposed Solution)

### ۲.۱ معماری ماژولار پروژه

پروژه به صورت **ماژولار** توسعه داده شده است:

```
invproj/
├── shared/              # ماژول مشترک (کدهای پایه)
│   ├── views/
│   │   └── base.py     # BaseListView, BaseCreateView, BaseUpdateView
│   ├── filters.py      # توابع فیلتر مشترک
│   └── ...
├── inventory/          # ماژول انبارداری
│   ├── views/
│   │   └── master_data.py  # ItemTypeListView(BaseListView)
│   └── ...
├── production/         # ماژول تولید
│   ├── views/
│   │   └── product_order.py  # ProductOrderListView(BaseListView)
│   └── ...
├── accounting/         # ماژول حسابداری
│   └── ...
└── ...                 # سایر ماژول‌ها
```

**نکته مهم**: Base classes در ماژول `shared` قرار می‌گیرند و **تمام ماژول‌ها** از آن‌ها استفاده می‌کنند.

### ۲.۲ معماری کلی Base Classes

```
┌─────────────────────────────────────────┐
│      shared/views/base.py               │
│  ┌───────────────────────────────────┐  │
│  │  BaseListView                     │  │
│  │  - Search logic                   │  │
│  │  - Filter logic                   │  │
│  │  - Pagination                     │  │
│  │  - Context setup                  │  │
│  │  - Permission checks              │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  BaseCreateView / BaseUpdateView  │  │
│  │  - Validation                     │  │
│  │  - Success messages               │  │
│  │  - Redirect logic                 │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
              ▲
              │ Inheritance
              │
┌─────────────┴─────────────────────────────┐
│  Module Views (inventory, production, ...) │
│                                           │
│  inventory/views/master_data.py:          │
│  ┌───────────────────────────────────┐    │
│  │  ItemTypeListView(BaseListView)   │    │
│  │  - model = ItemType              │    │
│  │  - search_fields = ['name', ...] │    │
│  │  - feature_code = 'inventory...' │    │
│  └───────────────────────────────────┘    │
│                                           │
│  production/views/product_order.py:       │
│  ┌───────────────────────────────────┐    │
│  │  ProductOrderListView(BaseListView)│    │
│  │  - model = ProductOrder          │    │
│  │  - search_fields = ['order_code'] │    │
│  └───────────────────────────────────┘    │
└───────────────────────────────────────────┘
```

**مزیت معماری ماژولار**:
- هر ماژول مستقل است و فقط از `shared` استفاده می‌کند
- می‌توان ماژول‌ها را جداگانه توسعه داد
- در آینده می‌توان ماژول‌ها را به microservices تبدیل کرد

---

### ۲.۳ BaseListView - کلاس پایه

**مسیر**: `shared/views/base.py` (در ماژول `shared` - ماژول مشترک پروژه)

**وظایف**:
1. دریافت پارامترهای سرچ و فیلتر از `request.GET`
2. ساخت queryset نهایی با اعمال فیلترها
3. تنظیم context استاندارد برای template
4. پشتیبانی از Pagination
5. پشتیبانی از Permission checks

**مثال استفاده**:
```python
class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']
    filter_fields = ['is_enabled']
    feature_code = 'inventory.master.item_types'
    
    # فقط تفاوت‌ها را مشخص می‌کنیم
    def get_breadcrumbs(self):
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Item Types'), 'url': None},
        ]
```

**مزیت**: به جای 50+ خط کد، فقط 10 خط می‌نویسیم!

---

### ۲.۴ سیستم فیلتر مشترک

**مسیر**: `shared/filters.py` (در ماژول `shared`)

**توابع مشترک**:
```python
def apply_search(queryset, search_query, fields):
    """Apply search across multiple fields."""
    if not search_query:
        return queryset
    
    q_objects = Q()
    for field in fields:
        q_objects |= Q(**{f"{field}__icontains": search_query})
    
    return queryset.filter(q_objects)

def apply_status_filter(queryset, status_value):
    """Apply status filter (active/inactive)."""
    if status_value in ('0', '1'):
        return queryset.filter(is_enabled=int(status_value))
    return queryset
```

**مزیت**: تغییر منطق فیلتر فقط در یک جا!

---

### ۲.۵ سیستم Actions مشترک

**در Model**:
```python
class ItemType(models.Model):
    # ... fields ...
    
    def get_available_actions(self, user):
        """Return list of available actions for this object."""
        actions = []
        
        if user.has_perm('inventory.view_itemtype', self):
            actions.append('view')
        if user.has_perm('inventory.change_itemtype', self) and not self.is_locked:
            actions.append('edit')
        if user.has_perm('inventory.delete_itemtype', self):
            actions.append('delete')
        
        return actions
```

**در Template** (`shared/partials/row_actions.html`):
```django
{% for action in object.get_available_actions request.user %}
    {% if action == 'view' %}
        <a href="{% url view_url_name object.pk %}" class="btn btn-info">View</a>
    {% elif action == 'edit' %}
        <a href="{% url edit_url_name object.pk %}" class="btn btn-secondary">Edit</a>
    {% endif %}
{% endfor %}
```

**مزیت**: منطق permission در یک جا (مدل)، نمایش در یک جا (template).

---

## ۳. مزایای این معماری

### ۳.۱ کاهش تکرار کد
- **قبل**: هر view 50+ خط کد تکراری
- **بعد**: هر view 10-15 خط کد اختصاصی
- **صرفه‌جویی**: ~70% کاهش کد

### ۳.۲ توسعه سریع‌تر
- ایجاد view جدید: از 2 ساعت به 15 دقیقه
- اضافه کردن فیلتر جدید: از تغییر 200+ فایل به تغییر 1 فایل

### ۳.۳ نگهداری آسان‌تر
- باگ در منطق فیلتر: فقط یک جا باید fix شود
- تغییر UI: فقط template base تغییر می‌کند
- اضافه کردن feature جدید: فقط BaseView را extend می‌کنیم

### ۳.۴ یکپارچگی UI/UX
- تمام لیست‌ها ظاهر یکسان دارند
- تمام فرم‌ها رفتار یکسان دارند
- کاربر تجربه یکپارچه دارد

### ۳.۵ امنیت بهتر
- منطق permission در یک جا (مدل)
- تست امنیت فقط روی BaseView
- کمتر احتمال خطای امنیتی

---

## ۴. معایب و چالش‌ها

### ۴.۱ زمان Refactoring
- **تخمین**: 2-3 ماه برای migration کامل
- **ریسک**: ممکن است باگ‌های جدید ایجاد شود

### ۴.۲ Learning Curve
- تیم باید با معماری جدید آشنا شود
- نیاز به مستندسازی کامل

### ۴.۳ Backward Compatibility
- باید viewهای قدیمی را حفظ کنیم تا زمانی که migrate شوند
- ممکن است نیاز به wrapper classes باشد

---

## ۵. مراحل پیاده‌سازی (Implementation Plan)

### فاز ۱: Infrastructure (هفته ۱-۲)

**وظایف**:
1. ایجاد `shared/views/base.py` در ماژول `shared` با کلاس‌های:
   - `BaseListView`
   - `BaseCreateView`
   - `BaseUpdateView`

2. ایجاد `shared/filters.py` در ماژول `shared` با توابع:
   - `apply_search()`
   - `apply_filters()`
   - `apply_date_range()`
   - `apply_status_filter()`

3. بهبود `templates/shared/partials/row_actions.html`:
   - پشتیبانی از `get_available_actions()`
   - نمایش دکمه‌ها بر اساس permission

4. تست واحد (Unit Tests):
   - تست BaseListView
   - تست filter functions
   - تست permission logic

**خروجی**: Infrastructure آماده برای استفاده

---

### فاز ۲: Pilot Implementation (هفته ۳)

**انتخاب ماژول Pilot**: `shared` module (ماژول مشترک - ساده‌ترین)

**دلیل انتخاب `shared`**:
- ماژول مشترک است و همه از آن استفاده می‌کنند
- Viewهای ساده‌تری دارد
- تست در این ماژول اعتماد‌سازی می‌کند

**Viewهای Pilot در ماژول `shared`**:
- ✅ `shared/views/companies.py`: تمام 5 view به Base classes منتقل شد
  - ✅ `CompanyListView` → `BaseListView`
  - ✅ `CompanyCreateView` → `BaseCreateView`
  - ✅ `CompanyUpdateView` → `BaseUpdateView`
  - ✅ `CompanyDetailView` → `BaseDetailView`
  - ✅ `CompanyDeleteView` → `BaseDeleteView`
- ⏳ `shared/views/access_levels.py`: `AccessLevelListView` → `BaseListView` (در انتظار)
- ⏳ `shared/views/groups.py`: `GroupListView` → `BaseListView` (در انتظار)

**هدف**: 
- تست معماری در محیط واقعی
- شناسایی مشکلات
- دریافت بازخورد از تیم
- اطمینان از اینکه Base classes در ماژول `shared` به درستی کار می‌کنند

**خروجی**: ✅ 5 view در ماژول `shared` (companies) که با معماری جدید کار می‌کنند

---

### فاز ۳: Rollout تدریجی به سایر ماژول‌ها (ماه ۲-۳)

**اولویت‌بندی ماژول‌ها**:
1. **ماژول‌های پراستفاده**: 
   - `inventory` (انبارداری)
   - `production` (تولید)
   
2. **ماژول‌های متوسط**: 
   - `accounting` (حسابداری)
   
3. **ماژول‌های کم‌استفاده**: 
   - `ticketing` (تیکتینگ)
   - `qc` (کنترل کیفیت)

**نکته**: ماژول‌های `sales`, `hr`, `transportation`, `office_automation`, `procurement` هنوز توسعه داده نشده‌اند و فعلاً از scope این پروژه خارج هستند. پس از توسعه این ماژول‌ها، می‌توان از Base classes مشترک استفاده کرد.

**استراتژی Migration**:
- هر هفته 1-2 ماژول migrate شود
- هر ماژول به صورت مستقل migrate می‌شود (معماری ماژولار حفظ می‌شود)
- بعد از هر migration: تست کامل + code review
- مستندسازی تغییرات در README هر ماژول

**مثال Migration یک ماژول**:
```python
# قبل: inventory/views/master_data.py
class ItemTypeListView(InventoryBaseView, ListView):
    # 50+ خط کد تکراری

# بعد: inventory/views/master_data.py
from shared.views.base import BaseListView

class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']
    # فقط 10 خط کد اختصاصی
```

**خروجی**: تمام viewها در تمام ماژول‌ها migrate شده‌اند

---

### فاز ۴: Cleanup و بهینه‌سازی (ماه ۴)

**وظایف**:
1. حذف کدهای قدیمی (legacy views)
2. بهینه‌سازی performance:
   - Caching برای فیلترهای پراستفاده
   - Optimize database queries
3. مستندسازی نهایی:
   - راهنمای استفاده برای توسعه‌دهندگان
   - Best practices
   - Examples

**خروجی**: کد تمیز و بهینه

---

## ۶. معیارهای موفقیت (Success Metrics)

### ۶.۱ کاهش کد
- **هدف**: کاهش 50%+ از کد viewها
- **اندازه‌گیری**: مقایسه LOC قبل و بعد

### ۶.۲ سرعت توسعه
- **هدف**: کاهش 60%+ زمان ایجاد view جدید
- **اندازه‌گیری**: زمان ایجاد 10 view جدید

### ۶.۳ کیفیت کد
- **هدف**: کاهش 80%+ باگ‌های مربوط به فیلتر/سرچ
- **اندازه‌گیری**: تعداد باگ‌های گزارش شده

### ۶.۴ رضایت تیم
- **هدف**: رضایت 80%+ از تیم توسعه
- **اندازه‌گیری**: نظرسنجی از تیم

---

## ۷. ریسک‌ها و راه‌حل‌ها

### ریسک ۱: باگ در BaseView
**احتمال**: متوسط  
**تأثیر**: بالا  
**راه‌حل**: 
- تست کامل قبل از rollout
- نگه داشتن viewهای قدیمی به عنوان backup
- Rollback plan آماده

### ریسک ۲: Performance Issues
**احتمال**: پایین  
**تأثیر**: متوسط  
**راه‌حل**:
- Profiling و monitoring
- Caching برای querysetهای پراستفاده
- Optimize database queries

### ریسک ۳: مقاومت تیم
**احتمال**: پایین  
**تأثیر**: متوسط  
**راه‌حل**:
- آموزش تیم قبل از rollout
- مستندسازی کامل
- پشتیبانی فنی

---

## ۸. بررسی دقیق ماژول `shared` (Pilot Module)

این بخش شامل بررسی کامل ماژول `shared` به عنوان ماژول pilot برای پیاده‌سازی معماری مشترک است.

---

### ۸.۱ ساختار ماژول `shared`

**فایل‌های View**:
- `shared/views/companies.py` - 5 view (List, Create, Update, Detail, Delete)
- `shared/views/users.py` - 5 view (List, Create, Update, Detail, Delete)
- `shared/views/access_levels.py` - 5 view (List, Create, Update, Detail, Delete)
- `shared/views/groups.py` - 5 view (List, Create, Update, Detail, Delete)
- `shared/views/company_units.py` - 5 view (List, Create, Update, Detail, Delete)
- `shared/views/smtp_server.py` - 4 view
- `shared/views/base.py` - Mixinها و کلاس‌های پایه

**فایل‌های Form**:
- `shared/forms/companies.py` - CompanyForm, CompanyUnitForm
- `shared/forms/users.py` - UserCreateForm, UserUpdateForm, UserCompanyAccessFormSet
- `shared/forms/groups.py` - GroupForm
- `shared/forms/access_levels.py` - AccessLevelForm
- `shared/forms/smtp_server.py` - SMTPServerForm

**کل**: 25+ view و 6+ form class

---

### ۸.۲ الگوهای مشترک در ListViewها

#### ۸.۲.۱ تکرار در `get_context_data()`

**همه ListViewها این context variables را تنظیم می‌کنند**:

```python
context['active_module'] = 'shared'
context['page_title'] = _('...')
context['breadcrumbs'] = [...]
context['create_url'] = reverse_lazy('...')
context['create_button_text'] = _('...')
context['show_filters'] = True
context['status_filter'] = True/False
context['search_placeholder'] = _('...')
context['clear_filter_url'] = reverse_lazy('...')
context['show_actions'] = True
context['feature_code'] = 'shared....'
context['detail_url_name'] = 'shared:..._detail'
context['edit_url_name'] = 'shared:..._edit'
context['delete_url_name'] = 'shared:..._delete'
context['table_headers'] = [...]
context['empty_state_title'] = _('...')
context['empty_state_message'] = _('...')
context['empty_state_icon'] = '...'
```

**تخمین**: هر ListView ~50 خط کد تکراری در `get_context_data()`

#### ۸.۲.۲ تکرار در `get_queryset()`

**الگوی مشترک**:
```python
def get_queryset(self):
    queryset = Model.objects.all().order_by('...')
    
    # Search filter
    search = self.request.GET.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            Q(field1__icontains=search) |
            Q(field2__icontains=search)
        )
    
    # Status filter
    status = self.request.GET.get('status', '')
    if status in ('0', '1'):
        queryset = queryset.filter(is_enabled=int(status))
    
    return queryset
```

**تفاوت‌ها**:
- `CompanyListView`: فیلتر بر اساس `UserCompanyAccess`
- `CompanyUnitListView`: فیلتر بر اساس `active_company_id`
- `UserListView`: فیلتر پیچیده‌تر (username, email, first_name, last_name)
- `AccessLevelListView`: فیلتر ساده (code, name)
- `GroupListView`: فیلتر بر اساس `GroupProfile.is_enabled`

**تخمین**: هر ListView ~20-30 خط کد تکراری در `get_queryset()`

---

### ۸.۳ الگوهای مشترک در CreateView/UpdateView

#### ۸.۳.۱ تکرار در `get_context_data()`

**همه CreateView/UpdateView این context variables را تنظیم می‌کنند**:

```python
context['active_module'] = 'shared'
context['form_title'] = _('Create/Edit ...')
context['breadcrumbs'] = [
    {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
    {'label': _('...'), 'url': reverse('shared:...')},
]
context['cancel_url'] = reverse('shared:...')
```

**تخمین**: هر CreateView/UpdateView ~15 خط کد تکراری

#### ۸.۳.۲ تکرار در `form_valid()`

**الگوی مشترک**:
```python
def form_valid(self, form):
    # Set created_by/edited_by
    if isinstance(self, CreateView):
        form.instance.created_by = self.request.user
    else:
        form.instance.edited_by = self.request.user
    
    response = super().form_valid(form)
    messages.success(self.request, _('... created/updated successfully.'))
    return response
```

**تخمین**: هر CreateView/UpdateView ~10 خط کد تکراری

---

### ۸.۴ الگوهای مشترک در DeleteView

**همه DeleteView این context variables را تنظیم می‌کنند**:

```python
context['active_module'] = 'shared'
context['delete_title'] = _('Delete ...')
context['confirmation_message'] = _('Are you sure...')
context['breadcrumbs'] = [...]
context['object_details'] = [...]
context['cancel_url'] = reverse('shared:...')
```

**همه DeleteView این منطق را دارند**:
```python
def delete(self, request, *args, **kwargs):
    messages.success(self.request, _('... deleted successfully.'))
    return super().delete(request, *args, **kwargs)
```

**تخمین**: هر DeleteView ~25 خط کد تکراری

---

### ۸.۵ Base Classes موجود در `shared/views/base.py`

#### ۸.۵.۱ Mixinهای موجود

1. **`UserAccessFormsetMixin`**
   - مدیریت formset برای `UserCompanyAccess`
   - فقط در `UserCreateView` و `UserUpdateView` استفاده می‌شود

2. **`AccessLevelPermissionMixin`**
   - مدیریت ماتریس permission (پیچیده - 230+ خط)
   - فقط در `AccessLevelCreateView` و `AccessLevelUpdateView` استفاده می‌شود

3. **`EditLockProtectedMixin`**
   - جلوگیری از ویرایش همزمان
   - در همه `UpdateView`ها استفاده می‌شود
   - منطق پیچیده (350+ خط)

**نکته**: این mixinها برای موارد خاص هستند و نمی‌توانند به عنوان Base classes استفاده شوند.

---

### ۸.۶ آمار تکرار کد در ماژول `shared`

#### ۸.۶.۱ ListView (5 view)

- `get_context_data()`: 5 × ~50 خط = **~250 خط تکراری**
- `get_queryset()`: 5 × ~25 خط = **~125 خط تکراری**
- **مجموع ListView**: **~375 خط تکراری**

#### ۸.۶.۲ CreateView (5 view)

- `get_context_data()`: 5 × ~15 خط = **~75 خط تکراری**
- `form_valid()`: 5 × ~10 خط = **~50 خط تکراری**
- **مجموع CreateView**: **~125 خط تکراری**

#### ۸.۶.۳ UpdateView (5 view)

- `get_context_data()`: 5 × ~15 خط = **~75 خط تکراری**
- `form_valid()`: 5 × ~10 خط = **~50 خط تکراری**
- **مجموع UpdateView**: **~125 خط تکراری**

#### ۸.۶.۴ DeleteView (5 view)

- `get_context_data()`: 5 × ~20 خط = **~100 خط تکراری**
- `delete()`: 5 × ~5 خط = **~25 خط تکراری**
- **مجموع DeleteView**: **~125 خط تکراری**

#### ۸.۶.۵ مجموع کل

**تکرار کد در ماژول `shared`**: **~750 خط کد تکراری**

**با Base classes**: این مقدار به **~150 خط** کاهش می‌یابد (فقط override کردن متدها)

**صرفه‌جویی**: **~600 خط کد** (80% کاهش)

---

### ۸.۷ چیزهایی که می‌توان مشترک کرد

#### ۸.۷.۱ BaseListView

**وظایف**:
1. منطق `get_queryset()` مشترک:
   - دریافت `search` از `request.GET`
   - دریافت `status` از `request.GET`
   - اعمال فیلتر search (با `search_fields` attribute)
   - اعمال فیلتر status
   - مرتب‌سازی (با `ordering` attribute)

2. تنظیم context در `get_context_data()`:
   - تمام context variables استاندارد
   - پشتیبانی از override کردن با متدهای hook

3. پشتیبانی از pagination (از Django ListView)

4. پشتیبانی از permission checks (از `FeaturePermissionRequiredMixin`)

**Attributes قابل تنظیم**:
```python
class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']  # فیلدهای قابل جستجو
    filter_fields = ['is_enabled']  # فیلدهای قابل فیلتر
    feature_code = 'shared.item_types'
    ordering = ['public_code']  # مرتب‌سازی پیش‌فرض
```

#### ۸.۷.۲ BaseCreateView / BaseUpdateView

**وظایف**:
1. تنظیم `created_by`/`edited_by` به صورت خودکار
2. نمایش پیام موفقیت استاندارد
3. تنظیم context (breadcrumbs, form_title, cancel_url)
4. پشتیبانی از `EditLockProtectedMixin`

**Attributes قابل تنظیم**:
```python
class ItemTypeCreateView(BaseCreateView):
    model = ItemType
    form_class = ItemTypeForm
    success_url = reverse_lazy('shared:item_types')
    feature_code = 'shared.item_types'
```

#### ۸.۷.۳ BaseDeleteView

**وظایف**:
1. تنظیم context برای `generic_confirm_delete.html`
2. نمایش پیام موفقیت
3. پشتیبانی از `object_details` customization

**Attributes قابل تنظیم**:
```python
class ItemTypeDeleteView(BaseDeleteView):
    model = ItemType
    success_url = reverse_lazy('shared:item_types')
    feature_code = 'shared.item_types'
```

#### ۸.۷.۴ توابع فیلتر مشترک (`shared/filters.py`)

**توابع پیشنهادی**:

```python
def apply_search(queryset, search_query, fields):
    """Apply search across multiple fields."""
    if not search_query:
        return queryset
    
    q_objects = Q()
    for field in fields:
        q_objects |= Q(**{f"{field}__icontains": search_query})
    
    return queryset.filter(q_objects)

def apply_status_filter(queryset, status_value):
    """Apply status filter (active/inactive)."""
    if status_value in ('0', '1'):
        return queryset.filter(is_enabled=int(status_value))
    return queryset

def apply_company_filter(queryset, company_id):
    """Apply company filter."""
    if company_id:
        return queryset.filter(company_id=company_id)
    return queryset
```

---

### ۸.۸ مزایای استفاده از Base classes در `shared`

1. **کاهش کد**: از ~750 خط به ~150 خط (80% کاهش)
2. **یکپارچگی**: همه viewها رفتار یکسان دارند
3. **نگهداری آسان‌تر**: تغییرات فقط در Base classes
4. **توسعه سریع‌تر**: ایجاد view جدید فقط 10-15 خط کد
5. **تست آسان‌تر**: تست Base classes = تست همه viewها

---

### ۸.۹ چالش‌های خاص ماژول `shared`

#### ۸.۹.۱ Viewهای خاص

- **`CompanyListView`**: فیلتر بر اساس `UserCompanyAccess` (نیاز به override)
- **`CompanyUnitListView`**: فیلتر بر اساس `active_company_id` (نیاز به override)
- **`UserListView`**: فیلتر پیچیده‌تر (نیاز به override)

**راه‌حل**: BaseListView باید hook methods داشته باشد:
```python
def get_base_queryset(self):
    """Override for custom base queryset."""
    return self.model.objects.all()

def apply_custom_filters(self, queryset):
    """Override for custom filters."""
    return queryset
```

#### ۸.۹.۲ Formset Management

- **`UserCreateView`/`UserUpdateView`**: استفاده از `UserAccessFormsetMixin`

**راه‌حل**: BaseCreateView/BaseUpdateView باید از mixinها پشتیبانی کنند.

---

### ۸.۱۰ نتیجه‌گیری برای ماژول `shared`

✅ **ماژول `shared` برای pilot مناسب است** چون:
- Viewهای نسبتاً ساده‌ای دارد
- الگوهای مشترک واضح است
- تکرار کد زیاد است (~750 خط)
- می‌توان به عنوان نمونه برای سایر ماژول‌ها استفاده کرد

✅ **پس از پیاده‌سازی Base classes**:
- کد از ~750 خط به ~150 خط کاهش می‌یابد
- توسعه view جدید بسیار سریع‌تر می‌شود
- نگهداری آسان‌تر می‌شود

---

## ۹. بررسی دقیق ماژول `inventory` (انبار)

این بخش شامل بررسی کامل ماژول `inventory` به عنوان یکی از بزرگ‌ترین و پیچیده‌ترین ماژول‌های پروژه است.

---

### ۹.۱ ساختار ماژول `inventory`

**فایل‌های View** (12 فایل):
- `inventory/views/master_data.py` - 27 view (Item Types, Categories, Subcategories, Items, Warehouses, Suppliers)
- `inventory/views/receipts.py` - 12 view (Temporary, Permanent, Consignment Receipts)
- `inventory/views/issues.py` - 10 view (Permanent, Consumption, Consignment Issues)
- `inventory/views/requests.py` - 6 view (Purchase Requests, Warehouse Requests)
- `inventory/views/stocktaking.py` - 9 view (Deficit, Surplus, Records)
- `inventory/views/base.py` - Base classes و Mixinها
- `inventory/views/api.py` - JSON API endpoints
- `inventory/views/balance.py` - Balance calculation views
- `inventory/views/item_import.py` - Item import views
- `inventory/views/create_issue_from_warehouse_request.py` - Special workflow views
- `inventory/views/issues_from_warehouse_request.py` - Special workflow views

**کل**: **81+ view** (بیشترین تعداد view در بین ماژول‌ها)

**فایل‌های Form** (7 فایل):
- `inventory/forms/master_data.py` - Master data forms
- `inventory/forms/receipt.py` - Receipt forms (header + line formsets)
- `inventory/forms/issue.py` - Issue forms (header + line formsets)
- `inventory/forms/request.py` - Request forms (header + line formsets)
- `inventory/forms/stocktaking.py` - Stocktaking forms (header + line formsets)
- `inventory/forms/base.py` - Base form classes

---

### ۹.۲ Base Classes موجود در `inventory/views/base.py`

#### ۹.۲.۱ `InventoryBaseView`

**وظایف**:
- فیلتر خودکار بر اساس `active_company_id`
- اضافه کردن `active_module = 'inventory'` به context
- Helper methods برای permission checks:
  - `add_delete_permissions_to_context()`
  - `add_view_edit_permissions_to_context()`
  - `filter_queryset_by_permissions()`

**استفاده**: همه viewهای ماژول inventory از این base استفاده می‌کنند

#### ۹.۲.۲ `LineFormsetMixin`

**وظایف**:
- مدیریت formset برای اسناد چند ردیفی (Receipts, Issues, Requests, Stocktaking)
- ذخیره ردیف‌ها با document
- مدیریت سریال‌ها برای issue lines

**استفاده**: در تمام CreateView/UpdateViewهای اسناد چند ردیفی

#### ۹.۲.۳ `ItemUnitFormsetMixin`

**وظایف**:
- مدیریت formset برای واحدهای کالا (`ItemUnit`)
- تولید کد واحد
- همگام‌سازی روابط Item-Warehouse

**استفاده**: فقط در `ItemCreateView` و `ItemUpdateView`

#### ۹.۲.۴ `DocumentLockProtectedMixin`

**وظایف**:
- جلوگیری از ویرایش/حذف اسناد قفل‌شده (`is_locked=1`)
- بررسی مالکیت سند (creator)
- پیام خطا و redirect

**استفاده**: در تمام UpdateView/DeleteViewهای اسناد

#### ۹.۲.۵ `DocumentDeleteViewBase`

**وظایف**:
- Base class برای حذف اسناد
- بررسی permission (`DELETE_OWN`, `DELETE_OTHER`)
- محافظت از اسناد قفل‌شده

**استفاده**: در تمام DeleteViewهای اسناد

---

### ۹.۳ الگوهای مشترک در ListViewها

#### ۹.۳.۱ تکرار در `get_context_data()`

**الگوی مشترک در همه ListViewها**:

```python
context['page_title'] = _('...')
context['breadcrumbs'] = [
    {'label': _('Inventory'), 'url': None},
    {'label': _('...'), 'url': None},
]
context['create_url'] = reverse_lazy('inventory:..._create')
context['create_button_text'] = _('Create ...')
context['show_filters'] = True
context['print_enabled'] = True
context['show_actions'] = True
context['feature_code'] = 'inventory....'
context['detail_url_name'] = 'inventory:..._detail'
context['edit_url_name'] = 'inventory:..._edit'
context['delete_url_name'] = 'inventory:..._delete'
context['empty_state_title'] = _('No ... Found')
context['empty_state_message'] = _('Start by creating...')
context['empty_state_icon'] = '...'
```

**تخمین**: هر ListView ~40-60 خط کد تکراری در `get_context_data()`

#### ۹.۳.۲ تکرار در `get_queryset()`

**الگوی مشترک**:
```python
def get_queryset(self):
    queryset = super().get_queryset()
    # Filter by permissions
    queryset = self.filter_queryset_by_permissions(queryset, 'inventory....', 'created_by')
    # Prefetch related objects
    queryset = queryset.select_related(...).prefetch_related(...)
    # Apply filters (status, search, etc.)
    queryset = self._apply_filters(queryset)
    return queryset
```

**تفاوت‌ها**:
- **Master Data Views**: فیلتر ساده (search, status)
- **Document Views** (Receipts, Issues): فیلتر پیچیده‌تر (status, search, prefetch lines)
- **Request Views**: فیلتر بر اساس status, priority, search + stats
- **Stocktaking Views**: فیلتر ساده + prefetch lines

**تخمین**: هر ListView ~30-50 خط کد تکراری در `get_queryset()`

#### ۹.۳.۳ Stats Methods

**الگوی مشترک**: بسیاری از ListViewها متد `_get_stats()` دارند:

```python
def _get_stats(self) -> Dict[str, int]:
    """Return aggregate stats for summary cards."""
    stats = {'total': 0, 'draft': 0, ...}
    company_id = self.request.session.get('active_company_id')
    if not company_id:
        return stats
    base_qs = Model.objects.filter(company_id=company_id)
    stats['total'] = base_qs.count()
    # ... more stats
    return stats
```

**استفاده**: در `ReceiptTemporaryListView`, `IssuePermanentListView`, `PurchaseRequestListView`, `WarehouseRequestListView`

**تخمین**: هر stats method ~15-20 خط کد تکراری

---

### ۹.۴ الگوهای مشترک در CreateView/UpdateView

#### ۹.۴.۱ Document Views (Receipts, Issues, Stocktaking)

**الگوی مشترک**:
```python
class ReceiptCreateView(LineFormsetMixin, ReceiptFormMixin, CreateView):
    model = ReceiptPermanent
    form_class = ReceiptPermanentForm
    formset_class = ReceiptPermanentLineFormSet
    success_url = reverse_lazy('inventory:receipt_permanent')
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        # Save document
        self.object = form.save()
        # Save lines formset
        lines_formset = self.build_line_formset(...)
        self._save_line_formset(lines_formset)
        messages.success(...)
        return HttpResponseRedirect(...)
```

**تخمین**: هر CreateView/UpdateView ~30-40 خط کد تکراری

#### ۹.۴.۲ Master Data Views

**الگوی مشترک**:
```python
class ItemTypeCreateView(InventoryBaseView, CreateView):
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(...)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Type')
        context['breadcrumbs'] = [...]
        context['cancel_url'] = reverse_lazy('inventory:item_types')
        return context
```

**تخمین**: هر CreateView/UpdateView ~20-25 خط کد تکراری

---

### ۹.۵ الگوهای مشترک در DeleteView

#### ۹.۵.۱ Document Delete Views

**استفاده از `DocumentDeleteViewBase`**:
```python
class ReceiptPermanentDeleteView(DocumentDeleteViewBase):
    model = ReceiptPermanent
    success_url = reverse_lazy('inventory:receipt_permanent')
    feature_code = 'inventory.receipts.permanent'
```

**مزیت**: منطق permission و lock protection در base class

#### ۹.۵.۲ Master Data Delete Views

**الگوی مشترک**:
```python
class ItemTypeDeleteView(InventoryBaseView, DeleteView):
    model = ItemType
    success_url = reverse_lazy('inventory:item_types')
    
    def delete(self, request, *args, **kwargs):
        messages.success(...)
        return super().delete(request, *args, **kwargs)
```

**تخمین**: هر DeleteView ~10-15 خط کد تکراری

---

### ۹.۶ آمار تکرار کد در ماژول `inventory`

#### ۹.۶.۱ ListView (27+ view)

- `get_context_data()`: 27 × ~50 خط = **~1,350 خط تکراری**
- `get_queryset()`: 27 × ~40 خط = **~1,080 خط تکراری**
- `_get_stats()`: 5 × ~20 خط = **~100 خط تکراری**
- `_apply_filters()`: 10 × ~30 خط = **~300 خط تکراری**
- **مجموع ListView**: **~2,830 خط تکراری**

#### ۹.۶.۲ CreateView (15+ view)

- `form_valid()`: 15 × ~30 خط = **~450 خط تکراری**
- `get_context_data()`: 15 × ~20 خط = **~300 خط تکراری**
- **مجموع CreateView**: **~750 خط تکراری**

#### ۹.۶.۳ UpdateView (15+ view)

- `form_valid()`: 15 × ~30 خط = **~450 خط تکراری**
- `get_context_data()`: 15 × ~20 خط = **~300 خط تکراری**
- **مجموع UpdateView**: **~750 خط تکراری**

#### ۹.۶.۴ DeleteView (15+ view)

- `delete()`: 15 × ~5 خط = **~75 خط تکراری**
- `get_context_data()`: 15 × ~15 خط = **~225 خط تکراری**
- **مجموع DeleteView**: **~300 خط تکراری**

#### ۹.۶.۵ مجموع کل

**تکرار کد در ماژول `inventory`**: **~4,630 خط کد تکراری**

**با Base classes**: این مقدار به **~800 خط** کاهش می‌یابد (فقط override کردن متدها)

**صرفه‌جویی**: **~3,830 خط کد** (83% کاهش)

---

### ۹.۷ چیزهایی که می‌توان مشترک کرد

#### ۹.۷.۱ BaseListView برای Master Data

**وظایف**:
1. منطق `get_queryset()` مشترک:
   - فیلتر بر اساس permissions
   - فیلتر بر اساس search
   - فیلتر بر اساس status
   - مرتب‌سازی

2. تنظیم context در `get_context_data()`:
   - تمام context variables استاندارد
   - پشتیبانی از override کردن

**Attributes قابل تنظیم**:
```python
class ItemTypeListView(BaseListView):
    model = ItemType
    search_fields = ['name', 'public_code']
    filter_fields = ['is_enabled']
    feature_code = 'inventory.master.item_types'
    permission_field = 'created_by'  # برای permission filtering
```

#### ۹.۷.۲ BaseListView برای Documents

**وظایف اضافی**:
1. Prefetch lines و related objects
2. Stats calculation
3. فیلترهای پیچیده‌تر (status, conversion, etc.)

**Attributes قابل تنظیم**:
```python
class ReceiptPermanentListView(BaseDocumentListView):
    model = ReceiptPermanent
    feature_code = 'inventory.receipts.permanent'
    prefetch_lines = True
    stats_enabled = True
    filter_fields = ['status', 'is_locked']
```

#### ۹.۷.۳ BaseCreateView / BaseUpdateView برای Documents

**وظایف**:
1. مدیریت `LineFormsetMixin`
2. تنظیم `company_id`, `created_by`, `edited_by`
3. ذخیره formset
4. نمایش پیام موفقیت

**Attributes قابل تنظیم**:
```python
class ReceiptPermanentCreateView(BaseDocumentCreateView):
    model = ReceiptPermanent
    form_class = ReceiptPermanentForm
    formset_class = ReceiptPermanentLineFormSet
    success_url = reverse_lazy('inventory:receipt_permanent')
    feature_code = 'inventory.receipts.permanent'
```

#### ۹.۷.۴ BaseDeleteView برای Documents

**وظایف**:
1. بررسی permission (`DELETE_OWN`, `DELETE_OTHER`)
2. محافظت از اسناد قفل‌شده
3. نمایش پیام موفقیت

**استفاده از `DocumentDeleteViewBase` موجود**: می‌توان به `BaseDeleteView` تبدیل شود

---

### ۹.۸ چالش‌های خاص ماژول `inventory`

#### ۹.۸.۱ Document Views با Formset

- **مشکل**: همه document views از `LineFormsetMixin` استفاده می‌کنند
- **راه‌حل**: BaseDocumentCreateView/UpdateView باید از `LineFormsetMixin` استفاده کنند

#### ۹.۸.۲ Stats Methods

- **مشکل**: برخی ListViewها stats دارند، برخی ندارند
- **راه‌حل**: BaseListView باید hook method داشته باشد:
```python
def get_stats(self):
    """Override to return stats dictionary."""
    return None  # Default: no stats
```

#### ۹.۸.۳ Permission Filtering

- **مشکل**: هر view از `filter_queryset_by_permissions()` استفاده می‌کند اما با fieldهای مختلف (`created_by`, `requested_by`, etc.)
- **راه‌حل**: BaseListView باید attribute `permission_field` داشته باشد

#### ۹.۸.۴ Prefetch Related

- **مشکل**: هر view prefetchهای متفاوتی دارد
- **راه‌حل**: BaseListView باید hook methods داشته باشد:
```python
def get_prefetch_related(self):
    """Override to return prefetch_related list."""
    return []

def get_select_related(self):
    """Override to return select_related list."""
    return []
```

---

### ۹.۹ نتیجه‌گیری برای ماژول `inventory`

✅ **ماژول `inventory` بزرگترین و پیچیده‌ترین ماژول است**:
- 81+ view (بیشترین تعداد)
- 4,630+ خط کد تکراری
- الگوهای متنوع (Master Data, Documents, Requests, Stocktaking)

✅ **پس از پیاده‌سازی Base classes**:
- کد از ~4,630 خط به ~800 خط کاهش می‌یابد (83% کاهش)
- توسعه view جدید بسیار سریع‌تر می‌شود
- نگهداری آسان‌تر می‌شود

⚠️ **چالش‌ها**:
- نیاز به Base classes مختلف برای انواع مختلف viewها:
  - `BaseListView` (برای Master Data)
  - `BaseDocumentListView` (برای Documents)
  - `BaseDocumentCreateView/UpdateView` (برای Documents با formset)
- نیاز به hook methods برای customization

---

## ۱۰. موارد مشترک دیگر (Beyond Views and Forms)

علاوه بر viewها و formها، موارد مشترک دیگری در پروژه وجود دارد که می‌توانند یکپارچه شوند.

---

### ۱۰.۱ Permission Checking Logic

#### ۱۰.۱.۱ تکرار در Base Views

**مشکل**: متد `filter_queryset_by_permissions()` در چندین base view تکرار شده است:

- `inventory/views/base.py` - `InventoryBaseView.filter_queryset_by_permissions()` (~80 خط)
- `accounting/views/base.py` - `AccountingBaseView.filter_queryset_by_permissions()` (~60 خط)
- احتمالاً در ماژول‌های دیگر هم تکرار شده

**الگوی مشترک**:
```python
def filter_queryset_by_permissions(self, queryset, feature_code: str, owner_field: str = 'created_by'):
    """Filter queryset based on user permissions."""
    if self.request.user.is_superuser:
        return queryset
    
    permissions = get_user_feature_permissions(...)
    can_view_all = has_feature_permission(..., 'view_all')
    can_view_own = has_feature_permission(..., 'view_own')
    can_view_same_group = has_feature_permission(..., 'view_same_group')
    
    # Build filter conditions
    # Apply filters
    return queryset.filter(...)
```

**راه‌حل**: ایجاد `PermissionFilterMixin` در `shared/mixins.py`:
```python
class PermissionFilterMixin:
    """Mixin for filtering queryset by permissions."""
    
    def filter_queryset_by_permissions(self, queryset, feature_code: str, owner_field: str = 'created_by'):
        # منطق مشترک
```

**صرفه‌جویی**: ~200 خط کد تکراری

---

### ۱۰.۲ Success Messages

#### ۱۰.۲.۱ تکرار در همه Viewها

**مشکل**: همه CreateView/UpdateView/DeleteView از `messages.success()` استفاده می‌کنند:

- **361 بار** استفاده از `messages.success()` در 52 فایل
- پیام‌های مشابه در viewهای مشابه

**الگوی مشترک**:
```python
def form_valid(self, form):
    # ... save logic ...
    messages.success(self.request, _('... created/updated successfully.'))
    return super().form_valid(form)

def delete(self, request, *args, **kwargs):
    messages.success(self.request, _('... deleted successfully.'))
    return super().delete(request, *args, **kwargs)
```

**راه‌حل**: Base classes باید به صورت خودکار پیام موفقیت را نمایش دهند:

```python
class BaseCreateView(CreateView):
    success_message = None  # Override in subclass
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response
```

**صرفه‌جویی**: حذف ~300 خط کد تکراری

---

### ۱۰.۳ Company/User Field Setting

#### ۱۰.۳.۱ تکرار در همه CreateView/UpdateView

**مشکل**: همه CreateView/UpdateView این منطق را تکرار می‌کنند:

- **240 بار** استفاده از `form.instance.company_id = ...`
- **240 بار** استفاده از `form.instance.created_by = ...`
- **240 بار** استفاده از `form.instance.edited_by = ...`

**الگوی مشترک**:
```python
def form_valid(self, form):
    form.instance.company_id = self.request.session.get('active_company_id')
    form.instance.created_by = self.request.user  # CreateView
    form.instance.edited_by = self.request.user    # UpdateView
    return super().form_valid(form)
```

**راه‌حل**: Base classes باید به صورت خودکار این فیلدها را تنظیم کنند:

```python
class BaseCreateView(CreateView):
    auto_set_company = True
    auto_set_created_by = True
    
    def form_valid(self, form):
        if self.auto_set_company:
            form.instance.company_id = self.request.session.get('active_company_id')
        if self.auto_set_created_by:
            form.instance.created_by = self.request.user
        return super().form_valid(form)
```

**صرفه‌جویی**: حذف ~720 خط کد تکراری

---

### ۱۰.۴ Form Widget Styling

#### ۱۰.۴.۱ تکرار در همه Formها

**مشکل**: همه formها از CSS classهای یکسان استفاده می‌کنند:

- **728 بار** استفاده از `'class': 'form-control'` در 87 فایل
- **728 بار** استفاده از `'class': 'form-check-input'` برای checkboxها

**الگوی مشترک**:
```python
widgets = {
    'field_name': forms.TextInput(attrs={'class': 'form-control'}),
    'is_enabled': forms.Select(attrs={'class': 'form-control'}),
    'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
}
```

**راه‌حل**: ایجاد Base Form Classes:

```python
class BaseModelForm(forms.ModelForm):
    """Base form with default widget styling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply default styling to all fields
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            else:
                field.widget.attrs.setdefault('class', 'form-control')
```

**صرفه‌جویی**: حذف ~1,500 خط کد تکراری در widget definitions

---

### ۱۰.۵ Stats Calculation Methods

#### ۱۰.۵.۱ تکرار در ListViewها

**مشکل**: متد `_get_stats()` در چندین ListView تکرار شده است:

- `ReceiptTemporaryListView._get_stats()`
- `IssuePermanentListView._get_stats()`
- `PurchaseRequestListView._get_stats()`
- `WarehouseRequestListView._get_stats()`
- و چندین view دیگر

**الگوی مشترک**:
```python
def _get_stats(self) -> Dict[str, int]:
    """Return aggregate stats for summary cards."""
    stats = {'total': 0, 'draft': 0, ...}
    company_id = self.request.session.get('active_company_id')
    if not company_id:
        return stats
    base_qs = Model.objects.filter(company_id=company_id)
    stats['total'] = base_qs.count()
    # ... more stats
    return stats
```

**راه‌حل**: BaseListView باید hook method داشته باشد:

```python
class BaseListView(ListView):
    stats_enabled = False
    stats_fields = []  # List of stat field names
    
    def get_stats(self):
        """Override to return stats dictionary."""
        if not self.stats_enabled:
            return None
        # Default implementation
        return {}
```

**صرفه‌جویی**: حذف ~150 خط کد تکراری

---

### ۱۰.۶ Filter Methods

#### ۱۰.۶.۱ تکرار در ListViewها

**مشکل**: متد `_apply_filters()` در چندین ListView تکرار شده است:

- `ReceiptTemporaryListView._apply_filters()`
- و احتمالاً در viewهای دیگر

**الگوی مشترک**:
```python
def _apply_filters(self, queryset):
    """Apply status, search, and other filters."""
    status_param = self.request.GET.get('status')
    if status_param:
        queryset = queryset.filter(status=status_param)
    
    search_query = self.request.GET.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(Q(...) | Q(...))
    
    return queryset
```

**راه‌حل**: BaseListView باید filter logic مشترک داشته باشد:

```python
class BaseListView(ListView):
    filter_fields = []  # List of filter field names
    search_fields = []  # List of searchable field names
    
    def apply_filters(self, queryset):
        """Apply filters based on request.GET."""
        # Apply status filter
        # Apply search filter
        return queryset
```

**صرفه‌جویی**: حذف ~200 خط کد تکراری

---

### ۱۰.۷ Base View Classes

#### ۱۰.۷.۱ تکرار منطق Company Filtering

**مشکل**: چندین base view class منطق مشابه دارند:

- `InventoryBaseView` - فیلتر بر اساس `active_company_id`
- `AccountingBaseView` - فیلتر بر اساس `active_company_id`
- احتمالاً در ماژول‌های دیگر هم تکرار شده

**الگوی مشترک**:
```python
class ModuleBaseView(LoginRequiredMixin):
    def get_queryset(self):
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id and hasattr(queryset.model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'module_name'
        return context
```

**راه‌حل**: ایجاد `CompanyScopedViewMixin` در `shared/mixins.py`:

```python
class CompanyScopedViewMixin:
    """Mixin for views that filter by active company."""
    
    def get_queryset(self):
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id and hasattr(queryset.model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        return queryset
```

**صرفه‌جویی**: حذف ~100 خط کد تکراری

---

### ۱۰.۸ Validation Logic

#### ۱۰.۸.۱ تکرار در Formها

**مشکل**: برخی validation logic در formهای مختلف تکرار می‌شود:

- بررسی `active_company_id` در CreateView
- بررسی `is_locked` در UpdateView
- بررسی permission در DeleteView

**الگوی مشترک**:
```python
def form_valid(self, form):
    active_company_id = self.request.session.get('active_company_id')
    if not active_company_id:
        messages.error(self.request, _('Please select a company first.'))
        return self.form_invalid(form)
    # ... rest of logic
```

**راه‌حل**: Base classes باید validation مشترک داشته باشند:

```python
class BaseCreateView(CreateView):
    require_active_company = True
    
    def validate_company(self):
        """Validate active company exists."""
        if self.require_active_company:
            company_id = self.request.session.get('active_company_id')
            if not company_id:
                messages.error(self.request, _('Please select a company first.'))
                return False
        return True
    
    def form_valid(self, form):
        if not self.validate_company():
            return self.form_invalid(form)
        return super().form_valid(form)
```

**صرفه‌جویی**: حذف ~100 خط کد تکراری

---

### ۱۰.۹ آمار تکرار کد (موارد مشترک دیگر)

#### ۱۰.۹.۱ مجموع تکرار

| مورد | تعداد تکرار | تخمین خط کد |
|------|-------------|-------------|
| Permission checking logic | 3+ base views | ~200 خط |
| Success messages | 361 بار | ~300 خط |
| Company/User field setting | 240 بار | ~720 خط |
| Form widget styling | 728 بار | ~1,500 خط |
| Stats calculation | 10+ views | ~150 خط |
| Filter methods | 5+ views | ~200 خط |
| Base view classes | 3+ modules | ~100 خط |
| Validation logic | 20+ views | ~100 خط |
| **مجموع** | | **~3,270 خط** |

**با Base classes و Mixinها**: این مقدار به **~500 خط** کاهش می‌یابد

**صرفه‌جویی**: **~2,770 خط کد** (85% کاهش)

---

### ۱۰.۱۰ DetailView Patterns

#### ۱۰.۱۰.۱ تکرار در DetailViewها

**مشکل**: 44+ DetailView در پروژه وجود دارد که الگوهای مشترک دارند:

**الگوی مشترک**:
```python
class ItemTypeDetailView(InventoryBaseView, DetailView):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(...)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('View ...')
        context['breadcrumbs'] = [...]
        context['list_url'] = reverse_lazy('...')
        context['edit_url'] = reverse_lazy('...')
        context['can_edit'] = not getattr(self.object, 'is_locked', 0)
        context['feature_code'] = '...'
        return context
```

**تخمین**: هر DetailView ~25-30 خط کد تکراری

**راه‌حل**: ایجاد `BaseDetailView` در `shared/views/base.py`:
```python
class BaseDetailView(DetailView):
    """Base detail view with common context setup."""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_page_title()
        context['breadcrumbs'] = self.get_breadcrumbs()
        context['list_url'] = self.get_list_url()
        context['edit_url'] = self.get_edit_url()
        context['can_edit'] = self.can_edit_object()
        return context
```

**صرفه‌جویی**: حذف ~1,100 خط کد تکراری (44 × ~25 خط)

---

### ۱۰.۱۱ JavaScript Patterns مشترک

#### ۱۰.۱۱.۱ Formset Management

**مشکل**: JavaScript برای مدیریت formset در چندین template تکرار شده است:

- `addFormsetRow()` - اضافه کردن ردیف جدید
- `removeFormsetRow()` - حذف ردیف
- `updateFormsetTotal()` - به‌روزرسانی `TOTAL_FORMS`
- `reindexFormset()` - بازنشانی index ردیف‌ها

**الگوی مشترک**:
```javascript
function addFormsetRow(prefix) {
    const totalForms = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
    const formCount = parseInt(totalForms.value);
    // Clone template row
    // Update indices
    // Increment TOTAL_FORMS
}

function removeFormsetRow(button) {
    const row = button.closest('tr');
    row.remove();
    updateFormsetTotal(prefix);
    reindexFormset(prefix);
}
```

**استفاده**: در 18+ template (BOM, Process, Receipt, Issue, PerformanceRecord, etc.)

**راه‌حل**: ایجاد `static/js/formset.js` با توابع مشترک

**صرفه‌جویی**: حذف ~500 خط کد JavaScript تکراری

---

#### ۱۰.۱۱.۲ Cascading Dropdowns

**مشکل**: منطق cascading dropdowns در چندین template تکرار شده است:

- Item Type → Category → Subcategory → Item
- Warehouse → Item Units
- BOM → Materials

**الگوی مشترک**:
```javascript
function updateCategoryDropdown(itemTypeId) {
    fetch(`/api/categories/?item_type=${itemTypeId}`)
        .then(response => response.json())
        .then(data => {
            const categorySelect = document.getElementById('id_category');
            categorySelect.innerHTML = '<option value="">---</option>';
            data.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.name;
                categorySelect.appendChild(option);
            });
        });
}
```

**راه‌حل**: ایجاد `static/js/cascading-dropdowns.js` با توابع مشترک

**صرفه‌جویی**: حذف ~300 خط کد JavaScript تکراری

---

#### ۱۰.۱۱.۳ Table Export

**مشکل**: تابع `exportToExcel()` در چندین template تکرار شده است:

**الگوی مشترک**:
```javascript
function exportToExcel(tableId) {
    const table = document.getElementById(tableId);
    // Convert to CSV
    // Trigger download
}
```

**راه‌حل**: ایجاد `static/js/table-export.js`

**صرفه‌جویی**: حذف ~100 خط کد JavaScript تکراری

---

### ۱۰.۱۲ Template Patterns مشترک

#### ۱۰.۱۲.۱ Breadcrumb Pattern

**مشکل**: الگوی breadcrumb در همه templateها تکرار شده است:

**الگوی مشترک**:
```django
<nav class="breadcrumb">
  <a href="{% url 'ui:dashboard' %}">{% trans "Dashboard" %}</a>
  {% for crumb in breadcrumbs %}
    <span class="separator">/</span>
    {% if crumb.url %}
      <a href="{{ crumb.url }}">{{ crumb.label }}</a>
    {% else %}
      <span>{{ crumb.label }}</span>
    {% endif %}
  {% endfor %}
</nav>
```

**راه‌حل**: این الگو در `generic_list.html` و `generic_form.html` و `generic_detail.html` موجود است ✅

---

#### ۱۰.۱۲.۲ Message Display Pattern

**مشکل**: الگوی نمایش messages در همه templateها تکرار شده است:

**الگوی مشترک**:
```django
{% if messages %}
  {% for message in messages %}
    <div class="alert alert-{{ message.tags }}" style="...">
      {{ message }}
    </div>
  {% endfor %}
{% endif %}
```

**راه‌حل**: این الگو در base templates موجود است ✅

---

#### ۱۰.۱۲.۳ Empty State Pattern

**مشکل**: الگوی empty state در ListViewها تکرار شده است:

**الگوی مشترک**:
```django
{% if object_list %}
  <!-- Table -->
{% else %}
  <div class="empty-state">
    <div class="empty-state-icon">{{ empty_state_icon|default:"📋" }}</div>
    <h3>{{ empty_state_title|default:"No Items Found" }}</h3>
    <p>{{ empty_state_message|default:"Start by creating..." }}</p>
  </div>
{% endif %}
```

**راه‌حل**: این الگو در `generic_list.html` موجود است ✅

---

#### ۱۰.۱۲.۴ Pagination Pattern

**مشکل**: الگوی pagination در ListViewها تکرار شده است:

**الگوی مشترک**:
```django
{% if is_paginated %}
  <div class="pagination">
    {% if page_obj.has_previous %}
      <a href="?page={{ page_obj.previous_page_number }}">Previous</a>
    {% endif %}
    <!-- Page numbers -->
    {% if page_obj.has_next %}
      <a href="?page={{ page_obj.next_page_number }}">Next</a>
    {% endif %}
  </div>
{% endif %}
```

**راه‌حل**: این الگو در `generic_list.html` موجود است ✅

---

### ۱۰.۱۳ API Endpoints Patterns

#### ۱۰.۱۳.۱ تکرار در API Views

**مشکل**: الگوهای مشترک در API endpoints:

- JSON response format
- Error handling
- Permission checks
- Company filtering

**الگوی مشترک**:
```python
def get_categories(request):
    company_id = request.session.get('active_company_id')
    item_type_id = request.GET.get('item_type_id')
    
    if not company_id:
        return JsonResponse({'error': 'No company selected'}, status=400)
    
    categories = ItemCategory.objects.filter(company_id=company_id)
    if item_type_id:
        categories = categories.filter(...)
    
    data = [{'id': c.id, 'name': c.name} for c in categories]
    return JsonResponse({'results': data})
```

**تخمین**: 230+ API endpoint در پروژه

**راه‌حل**: ایجاد `BaseAPIView` در `shared/views/api.py`:
```python
class BaseAPIView(View):
    """Base API view with common patterns."""
    
    def get_company_id(self):
        return self.request.session.get('active_company_id')
    
    def json_response(self, data, status=200):
        return JsonResponse(data, status=status)
    
    def error_response(self, message, status=400):
        return JsonResponse({'error': message}, status=status)
```

**صرفه‌جویی**: حذف ~500 خط کد تکراری

---

### ۱۰.۱۴ آمار تکرار کد (موارد مشترک دیگر - به‌روزرسانی)

#### ۱۰.۱۴.۱ مجموع تکرار (به‌روزرسانی)

| مورد | تعداد تکرار | تخمین خط کد |
|------|-------------|-------------|
| Permission checking logic | 3+ base views | ~200 خط |
| Success messages | 361 بار | ~300 خط |
| Company/User field setting | 240 بار | ~720 خط |
| Form widget styling | 728 بار | ~1,500 خط |
| Stats calculation | 10+ views | ~150 خط |
| Filter methods | 5+ views | ~200 خط |
| Base view classes | 3+ modules | ~100 خط |
| Validation logic | 20+ views | ~100 خط |
| **DetailView patterns** | **44+ views** | **~1,100 خط** |
| **JavaScript formset** | **18+ templates** | **~500 خط** |
| **JavaScript cascading** | **10+ templates** | **~300 خط** |
| **JavaScript table export** | **5+ templates** | **~100 خط** |
| **API endpoints** | **230+ endpoints** | **~500 خط** |
| **مجموع** | | **~6,270 خط** |

**با Base classes و Mixinها و JavaScript مشترک**: این مقدار به **~800 خط** کاهش می‌یابد

**صرفه‌جویی**: **~5,470 خط کد** (87% کاهش)

---

### ۱۰.۱۵ نتیجه‌گیری برای موارد مشترک دیگر

✅ **موارد مشترک زیادی وجود دارد** که می‌توانند یکپارچه شوند:
- Permission checking logic
- Success messages
- Company/User field setting
- Form widget styling
- Stats calculation
- Filter methods
- Base view classes
- Validation logic
- **DetailView patterns** (جدید)
- **JavaScript patterns** (جدید)
- **API endpoints patterns** (جدید)

✅ **پس از یکپارچه‌سازی**:
- کد از ~6,270 خط به ~800 خط کاهش می‌یابد (87% کاهش)
- نگهداری بسیار آسان‌تر می‌شود
- تغییرات فقط در یک جا اعمال می‌شوند
- JavaScript مشترک باعث یکپارچگی UX می‌شود

---

## ۱۱. بررسی دقیق ماژول `production` (تولید)

این بخش شامل بررسی کامل ماژول `production` به عنوان یکی از ماژول‌های پیچیده پروژه است.

---

### ۱۱.۱ ساختار ماژول `production`

**فایل‌های View** (13 فایل):
- `production/views/personnel.py` - 5 view (Person CRUD)
- `production/views/machine.py` - 5 view (Machine CRUD)
- `production/views/work_line.py` - 5 view (WorkLine CRUD)
- `production/views/bom.py` - 4 view (BOM CRUD)
- `production/views/process.py` - 4 view (Process CRUD)
- `production/views/product_order.py` - 4 view (ProductOrder CRUD)
- `production/views/transfer_to_line.py` - 6 view (TransferToLine CRUD + Approve/Reject)
- `production/views/performance_record.py` - 7 view (PerformanceRecord CRUD + Approve/Reject + CreateReceipt)
- `production/views/rework.py` - 4 view (ReworkDocument CRUD)
- `production/views/qc_operations.py` - 3 view (QC Operations List + Approve/Reject)
- `production/views/api.py` - JSON API endpoints
- `production/views/placeholders.py` - Placeholder views

**کل**: **41+ view**

**فایل‌های Form** (10 فایل):
- `production/forms/person.py` - PersonForm
- `production/forms/machine.py` - MachineForm
- `production/forms/work_line.py` - WorkLineForm
- `production/forms/bom.py` - BOMForm + BOMMaterialLineFormSet
- `production/forms/process.py` - ProcessForm + ProcessOperationFormSet
- `production/forms/product_order.py` - ProductOrderForm
- `production/forms/transfer_to_line.py` - TransferToLineForm + TransferToLineItemFormSet
- `production/forms/performance_record.py` - PerformanceRecordForm + Multiple Formsets

**نکته مهم**: ماژول `production` **هیچ base view class ندارد** (برخلاف `inventory` که `InventoryBaseView` دارد)

---

### ۱۱.۲ الگوهای مشترک در ListViewها

#### ۱۱.۲.۱ تکرار در `get_queryset()`

**الگوی مشترک در همه ListViewها**:

```python
def get_queryset(self):
    active_company_id = self.request.session.get('active_company_id')
    if not active_company_id:
        return Model.objects.none()
    
    queryset = Model.objects.filter(company_id=active_company_id)
    # ... prefetch/select_related ...
    # ... search filter ...
    # ... status filter ...
    return queryset.order_by(...)
```

**تفاوت‌ها**:
- **Simple Views** (Personnel, Machine, WorkLine): فیلتر ساده (search, status)
- **Complex Views** (BOM, Process, ProductOrder): prefetch related objects
- **Document Views** (TransferToLine, PerformanceRecord): prefetch lines + permission filtering
- **Special Views** (QCOperations): فیلتر پیچیده بر اساس conditions

**تخمین**: هر ListView ~30-50 خط کد تکراری در `get_queryset()`

#### ۱۱.۲.۲ تکرار در `get_context_data()`

**الگوی مشترک**:

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['page_title'] = _('...')
    context['breadcrumbs'] = [
        {'label': _('Production'), 'url': None},
        {'label': _('...'), 'url': None},
    ]
    context['create_url'] = reverse_lazy('production:..._create')
    context['create_button_text'] = _('Create ...')
    context['show_filters'] = True/False
    context['show_actions'] = True
    context['feature_code'] = 'production....'
    context['detail_url_name'] = 'production:..._detail'
    context['edit_url_name'] = 'production:..._edit'
    context['delete_url_name'] = 'production:..._delete'
    context['empty_state_title'] = _('No ... Found')
    context['empty_state_message'] = _('Start by creating...')
    context['empty_state_icon'] = '...'
    return context
```

**تخمین**: هر ListView ~40-60 خط کد تکراری در `get_context_data()`

#### ۱۱.۲.۳ Permission Checking در ListView

**الگوی مشترک**: برخی ListViewها permission checking دارند:

```python
# Check if user has view_all permission
permissions = get_user_feature_permissions(self.request.user, active_company_id)
if not has_feature_permission(permissions, 'production....', action='view_all'):
    queryset = queryset.filter(created_by=self.request.user)
```

**استفاده**: در `PerformanceRecordListView`, `ReworkDocumentListView`

---

### ۱۱.۳ الگوهای مشترک در CreateView/UpdateView

#### ۱۱.۳.۱ Simple Views (Personnel, Machine, WorkLine)

**الگوی مشترک**:
```python
class PersonCreateView(FeaturePermissionRequiredMixin, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(...)
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        messages.success(...)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create ...')
        context['breadcrumbs'] = [...]
        context['cancel_url'] = reverse_lazy('production:...')
        return context
```

**تخمین**: هر CreateView/UpdateView ~30-40 خط کد تکراری

#### ۱۱.۳.۲ Formset Views (BOM, Process, PerformanceRecord, TransferToLine)

**الگوی مشترک**:
```python
class BOMCreateView(FeaturePermissionRequiredMixin, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Create formset
        if self.request.POST:
            context['formset'] = FormSet(self.request.POST, ...)
        else:
            context['formset'] = FormSet(...)
        return context
    
    @transaction.atomic
    def form_valid(self, form):
        # Save main object
        self.object = form.save()
        # Save formset
        formset = FormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            formset.save()
        else:
            # Handle errors
        messages.success(...)
        return HttpResponseRedirect(...)
```

**تخمین**: هر CreateView/UpdateView با formset ~60-100 خط کد تکراری

#### ۱۱.۳.۳ Complex Views (ProductOrder, TransferToLine)

**الگوی مشترک**: این viewها منطق پیچیده‌تری دارند:
- Auto-set fields از related objects
- ایجاد multiple objects
- Workflow logic

**مثال**: `ProductOrderCreateView`:
- Auto-set `finished_item` از `BOM`
- Auto-generate `order_code`
- ایجاد `TransferToLine` (optional)
- ~200+ خط کد

---

### ۱۱.۴ الگوهای مشترک در DeleteView

**الگوی مشترک**:
```python
class PersonDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    template_name = 'shared/generic/generic_confirm_delete.html'
    
    def get_queryset(self):
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Model.objects.none()
        return Model.objects.filter(company_id=active_company_id)
    
    def delete(self, request, *args, **kwargs):
        messages.success(...)
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete ...')
        context['confirmation_message'] = _('Are you sure...')
        context['object_details'] = [...]
        context['cancel_url'] = reverse_lazy('production:...')
        context['breadcrumbs'] = [...]
        return context
```

**تخمین**: هر DeleteView ~25-30 خط کد تکراری

---

### ۱۱.۵ Approval Workflow Views

#### ۱۱.۵.۱ Approve/Reject Views

**الگوی مشترک**: در `TransferToLine`, `PerformanceRecord`, `QCOperations`:

```python
class TransferToLineApproveView(FeaturePermissionRequiredMixin, View):
    feature_code = 'production.transfer_requests'
    required_action = 'approve'
    
    def post(self, request, pk):
        # Get object
        # Check permissions
        # Update status
        # Set approved_by
        # Save
        messages.success(...)
        return JsonResponse(...)
```

**تخمین**: هر Approve/Reject view ~30-40 خط کد تکراری

---

### ۱۱.۶ آمار تکرار کد در ماژول `production`

#### ۱۱.۶.۱ ListView (10+ view)

- `get_queryset()`: 10 × ~40 خط = **~400 خط تکراری**
- `get_context_data()`: 10 × ~50 خط = **~500 خط تکراری**
- Permission checking: 3 × ~15 خط = **~45 خط تکراری**
- **مجموع ListView**: **~945 خط تکراری**

#### ۱۱.۶.۲ CreateView (10+ view)

- `get_form_kwargs()`: 10 × ~5 خط = **~50 خط تکراری**
- `form_valid()`: 10 × ~30 خط = **~300 خط تکراری**
- `get_context_data()`: 10 × ~25 خط = **~250 خط تکراری**
- Formset handling: 4 × ~50 خط = **~200 خط تکراری**
- **مجموع CreateView**: **~800 خط تکراری**

#### ۱۱.۶.۳ UpdateView (10+ view)

- `get_form_kwargs()`: 10 × ~5 خط = **~50 خط تکراری**
- `form_valid()`: 10 × ~30 خط = **~300 خط تکراری**
- `get_context_data()`: 10 × ~25 خط = **~250 خط تکراری**
- Formset handling: 4 × ~50 خط = **~200 خط تکراری**
- **مجموع UpdateView**: **~800 خط تکراری**

#### ۱۱.۶.۴ DeleteView (10+ view)

- `get_queryset()`: 10 × ~10 خط = **~100 خط تکراری**
- `delete()`: 10 × ~5 خط = **~50 خط تکراری**
- `get_context_data()`: 10 × ~20 خط = **~200 خط تکراری**
- **مجموع DeleteView**: **~350 خط تکراری**

#### ۱۱.۶.۵ Approval Views (6+ view)

- Approve/Reject logic: 6 × ~35 خط = **~210 خط تکراری**

#### ۱۱.۶.۶ مجموع کل

**تکرار کد در ماژول `production`**: **~3,105 خط کد تکراری**

**با Base classes**: این مقدار به **~600 خط** کاهش می‌یابد (فقط override کردن متدها)

**صرفه‌جویی**: **~2,505 خط کد** (81% کاهش)

---

### ۱۱.۷ چیزهایی که می‌توان مشترک کرد

#### ۱۱.۷.۱ BaseListView

**وظایف**:
1. فیلتر بر اساس `active_company_id`
2. منطق `get_queryset()` مشترک
3. تنظیم context در `get_context_data()`
4. پشتیبانی از permission filtering

**Attributes قابل تنظیم**:
```python
class PersonnelListView(BaseListView):
    model = Person
    search_fields = ['public_code', 'first_name', 'last_name']
    filter_fields = ['is_enabled']
    feature_code = 'production.personnel'
    permission_field = 'created_by'  # برای permission filtering
```

#### ۱۱.۷.۲ BaseCreateView / BaseUpdateView

**وظایف**:
1. تنظیم `company_id`, `created_by`, `edited_by`
2. نمایش پیام موفقیت
3. تنظیم context (breadcrumbs, form_title, cancel_url)
4. پشتیبانی از `get_form_kwargs()` برای `company_id`

**Attributes قابل تنظیم**:
```python
class PersonCreateView(BaseCreateView):
    model = Person
    form_class = PersonForm
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
```

#### ۱۱.۷.۳ BaseFormsetCreateView / BaseFormsetUpdateView

**وظایف**:
1. مدیریت formset
2. Transaction safety
3. ذخیره formset با main object
4. Error handling

**Attributes قابل تنظیم**:
```python
class BOMCreateView(BaseFormsetCreateView):
    model = BOM
    form_class = BOMForm
    formset_class = BOMMaterialLineFormSet
    success_url = reverse_lazy('production:bom_list')
    feature_code = 'production.bom'
```

#### ۱۱.۷.۴ BaseDeleteView

**وظایف**:
1. تنظیم context برای `generic_confirm_delete.html`
2. نمایش پیام موفقیت
3. فیلتر بر اساس `active_company_id`

---

### ۱۱.۸ چالش‌های خاص ماژول `production`

#### ۱۱.۸.۱ عدم وجود Base View Class

- **مشکل**: ماژول `production` هیچ base view class ندارد (برخلاف `inventory`)
- **راه‌حل**: باید `ProductionBaseView` ایجاد شود یا از `BaseListView` در `shared` استفاده شود

#### ۱۱.۸.۲ Formset Management

- **مشکل**: 4+ view از formset استفاده می‌کنند (BOM, Process, PerformanceRecord, TransferToLine)
- **راه‌حل**: BaseFormsetCreateView/UpdateView باید ایجاد شود

#### ۱۱.۸.۳ Approval Workflow

- **مشکل**: 3+ view workflow approval دارند (TransferToLine, PerformanceRecord, QCOperations)
- **راه‌حل**: BaseApprovalView یا Mixin برای approve/reject logic

#### ۱۱.۸.۴ Complex Business Logic

- **مشکل**: برخی viewها منطق پیچیده دارند (ProductOrderCreateView ~200 خط)
- **راه‌حل**: این منطق باید در service layer قرار گیرد

#### ۱۱.۸.۵ Permission Checking در ListView

- **مشکل**: برخی ListViewها permission checking دارند، برخی ندارند
- **راه‌حل**: BaseListView باید hook method داشته باشد

---

### ۱۱.۹ نتیجه‌گیری برای ماژول `production`

✅ **ماژول `production` پیچیده است**:
- 41+ view (دومین ماژول بزرگ)
- 3,105+ خط کد تکراری
- الگوهای متنوع (Simple CRUD, Formset Views, Approval Workflow)

✅ **پس از پیاده‌سازی Base classes**:
- کد از ~3,105 خط به ~600 خط کاهش می‌یابد (81% کاهش)
- توسعه view جدید بسیار سریع‌تر می‌شود
- نگهداری آسان‌تر می‌شود

⚠️ **چالش‌ها**:
- نیاز به Base classes مختلف:
  - `BaseListView` (برای Simple views)
  - `BaseFormsetCreateView/UpdateView` (برای Formset views)
  - `BaseApprovalView` (برای Approval workflow)
- نیاز به service layer برای منطق پیچیده

---

## ۱۲. آمار کلی تکرار کد در تمام ماژول‌های بررسی شده

### ۱۲.۱ خلاصه ماژول‌ها

| ماژول | تعداد View | خط کد تکراری | صرفه‌جویی با Base Classes |
|-------|-----------|--------------|---------------------------|
| `shared` | 25+ | ~750 خط | ~600 خط (80%) |
| `inventory` | 81+ | ~4,630 خط | ~3,830 خط (83%) |
| `production` | 41+ | ~3,105 خط | ~2,505 خط (81%) |
| `accounting` | 28+ | ~1,435 خط | ~1,135 خط (79%) |
| `ticketing` | 19+ | ~1,000 خط | ~800 خط (80%) |
| `qc` | 6+ | ~160 خط | ~110 خط (69%) |
| **موارد مشترک دیگر** | - | ~6,270 خط | ~5,470 خط (87%) |
| **مجموع** | **200+** | **~18,055 خط** | **~15,455 خط (86%)** |

### ۱۲.۲ دسته‌بندی تکرار کد

#### ۱۲.۲.۱ View Layer

| نوع View | تعداد | خط کد تکراری |
|----------|-------|--------------|
| ListView | 50+ | ~3,500 خط |
| CreateView | 30+ | ~1,200 خط |
| UpdateView | 30+ | ~1,200 خط |
| DeleteView | 30+ | ~900 خط |
| Approval Views | 10+ | ~350 خط |
| **مجموع View Layer** | **150+** | **~7,150 خط** |

#### ۱۲.۲.۲ موارد مشترک دیگر

| مورد | خط کد تکراری |
|------|--------------|
| Permission checking logic | ~200 خط |
| Success messages | ~300 خط |
| Company/User field setting | ~720 خط |
| Form widget styling | ~1,500 خط |
| Stats calculation | ~150 خط |
| Filter methods | ~200 خط |
| Base view classes | ~100 خط |
| Validation logic | ~100 خط |
| **مجموع موارد مشترک** | **~3,270 خط** |

### ۱۲.۳ صرفه‌جویی کلی

**قبل از Base Classes**:
- **~18,055 خط** کد تکراری در 6 ماژول بررسی شده
- تکرار در 200+ view + 18+ template (JavaScript) + 230+ API endpoint
- نگهداری دشوار (تغییرات در 200+ جا)

**بعد از Base Classes**:
- **~2,600 خط** کد (فقط override کردن متدها)
- **صرفه‌جویی**: **~15,455 خط کد** (86% کاهش)
- نگهداری آسان (تغییرات فقط در Base classes و JavaScript مشترک)

---

## ۱۳. بررسی دقیق ماژول `accounting` (حسابداری)

این بخش شامل بررسی کامل ماژول `accounting` به عنوان یکی از ماژول‌های مهم پروژه است.

---

### ۱۳.۱ ساختار ماژول `accounting`

**فایل‌های View** (10 فایل):
- `accounting/views/base.py` - `AccountingBaseView` (base class)
- `accounting/views/accounts.py` - 5 view (Account CRUD)
- `accounting/views/tafsili_accounts.py` - 5 view (TafsiliAccount CRUD)
- `accounting/views/sub_accounts.py` - 5 view (SubAccount CRUD)
- `accounting/views/gl_accounts.py` - 5 view (GLAccount CRUD)
- `accounting/views/fiscal_years.py` - 5 view (FiscalYear CRUD)
- `accounting/views/tafsili_hierarchy.py` - 5 view (TafsiliHierarchy CRUD)
- `accounting/views/document_attachments.py` - 3 view (DocumentAttachment List + Download)
- `accounting/views/auth.py` - Authentication views

**کل**: **28+ view**

**فایل‌های Form** (13 فایل):
- `accounting/forms/accounts.py` - AccountForm
- `accounting/forms/tafsili_accounts.py` - TafsiliAccountForm
- `accounting/forms/sub_accounts.py` - SubAccountForm
- `accounting/forms/gl_accounts.py` - GLAccountForm
- `accounting/forms/fiscal_years.py` - FiscalYearForm
- `accounting/forms/tafsili_hierarchy.py` - TafsiliHierarchyForm
- و چندین form دیگر

**نکته مهم**: ماژول `accounting` **دارای base view class است**: `AccountingBaseView`

---

### ۱۳.۲ AccountingBaseView

#### ۱۳.۲.۱ ویژگی‌های Base View

**کلاس**: `AccountingBaseView(LoginRequiredMixin)`

**متدهای مشترک**:
1. `get_queryset()` - فیلتر بر اساس `active_company_id`
2. `get_context_data()` - اضافه کردن `active_module = 'accounting'`
3. `filter_queryset_by_permissions()` - فیلتر بر اساس permissions (~60 خط)

**مزیت**: این base view **قبلاً وجود دارد** و استفاده می‌شود، اما می‌تواند بهبود یابد.

---

### ۱۳.۳ الگوهای مشترک در ListViewها

#### ۱۳.۳.۱ تکرار در `get_queryset()`

**الگوی مشترک**:

```python
def get_queryset(self):
    queryset = super().get_queryset()
    queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
    
    search = self.request.GET.get('search', '').strip()
    status = self.request.GET.get('status', '')
    # ... other filters ...
    
    if search:
        queryset = queryset.filter(Q(...) | Q(...))
    
    if status in ('0', '1'):
        queryset = queryset.filter(is_enabled=int(status))
    else:
        queryset = queryset.filter(is_enabled=1)  # Default
    
    return queryset.order_by(...)
```

**تفاوت‌ها**:
- **Account Views**: فیلتر بر اساس `account_type`, `account_level`
- **Tafsili/Sub/GL Views**: فیلتر بر اساس `account_level` (1, 2, 3)
- **FiscalYear View**: فیلتر ساده (search, status)
- **TafsiliHierarchy View**: فیلتر بر اساس `level`, `parent_id`

**تخمین**: هر ListView ~40-50 خط کد تکراری در `get_queryset()`

#### ۱۳.۳.۲ تکرار در `get_context_data()`

**الگوی مشترک**:

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['page_title'] = _('...')
    context['breadcrumbs'] = [
        {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
        {'label': _('Accounting'), 'url': reverse('accounting:...')},
        {'label': _('...')},
    ]
    context['create_url'] = reverse('accounting:..._create')
    context['create_button_text'] = _('...')
    context['show_filters'] = True
    context['status_filter'] = True
    context['search_placeholder'] = _('...')
    context['clear_filter_url'] = reverse('accounting:...')
    context['print_enabled'] = True
    context['show_actions'] = True
    context['feature_code'] = 'accounting....'
    context['detail_url_name'] = 'accounting:..._detail'
    context['edit_url_name'] = 'accounting:..._edit'
    context['delete_url_name'] = 'accounting:..._delete'
    context['table_headers'] = [...]
    context['empty_state_title'] = _('...')
    context['empty_state_message'] = _('...')
    context['empty_state_icon'] = '...'
    return context
```

**تخمین**: هر ListView ~50-60 خط کد تکراری در `get_context_data()`

---

### ۱۳.۴ الگوهای مشترک در CreateView/UpdateView

#### ۱۳.۴.۱ Simple Views (Account, FiscalYear, TafsiliHierarchy)

**الگوی مشترک**:
```python
class AccountCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(...)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create ...')
        context['breadcrumbs'] = [...]
        context['cancel_url'] = reverse('accounting:...')
        return context
```

**تخمین**: هر CreateView/UpdateView ~30-35 خط کد تکراری

#### ۱۳.۴.۲ Account Level Views (GLAccount, SubAccount, TafsiliAccount)

**الگوی مشترک**: مشابه Simple Views، اما:
- `form.instance.account_level = 1/2/3` در `form_valid()`
- `get_queryset()` در UpdateView فیلتر بر اساس `account_level`

**تخمین**: هر CreateView/UpdateView ~35-40 خط کد تکراری

---

### ۱۳.۵ الگوهای مشترک در DeleteView

**الگوی مشترک**:
```python
class AccountDeleteView(FeaturePermissionRequiredMixin, AccountingBaseView, DeleteView):
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        # Validation checks
        if obj.is_system_account:
            messages.error(...)
            return HttpResponseRedirect(self.success_url)
        
        if obj.child_accounts.exists():
            messages.error(...)
            return HttpResponseRedirect(self.success_url)
        
        messages.success(...)
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete ...')
        context['confirmation_message'] = _('...')
        context['breadcrumbs'] = [...]
        context['object_details'] = [...]
        context['cancel_url'] = reverse('accounting:...')
        return context
```

**تخمین**: هر DeleteView ~30-35 خط کد تکراری

---

### ۱۳.۶ آمار تکرار کد در ماژول `accounting`

#### ۱۳.۶.۱ ListView (7+ view)

- `get_queryset()`: 7 × ~45 خط = **~315 خط تکراری**
- `get_context_data()`: 7 × ~55 خط = **~385 خط تکراری**
- **مجموع ListView**: **~700 خط تکراری**

#### ۱۳.۶.۲ CreateView (7+ view)

- `get_form_kwargs()`: 7 × ~5 خط = **~35 خط تکراری**
- `form_valid()`: 7 × ~10 خط = **~70 خط تکراری**
- `get_context_data()`: 7 × ~20 خط = **~140 خط تکراری**
- **مجموع CreateView**: **~245 خط تکراری**

#### ۱۳.۶.۳ UpdateView (7+ view)

- `get_form_kwargs()`: 7 × ~5 خط = **~35 خط تکراری**
- `form_valid()`: 7 × ~10 خط = **~70 خط تکراری**
- `get_context_data()`: 7 × ~20 خط = **~140 خط تکراری**
- **مجموع UpdateView**: **~245 خط تکراری**

#### ۱۳.۶.۴ DeleteView (7+ view)

- `delete()`: 7 × ~15 خط = **~105 خط تکراری**
- `get_context_data()`: 7 × ~20 خط = **~140 خط تکراری**
- **مجموع DeleteView**: **~245 خط تکراری**

#### ۱۳.۶.۵ مجموع کل

**تکرار کد در ماژول `accounting`**: **~1,435 خط کد تکراری**

**با Base classes بهبود یافته**: این مقدار به **~300 خط** کاهش می‌یابد (فقط override کردن متدها)

**صرفه‌جویی**: **~1,135 خط کد** (79% کاهش)

---

### ۱۳.۷ چیزهایی که می‌توان مشترک کرد

#### ۱۳.۷.۱ بهبود AccountingBaseView

**وضعیت فعلی**: `AccountingBaseView` وجود دارد اما می‌تواند بهبود یابد

**پیشنهادات**:
1. اضافه کردن `search_fields` و `filter_fields` attributes
2. اضافه کردن `default_status_filter = True`
3. اضافه کردن `default_order_by` attribute

#### ۱۳.۷.۲ BaseListView

**وظایف**:
1. استفاده از `AccountingBaseView.filter_queryset_by_permissions()`
2. منطق `get_queryset()` مشترک (search, status, filters)
3. تنظیم context در `get_context_data()`

**Attributes قابل تنظیم**:
```python
class AccountListView(BaseListView):
    model = Account
    search_fields = ['account_code', 'account_name', 'account_name_en']
    filter_fields = ['is_enabled', 'account_type', 'account_level']
    default_status_filter = True
    default_order_by = 'account_code'
    feature_code = 'accounting.accounts'
```

#### ۱۳.۷.۳ BaseCreateView / BaseUpdateView

**وظایف**:
1. تنظیم `company_id` در `get_form_kwargs()`
2. تنظیم `created_by` / `edited_by`
3. نمایش پیام موفقیت
4. تنظیم context (breadcrumbs, form_title, cancel_url)

#### ۱۳.۷.۴ BaseDeleteView

**وظایف**:
1. Validation checks (system account, child accounts)
2. تنظیم context برای `generic_confirm_delete.html`
3. نمایش پیام موفقیت

---

### ۱۳.۸ چالش‌های خاص ماژول `accounting`

#### ۱۳.۸.۱ Account Level Filtering

- **مشکل**: GLAccount (level 1), SubAccount (level 2), TafsiliAccount (level 3) همه از model `Account` استفاده می‌کنند
- **راه‌حل**: BaseListView باید `default_filter` attribute داشته باشد

#### ۱۳.۸.۲ System Account Protection

- **مشکل**: DeleteView باید بررسی کند که account سیستم نیست
- **راه‌حل**: BaseDeleteView باید hook method داشته باشد

#### ۱۳.۸.۳ Child Account Validation

- **مشکل**: DeleteView باید بررسی کند که account دارای child accounts نیست
- **راه‌حل**: BaseDeleteView باید hook method داشته باشد

#### ۱۳.۸.۴ Permission Filtering

- **مشکل**: `filter_queryset_by_permissions()` در `AccountingBaseView` وجود دارد اما در همه viewها استفاده نمی‌شود
- **راه‌حل**: BaseListView باید به صورت خودکار از این متد استفاده کند

---

### ۱۳.۹ نتیجه‌گیری برای ماژول `accounting`

✅ **ماژول `accounting` نسبتاً ساده است**:
- 28+ view
- 1,435+ خط کد تکراری
- Base view class وجود دارد (`AccountingBaseView`)

✅ **پس از بهبود Base classes**:
- کد از ~1,435 خط به ~300 خط کاهش می‌یابد (79% کاهش)
- توسعه view جدید بسیار سریع‌تر می‌شود
- نگهداری آسان‌تر می‌شود

⚠️ **چالش‌ها**:
- نیاز به بهبود `AccountingBaseView`
- نیاز به Base classes برای ListView, CreateView, UpdateView, DeleteView
- نیاز به پشتیبانی از Account Level Filtering

---

## ۱۴. بررسی دقیق ماژول‌های `ticketing` و `qc`

این بخش شامل بررسی کامل ماژول‌های `ticketing` و `qc` است.

---

### ۱۴.۱ ماژول `ticketing` (تیکتینگ)

#### ۱۴.۱.۱ ساختار ماژول

**فایل‌های View** (9 فایل):
- `ticketing/views/base.py` - `TicketingBaseView` + `TicketLockProtectedMixin`
- `ticketing/views/categories.py` - 5 view (TicketCategory CRUD)
- `ticketing/views/subcategories.py` - 5 view (TicketSubcategory CRUD)
- `ticketing/views/templates.py` - 5 view (TicketTemplate CRUD)
- `ticketing/views/tickets.py` - 4 view (Ticket List, Create, Detail, Edit)
- `ticketing/views/entity_reference.py` - API views
- `ticketing/views/debug.py` - Debug views
- `ticketing/views/placeholders.py` - Placeholder views

**کل**: **19+ view**

**فایل‌های Form** (4 فایل):
- `ticketing/forms/categories.py` - TicketCategoryForm + TicketCategoryPermissionFormSet
- `ticketing/forms/templates.py` - TicketTemplateForm + Multiple Formsets
- `ticketing/forms/tickets.py` - Ticket forms
- `ticketing/forms/base.py` - Base forms

**نکته مهم**: ماژول `ticketing` **دارای base view class است**: `TicketingBaseView`

---

#### ۱۴.۱.۲ TicketingBaseView

**کلاس**: `TicketingBaseView(LoginRequiredMixin)`

**متدهای مشترک**:
1. `get_queryset()` - فیلتر بر اساس `active_company_id`
2. `get_context_data()` - اضافه کردن `active_module = 'ticketing'`

**مزیت**: این base view **قبلاً وجود دارد** و استفاده می‌شود.

---

#### ۱۴.۱.۳ الگوهای مشترک در ListViewها

**الگوی مشترک**:

```python
def get_queryset(self):
    company_id = self.request.session.get("active_company_id")
    queryset = Model.objects.filter(company_id=company_id)
    
    search = self.request.GET.get("search", "")
    if search:
        queryset = queryset.filter(Q(...) | Q(...))
    
    # Additional filters
    return queryset.order_by(...)
```

**تخمین**: هر ListView ~30-40 خط کد تکراری در `get_queryset()`

**الگوی مشترک در `get_context_data()`**:

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["page_title"] = _("...")
    context["breadcrumbs"] = [...]
    context["create_url"] = reverse_lazy("ticketing:..._create")
    context["create_button_text"] = _("...")
    context["show_filters"] = True
    context["show_actions"] = True
    context["feature_code"] = "ticketing...."
    # ... more context
    return context
```

**تخمین**: هر ListView ~40-50 خط کد تکراری در `get_context_data()`

---

#### ۱۴.۱.۴ الگوهای مشترک در CreateView/UpdateView

**الگوی مشترک**:
```python
class TicketCategoryCreateView(FeaturePermissionRequiredMixin, TicketingBaseView, CreateView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # یا company_id
        return kwargs
    
    def form_valid(self, form):
        company_id = self.request.session.get("active_company_id")
        if company_id:
            form.instance.company_id = company_id
        messages.success(...)
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Create ...")
        context["breadcrumbs"] = [...]
        context["cancel_url"] = reverse_lazy("ticketing:...")
        # Formset handling
        return context
```

**تخمین**: هر CreateView/UpdateView ~35-45 خط کد تکراری

**نکته**: برخی viewها (Category, Template) از **formset** استفاده می‌کنند که کد بیشتری نیاز دارد.

---

#### ۱۴.۱.۵ الگوهای مشترک در DeleteView

**الگوی مشترک**:
```python
class TicketCategoryDeleteView(FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView):
    def get_queryset(self):
        company_id = self.request.session.get("active_company_id")
        return Model.objects.filter(company_id=company_id)
    
    def delete(self, request, *args, **kwargs):
        messages.success(...)
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delete_title"] = _("Delete ...")
        context["confirmation_message"] = _("...")
        context["object_details"] = [...]
        context["cancel_url"] = reverse_lazy("ticketing:...")
        return context
```

**تخمین**: هر DeleteView ~25-30 خط کد تکراری

---

#### ۱۴.۱.۶ آمار تکرار کد در ماژول `ticketing`

**ListView** (4+ view):
- `get_queryset()`: 4 × ~35 خط = **~140 خط تکراری**
- `get_context_data()`: 4 × ~45 خط = **~180 خط تکراری**
- **مجموع ListView**: **~320 خط تکراری**

**CreateView** (4+ view):
- `get_form_kwargs()`: 4 × ~5 خط = **~20 خط تکراری**
- `form_valid()`: 4 × ~15 خط = **~60 خط تکراری**
- `get_context_data()`: 4 × ~25 خط = **~100 خط تکراری**
- Formset handling: 2 × ~50 خط = **~100 خط تکراری**
- **مجموع CreateView**: **~280 خط تکراری**

**UpdateView** (4+ view):
- `get_form_kwargs()`: 4 × ~5 خط = **~20 خط تکراری**
- `form_valid()`: 4 × ~15 خط = **~60 خط تکراری**
- `get_context_data()`: 4 × ~25 خط = **~100 خط تکراری**
- Formset handling: 2 × ~50 خط = **~100 خط تکراری**
- **مجموع UpdateView**: **~280 خط تکراری**

**DeleteView** (4+ view):
- `get_queryset()`: 4 × ~5 خط = **~20 خط تکراری**
- `delete()`: 4 × ~5 خط = **~20 خط تکراری**
- `get_context_data()`: 4 × ~20 خط = **~80 خط تکراری**
- **مجموع DeleteView**: **~120 خط تکراری**

**مجموع کل**: **~1,000 خط کد تکراری**

**با Base classes**: این مقدار به **~200 خط** کاهش می‌یابد (فقط override کردن متدها)

**صرفه‌جویی**: **~800 خط کد** (80% کاهش)

---

### ۱۴.۲ ماژول `qc` (کنترل کیفیت)

#### ۱۴.۲.۱ ساختار ماژول

**فایل‌های View** (3 فایل):
- `qc/views/base.py` - `QCBaseView`
- `qc/views/inspections.py` - 6 view (TemporaryReceiptQC List + Approval/Rejection workflow)
- `qc/views/__init__.py`

**کل**: **6+ view**

**نکته مهم**: ماژول `qc` **دارای base view class است**: `QCBaseView`

**ویژگی خاص**: این ماژول بیشتر **workflow views** دارد تا CRUD views

---

#### ۱۴.۲.۲ QCBaseView

**کلاس**: `QCBaseView(LoginRequiredMixin)`

**متدهای مشترک**:
1. `get_queryset()` - فیلتر بر اساس `active_company_id`
2. `get_context_data()` - اضافه کردن `active_module = 'qc'`

**مزیت**: این base view **قبلاً وجود دارد** و استفاده می‌شود.

---

#### ۱۴.۲.۳ الگوهای مشترک

**ListView** (1 view):
- `TemporaryReceiptQCListView` - List view با stats calculation

**Workflow Views** (5+ view):
- `TemporaryReceiptQCLineSelectionView` - TemplateView برای انتخاب خطوط
- `TemporaryReceiptQCApproveView` - View برای approve
- `TemporaryReceiptQCRejectView` - View برای reject
- `TemporaryReceiptQCRejectionManagementView` - TemplateView برای مدیریت rejection
- `TemporaryReceiptQCRejectionManagementSaveView` - View برای ذخیره rejection

**الگوی مشترک در Workflow Views**:
```python
class TemporaryReceiptQCApproveView(FeaturePermissionRequiredMixin, QCBaseView, View):
    feature_code = 'qc.inspections'
    required_action = 'approve'
    
    def post(self, request, *args, **kwargs):
        # Get object
        # Validation checks
        # Update status
        # Save
        messages.success(...)
        return HttpResponseRedirect(...)
```

**تخمین**: هر Workflow View ~40-60 خط کد (اما منطق business-specific است)

---

#### ۱۴.۲.۴ آمار تکرار کد در ماژول `qc`

**ListView** (1 view):
- `get_queryset()`: 1 × ~20 خط = **~20 خط تکراری**
- `get_context_data()`: 1 × ~30 خط = **~30 خط تکراری**
- Stats calculation: 1 × ~10 خط = **~10 خط تکراری**
- **مجموع ListView**: **~60 خط تکراری**

**Workflow Views** (5+ view):
- Validation checks: 5 × ~10 خط = **~50 خط تکراری**
- Messages: 5 × ~5 خط = **~25 خط تکراری**
- Redirect logic: 5 × ~5 خط = **~25 خط تکراری**
- **مجموع Workflow Views**: **~100 خط تکراری**

**مجموع کل**: **~160 خط کد تکراری**

**با Base classes**: این مقدار به **~50 خط** کاهش می‌یابد (فقط override کردن متدها)

**صرفه‌جویی**: **~110 خط کد** (69% کاهش)

**نکته**: ماژول `qc` کوچک است و بیشتر workflow logic دارد تا CRUD logic، بنابراین تکرار کمتری دارد.

---

### ۱۴.۳ نتیجه‌گیری برای ماژول‌های `ticketing` و `qc`

✅ **ماژول `ticketing`**:
- 19+ view
- 1,000+ خط کد تکراری
- Base view class وجود دارد (`TicketingBaseView`)
- برخی viewها از formset استفاده می‌کنند

✅ **ماژول `qc`**:
- 6+ view
- 160+ خط کد تکراری
- Base view class وجود دارد (`QCBaseView`)
- بیشتر workflow views دارد تا CRUD views

✅ **پس از بهبود Base classes**:
- `ticketing`: کد از ~1,000 خط به ~200 خط کاهش می‌یابد (80% کاهش)
- `qc`: کد از ~160 خط به ~50 خط کاهش می‌یابد (69% کاهش)

⚠️ **چالش‌ها**:
- نیاز به بهبود `TicketingBaseView` و `QCBaseView`
- نیاز به Base classes برای ListView, CreateView, UpdateView, DeleteView
- نیاز به پشتیبانی از Formset Views در `ticketing`

---

## ۱۵. نتیجه‌گیری

این معماری مشترک:
- ✅ تکرار کد را به شدت کاهش می‌دهد (**86% کاهش**)
- ✅ توسعه را سریع‌تر می‌کند (از 2 ساعت به 15 دقیقه برای view جدید)
- ✅ نگهداری را آسان‌تر می‌کند (تغییرات فقط در Base classes و JavaScript مشترک)
- ✅ یکپارچگی UI/UX را تضمین می‌کند (templates و JavaScript مشترک)
- ✅ امنیت را بهبود می‌بخشد (منطق permission در یک جا)
- ✅ JavaScript مشترک باعث یکپارچگی رفتار frontend می‌شود

**توصیه**: پیاده‌سازی به صورت **تدریجی** و **با دقت** انجام شود:
1. شروع با ماژول `shared` (pilot)
2. سپس `inventory`, `production`, `accounting`, `ticketing`, و `qc`
3. در نهایت سایر ماژول‌ها (در صورت توسعه در آینده)

**نکته**: ماژول‌های `sales`, `hr`, `transportation`, `office_automation`, `procurement` فعلاً در scope این پروژه نیستند و پس از توسعه، می‌توانند از Base classes مشترک استفاده کنند.

---

## ۱۶. مراجع و منابع

- Django Class-Based Views Documentation
- Django Filter Package (برای فیلترهای پیشرفته)
- Current Codebase: `shared/generic/generic_list.html` (template base موجود)
- Current Codebase: `shared/generic/generic_form.html` (template base موجود)
- Current Codebase: `shared/generic/generic_detail.html` (template base موجود)
- Current Codebase: `inventory/views/master_data.py` (مثال viewهای فعلی)
- Current Codebase: `shared/models.py` (Base model mixins موجود)
- Current Codebase: `shared/views/base.py` (Base view mixins موجود)

---

**تاریخ ایجاد**: 2024  
**آخرین به‌روزرسانی**: 2024-12-05  
**وضعیت**: در حال پیاده‌سازی - Pilot (companies) تکمیل شد ✅

---

## خلاصه نهایی

این سند شامل بررسی کامل **6 ماژول** (`shared`, `inventory`, `production`, `accounting`, `ticketing`, `qc`) و شناسایی **~18,055 خط کد تکراری** است که با پیاده‌سازی معماری مشترک به **~2,600 خط** کاهش می‌یابد (**86% کاهش**).

---

## پیشرفت پیاده‌سازی (Implementation Progress)

### ✅ فاز ۱: Infrastructure (تکمیل شده)
- ✅ تمام Base View Classes ساخته شد
- ✅ تمام Filter Functions ساخته شد
- ✅ تمام Mixins ساخته شد
- ✅ تمام JavaScript مشترک ساخته شد
- ✅ تمام Template Partials ساخته شد

### ✅ فاز ۲: Pilot Implementation - ماژول `shared` (در حال انجام)
- ✅ **`shared/views/companies.py`** - تمام 5 view به Base classes منتقل شد:
  - ✅ `CompanyListView` → `BaseListView` (استفاده از `generic_list.html`)
  - ✅ `CompanyCreateView` → `BaseCreateView` (استفاده از `generic_form.html`)
  - ✅ `CompanyUpdateView` → `BaseUpdateView` (استفاده از `generic_form.html`)
  - ✅ `CompanyDetailView` → `BaseDetailView` (استفاده از `generic_detail.html`)
  - ✅ `CompanyDeleteView` → `BaseDeleteView` (استفاده از `generic_confirm_delete.html`)
  - ✅ استفاده از partials مشترک: `row_actions.html`, `filter_panel.html`, `pagination.html`, `empty_state.html`
  - ✅ رفع مشکل RecursionError در `row_actions.html`
- ⏳ `shared/views/access_levels.py` - در انتظار
- ⏳ `shared/views/groups.py` - در انتظار
- ⏳ `shared/views/users.py` - در انتظار
- ⏳ `shared/views/company_units.py` - در انتظار

### ⏳ فاز ۳: Rollout به سایر ماژول‌ها (در انتظار)
- ⏳ ماژول `inventory`
- ⏳ ماژول `production`
- ⏳ ماژول `accounting`
- ⏳ ماژول `ticketing`
- ⏳ ماژول `qc`

**موارد پوشش داده شده**:
- ✅ View Layer (ListView, CreateView, UpdateView, DeleteView, DetailView)
- ✅ Form Layer (Form classes, Formset patterns)
- ✅ Template Layer (generic templates, breadcrumbs, messages, pagination)
- ✅ JavaScript Layer (formset management, cascading dropdowns, table export)
- ✅ API Layer (API endpoints patterns)
- ✅ Permission & Security (permission checking, validation logic)
- ✅ Common Utilities (success messages, company/user field setting, widget styling)

**نتیجه**: سند کامل و آماده برای استفاده تیم است.

