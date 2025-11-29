# ticketing/views/entity_reference.py - Entity Reference API Views (Complete Documentation)

**هدف**: API views برای Entity Reference System در ماژول ticketing

این فایل شامل API endpoints برای سیستم سه‌سطحی Entity Reference UI:
1. Sections (از SectionRegistry)
2. Actions (از ActionRegistry برای section انتخاب شده)
3. Parameters (از parameter_schema برای action انتخاب شده)
4. Parameter values (dynamic بر اساس parameter type)

---

## وابستگی‌ها

- `shared.models`: `SectionRegistry`, `ActionRegistry`
- `django.contrib.auth.models`: `Group as AuthGroup`
- `django.http.JsonResponse`
- `django.views.View`
- `django.contrib.auth.decorators.login_required`
- `django.utils.decorators.method_decorator`
- `django.db.models.Q`
- `json`

---

## API Endpoints

### `EntityReferenceSectionsView`

**توضیح**: API endpoint برای دریافت لیست تمام sections فعال از SectionRegistry

**Decorator**: `@method_decorator(login_required, name='dispatch')` (نیاز به authentication)

**HTTP Method**: `GET`

**پارامترهای ورودی**: ندارد

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با لیست sections

**منطق**:
1. دریافت sections:
   - `SectionRegistry.objects.filter(is_enabled=1)`
   - مرتب‌سازی: `order_by('module_code', 'menu_number', 'submenu_number', 'sort_order')`
2. ساخت `sections_data`:
   - برای هر section:
     - `code`: `section.section_code`
     - `nickname`: `section.nickname`
     - `name`: `section.name`
     - `name_en`: `section.name_en or section.name` (fallback به name)
3. بازگشت `JsonResponse({'sections': sections_data})`

**Response Format**:
```json
{
    "sections": [
        {
            "code": "010301",
            "nickname": "users",
            "name": "Users",
            "name_en": "Users"
        }
    ]
}
```

**نکات مهم**:
- فقط sections enabled (`is_enabled=1`) برگردانده می‌شوند
- User می‌تواند nickname یا code را نمایش دهد (frontend تصمیم می‌گیرد)
- نیاز به authentication دارد

**URL**: `/ticketing/api/entity-reference/sections/`

---

### `EntityReferenceActionsView`

**توضیح**: API endpoint برای دریافت لیست actions فعال برای یک section مشخص

**Decorator**: `@method_decorator(login_required, name='dispatch')` (نیاز به authentication)

**HTTP Method**: `GET`

**Query Parameters**:
- `section_code`: Section code (مثلاً "010301") یا nickname (مثلاً "users")

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با لیست actions

**منطق**:
1. دریافت `section_identifier` از query parameter:
   - `request.GET.get('section_code')` یا `request.GET.get('nickname')`
2. اگر `section_identifier` موجود نیست:
   - بازگشت `JsonResponse({'error': 'section_code or nickname required'}, status=400)`
3. **یافتن section**:
   - اگر `section_identifier.isdigit()`: جستجو با `section_code`
   - در غیر این صورت: جستجو با `nickname`
   - `SectionRegistry.objects.get(section_code=section_identifier, is_enabled=1)` یا `SectionRegistry.objects.get(nickname=section_identifier, is_enabled=1)`
   - اگر section پیدا نشود: `JsonResponse({'error': 'Section not found'}, status=404)`
4. دریافت actions:
   - `ActionRegistry.objects.filter(section=section, is_enabled=1)`
   - مرتب‌سازی: `order_by('sort_order', 'action_name')`
5. ساخت `actions_data`:
   - برای هر action:
     - `action_name`: `action.action_name`
     - `action_label`: `action.action_label`
     - `action_label_en`: `action.action_label_en or action.action_label` (fallback)
     - `parameter_schema`: `action.parameter_schema or {}` (fallback به empty dict)
6. بازگشت `JsonResponse({'actions': actions_data})`

**Response Format**:
```json
{
    "actions": [
        {
            "action_name": "show",
            "action_label": "مشاهده",
            "action_label_en": "View",
            "parameter_schema": {}
        }
    ]
}
```

**Error Responses**:
- `400`: section_code or nickname required
- `404`: Section not found

**نکات مهم**:
- فقط actions enabled (`is_enabled=1`) برگردانده می‌شوند
- می‌تواند با section_code (numeric) یا nickname (string) جستجو کند
- نیاز به authentication دارد

