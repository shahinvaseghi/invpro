"""
AccountGroup (گروه حساب‌ها) CRUD views for accounting module.
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
from accounting.models import AccountGroup, Account
from accounting.forms import AccountGroupForm
from accounting.views.base import AccountingBaseView


class AccountGroupListView(BaseListView):
    """
    List all account groups (گروه حساب‌ها) for the active company.
    """
    model = AccountGroup
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.groups'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['group_code']
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
        return ['group_code', 'group_name', 'group_name_en']
    
    def get_queryset(self):
        """Filter account groups by active company and search/filter criteria."""
        queryset = super().get_queryset()
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('گروه حساب‌ها')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('گروه حساب‌ها'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:account_group_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('افزودن گروه حساب')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:account_group_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:account_group_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:account_group_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('هیچ گروه حسابی یافت نشد')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('با افزودن اولین گروه حساب شروع کنید.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📊'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('کد گروه'), 'field': 'group_code', 'type': 'code'},
            {'label': _('نام گروه'), 'field': 'group_name'},
            {'label': _('تعداد حساب‌های کل'), 'field': 'accounts_count', 'type': 'custom'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        context['print_enabled'] = True
        
        # Add accounts count for each group
        for obj in context['object_list']:
            obj.accounts_count = Account.objects.filter(
                account_group=obj,
                account_level=1,
                is_enabled=1
            ).count()
        
        return context


class AccountGroupCreateView(BaseCreateView):
    """Create a new account group (گروه حساب)."""
    model = AccountGroup
    form_class = AccountGroupForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:account_groups')
    feature_code = 'accounting.accounts.groups'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('گروه حساب با موفقیت ایجاد شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: AccountGroupForm) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('گروه حساب‌ها'), 'url': reverse('accounting:account_groups')},
            {'label': _('افزودن'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:account_groups')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('افزودن گروه حساب')


class AccountGroupUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing account group (گروه حساب)."""
    model = AccountGroup
    form_class = AccountGroupForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:account_groups')
    feature_code = 'accounting.accounts.groups'
    required_action = 'edit_own'
    active_module = 'accounting'
    success_message = _('گروه حساب با موفقیت به‌روزرسانی شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: AccountGroupForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('گروه حساب‌ها'), 'url': reverse('accounting:account_groups')},
            {'label': _('ویرایش'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:account_groups')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('ویرایش گروه حساب')


class AccountGroupDetailView(BaseDetailView):
    """Detail view for viewing account groups (read-only)."""
    model = AccountGroup
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'accounting.accounts.groups'
    required_action = 'view_own'
    active_module = 'accounting'
    
    def get_queryset(self):
        """Filter account groups by active company."""
        queryset = super().get_queryset()
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        queryset = queryset.select_related(
            'created_by',
            'edited_by',
        ).prefetch_related('accounts')
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('مشاهده گروه حساب')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        account_group = self.object
        
        context['detail_title'] = self.get_page_title()
        info_banner = [
            {'label': _('کد گروه'), 'value': account_group.group_code, 'type': 'code'},
            {'label': _('وضعیت'), 'value': account_group.is_enabled, 'type': 'badge'},
        ]
        context['info_banner'] = info_banner
        
        # Basic Information section
        basic_fields = [
            {'label': _('نام گروه'), 'value': account_group.group_name},
        ]
        if account_group.group_name_en:
            basic_fields.append({'label': _('نام گروه (انگلیسی)'), 'value': account_group.group_name_en})
        if account_group.description:
            basic_fields.append({'label': _('توضیحات'), 'value': account_group.description})
        
        detail_sections = [
            {
                'title': _('اطلاعات پایه'),
                'fields': basic_fields,
            },
        ]
        
        # GL Accounts section
        gl_accounts = Account.objects.filter(
            account_group=account_group,
            account_level=1,
            is_enabled=1
        ).order_by('account_code')
        
        if gl_accounts.exists():
            gl_accounts_text = '<br>'.join([
                f"<code>{account.account_code}</code> - {account.account_name}"
                for account in gl_accounts
            ])
            detail_sections.append({
                'title': _('حساب‌های کل') + f' ({gl_accounts.count()})',
                'type': 'custom',
                'content': f'<div class="readonly-field">{gl_accounts_text}</div>',
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('accounting:account_groups')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('accounting:account_group_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class AccountGroupDeleteView(BaseDeleteView):
    """Delete an account group (گروه حساب)."""
    model = AccountGroup
    success_url = reverse_lazy('accounting:account_groups')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.groups'
    required_action = 'delete_own'
    active_module = 'accounting'
    success_message = _('گروه حساب با موفقیت حذف شد.')
    
    def validate_deletion(self) -> tuple[bool, Optional[str]]:
        """Validate if account group can be deleted."""
        obj = self.get_object()
        
        # Check if account group has GL accounts
        gl_accounts_count = Account.objects.filter(
            account_group=obj,
            account_level=1
        ).count()
        
        if gl_accounts_count > 0:
            return False, _('نمی‌توان گروه حسابی که دارای حساب کل است را حذف کرد.')
        
        return True, None
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('حذف گروه حساب')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('آیا مطمئن هستید که می‌خواهید این گروه حساب را حذف کنید؟')
    
    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        return [
            {'label': _('کد گروه'), 'value': self.object.group_code, 'type': 'code'},
            {'label': _('نام گروه'), 'value': self.object.group_name},
        ]
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('گروه حساب‌ها'), 'url': reverse('accounting:account_groups')},
            {'label': _('حذف'), 'url': None},
        ]

