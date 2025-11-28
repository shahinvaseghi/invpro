"""
User CRUD views for shared module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.views.base import UserAccessFormsetMixin, EditLockProtectedMixin
from shared.mixins import FeaturePermissionRequiredMixin
from shared.forms import UserCreateForm, UserUpdateForm

User = get_user_model()


class UserListView(FeaturePermissionRequiredMixin, ListView):
    """List all users."""
    model = User
    template_name = 'shared/users_list.html'
    context_object_name = 'users'
    paginate_by = 20
    feature_code = 'shared.users'

    def get_queryset(self):
        """Filter users by search and status."""
        queryset = (
            User.objects.all()
            .order_by('username')
            .prefetch_related('groups', 'company_accesses__company', 'company_accesses__access_level')
        )
        search: Optional[str] = self.request.GET.get('search')
        status: Optional[str] = self.request.GET.get('status')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        if status in {'active', 'inactive'}:
            queryset = queryset.filter(is_active=(status == 'active'))
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and filters to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['search_term'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        return context


class UserCreateView(FeaturePermissionRequiredMixin, UserAccessFormsetMixin, CreateView):
    """Create a new user."""
    model = User
    form_class = UserCreateForm
    template_name = 'shared/user_form.html'
    success_url = reverse_lazy('shared:users')
    feature_code = 'shared.users'
    required_action = 'create'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add access formset and active module to context."""
        context = super().get_context_data(**kwargs)
        context.setdefault('access_formset', self.get_access_formset(context.get('form')))
        context['active_module'] = 'shared'
        context['page_title'] = _('Create User')
        context['is_create'] = True
        return context

    def form_valid(self, form: UserCreateForm) -> HttpResponseRedirect:
        """Save user and company access formset."""
        access_formset = self.get_access_formset(form)
        if not access_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, access_formset=access_formset))

        with transaction.atomic():
            # Save the core user fields (including role toggles & groups)
            self.object = form.save()
            # Persist company access rows
            access_formset.instance = self.object
            access_formset.save()
        messages.success(self.request, _('User created successfully.'))
        return HttpResponseRedirect(self.get_success_url())


class UserUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UserAccessFormsetMixin, UpdateView):
    """Update an existing user."""
    model = User
    form_class = UserUpdateForm
    template_name = 'shared/user_form.html'
    success_url = reverse_lazy('shared:users')
    feature_code = 'shared.users'
    required_action = 'edit_own'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add access formset and active module to context."""
        context = super().get_context_data(**kwargs)
        context.setdefault('access_formset', self.get_access_formset(context.get('form')))
        context['active_module'] = 'shared'
        context['page_title'] = _('Edit User')
        context['is_create'] = False
        return context

    def form_valid(self, form: UserUpdateForm) -> HttpResponseRedirect:
        """Save user and company access formset."""
        access_formset = self.get_access_formset(form)
        if not access_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, access_formset=access_formset))

        with transaction.atomic():
            # Persist user core data before saving company access rows
            self.object = form.save()
            access_formset.instance = self.object
            access_formset.save()
        messages.success(self.request, _('User updated successfully.'))
        return HttpResponseRedirect(self.get_success_url())


class UserDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a user."""
    model = User
    template_name = 'shared/user_confirm_delete.html'
    success_url = reverse_lazy('shared:users')
    feature_code = 'shared.users'
    required_action = 'delete_own'

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete user and show success message."""
        messages.success(self.request, _('User deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context

