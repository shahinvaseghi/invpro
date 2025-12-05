"""
Base mixins and helper classes for shared views.
"""
from collections import defaultdict
from typing import Optional, Any, Dict, Set
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils import timezone as tz
from datetime import timedelta
from shared.forms import UserCompanyAccessFormSet

User = get_user_model()


class UserAccessFormsetMixin:
    """Helper mixin to manage UserCompanyAccess formsets."""

    def get_access_formset(self, form: Optional[Any] = None) -> UserCompanyAccessFormSet:
        """Get or create UserCompanyAccess formset for a user."""
        instance = None
        if form is not None:
            instance = form.instance
        elif hasattr(self, 'object'):
            instance = self.object
        if instance is None:
            instance = User()
        return UserCompanyAccessFormSet(
            self.request.POST if self.request.method == 'POST' else None,
            instance=instance,
        )


class AccessLevelPermissionMixin:
    """Mixin to handle access level permissions management."""
    template_name = 'shared/access_level_form.html'

    action_labels: Dict[str, str] = {}

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize action labels."""
        super().__init__(*args, **kwargs)
        from django.utils.translation import gettext_lazy as _
        from shared.permissions import PermissionAction
        
        self.action_labels = {
            PermissionAction.VIEW_OWN.value: _('View own records'),
            PermissionAction.VIEW_ALL.value: _('View all records'),
            PermissionAction.VIEW_SAME_GROUP.value: _('View same group records'),
            PermissionAction.CREATE.value: _('Create'),
            PermissionAction.EDIT_OWN.value: _('Edit own records'),
            PermissionAction.EDIT_OTHER.value: _('Edit others records'),
            PermissionAction.EDIT_SAME_GROUP.value: _('Edit same group records'),
            PermissionAction.DELETE_OWN.value: _('Delete own records'),
            PermissionAction.DELETE_OTHER.value: _('Delete others records'),
            PermissionAction.DELETE_SAME_GROUP.value: _('Delete same group records'),
            PermissionAction.LOCK_OWN.value: _('Lock own documents'),
            PermissionAction.LOCK_OTHER.value: _('Lock others documents'),
            PermissionAction.LOCK_SAME_GROUP.value: _('Lock same group documents'),
            PermissionAction.UNLOCK_OWN.value: _('Unlock own documents'),
            PermissionAction.UNLOCK_OTHER.value: _('Unlock others documents'),
            PermissionAction.UNLOCK_SAME_GROUP.value: _('Unlock same group documents'),
            PermissionAction.APPROVE.value: _('Approve'),
            PermissionAction.REJECT.value: _('Reject'),
            PermissionAction.CANCEL.value: _('Cancel'),
            PermissionAction.CREATE_TRANSFER_FROM_ORDER.value: _('Create Transfer from Order'),
            PermissionAction.CREATE_RECEIPT.value: _('Create Receipt'),
            PermissionAction.CREATE_RECEIPT_FROM_PURCHASE_REQUEST.value: _('Create Receipt from Purchase Request'),
            PermissionAction.CREATE_ISSUE_FROM_WAREHOUSE_REQUEST.value: _('Create Issue from Warehouse Request'),
        }

    def _feature_key(self, code: str) -> str:
        """Convert feature code to HTML-safe key."""
        return code.replace('.', '__')

    def _prepare_feature_context(self, instance: Optional[Any] = None) -> list:
        """Prepare feature permissions context for template."""
        from django.utils.translation import gettext_lazy as _
        from shared.permissions import FEATURE_PERMISSION_MAP, PermissionAction
        
        existing: Dict[str, Dict[str, Any]] = {}
        if instance and instance.pk:
            for perm in instance.permissions.all():
                meta_actions: Dict[str, Any] = {}
                if isinstance(perm.metadata, dict):
                    meta_actions = perm.metadata.get('actions', {})
                existing[perm.resource_code] = {
                    'view_scope': meta_actions.get(
                        'view_scope',
                        'all' if meta_actions.get(PermissionAction.VIEW_ALL.value) else (
                            'own' if meta_actions.get(PermissionAction.VIEW_OWN.value) else ('all' if perm.can_view else 'none')
                        ),
                    ),
                    'checked': {
                        action: bool(meta_actions.get(action)) for action in meta_actions
                    },
                    'fallback_can_create': bool(perm.can_create),
                    'fallback_can_edit': bool(perm.can_edit),
                    'fallback_can_delete': bool(perm.can_delete),
                    'fallback_can_approve': bool(perm.can_approve),
                }
        features: list = []
        for feature in FEATURE_PERMISSION_MAP.values():
            code: str = feature.code
            key: str = self._feature_key(code)
            feature_state: Dict[str, Any] = existing.get(code, {})
            view_scope: str = feature_state.get('view_scope', 'none')
            checked_actions: Dict[str, bool] = feature_state.get('checked', {})
            data_actions: list = []
            for action in feature.actions:
                if action in {PermissionAction.VIEW_OWN, PermissionAction.VIEW_ALL}:
                    continue
                checked: bool = checked_actions.get(action.value, False)
                if not feature_state and action == PermissionAction.CREATE:
                    checked = feature_state.get('fallback_can_create', False)
                if not feature_state and action == PermissionAction.EDIT_OWN:
                    checked = feature_state.get('fallback_can_edit', False)
                if not feature_state and action == PermissionAction.DELETE_OWN:
                    checked = feature_state.get('fallback_can_delete', False)
                if not feature_state and action == PermissionAction.APPROVE:
                    checked = feature_state.get('fallback_can_approve', False)
                data_actions.append(
                    {
                        'code': action.value,
                        'label': self.action_labels[action.value],
                        'checked': checked,
                    }
                )
            # Extract module from feature code (e.g., "production.product_orders" -> "production")
            module_code = code.split('.')[0] if '.' in code else 'shared'
            
            features.append(
                {
                    'code': code,
                    'html_id': key,
                    'label': feature.label,
                    'module_code': module_code,
                    'view_supported': PermissionAction.VIEW_OWN in feature.actions or PermissionAction.VIEW_ALL in feature.actions,
                    'view_scope': view_scope,
                    'actions': data_actions,
                }
            )
        
        # Group features by module
        grouped_features = defaultdict(list)
        for feature in features:
            grouped_features[feature['module_code']].append(feature)
        
        # Convert to list of dicts with module info
        module_list = []
        module_labels = {
            'shared': _('Shared'),
            'production': _('Production'),
            'inventory': _('Inventory'),
            'qc': _('Quality Control'),
            'ticketing': _('Ticketing'),
            'accounting': _('Accounting'),
            'sales': _('Sales'),
            'hr': _('Human Resources'),
            'office_automation': _('Office Automation'),
            'transportation': _('Transportation'),
            'procurement': _('Procurement'),
        }
        
        for module_code, module_features in sorted(grouped_features.items()):
            module_list.append({
                'code': module_code,
                'label': module_labels.get(module_code, module_code.title()),
                'features': module_features,
            })
        
        return module_list

    def _save_permissions(self, form: Any) -> None:
        """Save permissions from form POST data."""
        from shared.permissions import FEATURE_PERMISSION_MAP, PermissionAction
        
        active_codes: Set[str] = set()
        for feature in FEATURE_PERMISSION_MAP.values():
            code: str = feature.code
            html_key: str = self._feature_key(code)
            view_scope: str = self.request.POST.get(f'perm-{html_key}-view', 'none')
            selected_actions: list = []
            for action in feature.actions:
                if action in {PermissionAction.VIEW_OWN, PermissionAction.VIEW_ALL}:
                    continue
                if self.request.POST.get(f'perm-{html_key}-{action.value}') == 'on':
                    selected_actions.append(action)

            if view_scope == 'none' and not selected_actions:
                # Remove existing permission if it exists
                self.object.permissions.filter(resource_code=code).delete()
                continue

            perm, _created = self.object.permissions.get_or_create(
                resource_code=code,
                defaults={
                    'module_code': code.split('.')[0],
                    'resource_type': 'menu',
                },
            )
            perm.module_code = code.split('.')[0]
            perm.resource_type = 'menu'
            perm.can_view = 1 if view_scope != 'none' else 0
            perm.can_create = 1 if PermissionAction.CREATE in selected_actions else 0
            perm.can_edit = 1 if PermissionAction.EDIT_OWN in selected_actions else 0
            perm.can_delete = 1 if PermissionAction.DELETE_OWN in selected_actions else 0
            perm.can_approve = 1 if PermissionAction.APPROVE in selected_actions else 0

            metadata_actions: Dict[str, Any] = {
                'view_scope': view_scope,
                PermissionAction.VIEW_OWN.value: view_scope in {'own', 'all'},
                PermissionAction.VIEW_ALL.value: view_scope == 'all',
            }
            for action in feature.actions:
                if action in {PermissionAction.VIEW_OWN, PermissionAction.VIEW_ALL}:
                    continue
                metadata_actions[action.value] = action in selected_actions
            perm.metadata = {'actions': metadata_actions}
            perm.save()
            active_codes.add(code)

        # Remove stale permissions not present anymore
        self.object.permissions.exclude(resource_code__in=active_codes).delete()


class EditLockProtectedMixin:
    """
    Mixin to prevent concurrent editing of records.
    
    This mixin checks if a record is being edited by another user when
    opening the edit form (GET request). If so, it blocks access and shows
    an error message.
    
    The edit lock is automatically set when opening the form and cleared
    after saving or canceling.
    
    Timeout: 5 minutes (edit locks older than 5 minutes are considered stale)
    """
    edit_lock_timeout_minutes = 5
    edit_lock_error_message = _('این رکورد در حال ویرایش توسط {user_name} است و نمی‌توانید همزمان آن را ویرایش کنید.')
    edit_lock_redirect_url_name = None
    
    def dispatch(self, request, *args, **kwargs):
        """Check edit lock before allowing access to edit form."""
        # Only check for GET requests (opening the form)
        if request.method == 'GET':
            obj = self.get_object()
            
            # Check if object has EditableModel mixin
            if not hasattr(obj, 'editing_by'):
                return super().dispatch(request, *args, **kwargs)
            
            # Refresh from DB to get latest state
            obj.refresh_from_db()
            
            # Check for stale locks (older than timeout)
            if obj.editing_by and obj.editing_started_at:
                timeout_threshold = timezone.now() - timedelta(minutes=self.edit_lock_timeout_minutes)
                if obj.editing_started_at < timeout_threshold:
                    # Lock is stale, clear it
                    obj.clear_edit_lock()
                    obj.refresh_from_db()
            
            # Check if record is being edited by another user/session
            # Only check if editing_by is still set (not cleared by timeout)
            if obj.editing_by:
                current_session_key = request.session.session_key or ''
                # Check if it's being edited by someone else
                if obj.is_being_edited_by(user=request.user, session_key=current_session_key):
                    # Record is being edited by someone else
                    editor_name = obj.editing_by.get_full_name() or obj.editing_by.username if obj.editing_by else _('کاربر ناشناس')
                    messages.error(
                        request,
                        self.edit_lock_error_message.format(user_name=editor_name)
                    )
                    # Redirect to list or detail view
                    redirect_url = self._get_edit_lock_redirect_url()
                    return HttpResponseRedirect(redirect_url)
            
            # Set edit lock for current user
            current_session_key = request.session.session_key or ''
            obj.editing_by = request.user
            obj.editing_started_at = timezone.now()
            obj.editing_session_key = current_session_key
            obj.save(update_fields=['editing_by', 'editing_started_at', 'editing_session_key'])
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Clear edit lock after successful save."""
        result = super().form_valid(form)
        self._clear_edit_lock()
        return result
    
    def form_invalid(self, form):
        """Keep edit lock on validation errors (user is still editing)."""
        return super().form_invalid(form)
    
    def _clear_edit_lock(self):
        """Clear the edit lock for the current object."""
        if hasattr(self, 'object') and self.object and hasattr(self.object, 'clear_edit_lock'):
            self.object.clear_edit_lock()
    
    def _get_edit_lock_redirect_url(self) -> str:
        """Get redirect URL when edit lock is active."""
        # Priority 1: Explicit redirect URL name
        if self.edit_lock_redirect_url_name:
            return reverse(self.edit_lock_redirect_url_name)
        
        # Priority 2: List URL name
        if hasattr(self, 'list_url_name') and self.list_url_name:
            return reverse(self.list_url_name)
        
        # Priority 3: Success URL (most common case - handles reverse_lazy)
        if hasattr(self, 'success_url') and self.success_url:
            if isinstance(self.success_url, str):
                return self.success_url
            elif hasattr(self.success_url, 'url'):
                return self.success_url.url
            else:
                # Handle reverse_lazy: convert to string to resolve it
                try:
                    # reverse_lazy objects are resolved when converted to string
                    return str(self.success_url)
                except Exception:
                    pass
        
        # Priority 4: Use get_success_url() method if available (handles reverse_lazy properly)
        # Note: This might need self.object, so we try it after checking success_url directly
        if hasattr(self, 'get_success_url'):
            try:
                # Make sure object is available
                if not hasattr(self, 'object') or not self.object:
                    obj = self.get_object()
                    if obj:
                        self.object = obj
                return self.get_success_url()
            except Exception:
                pass
        
        # Priority 5: Object detail URL
        if hasattr(self, 'object') and self.object and hasattr(self.object, 'get_absolute_url'):
            try:
                return self.object.get_absolute_url()
            except Exception:
                pass
        
        # Last resort: redirect to home
        return '/'


