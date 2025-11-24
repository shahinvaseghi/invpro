"""
Base form classes for ticketing module.

This module contains reusable base form classes and helper functions
that are used across all ticketing forms.
"""
from typing import Dict, Any, Optional

from django import forms
from django.utils.translation import gettext_lazy as _


class TicketingBaseForm(forms.ModelForm):
    """Base form for ticketing models."""

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """Initialize form with company context."""
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        # Add company_id to form if available in request
        if self.request:
            company_id = self.request.session.get("active_company_id")
            if company_id:
                # Filter foreign key fields by company if applicable
                self._filter_foreign_keys_by_company(company_id)

    def _filter_foreign_keys_by_company(self, company_id: int) -> None:
        """Filter foreign key fields by active company."""
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                # Filter queryset by company if model has company field
                queryset = field.queryset
                if queryset and hasattr(queryset.model, "company"):
                    field.queryset = queryset.filter(company_id=company_id)


class TicketFormMixin:
    """Mixin for ticket-related forms."""

    def clean(self) -> Dict[str, Any]:
        """Perform cross-field validation."""
        cleaned_data = super().clean()
        # Add ticket-specific validation here
        return cleaned_data

