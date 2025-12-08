# shared/views/api.py - Base API View Classes

**هدف**: کلاس‌های پایه برای API endpoints با JSON responses در تمام ماژول‌ها

این فایل شامل کلاس‌های پایه زیر است:
- `BaseAPIView` - کلاس پایه برای API endpoints با JSON responses
- `BaseListAPIView` - کلاس پایه برای لیست کردن objects به صورت JSON
- `BaseDetailAPIView` - کلاس پایه برای دریافت یک object به صورت JSON

---

## کلاس‌ها

### `BaseAPIView`

**توضیح**: کلاس پایه API view با قابلیت‌های مشترک برای JSON endpoints

این کلاس قابلیت‌های زیر را ارائه می‌دهد:
- Company validation
- JSON response formatting
- Error handling
- User authentication

**Type**: `LoginRequiredMixin, View`

**متدها**:

#### `get_company_id(self) -> Optional[int]`

**توضیح**: دریافت ID شرکت فعال از session

**مقدار بازگشتی**:
- `Optional[int]`: Company ID یا `None` اگر شرکتی فعال نباشد

**منطق**:
1. `active_company_id` را از `self.request.session` دریافت می‌کند
2. آن را برمی‌گرداند

#### `validate_company(self) -> tuple[bool, Optional[str]]`

**توضیح**: اعتبارسنجی اینکه شرکت فعال وجود دارد

**مقدار بازگشتی**:
- `tuple[bool, Optional[str]]`: Tuple شامل (is_valid, error_message)

**منطق**:
1. `company_id` را با `get_company_id()` دریافت می‌کند
2. اگر `company_id` وجود نداشته باشد، `(False, _('No active company selected.'))` برمی‌گرداند
3. در غیر این صورت، `(True, None)` برمی‌گرداند

#### `get_user(self) -> User`

**توضیح**: دریافت کاربر احراز هویت شده فعلی

**مقدار بازگشتی**:
- `User`: کاربر فعلی

#### `json_response(self, data: Dict[str, Any], status: int = 200) -> JsonResponse`

**توضیح**: برگرداندن پاسخ JSON با data

**پارامترهای ورودی**:
- `data`: Dictionary برای serialize کردن به JSON
- `status`: HTTP status code (پیش‌فرض: 200)

**مقدار بازگشتی**:
- `JsonResponse`: Object JsonResponse

#### `error_response(self, message: str, status: int = 400, **kwargs) -> JsonResponse`

**توضیح**: برگرداندن پاسخ خطای JSON

**پارامترهای ورودی**:
- `message`: پیام خطا
- `status`: HTTP status code (پیش‌فرض: 400)
- `**kwargs`: داده‌های خطای اضافی

**مقدار بازگشتی**:
- `JsonResponse`: JsonResponse با فرمت خطا

**منطق**:
1. `response_data` را با `{'error': message}` و `**kwargs` ایجاد می‌کند
2. `JsonResponse` را با status code برمی‌گرداند

#### `success_response(self, message: Optional[str] = None, data: Optional[Dict[str, Any]] = None, **kwargs) -> JsonResponse`

**توضیح**: برگرداندن پاسخ موفقیت JSON

**پارامترهای ورودی**:
- `message`: پیام موفقیت (اختیاری)
- `data`: داده‌های اضافی (اختیاری)
- `**kwargs`: داده‌های پاسخ اضافی

**مقدار بازگشتی**:
- `JsonResponse`: JsonResponse با فرمت موفقیت

**منطق**:
1. `response_data` را با `{'success': True}` و `**kwargs` ایجاد می‌کند
2. اگر `message` وجود داشته باشد، آن را اضافه می‌کند
3. اگر `data` وجود داشته باشد، آن را به response_data اضافه می‌کند
4. `JsonResponse` را با status 200 برمی‌گرداند

---

### `BaseListAPIView`

**توضیح**: کلاس پایه API view برای لیست کردن objects به صورت JSON

این کلاس قابلیت‌های زیر را ارائه می‌دهد:
- List serialization
- Filtering
- Pagination support

**Type**: `BaseAPIView`