# ============================================================================
# Base View Classes
# ============================================================================

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.db.models import QuerySet, Prefetch
from django.urls import reverse_lazy, reverse
from typing import List, Optional, Dict, Any
from shared.mixins import (
    FeaturePermissionRequiredMixin,
    PermissionFilterMixin,
    CompanyScopedViewMixin,
    AutoSetFieldsMixin,
    SuccessMessageMixin,
)
from shared.filters import (
    apply_search,
    apply_status_filter,
    apply_company_filter,
    apply_multi_field_filter,
)


class BaseListView(
    FeaturePermissionRequiredMixin,
    PermissionFilterMixin,
    CompanyScopedViewMixin,
    ListView
):
    """
    Base ListView with common functionality for all modules.
    
    This class provides:
    - Automatic search filtering
    - Status filtering
    - Company filtering
    - Permission filtering
    - Standard context setup
    - Pagination
    
    Usage:
        class ItemTypeListView(BaseListView):
            model = ItemType
            search_fields = ['name', 'public_code', 'name_en']
            filter_fields = ['is_enabled']
            feature_code = 'inventory.master.item_types'
            permission_field = 'created_by'
            default_order_by = ['public_code']
            
            def get_breadcrumbs(self):
                return [
                    {'label': _('Inventory'), 'url': None},
                    {'label': _('Item Types'), 'url': None},
                ]
    """
    
    # Required attributes
    model = None
    feature_code: Optional[str] = None
    
    # Search and filter configuration
    search_fields: List[str] = []
    filter_fields: List[str] = []
    permission_field: str = 'created_by'
    default_status_filter: bool = True
    default_order_by: List[str] = []
    paginate_by: int = 50
    
    # Template configuration
    template_name: str = 'shared/generic/generic_list.html'
    context_object_name: str = 'object_list'
    
    def get_queryset(self) -> QuerySet:
        """Build queryset with filters, search, and permissions."""
        # Get base queryset
        queryset = self.get_base_queryset()
        
        # Apply company filter
        company_id = self.request.session.get('active_company_id')
        queryset = apply_company_filter(queryset, company_id)
        
        # Apply permission filtering
        if self.feature_code and self.permission_field:
            queryset = self.filter_queryset_by_permissions(
                queryset,
                self.feature_code,
                self.permission_field
            )
        
        # Apply prefetch/select related
        prefetch_related = self.get_prefetch_related()
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        
        select_related = self.get_select_related()
        if select_related:
            queryset = queryset.select_related(*select_related)
        
        # Apply search
        search_query = self.request.GET.get('search', '').strip()
        if search_query and self.search_fields:
            queryset = apply_search(queryset, search_query, self.search_fields)
        
        # Apply status filter
        if self.default_status_filter:
            status_value = self.request.GET.get('status', '')
            queryset = apply_status_filter(queryset, status_value)
        
        # Apply custom filters
        queryset = self.apply_custom_filters(queryset)
        
        # Apply ordering
        if self.default_order_by:
            queryset = queryset.order_by(*self.default_order_by)
        
        return queryset
    
    def get_base_queryset(self) -> QuerySet:
        """Get base queryset. Override for custom base filtering."""
        return self.model.objects.all()
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch. Override for custom prefetch."""
        return []
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related. Override for custom select."""
        return []
    
    def apply_custom_filters(self, queryset: QuerySet) -> QuerySet:
        """Apply custom filters. Override for additional filtering."""
        if self.filter_fields:
            filter_map = {field: field for field in self.filter_fields}
            queryset = apply_multi_field_filter(queryset, self.request, filter_map)
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Setup standard context for list view."""
        context = super().get_context_data(**kwargs)
        
        # Page title
        context['page_title'] = self.get_page_title()
        
        # Breadcrumbs
        context['breadcrumbs'] = self.get_breadcrumbs()
        
        # Create URL
        context['create_url'] = self.get_create_url()
        context['create_button_text'] = self.get_create_button_text()
        
        # Filter configuration
        context['show_filters'] = True
        context['status_filter'] = self.default_status_filter
        context['search_placeholder'] = self.get_search_placeholder()
        context['clear_filter_url'] = self.get_clear_filter_url()
        
        # Actions configuration
        context['show_actions'] = True
        context['feature_code'] = self.feature_code
        context['detail_url_name'] = self.get_detail_url_name()
        context['edit_url_name'] = self.get_edit_url_name()
        context['delete_url_name'] = self.get_delete_url_name()
        
        # Empty state
        context['empty_state_title'] = self.get_empty_state_title()
        context['empty_state_message'] = self.get_empty_state_message()
        context['empty_state_icon'] = self.get_empty_state_icon()
        
        # Stats (if enabled)
        stats = self.get_stats()
        if stats:
            context['stats'] = stats
            context['stats_labels'] = self.get_stats_labels()
        
        return context
    
    # Hook methods for customization
    def get_page_title(self) -> str:
        """Return page title. Override for custom title."""
        return str(self.model._meta.verbose_name_plural)
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list. Override for custom breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': self.get_page_title(), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL. Override for custom URL."""
        return None
    
    def get_create_button_text(self) -> str:
        """Return create button text. Override for custom text."""
        return _('Create')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder. Override for custom placeholder."""
        return _('Search...')
    
    def get_clear_filter_url(self):
        """Return clear filter URL. Override for custom URL."""
        return reverse_lazy(self.request.resolver_match.url_name)
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name. Override for custom URL name."""
        return None
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name. Override for custom URL name."""
        return None
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name. Override for custom URL name."""
        return None
    
    def get_empty_state_title(self) -> str:
        """Return empty state title. Override for custom title."""
        return _('No items found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message. Override for custom message."""
        return _('Start by creating your first item.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon. Override for custom icon."""
        return '📋'
    
    def get_stats(self) -> Optional[Dict[str, int]]:
        """Return stats dictionary. Override for custom stats."""
        return None
    
    def get_stats_labels(self) -> Dict[str, str]:
        """Return stats labels dictionary. Override for custom labels."""
        return {}


class BaseCreateView(
    FeaturePermissionRequiredMixin,
    AutoSetFieldsMixin,
    SuccessMessageMixin,
    CompanyScopedViewMixin,
    CreateView
):
    """
    Base CreateView with common functionality for all modules.
    
    This class provides:
    - Automatic company_id and created_by setting
    - Success message display
    - Standard context setup
    - Form kwargs with company_id
    
    Usage:
        class ItemTypeCreateView(BaseCreateView):
            model = ItemType
            form_class = ItemTypeForm
            success_url = reverse_lazy('inventory:item_types')
            feature_code = 'inventory.master.item_types'
            success_message = _('Item type created successfully.')
            
            def get_breadcrumbs(self):
                return [
                    {'label': _('Inventory'), 'url': None},
                    {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
                    {'label': _('Create'), 'url': None},
                ]
    """
    
    # Required attributes
    model = None
    form_class = None
    success_url = None
    feature_code: Optional[str] = None
    
    # Template configuration
    template_name: str = 'shared/generic/generic_form.html'
    
    def get_form_kwargs(self):
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Setup standard context for create view."""
        context = super().get_context_data(**kwargs)
        
        # Form title
        context['form_title'] = self.get_form_title()
        
        # Breadcrumbs
        context['breadcrumbs'] = self.get_breadcrumbs()
        
        # Cancel URL
        context['cancel_url'] = self.get_cancel_url()
        
        return context
    
    # Hook methods for customization
    def get_form_title(self) -> str:
        """Return form title. Override for custom title."""
        return _('Create {model}').format(model=self.model._meta.verbose_name)
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list. Override for custom breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': self.model._meta.verbose_name_plural, 'url': None},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL. Override for custom URL."""
        return self.success_url


class BaseUpdateView(
    EditLockProtectedMixin,
    FeaturePermissionRequiredMixin,
    AutoSetFieldsMixin,
    SuccessMessageMixin,
    CompanyScopedViewMixin,
    UpdateView
):
    """
    Base UpdateView with common functionality for all modules.
    
    This class provides:
    - Edit lock protection
    - Automatic edited_by setting
    - Success message display
    - Standard context setup
    - Form kwargs with company_id
    
    Usage:
        class ItemTypeUpdateView(BaseUpdateView):
            model = ItemType
            form_class = ItemTypeForm
            success_url = reverse_lazy('inventory:item_types')
            feature_code = 'inventory.master.item_types'
            success_message = _('Item type updated successfully.')
            
            def get_breadcrumbs(self):
                return [
                    {'label': _('Inventory'), 'url': None},
                    {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
                    {'label': _('Edit'), 'url': None},
                ]
    """
    
    # Required attributes
    model = None
    form_class = None
    success_url = None
    feature_code: Optional[str] = None
    
    # Template configuration
    template_name: str = 'shared/generic/generic_form.html'
    
    def get_form_kwargs(self):
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Setup standard context for update view."""
        context = super().get_context_data(**kwargs)
        
        # Form title
        context['form_title'] = self.get_form_title()
        
        # Breadcrumbs
        context['breadcrumbs'] = self.get_breadcrumbs()
        
        # Cancel URL
        context['cancel_url'] = self.get_cancel_url()
        
        return context
    
    # Hook methods for customization
    def get_form_title(self) -> str:
        """Return form title. Override for custom title."""
        return _('Edit {model}').format(model=self.model._meta.verbose_name)
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list. Override for custom breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': self.model._meta.verbose_name_plural, 'url': None},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL. Override for custom URL."""
        return self.success_url


class BaseDeleteView(
    FeaturePermissionRequiredMixin,
    SuccessMessageMixin,
    CompanyScopedViewMixin,
    DeleteView
):
    """
    Base DeleteView with common functionality for all modules.
    
    This class provides:
    - Success message display
    - Standard context setup
    - Object details display
    
    Usage:
        class ItemTypeDeleteView(BaseDeleteView):
            model = ItemType
            success_url = reverse_lazy('inventory:item_types')
            feature_code = 'inventory.master.item_types'
            success_message = _('Item type deleted successfully.')
            
            def get_breadcrumbs(self):
                return [
                    {'label': _('Inventory'), 'url': None},
                    {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
                    {'label': _('Delete'), 'url': None},
                ]
            
            def get_object_details(self):
                return [
                    {'label': _('Name'), 'value': self.object.name},
                    {'label': _('Code'), 'value': self.object.public_code, 'type': 'code'},
                ]
    """
    
    # Required attributes
    model = None
    success_url = None
    feature_code: Optional[str] = None
    
    # Template configuration
    template_name: str = 'shared/generic/generic_confirm_delete.html'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Setup standard context for delete view."""
        context = super().get_context_data(**kwargs)
        
        # Delete title
        context['delete_title'] = self.get_delete_title()
        
        # Confirmation message
        context['confirmation_message'] = self.get_confirmation_message()
        
        # Breadcrumbs
        context['breadcrumbs'] = self.get_breadcrumbs()
        
        # Object details
        context['object_details'] = self.get_object_details()
        
        # Cancel URL
        context['cancel_url'] = self.get_cancel_url()
        
        return context
    
    # Hook methods for customization
    def get_delete_title(self) -> str:
        """Return delete title. Override for custom title."""
        return _('Delete {model}').format(model=self.model._meta.verbose_name)
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message. Override for custom message."""
        return _('Are you sure you want to delete this {model}? This action cannot be undone.').format(
            model=self.model._meta.verbose_name
        )
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list. Override for custom breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': self.model._meta.verbose_name_plural, 'url': None},
            {'label': _('Delete'), 'url': None},
        ]
    
    def get_object_details(self) -> List[Dict[str, Any]]:
        """Return object details for display. Override for custom details."""
        details = []
        if hasattr(self.object, 'public_code'):
            details.append({
                'label': _('Code'),
                'value': self.object.public_code,
                'type': 'code'
            })
        if hasattr(self.object, 'name'):
            details.append({
                'label': _('Name'),
                'value': self.object.name
            })
        return details
    
    def get_cancel_url(self):
        """Return cancel URL. Override for custom URL."""
        return self.success_url
    
    def validate_deletion(self) -> tuple[bool, Optional[str]]:
        """
        Validate if object can be deleted. Override for custom validation.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        return True, None


class BaseDetailView(
    FeaturePermissionRequiredMixin,
    PermissionFilterMixin,
    CompanyScopedViewMixin,
    DetailView
):
    """
    Base DetailView with common functionality for all modules.
    
    This class provides:
    - Permission filtering
    - Standard context setup
    - Edit permission check
    
    Usage:
        class ItemTypeDetailView(BaseDetailView):
            model = ItemType
            feature_code = 'inventory.master.item_types'
            
            def get_breadcrumbs(self):
                return [
                    {'label': _('Inventory'), 'url': None},
                    {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
                    {'label': _('View'), 'url': None},
                ]
    """
    
    # Required attributes
    model = None
    feature_code: Optional[str] = None
    
    # Template configuration
    template_name: str = 'shared/generic/generic_detail.html'
    context_object_name: str = 'object'
    
    def get_queryset(self) -> QuerySet:
        """Filter queryset by permissions."""
        queryset = super().get_queryset()
        
        # Apply permission filtering
        if self.feature_code and self.permission_field:
            queryset = self.filter_queryset_by_permissions(
                queryset,
                self.feature_code,
                self.permission_field
            )
        
        return queryset
    
    @property
    def permission_field(self) -> str:
        """Return permission field name. Override for custom field."""
        return 'created_by'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Setup standard context for detail view."""
        context = super().get_context_data(**kwargs)
        
        # Page title
        context['page_title'] = self.get_page_title()
        
        # Breadcrumbs
        context['breadcrumbs'] = self.get_breadcrumbs()
        
        # URLs
        context['list_url'] = self.get_list_url()
        context['edit_url'] = self.get_edit_url()
        
        # Permissions
        context['can_edit'] = self.can_edit_object()
        context['feature_code'] = self.feature_code
        
        return context
    
    # Hook methods for customization
    def get_page_title(self) -> str:
        """Return page title. Override for custom title."""
        return str(self.object)
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list. Override for custom breadcrumbs."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': self.model._meta.verbose_name_plural, 'url': None},
            {'label': _('View'), 'url': None},
        ]
    
    def get_list_url(self):
        """Return list URL. Override for custom URL."""
        return None
    
    def get_edit_url(self):
        """Return edit URL. Override for custom URL."""
        return None
    
    def can_edit_object(self) -> bool:
        """Check if object can be edited. Override for custom logic."""
        # Check if object is locked
        if hasattr(self.object, 'is_locked'):
            return not bool(self.object.is_locked)
        return True


class BaseFormsetCreateView(BaseCreateView):
    """
    Base CreateView with formset support.
    
    This class extends BaseCreateView to handle formsets for related objects.
    
    Usage:
        class BOMCreateView(BaseFormsetCreateView):
            model = BOM
            form_class = BOMForm
            formset_class = BOMMaterialLineFormSet
            success_url = reverse_lazy('production:bom_list')
            feature_code = 'production.bom'
    """
    
    formset_class = None
    formset_prefix: str = 'formset'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add formset to context."""
        context = super().get_context_data(**kwargs)
        
        # Add formset
        if self.request.method == 'POST':
            formset = self.formset_class(
                self.request.POST,
                prefix=self.formset_prefix,
                **self.get_formset_kwargs()
            )
        else:
            formset = self.formset_class(
                prefix=self.formset_prefix,
                **self.get_formset_kwargs()
            )
        
        context['formset'] = formset
        
        return context
    
    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset. Override for custom kwargs."""
        kwargs = {}
        if hasattr(self, 'object') and self.object:
            kwargs['instance'] = self.object
        return kwargs
    
    def form_valid(self, form):
        """Save form and formset."""
        from django.db import transaction
        
        with transaction.atomic():
            # Save main object first
            response = super().form_valid(form)
            
            # Save formset
            formset = self.formset_class(
                self.request.POST,
                instance=self.object,
                prefix=self.formset_prefix,
                **self.get_formset_kwargs()
            )
            
            if formset.is_valid():
                formset.save()
            else:
                # Formset validation failed
                return self.form_invalid(form)
        
        return response


class BaseFormsetUpdateView(BaseUpdateView):
    """
    Base UpdateView with formset support.
    
    This class extends BaseUpdateView to handle formsets for related objects.
    
    Usage:
        class BOMUpdateView(BaseFormsetUpdateView):
            model = BOM
            form_class = BOMForm
            formset_class = BOMMaterialLineFormSet
            success_url = reverse_lazy('production:bom_list')
            feature_code = 'production.bom'
    """
    
    formset_class = None
    formset_prefix: str = 'formset'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add formset to context."""
        context = super().get_context_data(**kwargs)
        
        # Add formset
        if self.request.method == 'POST':
            formset = self.formset_class(
                self.request.POST,
                instance=self.object,
                prefix=self.formset_prefix,
                **self.get_formset_kwargs()
            )
        else:
            formset = self.formset_class(
                instance=self.object,
                prefix=self.formset_prefix,
                **self.get_formset_kwargs()
            )
        
        context['formset'] = formset
        
        return context
    
    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset. Override for custom kwargs."""
        return {}
    
    def form_valid(self, form):
        """Save form and formset."""
        from django.db import transaction
        
        with transaction.atomic():
            # Save main object first
            response = super().form_valid(form)
            
            # Save formset
            formset = self.formset_class(
                self.request.POST,
                instance=self.object,
                prefix=self.formset_prefix,
                **self.get_formset_kwargs()
            )
            
            if formset.is_valid():
                formset.save()
            else:
                # Formset validation failed
                return self.form_invalid(form)
        
        return response


class BaseDocumentListView(BaseListView):
    """
    Base ListView for documents with lines (Receipts, Issues, etc.).
    
    This class extends BaseListView to provide:
    - Prefetch lines and related objects
    - Stats calculation
    
    Usage:
        class ReceiptPermanentListView(BaseDocumentListView):
            model = ReceiptPermanent
            feature_code = 'inventory.receipts.permanent'
            prefetch_lines = True
            stats_enabled = True
    """
    
    prefetch_lines: bool = True
    stats_enabled: bool = True
    
    def get_prefetch_related(self) -> List[str]:
        """Prefetch lines and related objects."""
        prefetch = super().get_prefetch_related()
        
        if self.prefetch_lines:
            # Try to find lines relationship
            # Common patterns: 'lines', 'line_set', model_name.lower() + '_line_set'
            model_name = self.model.__name__.lower()
            possible_line_names = [
                'lines',
                'line_set',
                f'{model_name}_line_set',
                f'{model_name}line_set',
            ]
            
            for line_name in possible_line_names:
                if hasattr(self.model, line_name):
                    prefetch.append(line_name)
                    break
        
        return prefetch
    
    def get_stats(self) -> Optional[Dict[str, int]]:
        """Calculate stats for documents. Override for custom stats."""
        if not self.stats_enabled:
            return None
        
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return None
        
        base_qs = self.model.objects.filter(company_id=company_id)
        
        stats = {
            'total': base_qs.count(),
        }
        
        # Try to add status-based stats if model has status field
        if hasattr(self.model, 'status'):
            from django.db.models import Count
            status_stats = base_qs.values('status').annotate(count=Count('id'))
            for stat in status_stats:
                stats[stat['status']] = stat['count']
        
        return stats


class BaseDocumentCreateView(BaseFormsetCreateView):
    """
    Base CreateView for documents with lines.
    
    This class extends BaseFormsetCreateView to handle document headers and lines.
    
    Usage:
        class ReceiptPermanentCreateView(BaseDocumentCreateView):
            model = ReceiptPermanent
            form_class = ReceiptPermanentForm
            formset_class = ReceiptPermanentLineFormSet
            success_url = reverse_lazy('inventory:receipt_permanent')
            feature_code = 'inventory.receipts.permanent'
    """
    
    def save_lines_formset(self, formset):
        """Save lines formset. Override for custom line saving logic."""
        if formset.is_valid():
            formset.save()
        else:
            raise ValueError("Formset is not valid")


class BaseDocumentUpdateView(BaseFormsetUpdateView):
    """
    Base UpdateView for documents with lines.
    
    This class extends BaseFormsetUpdateView to handle document headers and lines.
    
    Usage:
        class ReceiptPermanentUpdateView(BaseDocumentUpdateView):
            model = ReceiptPermanent
            form_class = ReceiptPermanentForm
            formset_class = ReceiptPermanentLineFormSet
            success_url = reverse_lazy('inventory:receipt_permanent')
            feature_code = 'inventory.receipts.permanent'
    """
    
    def save_lines_formset(self, formset):
        """Save lines formset. Override for custom line saving logic."""
        if formset.is_valid():
            formset.save()
        else:
            raise ValueError("Formset is not valid")

