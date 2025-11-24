"""
Base views and mixins for ticketing module.

This module contains reusable base classes and mixins that are used across
all ticketing views.
"""
from typing import Dict, Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .. import models


class TicketingBaseView(LoginRequiredMixin):
    """Base view with common context for ticketing module."""

    login_url = "/admin/login/"

    def get_queryset(self):
        """Filter queryset by active company."""
        queryset = super().get_queryset()
        company_id = self.request.session.get("active_company_id")
        if company_id and hasattr(queryset.model, "company"):
            queryset = queryset.filter(company_id=company_id)
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add common context data."""
        context = super().get_context_data(**kwargs)
        context["active_module"] = "ticketing"
        return context


class TicketLockProtectedMixin:
    """Prevent modifying locked tickets."""

    lock_redirect_url_name: str = ""
    lock_error_message = _("Ticket is locked and cannot be modified.")
    owner_field: str = "reported_by"
    owner_error_message = _("Only the ticket creator can modify this ticket.")
    protected_methods = ("get", "post", "put", "patch", "delete")

    def dispatch(self, request, *args, **kwargs):
        """Check if ticket is locked before allowing modifications."""
        if request.method.lower() in self.protected_methods:
            obj = self.get_object()
            self.object = obj
            if getattr(obj, "is_locked", 0):
                messages.error(request, self.lock_error_message)
                return HttpResponseRedirect(self._get_lock_redirect_url())
            if self.owner_field:
                owner = getattr(obj, self.owner_field, None)
                owner_id = getattr(owner, "id", None) if owner else None
                if owner_id and owner_id != request.user.id:
                    messages.error(request, self.owner_error_message)
                    return HttpResponseRedirect(self._get_lock_redirect_url())
        return super().dispatch(request, *args, **kwargs)

    def _get_lock_redirect_url(self) -> str:
        """Get redirect URL when ticket is locked."""
        if self.lock_redirect_url_name:
            return reverse(self.lock_redirect_url_name)
        if hasattr(self, "list_url_name") and getattr(self, "list_url_name"):
            return reverse(self.list_url_name)
        return reverse("ticketing:ticket_list")

