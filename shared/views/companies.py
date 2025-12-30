"""
Company CRUD views for shared module.
"""
from typing import Any, Dict, List, Optional
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from shared.models import Company, UserCompanyAccess
from shared.forms import CompanyForm
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
    BaseDetailView,
)


class CompanyListView(BaseListView):
    """
    List all companies that the current user has access to.
    """
    model = Company
    feature_code = 'shared.companies'
    search_fields = ['public_code', 'display_name', 'legal_name']
    filter_fields = ['is_enabled']
    default_status_filter = True
    default_order_by = ['public_code']
    
    def get_base_queryset(self) -> QuerySet:
        """Filter companies based on user access."""
        user_company_ids = UserCompanyAccess.objects.filter(
            user=self.request.user,
            is_enabled=1
        ).values_list('company_id', flat=True)
        
        return Company.objects.filter(id__in=user_company_ids)
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Companies')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Companies'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('shared:company_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Company')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Search by code or name')
    
    def get_clear_filter_url(self):
        """Return clear filter URL."""
        return reverse('shared:companies')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'shared:company_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'shared:company_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'shared:company_delete'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add additional context variables."""
        context = super().get_context_data(**kwargs)
        context['print_enabled'] = True
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


class CompanyCreateView(BaseCreateView):
    """Create a new company."""
    model = Company
    form_class = CompanyForm
    template_name = 'shared/company_form.html'
    success_url = reverse_lazy('shared:companies')
    feature_code = 'shared.companies'
    required_action = 'create'
    success_message = _('Company created successfully.')
    
    def form_valid(self, form: CompanyForm) -> HttpResponseRedirect:
        """Auto-set created_by and create UserCompanyAccess."""
        response = super().form_valid(form)
        
        # Create UserCompanyAccess for the creator
        UserCompanyAccess.objects.create(
            user=self.request.user,
            company=self.object,
            access_level_id=1,  # ADMIN level
            is_primary=1,  # Make it primary
            is_enabled=1
        )
        
        return response
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Companies'), 'url': reverse('shared:companies')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Company')
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:companies')


class CompanyUpdateView(BaseUpdateView):
    """Update an existing company."""
    model = Company
    form_class = CompanyForm
    template_name = 'shared/company_form.html'
    success_url = reverse_lazy('shared:companies')
    feature_code = 'shared.companies'
    required_action = 'edit_own'
    success_message = _('Company updated successfully.')
    
    def get_queryset(self) -> QuerySet:
        """Filter companies based on user access."""
        user_company_ids = UserCompanyAccess.objects.filter(
            user=self.request.user,
            is_enabled=1
        ).values_list('company_id', flat=True)
        return Company.objects.filter(id__in=user_company_ids)
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Companies'), 'url': reverse('shared:companies')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Company')
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:companies')


class CompanyDetailView(BaseDetailView):
    """Detail view for viewing companies (read-only)."""
    model = Company
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'shared.companies'
    required_action = 'view_own'
    
    @property
    def permission_field(self) -> Optional[str]:
        """Return None to skip permission filtering (we filter by UserCompanyAccess)."""
        return None
    
    def get_queryset(self) -> QuerySet:
        """Filter companies based on user access."""
        user_company_ids = UserCompanyAccess.objects.filter(
            user=self.request.user,
            is_enabled=1
        ).values_list('company_id', flat=True)
        return Company.objects.filter(id__in=user_company_ids).select_related('created_by', 'edited_by')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Companies'), 'url': reverse('shared:companies')},
            {'label': _('View'), 'url': None},
        ]
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Company')
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('shared:companies')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('shared:company_edit', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add detail sections for generic_detail.html."""
        context = super().get_context_data(**kwargs)
        
        # Set detail_title (used by generic_detail.html)
        context['detail_title'] = self.get_page_title()
        
        # Set info_banner (used by generic_detail.html)
        context['info_banner'] = [
            {'label': _('Code'), 'value': self.object.public_code, 'type': 'code'},
            {'label': _('Status'), 'value': self.object.is_enabled, 'type': 'badge'},
        ]
        
        # Set detail_sections (used by generic_detail.html)
        basic_fields = [
            {'label': _('Display Name'), 'value': self.object.display_name},
        ]
        if self.object.legal_name:
            basic_fields.append({'label': _('Legal Name'), 'value': self.object.legal_name})
        if self.object.tax_id:
            basic_fields.append({'label': _('Tax ID'), 'value': self.object.tax_id})
        
        context['detail_sections'] = [
            {
                'title': _('Basic Information'),
                'fields': basic_fields,
            },
        ]
        
        # Add address section if exists
        if self.object.address or self.object.city or self.object.state or self.object.country:
            address_fields = []
            if self.object.address:
                address_fields.append({'label': _('Address'), 'value': self.object.address})
            if self.object.city:
                address_fields.append({'label': _('City'), 'value': self.object.city})
            if self.object.state:
                address_fields.append({'label': _('State/Province'), 'value': self.object.state})
            if self.object.country:
                address_fields.append({'label': _('Country'), 'value': self.object.country})
            
            if address_fields:
                context['detail_sections'].append({
                    'title': _('Address Information'),
                    'fields': address_fields,
                })
        
        # Add contact section if exists
        contact_fields = []
        if self.object.phone_number:
            contact_fields.append({'label': _('Phone'), 'value': self.object.phone_number})
        if self.object.email:
            contact_fields.append({'label': _('Email'), 'value': self.object.email})
        if self.object.website:
            contact_fields.append({
                'label': _('Website'),
                'value': f"<a href='{self.object.website}' target='_blank'>{self.object.website}</a>",
                'type': 'custom'
            })
        
        if contact_fields:
            context['detail_sections'].append({
                'title': _('Contact Information'),
                'fields': contact_fields,
            })
        
        return context


class CompanyDeleteView(BaseDeleteView):
    """Delete a company."""
    model = Company
    success_url = reverse_lazy('shared:companies')
    feature_code = 'shared.companies'
    required_action = 'delete_own'
    success_message = _('Company deleted successfully.')
    
    def get_queryset(self) -> QuerySet:
        """Filter companies based on user access."""
        user_company_ids = UserCompanyAccess.objects.filter(
            user=self.request.user,
            is_enabled=1
        ).values_list('company_id', flat=True)
        return Company.objects.filter(id__in=user_company_ids)
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Companies'), 'url': reverse('shared:companies')},
            {'label': _('Delete'), 'url': None},
        ]
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Company')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this company?')
    
    def get_object_details(self) -> List[Dict[str, Any]]:
        """Return object details for display."""
        return [
            {'label': _('Code'), 'value': self.object.public_code, 'type': 'code'},
            {'label': _('Display Name'), 'value': self.object.display_name},
            {'label': _('Legal Name'), 'value': self.object.legal_name},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:companies')