**Attributes**:
- `model`: `Optional[Model]` - Model class (باید در subclass تنظیم شود)
- `paginate_by`: `Optional[int]` - تعداد items در هر صفحه (اختیاری)

**متدها**:

#### `get(self, request: HttpRequest) -> JsonResponse`

**توضیح**: برگرداندن لیست objects به صورت JSON

**پارامترهای ورودی**:
- `request`: HTTP request

**مقدار بازگشتی**:
- `JsonResponse`: پاسخ JSON با لیست objects

**منطق**:
1. Company را با `validate_company()` اعتبارسنجی می‌کند
2. اگر معتبر نباشد، خطا برمی‌گرداند (`status=400`)
3. queryset را با `get_queryset()` دریافت می‌کند
4. queryset را با `filter_queryset()` فیلتر می‌کند
5. objects را با `serialize_object()` serialize می‌کند
6. اگر `paginate_by` تنظیم شده باشد:
   - Paginator ایجاد می‌کند
   - صفحه را از GET parameter دریافت می‌کند
   - پاسخ paginated را برمی‌گرداند: `{'results': [...], 'count': ..., 'page': ..., 'num_pages': ..., 'has_next': ..., 'has_previous': ...}`
7. در غیر این صورت، پاسخ ساده را برمی‌گرداند: `{'results': [...], 'count': ...}`

#### `get_queryset(self) -> QuerySet`

**توضیح**: دریافت queryset برای لیست کردن

**مقدار بازگشتی**:
- `QuerySet`: queryset برای listing

**منطق**:
1. اگر `self.model` تنظیم نشده باشد، `ValueError` می‌اندازد
2. `self.model.objects.all()` را برمی‌گرداند

**نکته**: این متد باید در subclass override شود برای custom queryset

#### `filter_queryset(self, queryset: QuerySet) -> QuerySet`

**توضیح**: فیلتر کردن queryset بر اساس پارامترهای request

**پارامترهای ورودی**:
- `queryset`: queryset برای فیلتر کردن

**مقدار بازگشتی**:
- `QuerySet`: queryset فیلتر شده

**نکته**: این متد باید در subclass override شود برای custom filtering

#### `serialize_object(self, obj: Model) -> Dict[str, Any]`

**توضیح**: serialize کردن یک object به dictionary

**پارامترهای ورودی**:
- `obj`: Model instance برای serialize کردن

**مقدار بازگشتی**:
- `Dict[str, Any]`: نمایش dictionary از object

**منطق پیش‌فرض**:
1. `{'id': obj.pk, 'str': str(obj)}` را برمی‌گرداند

**نکته**: این متد باید در subclass override شود برای custom serialization

---

### `BaseDetailAPIView`

**توضیح**: کلاس پایه API view برای دریافت یک object به صورت JSON

این کلاس قابلیت‌های زیر را ارائه می‌دهد:
- Object retrieval
- Serialization
- Error handling

**Type**: `BaseAPIView`

**Attributes**:
- `model`: `Optional[Model]` - Model class (باید در subclass تنظیم شود)
- `lookup_field`: `str` - فیلد برای lookup (پیش‌فرض: `'pk'`)
- `lookup_url_kwarg`: `str` - URL kwarg برای lookup (پیش‌فرض: `'pk'`)

**متدها**:

#### `get(self, request: HttpRequest, **kwargs) -> JsonResponse`

**توضیح**: برگرداندن یک object به صورت JSON

**پارامترهای ورودی**:
- `request`: HTTP request
- `**kwargs`: URL kwargs

**مقدار بازگشتی**:
- `JsonResponse`: پاسخ JSON با object

**منطق**:
1. Company را با `validate_company()` اعتبارسنجی می‌کند
2. اگر معتبر نباشد، خطا برمی‌گرداند (`status=400`)
3. object را با `get_object()` دریافت می‌کند
4. اگر `ObjectDoesNotExist` رخ دهد، خطا برمی‌گرداند (`status=404`)
5. اگر exception دیگری رخ دهد، خطا را log می‌کند و خطا برمی‌گرداند (`status=500`)
6. object را با `serialize_object()` serialize می‌کند
7. پاسخ JSON را برمی‌گرداند

