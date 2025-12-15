"""
GL Account (حساب کل) CRUD views for accounting module.
"""
from typing import Any, Dict
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from typing import Optional
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
from accounting.forms import GLAccountForm
from accounting.views.base import AccountingBaseView


class GLAccountListView(BaseListView):
    """
    List all GL accounts (حساب کل) for the active company.
    """
    model = Account
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.gl'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['account_code']
    default_status_filter = True
    
    def get_base_queryset(self):
        """Get base queryset filtered by company and account_level=1."""
        queryset = Account.objects.filter(account_level=1)
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        return queryset
    
    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ['account_code', 'account_name', 'account_name_en']
    
    def get_queryset(self):
        """Filter GL accounts by active company and search/filter criteria."""
        queryset = super().get_queryset()
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('تعریف حساب کل')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('تعریف حساب کل'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:gl_account_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('افزودن حساب کل')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:gl_account_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:gl_account_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:gl_account_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('هیچ حساب کلی یافت نشد')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('با افزودن اولین حساب کل شروع کنید.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📊'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('کد کل'), 'field': 'account_code', 'type': 'code'},
            {'label': _('نام کل'), 'field': 'account_name'},
            {'label': _('مانده جاری'), 'field': 'current_balance'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        context['print_enabled'] = True
        return context


class GLAccountCreateView(BaseCreateView):
    """Create a new GL account (حساب کل)."""
    model = Account
    form_class = GLAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:gl_accounts')
    feature_code = 'accounting.accounts.gl'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('حساب کل با موفقیت ایجاد شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: GLAccountForm) -> HttpResponseRedirect:
        """Set created_by and account_level."""
        form.instance.created_by = self.request.user
        form.instance.account_level = 1  # GL account level
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('تعریف حساب کل'), 'url': reverse('accounting:gl_accounts')},
            {'label': _('افزودن'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:gl_accounts')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('افزودن حساب کل')


class GLAccountUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing GL account (حساب کل)."""
    model = Account
    form_class = GLAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:gl_accounts')
    feature_code = 'accounting.accounts.gl'
    required_action = 'edit_own'
    active_module = 'accounting'
    success_message = _('حساب کل با موفقیت به‌روزرسانی شد.')
    
    def get_queryset(self):
        """Only allow editing GL accounts (level 1)."""
        return super().get_queryset().filter(account_level=1)
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: GLAccountForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('تعریف حساب کل'), 'url': reverse('accounting:gl_accounts')},
            {'label': _('ویرایش'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:gl_accounts')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('ویرایش حساب کل')


class GLAccountDetailView(BaseDetailView):
    """Detail view for viewing GL accounts (read-only)."""
    model = Account
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'accounting.accounts.gl'
    required_action = 'view_own'
    active_module = 'accounting'
    
    def get_queryset(self):
        """Filter GL accounts (level 1) by active company."""
        queryset = Account.objects.filter(account_level=1)
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        queryset = queryset.select_related(
            'created_by',
            'edited_by',
        ).prefetch_related('child_accounts')
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View GL Account')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        account = self.object
        
        context['detail_title'] = self.get_page_title()
        info_banner = [
            {'label': _('Account Code'), 'value': account.account_code, 'type': 'code'},
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
                f"<code>{child.account_code}</code> - {child.account_name}"
                for child in account.child_accounts.all()
            ])
            detail_sections.append({
                'title': _('Child Accounts') + ' (' + _('Sub Accounts') + ')',
                'type': 'custom',
                'content': f'<div class="readonly-field">{child_accounts_text}</div>',
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('accounting:gl_accounts')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('accounting:gl_account_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class GLAccountDeleteView(BaseDeleteView):
    """Delete a GL account (حساب کل)."""
    model = Account
    success_url = reverse_lazy('accounting:gl_accounts')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.gl'
    required_action = 'delete_own'
    active_module = 'accounting'
    success_message = _('حساب کل با موفقیت حذف شد.')
    
    def get_queryset(self):
        """Only allow deleting GL accounts (level 1)."""
        return super().get_queryset().filter(account_level=1)
    
    def validate_deletion(self) -> tuple[bool, Optional[str]]:
        """Validate if account can be deleted."""
        obj = self.get_object()
        # Check if account is system account
        if obj.is_system_account:
            return False, _('حساب‌های سیستمی قابل حذف نیستند.')
        
        # Check if account has child accounts (معین)
        if obj.child_accounts.exists():
            return False, _('نمی‌توان حساب کلی که دارای حساب معین است را حذف کرد.')
        
        return True, None
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('حذف حساب کل')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('آیا مطمئن هستید که می‌خواهید این حساب کل را حذف کنید؟')
    
    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        return [
            {'label': _('کد کل'), 'value': self.object.account_code, 'type': 'code'},
            {'label': _('نام کل'), 'value': self.object.account_name},
        ]
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('تعریف حساب کل'), 'url': reverse('accounting:gl_accounts')},
            {'label': _('حذف'), 'url': None},
        ]

