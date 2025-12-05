"""
CompanyUnit CRUD views for shared module.
"""
from typing import Any, Dict, List, Optional
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from shared.models import CompanyUnit
from shared.forms import CompanyUnitForm
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
    BaseDetailView,
)


class CompanyUnitListView(BaseListView):
    """
    List all company units for the active company.
    """
    model = CompanyUnit
    feature_code = 'shared.company_units'
    search_fields = ['public_code', 'name']
    filter_fields = ['is_enabled']
    default_status_filter = True
    default_order_by = ['public_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['parent_unit']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Company Units')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Company Units'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse('shared:company_unit_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Unit')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Search by code or name')
    
    def get_clear_filter_url(self):
        """Return clear filter URL."""
        return reverse('shared:company_units')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'shared:company_unit_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'shared:company_unit_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'shared:company_unit_delete'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add additional context variables."""
        context = super().get_context_data(**kwargs)
        context['print_enabled'] = True
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


class CompanyUnitCreateView(BaseCreateView):
    """Create a new company unit."""
    model = CompanyUnit
    form_class = CompanyUnitForm
    template_name = 'shared/company_unit_form.html'
    success_url = reverse_lazy('shared:company_units')
    feature_code = 'shared.company_units'
    required_action = 'create'
    success_message = _('Company unit created successfully.')

    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Company Units'), 'url': reverse('shared:company_units')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Company Unit')
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:company_units')


class CompanyUnitUpdateView(BaseUpdateView):
    """Update existing company unit."""
    model = CompanyUnit
    form_class = CompanyUnitForm
    template_name = 'shared/company_unit_form.html'
    success_url = reverse_lazy('shared:company_units')
    feature_code = 'shared.company_units'
    required_action = 'edit_own'
    success_message = _('Company unit updated successfully.')
    
    def get_queryset(self) -> QuerySet:
        """Filter by active company."""
        queryset = super().get_queryset()
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return CompanyUnit.objects.none()
        return queryset.filter(company_id=active_company_id)

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        # Use object's company_id for parent_unit filtering
        if self.object:
            kwargs['company_id'] = self.object.company_id
        return kwargs

    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Company Units'), 'url': reverse('shared:company_units')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Company Unit')
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:company_units')


class CompanyUnitDetailView(BaseDetailView):
    """Detail view for viewing company units (read-only)."""
    model = CompanyUnit
    # Use generic_detail.html (default in BaseDetailView)
    context_object_name = 'unit'
    feature_code = 'shared.company_units'
    required_action = 'view_own'
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['parent_unit', 'company', 'created_by', 'edited_by']
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        return ['child_units']
    
    def get_queryset(self) -> QuerySet:
        """Filter by active company."""
        queryset = super().get_queryset()
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return CompanyUnit.objects.none()
        return queryset.filter(company_id=active_company_id)
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Company Unit')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Company Units'), 'url': reverse('shared:company_units')},
            {'label': _('View'), 'url': None},
        ]
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('shared:company_units')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('shared:company_unit_edit', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add detail sections for generic_detail.html."""
        context = super().get_context_data(**kwargs)
        
        # Set detail_title (used by generic_detail.html)
        context['detail_title'] = self.get_page_title()
        
        # Set info_banner (used by generic_detail.html)
        context['info_banner'] = [
            {'label': _('Code'), 'value': self.object.public_code, 'type': 'code'},
            {'label': _('Status'), 'value': self.object.is_enabled, 'type': 'badge',
             'true_label': _('Active'), 'false_label': _('Inactive')},
        ]
        
        # Set detail_sections (used by generic_detail.html)
        context['detail_sections'] = [
            {
                'title': _('Basic Information'),
                'type': 'fields',
                'fields': [
                    {'label': _('Unit Name'), 'value': self.object.name},
                    {'label': _('Unit Name (English)'), 'value': self.object.name_en or '-'},
                    {'label': _('Parent Unit'), 'value': self.object.parent_unit.name if self.object.parent_unit else '-'},
                    {'label': _('Description'), 'value': self.object.description or '-'},
                ],
            },
        ]
        
        # Add notes section if exists
        if self.object.notes:
            context['detail_sections'].append({
                'title': _('Notes'),
                'type': 'fields',
                'fields': [
                    {'label': _('Notes'), 'value': self.object.notes},
                ],
            })
        
        # Add audit information
        audit_fields = []
        if self.object.created_by:
            audit_fields.append({'label': _('Created By'), 'value': self.object.created_by.get_full_name() or self.object.created_by.username})
        if self.object.created_at:
            audit_fields.append({'label': _('Created At'), 'value': self.object.created_at, 'type': 'date'})
        if self.object.edited_by:
            audit_fields.append({'label': _('Edited By'), 'value': self.object.edited_by.get_full_name() or self.object.edited_by.username})
        if self.object.edited_at:
            audit_fields.append({'label': _('Last Updated'), 'value': self.object.edited_at, 'type': 'date'})
        
        if audit_fields:
            context['detail_sections'].append({
                'title': _('Audit Information'),
                'type': 'fields',
                'fields': audit_fields,
            })
        
        return context


class CompanyUnitDeleteView(BaseDeleteView):
    """Delete a company unit."""
    model = CompanyUnit
    success_url = reverse_lazy('shared:company_units')
    feature_code = 'shared.company_units'
    required_action = 'delete_own'
    success_message = _('Company unit deleted successfully.')
    
    def get_queryset(self) -> QuerySet:
        """Filter by active company."""
        queryset = super().get_queryset()
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return CompanyUnit.objects.none()
        return queryset.filter(company_id=active_company_id)

    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
            {'label': _('Company Units'), 'url': reverse('shared:company_units')},
            {'label': _('Delete'), 'url': None},
        ]
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Company Unit')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete unit "{name}"?').format(name=self.object.name)
    
    def get_object_details(self) -> List[Dict[str, Any]]:
        """Return object details for display."""
        return [
            {'label': _('Code'), 'value': self.object.public_code, 'type': 'code'},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Parent Unit'), 'value': self.object.parent_unit.name if self.object.parent_unit else '-'},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse('shared:company_units')

