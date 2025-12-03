"""
AccessLevel CRUD views for shared module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from shared.views.base import AccessLevelPermissionMixin, EditLockProtectedMixin
from shared.mixins import FeaturePermissionRequiredMixin
from shared.models import AccessLevel
from shared.forms import AccessLevelForm


class AccessLevelListView(FeaturePermissionRequiredMixin, ListView):
    """List all access levels."""
    model = AccessLevel
    template_name = 'shared/access_levels_list.html'
    context_object_name = 'object_list'
    paginate_by = 20
    feature_code = 'shared.access_levels'

    def get_queryset(self):
        """Filter access levels by search and status."""
        queryset = AccessLevel.objects.all().order_by('code').prefetch_related('permissions')
        search: Optional[str] = self.request.GET.get('search')
        status: Optional[str] = self.request.GET.get('status')
        if search:
            queryset = queryset.filter(Q(code__icontains=search) | Q(name__icontains=search))
        if status in {'active', 'inactive'}:
            queryset = queryset.filter(is_enabled=1 if status == 'active' else 0)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        
        # Ensure object_list is properly set from page_obj if pagination is used
        if 'page_obj' in context and hasattr(context['page_obj'], 'object_list'):
            context['object_list'] = context['page_obj'].object_list
        elif 'object_list' in context and hasattr(context['object_list'], 'query'):
            context['object_list'] = list(context['object_list'])
        
        context['active_module'] = 'shared'
        context['page_title'] = _('Access Levels')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('Access Levels')},
        ]
        context['create_url'] = reverse_lazy('shared:access_level_create')
        context['create_button_text'] = _('Create Access Level')
        context['show_filters'] = True
        context['status_filter'] = False
        context['status_filter_value'] = self.request.GET.get('status', '')
        context['search_placeholder'] = _('Code or name')
        context['clear_filter_url'] = reverse_lazy('shared:access_levels')
        context['show_actions'] = True
        context['feature_code'] = 'shared.access_levels'
        context['detail_url_name'] = 'shared:access_level_detail'
        context['edit_url_name'] = 'shared:access_level_edit'
        context['delete_url_name'] = 'shared:access_level_delete'
        context['empty_state_title'] = _('No Access Levels Found')
        context['empty_state_message'] = _('Start by defining an access level and assigning feature permissions.')
        context['empty_state_icon'] = '🔐'
        
        return context


class AccessLevelCreateView(FeaturePermissionRequiredMixin, AccessLevelPermissionMixin, CreateView):
    """Create a new access level."""
    model = AccessLevel
    form_class = AccessLevelForm
    template_name = 'shared/access_level_form.html'
    success_url = reverse_lazy('shared:access_levels')
    feature_code = 'shared.access_levels'
    required_action = 'create'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module, form title, and feature permissions to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Create Access Level')
        context['page_title'] = _('Create Access Level')
        context['is_create'] = True
        context['feature_permissions'] = self._prepare_feature_context()
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('Access Levels'), 'url': reverse_lazy('shared:access_levels')},
        ]
        context['cancel_url'] = reverse_lazy('shared:access_levels')
        return context

    def form_valid(self, form: AccessLevelForm) -> Any:
        """Save access level and permissions."""
        response = super().form_valid(form)
        self.object.refresh_from_db()
        self._save_permissions(form)
        messages.success(self.request, _('Access level created successfully.'))
        return response


class AccessLevelUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, AccessLevelPermissionMixin, UpdateView):
    """Update an existing access level."""
    model = AccessLevel
    form_class = AccessLevelForm
    template_name = 'shared/access_level_form.html'
    success_url = reverse_lazy('shared:access_levels')
    edit_lock_redirect_url_name = 'shared:access_levels'
    feature_code = 'shared.access_levels'
    required_action = 'edit_own'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module, form title, and feature permissions to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Edit Access Level')
        context['page_title'] = _('Edit Access Level')
        context['is_create'] = False
        context['feature_permissions'] = self._prepare_feature_context(self.object)
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('Access Levels'), 'url': reverse_lazy('shared:access_levels')},
        ]
        context['cancel_url'] = reverse_lazy('shared:access_levels')
        return context

    def form_valid(self, form: AccessLevelForm) -> Any:
        """Save access level and permissions."""
        response = super().form_valid(form)
        self._save_permissions(form)
        messages.success(self.request, _('Access level updated successfully.'))
        return response


class AccessLevelDetailView(FeaturePermissionRequiredMixin, DetailView):
    """Detail view for viewing access levels (read-only)."""
    model = AccessLevel
    template_name = 'shared/access_level_detail.html'
    context_object_name = 'access_level'
    feature_code = 'shared.access_levels'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Get all access levels."""
        queryset = AccessLevel.objects.all()
        queryset = queryset.prefetch_related(
            'permissions',
            'groups',
        ).select_related('created_by', 'edited_by')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['list_url'] = reverse_lazy('shared:access_levels')
        context['edit_url'] = reverse_lazy('shared:access_level_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        context['feature_code'] = 'shared.access_levels'
        
        # Get permissions for this access level
        from shared.models import AccessLevelPermission
        permissions = AccessLevelPermission.objects.filter(
            access_level=self.object
        ).select_related('access_level').order_by('feature_code', 'action')
        context['permissions'] = permissions
        
        return context


class AccessLevelDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete an access level."""
    model = AccessLevel
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('shared:access_levels')
    feature_code = 'shared.access_levels'
    required_action = 'delete_own'

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Delete access level and show success message."""
        messages.success(self.request, _('Access level deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['delete_title'] = _('Delete Access Level')
        context['confirmation_message'] = _('Are you sure you want to delete access level "{name}"?').format(name=self.object.name)
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('Access Levels'), 'url': reverse_lazy('shared:access_levels')},
            {'label': _('Delete')},
        ]
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.code, 'type': 'code'},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Global'), 'value': self.object.is_global, 'type': 'badge', 'true_label': _('Yes'), 'false_label': _('No')},
        ]
        context['cancel_url'] = reverse_lazy('shared:access_levels')
        return context