#### `get_object(self, **kwargs) -> Model`

**توضیح**: دریافت object instance

**پارامترهای ورودی**:
- `**kwargs`: URL kwargs

**مقدار بازگشتی**:
- `Model`: Model instance

**منطق**:
1. اگر `self.model` تنظیم نشده باشد، `ValueError` می‌اندازد
2. `lookup_value` را از kwargs دریافت می‌کند
3. اگر `lookup_value` وجود نداشته باشد، `ValueError` می‌اندازد
4. lookup را با `{self.lookup_field: lookup_value}` ایجاد می‌کند
5. اگر model دارای `company_id` باشد و `company_id` از session وجود داشته باشد، آن را به lookup اضافه می‌کند
6. object را با `self.model.objects.get(**lookup)` پیدا می‌کند و برمی‌گرداند

**نکته**: این متد می‌تواند در subclass override شود برای custom object retrieval

#### `serialize_object(self, obj: Model) -> Dict[str, Any]`

**توضیح**: serialize کردن یک object به dictionary

**پارامترهای ورودی**:
- `obj`: Model instance برای serialize کردن

**مقدار بازگشتی**:
- `Dict[str, Any]`: نمایش dictionary از object

**منطق پیش‌فرض**:
1. `{'id': obj.pk, 'str': str(obj)}` را برمی‌گرداند

**نکته**: این متد باید در subclass override شود برای custom serialization

---

## وابستگی‌ها

- `django.http`: `JsonResponse`, `HttpRequest`
- `django.views`: `View`
- `django.contrib.auth.mixins`: `LoginRequiredMixin`
- `django.db.models`: `QuerySet`, `Model`
- `django.core.exceptions`: `ValidationError`, `ObjectDoesNotExist`
- `django.utils.translation`: `gettext_lazy as _`
- `logging`: برای error logging

---

## استفاده در پروژه

### مثال استفاده از BaseListAPIView

```python
from shared.views.api import BaseListAPIView
from inventory.models import Item

class ItemListAPIView(BaseListAPIView):
    model = Item
    
    def get_queryset(self):
        company_id = self.get_company_id()
        return self.model.objects.filter(company_id=company_id)
    
    def serialize_object(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'code': obj.public_code,
            'category': obj.category.name if obj.category else None,
        }
```

### مثال استفاده از BaseDetailAPIView

```python
from shared.views.api import BaseDetailAPIView
from inventory.models import Item

class ItemDetailAPIView(BaseDetailAPIView):
    model = Item
    
    def serialize_object(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'code': obj.public_code,
            'description': obj.description,
            'category': {
                'id': obj.category.id,
                'name': obj.category.name,
            } if obj.category else None,
        }
```

### مثال استفاده از BaseAPIView

```python
from shared.views.api import BaseAPIView

class CustomAPIView(BaseAPIView):
    def get(self, request):
        company_id = self.get_company_id()
        if not company_id:
            return self.error_response('No active company', status=400)
        
        data = {'result': 'success', 'company_id': company_id}
        return self.json_response(data)
```

---

## نکات مهم

1. **Authentication**: تمام API views از `LoginRequiredMixin` استفاده می‌کنند و نیاز به authentication دارند

2. **Company Validation**: تمام API views باید company را validate کنند قبل از پردازش request

3. **Error Handling**: تمام خطاها به صورت JSON با status code مناسب برمی‌گردانند

4. **Serialization**: متد `serialize_object()` باید در subclass override شود برای custom serialization

5. **Pagination**: `BaseListAPIView` از pagination پشتیبانی می‌کند اگر `paginate_by` تنظیم شود

6. **Company Scoping**: `BaseDetailAPIView.get_object()` به صورت خودکار company filter را اضافه می‌کند اگر model دارای `company_id` باشد

7. **Logging**: خطاها در `BaseDetailAPIView.get()` log می‌شوند

8. **Response Format**: 
   - Success: `{'success': True, 'message': ..., 'data': ...}`
   - Error: `{'error': '...', ...}`
   - List: `{'results': [...], 'count': ..., ...}`
