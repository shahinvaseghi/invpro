"""
CompanyUnit CRUD views for shared module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.models import CompanyUnit
from shared.forms import CompanyUnitForm
from shared.views.base import EditLockProtectedMixin


class CompanyUnitListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all company units for the active company.
    """
    model = CompanyUnit
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'shared.company_units'

    def get_queryset(self):
        """Filter company units by active company and search/filter criteria."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return CompanyUnit.objects.none()

        queryset = CompanyUnit.objects.filter(
            company_id=active_company_id,
        ).select_related('parent_unit').order_by('public_code')

        search: str = self.request.GET.get('search', '').strip()
        status: Optional[str] = self.request.GET.get('status')

        if search:
            queryset = queryset.filter(
                Q(public_code__icontains=search) |
                Q(name__icontains=search)
            )

        if status in ('0', '1'):
            queryset = queryset.filter(is_enabled=status)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['page_title'] = _('Company Units')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Company Units')},
        ]
        context['create_url'] = reverse('shared:company_unit_create')
        context['create_button_text'] = _('Create Unit')
        context['show_filters'] = True
        context['status_filter'] = True
        context['search_placeholder'] = _('Search by code or name')
        context['clear_filter_url'] = reverse('shared:company_units')
        context['print_enabled'] = True
        context['show_actions'] = True
        context['edit_url_name'] = 'shared:company_unit_edit'
        context['delete_url_name'] = 'shared:company_unit_delete'
        context['table_headers'] = [
            {'label': _('CODE'), 'field': 'public_code', 'type': 'code'},
            {'label': _('Unit Name'), 'field': 'name'},
            {'label': _('Parent Unit'), 'field': 'parent_unit.name'},
            {'label': _('Status'), 'field': 'is_enabled', 'type': 'badge', 
             'true_label': _('Active'), 'false_label': _('Inactive')},
        ]
        context['empty_state_title'] = _('No Units Found')
        context['empty_state_message'] = _('Start by adding your first company unit.')
        context['empty_state_icon'] = '🏢'
        return context


class CompanyUnitCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new company unit."""
    model = CompanyUnit
    form_class = CompanyUnitForm
    template_name = 'shared/company_unit_form.html'
    success_url = reverse_lazy('shared:company_units')
    feature_code = 'shared.company_units'
    required_action = 'create'

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs

    def form_valid(self, form: CompanyUnitForm) -> HttpResponseRedirect:
        """Set company_id and show success message."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)

        form.instance.company_id = active_company_id
        messages.success(self.request, 'واحد سازمانی با موفقیت ایجاد شد.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Create Company Unit')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Company Units'), 'url': reverse('shared:company_units')},
        ]
        context['cancel_url'] = reverse('shared:company_units')
        return context


class CompanyUnitUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
    """Update existing company unit."""
    model = CompanyUnit
    form_class = CompanyUnitForm
    template_name = 'shared/company_unit_form.html'
    success_url = reverse_lazy('shared:company_units')
    feature_code = 'shared.company_units'
    required_action = 'edit_own'

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs

    def form_valid(self, form: CompanyUnitForm) -> HttpResponseRedirect:
        """Show success message."""
        messages.success(self.request, 'واحد سازمانی با موفقیت ویرایش شد.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Edit Company Unit')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Company Units'), 'url': reverse('shared:company_units')},
        ]
        context['cancel_url'] = reverse('shared:company_units')
        return context


class CompanyUnitDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a company unit."""
    model = CompanyUnit
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('shared:company_units')
    feature_code = 'shared.company_units'
    required_action = 'delete_own'

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete company unit and show success message."""
        messages.success(self.request, _('Company unit deleted successfully.'))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['delete_title'] = _('Delete Company Unit')
        context['confirmation_message'] = _('Are you sure you want to delete unit "{name}"?').format(name=self.object.name)
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Company Units'), 'url': reverse('shared:company_units')},
            {'label': _('Delete')},
        ]
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.public_code, 'type': 'code'},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Parent Unit'), 'value': self.object.parent_unit.name if self.object.parent_unit else '-'},
        ]
        context['cancel_url'] = reverse('shared:company_units')
        return context

