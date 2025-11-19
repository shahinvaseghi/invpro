# Development Guide

Complete guide for developers working on the invproj platform.

---

## Table of Contents
1. [Development Environment Setup](#1-development-environment-setup)
2. [Project Structure](#2-project-structure)
3. [Coding Standards](#3-coding-standards)
4. [Database Workflow](#4-database-workflow)
5. [Creating New Features](#5-creating-new-features)
6. [Testing](#6-testing)
7. [Internationalization](#7-internationalization)
8. [Common Tasks](#8-common-tasks)
9. [Troubleshooting](#9-troubleshooting)
10. [Best Practices](#10-best-practices)

---

## 1. Development Environment Setup

### Initial Setup
```bash
# Clone repository
git clone <repo-url> invproj
cd invproj

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
cp env.sample .env

# Edit .env with your settings
nano .env

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Compile translations
python manage.py compilemessages

# Run development server
python manage.py runserver 0.0.0.0:8000
```

### Database Setup (PostgreSQL)
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
postgres=# CREATE DATABASE invproj_db;
postgres=# CREATE USER invproj_user WITH PASSWORD 'your_password';
postgres=# GRANT ALL PRIVILEGES ON DATABASE invproj_db TO invproj_user;
postgres=# \q

# Update .env
DATABASE_URL=postgres://invproj_user:your_password@localhost:5432/invproj_db
```

---

## 2. Project Structure

```
invproj/
├── config/              # Django settings and main URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shared/              # Shared entities (User, Company, Person)
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── context_processors.py
├── inventory/           # Inventory management
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   └── inventory_balance.py
├── production/          # Production management
│   ├── models.py
│   └── ...
├── qc/                  # Quality control
│   └── ...
├── ui/                  # UI templates and views
│   ├── views.py
│   └── urls.py
├── templates/           # Django templates
│   ├── base.html
│   ├── ui/
│   ├── inventory/
│   └── shared/
├── static/              # Static files (CSS, JS, images)
│   └── css/
│       └── base.css
├── locale/              # Translation files
│   └── fa/
│       └── LC_MESSAGES/
│           ├── django.po
│           └── django.mo
└── manage.py
```

---

## 3. Coding Standards

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use meaningful variable names

### Django Conventions
```python
# Model naming
class ItemType(models.Model):  # CamelCase, singular
    pass

# View naming
class ItemTypeListView(ListView):  # Descriptive + purpose
    pass

# URL naming
urlpatterns = [
    path('item-types/', ..., name='item_types'),  # kebab-case URL, snake_case name
]

# Template naming
templates/inventory/item_types.html  # snake_case
```

### Documentation
```python
def calculate_item_balance(company_id, warehouse_id, item_id, as_of_date=None):
    """
    Calculate current inventory balance for an item in a warehouse.
    
    Args:
        company_id (int): Company ID for scope
        warehouse_id (int): Warehouse ID
        item_id (int): Item ID
        as_of_date (date, optional): Calculate as of this date. Defaults to today.
    
    Returns:
        dict: Balance information with keys:
            - item_id
            - warehouse_id
            - quantity
            - unit
            - as_of_date
    """
    pass
```

---

## 4. Database Workflow

### Creating Models
```python
# 1. Define model in models.py
class MyModel(InventorySortableModel):
    """Brief description."""
    name = models.CharField(max_length=120)
    # ... fields ...
    
    class Meta:
        verbose_name = _("My Model")
        constraints = [...]
```

### Migrations
```bash
# Create migration
python manage.py makemigrations inventory

# Review migration file
cat inventory/migrations/0XXX_auto_YYYYMMDD_HHMM.py

# Apply migration
python manage.py migrate

# Check migration status
python manage.py showmigrations inventory
```

### Reverting Migrations
```bash
# Revert to specific migration
python manage.py migrate inventory 0005

# Revert all
python manage.py migrate inventory zero
```

---

## 5. Creating New Features

### Adding a New CRUD Entity

#### Step 1: Create Model
```python
# inventory/models.py
class NewEntity(InventorySortableModel):
    public_code = models.CharField(max_length=5)
    name = models.CharField(max_length=120)
    # ... other fields
```

#### Step 2: Create Form
```python
# inventory/forms.py
class NewEntityForm(forms.ModelForm):
    class Meta:
        model = NewEntity
        fields = ['public_code', 'name', ...]
        widgets = {
            'public_code': forms.TextInput(attrs={'class': 'form-control'}),
            # ...
        }
        labels = {
            'public_code': _('Code'),
            # ...
        }
```

#### Step 3: Create Views
```python
# inventory/views.py
class NewEntityListView(InventoryBaseView, ListView):
    model = models.NewEntity
    template_name = 'inventory/new_entities.html'
    context_object_name = 'new_entities'
    paginate_by = 50

class NewEntityCreateView(InventoryBaseView, CreateView):
    model = models.NewEntity
    form_class = forms.NewEntityForm
    template_name = 'inventory/newentity_form.html'
    success_url = reverse_lazy('inventory:new_entities')
    
    def form_valid(self, form):
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Entity created successfully.'))
        return super().form_valid(form)

# Add UpdateView and DeleteView similarly
```

#### Step 4: Add URLs
```python
# inventory/urls.py
urlpatterns = [
    path('new-entities/', views.NewEntityListView.as_view(), name='new_entities'),
    path('new-entities/create/', views.NewEntityCreateView.as_view(), name='newentity_create'),
    path('new-entities/<int:pk>/edit/', views.NewEntityUpdateView.as_view(), name='newentity_edit'),
    path('new-entities/<int:pk>/delete/', views.NewEntityDeleteView.as_view(), name='newentity_delete'),
]
```

#### Step 5: Create Templates
```bash
# Create symlinks to generic templates
cd templates/inventory
ln -s generic_form.html newentity_form.html
ln -s generic_confirm_delete.html newentity_confirm_delete.html

# Create list template
cp item_types.html new_entities.html
# Edit new_entities.html to match your fields
```

#### Step 6: Register Admin
```python
# inventory/admin.py
@admin.register(models.NewEntity)
class NewEntityAdmin(admin.ModelAdmin):
    list_display = ['public_code', 'name', 'company', 'is_enabled']
    list_filter = ['company', 'is_enabled']
    search_fields = ['public_code', 'name']
```

#### Step 7: Add to Sidebar
```html
<!-- templates/ui/components/sidebar.html -->
<li><a href="{% url 'inventory:new_entities' %}" class="nav-link-sub">{% trans "New Entities" %}</a></li>
```

#### Step 8: Add Translations
```bash
# Extract new strings
python manage.py makemessages -l fa

# Edit locale/fa/LC_MESSAGES/django.po
# Add translations

# Compile
python manage.py compilemessages -l fa
```

### Purchase & Warehouse Request Notes
- `forms.PurchaseRequestForm` و `forms.WarehouseRequestForm` هر دو `company_id` را از ویو دریافت می‌کنند و بر اساس کالا، واحد و (برای حواله داخلی) انبارهای مجاز را پویا فیلتر می‌کنند.
- فیلد «approver» تنها کاربرانی را نمایش می‌دهد که در `FEATURE_PERMISSION_MAP` برای اکشن `approve` همان منو سطح دسترسی دارند؛ قبل از استفاده در UI، سطح دسترسی مناسب را در نقش‌ها تعریف کنید.
- پس از تایید، `is_locked=1` روی درخواست‌ها تنظیم می‌شود و تنها همین درخواست‌های تاییدشده/قفل‌شده در فرم‌های رسید دائم و امانی قابل انتخاب هستند؛ منطق فرم‌ها تطابق کالا و انبار را پیش از ذخیره بررسی می‌کند.
- ارتباطات «درخواست‌کننده» همچنان به `production.Person` متصل می‌مانند تا گزارش‌گیری نفر-ساعت حفظ شود، اما همه‌ی فیلدهای «approver» باید به Django `User` اشاره کنند. برای جزئیات کامل جریان تأیید، به `docs/approval_workflow.md` مراجعه کنید.

### User Management Forms Notes
- `UserCreateForm` و `UserUpdateForm` از `UserBaseForm` ارث‌بری می‌کنند و مدیریت کامل کاربران را فراهم می‌کنند.
- **Group Assignments**: گروه‌ها به‌صورت ManyToMany ذخیره می‌شوند. در `UserUpdateForm.save()`، گروه‌ها مستقیماً بعد از `user.save()` ذخیره می‌شوند تا از پایداری اطمینان حاصل شود.
- **Superuser Status**: وضعیت superuser به‌درستی ذخیره می‌شود.
- **Password Management**: 
  - در `UserCreateForm`: رمز عبور با `set_password()` تنظیم می‌شود
  - در `UserUpdateForm`: رمز عبور فقط در صورت ارائه `new_password1` تغییر می‌کند
- **Company Access**: دسترسی شرکت‌ها از طریق `UserCompanyAccessFormSet` در view مدیریت می‌شود (نه در خود فرم).

#### Step 9: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Step 10: Test
```bash
# Create test data
python manage.py shell
>>> from inventory.models import NewEntity
>>> from shared.models import Company
>>> company = Company.objects.first()
>>> NewEntity.objects.create(company=company, public_code='00001', name='Test')
>>> exit()

# Test in browser
# Navigate to /fa/inventory/new-entities/
```

---

## 6. Testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test inventory

# Run specific test class
python manage.py test inventory.tests.TestItemType

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Writing Tests
```python
# inventory/tests.py
from django.test import TestCase
from .models import ItemType
from shared.models import Company, User

class ItemTypeTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            public_code='001',
            legal_name='Test Company'
        )
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
    
    def test_create_item_type(self):
        item_type = ItemType.objects.create(
            company=self.company,
            public_code='001',
            name='Test Type',
            name_en='Test Type EN'
        )
        self.assertEqual(item_type.name, 'Test Type')
        self.assertEqual(str(item_type), 'Test Company · Test Type')
```

---

## 7. Internationalization

### Default Language
- **Persian (Farsi)** is the default language (`LANGUAGE_CODE = 'fa'`)
- Application opens in Persian by default for all new users
- Users can switch to English using the language switcher in the header

### Adding Translatable Strings
```python
# In Python code
from django.utils.translation import gettext_lazy as _

name = _('Item Type')  # Will be translated

# In templates
{% load i18n %}
<h1>{% trans "Item Types" %}</h1>
```

### Translation Workflow
```bash
# 1. Mark strings with _() or {% trans %}
# 2. Extract strings
python manage.py makemessages -l fa

# 3. Edit locale/fa/LC_MESSAGES/django.po
msgid "Item Type"
msgstr "نوع کالا"

# 4. Compile
python manage.py compilemessages -l fa

# 5. Restart server
pkill -f runserver
python manage.py runserver
```

---

## 8. Common Tasks

### Adding a New Field to Model
```python
# 1. Add field to model
class ItemType(models.Model):
    # ... existing fields
    new_field = models.CharField(max_length=50, blank=True)

# 2. Create migration
python manage.py makemigrations inventory

# 3. Apply migration
python manage.py migrate

# 4. Add to form
class ItemTypeForm(forms.ModelForm):
    class Meta:
        fields = [..., 'new_field']

# 5. Add to template
# 6. Add translation
```

### Changing Field Length
```python
# 1. Change in model
public_code = models.CharField(max_length=5)  # was 3

# 2. Create migration
python manage.py makemigrations

# 3. If data exists, may need to update:
python manage.py shell
>>> from inventory.models import ItemType
>>> ItemType.objects.filter(public_code__length=3).update(public_code=F('public_code').zfill(5))

# 4. Apply migration
python manage.py migrate
```

### Adding Company Filtering
```python
# For any view that needs company filtering:
class MyView(InventoryBaseView, ListView):
    # InventoryBaseView automatically filters by company
    pass

# For custom querysets:
def get_queryset(self):
    qs = super().get_queryset()
    company_id = self.request.session.get('active_company_id')
    return qs.filter(company_id=company_id)
```

---

## 9. Troubleshooting

### Server Won't Start
```bash
# Check for errors
python manage.py check

# Check migrations
python manage.py showmigrations

# Check imports
python manage.py shell
>>> from inventory import models
>>> from inventory import views
```

### Translation Not Showing
```bash
# Recompile translations
python manage.py compilemessages -l fa

# Check .mo file exists
ls -la locale/fa/LC_MESSAGES/django.mo

# Restart server
pkill -f runserver
python manage.py runserver
```

### Company Filtering Not Working
```python
# Check session
python manage.py shell
>>> from django.contrib.sessions.models import Session
>>> s = Session.objects.first()
>>> s.get_decoded()
# Should show active_company_id

# Check context processor in settings.py
TEMPLATES[0]['OPTIONS']['context_processors']
# Should include 'shared.context_processors.active_company'
```

### Migration Conflicts
```bash
# If migrations conflict:
python manage.py migrate inventory --fake 0XXX
python manage.py makemigrations --merge
python manage.py migrate
```

---

## 10. Best Practices

### Model Design
- Always extend base mixins (TimeStampedModel, etc.)
- Use meaningful field names
- Add `__str__` method
- Add `class Meta` with verbose_name
- Add database constraints for uniqueness
- Use `blank=True` for optional fields
- Use `null=True` sparingly (only for database NULL)

### View Design
- Extend InventoryBaseView for company filtering
- Always set `company_id` from session
- Always set `created_by` / `edited_by`
- Add success messages
- Handle errors gracefully
- Validate permissions

### Form Design
- Use ModelForm when possible
- Add CSS classes to widgets
- Translate all labels
- Add help_text where needed
- Validate business logic in clean()
- Filter foreign key choices by company

### Template Design
- Extend base templates
- Use blocks for customization
- Use template inheritance
- Add breadcrumbs
- Include empty states
- Make responsive

### Security
- Never trust user input
- Always filter by company
- Use CSRF tokens
- Validate permissions
- Sanitize HTML output
- Use parameterized queries (ORM)

### Access Control
- Centralise feature/action definitions inside `shared/permissions.py` (`FEATURE_PERMISSION_MAP` + `PermissionAction`).
- هنگام پیاده‌سازی ویوها یا فرم‌ها، ابتدا تعیین کنید آیا کاربر نیاز به `view_own` یا `view_all` دارد؛ سپس سایر اکشن‌ها (`create`, `edit_own`, `lock_own`, `lock_other`, `unlock_*`, `approve`, `reject`, `cancel`) را از همان کاتالوگ بخوانید.
- تا تکمیل CRUD سطوح دسترسی، صفحات `/shared/users/`, `/shared/groups/`, `/shared/access-levels/` به‌عنوان Placeholder باقی می‌مانند؛ بعد از پیاده‌سازی حتماً این مستند را با جریان کامل بروزرسانی کنید.

### Performance
- Use select_related for ForeignKeys
- Use prefetch_related for Many-to-Many
- Add database indexes
- Paginate large lists
- Cache expensive queries
- Optimize N+1 queries

---

## Quick Reference

### Useful Commands
```bash
# Development
python manage.py runserver 0.0.0.0:8000
python manage.py shell
python manage.py dbshell

# Migrations
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations

# Translation
python manage.py makemessages -l fa
python manage.py compilemessages -l fa

# Admin
python manage.py createsuperuser
python manage.py changepassword username

# Testing
python manage.py test
python manage.py test --keepdb  # faster

# Database
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json
```

### Project Contacts
- Architecture questions: See README.md
- Database design: See inventory_module_db_design_plan.md
- UI guidelines: See ui_guidelines.md
- Forms: See README_FORMS.md (per module)

---

Happy coding! 🚀

