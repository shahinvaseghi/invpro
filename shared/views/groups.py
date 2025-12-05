"""
Group CRUD views for shared module.
"""
from typing import Any, Dict, List, Optional
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from shared.forms import GroupForm
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
    BaseDetailView,
)


class GroupListView(BaseListView):
    """List all groups."""
    model = Group
    template_name = 'shared/groups_list.html'
    feature_code = 'shared.groups'
    search_fields = ['name']
    filter_fields = []
    default_status_filter = True  # We handle status filter manually
    default_order_by = ['name']
    paginate_by = 20
    permission_field = ''  # Skip permission filtering for Group model
    auto_set_company = False  # Groups are not company-scoped
    require_active_company = False  # Groups are global
    
    def get_base_queryset(self) -> QuerySet:
        """Get base queryset with prefetch related."""
        return Group.objects.all().prefetch_related(
            'user_set',
            'profile__access_levels'
        )
    
    def get_queryset(self) -> QuerySet:
        """Filter groups by search and status."""
        # Skip CompanyScopedViewMixin and BaseListView.get_queryset()
        # and use our custom logic directly
        queryset = self.get_base_queryset()
        
        # Apply search
        search_query = self.request.GET.get('search', '').strip()
        if search_query and self.search_fields:
            from shared.filters import apply_search
            queryset = apply_search(queryset, search_query, self.search_fields)
        
        # Apply custom status filter (profile.is_enabled field)
        status: Optional[str] = self.request.GET.get('status')
        if status in {'active', 'inactive'}:
            desired: int = 1 if status == 'active' else 0
            queryset = queryset.filter(profile__is_enabled=desired)
        
        # Apply ordering
        if self.default_order_by:
            queryset = queryset.order_by(*self.default_order_by)
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Groups')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Groups'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('shared:group_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Group')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Group name')
    
    def get_clear_filter_url(self):
        """Return clear filter URL."""
        return reverse('shared:groups')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'shared:group_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'shared:group_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'shared:group_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Groups Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating a group and assigning access levels.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '👥'


class GroupCreateView(BaseCreateView):
    """Create a new group."""
    model = Group
    form_class = GroupForm
    template_name = 'shared/group_form.html'
    success_url = reverse_lazy('shared:groups')
    feature_code = 'shared.groups'
    required_action = 'create'
    success_message = _('Group created successfully.')
    auto_set_company = False  # Groups are not company-scoped
    require_active_company = False  # Groups are global
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Group')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Groups'), 'url': reverse('shared:groups')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:groups')


class GroupUpdateView(BaseUpdateView):
    """Update an existing group."""
    model = Group
    form_class = GroupForm
    template_name = 'shared/group_form.html'
    success_url = reverse_lazy('shared:groups')
    feature_code = 'shared.groups'
    required_action = 'edit_own'
    success_message = _('Group updated successfully.')
    auto_set_company = False  # Groups are not company-scoped
    require_active_company = False  # Groups are global
    permission_field = ''  # Skip permission filtering for Group model
    
    def get_queryset(self) -> QuerySet:
        """Get all groups (no company filtering)."""
        return Group.objects.all()
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Group')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Groups'), 'url': reverse('shared:groups')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:groups')


class GroupDetailView(BaseDetailView):
    """Detail view for viewing groups (read-only)."""
    model = Group
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'group'
    feature_code = 'shared.groups'
    required_action = 'view_own'
    auto_set_company = False  # Groups are not company-scoped
    require_active_company = False  # Groups are global
    permission_field = ''  # Skip permission filtering for Group model
    
    def get_queryset(self) -> QuerySet:
        """Get all groups with prefetch related."""
        return Group.objects.all().prefetch_related(
            'user_set',
            'profile__access_levels',
        )
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Group')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Groups'), 'url': reverse('shared:groups')},
            {'label': _('View'), 'url': None},
        ]
    
    def get_list_url(self):
        """Return list URL."""
        return reverse('shared:groups')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse('shared:group_edit', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add additional context for detail template."""
        context = super().get_context_data(**kwargs)
        
        # Setup detail sections for generic_detail.html
        group = self.object
        detail_sections = []
        
        # Basic Information
        basic_info = {
            'title': _('Basic Information'),
            'fields': [
                {'label': _('Group Name'), 'value': group.name},
            ]
        }
        if group.profile and group.profile.description:
            basic_info['fields'].append({
                'label': _('Description'),
                'value': group.profile.description
            })
        detail_sections.append(basic_info)
        
        # Members
        if group.user_set.exists():
            members = ', '.join([
                user.get_full_name() or user.username
                for user in group.user_set.all()
            ])
            detail_sections.append({
                'title': _('Members') + f' ({group.user_set.count()})',
                'fields': [
                    {'label': _('Members'), 'value': members}
                ]
            })
        
        # Access Levels
        if group.profile and group.profile.access_levels.exists():
            access_levels = ', '.join([
                str(level) for level in group.profile.access_levels.all()
            ])
            detail_sections.append({
                'title': _('Access Levels'),
                'fields': [
                    {'label': _('Access Levels'), 'value': access_levels}
                ]
            })
        
        context['detail_sections'] = detail_sections
        
        # Info banner (format: list of dicts with label, value, type)
        info_banner = [
            {'label': _('Group Name'), 'value': group.name, 'type': 'code'},
        ]
        if group.profile:
            info_banner.append({
                'label': _('Status'),
                'value': group.profile.is_enabled,
                'type': 'badge',
                'true_label': _('Active'),
                'false_label': _('Inactive'),
            })
        context['info_banner'] = info_banner
        
        return context


class GroupDeleteView(BaseDeleteView):
    """Delete a group."""
    model = Group
    success_url = reverse_lazy('shared:groups')
    feature_code = 'shared.groups'
    required_action = 'delete_own'
    success_message = _('Group deleted successfully.')
    auto_set_company = False  # Groups are not company-scoped
    require_active_company = False  # Groups are global
    permission_field = ''  # Skip permission filtering for Group model
    
    def get_queryset(self) -> QuerySet:
        """Get all groups (no company filtering)."""
        return Group.objects.all()
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Group')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete group "{name}"?').format(name=self.object.name)
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Groups'), 'url': reverse('shared:groups')},
            {'label': _('Delete'), 'url': None},
        ]
    
    def get_object_details(self) -> List[Dict[str, Any]]:
        """Return object details for display."""
        return [
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Members'), 'value': self.object.user_set.count()},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:groups')

