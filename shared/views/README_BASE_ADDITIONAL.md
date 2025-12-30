# shared/views/base_additional.py - Additional Base Classes

**هدف**: کلاس‌های پایه اضافی برای الگوهای پیچیده view

این فایل شامل کلاس‌های پایه زیر است:
- `TransferRequestCreationMixin` - Mixin برای ایجاد transfer requests از orders
- `BaseMultipleFormsetCreateView` - Base CreateView با پشتیبانی از چند formset
- `BaseMultipleFormsetUpdateView` - Base UpdateView با پشتیبانی از چند formset
- `BaseMultipleDocumentCreateView` - Base CreateView برای ایجاد چند document از یک form

---

## کلاس‌ها

### `TransferRequestCreationMixin`

**توضیح**: Mixin برای ایجاد transfer requests از orders

این mixin قابلیت ایجاد transfer request را بعد از ایجاد order فراهم می‌کند، با permission checking و منطق شرطی.

**متدها**:

#### `should_create_transfer_request(self, form) -> bool`

**توضیح**: بررسی اینکه آیا transfer request باید ایجاد شود

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `bool`: `True` اگر transfer request باید ایجاد شود

**منطق پیش‌فرض**:
1. `create_transfer_request` را از `form.cleaned_data` دریافت می‌کند
2. آن را برمی‌گرداند

**نکته**: این متد باید در subclass override شود برای custom logic

#### `get_transfer_request_feature_code(self) -> str`

**توضیح**: برگرداندن feature code برای permission check

**مقدار بازگشتی**:
- `str`: feature code (پیش‌فرض: `self.feature_code`)

**نکته**: این متد باید در subclass override شود برای custom feature code

#### `get_transfer_request_action(self) -> str`

**توضیح**: برگرداندن action name برای permission check

**مقدار بازگشتی**:
- `str`: action name (پیش‌فرض: `'create_transfer_from_order'`)

**نکته**: این متد باید در subclass override شود برای custom action

#### `get_transfer_request_kwargs(self, form) -> Dict[str, Any]`

**توضیح**: برگرداندن kwargs برای ایجاد transfer request

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `Dict[str, Any]`: Dictionary از kwargs برای `_create_transfer_request`

**منطق پیش‌فرض**:
1. `{'approved_by': form.cleaned_data.get('transfer_approved_by'), 'transfer_type': form.cleaned_data.get('transfer_type', 'full'), 'selected_operations': form.cleaned_data.get('selected_operations', [])}` را برمی‌گرداند

**نکته**: این متد باید در subclass override شود برای custom kwargs

#### `create_transfer_request_if_needed(self, form, order) -> Optional[Any]`

**توضیح**: ایجاد transfer request اگر شرایط برقرار باشد

**پارامترهای ورودی**:
- `form`: فرم معتبر
- `order`: order object ایجاد شده

**مقدار بازگشتی**:
- `Optional[Any]`: transfer request ایجاد شده یا `None`

**منطق**:
1. اگر `should_create_transfer_request()` `False` برگرداند، `None` برمی‌گرداند
2. `active_company_id` را از session دریافت می‌کند
3. اگر `active_company_id` وجود نداشته باشد، `None` برمی‌گرداند
4. permission را بررسی می‌کند با `get_user_feature_permissions()` و `has_feature_permission()`
5. اگر permission نداشته باشد، warning message نمایش می‌دهد و `None` برمی‌گرداند
6. kwargs را با `get_transfer_request_kwargs()` دریافت می‌کند
7. `order` و `company_id` را به kwargs اضافه می‌کند
8. `_create_transfer_request()` را فراخوانی می‌کند
9. اگر موفق باشد، success message نمایش می‌دهد و transfer request را برمی‌گرداند
10. اگر exception رخ دهد، warning message نمایش می‌دهد و `None` برمی‌گرداند

#### `_create_transfer_request(self, order, approved_by, company_id: int, **kwargs) -> Any`

**توضیح**: ایجاد transfer request. باید در subclass implement شود.

