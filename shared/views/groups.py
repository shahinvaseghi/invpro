"""
Group CRUD views for shared module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.forms import GroupForm
from shared.views.base import EditLockProtectedMixin


class GroupListView(FeaturePermissionRequiredMixin, ListView):
    """List all groups."""
    model = Group
    template_name = 'shared/groups_list.html'
    context_object_name = 'object_list'
    paginate_by = 20
    feature_code = 'shared.groups'

    def get_queryset(self):
        """Filter groups by search and status."""
        search: Optional[str] = self.request.GET.get('search')
        queryset = Group.objects.all().order_by('name').prefetch_related('user_set', 'profile__access_levels')
        if search:
            queryset = queryset.filter(name__icontains=search)
        status: Optional[str] = self.request.GET.get('status')
        if status in {'active', 'inactive'}:
            desired: int = 1 if status == 'active' else 0
            queryset = queryset.filter(profile__is_enabled=desired)
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
        context['page_title'] = _('Groups')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('Groups')},
        ]
        context['create_url'] = reverse_lazy('shared:group_create')
        context['create_button_text'] = _('Create Group')
        context['show_filters'] = True
        context['status_filter'] = False
        context['status_filter_value'] = self.request.GET.get('status', '')
        context['search_placeholder'] = _('Group name')
        context['clear_filter_url'] = reverse_lazy('shared:groups')
        context['show_actions'] = True
        context['edit_url_name'] = 'shared:group_edit'
        context['delete_url_name'] = 'shared:group_delete'
        context['empty_state_title'] = _('No Groups Found')
        context['empty_state_message'] = _('Start by creating a group and assigning access levels.')
        context['empty_state_icon'] = '👥'
        
        return context


class GroupCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new group."""
    model = Group
    form_class = GroupForm
    template_name = 'shared/group_form.html'
    success_url = reverse_lazy('shared:groups')
    feature_code = 'shared.groups'
    required_action = 'create'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Create Group')
        context['page_title'] = _('Create Group')
        context['is_create'] = True
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('Groups'), 'url': reverse_lazy('shared:groups')},
        ]
        context['cancel_url'] = reverse_lazy('shared:groups')
        return context

    def form_valid(self, form: GroupForm) -> Any:
        """Show success message after creating group."""
        response = super().form_valid(form)
        messages.success(self.request, _('Group created successfully.'))
        return response


class GroupUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing group."""
    model = Group
    form_class = GroupForm
    template_name = 'shared/group_form.html'
    success_url = reverse_lazy('shared:groups')
    feature_code = 'shared.groups'
    required_action = 'edit_own'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Edit Group')
        context['page_title'] = _('Edit Group')
        context['is_create'] = False
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('Groups'), 'url': reverse_lazy('shared:groups')},
        ]
        context['cancel_url'] = reverse_lazy('shared:groups')
        return context

    def form_valid(self, form: GroupForm) -> Any:
        """Show success message after updating group."""
        response = super().form_valid(form)
        messages.success(self.request, _('Group updated successfully.'))
        return response


class GroupDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a group."""
    model = Group
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('shared:groups')
    feature_code = 'shared.groups'
    required_action = 'delete_own'

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Delete group and show success message."""
        messages.success(self.request, _('Group deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['delete_title'] = _('Delete Group')
        context['confirmation_message'] = _('Are you sure you want to delete group "{name}"?').format(name=self.object.name)
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('Groups'), 'url': reverse_lazy('shared:groups')},
            {'label': _('Delete')},
        ]
        context['object_details'] = [
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Members'), 'value': self.object.user_set.count()},
        ]
        context['cancel_url'] = reverse_lazy('shared:groups')
        return context

