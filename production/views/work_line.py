"""
WorkLine CRUD views for production module.
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
from production.forms import WorkLineForm
from production.models import WorkLine


class WorkLineListView(BaseListView):
    """List all work lines for the active company."""
    model = WorkLine
    template_name = 'production/work_lines.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.work_lines'
    required_action = 'view_own'
    active_module = 'production'
    default_status_filter = False
    default_order_by = ['warehouse__name', 'sort_order', 'public_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        try:
            return ['warehouse']
        except Exception:
            return []
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        return ['personnel', 'machines']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Work Lines')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Work Lines'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('production:work_line_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('+ Create Work Line')
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name."""
        return 'production:work_line_detail'
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name."""
        return 'production:work_line_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'production:work_line_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Work Lines Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first work line.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '🏭'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = []  # Overridden in template
        return context


class WorkLineCreateView(BaseCreateView):
    """Create a new work line."""
    model = WorkLine
    form_class = WorkLineForm
    template_name = 'production/work_line_form.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'create'
    active_module = 'production'
    success_message = _('Work line created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: WorkLineForm):
        """Auto-set company and created_by, save M2M relationships."""
        response = super().form_valid(form)
        # Save Many-to-Many relationships
        form.save_m2m()
        return response
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Work Line')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Work Lines'), 'url': reverse_lazy('production:work_lines')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic template."""
        context = super().get_context_data(**kwargs)
        context['form_id'] = 'work-line-form'
        return context


class WorkLineUpdateView(BaseUpdateView):
    """Update an existing work line."""
    model = WorkLine
    form_class = WorkLineForm
    template_name = 'production/work_line_form.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'edit_own'
    active_module = 'production'
    success_message = _('Work line updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def form_valid(self, form: WorkLineForm):
        """Auto-set edited_by, save M2M relationships."""
        response = super().form_valid(form)
        # Save Many-to-Many relationships
        form.save_m2m()
        return response
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Work Line')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Work Lines'), 'url': reverse_lazy('production:work_lines')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic template."""
        context = super().get_context_data(**kwargs)
        context['form_id'] = 'work-line-form'
        return context


class WorkLineDetailView(BaseDetailView):
    """Detail view for viewing work lines (read-only)."""
    model = WorkLine
    template_name = 'production/work_line_detail.html'
    context_object_name = 'work_line'
    feature_code = 'production.work_lines'
    required_action = 'view_own'
    active_module = 'production'
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        try:
            queryset = queryset.select_related('warehouse', 'created_by', 'edited_by')
        except Exception:
            queryset = queryset.select_related('created_by', 'edited_by')
        queryset = queryset.prefetch_related('personnel', 'machines')
        return queryset
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('production:work_lines')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('production:work_line_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class WorkLineDeleteView(BaseDeleteView):
    """Delete a work line."""
    model = WorkLine
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'delete_own'
    active_module = 'production'
    success_message = _('Work line deleted successfully.')
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        try:
            queryset = queryset.select_related('warehouse')
        except Exception:
            pass
        return queryset
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Work Line')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete this work line? This action cannot be undone.')
    
    def get_object_details(self) -> List[Dict[str, str]]:
        """Return object details for confirmation."""
        details = [
            {'label': _('Code'), 'value': self.object.public_code},
            {'label': _('Name'), 'value': self.object.name},
        ]
        if hasattr(self.object, 'warehouse') and self.object.warehouse:
            details.append({'label': _('Warehouse'), 'value': self.object.warehouse.name})
        return details
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Work Lines'), 'url': reverse_lazy('production:work_lines')},
            {'label': _('Delete'), 'url': None},
        ]