**پارامترهای ورودی**:
- `order`: order object
- `approved_by`: کاربری که transfer را approve می‌کند
- `company_id`: Company ID
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Any`: transfer request object ایجاد شده

**نکته**: این متد باید در subclass implement شود

---

### `BaseMultipleFormsetCreateView`

**توضیح**: Base CreateView با پشتیبانی از چند formset

این کلاس `BaseCreateView` را گسترش می‌دهد تا چند formset را مدیریت کند (مثلاً PerformanceRecord با formsets مواد، افراد، و ماشین‌ها).

**Type**: `BaseCreateView`

**Attributes**:
- `formsets`: `Dict[str, Any]` - Dictionary mapping formset names به formset classes
- `formset_prefixes`: `Dict[str, str]` - Dictionary mapping formset names به prefixes

**متدها**:

#### `get_formset_kwargs(self, formset_name: str) -> Dict[str, Any]`

**توضیح**: برگرداندن kwargs برای یک formset خاص

**پارامترهای ورودی**:
- `formset_name`: نام formset

**مقدار بازگشتی**:
- `Dict[str, Any]`: Dictionary از kwargs برای formset

**منطق پیش‌فرض**:
1. اگر `self.object` وجود داشته باشد، `{'instance': self.object}` را برمی‌گرداند
2. در غیر این صورت، `{}` را برمی‌گرداند

**نکته**: این متد باید در subclass override شود برای custom kwargs

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن چند formset به context

**پارامترهای ورودی**:
- `**kwargs`: آرگومان‌های اضافی

**مقدار بازگشتی**:
- `Dict[str, Any]`: context شامل formsets

**منطق**:
1. context پایه را از `super().get_context_data()` دریافت می‌کند
2. برای هر formset در `self.formsets`:
   - prefix را از `self.formset_prefixes` دریافت می‌کند (یا از formset_name استفاده می‌کند)
   - اگر request method POST باشد:
     - formset را با POST data ایجاد می‌کند
   - در غیر این صورت:
     - formset خالی ایجاد می‌کند
   - formset را به context با نام `{formset_name}_formset` اضافه می‌کند
3. context را برمی‌گرداند

#### `validate_formsets(self) -> bool`

**توضیح**: اعتبارسنجی تمام formsets

**مقدار بازگشتی**:
- `bool`: `True` اگر تمام formsets معتبر باشند

**منطق**:
1. context را با `get_context_data()` دریافت می‌کند
2. برای هر formset در `self.formsets`:
   - formset را از context دریافت می‌کند
   - اگر formset وجود داشته باشد و معتبر نباشد، `False` برمی‌گرداند
3. `True` برمی‌گرداند

**نکته**: این متد باید در subclass override شود برای custom validation logic

#### `save_formsets(self) -> Dict[str, List[Any]]`

**توضیح**: ذخیره تمام formsets

**مقدار بازگشتی**:
- `Dict[str, List[Any]]`: Dictionary mapping formset names به saved instances

**منطق**:
1. context را با `get_context_data()` دریافت می‌کند
2. `saved_instances` را ایجاد می‌کند
3. برای هر formset در `self.formsets`:
   - formset را از context دریافت می‌کند
   - اگر formset معتبر باشد:
     - `process_formset()` را فراخوانی می‌کند
     - اگر `None` برگرداند، formset را به صورت عادی ذخیره می‌کند
     - در غیر این صورت، instances برگردانده شده را استفاده می‌کند
   - در غیر این صورت، لیست خالی را اضافه می‌کند
4. `saved_instances` را برمی‌گرداند

#### `process_formset(self, formset_name: str, formset) -> Optional[List[Any]]`

**توضیح**: پردازش formset قبل از ذخیره

**پارامترهای ورودی**:
- `formset_name`: نام formset
- `formset`: formset instance

**مقدار بازگشتی**:
- `Optional[List[Any]]`: لیست instances ذخیره شده، یا `None` برای استفاده از default saving

**نکته**: این متد باید در subclass override شود برای custom logic

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: ذخیره form و تمام formsets

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق** (با `@transaction.atomic`):
1. object اصلی را با `form.save()` ذخیره می‌کند
2. برای هر formset در `self.formsets`:
   - formset را با instance جدید دوباره ایجاد می‌کند
   - اگر formset معتبر نباشد، `form_invalid` برمی‌گرداند
3. تمام formsets را با `save_formsets()` ذخیره می‌کند
4. `after_formsets_save()` را فراخوانی می‌کند
5. redirect به success_url برمی‌گرداند

#### `after_formsets_save(self, saved_instances: Dict[str, List[Any]]) -> None`

**توضیح**: Hook فراخوانی شده بعد از ذخیره تمام formsets

**پارامترهای ورودی**:
- `saved_instances`: Dictionary mapping formset names به saved instances

**نکته**: این متد باید در subclass override شود برای custom logic

---

### `BaseMultipleFormsetUpdateView`

**توضیح**: Base UpdateView با پشتیبانی از چند formset

این کلاس `BaseUpdateView` را گسترش می‌دهد تا چند formset را مدیریت کند.

**Type**: `BaseUpdateView`

**Attributes**:
- `formsets`: `Dict[str, Any]` - Dictionary mapping formset names به formset classes
- `formset_prefixes`: `Dict[str, str]` - Dictionary mapping formset names به prefixes

**متدها**:

#### `get_formset_kwargs(self, formset_name: str) -> Dict[str, Any]`

**توضیح**: برگرداندن kwargs برای یک formset خاص (مشابه CreateView)

#### `get_context_data(self, **kwargs) -> Dict[str, Any]`

**توضیح**: اضافه کردن چند formset به context (مشابه CreateView)

#### `validate_formsets(self) -> bool`

**توضیح**: اعتبارسنجی تمام formsets (مشابه CreateView)

#### `save_formsets(self) -> Dict[str, List[Any]]`

**توضیح**: ذخیره تمام formsets (مشابه CreateView)

#### `process_formset(self, formset_name: str, formset) -> Optional[List[Any]]`

**توضیح**: پردازش formset قبل از ذخیره (مشابه CreateView)

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: ذخیره form و تمام formsets

**منطق** (با `@transaction.atomic`):
1. object اصلی را با `form.save()` ذخیره می‌کند
2. تمام formsets را با `validate_formsets()` اعتبارسنجی می‌کند
3. اگر معتبر نباشند، `form_invalid` برمی‌گرداند
4. تمام formsets را با `save_formsets()` ذخیره می‌کند
5. `after_formsets_save()` را فراخوانی می‌کند
6. redirect به success_url برمی‌گرداند

#### `after_formsets_save(self, saved_instances: Dict[str, Any]) -> None`

**توضیح**: Hook فراخوانی شده بعد از ذخیره تمام formsets (مشابه CreateView)

---

### `BaseMultipleDocumentCreateView`

**توضیح**: Base CreateView برای ایجاد چند document از یک form

این کلاس `BaseCreateView` را گسترش می‌دهد تا ایجاد چند document را مدیریت کند (مثلاً TransferToLine که یک document برای هر operation ایجاد می‌کند).

**متدها**:

#### `get_documents_to_create(self, form) -> List[Dict[str, Any]]`

**توضیح**: برگرداندن لیست dictionaryهای داده document برای ایجاد

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `List[Dict[str, Any]]`: لیست dictionaries، هر کدام شامل data برای یک document

**نکته**: این متد باید در subclass implement شود

#### `create_document(self, document_data: Dict[str, Any]) -> Any`

**توضیح**: ایجاد یک document از document_data

**پارامترهای ورودی**:
- `document_data`: Dictionary از data برای document

**مقدار بازگشتی**:
- `Any`: document object ایجاد شده

**نکته**: این متد باید در subclass implement شود

#### `after_document_created(self, document: Any, document_data: Dict[str, Any]) -> None`

**توضیح**: Hook فراخوانی شده بعد از ایجاد هر document

**پارامترهای ورودی**:
- `document`: document ایجاد شده
- `document_data`: data استفاده شده برای ایجاد document

**نکته**: این متد باید در subclass override شود برای custom logic

#### `after_all_documents_created(self, documents: List[Any]) -> None`

**توضیح**: Hook فراخوانی شده بعد از ایجاد تمام documents

**پارامترهای ورودی**:
- `documents`: لیست تمام documents ایجاد شده

**نکته**: این متد باید در subclass override شود برای custom logic

#### `form_valid(self, form) -> HttpResponseRedirect`

**توضیح**: ایجاد چند document از form data

**پارامترهای ورودی**:
- `form`: فرم معتبر

**مقدار بازگشتی**:
- `HttpResponseRedirect`: redirect به success_url

**منطق** (با `@transaction.atomic`):
1. لیست documents برای ایجاد را با `get_documents_to_create()` دریافت می‌کند
2. اگر لیست خالی باشد، error message نمایش می‌دهد و `form_invalid` برمی‌گرداند
3. لیست `created_documents` را ایجاد می‌کند
4. برای هر document_data:
   - `create_document()` را فراخوانی می‌کند
   - document را به لیست اضافه می‌کند
   - `after_document_created()` را فراخوانی می‌کند
   - اگر exception رخ دهد، error message نمایش می‌دهد و transaction را rollback می‌کند
5. `after_all_documents_created()` را فراخوانی می‌کند
6. `self.object` را به اولین document تنظیم می‌کند (برای compatibility)
7. redirect به success_url برمی‌گرداند

---

## وابستگی‌ها

- `shared.views.base`: `BaseCreateView`, `BaseUpdateView`
- `django.contrib`: `messages`
- `django.utils.translation`: `gettext_lazy as _`
- `django.db`: `transaction`
- `django.http`: `HttpResponseRedirect`

---

## استفاده در پروژه

### مثال استفاده از BaseMultipleFormsetCreateView

```python
from shared.views.base_additional import BaseMultipleFormsetCreateView
from production.models import PerformanceRecord
from production.forms import (
    PerformanceRecordForm,
    PerformanceRecordMaterialFormSet,
    PerformanceRecordPersonFormSet,
    PerformanceRecordMachineFormSet,
)

