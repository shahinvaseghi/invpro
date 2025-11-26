# qc/views/base.py - Base Views

**هدف**: کلاس‌های پایه برای views ماژول QC

---

## Base Classes

### `QCBaseView(LoginRequiredMixin)`

**توضیح**: کلاس پایه با context و فیلتر شرکت مشترک برای تمام views ماژول QC.

**متدها**:

#### `get_queryset()`

**توضیح**: queryset را بر اساس شرکت فعال فیلتر می‌کند.

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده بر اساس `active_company_id`

---

#### `get_context_data(**kwargs) -> Dict[str, Any]`

**توضیح**: context مشترک را اضافه می‌کند.

**مقدار بازگشتی**:
- Context با `active_module = 'qc'` اضافه شده

---

## وابستگی‌ها

- `django.contrib.auth.mixins`: `LoginRequiredMixin`
- `qc.models`: تمام مدل‌های QC

---

## استفاده در پروژه

```python
from qc.views.base import QCBaseView

class InspectionListView(QCBaseView, ListView):
    model = ReceiptInspection
```

---

## نکات مهم

1. **Company Filtering**: تمام views به صورت خودکار بر اساس شرکت فعال فیلتر می‌شوند
2. **Simple Structure**: این ماژول ساختار ساده‌ای دارد و فقط یک base view دارد

