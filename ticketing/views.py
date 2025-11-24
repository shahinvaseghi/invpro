"""
Views for ticketing app - placeholder views for menu structure.
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class TicketCreateView(LoginRequiredMixin, TemplateView):
    """Placeholder view for creating tickets."""
    template_name = 'ticketing/ticket_create.html'


class TicketRespondView(LoginRequiredMixin, TemplateView):
    """Placeholder view for responding to tickets."""
    template_name = 'ticketing/ticket_respond.html'


class TemplateCreateView(LoginRequiredMixin, TemplateView):
    """Placeholder view for creating ticket templates."""
    template_name = 'ticketing/template_create.html'


class CategoriesView(LoginRequiredMixin, TemplateView):
    """Placeholder view for ticket categories."""
    template_name = 'ticketing/categories.html'


class SubcategoriesView(LoginRequiredMixin, TemplateView):
    """Placeholder view for ticket subcategories."""
    template_name = 'ticketing/subcategories.html'


class AutoResponseView(LoginRequiredMixin, TemplateView):
    """Placeholder view for auto response automation."""
    template_name = 'ticketing/auto_response.html'
