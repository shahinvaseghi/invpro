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

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from accounting.models import TafsiliHierarchy
from accounting.forms import TafsiliHierarchyForm
from accounting.views.base import AccountingBaseView


class TafsiliHierarchyListView(FeaturePermissionRequiredMixin, AccountingBaseView, ListView):
    """
    List all Tafsili Hierarchies (تفصیلی چند سطحی) for the active company.
    Shows tree structure.
    """
    model = TafsiliHierarchy
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    
    def get_queryset(self):
        """Filter hierarchies by active company and search/filter criteria."""
        queryset = TafsiliHierarchy.objects.all()
        queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
        
        search: str = self.request.GET.get('search', '').strip()
        status: str = self.request.GET.get('status', '')
        level: str = self.request.GET.get('level', '')
        parent_id: str = self.request.GET.get('parent_id', '')
        
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search) |
                Q(name_en__icontains=search)
            )
        
        if status in ('0', '1'):
            queryset = queryset.filter(is_enabled=int(status))
        else:
            # Default: show only enabled hierarchies
            queryset = queryset.filter(is_enabled=1)
        
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
        
        return queryset.order_by('level', 'sort_order', 'code')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('تفصیلی چند سطحی')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تفصیلی چند سطحی')},
        ]
        context['create_url'] = reverse('accounting:tafsili_hierarchy_create')
        context['create_button_text'] = _('افزودن تفصیلی چند سطحی')
        context['show_filters'] = True
        context['status_filter'] = True
        context['search_placeholder'] = _('جستجو بر اساس کد یا نام')
        context['clear_filter_url'] = reverse('accounting:tafsili_hierarchy_list')
        context['print_enabled'] = True
        context['show_actions'] = True
        context['feature_code'] = 'accounting.accounts.tafsili_hierarchy'
        context['detail_url_name'] = 'accounting:tafsili_hierarchy_detail'
        context['edit_url_name'] = 'accounting:tafsili_hierarchy_edit'
        context['delete_url_name'] = 'accounting:tafsili_hierarchy_delete'
        context['table_headers'] = [
            {'label': _('کد'), 'field': 'code', 'type': 'code'},
            {'label': _('نام'), 'field': 'name'},
            {'label': _('مسیر کامل'), 'field': 'full_path_display', 'type': 'custom'},
            {'label': _('سطح'), 'field': 'level'},
            {'label': _('تفصیلی اصلی'), 'field': 'tafsili_account.account_code', 'type': 'code'},
            {'label': _('وضعیت'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('فعال'), 'false_label': _('غیرفعال')},
        ]
        context['empty_state_title'] = _('هیچ تفصیلی چند سطحی یافت نشد')
        context['empty_state_message'] = _('با افزودن اولین تفصیلی چند سطحی شروع کنید.')
        context['empty_state_icon'] = '🌳'
        
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
        
        return context


class TafsiliHierarchyCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create a new Tafsili Hierarchy (تفصیلی چند سطحی)."""
    model = TafsiliHierarchy
    form_class = TafsiliHierarchyForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_hierarchy_list')
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: TafsiliHierarchyForm) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        messages.success(self.request, _('تفصیلی چند سطحی با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('افزودن تفصیلی چند سطحی')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تفصیلی چند سطحی'), 'url': reverse('accounting:tafsili_hierarchy_list')},
            {'label': _('افزودن')},
        ]
        context['cancel_url'] = reverse('accounting:tafsili_hierarchy_list')
        return context


class TafsiliHierarchyUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, AccountingBaseView, UpdateView):
    """Update an existing Tafsili Hierarchy (تفصیلی چند سطحی)."""
    model = TafsiliHierarchy
    form_class = TafsiliHierarchyForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:tafsili_hierarchy_list')
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'edit_own'
    
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
        messages.success(self.request, _('تفصیلی چند سطحی با موفقیت به‌روزرسانی شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ویرایش تفصیلی چند سطحی')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تفصیلی چند سطحی'), 'url': reverse('accounting:tafsili_hierarchy_list')},
            {'label': _('ویرایش')},
        ]
        context['cancel_url'] = reverse('accounting:tafsili_hierarchy_list')
        return context


class TafsiliHierarchyDetailView(FeaturePermissionRequiredMixin, AccountingBaseView, DetailView):
    """Detail view for viewing Tafsili Hierarchies (read-only)."""
    model = TafsiliHierarchy
    template_name = 'accounting/tafsili_hierarchy_detail.html'
    context_object_name = 'hierarchy'
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter by active company."""
        queryset = TafsiliHierarchy.objects.all()
        queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
        queryset = queryset.select_related(
            'parent',
            'tafsili_account',
            'created_by',
            'edited_by',
        ).prefetch_related('children')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('مشاهده تفصیلی چند سطحی')
        context['list_url'] = reverse_lazy('accounting:tafsili_hierarchy_list')
        context['edit_url'] = reverse_lazy('accounting:tafsili_hierarchy_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        context['feature_code'] = 'accounting.accounts.tafsili_hierarchy'
        return context


class TafsiliHierarchyDeleteView(FeaturePermissionRequiredMixin, AccountingBaseView, DeleteView):
    """Delete a Tafsili Hierarchy (تفصیلی چند سطحی)."""
    model = TafsiliHierarchy
    success_url = reverse_lazy('accounting:tafsili_hierarchy_list')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.accounts.tafsili_hierarchy'
    required_action = 'delete_own'
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete hierarchy and show success message."""
        obj = self.get_object()
        # Check if hierarchy has children
        if obj.children.exists():
            messages.error(self.request, _('نمی‌توان تفصیلی چند سطحی که دارای زیرگروه است را حذف کرد.'))
            return HttpResponseRedirect(self.success_url)
        
        messages.success(self.request, _('تفصیلی چند سطحی با موفقیت حذف شد.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('حذف تفصیلی چند سطحی')
        context['confirmation_message'] = _('آیا مطمئن هستید که می‌خواهید این تفصیلی چند سطحی را حذف کنید؟')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:general_detail')},
            {'label': _('تفصیلی چند سطحی'), 'url': reverse('accounting:tafsili_hierarchy_list')},
            {'label': _('حذف')},
        ]
        context['object_details'] = [
            {'label': _('کد'), 'value': self.object.code, 'type': 'code'},
            {'label': _('نام'), 'value': self.object.name},
            {'label': _('مسیر کامل'), 'value': self.object.get_full_path()},
            {'label': _('سطح'), 'value': self.object.level},
        ]
        context['cancel_url'] = reverse('accounting:tafsili_hierarchy_list')
        return context

