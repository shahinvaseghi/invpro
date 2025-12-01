"""
Sub Account (حساب معین) CRUD views for accounting module.
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
from accounting.forms import SubAccountForm
from accounting.views.base import AccountingBaseView


class SubAccountListView(FeaturePermissionRequiredMixin, AccountingBaseView, ListView):
    """
    List all Sub accounts (حساب معین) for the active company.
    """
    model = Account
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.sub'
    
    def get_queryset(self):
        """Filter Sub accounts (level 2) by active company and search/filter criteria."""
        queryset = Account.objects.filter(account_level=2)
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
                # Filter by GL account relation
                from accounting.models import SubAccountGLAccountRelation
                queryset = queryset.filter(
                    gl_account_relations__gl_account_id=int(parent_id),
                    gl_account_relations__company_id=self.request.session.get('active_company_id')
                ).distinct()
            except ValueError:
                pass
        
        return queryset.order_by('account_code')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('تعریف حساب معین')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_subsidiary')},
            {'label': _('تعریف حساب معین')},
        ]
        context['create_url'] = reverse('accounting:sub_account_create')
        context['create_button_text'] = _('افزودن حساب معین')
        context['show_filters'] = True
        context['status_filter'] = True
        context['search_placeholder'] = _('جستجو بر اساس کد یا نام')
        context['clear_filter_url'] = reverse('accounting:sub_accounts')
        context['print_enabled'] = True
        context['show_actions'] = True
        context['edit_url_name'] = 'accounting:sub_account_edit'
        context['delete_url_name'] = 'accounting:sub_account_delete'
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
        context['empty_state_title'] = _('هیچ حساب معینی یافت نشد')
        context['empty_state_message'] = _('با افزودن اولین حساب معین شروع کنید.')
        context['empty_state_icon'] = '📊'
        
        # Add GL accounts for filter dropdown
        company_id = self.request.session.get('active_company_id')
        if company_id:
            context['gl_accounts'] = Account.objects.filter(
                company_id=company_id,
                account_level=1,
                is_enabled=1
            ).order_by('account_code')
        
        return context


class SubAccountCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create a new Sub account (حساب معین)."""
    model = Account
    form_class = SubAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:sub_accounts')
    feature_code = 'accounting.accounts.sub'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: SubAccountForm) -> HttpResponseRedirect:
        """Set created_by and account_level."""
        form.instance.created_by = self.request.user
        form.instance.account_level = 2  # Sub account level
        messages.success(self.request, _('حساب معین با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('افزودن حساب معین')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_subsidiary')},
            {'label': _('تعریف حساب معین'), 'url': reverse('accounting:sub_accounts')},
            {'label': _('افزودن')},
        ]
        context['cancel_url'] = reverse('accounting:sub_accounts')
        return context


class SubAccountUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, AccountingBaseView, UpdateView):
    """Update an existing Sub account (حساب معین)."""
    model = Account
    form_class = SubAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:sub_accounts')
    feature_code = 'accounting.accounts.sub'
    required_action = 'edit_own'
    
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
        messages.success(self.request, _('حساب معین با موفقیت به‌روزرسانی شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ویرایش حساب معین')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_subsidiary')},
            {'label': _('تعریف حساب معین'), 'url': reverse('accounting:sub_accounts')},
            {'label': _('ویرایش')},
        ]
        context['cancel_url'] = reverse('accounting:sub_accounts')
        return context


class SubAccountDeleteView(FeaturePermissionRequiredMixin, AccountingBaseView, DeleteView):
    """Delete a Sub account (حساب معین)."""
    model = Account
    success_url = reverse_lazy('accounting:sub_accounts')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.sub'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Only allow deleting Sub accounts (level 2)."""
        return super().get_queryset().filter(account_level=2)
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete account and show success message."""
        obj = self.get_object()
        # Check if account is system account
        if obj.is_system_account:
            messages.error(self.request, _('حساب‌های سیستمی قابل حذف نیستند.'))
            return HttpResponseRedirect(self.success_url)
        
        # Check if account has child accounts (تفصیلی)
        if obj.child_accounts.exists():
            messages.error(self.request, _('نمی‌توان حساب معینی که دارای حساب تفصیلی است را حذف کرد.'))
            return HttpResponseRedirect(self.success_url)
        
        messages.success(self.request, _('حساب معین با موفقیت حذف شد.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('حذف حساب معین')
        context['confirmation_message'] = _('آیا مطمئن هستید که می‌خواهید این حساب معین را حذف کنید؟')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_subsidiary')},
            {'label': _('تعریف حساب معین'), 'url': reverse('accounting:sub_accounts')},
            {'label': _('حذف')},
        ]
        context['object_details'] = [
            {'label': _('کد معین'), 'value': self.object.account_code, 'type': 'code'},
            {'label': _('نام معین'), 'value': self.object.account_name},
            {'label': _('حساب کل والد'), 'value': self.object.parent_account.account_code if self.object.parent_account else '-', 'type': 'code'},
        ]
        context['cancel_url'] = reverse('accounting:sub_accounts')
        return context

