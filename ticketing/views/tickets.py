"""
Views for ticket management.

This module contains views for creating, editing, listing, and managing tickets.
"""
from typing import Dict, Any

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from .. import models
from .base import TicketingBaseView
from shared.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDetailView,
    EditLockProtectedMixin,
)


class TicketListView(BaseListView):
    """List view for tickets."""

    model = models.Ticket
    template_name = "ticketing/ticket_list.html"
    context_object_name = "tickets"
    paginate_by = 50
    feature_code = "ticketing.tickets"
    required_action = "view_all"
    active_module = "ticketing"

    def get_page_title(self) -> str:
        """Return page title."""
        return _("Tickets")

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return "ticketing:ticket_detail"

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return "ticketing:ticket_edit"


class TicketCreateView(BaseCreateView):
    """View for creating a new ticket."""

    model = models.Ticket
    template_name = "ticketing/ticket_create.html"
    fields = ["template", "title", "description", "category", "priority"]
    feature_code = "ticketing.tickets"
    required_action = "create"
    active_module = "ticketing"
    success_message = _("Ticket created successfully.")

    def get_form_title(self) -> str:
        """Return form title."""
        return _("Create Ticket")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data with available templates or selected template."""
        context = super().get_context_data(**kwargs)
        
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
                            
                            # Check if manual options exist
                            if field_config.get('options_source') == 'manual' and field_config.get('options'):
                                # Options from field_config
                                for opt in field_config['options']:
                                    if isinstance(opt, dict) and 'value' in opt and 'label' in opt:
                                        field_data['options'].append({
                                            'value': opt['value'],
                                            'label': opt['label'],
                                            'is_default': opt.get('is_default', False)
                                        })
                            elif field_config.get('options'):
                                # Fallback: options without options_source
                                for opt in field_config['options']:
                                    if isinstance(opt, dict) and 'value' in opt and 'label' in opt:
                                        field_data['options'].append({
                                            'value': opt['value'],
                                            'label': opt['label'],
                                            'is_default': opt.get('is_default', False)
                                        })
                            else:
                                # Fallback: use TicketTemplateFieldOption model
                                for opt in field.options.all():
                                    if opt.is_enabled == 1:
                                        field_data['options'].append({
                                            'value': opt.option_value,
                                            'label': opt.option_label,
                                            'is_default': opt.is_default == 1
                                        })
                        
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
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to ticket list."""
        return reverse_lazy("ticketing:ticket_list")


class TicketDetailView(BaseDetailView):
    """Detail view for viewing tickets (read-only)."""
    model = models.Ticket
    template_name = "ticketing/ticket_detail.html"
    context_object_name = "ticket"
    feature_code = "ticketing.tickets"
    required_action = "view_all"
    active_module = "ticketing"
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        company_id = self.request.session.get("active_company_id")
        if not company_id:
            return models.Ticket.objects.none()
        queryset = models.Ticket.objects.filter(company_id=company_id)
        queryset = queryset.select_related(
            'template',
            'category',
            'subcategory',
            'reported_by',
            'assigned_to',
            'created_by',
            'edited_by',
        )
        return queryset
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy("ticketing:ticket_list")
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy("ticketing:ticket_edit", kwargs={"pk": self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, "is_locked"):
            return not bool(check_obj.is_locked)
        return True


class TicketEditView(BaseUpdateView, EditLockProtectedMixin):
    """View for editing an existing ticket."""

    model = models.Ticket
    template_name = "ticketing/ticket_edit.html"
    fields = ["title", "description", "category", "priority", "status", "assigned_to"]
    feature_code = "ticketing.tickets"
    required_action = "edit_own"
    active_module = "ticketing"
    success_message = _("Ticket updated successfully.")
    success_url = reverse_lazy("ticketing:ticket_list")

    def get_form_title(self) -> str:
        """Return form title."""
        return _("Edit Ticket")

