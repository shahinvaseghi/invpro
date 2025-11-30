"""
Personnel (Person) CRUD views for production module.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from production.forms import PersonForm
from production.models import Person


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
        """Filter personnel by active company and search/status filters."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return Person.objects.none()
        
        queryset = Person.objects.filter(
            company_id=active_company_id,
        ).select_related('company').prefetch_related('company_units').order_by('public_code')
        
        # Apply search filter
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(public_code__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(national_id__icontains=search)
            )
        
        # Apply status filter
        status = self.request.GET.get('status')
        if status == '1':
            queryset = queryset.filter(is_enabled=1)
        elif status == '0':
            queryset = queryset.filter(is_enabled=0)
        
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Personnel')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Personnel'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('production:person_create')
        context['create_button_text'] = _('Create Person +')
        context['search_placeholder'] = _('Search by code, name, or national ID...')
        context['show_filters'] = True
        context['status_filter'] = True  # Enable status filter
        context['clear_filter_url'] = reverse_lazy('production:personnel')
        context['table_headers'] = [
            _('Code'),
            _('Name'),
            _('National ID'),
            _('Company Units'),
            _('Status'),
        ]
        context['show_actions'] = True
        context['edit_url_name'] = 'production:person_edit'
        context['delete_url_name'] = 'production:person_delete'
        context['empty_state_title'] = _('No Personnel Found')
        context['empty_state_message'] = _('Create your first person to get started.')
        context['empty_state_icon'] = '👤'
        context['print_enabled'] = True
        return context


class PersonCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new person."""
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
    required_action = 'create'

    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def form_valid(self, form: PersonForm) -> HttpResponseRedirect:
        """Auto-set company and created_by."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Person created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Person')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Personnel'), 'url': reverse_lazy('production:personnel')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:personnel')
        return context


class PersonUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing person."""
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
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
            return Person.objects.none()
        return Person.objects.filter(company_id=active_company_id)
    
    def form_valid(self, form: PersonForm) -> HttpResponseRedirect:
        """Auto-set edited_by."""
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Person updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Person')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Personnel'), 'url': reverse_lazy('production:personnel')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:personnel')
        return context


class PersonDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a person."""
    model = Person
    success_url = reverse_lazy('production:personnel')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'production.personnel'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return Person.objects.none()
        return Person.objects.filter(company_id=active_company_id)
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete person and show success message."""
        messages.success(self.request, _('Person deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Person')
        context['confirmation_message'] = _('Are you sure you want to delete this person?')
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.public_code},
            {'label': _('Name'), 'value': f"{self.object.first_name} {self.object.last_name}"},
            {'label': _('National ID'), 'value': self.object.national_id or '-'},
            {'label': _('Email'), 'value': self.object.email or '-'},
        ]
        context['cancel_url'] = reverse_lazy('production:personnel')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Personnel'), 'url': reverse_lazy('production:personnel')},
            {'label': _('Delete'), 'url': None},
        ]
        return context

