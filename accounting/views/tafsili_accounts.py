"""
Tafsili Account (حساب تفصیلی) CRUD views for accounting module.
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
from accounting.forms import TafsiliAccountForm
from accounting.views.base import AccountingBaseView


class TafsiliAccountListView(BaseListView):
    """
    List all Tafsili accounts (حساب تفصیلی) for the active company.
    """
    model = Account
    template_name = 'accounting/tafsili_accounts.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['account_code']
    default_status_filter = True
    
    def get_base_queryset(self):
        """Get base queryset filtered by company and account_level=3."""
        queryset = Account.objects.filter(account_level=3)
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        return queryset
    
    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ['account_code', 'account_name', 'account_name_en']
    
    def get_queryset(self):
        """Filter Tafsili accounts by active company and search/filter criteria."""
        queryset = super().get_queryset()
        
        parent_id: str = self.request.GET.get('parent_id', '')
        
        if parent_id:
            try:
                # Filter by sub account relation
                from accounting.models import TafsiliSubAccountRelation
                queryset = queryset.filter(
                    sub_account_relations_as_tafsili__sub_account_id=int(parent_id),
                    sub_account_relations_as_tafsili__company_id=self.request.session.get('active_company_id')
                ).distinct()
            except ValueError:
                pass
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('تعریف حساب تفصیلی')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:tafsili_account_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('افزودن حساب تفصیلی')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:tafsili_account_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:tafsili_account_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:tafsili_account_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('هیچ حساب تفصیلی یافت نشد')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('با افزودن اولین حساب تفصیلی شروع کنید.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📊'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('کد تفصیلی'), 'field': 'account_code', 'type': 'code'},
            {'label': _('نام تفصیلی'), 'field': 'account_name'},
            {'label': _('حساب‌های معین مرتبط'), 'field': 'sub_accounts_display', 'type': 'custom'},
            {'label': _('مانده جاری'), 'field': 'current_balance'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        
        # Add sub accounts info to each object for display
        from accounting.models import TafsiliSubAccountRelation
        company_id = self.request.session.get('active_company_id')
        if company_id:
            for obj in context['object_list']:
                relations = TafsiliSubAccountRelation.objects.filter(
                    tafsili_account=obj,
                    company_id=company_id
                ).select_related('sub_account')
                sub_accounts = [rel.sub_account for rel in relations]
                obj.sub_accounts_display = ', '.join([f"{sa.account_code} ({sa.account_name})" for sa in sub_accounts[:3]])
                if len(sub_accounts) > 3:
                    obj.sub_accounts_display += f" +{len(sub_accounts) - 3} بیشتر"
        
        # Add Sub accounts for filter dropdown
        if company_id:
            context['sub_accounts'] = Account.objects.filter(
                company_id=company_id,
                account_level=2,
                is_enabled=1
            ).order_by('account_code')
        context['print_enabled'] = True
        
        return context


class TafsiliAccountCreateView(BaseCreateView):
    """Create a new Tafsili account (حساب تفصیلی)."""
    model = Account
    form_class = TafsiliAccountForm
    template_name = 'accounting/tafsili_account_form.html'
    success_url = reverse_lazy('accounting:tafsili_accounts')
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('حساب تفصیلی با موفقیت ایجاد شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: TafsiliAccountForm) -> HttpResponseRedirect:
        """Set created_by and account_level."""
        form.instance.created_by = self.request.user
        form.instance.account_level = 3  # Tafsili account level
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('افزودن'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:tafsili_accounts')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('افزودن حساب تفصیلی')


class TafsiliAccountUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing Tafsili account (حساب تفصیلی)."""
    model = Account
    form_class = TafsiliAccountForm
    template_name = 'accounting/tafsili_account_form.html'
    success_url = reverse_lazy('accounting:tafsili_accounts')
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'edit_own'
    active_module = 'accounting'
    success_message = _('حساب تفصیلی با موفقیت به‌روزرسانی شد.')
    
    def get_queryset(self):
        """Only allow editing Tafsili accounts (level 3)."""
        return super().get_queryset().filter(account_level=3)
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        # Exclude current instance from parent account choices
        if self.object:
            kwargs['exclude_account_id'] = self.object.id
        return kwargs
    
    def form_valid(self, form: TafsiliAccountForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('ویرایش'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:tafsili_accounts')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('ویرایش حساب تفصیلی')


class TafsiliAccountDetailView(BaseDetailView):
    """Detail view for viewing Tafsili accounts (read-only)."""
    model = Account
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'view_own'
    active_module = 'accounting'
    
    def get_queryset(self):
        """Filter Tafsili accounts (level 3) by active company."""
        queryset = Account.objects.filter(account_level=3)
        # Use AccountingBaseView's permission filtering
        base_view = AccountingBaseView()
        base_view.request = self.request
        queryset = base_view.filter_queryset_by_permissions(queryset, self.feature_code)
        queryset = queryset.select_related(
            'parent_account',
            'created_by',
            'edited_by',
        ).prefetch_related('sub_account_relations_as_tafsili__sub_account')
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Tafsili Account')
    
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
        if account.description:
            basic_fields.append({'label': _('Description'), 'value': account.description})
        
        detail_sections = [
            {
                'title': _('Basic Information'),
                'fields': basic_fields,
            },
        ]
        
        # Get related sub accounts
        from accounting.models import TafsiliSubAccountRelation
        company_id = self.request.session.get('active_company_id')
        related_sub_accounts = []
        if company_id:
            relations = TafsiliSubAccountRelation.objects.filter(
                tafsili_account=account,
                company_id=company_id
            ).select_related('sub_account')
            related_sub_accounts = [rel.sub_account for rel in relations]
        
        # Related Sub Accounts section
        if related_sub_accounts:
            sub_accounts_text = '<br>'.join([
                f"<code>{sub.account_code}</code> - {sub.account_name}"
                for sub in related_sub_accounts
            ])
            detail_sections.append({
                'title': _('Related Sub Accounts'),
                'type': 'custom',
                'content': f'<div class="readonly-field">{sub_accounts_text}</div>',
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('accounting:tafsili_accounts')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('accounting:tafsili_account_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class TafsiliAccountDeleteView(BaseDeleteView):
    """Delete a Tafsili account (حساب تفصیلی)."""
    model = Account
    success_url = reverse_lazy('accounting:tafsili_accounts')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'delete_own'
    active_module = 'accounting'
    success_message = _('حساب تفصیلی با موفقیت حذف شد.')
    
    def get_queryset(self):
        """Only allow deleting Tafsili accounts (level 3)."""
        return super().get_queryset().filter(account_level=3)
    
    def validate_deletion(self) -> tuple[bool, Optional[str]]:
        """Validate if account can be deleted."""
        obj = self.get_object()
        # Check if account is system account
        if obj.is_system_account:
            return False, _('حساب‌های سیستمی قابل حذف نیستند.')
        
        return True, None
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('حذف حساب تفصیلی')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('آیا مطمئن هستید که می‌خواهید این حساب تفصیلی را حذف کنید؟')
    
    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        return [
            {'label': _('کد تفصیلی'), 'value': self.object.account_code, 'type': 'code'},
            {'label': _('نام تفصیلی'), 'value': self.object.account_name},
            {'label': _('حساب معین والد'), 'value': self.object.parent_account.account_code if self.object.parent_account else '-', 'type': 'code'},
        ]
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('حذف'), 'url': None},
        ]

