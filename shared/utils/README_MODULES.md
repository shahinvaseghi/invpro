# shared/utils/modules.py - Module Availability Utilities

**هدف**: توابع کمکی برای بررسی نصب بودن ماژول‌های اختیاری و دریافت مدل‌های آن‌ها

این فایل برای مدیریت وابستگی‌های اختیاری بین ماژول‌ها استفاده می‌شود. برخی ماژول‌ها (مثل Production و QC) ممکن است نصب نباشند، و این توابع به ما کمک می‌کنند که قبل از استفاده از آن‌ها، بررسی کنیم که آیا نصب هستند یا نه.

---

## توابع

### `is_production_installed() -> bool`

**هدف**: بررسی اینکه آیا ماژول Production نصب است یا نه

**مقدار بازگشتی**:
- `bool`: `True` اگر ماژول Production نصب باشد، `False` در غیر این صورت

**منطق کار**:
- از `django.apps.apps.is_installed('production')` استفاده می‌کند
- این تابع بررسی می‌کند که آیا `production` در `INSTALLED_APPS` در `settings.py` وجود دارد یا نه

**مثال استفاده**:
```python
from shared.utils.modules import is_production_installed

if is_production_installed():
    # استفاده از ماژول Production
    from production.models import WorkLine
else:
    # ماژول Production نصب نیست
    pass
```

---

### `is_qc_installed() -> bool`

**هدف**: بررسی اینکه آیا ماژول QC (Quality Control) نصب است یا نه

**مقدار بازگشتی**:
- `bool`: `True` اگر ماژول QC نصب باشد، `False` در غیر این صورت

**منطق کار**:
- از `django.apps.apps.is_installed('qc')` استفاده می‌کند
- این تابع بررسی می‌کند که آیا `qc` در `INSTALLED_APPS` در `settings.py` وجود دارد یا نه

**مثال استفاده**:
```python
from shared.utils.modules import is_qc_installed

if is_qc_installed():
    # استفاده از ماژول QC
    from qc.models import QCInspection
else:
    # ماژول QC نصب نیست
    pass
```

---

### `get_work_line_model()`

**هدف**: دریافت مدل `WorkLine` از ماژول Production (اگر نصب باشد)

**مقدار بازگشتی**:
- `WorkLine` model class: اگر ماژول Production نصب باشد
- `None`: اگر ماژول Production نصب نباشد یا import خطا بدهد

**منطق کار**:
1. ابتدا بررسی می‌کند که آیا ماژول Production نصب است (`is_production_installed()`)
2. اگر نصب نباشد، `None` برمی‌گرداند
3. اگر نصب باشد، سعی می‌کند `WorkLine` را از `production.models` import کند
4. اگر import موفق باشد، مدل را برمی‌گرداند
5. اگر import خطا بدهد (مثلاً مدل وجود نداشته باشد)، `None` برمی‌گرداند

**مثال استفاده**:
```python
from shared.utils.modules import get_work_line_model

WorkLine = get_work_line_model()
if WorkLine:
    # استفاده از WorkLine
    work_lines = WorkLine.objects.filter(company_id=1)
else:
    # ماژول Production نصب نیست
    pass
```

---

### `get_person_model()`

**هدف**: دریافت مدل `Person` از ماژول Production (اگر نصب باشد)

**مقدار بازگشتی**:
- `Person` model class: اگر ماژول Production نصب باشد
- `None`: اگر ماژول Production نصب نباشد یا import خطا بدهد

**منطق کار**:
1. ابتدا بررسی می‌کند که آیا ماژول Production نصب است (`is_production_installed()`)
2. اگر نصب نباشد، `None` برمی‌گرداند
3. اگر نصب باشد، سعی می‌کند `Person` را از `production.models` import کند
4. اگر import موفق باشد، مدل را برمی‌گرداند
5. اگر import خطا بدهد (مثلاً مدل وجود نداشته باشد)، `None` برمی‌گرداند

**مثال استفاده**:
```python
from shared.utils.modules import get_person_model

Person = get_person_model()
if Person:
    # استفاده از Person
    persons = Person.objects.filter(company_id=1)
else:
    # ماژول Production نصب نیست
    pass
```

---

## وابستگی‌ها

- `django.apps.apps`: برای بررسی نصب بودن ماژول‌ها
- `production.models`: برای import مدل‌های Production (اختیاری)

---

## استفاده در پروژه

### در Models

```python
from shared.utils.modules import get_work_line_model

class Item(InventoryBaseModel):
    work_line = models.ForeignKey(
        'production.WorkLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    
    def clean(self):
        WorkLine = get_work_line_model()
        if self.work_line and not WorkLine:
            raise ValidationError('ماژول Production نصب نیست')
```

### در Views

```python
from shared.utils.modules import is_production_installed

class ItemListView(ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['production_installed'] = is_production_installed()
        return context
```

### در Forms

```python
from shared.utils.modules import get_person_model

class ReceiptForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        Person = get_person_model()
        if Person:
            self.fields['person'].queryset = Person.objects.filter(
                company_id=self.company_id
            )
        else:
            self.fields['person'].widget = forms.HiddenInput()
```

---

## نکات مهم

1. **Optional Dependencies**: این توابع برای مدیریت وابستگی‌های اختیاری طراحی شده‌اند
2. **Error Handling**: تمام توابع در صورت خطا `None` یا `False` برمی‌گردانند (fail-safe)
3. **Lazy Import**: مدل‌ها فقط زمانی import می‌شوند که ماژول نصب باشد
4. **Performance**: بررسی نصب بودن ماژول با `apps.is_installed()` بسیار سریع است
5. **Extensibility**: می‌توان توابع مشابه برای ماژول‌های دیگر (مثل Ticketing) اضافه کرد

---

## الگوی استفاده

**الگوی پیشنهادی**:
```python
from shared.utils.modules import is_production_installed, get_work_line_model

# بررسی نصب بودن
if is_production_installed():
    # دریافت مدل
    WorkLine = get_work_line_model()
    if WorkLine:
        # استفاده از مدل
        work_lines = WorkLine.objects.all()
```

**الگوی جایگزین (کوتاه‌تر)**:
```python
from shared.utils.modules import get_work_line_model

WorkLine = get_work_line_model()
if WorkLine:
    # استفاده از مدل
    work_lines = WorkLine.objects.all()
```

---

## ماژول‌های پشتیبانی شده

در حال حاضر این فایل فقط برای ماژول‌های زیر توابع دارد:

1. **Production**: `is_production_installed()`, `get_work_line_model()`, `get_person_model()`
2. **QC**: `is_qc_installed()`

برای ماژول‌های دیگر (مثل Ticketing) می‌توان توابع مشابه اضافه کرد.

