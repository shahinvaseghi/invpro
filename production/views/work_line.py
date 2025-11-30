"""
WorkLine CRUD views for production module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from production.forms import WorkLineForm
from production.models import WorkLine


class WorkLineListView(FeaturePermissionRequiredMixin, ListView):
    """List all work lines for the active company."""
    model = WorkLine
    template_name = 'production/work_lines.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.work_lines'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter work lines by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return WorkLine.objects.none()
        
        queryset = WorkLine.objects.filter(
            company_id=active_company_id
        )
        
        # Try to select_related warehouse if inventory module is installed
        try:
            queryset = queryset.select_related('warehouse')
        except Exception:
            pass
        
        queryset = queryset.prefetch_related('personnel', 'machines')
        
        return queryset.order_by('warehouse__name', 'sort_order', 'public_code')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Work Lines')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Work Lines'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('production:work_line_create')
        context['create_button_text'] = _('+ Create Work Line')
        context['table_headers'] = []  # Overridden in template
        context['show_actions'] = True
        context['edit_url_name'] = 'production:work_line_edit'
        context['delete_url_name'] = 'production:work_line_delete'
        context['empty_state_title'] = _('No Work Lines Found')
        context['empty_state_message'] = _('Start by creating your first work line.')
        context['empty_state_icon'] = '🏭'
        return context


class WorkLineCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new work line."""
    model = WorkLine
    form_class = WorkLineForm
    template_name = 'production/work_line_form.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: WorkLineForm) -> HttpResponseRedirect:
        """Auto-set company and created_by, save M2M relationships."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        # Save Many-to-Many relationships
        form.save_m2m()
        messages.success(self.request, _('Work line created successfully.'))
        return response
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form title and context for generic template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Work Line')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Work Lines'), 'url': reverse_lazy('production:work_lines')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:work_lines')
        context['form_id'] = 'work-line-form'
        return context


class WorkLineUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing work line."""
    model = WorkLine
    form_class = WorkLineForm
    template_name = 'production/work_line_form.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'edit_own'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return WorkLine.objects.none()
        return WorkLine.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form: WorkLineForm) -> HttpResponseRedirect:
        """Auto-set edited_by, save M2M relationships."""
        form.instance.edited_by = self.request.user
        response = super().form_valid(form)
        # Save Many-to-Many relationships
        form.save_m2m()
        messages.success(self.request, _('Work line updated successfully.'))
        return response
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add form title and context for generic template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Work Line')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Work Lines'), 'url': reverse_lazy('production:work_lines')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:work_lines')
        context['form_id'] = 'work-line-form'
        return context


class WorkLineDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a work line."""
    model = WorkLine
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('production:work_lines')
    feature_code = 'production.work_lines'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return WorkLine.objects.none()
        try:
            return WorkLine.objects.filter(company_id=active_company_id).select_related('warehouse')
        except Exception:
            return WorkLine.objects.filter(company_id=active_company_id)
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete work line and show success message."""
        messages.success(self.request, _('Work line deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Work Line')
        context['confirmation_message'] = _('Are you sure you want to delete this work line? This action cannot be undone.')
        
        object_details = [
            {'label': _('Code'), 'value': self.object.public_code},
            {'label': _('Name'), 'value': self.object.name},
        ]
        
        if hasattr(self.object, 'warehouse') and self.object.warehouse:
            object_details.append({'label': _('Warehouse'), 'value': self.object.warehouse.name})
        
        context['object_details'] = object_details
        context['cancel_url'] = reverse_lazy('production:work_lines')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Work Lines'), 'url': reverse_lazy('production:work_lines')},
            {'label': _('Delete'), 'url': None},
        ]
        return context

