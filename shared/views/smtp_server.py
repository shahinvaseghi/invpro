"""
SMTP Server CRUD views for shared module.
"""
from typing import Any, Dict
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.models import SMTPServer
from shared.forms import SMTPServerForm


class SMTPServerListView(FeaturePermissionRequiredMixin, ListView):
    """List all SMTP server configurations."""
    model = SMTPServer
    template_name = 'shared/smtp_server_list.html'
    context_object_name = 'smtp_servers'
    paginate_by = 50
    feature_code = 'shared.smtp_servers'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Get all SMTP servers."""
        return SMTPServer.objects.all().order_by('name')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
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
        return context


class SMTPServerUpdateView(FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing SMTP server configuration."""
    model = SMTPServer
    form_class = SMTPServerForm
    template_name = 'shared/smtp_server_form.html'
    success_url = reverse_lazy('shared:smtp_servers')
    feature_code = 'shared.smtp_servers'
    required_action = 'edit_own'
    
    def form_valid(self, form: SMTPServerForm) -> HttpResponseRedirect:
        """Auto-set edited_by and handle password."""
        form.instance.edited_by = self.request.user
        
        # If password is empty and editing, keep existing password
        if not form.cleaned_data.get('password'):
            form.instance.password = self.object.password
        
        messages.success(self.request, _('SMTP server configuration updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        context['form_title'] = _('Edit SMTP Server')
        return context


class SMTPServerDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete an SMTP server configuration."""
    model = SMTPServer
    template_name = 'shared/smtp_server_confirm_delete.html'
    success_url = reverse_lazy('shared:smtp_servers')
    context_object_name = 'smtp_server'
    feature_code = 'shared.smtp_servers'
    required_action = 'delete_own'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'shared'
        return context
    
    def delete(self, request, *args, **kwargs):
        """Delete the SMTP server and show success message."""
        messages.success(request, _('SMTP server configuration deleted successfully.'))
        return super().delete(request, *args, **kwargs)

