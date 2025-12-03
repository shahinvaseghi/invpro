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

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from accounting.models import Account
from accounting.forms import GLAccountForm
from accounting.views.base import AccountingBaseView


class GLAccountListView(FeaturePermissionRequiredMixin, AccountingBaseView, ListView):
    """
    List all GL accounts (حساب کل) for the active company.
    """
    model = Account
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.gl'
    
    def get_queryset(self):
        """Filter GL accounts (level 1) by active company and search/filter criteria."""
        queryset = Account.objects.filter(account_level=1)
        queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
        
        search: str = self.request.GET.get('search', '').strip()
        status: str = self.request.GET.get('status', '')
        account_type: str = self.request.GET.get('account_type', '')
        
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
        
        return queryset.order_by('account_code')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('تعریف حساب کل')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('تعریف حساب کل')},
        ]
        context['create_url'] = reverse('accounting:gl_account_create')
        context['create_button_text'] = _('افزودن حساب کل')
        context['show_filters'] = True
        context['status_filter'] = True
        context['search_placeholder'] = _('جستجو بر اساس کد یا نام')
        context['clear_filter_url'] = reverse('accounting:gl_accounts')
        context['print_enabled'] = True
        context['show_actions'] = True
        context['feature_code'] = 'accounting.accounts.gl'
        context['detail_url_name'] = 'accounting:gl_account_detail'
        context['edit_url_name'] = 'accounting:gl_account_edit'
        context['delete_url_name'] = 'accounting:gl_account_delete'
        context['table_headers'] = [
            {'label': _('کد کل'), 'field': 'account_code', 'type': 'code'},
            {'label': _('نام کل'), 'field': 'account_name'},
            {'label': _('نوع حساب'), 'field': 'account_type'},
            {'label': _('طرف تراز'), 'field': 'normal_balance'},
            {'label': _('مانده جاری'), 'field': 'current_balance'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        context['empty_state_title'] = _('هیچ حساب کلی یافت نشد')
        context['empty_state_message'] = _('با افزودن اولین حساب کل شروع کنید.')
        context['empty_state_icon'] = '📊'
        return context


class GLAccountCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create a new GL account (حساب کل)."""
    model = Account
    form_class = GLAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:gl_accounts')
    feature_code = 'accounting.accounts.gl'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: GLAccountForm) -> HttpResponseRedirect:
        """Set created_by and account_level."""
        form.instance.created_by = self.request.user
        form.instance.account_level = 1  # GL account level
        messages.success(self.request, _('حساب کل با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('افزودن حساب کل')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('تعریف حساب کل'), 'url': reverse('accounting:gl_accounts')},
            {'label': _('افزودن')},
        ]
        context['cancel_url'] = reverse('accounting:gl_accounts')
        return context


class GLAccountUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, AccountingBaseView, UpdateView):
    """Update an existing GL account (حساب کل)."""
    model = Account
    form_class = GLAccountForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:gl_accounts')
    feature_code = 'accounting.accounts.gl'
    required_action = 'edit_own'
    
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
        messages.success(self.request, _('حساب کل با موفقیت به‌روزرسانی شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ویرایش حساب کل')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('تعریف حساب کل'), 'url': reverse('accounting:gl_accounts')},
            {'label': _('ویرایش')},
        ]
        context['cancel_url'] = reverse('accounting:gl_accounts')
        return context


class GLAccountDetailView(FeaturePermissionRequiredMixin, AccountingBaseView, DetailView):
    """Detail view for viewing GL accounts (read-only)."""
    model = Account
    template_name = 'accounting/gl_account_detail.html'
    context_object_name = 'account'
    feature_code = 'accounting.accounts.gl'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter GL accounts (level 1) by active company."""
        queryset = Account.objects.filter(account_level=1)
        queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
        queryset = queryset.select_related(
            'created_by',
            'edited_by',
        ).prefetch_related('child_accounts')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('مشاهده حساب کل')
        context['list_url'] = reverse_lazy('accounting:gl_accounts')
        context['edit_url'] = reverse_lazy('accounting:gl_account_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        context['feature_code'] = 'accounting.accounts.gl'
        return context


class GLAccountDeleteView(FeaturePermissionRequiredMixin, AccountingBaseView, DeleteView):
    """Delete a GL account (حساب کل)."""
    model = Account
    success_url = reverse_lazy('accounting:gl_accounts')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.gl'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Only allow deleting GL accounts (level 1)."""
        return super().get_queryset().filter(account_level=1)
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete account and show success message."""
        obj = self.get_object()
        # Check if account is system account
        if obj.is_system_account:
            messages.error(self.request, _('حساب‌های سیستمی قابل حذف نیستند.'))
            return HttpResponseRedirect(self.success_url)
        
        # Check if account has child accounts (معین)
        if obj.child_accounts.exists():
            messages.error(self.request, _('نمی‌توان حساب کلی که دارای حساب معین است را حذف کرد.'))
            return HttpResponseRedirect(self.success_url)
        
        messages.success(self.request, _('حساب کل با موفقیت حذف شد.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('حذف حساب کل')
        context['confirmation_message'] = _('آیا مطمئن هستید که می‌خواهید این حساب کل را حذف کنید؟')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_ledger')},
            {'label': _('تعریف حساب کل'), 'url': reverse('accounting:gl_accounts')},
            {'label': _('حذف')},
        ]
        context['object_details'] = [
            {'label': _('کد کل'), 'value': self.object.account_code, 'type': 'code'},
            {'label': _('نام کل'), 'value': self.object.account_name},
            {'label': _('نوع حساب'), 'value': self.object.get_account_type_display()},
        ]
        context['cancel_url'] = reverse('accounting:gl_accounts')
        return context

