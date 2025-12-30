# 🔮 Future Checks - مواردی که باید اضافه شوند

این فایل شامل لیست چک‌هایی است که باید به Standards Checker اضافه شوند تا تمام استانداردهای `DEVELOPMENT_GUIDE.md` را پوشش دهد.

---

## 📊 وضعیت فعلی

### ✅ چک‌های موجود (30-40% پوشش)

1. **Base Classes** ✅
   - چک استفاده از BaseListView, BaseCreateView, etc.
   - چک عدم استفاده از Django generic views

2. **Templates** ✅
   - چک inline styles
   - چک inline JavaScript
   - چک استفاده از generic templates
   - چک template tags

3. **Documentation** ✅
   - چک وجود docstrings

4. **Security** ✅
   - چک SQL Injection
   - چک XSS
   - چک hardcoded secrets

5. **Naming Conventions** ✅
   - چک PascalCase برای classes
   - چک snake_case برای functions

---

## 🎯 چک‌های پیشنهادی (60-70% باقی‌مانده)

### 1. 🧪 Testing Standards (اولویت: بالا)

#### 1.1 Unit Tests
- [ ] چک وجود فایل `tests.py` یا `tests/` directory
- [ ] چک وجود test classes برای هر model/view
- [ ] چک استفاده از AAA pattern (Arrange, Act, Assert)
- [ ] چک وجود docstrings در test methods
- [ ] چک نام‌گذاری tests (باید با `test_` شروع بشه)

**مثال چک:**
```python
# ✅ درست
def test_item_type_creation_with_valid_data_should_succeed(self):
    # Arrange
    company = Company.objects.create(...)
    # Act
    item_type = ItemType.objects.create(...)
    # Assert
    self.assertEqual(item_type.name, 'Test')

# ❌ اشتباه
def test_item(self):  # نام مبهم
    pass
```

#### 1.2 Test Coverage
- [ ] چک coverage حداقل 80%
- [ ] چک coverage برای models
- [ ] چک coverage برای views
- [ ] چک coverage برای forms

**Implementation:**
- استفاده از `coverage.py` برای محاسبه coverage
- مقایسه با threshold (80%)

#### 1.3 Test Data Management
- [ ] چک استفاده از factories به جای fixtures
- [ ] چک وجود `setUp` و `tearDown` در test classes
- [ ] چک isolation tests (عدم وابستگی)

---

### 2. ⚡ Performance Checks (اولویت: بالا)

#### 2.1 Database Query Optimization
- [ ] چک استفاده از `select_related` برای ForeignKey
- [ ] چک استفاده از `prefetch_related` برای ManyToMany
- [ ] چک N+1 queries در loops
- [ ] چک استفاده از `only()` و `defer()` برای فیلدهای خاص

**مثال چک:**
```python
# ✅ درست
items = Item.objects.select_related('category', 'subcategory')

# ❌ اشتباه - N+1 query
items = Item.objects.all()
for item in items:
    print(item.category.name)  # Query برای هر item!
```

**Implementation:**
- Parse AST و پیدا کردن loops
- چک کردن queries داخل loops
- پیشنهاد استفاده از select_related/prefetch_related

#### 2.2 Indexes
- [ ] چک وجود indexes برای فیلدهای frequently queried
- [ ] چک وجود indexes برای ForeignKeys
- [ ] چک وجود indexes برای fields در filter_fields

**Implementation:**
- Parse model Meta class
- چک وجود `indexes` در Meta
- پیشنهاد indexes بر اساس usage

#### 2.3 Caching
- [ ] چک استفاده از cache برای queries تکراری
- [ ] چک cache invalidation
- [ ] چک cache key naming

---

### 3. 🌐 API Standards (اولویت: متوسط)

#### 3.1 Response Format
- [ ] چک فرمت response (status, data, message)
- [ ] چک استفاده از BaseAPIView
- [ ] چک HTTP status codes صحیح

**مثال چک:**
```python
# ✅ درست
{
    "status": "success",
    "data": {...},
    "message": "..."
}

# ❌ اشتباه
{
    "items": [...]
}
```

#### 3.2 API Versioning
- [ ] چک وجود version در URL (`/api/v1/`)
- [ ] چک consistency در versioning

#### 3.3 Error Handling
- [ ] چک فرمت error response
- [ ] چک error codes
- [ ] چک error messages