class PerformanceRecordCreateView(BaseMultipleFormsetCreateView):
    model = PerformanceRecord
    form_class = PerformanceRecordForm
    formsets = {
        'materials': PerformanceRecordMaterialFormSet,
        'persons': PerformanceRecordPersonFormSet,
        'machines': PerformanceRecordMachineFormSet,
    }
    formset_prefixes = {
        'materials': 'materials',
        'persons': 'persons',
        'machines': 'machines',
    }
    success_url = reverse_lazy('production:performance_records')
    feature_code = 'production.performance_records'
```

### مثال استفاده از BaseMultipleDocumentCreateView

```python
from shared.views.base_additional import BaseMultipleDocumentCreateView
from production.models import TransferToLine
from production.forms import TransferToLineForm

class TransferToLineCreateView(BaseMultipleDocumentCreateView):
    model = TransferToLine
    form_class = TransferToLineForm
    success_url = reverse_lazy('production:transfer_requests')
    feature_code = 'production.transfer_requests'
    
    def get_documents_to_create(self, form):
        # Return list of document data dictionaries
        order = form.cleaned_data['order']
        operations = form.cleaned_data['operations']
        
        documents = []
        for operation in operations:
            documents.append({
                'order': order,
                'operation': operation,
                'company_id': self.request.session.get('active_company_id'),
            })
        return documents
    
    def create_document(self, document_data):
        return TransferToLine.objects.create(**document_data)
```

---

## نکات مهم

1. **Transaction Safety**: تمام متدهای `form_valid()` با `@transaction.atomic` محافظت می‌شوند

2. **Formset Prefixes**: هنگام استفاده از چند formset، باید prefixهای مختلف استفاده شود

3. **Custom Processing**: متدهای `process_formset()` و `after_formsets_save()` برای custom processing در دسترس هستند

4. **Error Handling**: در `BaseMultipleDocumentCreateView`، اگر ایجاد document با خطا مواجه شود، transaction rollback می‌شود

5. **Hooks**: متدهای hook (`after_document_created`, `after_all_documents_created`, `after_formsets_save`) برای custom logic در دسترس هستند

6. **Permission Checking**: `TransferRequestCreationMixin` permission را بررسی می‌کند قبل از ایجاد transfer request

7. **Flexibility**: تمام متدهای helper می‌توانند در subclass override شوند برای custom behavior
