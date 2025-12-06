"""
Fiscal Year CRUD views for accounting module.
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
from accounting.models import FiscalYear
from accounting.forms import FiscalYearForm
from accounting.views.base import AccountingBaseView


class FiscalYearListView(BaseListView):
    """
    List all fiscal years for the active company.
    """
    model = FiscalYear
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'accounting.fiscal_years'
    required_action = 'view_all'
    active_module = 'accounting'
    default_order_by = ['-fiscal_year_code']
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
        return ['fiscal_year_code', 'fiscal_year_name']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Fiscal Years')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Fiscal Years'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('accounting:fiscal_year_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Fiscal Year')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'accounting:fiscal_year_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'accounting:fiscal_year_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'accounting:fiscal_year_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Fiscal Years Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by adding your first fiscal year.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📅'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
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
        context['print_enabled'] = True
        return context


class FiscalYearCreateView(BaseCreateView):
    """Create a new fiscal year."""
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:fiscal_years')
    feature_code = 'accounting.fiscal_years'
    required_action = 'create'
    active_module = 'accounting'
    success_message = _('Fiscal year created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: FiscalYearForm) -> HttpResponseRedirect:
        """Set created_by."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Fiscal Years'), 'url': reverse('accounting:fiscal_years')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:fiscal_years')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Fiscal Year')


class FiscalYearUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing fiscal year."""
    model = FiscalYear
    form_class = FiscalYearForm
    template_name = 'shared/generic/generic_form.html'
    success_url = reverse_lazy('accounting:fiscal_years')
    feature_code = 'accounting.fiscal_years'
    required_action = 'edit_own'
    active_module = 'accounting'
    success_message = _('Fiscal year updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: FiscalYearForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        return super().form_valid(form)
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Fiscal Years'), 'url': reverse('accounting:fiscal_years')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('accounting:fiscal_years')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Fiscal Year')


class FiscalYearDetailView(BaseDetailView):
    """Detail view for viewing fiscal years (read-only)."""
    model = FiscalYear
    template_name = 'accounting/fiscal_year_detail.html'
    context_object_name = 'fiscal_year'
    feature_code = 'accounting.fiscal_years'
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
        )
        return queryset
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('accounting:fiscal_years')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('accounting:fiscal_year_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class FiscalYearDeleteView(BaseDeleteView):
    """Delete a fiscal year."""
    model = FiscalYear
    success_url = reverse_lazy('accounting:fiscal_years')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'accounting.fiscal_years'
    required_action = 'delete_own'
    active_module = 'accounting'
    success_message = _('Fiscal year deleted successfully.')
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Fiscal Year')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this fiscal year?')
    
    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        return [
            {'label': _('Code'), 'value': self.object.fiscal_year_code, 'type': 'code'},
            {'label': _('Name'), 'value': self.object.fiscal_year_name},
            {'label': _('Start Date'), 'value': self.object.start_date},
            {'label': _('End Date'), 'value': self.object.end_date},
        ]
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Accounting'), 'url': reverse('accounting:dashboard')},
            {'label': _('Fiscal Years'), 'url': reverse('accounting:fiscal_years')},
            {'label': _('Delete'), 'url': None},
        ]

