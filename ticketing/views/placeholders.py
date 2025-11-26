"""
Placeholder views for ticketing module.

These views are placeholder implementations that will be replaced
with full functionality in future iterations.
"""
from typing import Dict, Any

from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _

from .base import TicketingBaseView


class TicketRespondView(TicketingBaseView, TemplateView):
    """Placeholder view for responding to tickets."""

    template_name = "ticketing/ticket_respond.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Respond to Ticket")
        return context


class TemplateCreateView(TicketingBaseView, TemplateView):
    """Placeholder view for creating ticket templates."""

    template_name = "ticketing/template_create.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Template")
        return context


class CategoriesView(TicketingBaseView, TemplateView):
    """Placeholder view for managing ticket categories."""

    template_name = "ticketing/categories.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Categories")
        return context


# SubcategoriesView has been moved to subcategories.py


class AutoResponseView(TicketingBaseView, TemplateView):
    """Placeholder view for auto response automation."""

    template_name = "ticketing/auto_response.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Auto Response")
        return context

