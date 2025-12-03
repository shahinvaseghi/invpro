"""
Account (Chart of Accounts) CRUD views for accounting module.
"""
from typing import Any, Dict
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from accounting.models import Account
from accounting.forms import AccountForm
from accounting.views.base import AccountingBaseView


class AccountListView(FeaturePermissionRequiredMixin, AccountingBaseView, ListView):
    """
    List all accounts for the active company.
    """
    model = Account
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts'
    
    def get_queryset(self):
        """Filter accounts by active company and search/filter criteria."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
        
        search: str = self.request.GET.get('search', '').strip()
        status: str = self.request.GET.get('status', '')
        account_type: str = self.request.GET.get('account_type', '')
        account_level: str = self.request.GET.get('account_level', '')
        
        if search:
            queryset = queryset.filter(
                Q(account_code__icontains=search) |
                Q(account_name__icontains=search) |
                Q(account_name_en__icontains=search)
            )
        
        if status in ('0', '1'):
            queryset = queryset.filter(is_enabled=int(status))
        else:
            # Default: show only enabled accounts
            queryset = queryset.filter(is_enabled=1)
        
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        
        if account_level:
            queryset = queryset.filter(account_level=int(account_level))
        
        return queryset.order_by('account_code')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Chart of Accounts')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Chart of Accounts')},
        ]
        context['create_url'] = reverse('accounting:account_create')
        context['create_button_text'] = _('Create Account')
        context['show_filters'] = True
        context['status_filter'] = True
        context['search_placeholder'] = _('Search by code or name')
        context['clear_filter_url'] = reverse('accounting:accounts')
        context['print_enabled'] = True
        context['show_actions'] = True
        context['feature_code'] = 'accounting.accounts'
        context['detail_url_name'] = 'accounting:account_detail'
        context['edit_url_name'] = 'accounting:account_edit'
        context['delete_url_name'] = 'accounting:account_delete'
        context['table_headers'] = [
            {'label': _('CODE'), 'field': 'account_code', 'type': 'code'},
            {'label': _('Account Name'), 'field': 'account_name'},
            {'label': _('Type'), 'field': 'account_type'},
            {'label': _('Level'), 'field': 'account_level'},
            {'label': _('Parent'), 'field': 'parent_account.account_code'},
            {'label': _('Normal Balance'), 'field': 'normal_balance'},
            {'label': _('Current Balance'), 'field': 'current_balance'},
            {'label': _('Status'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('Active'), 'false_label': _('Inactive')},
        ]
        context['empty_state_title'] = _('No Accounts Found')
        context['empty_state_message'] = _('Start by adding your first account.')
        context['empty_state_icon'] = '📊'
        return context


class AccountCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create a new account."""
    model = Account
    form_class = AccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:accounts')
    feature_code = 'accounting.accounts'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: AccountForm) -> HttpResponseRedirect:
        """Set created_by and show success message."""
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Account created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Account')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Chart of Accounts'), 'url': reverse('accounting:accounts')},
        ]
        context['cancel_url'] = reverse('accounting:accounts')
        return context


class AccountUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, AccountingBaseView, UpdateView):
    """Update an existing account."""
    model = Account
    form_class = AccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:accounts')
    feature_code = 'accounting.accounts'
    required_action = 'edit_own'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        # Exclude current instance from parent account choices
        if self.object:
            kwargs['exclude_account_id'] = self.object.id
        return kwargs
    
    def form_valid(self, form: AccountForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Account updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Account')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Chart of Accounts'), 'url': reverse('accounting:accounts')},
        ]
        context['cancel_url'] = reverse('accounting:accounts')
        return context


class AccountDetailView(FeaturePermissionRequiredMixin, AccountingBaseView, DetailView):
    """Detail view for viewing accounts (read-only)."""
    model = Account
    template_name = 'accounting/account_detail.html'
    context_object_name = 'account'
    feature_code = 'accounting.accounts'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter by active company."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
        queryset = queryset.select_related(
            'parent_account',
            'created_by',
            'edited_by',
        ).prefetch_related('child_accounts')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('View Account')
        context['list_url'] = reverse_lazy('accounting:accounts')
        context['edit_url'] = reverse_lazy('accounting:account_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        context['feature_code'] = 'accounting.accounts'
        return context


class AccountDeleteView(FeaturePermissionRequiredMixin, AccountingBaseView, DeleteView):
    """Delete an account."""
    model = Account
    success_url = reverse_lazy('accounting:accounts')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts'
    required_action = 'delete_own'
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete account and show success message."""
        obj = self.get_object()
        # Check if account is system account
        if obj.is_system_account:
            messages.error(self.request, _('System accounts cannot be deleted.'))
            return HttpResponseRedirect(self.success_url)
        
        # Check if account has child accounts
        if obj.child_accounts.exists():
            messages.error(self.request, _('Cannot delete account with child accounts.'))
            return HttpResponseRedirect(self.success_url)
        
        messages.success(self.request, _('Account deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Account')
        context['confirmation_message'] = _('Do you really want to delete this account?')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Chart of Accounts'), 'url': reverse('accounting:accounts')},
            {'label': _('Delete')},
        ]
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.account_code, 'type': 'code'},
            {'label': _('Name'), 'value': self.object.account_name},
            {'label': _('Type'), 'value': self.object.get_account_type_display()},
            {'label': _('Level'), 'value': self.object.get_account_level_display()},
        ]
        context['cancel_url'] = reverse('accounting:accounts')
        return context

