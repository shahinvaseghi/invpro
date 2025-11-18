"""
Views for production module.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from .forms import MachineForm, PersonForm
from .models import Machine, Person


class PersonnelListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all personnel (Person objects) for the active company.
    """
    model = Person
    template_name = 'production/personnel.html'
    context_object_name = 'personnel'
    paginate_by = 50
    feature_code = 'production.personnel'
    
    def get_queryset(self):
        """Filter personnel by active company."""
        active_company_id = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return Person.objects.none()
        
        return Person.objects.filter(
            company_id=active_company_id,
            is_enabled=1
        ).select_related('company').prefetch_related('company_units').order_by('public_code')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


class PersonCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new person."""
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
    required_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        # Auto-set company and created_by
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Person created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Create Person')
        return context


class PersonUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing person."""
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
    required_action = 'edit_own'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Person.objects.none()
        return Person.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form):
        # Auto-set edited_by
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Person updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Edit Person')
        return context


class PersonDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a person."""
    model = Person
    success_url = reverse_lazy('production:personnel')
    template_name = 'production/person_confirm_delete.html'
    feature_code = 'production.personnel'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Person.objects.none()
        return Person.objects.filter(company_id=active_company_id)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Person deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context


class MachineListView(FeaturePermissionRequiredMixin, ListView):
    """
    List all machines for the active company.
    """
    model = Machine
    template_name = 'production/machines.html'
    context_object_name = 'machines'
    paginate_by = 50
    feature_code = 'production.machines'
    
    def get_queryset(self):
        """Filter machines by active company."""
        active_company_id = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return Machine.objects.none()
        
        queryset = Machine.objects.filter(
            company_id=active_company_id,
            is_enabled=1
        ).select_related('company', 'work_center').order_by('public_code')
        
        # Filter by work center if provided
        work_center_id = self.request.GET.get('work_center')
        if work_center_id:
            queryset = queryset.filter(work_center_id=work_center_id)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        from .models import WorkCenter
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            context['work_centers'] = WorkCenter.objects.filter(company_id=active_company_id, is_enabled=1)
        return context


class MachineCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new machine."""
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    success_url = reverse_lazy('production:machines')
    feature_code = 'production.machines'
    required_action = 'create'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form):
        # Auto-set company and created_by
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Machine created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Create Machine')
        return context


class MachineUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing machine."""
    model = Machine
    form_class = MachineForm
    template_name = 'production/machine_form.html'
    success_url = reverse_lazy('production:machines')
    feature_code = 'production.machines'
    required_action = 'edit_own'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Machine.objects.none()
        return Machine.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form):
        # Auto-set edited_by
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Machine updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['form_title'] = _('Edit Machine')
        return context


class MachineDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a machine."""
    model = Machine
    success_url = reverse_lazy('production:machines')
    template_name = 'production/machine_confirm_delete.html'
    feature_code = 'production.machines'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id = self.request.session.get('active_company_id')
        if not active_company_id:
            return Machine.objects.none()
        return Machine.objects.filter(company_id=active_company_id)
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, _('Machine deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        return context
