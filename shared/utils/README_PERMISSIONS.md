# shared/utils/permissions.py - Permission Utilities (Complete Documentation)

**هدف**: Utility functions برای resolve کردن feature permissions کاربران

این فایل شامل:
- **1 Dataclass**: `FeaturePermissionState`
- **3 Helper Functions**: `_feature_key`, `_collect_access_level_ids_for_user`, `_resolve_feature_permissions`
- **3 Public Functions**: `get_user_feature_permissions`, `are_users_in_same_primary_group`, `has_feature_permission`

---

## وابستگی‌ها

- `shared.models`: `AccessLevel`, `AccessLevelPermission`, `GroupProfile`, `UserCompanyAccess`
- `shared.permissions`: `FEATURE_PERMISSION_MAP`
- `django.contrib.auth`: `get_user_model`
- `django.db.models`: `Prefetch`
- `collections`: `defaultdict`
- `dataclasses`: `dataclass`
- `typing`: `Dict`, `Iterable`, `Mapping`, `Optional`, `Set`

---

## FeaturePermissionState

**Type**: `@dataclass(frozen=True)`

**توضیح**: Represents the resolved permissions for a single feature.

**Attributes**:
- `view_scope` (str): Scope of view permission ('none', 'own', 'all')
- `can_view` (bool): Whether user can view this feature
- `actions` (Mapping[str, bool]): Dictionary of action permissions

**نکات مهم**:
- `frozen=True`: Immutable dataclass
- Used to represent resolved permissions for a feature

---

## Helper Functions

### `_feature_key(code: str) -> str`

**توضیح**: Normalize feature code for template-friendly lookups.

**پارامترهای ورودی**:
- `code` (str): Feature code (e.g., `'inventory.items'`)

**مقدار بازگشتی**:
- `str`: Normalized key (e.g., `'inventory__items'`)

**منطق**:
- جایگزینی `.` با `__` برای استفاده در templates

**مثال**:
```python
_feature_key('inventory.items')  # Returns: 'inventory__items'
```

---

### `_collect_access_level_ids_for_user(user: User, company_id: Optional[int]) -> Set[int]`

**توضیح**: Return all active access level IDs applicable to the user.

**پارامترهای ورودی**:
- `user` (User): User object
- `company_id` (Optional[int]): Company ID (None for global)

**مقدار بازگشتی**:
- `Set[int]`: Set of access level IDs

**منطق**:
1. اگر user authenticated نیست، return empty set
2. **Company-scoped access levels**:
   - دریافت `UserCompanyAccess` برای user و company
   - فیلتر: `is_enabled=1`
   - استخراج `access_level_id` از enabled accesses
3. **Group-derived access levels** (global roles):
   - دریافت user groups
   - دریافت `GroupProfile` برای groups
   - دریافت `AccessLevel` از profiles (فقط global ones: `is_global=1`)
   - استخراج access level IDs
4. Return union of both sets

**نکات مهم**:
- Company-scoped: از `UserCompanyAccess` استفاده می‌کند
- Group-derived: از `GroupProfile` و global `AccessLevel` استفاده می‌کند
- فقط enabled access levels در نظر گرفته می‌شوند

---

### `_resolve_feature_permissions(access_level_ids: Iterable[int]) -> Dict[str, FeaturePermissionState]`

**توضیح**: Build a consolidated feature-permission mapping for given AccessLevels.

**پارامترهای ورودی**:
- `access_level_ids` (Iterable[int]): Collection of access level IDs

**مقدار بازگشتی**:
- `Dict[str, FeaturePermissionState]`: Dictionary mapping feature keys to permission states

**منطق**:
1. ایجاد `defaultdict` با default payload:
   - `view_scope`: `'none'`
   - `can_view`: `False`
   - `actions`: `defaultdict(bool)`
2. اگر `access_level_ids` خالی باشد، return empty dict
3. دریافت `AccessLevelPermission` برای access levels
4. برای هر permission:
   - استخراج `resource_code` (feature code)
   - استخراج `metadata.actions` (اگر موجود باشد)
   - تعیین `view_scope` از metadata یا fallback به legacy fields
   - **Scope promotion**: `none < own < all` (highest priority)
   - استخراج actions از metadata
   - Fallback به legacy boolean fields (`can_create`, `can_edit`, etc.)
5. Ensure every known feature has an entry (از `FEATURE_PERMISSION_MAP`)
6. Convert to `FeaturePermissionState` dataclass
7. Return dictionary with normalized keys (`_feature_key`)

