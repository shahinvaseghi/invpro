"""
Process CRUD views for production module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from production.forms import ProcessForm
from production.models import Process


class ProcessListView(FeaturePermissionRequiredMixin, ListView):
    """List all processes for the active company."""
    model = Process
    template_name = 'production/processes.html'
    context_object_name = 'processes'
    paginate_by = 50
    feature_code = 'production.processes'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter processes by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return Process.objects.none()
        
        queryset = Process.objects.filter(
            company_id=active_company_id
        )
        
        queryset = queryset.select_related(
            'finished_item',
            'bom',
            'approved_by',  # Now FK to User, not Person
        ).prefetch_related('work_lines')
        
        return queryset.order_by('finished_item__name', 'revision', 'sort_order')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


class ProcessCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new process."""
    model = Process
    form_class = ProcessForm
    template_name = 'production/process_form.html'
    success_url = reverse_lazy('production:processes')
    feature_code = 'production.processes'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id and request to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        kwargs['request'] = self.request
        return kwargs
    
    def form_valid(self, form: ProcessForm) -> HttpResponseRedirect:
        """Auto-set company, created_by, finished_item, save M2M relationships."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        # Set finished_item from BOM
        if form.cleaned_data.get('bom'):
            form.instance.finished_item = form.cleaned_data['bom'].finished_item
        response = super().form_valid(form)
        # Save Many-to-Many relationships
        form.save_m2m()
        messages.success(self.request, _('Process created successfully.'))
        return response
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Create Process')
        return context


class ProcessUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing process."""
    model = Process
    form_class = ProcessForm
    template_name = 'production/process_form.html'
    success_url = reverse_lazy('production:processes')
    feature_code = 'production.processes'
    required_action = 'edit_own'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id and request to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        kwargs['request'] = self.request
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return Process.objects.none()
        return Process.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form: ProcessForm) -> HttpResponseRedirect:
        """Auto-set edited_by, finished_item, save M2M relationships."""
        form.instance.edited_by = self.request.user
        # Set finished_item from BOM if changed
        if form.cleaned_data.get('bom'):
            form.instance.finished_item = form.cleaned_data['bom'].finished_item
        response = super().form_valid(form)
        # Save Many-to-Many relationships
        form.save_m2m()
        messages.success(self.request, _('Process updated successfully.'))
        return response
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Edit Process')
        return context


class ProcessDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a process."""
    model = Process
    template_name = 'production/process_confirm_delete.html'
    success_url = reverse_lazy('production:processes')
    feature_code = 'production.processes'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return Process.objects.none()
        return Process.objects.filter(company_id=active_company_id)
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete process and show success message."""
        messages.success(self.request, _('Process deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context

