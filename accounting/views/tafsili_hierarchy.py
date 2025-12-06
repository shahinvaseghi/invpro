"""
Tafsili Hierarchy (تفصیلی چند سطحی) CRUD views for accounting module.
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
from accounting.models import TafsiliHierarchy
from accounting.forms import TafsiliHierarchyForm
from accounting.views.base import AccountingBaseView


class TafsiliHierarchyListView(BaseListView):
    """
    List all Tafsili Hierarchies (تفصیلی چند سطحی) for the active company.
    Shows tree structure.
    """
    model = TafsiliHierarchy
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['level', 'sort_order', 'code']
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
        """Filter hierarchies by active company and search/filter criteria."""
        queryset = super().get_queryset()
        
        level: str = self.request.GET.get('level', '')
        parent_id: str = self.request.GET.get('parent_id', '')
        
        if level:
            try:
                queryset = queryset.filter(level=int(level))
            except ValueError:
                pass
        
        if parent_id:
            try:
                queryset = queryset.filter(parent_id=int(parent_id))
            except ValueError:
                pass
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('تفصیلی چند سطحی')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تفصیلی چند سطحی'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:tafsili_hierarchy_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('افزودن تفصیلی چند سطحی')
    
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
        return _('هیچ تفصیلی چند سطحی یافت نشد')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('با افزودن اولین تفصیلی چند سطحی شروع کنید.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '🌳'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            {'label': _('کد'), 'field': 'code', 'type': 'code'},
            {'label': _('نام'), 'field': 'name'},
            {'label': _('مسیر کامل'), 'field': 'full_path_display', 'type': 'custom'},
            {'label': _('سطح'), 'field': 'level'},
            {'label': _('تفصیلی اصلی'), 'field': 'tafsili_account.account_code', 'type': 'code'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        
        # Add full path to each object for display
        for obj in context['object_list']:
            obj.full_path_display = obj.get_full_path()
        
        # Add root hierarchies for filter dropdown
        company_id = self.request.session.get('active_company_id')
        if company_id:
            context['root_hierarchies'] = TafsiliHierarchy.objects.filter(
                company_id=company_id,
                parent__isnull=True,
                is_enabled=1
            ).order_by('sort_order', 'code')
        context['print_enabled'] = True
        
        return context


class TafsiliHierarchyCreateView(BaseCreateView):
    """Create a new Tafsili Hierarchy (تفصیلی چند سطحی)."""
    model = TafsiliHierarchy
    form_class = TafsiliHierarchyForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_hierarchy_list')
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('تفصیلی چند سطحی با موفقیت ایجاد شد.')
    
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
            {'label': _('تفصیلی چند سطحی'), 'url': reverse('accounting:tafsili_hierarchy_list')},
            {'label': _('افزودن'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:tafsili_hierarchy_list')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('افزودن تفصیلی چند سطحی')


class TafsiliHierarchyUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing Tafsili Hierarchy (تفصیلی چند سطحی)."""
    model = TafsiliHierarchy
    form_class = TafsiliHierarchyForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_hierarchy_list')
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'edit_own'
    active_module = 'accounting'
    success_message = _('تفصیلی چند سطحی با موفقیت به‌روزرسانی شد.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        # Exclude current instance from parent choices
        if self.object:
            kwargs['exclude_hierarchy_id'] = self.object.id
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
            {'label': _('تفصیلی چند سطحی'), 'url': reverse('accounting:tafsili_hierarchy_list')},
            {'label': _('ویرایش'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:tafsili_hierarchy_list')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('ویرایش تفصیلی چند سطحی')


class TafsiliHierarchyDetailView(BaseDetailView):
    """Detail view for viewing Tafsili Hierarchies (read-only)."""
    model = TafsiliHierarchy
    template_name = 'accounting/tafsili_hierarchy_detail.html'
    context_object_name = 'hierarchy'
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
            'parent',
            'tafsili_account',
            'created_by',
            'edited_by',
        ).prefetch_related('children')
        return queryset
    
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
    """Delete a Tafsili Hierarchy (تفصیلی چند سطحی)."""
    model = TafsiliHierarchy
    success_url = reverse_lazy('accounting:tafsili_hierarchy_list')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'delete_own'
    active_module = 'accounting'
    success_message = _('تفصیلی چند سطحی با موفقیت حذف شد.')
    
    def validate_deletion(self) -> tuple[bool, Optional[str]]:
        """Validate if hierarchy can be deleted."""
        obj = self.get_object()
        # Check if hierarchy has children
        if obj.children.exists():
            return False, _('نمی‌توان تفصیلی چند سطحی که دارای زیرگروه است را حذف کرد.')
        
        return True, None
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('حذف تفصیلی چند سطحی')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('آیا مطمئن هستید که می‌خواهید این تفصیلی چند سطحی را حذف کنید؟')
    
    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        return [
            {'label': _('کد'), 'value': self.object.code, 'type': 'code'},
            {'label': _('نام'), 'value': self.object.name},
            {'label': _('مسیر کامل'), 'value': self.object.get_full_path()},
            {'label': _('سطح'), 'value': self.object.level},
        ]
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تفصیلی چند سطحی'), 'url': reverse('accounting:tafsili_hierarchy_list')},
            {'label': _('حذف'), 'url': None},
        ]

