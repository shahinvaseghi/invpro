"""
Tafsili Level (سطح تفصیلی) CRUD views for accounting module.
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
from accounting.models import TafsiliHierarchy, TafsiliLevelSubAccountRelation, Account
from accounting.forms import TafsiliHierarchyForm
from accounting.views.base import AccountingBaseView


class TafsiliHierarchyListView(BaseListView):
    """
    List all Tafsili Levels (سطوح تفصیلی) for the active company.
    """
    model = TafsiliHierarchy
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['sort_order', 'code']
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
        return ['code', 'name', 'name_en']
    
    def get_queryset(self):
        """Filter tafsili levels by active company and search/filter criteria."""
        queryset = super().get_queryset()
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('سطوح تفصیلی')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('سطوح تفصیلی'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:tafsili_hierarchy_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('افزودن سطح تفصیلی')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:tafsili_hierarchy_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:tafsili_hierarchy_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:tafsili_hierarchy_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('هیچ سطح تفصیلی یافت نشد')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('با افزودن اولین سطح تفصیلی شروع کنید.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📊'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('کد'), 'field': 'code', 'type': 'code'},
            {'label': _('نام'), 'field': 'name'},
            {'label': _('حساب‌های معین مرتبط'), 'field': 'sub_accounts_display', 'type': 'custom'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        
        # Add sub accounts info to each object for display
        company_id = self.request.session.get('active_company_id')
        if company_id:
            for obj in context['object_list']:
                sub_accounts = Account.objects.filter(
                    tafsili_level_relations__tafsili_level=obj,
                    tafsili_level_relations__company_id=company_id
                ).order_by('account_code')
                obj.sub_accounts_display = ', '.join([f"{sa.account_code} ({sa.account_name})" for sa in sub_accounts[:3]])
                if sub_accounts.count() > 3:
                    obj.sub_accounts_display += f" +{sub_accounts.count() - 3} بیشتر"
        
        context['print_enabled'] = True
        
        return context


class TafsiliHierarchyCreateView(BaseCreateView):
    """Create a new Tafsili Level (سطح تفصیلی)."""
    model = TafsiliHierarchy
    form_class = TafsiliHierarchyForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_hierarchy_list')
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('سطح تفصیلی با موفقیت ایجاد شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: TafsiliHierarchyForm) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('سطوح تفصیلی'), 'url': reverse('accounting:tafsili_hierarchy_list')},
            {'label': _('افزودن'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:tafsili_hierarchy_list')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('افزودن سطح تفصیلی')


class TafsiliHierarchyUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing Tafsili Level (سطح تفصیلی)."""
    model = TafsiliHierarchy
    form_class = TafsiliHierarchyForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_hierarchy_list')
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'edit_own'
    active_module = 'accounting'
    success_message = _('سطح تفصیلی با موفقیت به‌روزرسانی شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: TafsiliHierarchyForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('سطوح تفصیلی'), 'url': reverse('accounting:tafsili_hierarchy_list')},
            {'label': _('ویرایش'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:tafsili_hierarchy_list')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('ویرایش سطح تفصیلی')


class TafsiliHierarchyDetailView(BaseDetailView):
    """Detail view for viewing Tafsili Levels (read-only)."""
    model = TafsiliHierarchy
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'accounting.accounts.tafsili_hierarchy'
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
            'created_by',
            'edited_by',
        ).prefetch_related('sub_account_relations__sub_account')
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Tafsili Level')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        tafsili_level = self.object
        company_id = self.request.session.get('active_company_id')
        
        context['detail_title'] = self.get_page_title()
        context['info_banner'] = [
            {'label': _('Code'), 'value': tafsili_level.code, 'type': 'code'},
            {'label': _('Status'), 'value': tafsili_level.is_enabled, 'type': 'badge'},
        ]
        
        # Basic Information section
        basic_fields = [
            {'label': _('Name'), 'value': tafsili_level.name},
        ]
        if tafsili_level.name_en:
            basic_fields.append({'label': _('Name (EN)'), 'value': tafsili_level.name_en})
        if tafsili_level.description:
            basic_fields.append({'label': _('Description'), 'value': tafsili_level.description})
        
        detail_sections = [
            {
                'title': _('Basic Information'),
                'fields': basic_fields,
            },
        ]
        
        # Sub Accounts section
        if company_id:
            sub_accounts = Account.objects.filter(
                tafsili_level_relations__tafsili_level=tafsili_level,
                tafsili_level_relations__company_id=company_id
            ).order_by('account_code')
            if sub_accounts.exists():
                sub_accounts_text = '<br>'.join([
                    f"<code>{sa.account_code}</code> - {sa.account_name}"
                    for sa in sub_accounts
                ])
                detail_sections.append({
                    'title': _('Sub Accounts'),
                    'type': 'custom',
                    'content': f'<div class="readonly-field">{sub_accounts_text}</div>',
                })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('accounting:tafsili_hierarchy_list')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('accounting:tafsili_hierarchy_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class TafsiliHierarchyDeleteView(BaseDeleteView):
    """Delete a Tafsili Level (سطح تفصیلی)."""
    model = TafsiliHierarchy
    success_url = reverse_lazy('accounting:tafsili_hierarchy_list')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'delete_own'
    active_module = 'accounting'
    success_message = _('سطح تفصیلی با موفقیت حذف شد.')
    
    def validate_deletion(self) -> tuple[bool, Optional[str]]:
        """Validate if tafsili level can be deleted."""
        return True, None
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('حذف سطح تفصیلی')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('آیا مطمئن هستید که می‌خواهید این سطح تفصیلی را حذف کنید؟')
    
    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        return [
            {'label': _('کد'), 'value': self.object.code, 'type': 'code'},
            {'label': _('نام'), 'value': self.object.name},
        ]
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('سطوح تفصیلی'), 'url': reverse('accounting:tafsili_hierarchy_list')},
            {'label': _('حذف'), 'url': None},
        ]

