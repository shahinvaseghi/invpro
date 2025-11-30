"""
User CRUD views for shared module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
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
    context_object_name = 'object_list'
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
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        
        # Ensure object_list is properly set from page_obj if pagination is used
        if 'page_obj' in context and hasattr(context['page_obj'], 'object_list'):
            context['object_list'] = context['page_obj'].object_list
        elif 'object_list' in context and hasattr(context['object_list'], 'query'):
            # If object_list is a queryset, evaluate it to ensure it's accessible in template
            context['object_list'] = list(context['object_list'])
        
        context['active_module'] = 'shared'
        context['page_title'] = _('Users')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Users')},
        ]
        context['create_url'] = reverse('shared:user_create')
        context['create_button_text'] = _('Create User')
        context['show_filters'] = True
        context['status_filter'] = False  # We override filter_fields block instead
        context['status_filter_value'] = self.request.GET.get('status', '')
        context['search_placeholder'] = _('Username, email or name')
        context['clear_filter_url'] = reverse('shared:users')
        context['show_actions'] = True
        context['edit_url_name'] = 'shared:user_edit'
        context['delete_url_name'] = 'shared:user_delete'
        
        # Table headers are not used since we override table_rows block
        context['table_headers'] = [
            {'label': _('Username')},
            {'label': _('Name')},
            {'label': _('Email')},
            {'label': _('Default Company')},
            {'label': _('Groups')},
            {'label': _('Company Access')},
            {'label': _('Status')},
        ]
        context['empty_state_title'] = _('No Users Found')
        context['empty_state_message'] = _('Start by adding your first user to the system.')
        context['empty_state_icon'] = '👤'
        
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
        context['form_title'] = _('Create User')
        context['page_title'] = _('Create User')
        context['is_create'] = True
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Users'), 'url': reverse('shared:users')},
        ]
        context['cancel_url'] = reverse('shared:users')
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
        context['form_title'] = _('Edit User')
        context['page_title'] = _('Edit User')
        context['is_create'] = False
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Users'), 'url': reverse('shared:users')},
        ]
        context['cancel_url'] = reverse('shared:users')
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
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('shared:users')
    feature_code = 'shared.users'
    required_action = 'delete_own'

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete user and show success message."""
        messages.success(self.request, _('User deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['delete_title'] = _('Delete User')
        context['confirmation_message'] = _('Do you really want to delete user "{username}"?').format(username=self.object.username)
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Users'), 'url': reverse('shared:users')},
            {'label': _('Delete')},
        ]
        context['object_details'] = [
            {'label': _('Username'), 'value': self.object.username},
            {'label': _('Email'), 'value': self.object.email or '-'},
            {'label': _('Name'), 'value': self.object.get_full_name() or '-'},
        ]
        context['cancel_url'] = reverse('shared:users')
        return context

