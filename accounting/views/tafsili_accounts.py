"""
Tafsili Account (حساب تفصیلی) CRUD views for accounting module.
"""
from typing import Any, Dict
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from accounting.models import Account
from accounting.forms import TafsiliAccountForm
from accounting.views.base import AccountingBaseView


class TafsiliAccountListView(FeaturePermissionRequiredMixin, AccountingBaseView, ListView):
    """
    List all Tafsili accounts (حساب تفصیلی) for the active company.
    """
    model = Account
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.tafsili'
    
    def get_queryset(self):
        """Filter Tafsili accounts (level 3) by active company and search/filter criteria."""
        queryset = Account.objects.filter(account_level=3)
        queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
        
        search: str = self.request.GET.get('search', '').strip()
        status: str = self.request.GET.get('status', '')
        parent_id: str = self.request.GET.get('parent_id', '')
        
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
        
        return queryset.order_by('account_code')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('تعریف حساب تفصیلی')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی')},
        ]
        context['create_url'] = reverse('accounting:tafsili_account_create')
        context['create_button_text'] = _('افزودن حساب تفصیلی')
        context['show_filters'] = True
        context['status_filter'] = True
        context['search_placeholder'] = _('جستجو بر اساس کد یا نام')
        context['clear_filter_url'] = reverse('accounting:tafsili_accounts')
        context['print_enabled'] = True
        context['show_actions'] = True
        context['edit_url_name'] = 'accounting:tafsili_account_edit'
        context['delete_url_name'] = 'accounting:tafsili_account_delete'
        context['table_headers'] = [
            {'label': _('کد تفصیلی'), 'field': 'account_code', 'type': 'code'},
            {'label': _('نام تفصیلی'), 'field': 'account_name'},
            {'label': _('حساب‌های معین مرتبط'), 'field': 'sub_accounts_display', 'type': 'custom'},
            {'label': _('طرف تراز'), 'field': 'normal_balance'},
            {'label': _('مانده جاری'), 'field': 'current_balance'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        
        # Add sub accounts info to each object for display
        from accounting.models import TafsiliSubAccountRelation
        company_id = self.request.session.get('active_company_id')
        if company_id:
            for obj in context['object_list']:
                sub_accounts = Account.objects.filter(
                    sub_account_relations_as_tafsili__tafsili_account=obj,
                    sub_account_relations_as_tafsili__company_id=company_id
                ).order_by('account_code')
                obj.sub_accounts_display = ', '.join([f"{sa.account_code} ({sa.account_name})" for sa in sub_accounts[:3]])
                if sub_accounts.count() > 3:
                    obj.sub_accounts_display += f" +{sub_accounts.count() - 3} بیشتر"
        context['empty_state_title'] = _('هیچ حساب تفصیلی یافت نشد')
        context['empty_state_message'] = _('با افزودن اولین حساب تفصیلی شروع کنید.')
        context['empty_state_icon'] = '📊'
        
        # Add Sub accounts for filter dropdown
        company_id = self.request.session.get('active_company_id')
        if company_id:
            context['sub_accounts'] = Account.objects.filter(
                company_id=company_id,
                account_level=2,
                is_enabled=1
            ).order_by('account_code')
        
        return context


class TafsiliAccountCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create a new Tafsili account (حساب تفصیلی)."""
    model = Account
    form_class = TafsiliAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_accounts')
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: TafsiliAccountForm) -> HttpResponseRedirect:
        """Set created_by and account_level."""
        form.instance.created_by = self.request.user
        form.instance.account_level = 3  # Tafsili account level
        messages.success(self.request, _('حساب تفصیلی با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('افزودن حساب تفصیلی')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('افزودن')},
        ]
        context['cancel_url'] = reverse('accounting:tafsili_accounts')
        return context


class TafsiliAccountUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, AccountingBaseView, UpdateView):
    """Update an existing Tafsili account (حساب تفصیلی)."""
    model = Account
    form_class = TafsiliAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_accounts')
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'edit_own'
    
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
        messages.success(self.request, _('حساب تفصیلی با موفقیت به‌روزرسانی شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ویرایش حساب تفصیلی')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('ویرایش')},
        ]
        context['cancel_url'] = reverse('accounting:tafsili_accounts')
        return context


class TafsiliAccountDeleteView(FeaturePermissionRequiredMixin, AccountingBaseView, DeleteView):
    """Delete a Tafsili account (حساب تفصیلی)."""
    model = Account
    success_url = reverse_lazy('accounting:tafsili_accounts')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.tafsili'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Only allow deleting Tafsili accounts (level 3)."""
        return super().get_queryset().filter(account_level=3)
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete account and show success message."""
        obj = self.get_object()
        # Check if account is system account
        if obj.is_system_account:
            messages.error(self.request, _('حساب‌های سیستمی قابل حذف نیستند.'))
            return HttpResponseRedirect(self.success_url)
        
        messages.success(self.request, _('حساب تفصیلی با موفقیت حذف شد.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('حذف حساب تفصیلی')
        context['confirmation_message'] = _('آیا مطمئن هستید که می‌خواهید این حساب تفصیلی را حذف کنید؟')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تعریف حساب تفصیلی'), 'url': reverse('accounting:tafsili_accounts')},
            {'label': _('حذف')},
        ]
        context['object_details'] = [
            {'label': _('کد تفصیلی'), 'value': self.object.account_code, 'type': 'code'},
            {'label': _('نام تفصیلی'), 'value': self.object.account_name},
            {'label': _('حساب معین والد'), 'value': self.object.parent_account.account_code if self.object.parent_account else '-', 'type': 'code'},
        ]
        context['cancel_url'] = reverse('accounting:tafsili_accounts')
        return context

