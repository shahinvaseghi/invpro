"""
Fiscal Year CRUD views for accounting module.
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
from accounting.models import FiscalYear
from accounting.forms import FiscalYearForm
from accounting.views.base import AccountingBaseView


class FiscalYearListView(FeaturePermissionRequiredMixin, AccountingBaseView, ListView):
    """
    List all fiscal years for the active company.
    """
    model = FiscalYear
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.fiscal_years'
    
    def get_queryset(self):
        """Filter fiscal years by active company and search/filter criteria."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, self.feature_code)
        
        search: str = self.request.GET.get('search', '').strip()
        status: str = self.request.GET.get('status', '')
        
        if search:
            queryset = queryset.filter(
                Q(fiscal_year_code__icontains=search) |
                Q(fiscal_year_name__icontains=search)
            )
        
        if status in ('0', '1'):
            queryset = queryset.filter(is_enabled=int(status))
        else:
            # Default: show only enabled fiscal years
            queryset = queryset.filter(is_enabled=1)
        
        return queryset.order_by('-fiscal_year_code')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Fiscal Years')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Fiscal Years')},
        ]
        context['create_url'] = reverse('accounting:fiscal_year_create')
        context['create_button_text'] = _('Create Fiscal Year')
        context['show_filters'] = True
        context['status_filter'] = True
        context['search_placeholder'] = _('Search by code or name')
        context['clear_filter_url'] = reverse('accounting:fiscal_years')
        context['print_enabled'] = True
        context['show_actions'] = True
        context['edit_url_name'] = 'accounting:fiscal_year_edit'
        context['delete_url_name'] = 'accounting:fiscal_year_delete'
        context['table_headers'] = [
            {'label': _('CODE'), 'field': 'fiscal_year_code', 'type': 'code'},
            {'label': _('Name'), 'field': 'fiscal_year_name'},
            {'label': _('Start Date'), 'field': 'start_date'},
            {'label': _('End Date'), 'field': 'end_date'},
            {'label': _('Current'), 'field': 'is_current', 'type': 'badge',
             'true_label': _('Yes'), 'false_label': _('No')},
            {'label': _('Status'), 'field': 'is_enabled', 'type': 'badge',
             'true_label': _('Active'), 'false_label': _('Inactive')},
        ]
        context['empty_state_title'] = _('No Fiscal Years Found')
        context['empty_state_message'] = _('Start by adding your first fiscal year.')
        context['empty_state_icon'] = '📅'
        return context


class FiscalYearCreateView(FeaturePermissionRequiredMixin, AccountingBaseView, CreateView):
    """Create a new fiscal year."""
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:fiscal_years')
    feature_code = 'accounting.fiscal_years'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: FiscalYearForm) -> HttpResponseRedirect:
        """Set created_by and show success message."""
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Fiscal year created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Fiscal Year')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Fiscal Years'), 'url': reverse('accounting:fiscal_years')},
        ]
        context['cancel_url'] = reverse('accounting:fiscal_years')
        return context


class FiscalYearUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, AccountingBaseView, UpdateView):
    """Update an existing fiscal year."""
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:fiscal_years')
    feature_code = 'accounting.fiscal_years'
    required_action = 'edit_own'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: FiscalYearForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Fiscal year updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Fiscal Year')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Fiscal Years'), 'url': reverse('accounting:fiscal_years')},
        ]
        context['cancel_url'] = reverse('accounting:fiscal_years')
        return context


class FiscalYearDeleteView(FeaturePermissionRequiredMixin, AccountingBaseView, DeleteView):
    """Delete a fiscal year."""
    model = FiscalYear
    success_url = reverse_lazy('accounting:fiscal_years')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.fiscal_years'
    required_action = 'delete_own'
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete fiscal year and show success message."""
        messages.success(self.request, _('Fiscal year deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Fiscal Year')
        context['confirmation_message'] = _('Do you really want to delete this fiscal year?')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Fiscal Years'), 'url': reverse('accounting:fiscal_years')},
            {'label': _('Delete')},
        ]
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.fiscal_year_code, 'type': 'code'},
            {'label': _('Name'), 'value': self.object.fiscal_year_name},
            {'label': _('Start Date'), 'value': self.object.start_date},
            {'label': _('End Date'), 'value': self.object.end_date},
        ]
        context['cancel_url'] = reverse('accounting:fiscal_years')
        return context

