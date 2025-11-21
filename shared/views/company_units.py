"""
CompanyUnit CRUD views for shared module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.models import CompanyUnit
from shared.forms import CompanyUnitForm


class CompanyUnitListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all company units for the active company.
    """
    model = CompanyUnit
    template_name = 'shared/company_units.html'
    context_object_name = 'units'
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
        """Add active module and filters to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['filters'] = {
            'search': self.request.GET.get('search', '').strip(),
            'status': self.request.GET.get('status', ''),
        }
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
        context['form_title'] = 'ایجاد واحد سازمانی'
        return context


class CompanyUnitUpdateView(FeaturePermissionRequiredMixin, UpdateView):
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
        context['form_title'] = 'ویرایش واحد سازمانی'
        return context


class CompanyUnitDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a company unit."""
    model = CompanyUnit
    template_name = 'shared/company_unit_confirm_delete.html'
    success_url = reverse_lazy('shared:company_units')
    feature_code = 'shared.company_units'
    required_action = 'delete_own'

    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete company unit and show success message."""
        messages.success(self.request, 'واحد سازمانی حذف شد.')
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context

