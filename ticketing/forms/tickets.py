"""
Forms for ticket management.

This module contains forms for creating and editing tickets.
"""
from typing import Dict, Any, Optional

from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Ticket, TicketTemplate, TicketCategory, TicketPriority
from .base import TicketingBaseForm, TicketFormMixin


class TicketForm(TicketFormMixin, TicketingBaseForm):
    """Form for creating and editing tickets."""

    class Meta:
        model = Ticket
        fields = [
            "template",
            "title",
            "description",
            "category",
            "priority",
            "status",
            "assigned_to",
        ]
        widgets = {
            "template": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "assigned_to": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "template": _("Template"),
            "title": _("Title"),
            "description": _("Description"),
            "category": _("Category"),
            "priority": _("Priority"),
            "status": _("Status"),
            "assigned_to": _("Assigned To"),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with filtered querysets."""
        super().__init__(*args, **kwargs)
        company_id = None
        if hasattr(self, "request") and self.request:
            company_id = self.request.session.get("active_company_id")

        if company_id:
            # Filter by company and enabled items
            self.fields["template"].queryset = TicketTemplate.objects.filter(
                company_id=company_id, is_enabled=1
            )
            self.fields["category"].queryset = TicketCategory.objects.filter(
                company_id=company_id, is_enabled=1
            )
            self.fields["priority"].queryset = TicketPriority.objects.filter(
                company_id=company_id, is_enabled=1
            )
            # TODO: Filter assigned_to by company users


class TicketCreateForm(TicketForm):
    """Form for creating new tickets (excludes status and assigned_to)."""

    class Meta(TicketForm.Meta):
        fields = ["template", "title", "description", "category", "priority"]

    def __init__(self, *args, **kwargs):
        """Initialize create form."""
        super().__init__(*args, **kwargs)
        # Remove status and assigned_to fields for create form
        if "status" in self.fields:
            del self.fields["status"]
        if "assigned_to" in self.fields:
            del self.fields["assigned_to"]

