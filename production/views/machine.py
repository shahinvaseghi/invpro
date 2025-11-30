"""
Machine CRUD views for production module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from production.forms import MachineForm
from production.models import Machine


class MachineListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all machines for the active company.
    """
    model = Machine
    template_name = 'production/machines.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.machines'
    
    def get_queryset(self):
        """Filter machines by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return Machine.objects.none()
        
        queryset = Machine.objects.filter(
            company_id=active_company_id,
            is_enabled=1
        )
        
        # Search filter
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(public_code__icontains=search) | Q(name__icontains=search) | Q(name_en__icontains=search)
            )
        
        # Work center filter
        work_center_id = self.request.GET.get('work_center')
        if work_center_id:
            queryset = queryset.filter(work_center_id=work_center_id)
        
        # Status filter
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Try to select_related work_center if it exists
        try:
            queryset = queryset.select_related('work_center')
        except Exception:
            pass
        
        return queryset.order_by('public_code')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        if 'page_obj' in context and hasattr(context['page_obj'], 'object_list'):
            context['object_list'] = context['page_obj'].object_list
        elif 'object_list' in context and hasattr(context['object_list'], 'query'):
            context['object_list'] = list(context['object_list'])
        
        context['page_title'] = _('Machines')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Machines'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('production:machine_create')
        context['create_button_text'] = _('Create Machine')
        context['show_filters'] = True
        context['search_placeholder'] = _('Search by code or name')
        context['clear_filter_url'] = reverse_lazy('production:machines')
        context['show_actions'] = True
        context['edit_url_name'] = 'production:machine_edit'
        context['delete_url_name'] = 'production:machine_delete'
        context['empty_state_title'] = _('No Machines Found')
        context['empty_state_message'] = _('Start by adding your first machine.')
        context['empty_state_icon'] = '⚙️'
        context['print_enabled'] = True
        
        # Get work centers for filter
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if active_company_id:
            from production.models import WorkCenter
            context['work_centers'] = WorkCenter.objects.filter(
                company_id=active_company_id
            ).order_by('name')
        
        return context


class MachineCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new machine."""
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    success_url = reverse_lazy('production:machines')
    feature_code = 'production.machines'
    required_action = 'create'

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: MachineForm) -> HttpResponseRedirect:
        """Auto-set company and created_by."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Machine created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Machine')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Machines'), 'url': reverse_lazy('production:machines')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:machines')
        return context


class MachineUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing machine."""
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    success_url = reverse_lazy('production:machines')
    feature_code = 'production.machines'
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
            return Machine.objects.none()
        return Machine.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form: MachineForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Machine updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Machine')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Machines'), 'url': reverse_lazy('production:machines')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:machines')
        return context


class MachineDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a machine."""
    model = Machine
    success_url = reverse_lazy('production:machines')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'production.machines'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return Machine.objects.none()
        return Machine.objects.filter(company_id=active_company_id)
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete machine and show success message."""
        messages.success(self.request, _('Machine deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Machine')
        context['confirmation_message'] = _('Do you really want to delete this machine?')
        context['object_details'] = [
            {'label': _('Code'), 'value': f'<code>{self.object.public_code}</code>'},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Type'), 'value': str(self.object.machine_type)},
        ]
        if self.object.work_center:
            context['object_details'].append({'label': _('Work Center'), 'value': self.object.work_center.name})
        
        context['cancel_url'] = reverse_lazy('production:machines')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Machines'), 'url': reverse_lazy('production:machines')},
            {'label': _('Delete'), 'url': None},
        ]
        return context

