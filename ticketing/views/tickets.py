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
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Ticket")
        return context

    def form_valid(self, form):
        """Set reported_by to current user."""
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

