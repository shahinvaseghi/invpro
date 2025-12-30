"""
AccessLevel CRUD views for shared module.
"""
from typing import Any, Dict, List, Optional
from django.db.models import QuerySet
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
    BaseDetailView,
    AccessLevelPermissionMixin,
)
from shared.models import AccessLevel
from shared.forms import AccessLevelForm


class AccessLevelListView(BaseListView):
    """List all access levels."""
    model = AccessLevel
    template_name = 'shared/access_levels_list.html'
    feature_code = 'shared.access_levels'
    search_fields = ['code', 'name']
    filter_fields = []
    default_status_filter = True  # We handle status filter manually
    default_order_by = ['code']
    paginate_by = 20
    permission_field = ''  # Skip permission filtering for AccessLevel model
    auto_set_company = False  # AccessLevels are not company-scoped
    require_active_company = False  # AccessLevels are global
    
    def get_base_queryset(self) -> QuerySet:
        """Get base queryset with prefetch related."""
        return AccessLevel.objects.all().prefetch_related('permissions')
    
    def get_queryset(self) -> QuerySet:
        """Filter access levels by search and status."""
        # Skip CompanyScopedViewMixin and BaseListView.get_queryset()
        # and use our custom logic directly
        queryset = self.get_base_queryset()
        
        # Apply search
        search_query = self.request.GET.get('search', '').strip()
        if search_query and self.search_fields:
            from shared.filters import apply_search
            queryset = apply_search(queryset, search_query, self.search_fields)
        
        # Apply custom status filter (is_enabled field)
        status: Optional[str] = self.request.GET.get('status')
        if status in {'active', 'inactive'}:
            desired: int = 1 if status == 'active' else 0
            queryset = queryset.filter(is_enabled=desired)
        
        # Apply ordering
        if self.default_order_by:
            queryset = queryset.order_by(*self.default_order_by)
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Access Levels')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Access Levels'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('shared:access_level_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Access Level')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Code or name')
    
    def get_clear_filter_url(self):
        """Return clear filter URL."""
        return reverse('shared:access_levels')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'shared:access_level_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'shared:access_level_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'shared:access_level_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Access Levels Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by defining an access level and assigning feature permissions.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '🔐'


class AccessLevelCreateView(BaseCreateView, AccessLevelPermissionMixin):
    """Create a new access level."""
    model = AccessLevel
    form_class = AccessLevelForm
    template_name = 'shared/access_level_form.html'
    success_url = reverse_lazy('shared:access_levels')
    feature_code = 'shared.access_levels'
    required_action = 'create'
    success_message = _('Access level created successfully.')
    auto_set_company = False  # AccessLevels are not company-scoped
    require_active_company = False  # AccessLevels are global
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Access Level')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Access Levels'), 'url': reverse('shared:access_levels')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:access_levels')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add feature permissions to context."""
        context = super().get_context_data(**kwargs)
        context['is_create'] = True
        context['feature_permissions'] = self._prepare_feature_context()
        return context

    def form_valid(self, form: AccessLevelForm) -> Any:
        """Save access level and permissions."""
        response = super().form_valid(form)
        self.object.refresh_from_db()
        self._save_permissions(form)
        return response


class AccessLevelUpdateView(BaseUpdateView, AccessLevelPermissionMixin):
    """Update an existing access level."""
    model = AccessLevel
    form_class = AccessLevelForm
    template_name = 'shared/access_level_form.html'
    success_url = reverse_lazy('shared:access_levels')
    feature_code = 'shared.access_levels'
    required_action = 'edit_own'
    success_message = _('Access level updated successfully.')
    auto_set_company = False  # AccessLevels are not company-scoped
    require_active_company = False  # AccessLevels are global
    permission_field = ''  # Skip permission filtering for AccessLevel model
    
    def get_queryset(self) -> QuerySet:
        """Get all access levels (no company filtering)."""
        return AccessLevel.objects.all()
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Access Level')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Access Levels'), 'url': reverse('shared:access_levels')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:access_levels')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add feature permissions to context."""
        context = super().get_context_data(**kwargs)
        context['is_create'] = False
        context['feature_permissions'] = self._prepare_feature_context(self.object)
        return context

    def form_valid(self, form: AccessLevelForm) -> Any:
        """Save access level and permissions."""
        response = super().form_valid(form)
        self._save_permissions(form)
        return response