**Scope Priority**:
- `none`: 0 (lowest)
- `own`: 1
- `all`: 2 (highest)

**Legacy Support**:
- اگر metadata موجود نباشد، از legacy boolean fields استفاده می‌کند:
  - `can_create` → `create`
  - `can_edit` → `edit_own`
  - `can_delete` → `delete_own`
  - `can_approve` → `approve`

---

## Public Functions

### `are_users_in_same_primary_group(user1: User, user2: User) -> bool`

**توضیح**: بررسی اینکه آیا دو کاربر حداقل یک primary group مشترک دارند.

**پارامترهای ورودی**:
- `user1` (User): کاربر اول
- `user2` (User): کاربر دوم

**مقدار بازگشتی**:
- `bool`: True اگر کاربران حداقل یک primary group مشترک داشته باشند، در غیر این صورت False

**منطق**:
1. اگر `user1` یا `user2` موجود نباشد، return `False`
2. دریافت primary groups برای هر دو کاربر:
   - `user1_groups = set(user1.primary_groups.all().values_list('id', flat=True))`
   - `user2_groups = set(user2.primary_groups.all().values_list('id', flat=True))`
3. بررسی intersection:
   - `return bool(user1_groups & user2_groups)`

**نکات مهم**:
- از `primary_groups` (نه `groups`) استفاده می‌کند
- برای same-group permissions استفاده می‌شود
- اگر intersection موجود باشد، کاربران در same primary group هستند

**مثال**:
```python
if are_users_in_same_primary_group(current_user, resource_owner):
    # Users are in same primary group
    pass
```

---

### `get_user_feature_permissions(user: User, company_id: Optional[int]) -> Dict[str, FeaturePermissionState]`

**توضیح**: Public helper to resolve feature permissions for templates and views.

**پارامترهای ورودی**:
- `user` (User): User object
- `company_id` (Optional[int]): Company ID (None for global)

**مقدار بازگشتی**:
- `Dict[str, FeaturePermissionState]`: Dictionary mapping feature keys to permission states

**منطق**:
1. اگر user authenticated نیست، return empty dict
2. اگر user superuser است:
   - Return special `__superuser__` key با wildcard permissions:
     - `view_scope`: `'all'`
     - `can_view`: `True`
     - `actions`: `{'all': True}`
3. دریافت access level IDs از `_collect_access_level_ids_for_user`
4. Resolve permissions از `_resolve_feature_permissions`
5. Return resolved permissions

**نکات مهم**:
- Superuser bypass: superusers تمام permissions را دارند
- از `_collect_access_level_ids_for_user` و `_resolve_feature_permissions` استفاده می‌کند

**استفاده**:
```python
permissions = get_user_feature_permissions(user, company_id)
if permissions.get('inventory__items'):
    # User has access to inventory.items
    pass
```

---

### `has_feature_permission(permissions: Mapping[str, FeaturePermissionState], feature_code: str, action: str = 'view', allow_own_scope: bool = True, current_user: Optional[User] = None, resource_owner: Optional[User] = None) -> bool`

**توضیح**: Utility for validating a particular feature/action combination.

**پارامترهای ورودی**:
- `permissions` (Mapping[str, FeaturePermissionState]): Permission dictionary (از `get_user_feature_permissions`)
- `feature_code` (str): Feature code (e.g., `'inventory.items'`)
- `action` (str): Action to check (default: `'view'`)
- `allow_own_scope` (bool): Whether to allow 'own' scope for own-scope actions (default: `True`)
- `current_user` (Optional[User]): Current user (required for same_group checks)
- `resource_owner` (Optional[User]): Owner of the resource (required for same_group checks)

**مقدار بازگشتی**:
- `bool`: Whether user has permission for the feature/action

**منطق**:
1. اگر `__superuser__` در permissions باشد، return `True`
2. Normalize feature code با `_feature_key`
3. دریافت `FeaturePermissionState` از permissions
4. اگر state موجود نباشد， return `False`
5. **Special action handling**:
   - `action == 'view'`: return `state.can_view`
   - `action == 'view_all'`: return `state.view_scope == 'all'`
   - `action == 'view_own'`: return `state.view_scope in {'own', 'all'}`
