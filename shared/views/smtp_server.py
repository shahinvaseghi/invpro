"""
SMTP Server CRUD views for shared module.
"""
from typing import Any, Dict
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.models import SMTPServer
from shared.forms import SMTPServerForm
from shared.views.base import BaseUpdateView, BaseDetailView


class SMTPServerListView(FeaturePermissionRequiredMixin, ListView):
    """List all SMTP server configurations."""
    model = SMTPServer
    template_name = 'shared/smtp_server_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'shared.smtp_servers'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Get all SMTP servers."""
        return SMTPServer.objects.all().order_by('name')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context variables for generic_list template."""
        context = super().get_context_data(**kwargs)
        
        # Ensure object_list is properly set from page_obj if pagination is used
        if 'page_obj' in context and hasattr(context['page_obj'], 'object_list'):
            context['object_list'] = context['page_obj'].object_list
        elif 'object_list' in context and hasattr(context['object_list'], 'query'):
            context['object_list'] = list(context['object_list'])
        
        context['active_module'] = 'shared'
        context['page_title'] = _('SMTP Servers')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('SMTP Servers')},
        ]
        context['create_url'] = reverse_lazy('shared:smtp_server_create')
        context['create_button_text'] = _('Create SMTP Server')
        context['show_filters'] = False
        context['show_actions'] = True
        context['feature_code'] = 'shared.smtp_servers'
        context['detail_url_name'] = 'shared:smtp_server_detail'
        context['edit_url_name'] = 'shared:smtp_server_edit'
        context['delete_url_name'] = 'shared:smtp_server_delete'
        context['empty_state_title'] = _('No SMTP Servers Found')
        context['empty_state_message'] = _('No SMTP server configurations found. Create your first SMTP server to enable email notifications.')
        context['empty_state_icon'] = '📧'
        
        return context


class SMTPServerCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new SMTP server configuration."""
    model = SMTPServer
    form_class = SMTPServerForm
    template_name = 'shared/smtp_server_form.html'
    success_url = reverse_lazy('shared:smtp_servers')
    feature_code = 'shared.smtp_servers'
    required_action = 'create'
    
    def form_valid(self, form: SMTPServerForm) -> HttpResponseRedirect:
        """Auto-set created_by."""
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('SMTP server configuration created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Create SMTP Server')
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('SMTP Servers'), 'url': reverse_lazy('shared:smtp_servers')},
        ]
        context['cancel_url'] = reverse_lazy('shared:smtp_servers')
        return context


class SMTPServerUpdateView(BaseUpdateView):
    """Update an existing SMTP server configuration."""
    model = SMTPServer
    form_class = SMTPServerForm
    template_name = 'shared/smtp_server_form.html'
    success_url = reverse_lazy('shared:smtp_servers')
    feature_code = 'shared.smtp_servers'
    success_message = _('SMTP server configuration updated successfully.')
    
    def form_valid(self, form: SMTPServerForm) -> HttpResponseRedirect:
        """Handle password if empty."""
        # If password is empty and editing, keep existing password
        if not form.cleaned_data.get('password'):
            form.instance.password = self.object.password
        
        return super().form_valid(form)
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit SMTP Server')
    
    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('SMTP Servers'), 'url': reverse_lazy('shared:smtp_servers')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('shared:smtp_servers')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context


class SMTPServerDetailView(BaseDetailView):
    """Detail view for viewing SMTP servers (read-only)."""
    model = SMTPServer
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'shared.smtp_servers'
    required_action = 'view_own'
    auto_set_company = False  # SMTP servers are not company-scoped
    require_active_company = False  # SMTP servers are global
    permission_field = ''  # Skip permission filtering for SMTPServer model
    
    def get_queryset(self):
        """Get all SMTP servers."""
        queryset = SMTPServer.objects.all()
        queryset = queryset.select_related('created_by', 'edited_by')
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View SMTP Server')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        smtp_server = self.object
        
        context['detail_title'] = self.get_page_title()
        context['info_banner'] = [
            {'label': _('Name'), 'value': smtp_server.name, 'type': 'code'},
            {'label': _('Status'), 'value': smtp_server.is_enabled, 'type': 'badge'},
        ]
        
        # Server Configuration section
        config_fields = [
            {'label': _('Host'), 'value': smtp_server.host},
            {'label': _('Port'), 'value': str(smtp_server.port)},
            {'label': _('From Email'), 'value': smtp_server.from_email},
        ]
        if smtp_server.username:
            config_fields.append({'label': _('Username'), 'value': smtp_server.username})
        config_fields.append({
            'label': _('Use TLS'),
            'value': smtp_server.use_tls,
            'type': 'badge',
        })
        config_fields.append({
            'label': _('Use SSL'),
            'value': smtp_server.use_ssl,
            'type': 'badge',
        })
        
        context['detail_sections'] = [
            {
                'title': _('Server Configuration'),
                'fields': config_fields,
            },
        ]
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('shared:smtp_servers')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('shared:smtp_server_edit', kwargs={'pk': self.object.pk})


class SMTPServerDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete an SMTP server configuration."""
    model = SMTPServer
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('shared:smtp_servers')
    feature_code = 'shared.smtp_servers'
    required_action = 'delete_own'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['delete_title'] = _('Delete SMTP Server')
        context['confirmation_message'] = _('Are you sure you want to delete SMTP server "{name}"?').format(name=self.object.name)
        context['breadcrumbs'] = [
            {'label': _('Dashboard'), 'url': reverse_lazy('ui:dashboard')},
            {'label': _('SMTP Servers'), 'url': reverse_lazy('shared:smtp_servers')},
            {'label': _('Delete')},
        ]
        context['object_details'] = [
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Host'), 'value': self.object.host},
            {'label': _('Port'), 'value': self.object.port},
            {'label': _('From Email'), 'value': self.object.from_email},
        ]
        context['cancel_url'] = reverse_lazy('shared:smtp_servers')
        return context
    
    def delete(self, request, *args, **kwargs):
        """Delete the SMTP server and show success message."""
        messages.success(request, _('SMTP server configuration deleted successfully.'))
        return super().delete(request, *args, **kwargs)