class AccessLevelDetailView(BaseDetailView):
    """Detail view for viewing access levels (read-only)."""
    model = AccessLevel
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'shared.access_levels'
    required_action = 'view_own'
    auto_set_company = False  # AccessLevels are not company-scoped
    require_active_company = False  # AccessLevels are global
    permission_field = ''  # Skip permission filtering for AccessLevel model
    
    def get_queryset(self) -> QuerySet:
        """Get all access levels with prefetch related."""
        return AccessLevel.objects.all().prefetch_related(
            'permissions',
            'groups',
        ).select_related('created_by', 'edited_by')
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Access Level')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Access Levels'), 'url': reverse('shared:access_levels')},
            {'label': _('View'), 'url': None},
        ]
    
    def get_list_url(self):
        """Return list URL."""
        return reverse('shared:access_levels')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse('shared:access_level_edit', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add additional context for detail template."""
        context = super().get_context_data(**kwargs)
        
        access_level = self.object
        context['detail_title'] = self.get_page_title()
        
        # Setup detail sections for generic_detail.html
        detail_sections = []
        
        # Basic Information
        basic_fields = [
            {'label': _('Name'), 'value': access_level.name},
        ]
        if access_level.description:
            basic_fields.append({
                'label': _('Description'),
                'value': access_level.description
            })
        detail_sections.append({
            'title': _('Basic Information'),
            'fields': basic_fields,
        })
        
        # Feature Permissions
        from shared.models import AccessLevelPermission
        permissions = AccessLevelPermission.objects.filter(
            access_level=access_level
        ).select_related('access_level').order_by('resource_code')
        
        if permissions.exists():
            from django.utils.encoding import force_str
            permission_data = []
            for perm in permissions:
                actions = []
                if perm.can_view:
                    actions.append(force_str(_('View')))
                if perm.can_create:
                    actions.append(force_str(_('Create')))
                if perm.can_edit:
                    actions.append(force_str(_('Edit')))
                if perm.can_delete:
                    actions.append(force_str(_('Delete')))
                if perm.can_approve:
                    actions.append(force_str(_('Approve')))
                
                permission_data.append([
                    perm.resource_code,
                    ', '.join(actions) if actions else '-',
                    force_str(_('Global') if access_level.is_global else _('Company'))
                ])
            
            detail_sections.append({
                'title': _('Feature Permissions'),
                'type': 'table',
                'headers': [_('Feature Code'), _('Actions'), _('Scope')],
                'data': permission_data
            })
        
        # Assigned Groups
        if access_level.groups.exists():
            groups = ', '.join([str(group) for group in access_level.groups.all()])
            detail_sections.append({
                'title': _('Assigned Groups') + f' ({access_level.groups.count()})',
                'fields': [
                    {'label': _('Groups'), 'value': groups}
                ]
            })
        
        context['detail_sections'] = detail_sections
        
        # Info banner
        info_banner = [
            {'label': _('Code'), 'value': access_level.code, 'type': 'code'},
        ]
        info_banner.append({
            'label': _('Status'),
            'value': access_level.is_enabled,
            'type': 'badge',
            'true_label': _('Active'),
            'false_label': _('Inactive'),
        })
        info_banner.append({
            'label': _('Global'),
            'value': access_level.is_global,
            'type': 'badge',
            'true_label': _('Yes'),
            'false_label': _('No'),
        })
        context['info_banner'] = info_banner
        
        return context


class AccessLevelDeleteView(BaseDeleteView):
    """Delete an access level."""
    model = AccessLevel
    success_url = reverse_lazy('shared:access_levels')
    feature_code = 'shared.access_levels'
    required_action = 'delete_own'
    success_message = _('Access level deleted successfully.')
    auto_set_company = False  # AccessLevels are not company-scoped
    require_active_company = False  # AccessLevels are global
    permission_field = ''  # Skip permission filtering for AccessLevel model
    
    def get_queryset(self) -> QuerySet:
        """Get all access levels (no company filtering)."""
        return AccessLevel.objects.all()
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Access Level')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete access level "{name}"?').format(name=self.object.name)
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Access Levels'), 'url': reverse('shared:access_levels')},
            {'label': _('Delete'), 'url': None},
        ]
    
    def get_object_details(self) -> List[Dict[str, Any]]:
        """Return object details for display."""
        return [
            {'label': _('Code'), 'value': self.object.code, 'type': 'code'},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Global'), 'value': self.object.is_global, 'type': 'badge', 
             'true_label': _('Yes'), 'false_label': _('No')},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:access_levels')