---

### 4. 💾 Database & Migration (اولویت: متوسط)

#### 4.1 Migration Best Practices
- [ ] چک وجود reverse migration
- [ ] چک migration naming convention
- [ ] چک data migrations (RunPython)
- [ ] چک migration dependencies

**مثال چک:**
```python
# ✅ درست
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(...),
        migrations.RunPython(populate_data, reverse_populate_data),
    ]

# ❌ اشتباه - بدون reverse
operations = [
    migrations.RunPython(populate_data),  # بدون reverse!
]
```

#### 4.2 Model Constraints
- [ ] چک وجود UniqueConstraint
- [ ] چک وجود CheckConstraint
- [ ] چک on_delete برای ForeignKeys

---

### 5. 📊 Error Handling & Logging (اولویت: متوسط)

#### 5.1 Logging Usage
- [ ] چک استفاده از logger به جای print
- [ ] چک logging levels مناسب
- [ ] چک عدم log کردن sensitive data

**مثال چک:**
```python
# ✅ درست
import logging
logger = logging.getLogger(__name__)
logger.info(f"User {user.username} created item")

# ❌ اشتباه
print(f"User {user.username} created item")
logger.info(f"Password: {password}")  # Sensitive data!
```

#### 5.2 Error Handling
- [ ] چک try-except blocks
- [ ] چک custom exceptions
- [ ] چک error messages مناسب

---

### 6. 🔄 Git Workflow (اولویت: پایین)

#### 6.1 Commit Messages
- [ ] چک فرمت commit message (conventional commits)
- [ ] چک وجود type (feat, fix, docs, etc.)
- [ ] چک وجود scope
- [ ] چک وجود subject

**مثال چک:**
```bash
# ✅ درست
feat(inventory): add barcode support
fix(production): resolve BOM calculation error

# ❌ اشتباه
added new feature
fixed bug
```

**Implementation:**
- استفاده از `git log` برای بررسی commits
- Parse commit messages
- چک فرمت

#### 6.2 Branch Naming
- [ ] چک فرمت branch name (feature/, bugfix/, hotfix/)
- [ ] چک consistency در naming

---

### 7. 🔧 Shared Components Usage (اولویت: بالا)

#### 7.1 Filter Functions
- [ ] چک استفاده از `apply_search` به جای manual search
- [ ] چک استفاده از `apply_status_filter`
- [ ] چک استفاده از `apply_company_filter`
- [ ] چک استفاده از `apply_date_range_filter`

**مثال چک:**
```python
# ✅ درست
from shared.filters import apply_search
queryset = apply_search(queryset, search_query, ['name'])

# ❌ اشتباه
search = request.GET.get('search')
if search:
    queryset = queryset.filter(Q(name__icontains=search))
```

#### 7.2 Mixins
- [ ] چک استفاده از `PermissionFilterMixin`
- [ ] چک استفاده از `CompanyScopedViewMixin`
- [ ] چک استفاده از `AutoSetFieldsMixin`
- [ ] چک استفاده از `SuccessMessageMixin`

**مثال چک:**
```python
# ✅ درست
class ItemListView(BaseListView, PermissionFilterMixin):
    pass

# ❌ اشتباه
class ItemListView(BaseListView):
    def get_queryset(self):
        # Manual permission filtering
        pass
```

#### 7.3 JavaScript Files
- [ ] چک استفاده از `formset.js` به جای inline JS
- [ ] چک استفاده از `cascading-dropdowns.js`
- [ ] چک استفاده از `table-export.js`
- [ ] چک عدم وجود duplicate JavaScript code

**مثال چک:**
```html
<!-- ✅ درست -->
<script src="{% static 'js/formset.js' %}"></script>

<!-- ❌ اشتباه -->
<script>
function addFormsetRow() {
    // 50+ خط کد تکراری
}
</script>
```

#### 7.4 Template Partials
- [ ] چک استفاده از `row_actions.html`
- [ ] چک استفاده از `pagination.html`
- [ ] چک استفاده از `filter_panel.html`
- [ ] چک عدم duplicate template code

**مثال چک:**
```django
{# ✅ درست #}
{% include 'shared/partials/row_actions.html' %}

{# ❌ اشتباه #}
<td>
    <a href="{% url 'edit' object.pk %}">Edit</a>
    <a href="{% url 'delete' object.pk %}">Delete</a>
</td>
```

