"""
Company CRUD views for shared module.
"""
from typing import Any, Dict
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.models import Company, UserCompanyAccess
from shared.forms import CompanyForm


class CompanyListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all companies that the current user has access to.
    """
    model = Company
    template_name = 'shared/companies.html'
    context_object_name = 'companies'
    paginate_by = 50
    feature_code = 'shared.companies'
    
    def get_queryset(self):
        """Filter companies based on user access."""
        # Get companies user has access to
        user_company_ids = UserCompanyAccess.objects.filter(
            user=self.request.user,
            is_enabled=1
        ).values_list('company_id', flat=True)
        
        return Company.objects.filter(
            id__in=user_company_ids,
            is_enabled=1
        ).order_by('public_code')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context


class CompanyCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new company."""
    model = Company
    form_class = CompanyForm
    template_name = 'shared/company_form.html'
    success_url = reverse_lazy('shared:companies')
    feature_code = 'shared.companies'
    required_action = 'create'
    
    def form_valid(self, form: CompanyForm) -> HttpResponseRedirect:
        """Auto-set created_by and create UserCompanyAccess."""
        # Auto-set created_by
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        # Create UserCompanyAccess for the creator
        UserCompanyAccess.objects.create(
            user=self.request.user,
            company=self.object,
            access_level_id=1,  # ADMIN level
            is_primary=1,  # Make it primary
            is_enabled=1
        )
        
        messages.success(self.request, _('Company created successfully.'))
        return response
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Create Company')
        return context


class CompanyUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing company."""
    model = Company
    form_class = CompanyForm
    template_name = 'shared/company_form.html'
    success_url = reverse_lazy('shared:companies')
    feature_code = 'shared.companies'
    required_action = 'edit_own'
    
    def form_valid(self, form: CompanyForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        # Auto-set edited_by
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Company updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Edit Company')
        return context


class CompanyDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a company."""
    model = Company
    success_url = reverse_lazy('shared:companies')
    template_name = 'shared/company_confirm_delete.html'
    feature_code = 'shared.companies'
    required_action = 'delete_own'
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete company and show success message."""
        messages.success(self.request, _('Company deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context