6. **Same group action handling**:
   - اگر action در `{'view_same_group', 'edit_same_group', 'delete_same_group', 'lock_same_group', 'unlock_same_group'}` باشد:
     - بررسی action value از `state.actions.get(action)`
     - اگر action enabled نباشد، return `False`
     - اگر `current_user` و `resource_owner` موجود باشند:
       - فراخوانی `are_users_in_same_primary_group(current_user, resource_owner)`
       - اگر True باشد، return `True`
     - return `False`
7. **Regular action handling**:
   - دریافت action value از `state.actions.get(action)`
   - اگر action enabled باشد، return `True`
8. **Own scope fallback**:
   - اگر `allow_own_scope=True` و action در `{'edit_own', 'delete_own', 'lock_own', 'unlock_own'}` باشد:
     - return `state.view_scope in {'own', 'all'}`

**نکات مهم**:
- Superuser bypass: superusers همیشه `True` return می‌کنند
- Same group actions: نیاز به `current_user` و `resource_owner` دارند
- Own scope fallback: برای own-scope actions، اگر action enabled نباشد، از view_scope استفاده می‌کند

**مثال**:
```python
permissions = get_user_feature_permissions(user, company_id)
if has_feature_permission(permissions, 'inventory.items', 'create'):
    # User can create items
    pass

# Same group permission check
if has_feature_permission(
    permissions, 
    'inventory.items', 
    'edit_same_group',
    current_user=current_user,
    resource_owner=item.created_by
):
    # User can edit items created by users in same primary group
    pass
```

---

## نکات مهم

### 1. Permission Resolution Flow
1. `get_user_feature_permissions` → جمع‌آوری access level IDs
2. `_collect_access_level_ids_for_user` → استخراج IDs از UserCompanyAccess و GroupProfile
3. `_resolve_feature_permissions` → resolve کردن permissions از AccessLevelPermission
4. `has_feature_permission` → بررسی permission برای feature/action خاص

### 2. Superuser Bypass
- Superusers همیشه تمام permissions را دارند
- از `__superuser__` key برای tracking استفاده می‌شود

### 3. Scope Priority
- `none` < `own` < `all`
- Highest scope wins (اگر چند access level داشته باشد)

### 4. Legacy Support
- اگر metadata موجود نباشد، از legacy boolean fields استفاده می‌کند
- برای backward compatibility

### 5. Own Scope Fallback
- برای own-scope actions (`edit_own`, `delete_own`, etc.)، اگر action enabled نباشد، از `view_scope` استفاده می‌کند
- اگر `view_scope in {'own', 'all'}` باشد، permission granted است

### 6. Same Group Permissions
- برای same_group actions (`view_same_group`, `edit_same_group`, etc.)، نیاز به `current_user` و `resource_owner` دارند
- از `are_users_in_same_primary_group` برای بررسی استفاده می‌کند
- فقط اگر کاربران در same primary group باشند، permission granted است

### 7. Template-Friendly Keys
- Feature codes با `.` به `__` تبدیل می‌شوند (برای استفاده در templates)
- مثال: `'inventory.items'` → `'inventory__items'`

### 8. Company vs Global
- Company-scoped: از `UserCompanyAccess` استفاده می‌کند
- Global: از `GroupProfile` و global `AccessLevel` استفاده می‌کند

---

## الگوهای مشترک

1. **Immutable State**: از `frozen` dataclass استفاده می‌کند
2. **Default Values**: از `defaultdict` برای default values استفاده می‌کند
3. **Query Optimization**: از `select_related` و `prefetch_related` استفاده می‌کند
4. **Legacy Support**: از legacy fields برای backward compatibility استفاده می‌کند

---

## استفاده در پروژه

### در Views
```python
from shared.utils.permissions import get_user_feature_permissions, has_feature_permission

company_id = request.session.get('active_company_id')
permissions = get_user_feature_permissions(request.user, company_id)
if has_feature_permission(permissions, 'inventory.items', 'create'):
    # User can create items
    pass
```

### در Templates
```django
{% load access_tags %}
{% get_user_permissions user company_id as permissions %}
{% if permissions|has_permission:'inventory.items' 'create' %}
    <!-- User can create items -->
{% endif %}
```

---

## ارتباط با سایر ماژول‌ها

### Shared Models
- از `AccessLevel`, `AccessLevelPermission`, `GroupProfile`, `UserCompanyAccess` استفاده می‌کند

### Shared Permissions
- از `FEATURE_PERMISSION_MAP` برای feature definitions استفاده می‌کند

### Shared Mixins
- از `FeaturePermissionRequiredMixin` برای permission checking استفاده می‌کند (که از این functions استفاده می‌کند)

