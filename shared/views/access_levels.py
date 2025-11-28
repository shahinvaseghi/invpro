"""
AccessLevel CRUD views for shared module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.views.base import AccessLevelPermissionMixin, EditLockProtectedMixin
from shared.mixins import FeaturePermissionRequiredMixin
from shared.models import AccessLevel
from shared.forms import AccessLevelForm


class AccessLevelListView(FeaturePermissionRequiredMixin, ListView):
    """List all access levels."""
    model = AccessLevel
    template_name = 'shared/access_levels_list.html'
    context_object_name = 'access_levels'
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
        """Add active module and filters to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['search_term'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
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
        context['page_title'] = _('Create Access Level')
        context['is_create'] = True
        context['feature_permissions'] = self._prepare_feature_context()
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
        context['page_title'] = _('Edit Access Level')
        context['is_create'] = False
        context['feature_permissions'] = self._prepare_feature_context(self.object)
        return context

    def form_valid(self, form: AccessLevelForm) -> Any:
        """Save access level and permissions."""
        response = super().form_valid(form)
        self._save_permissions(form)
        messages.success(self.request, _('Access level updated successfully.'))
        return response


class AccessLevelDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete an access level."""
    model = AccessLevel
    template_name = 'shared/access_level_confirm_delete.html'
    success_url = reverse_lazy('shared:access_levels')
    feature_code = 'shared.access_levels'
    required_action = 'delete_own'

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Delete access level and show success message."""
        messages.success(self.request, _('Access level deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context

