"""
Account (Chart of Accounts) CRUD views for accounting module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDetailView,
    BaseDeleteView,
    EditLockProtectedMixin,
)
from accounting.models import Account
from accounting.forms import AccountForm
from accounting.views.base import AccountingBaseView


class AccountListView(BaseListView):
    """
    List all accounts for the active company.
    """
    model = Account
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['account_code']
    default_status_filter = True
    
    def get_base_queryset(self):
        """Get base queryset filtered by company."""
        queryset = super().get_base_queryset()
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        return queryset
    
    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ['account_code', 'account_name', 'account_name_en']
    
    def get_queryset(self):
        """Filter accounts by active company and search/filter criteria."""
        queryset = super().get_queryset()
        
        account_type: str = self.request.GET.get('account_type', '')
        account_level: str = self.request.GET.get('account_level', '')
        
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        
        if account_level:
            queryset = queryset.filter(account_level=int(account_level))
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Chart of Accounts')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Chart of Accounts'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:account_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Account')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:account_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:account_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:account_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Accounts Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by adding your first account.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📊'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
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
        context['print_enabled'] = True
        return context


class AccountCreateView(BaseCreateView):
    """Create a new account."""
    model = Account
    form_class = AccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:accounts')
    feature_code = 'accounting.accounts'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('Account created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: AccountForm) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Chart of Accounts'), 'url': reverse('accounting:accounts')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:accounts')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Account')


class AccountUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing account."""
    model = Account
    form_class = AccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:accounts')
    feature_code = 'accounting.accounts'
    required_action = 'edit_own'
    active_module = 'accounting'
    success_message = _('Account updated successfully.')
    
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
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Chart of Accounts'), 'url': reverse('accounting:accounts')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:accounts')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Account')


class AccountDetailView(BaseDetailView):
    """Detail view for viewing accounts (read-only)."""
    model = Account
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'accounting.accounts'
    required_action = 'view_own'
    active_module = 'accounting'
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        queryset = queryset.select_related(
            'parent_account',
            'created_by',
            'edited_by',
        ).prefetch_related('child_accounts')
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Account')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        account = self.object
        
        context['detail_title'] = self.get_page_title()
        info_banner = [
            {'label': _('Account Code'), 'value': account.account_code, 'type': 'code'},
            {'label': _('Account Level'), 'value': str(account.account_level)},
            {'label': _('Status'), 'value': account.is_enabled, 'type': 'badge'},
        ]
        if account.current_balance:
            info_banner.append({
                'label': _('Current Balance'),
                'value': f"{account.current_balance:.2f}",
            })
        context['info_banner'] = info_banner
        
        # Basic Information section
        basic_fields = [
            {'label': _('Account Name'), 'value': account.account_name},
        ]
        if account.account_name_en:
            basic_fields.append({'label': _('Account Name (EN)'), 'value': account.account_name_en})
        basic_fields.append({
            'label': _('Account Type'),
            'value': account.get_account_type_display() or account.account_type,
        })
        basic_fields.append({
            'label': _('Normal Balance'),
            'value': account.get_normal_balance_display() or account.normal_balance,
        })
        if account.parent_account:
            basic_fields.append({
                'label': _('Parent Account'),
                'value': f"{account.parent_account.account_code} - {account.parent_account.account_name}",
            })
        if account.description:
            basic_fields.append({'label': _('Description'), 'value': account.description})
        
        detail_sections = [
            {
                'title': _('Basic Information'),
                'fields': basic_fields,
            },
        ]
        
        # Child Accounts section
        if account.child_accounts.exists():
            child_accounts_text = '<br>'.join([
                f"<code>{child.account_code}</code> - {child.account_name} ({_('Level')} {child.account_level})"
                for child in account.child_accounts.all()
            ])
            detail_sections.append({
                'title': _('Child Accounts'),
                'type': 'custom',
                'content': f'<div class="readonly-field">{child_accounts_text}</div>',
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('accounting:accounts')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('accounting:account_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class AccountDeleteView(BaseDeleteView):
    """Delete an account."""
    model = Account
    success_url = reverse_lazy('accounting:accounts')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts'
    required_action = 'delete_own'
    active_module = 'accounting'
    success_message = _('Account deleted successfully.')
    
    def validate_deletion(self) -> tuple[bool, Optional[str]]:
        """Validate if account can be deleted."""
        obj = self.get_object()
        # Check if account is system account
        if obj.is_system_account:
            return False, _('System accounts cannot be deleted.')
        
        # Check if account has child accounts
        if obj.child_accounts.exists():
            return False, _('Cannot delete account with child accounts.')
        
        return True, None
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Account')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this account?')
    
    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        return [
            {'label': _('Code'), 'value': self.object.account_code, 'type': 'code'},
            {'label': _('Name'), 'value': self.object.account_name},
            {'label': _('Type'), 'value': self.object.get_account_type_display()},
            {'label': _('Level'), 'value': self.object.get_account_level_display()},
        ]
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Chart of Accounts'), 'url': reverse('accounting:accounts')},
            {'label': _('Delete'), 'url': None},
        ]

