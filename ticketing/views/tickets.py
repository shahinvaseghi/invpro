"""
Views for ticket management.

This module contains views for creating, editing, listing, and managing tickets.
"""
from typing import Dict, Any

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView

from .. import models
from .base import TicketingBaseView


class TicketListView(TicketingBaseView, ListView):
    """List view for tickets."""

    model = models.Ticket
    template_name = "ticketing/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 50

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Tickets")
        return context


class TicketCreateView(TicketingBaseView, CreateView):
    """View for creating a new ticket."""

    model = models.Ticket
    template_name = "ticketing/ticket_create.html"
    fields = ["template", "title", "description", "category", "priority"]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data with available templates or selected template."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Ticket")
        
        # Check if a template is selected
        template_id = self.request.GET.get("template_id")
        
        if template_id:
            # Show form for creating ticket with selected template
            try:
                selected_template = get_object_or_404(
                    models.TicketTemplate,
                    pk=template_id,
                    company_id=self.request.session.get("active_company_id"),
                    is_enabled=1
                )
                
                # Check permissions
                user = self.request.user
                has_permission = False
                
                if user.is_superuser:
                    has_permission = True
                else:
                    permissions = selected_template.permissions.filter(
                        is_enabled=1,
                        can_create=1
                    )
                    for perm in permissions:
                        if perm.user_id == user.id:
                            has_permission = True
                            break
                        if perm.group_id and user.groups.filter(id=perm.group_id).exists():
                            has_permission = True
                            break
                
                if has_permission:
                    context["selected_template"] = selected_template
                    fields = selected_template.fields.filter(is_enabled=1).prefetch_related('options').order_by("field_order")
                    
                    # Process fields to extract options for dropdown/radio fields
                    fields_with_options = []
                    for field in fields:
                        field_data = {
                            'field': field,
                            'options': []
                        }
                        
                        # Extract options from field_config
                        if field.field_type in ['dropdown', 'radio', 'checkbox', 'multi_select']:
                            field_config = field.field_config or {}
                            
                            print(f"🔵 [TICKET_CREATE] Field: {field.field_name} ({field.field_type})")
                            print(f"🔵 [TICKET_CREATE] Field config: {field_config}")
                            print(f"🔵 [TICKET_CREATE] Options source: {field_config.get('options_source')}")
                            print(f"🔵 [TICKET_CREATE] Has options: {bool(field_config.get('options'))}")
                            
                            # Check if manual options exist
                            if field_config.get('options_source') == 'manual' and field_config.get('options'):
                                print(f"🔵 [TICKET_CREATE] Loading manual options, count: {len(field_config['options'])}")
                                # Options from field_config
                                for opt in field_config['options']:
                                    if isinstance(opt, dict) and 'value' in opt and 'label' in opt:
                                        field_data['options'].append({
                                            'value': opt['value'],
                                            'label': opt['label'],
                                            'is_default': opt.get('is_default', False)
                                        })
                                        print(f"🔵 [TICKET_CREATE]   Added option: {opt.get('value')} = {opt.get('label')}")
                            elif field_config.get('options'):
                                print(f"🔵 [TICKET_CREATE] Loading options without options_source, count: {len(field_config['options'])}")
                                # Fallback: options without options_source
                                for opt in field_config['options']:
                                    if isinstance(opt, dict) and 'value' in opt and 'label' in opt:
                                        field_data['options'].append({
                                            'value': opt['value'],
                                            'label': opt['label'],
                                            'is_default': opt.get('is_default', False)
                                        })
                                        print(f"🔵 [TICKET_CREATE]   Added option: {opt.get('value')} = {opt.get('label')}")
                            else:
                                print(f"🔵 [TICKET_CREATE] No options in field_config, checking TicketTemplateFieldOption model")
                                # Fallback: use TicketTemplateFieldOption model
                                for opt in field.options.all():
                                    if opt.is_enabled == 1:
                                        field_data['options'].append({
                                            'value': opt.option_value,
                                            'label': opt.option_label,
                                            'is_default': opt.is_default == 1
                                        })
                                        print(f"🔵 [TICKET_CREATE]   Added option from model: {opt.option_value} = {opt.option_label}")
                            
                            print(f"🔵 [TICKET_CREATE] Final options count for {field.field_name}: {len(field_data['options'])}")
                        
                        fields_with_options.append(field_data)
                    
                    context["template_fields"] = fields_with_options
                else:
                    messages.error(self.request, _("You don't have permission to create tickets with this template."))
                    context["selected_template"] = None
            except Exception:
                messages.error(self.request, _("Template not found."))
                context["selected_template"] = None
        else:
            # Show template selection list
            context["selected_template"] = None
            
            # Get available templates for the user
            company_id = self.request.session.get("active_company_id")
            if company_id:
                # Get all enabled templates for this company
                all_templates = models.TicketTemplate.objects.filter(
                    company_id=company_id,
                    is_enabled=1
                ).order_by("sort_order", "name")
                
                # Filter templates by user permissions
                user = self.request.user
                available_templates = []
                
                for template in all_templates:
                    # Check if user has permission to create tickets with this template
                    has_permission = False
                    
                    # Check superuser
                    if user.is_superuser:
                        has_permission = True
                    else:
                        # Check template permissions
                        permissions = template.permissions.filter(
                            is_enabled=1,
                            can_create=1
                        )
                        
                        # Check if user or user's groups have permission
                        for perm in permissions:
                            if perm.user_id == user.id:
                                has_permission = True
                                break
                            if perm.group_id and user.groups.filter(id=perm.group_id).exists():
                                has_permission = True
                                break
                    
                    if has_permission:
                        available_templates.append(template)
                
                context["available_templates"] = available_templates
        
        return context

    def get_initial(self):
        """Set initial values for form."""
        initial = super().get_initial()
        template_id = self.request.GET.get("template_id")
        if template_id:
            initial['template'] = template_id
        return initial

    def form_valid(self, form):
        """Set reported_by to current user."""
        company_id = self.request.session.get("active_company_id")
        if company_id:
            form.instance.company_id = company_id
        form.instance.reported_by = self.request.user
        messages.success(self.request, _("Ticket created successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to ticket list."""
        return reverse_lazy("ticketing:ticket_list")


class TicketEditView(TicketingBaseView, UpdateView):
    """View for editing an existing ticket."""

    model = models.Ticket
    template_name = "ticketing/ticket_edit.html"
    fields = ["title", "description", "category", "priority", "status", "assigned_to"]

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Edit Ticket")
        return context

    def form_valid(self, form):
        """Handle form submission."""
        messages.success(self.request, _("Ticket updated successfully."))
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to ticket detail."""
        return reverse_lazy("ticketing:ticket_list")

