# ui/context_processors.py - Context Processors

**هدف**: فراهم کردن متغیرهای context برای ماژول UI

---

## تابع `active_module(request)`

**توضیح**: ماژول فعال را به context اضافه می‌کند.

**پارامترهای ورودی**:
- `request` (HttpRequest): درخواست HTTP Django

**مقدار بازگشتی**:
```python
{
    "active_module": str  # نام ماژول فعال (از query string یا "dashboard")
}
```

**منطق**:
- از `request.GET.get("module", "dashboard")` خوانده می‌شود
- اگر پارامتر `module` در query string نباشد، `"dashboard"` برمی‌گرداند

**مثال استفاده در template**:
```django
{% if active_module == "inventory" %}
  <div class="inventory-module">...</div>
{% endif %}
```

---

## استفاده در پروژه

این context processor در `config/settings.py` ثبت شده است:

```python
TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                # ...
                'ui.context_processors.active_module',
            ],
        },
    },
]
```

---

## نکات مهم

1. **Static Implementation**: در حال حاضر static است و از query string می‌خواند
2. **Future Enhancement**: در آینده می‌تواند به صورت خودکار از URL path استخراج شود
3. **Navigation Highlighting**: برای highlight کردن ماژول فعال در navigation استفاده می‌شود