---

### 8. 📝 Code Quality (اولویت: متوسط)

#### 8.1 Code Duplication
- [ ] چک duplicate code blocks
- [ ] چک duplicate functions
- [ ] پیشنهاد extract به shared functions

#### 8.2 Complexity
- [ ] چک cyclomatic complexity
- [ ] چک function length (بیشتر از 50 خط)
- [ ] چک class length (بیشتر از 500 خط)

#### 8.3 Imports
- [ ] چک unused imports
- [ ] چک import order
- [ ] چک absolute vs relative imports

---

### 9. 🔒 Security Enhancements (اولویت: بالا)

#### 9.1 CSRF Protection
- [ ] چک وجود `{% csrf_token %}` در forms
- [ ] چک CSRF token در AJAX requests

#### 9.2 Authentication & Authorization
- [ ] چک `@login_required` decorator
- [ ] چک `@feature_permission_required` decorator
- [ ] چک permission checking در views

#### 9.3 Input Validation
- [ ] چک form validation
- [ ] چک model validation
- [ ] چک sanitization

#### 9.4 File Upload Security
- [ ] چک file type validation
- [ ] چک file size limits
- [ ] چک secure file storage

---

### 10. 📖 Documentation (اولویت: پایین)

#### 10.1 Docstring Quality
- [ ] چک وجود Args در docstring
- [ ] چک وجود Returns در docstring
- [ ] چک وجود Raises در docstring
- [ ] چک وجود Examples در docstring

**مثال چک:**
```python
# ✅ درست
def calculate_total(item_id, quantity):
    """
    Calculate total cost for an item.
    
    Args:
        item_id (int): ID of the item
        quantity (Decimal): Quantity to calculate
    
    Returns:
        Decimal: Total cost
    
    Raises:
        ValueError: If item_id is invalid
    """
    pass

# ❌ اشتباه
def calculate_total(item_id, quantity):
    """Calculate total."""
    pass
```

#### 10.2 README Files
- [ ] چک وجود README.md در هر module
- [ ] چک وجود installation instructions
- [ ] چک وجود usage examples

---

## 🎯 اولویت‌بندی پیشنهادی

### Phase 1 (اولویت بالا - فوری)
1. ✅ Performance Checks (select_related, prefetch_related, N+1 queries)
2. ✅ Shared Components Usage (Filter Functions, Mixins, JS files)
3. ✅ Security Enhancements (CSRF, Authentication, Authorization)

### Phase 2 (اولویت متوسط - مهم)
4. ✅ Testing Standards (Unit Tests, Coverage)
5. ✅ Database & Migration (Indexes, Migration best practices)
6. ✅ Error Handling & Logging

### Phase 3 (اولویت پایین - خوب است)
7. ✅ API Standards
8. ✅ Code Quality (Duplication, Complexity)
9. ✅ Git Workflow
10. ✅ Documentation Quality

---

## 💡 پیشنهادات Implementation

### 1. استفاده از AST Parser
برای چک‌های پیچیده‌تر مثل:
- N+1 queries detection
- Code duplication
- Complexity analysis

### 2. استفاده از Coverage.py
برای:
- Test coverage calculation
- Coverage reporting

### 3. استفاده از Git Hooks
برای:
- Commit message validation
- Pre-commit checks

### 4. استفاده از Static Analysis Tools
- `pylint` برای code quality
- `mypy` برای type checking
- `bandit` برای security

---

## 📋 چک‌لیست Implementation

برای هر چک جدید:

- [ ] تعریف Issue class برای چک
- [ ] ایجاد Checker class
- [ ] نوشتن test cases
- [ ] اضافه کردن به StandardsChecker
- [ ] نوشتن documentation
- [ ] اضافه کردن به interactive_checker_v2.py

---

## 🔗 منابع

- [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) - استانداردهای کامل
- [check_standards.py](check_standards.py) - Implementation فعلی
- [AST Documentation](https://docs.python.org/3/library/ast.html) - برای parsing

---

**آخرین به‌روزرسانی**: 2024-12-23  
**نسخه**: 1.0

**نکته**: این فایل به صورت مداوم به‌روزرسانی می‌شود با اضافه شدن چک‌های جدید.

