"""
Sub Account (حساب معین) CRUD views for accounting module.
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
from accounting.forms import SubAccountForm
from accounting.views.base import AccountingBaseView


class SubAccountListView(BaseListView):
    """
    List all Sub accounts (حساب معین) for the active company.
    """
    model = Account
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.sub'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['account_code']
    default_status_filter = True
    
    def get_base_queryset(self):
        """Get base queryset filtered by company and account_level=2."""
        queryset = Account.objects.filter(account_level=2)
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        return queryset
    
    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ['account_code', 'account_name', 'account_name_en']
    
    def get_queryset(self):
        """Filter Sub accounts by active company and search/filter criteria."""
        queryset = super().get_queryset()
        
        parent_id: str = self.request.GET.get('parent_id', '')
        
        if parent_id:
            try:
                # Filter by GL account relation
                from accounting.models import SubAccountGLAccountRelation
                queryset = queryset.filter(
                    gl_account_relations__gl_account_id=int(parent_id),
                    gl_account_relations__company_id=self.request.session.get('active_company_id')
                ).distinct()
            except ValueError:
                pass
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('تعریف حساب معین')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_subsidiary')},
            {'label': _('تعریف حساب معین'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:sub_account_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('افزودن حساب معین')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:sub_account_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:sub_account_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:sub_account_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('هیچ حساب معینی یافت نشد')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('با افزودن اولین حساب معین شروع کنید.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📊'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('کد معین'), 'field': 'account_code', 'type': 'code'},
            {'label': _('نام معین'), 'field': 'account_name'},
            {'label': _('حساب‌های کل مرتبط'), 'field': 'gl_accounts_display', 'type': 'custom'},
            {'label': _('طرف تراز'), 'field': 'normal_balance'},
            {'label': _('مانده جاری'), 'field': 'current_balance'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        
        # Add GL accounts info to each object for display
        from accounting.models import SubAccountGLAccountRelation
        company_id = self.request.session.get('active_company_id')
        if company_id:
            for obj in context['object_list']:
                gl_accounts = Account.objects.filter(
                    sub_account_relations_as_gl__sub_account=obj,
                    sub_account_relations_as_gl__company_id=company_id
                ).order_by('account_code')
                obj.gl_accounts_display = ', '.join([f"{ga.account_code} ({ga.account_name})" for ga in gl_accounts[:3]])
                if gl_accounts.count() > 3:
                    obj.gl_accounts_display += f" +{gl_accounts.count() - 3} بیشتر"
        
        # Add GL accounts for filter dropdown
        if company_id:
            context['gl_accounts'] = Account.objects.filter(
                company_id=company_id,
                account_level=1,
                is_enabled=1
            ).order_by('account_code')
        context['print_enabled'] = True
        
        return context


class SubAccountCreateView(BaseCreateView):
    """Create a new Sub account (حساب معین)."""
    model = Account
    form_class = SubAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:sub_accounts')
    feature_code = 'accounting.accounts.sub'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('حساب معین با موفقیت ایجاد شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: SubAccountForm) -> HttpResponseRedirect:
        """Set created_by and account_level."""
        form.instance.created_by = self.request.user
        form.instance.account_level = 2  # Sub account level
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_subsidiary')},
            {'label': _('تعریف حساب معین'), 'url': reverse('accounting:sub_accounts')},
            {'label': _('افزودن'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:sub_accounts')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('افزودن حساب معین')


class SubAccountUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing Sub account (حساب معین)."""
    model = Account
    form_class = SubAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:sub_accounts')
    feature_code = 'accounting.accounts.sub'
    required_action = 'edit_own'
    active_module = 'accounting'
    success_message = _('حساب معین با موفقیت به‌روزرسانی شد.')
    
    def get_queryset(self):
        """Only allow editing Sub accounts (level 2)."""
        return super().get_queryset().filter(account_level=2)
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        # Exclude current instance from parent account choices
        if self.object:
            kwargs['exclude_account_id'] = self.object.id
        return kwargs
    
    def form_valid(self, form: SubAccountForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_subsidiary')},
            {'label': _('تعریف حساب معین'), 'url': reverse('accounting:sub_accounts')},
            {'label': _('ویرایش'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:sub_accounts')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('ویرایش حساب معین')


class SubAccountDetailView(BaseDetailView):
    """Detail view for viewing Sub accounts (read-only)."""
    model = Account
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'accounting.accounts.sub'
    required_action = 'view_own'
    active_module = 'accounting'
    
    def get_queryset(self):
        """Filter Sub accounts (level 2) by active company."""
        queryset = Account.objects.filter(account_level=2)
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        queryset = queryset.select_related(
            'parent_account',
            'created_by',
            'edited_by',
        ).prefetch_related(
            'gl_account_relations__gl_account',
            'child_accounts',
        )
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Sub Account')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
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
        if account.parent_account:
            basic_fields.append({
                'label': _('Parent Account'),
                'value': f"{account.parent_account.account_code} - {account.parent_account.account_name}",
            })
        basic_fields.append({
            'label': _('Normal Balance'),
            'value': account.get_normal_balance_display() or account.normal_balance,
        })
        if account.description:
            basic_fields.append({'label': _('Description'), 'value': account.description})
        
        detail_sections = [
            {
                'title': _('Basic Information'),
                'fields': basic_fields,
            },
        ]
        
        # Get related GL accounts
        from accounting.models import SubAccountGLAccountRelation
        company_id = self.request.session.get('active_company_id')
        related_gl_accounts = []
        if company_id:
            relations = SubAccountGLAccountRelation.objects.filter(
                sub_account=account,
                company_id=company_id
            ).select_related('gl_account')
            related_gl_accounts = [rel.gl_account for rel in relations]
        
        # Related GL Accounts section
        if related_gl_accounts:
            gl_accounts_text = '<br>'.join([
                f"<code>{gl.account_code}</code> - {gl.account_name}"
                for gl in related_gl_accounts
            ])
            detail_sections.append({
                'title': _('Related GL Accounts'),
                'type': 'custom',
                'content': f'<div class="readonly-field">{gl_accounts_text}</div>',
            })
        
        # Child Accounts section
        if account.child_accounts.exists():
            child_accounts_text = '<br>'.join([
                f"<code>{child.account_code}</code> - {child.account_name}"
                for child in account.child_accounts.all()
            ])
            detail_sections.append({
                'title': _('Child Accounts') + ' (' + _('Tafsili Accounts') + ')',
                'type': 'custom',
                'content': f'<div class="readonly-field">{child_accounts_text}</div>',
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('accounting:sub_accounts')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('accounting:sub_account_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class SubAccountDeleteView(BaseDeleteView):
    """Delete a Sub account (حساب معین)."""
    model = Account
    success_url = reverse_lazy('accounting:sub_accounts')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.sub'
    required_action = 'delete_own'
    active_module = 'accounting'
    success_message = _('حساب معین با موفقیت حذف شد.')
    
    def get_queryset(self):
        """Only allow deleting Sub accounts (level 2)."""
        return super().get_queryset().filter(account_level=2)
    
    def validate_deletion(self) -> tuple[bool, Optional[str]]:
        """Validate if account can be deleted."""
        obj = self.get_object()
        # Check if account is system account
        if obj.is_system_account:
            return False, _('حساب‌های سیستمی قابل حذف نیستند.')
        
        # Check if account has child accounts (تفصیلی)
        if obj.child_accounts.exists():
            return False, _('نمی‌توان حساب معینی که دارای حساب تفصیلی است را حذف کرد.')
        
        return True, None
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('حذف حساب معین')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('آیا مطمئن هستید که می‌خواهید این حساب معین را حذف کنید؟')
    
    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        return [
            {'label': _('کد معین'), 'value': self.object.account_code, 'type': 'code'},
            {'label': _('نام معین'), 'value': self.object.account_name},
            {'label': _('حساب کل والد'), 'value': self.object.parent_account.account_code if self.object.parent_account else '-', 'type': 'code'},
        ]
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_subsidiary')},
            {'label': _('تعریف حساب معین'), 'url': reverse('accounting:sub_accounts')},
            {'label': _('حذف'), 'url': None},
        ]

