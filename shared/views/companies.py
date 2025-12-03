"""
Company CRUD views for shared module.
"""
from typing import Any, Dict
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.models import Company, UserCompanyAccess
from shared.forms import CompanyForm
from shared.views.base import EditLockProtectedMixin


class CompanyListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all companies that the current user has access to.
    """
    model = Company
    template_name = 'shared/generic/generic_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'shared.companies'
    
    def get_queryset(self):
        """Filter companies based on user access and search/filter parameters."""
        # Get companies user has access to
        user_company_ids = UserCompanyAccess.objects.filter(
            user=self.request.user,
            is_enabled=1
        ).values_list('company_id', flat=True)
        
        queryset = Company.objects.filter(
            id__in=user_company_ids
        ).order_by('public_code')
        
        # Apply status filter
        status = self.request.GET.get('status', '')
        if status == '1':
            queryset = queryset.filter(is_enabled=1)
        elif status == '0':
            queryset = queryset.filter(is_enabled=0)
        else:
            # Default: show only enabled companies
            queryset = queryset.filter(is_enabled=1)
        
        # Apply search filter
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                public_code__icontains=search
            ) | queryset.filter(
                display_name__icontains=search
            ) | queryset.filter(
                legal_name__icontains=search
            )
        
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['page_title'] = _('Companies')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Companies')},
        ]
        context['create_url'] = reverse('shared:company_create')
        context['create_button_text'] = _('Create Company')
        context['show_filters'] = True
        context['status_filter'] = True
        context['search_placeholder'] = _('Search by code or name')
        context['clear_filter_url'] = reverse('shared:companies')
        context['print_enabled'] = True
        context['show_actions'] = True
        context['feature_code'] = 'shared.companies'
        context['detail_url_name'] = 'shared:company_detail'
        context['edit_url_name'] = 'shared:company_edit'
        context['delete_url_name'] = 'shared:company_delete'
        context['table_headers'] = [
            {'label': _('CODE'), 'field': 'public_code', 'type': 'code'},
            {'label': _('Display Name'), 'field': 'display_name'},
            {'label': _('Legal Name'), 'field': 'legal_name'},
            {'label': _('Tax ID'), 'field': 'tax_id'},
            {'label': _('City'), 'field': 'city'},
            {'label': _('Country'), 'field': 'country'},
            {'label': _('Status'), 'field': 'is_enabled', 'type': 'badge', 
             'true_label': _('Active'), 'false_label': _('Inactive')},
        ]
        context['empty_state_title'] = _('No Companies Found')
        context['empty_state_message'] = _("You don't have access to any companies yet.")
        context['empty_state_icon'] = '🏢'
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
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Companies'), 'url': reverse('shared:companies')},
        ]
        context['cancel_url'] = reverse('shared:companies')
        return context


class CompanyUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
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
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Companies'), 'url': reverse('shared:companies')},
        ]
        context['cancel_url'] = reverse('shared:companies')
        return context


class CompanyDetailView(FeaturePermissionRequiredMixin, DetailView):
    """Detail view for viewing companies (read-only)."""
    model = Company
    template_name = 'shared/company_detail.html'
    context_object_name = 'company'
    feature_code = 'shared.companies'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter companies based on user access."""
        user_company_ids = UserCompanyAccess.objects.filter(
            user=self.request.user,
            is_enabled=1
        ).values_list('company_id', flat=True)
        return Company.objects.filter(id__in=user_company_ids).select_related('created_by', 'edited_by')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['list_url'] = reverse_lazy('shared:companies')
        context['edit_url'] = reverse_lazy('shared:company_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        context['feature_code'] = 'shared.companies'
        return context


class CompanyDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a company."""
    model = Company
    success_url = reverse_lazy('shared:companies')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'shared.companies'
    required_action = 'delete_own'
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete company and show success message."""
        messages.success(self.request, _('Company deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['delete_title'] = _('Delete Company')
        context['confirmation_message'] = _('Do you really want to delete this company?')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Companies'), 'url': reverse('shared:companies')},
            {'label': _('Delete')},
        ]
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.public_code, 'type': 'code'},
            {'label': _('Display Name'), 'value': self.object.display_name},
            {'label': _('Legal Name'), 'value': self.object.legal_name},
        ]
        context['cancel_url'] = reverse('shared:companies')
        return context

