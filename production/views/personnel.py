"""
Personnel (Person) CRUD views for production module.
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
from production.forms import PersonForm
from production.models import Person


class PersonnelListView(BaseListView):
    """List all personnel (Person objects) for the active company."""
    model = Person
    template_name = 'production/personnel.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.personnel'
    active_module = 'production'
    search_fields = ['public_code', 'first_name', 'last_name', 'national_id']
    default_status_filter = True
    default_order_by = ['public_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['company']
    
    def get_prefetch_related(self) -> List[str]:
        """Return list of fields to prefetch_related."""
        return ['company_units']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Personnel')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Personnel'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('production:person_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Person +')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Search by code, name, or national ID...')
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name."""
        return 'production:person_detail'
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name."""
        return 'production:person_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'production:person_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Personnel Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Create your first person to get started.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '👤'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = [
            _('Code'),
            _('Name'),
            _('National ID'),
            _('Company Units'),
            _('Status'),
        ]
        context['print_enabled'] = True
        return context


class PersonCreateView(BaseCreateView):
    """Create a new person."""
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
    required_action = 'create'
    active_module = 'production'
    success_message = _('Person created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Person')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Personnel'), 'url': reverse_lazy('production:personnel')},
            {'label': _('Create'), 'url': None},
        ]


class PersonUpdateView(BaseUpdateView):
    """Update an existing person."""
    model = Person
    form_class = PersonForm
    template_name = 'production/person_form.html'
    success_url = reverse_lazy('production:personnel')
    feature_code = 'production.personnel'
    required_action = 'edit_own'
    active_module = 'production'
    success_message = _('Person updated successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Person')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Personnel'), 'url': reverse_lazy('production:personnel')},
            {'label': _('Edit'), 'url': None},
        ]


class PersonDetailView(BaseDetailView):
    """Detail view for viewing persons (read-only)."""
    model = Person
    template_name = 'production/person_detail.html'
    context_object_name = 'person'
    feature_code = 'production.personnel'
    required_action = 'view_own'
    active_module = 'production'
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'user',
            'created_by',
            'edited_by',
        ).prefetch_related('company_units')
        return queryset
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('production:personnel')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('production:person_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class PersonDeleteView(BaseDeleteView):
    """Delete a person."""
    model = Person
    success_url = reverse_lazy('production:personnel')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'production.personnel'
    required_action = 'delete_own'
    active_module = 'production'
    success_message = _('Person deleted successfully.')
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Person')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete this person?')
    
    def get_object_details(self) -> List[Dict[str, str]]:
        """Return object details for confirmation."""
        return [
            {'label': _('Code'), 'value': self.object.public_code},
            {'label': _('Name'), 'value': f"{self.object.first_name} {self.object.last_name}"},
            {'label': _('National ID'), 'value': self.object.national_id or '-'},
            {'label': _('Email'), 'value': self.object.email or '-'},
        ]
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Personnel'), 'url': reverse_lazy('production:personnel')},
            {'label': _('Delete'), 'url': None},
        ]

