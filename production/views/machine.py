"""
Machine CRUD views for production module.
"""
from typing import Any, Dict, Optional, List
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDetailView,
    BaseDeleteView,
)
from production.forms import MachineForm
from production.models import Machine


class MachineListView(BaseListView):
    """List all machines for the active company."""
    model = Machine
    template_name = 'production/machines.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.machines'
    active_module = 'production'
    search_fields = ['public_code', 'name', 'name_en']
    default_status_filter = False  # Custom status filter
    default_order_by = ['public_code']
    
    def get_base_queryset(self):
        """Get base queryset with is_enabled filter."""
        return self.model.objects.filter(is_enabled=1)
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        try:
            return ['work_center']
        except Exception:
            return []
    
    def apply_custom_filters(self, queryset):
        """Apply custom filters (work_center, status)."""
        # Work center filter
        work_center_id = self.request.GET.get('work_center')
        if work_center_id:
            queryset = queryset.filter(work_center_id=work_center_id)
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Machines')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Machines'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('production:machine_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Machine')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Search by code or name')
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name."""
        return 'production:machine_detail'
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name."""
        return 'production:machine_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'production:machine_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Machines Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by adding your first machine.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '⚙️'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['print_enabled'] = True
        
        # Get work centers for filter
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if active_company_id:
            from production.models import WorkCenter
            context['work_centers'] = WorkCenter.objects.filter(
                company_id=active_company_id
            ).order_by('name')
        
        return context


class MachineCreateView(BaseCreateView):
    """Create a new machine."""
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    success_url = reverse_lazy('production:machines')
    feature_code = 'production.machines'
    required_action = 'create'
    active_module = 'production'
    success_message = _('Machine created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Machine')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Machines'), 'url': reverse_lazy('production:machines')},
            {'label': _('Create'), 'url': None},
        ]


class MachineUpdateView(BaseUpdateView):
    """Update an existing machine."""
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    success_url = reverse_lazy('production:machines')
    feature_code = 'production.machines'
    required_action = 'edit_own'
    active_module = 'production'
    success_message = _('Machine updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Machine')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Machines'), 'url': reverse_lazy('production:machines')},
            {'label': _('Edit'), 'url': None},
        ]


class MachineDetailView(BaseDetailView):
    """Detail view for viewing machines (read-only)."""
    model = Machine
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'production.machines'
    required_action = 'view_own'
    active_module = 'production'
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'work_center',
            'created_by',
            'edited_by',
        )
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Machine')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        machine = self.object
        
        context['detail_title'] = self.get_page_title()
        context['info_banner'] = [
            {'label': _('Code'), 'value': machine.public_code, 'type': 'code'},
            {'label': _('Status'), 'value': machine.is_enabled, 'type': 'badge'},
            {'label': _('Machine Status'), 'value': machine.get_status_display()},
        ]
        
        # Basic Information section
        basic_fields = [
            {'label': _('Name'), 'value': machine.name},
        ]
        if machine.name_en:
            basic_fields.append({'label': _('Name (EN)'), 'value': machine.name_en})
        basic_fields.append({'label': _('Machine Type'), 'value': machine.machine_type})
        if machine.work_center:
            basic_fields.append({
                'label': _('Work Center'),
                'value': machine.work_center.name,
            })
        if machine.manufacturer:
            basic_fields.append({'label': _('Manufacturer'), 'value': machine.manufacturer})
        if machine.model_number:
            basic_fields.append({'label': _('Model Number'), 'value': machine.model_number})
        if machine.serial_number:
            basic_fields.append({'label': _('Serial Number'), 'value': machine.serial_number})
        if machine.purchase_date:
            basic_fields.append({'label': _('Purchase Date'), 'value': machine.purchase_date})
        if machine.installation_date:
            basic_fields.append({'label': _('Installation Date'), 'value': machine.installation_date})
        if machine.description:
            basic_fields.append({'label': _('Description'), 'value': machine.description})
        
        detail_sections = [
            {
                'title': _('Basic Information'),
                'fields': basic_fields,
            },
        ]
        
        # Maintenance Information section
        if machine.last_maintenance_date or machine.next_maintenance_date:
            maintenance_fields = []
            if machine.last_maintenance_date:
                maintenance_fields.append({
                    'label': _('Last Maintenance Date'),
                    'value': machine.last_maintenance_date,
                })
            if machine.next_maintenance_date:
                maintenance_fields.append({
                    'label': _('Next Maintenance Date'),
                    'value': machine.next_maintenance_date,
                })
            if maintenance_fields:
                detail_sections.append({
                    'title': _('Maintenance Information'),
                    'fields': maintenance_fields,
                })
        
        # Notes section
        if machine.notes:
            detail_sections.append({
                'title': _('Notes'),
                'fields': [
                    {'label': _('Notes'), 'value': machine.notes},
                ],
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('production:machines')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('production:machine_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class MachineDeleteView(BaseDeleteView):
    """Delete a machine."""
    model = Machine
    success_url = reverse_lazy('production:machines')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'production.machines'
    required_action = 'delete_own'
    active_module = 'production'
    success_message = _('Machine deleted successfully.')
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Machine')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Do you really want to delete this machine?')
    
    def get_object_details(self) -> List[Dict[str, str]]:
        """Return object details for confirmation."""
        details = [
            {'label': _('Code'), 'value': f'<code>{self.object.public_code}</code>'},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Type'), 'value': str(self.object.machine_type)},
        ]
        if self.object.work_center:
            details.append({'label': _('Work Center'), 'value': self.object.work_center.name})
        return details
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Machines'), 'url': reverse_lazy('production:machines')},
            {'label': _('Delete'), 'url': None},
        ]