**URL**: `/ticketing/api/entity-reference/actions/?section_code=010301` یا `/ticketing/api/entity-reference/actions/?nickname=users`

---

### `EntityReferenceParameterValuesView`

**توضیح**: API endpoint برای دریافت مقادیر ممکن برای یک parameter بر اساس type آن

**Decorator**: `@method_decorator(login_required, name='dispatch')` (نیاز به authentication)

**HTTP Method**: `GET`

**Query Parameters**:
- `parameter_name`: نام parameter (مثلاً "gp", "type", "id")
- `parameter_type`: نوع parameter (مثلاً "string", "integer", "enum", "group", "user", "company", "company_unit")
- `section_code`: Section code (برای برخی parameter types)
- `action_name`: Action name (برای برخی parameter types)

**مقدار بازگشتی**:
- `JsonResponse`: JSON response با مقادیر ممکن

**منطق**:
1. دریافت query parameters:
   - `parameter_name = request.GET.get('parameter_name')`
   - `parameter_type = request.GET.get('parameter_type')`
   - `section_code = request.GET.get('section_code')`
   - `action_name = request.GET.get('action_name')`
2. اگر `parameter_name` یا `parameter_type` موجود نیست:
   - بازگشت `JsonResponse({'error': 'parameter_name and parameter_type required'}, status=400)`
3. **بررسی parameter_type و ساخت values**:
   - **"string"**: `values = []` (empty - user باید مقدار را وارد کند)
   - **"integer"**: `values = []` (empty - user باید مقدار را وارد کند)
   - **"enum"**: 
     - دریافت `section_code` و `action_name`
     - یافتن section (مشابه EntityReferenceActionsView)
     - یافتن action: `ActionRegistry.objects.get(section=section, action_name=action_name, is_enabled=1)`
     - دریافت `parameter_schema` از action
     - دریافت enum values از `parameter_schema[parameter_name].get('enum', [])`
     - ساخت values list از enum values
   - **"group"**:
     - دریافت تمام groups: `AuthGroup.objects.all().order_by('name')`
     - ساخت values: `[{'value': str(g.id), 'label': g.name} for g in groups]`
   - **"user"**:
     - دریافت `company_id` از session
     - اگر `company_id` موجود است:
       - دریافت users: `User.objects.filter(usercompany__company_id=company_id, is_active=True).distinct().order_by('username')`
       - ساخت values: `[{'value': str(u.id), 'label': u.username} for u in users]`
     - در غیر این صورت: `values = []`
   - **"company"**:
     - دریافت companies: `Company.objects.filter(is_enabled=1).order_by('name')`
     - ساخت values: `[{'value': str(c.id), 'label': c.name} for c in companies]`
   - **"company_unit"**:
     - دریافت `company_id` از session
     - اگر `company_id` موجود است:
       - دریافت company units: `CompanyUnit.objects.filter(company_id=company_id, is_enabled=1).order_by('name')`
       - ساخت values: `[{'value': str(cu.id), 'label': cu.name} for cu in company_units]`
     - در غیر این صورت: `values = []`
   - **default**: `values = []`
4. بازگشت `JsonResponse({'values': values})`

**Response Format**:
```json
{
    "values": [
        {"value": "1", "label": "Label 1"},
        {"value": "2", "label": "Label 2"}
    ]
}
```

**Error Responses**:
- `400`: parameter_name and parameter_type required
- `404`: Section not found (برای enum type)

**نکات مهم**:
- برای "enum" type، نیاز به section_code و action_name دارد
- برای "user" و "company_unit" types، نیاز به active_company_id در session دارد
- نیاز به authentication دارد

**URL**: `/ticketing/api/entity-reference/parameter-values/?parameter_name=gp&parameter_type=group`

---

## نکات مهم

1. **Authentication**: تمام endpoints نیاز به authentication دارند (`@login_required`)
2. **Error Handling**: تمام endpoints error handling مناسب دارند
3. **Filtering**: فقط enabled records (`is_enabled=1`) برگردانده می‌شوند
4. **Ordering**: تمام results مرتب می‌شوند
5. **Session Dependency**: برخی endpoints (user، company_unit) نیاز به active_company_id در session دارند

---

## الگوهای مشترک

1. **JSON Response**: تمام endpoints JSON response برمی‌گردانند
2. **Error Handling**: تمام endpoints error handling مناسب دارند
3. **Authentication**: تمام endpoints نیاز به authentication دارند
4. **Enabled Filtering**: فقط enabled records برگردانده می‌شوند
