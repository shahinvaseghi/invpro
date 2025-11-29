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
    context_object_name = 'groups'
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
        """Add active module and filters to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['search_term'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
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
        context['page_title'] = _('Create Group')
        context['is_create'] = True
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
        context['page_title'] = _('Edit Group')
        context['is_create'] = False
        return context

    def form_valid(self, form: GroupForm) -> Any:
        """Show success message after updating group."""
        response = super().form_valid(form)
        messages.success(self.request, _('Group updated successfully.'))
        return response


class GroupDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a group."""
    model = Group
    template_name = 'shared/group_confirm_delete.html'
    success_url = reverse_lazy('shared:groups')
    feature_code = 'shared.groups'
    required_action = 'delete_own'

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Delete group and show success message."""
        messages.success(self.request, _('Group deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context

