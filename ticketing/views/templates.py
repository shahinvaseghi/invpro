"""
Views for ticket template management.
"""
from typing import Dict, Any

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .. import models
from ..forms.templates import (
    TicketTemplateForm,
    TicketTemplateFieldFormSet,
    TicketTemplatePermissionFormSet,
    TicketTemplateEventFormSet,
)
from .base import TicketingBaseView
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseListView,
    BaseDetailView,
    BaseDeleteView,
    EditLockProtectedMixin,
)
from shared.views.base_additional import (
    BaseMultipleFormsetCreateView,
    BaseMultipleFormsetUpdateView,
)


class TicketTemplateListView(BaseListView):
    """List view for ticket templates."""

    model = models.TicketTemplate
    template_name = "ticketing/templates_list.html"
    context_object_name = "object_list"
    paginate_by = 50
    feature_code = "ticketing.management.templates"
    required_action = "view_all"
    active_module = "ticketing"
    default_order_by = ["sort_order", "template_code", "name"]

    def get_base_queryset(self):
        """Filter templates by company."""
        company_id = self.request.session.get("active_company_id")
        if company_id:
            return models.TicketTemplate.objects.filter(company_id=company_id)
        return models.TicketTemplate.objects.none()

    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ["name", "template_code", "description"]

    def get_queryset(self):
        """Filter templates by company, search, and category filter."""
        queryset = super().get_queryset()

        # Filter by category
        category_id = self.request.GET.get("category", "")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)

        # Get all categories for filter
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by("name")

        return context

    def get_page_title(self) -> str:
        """Return page title."""
        return _("Ticket Templates")

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Templates"), "url": None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy("ticketing:template_create")

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _("Create Template")

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return "ticketing:template_detail"

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return "ticketing:template_edit"

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return "ticketing:template_delete"

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _("No Templates Found")

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _("Start by creating your first template.")

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return "📋"


class TicketTemplateCreateView(BaseMultipleFormsetCreateView):
    """View for creating a new ticket template."""

    model = models.TicketTemplate
    form_class = TicketTemplateForm
    template_name = "ticketing/template_form.html"
    success_url = reverse_lazy("ticketing:templates")
    feature_code = "ticketing.management.templates"
    required_action = "create"
    active_module = "ticketing"
    success_message = _("Template created successfully.")
    formsets = {
        "fields": TicketTemplateFieldFormSet,
        "permissions": TicketTemplatePermissionFormSet,
        "events": TicketTemplateEventFormSet,
    }
    formset_prefixes = {
        "fields": "fields",
        "permissions": "permissions",
        "events": "events",
    }

    def get_form_kwargs(self):
        """Add request to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_formset_kwargs(self, formset_name: str) -> Dict[str, Any]:
        """Return kwargs for a specific formset."""
        kwargs = super().get_formset_kwargs(formset_name)
        if not kwargs.get("instance"):
            kwargs["instance"] = models.TicketTemplate()
        return kwargs

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Templates"), "url": reverse_lazy("ticketing:templates")},
            {"label": _("Create"), "url": None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy("ticketing:templates")

    def get_form_title(self) -> str:
        """Return form title."""
        return _("Create Template")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including formsets."""
        context = super().get_context_data(**kwargs)

        # Get categories and priorities for form
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by("name")
            context["priorities"] = models.TicketPriority.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by("priority_level")

        return context

    def process_formset(self, formset_name: str, formset) -> list:
        """Process formset before saving."""
        company_id = self.request.session.get("active_company_id")
        if company_id:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.company_id = company_id
                if hasattr(instance, "template") and instance.template:
                    if hasattr(instance, "template_code"):
                        instance.template_code = instance.template.template_code
                instance.save()
            return instances
        return None

    def form_valid(self, form):
        """Save template and all formsets."""
        # Set company_id before saving
        company_id = self.request.session.get("active_company_id")
        if company_id:
            form.instance.company_id = company_id

        # Save using parent's form_valid which handles multiple formsets
        return super().form_valid(form)


class TicketTemplateUpdateView(BaseMultipleFormsetUpdateView, EditLockProtectedMixin):
    """View for editing an existing ticket template."""

    model = models.TicketTemplate
    form_class = TicketTemplateForm
    template_name = "ticketing/template_form.html"
    success_url = reverse_lazy("ticketing:templates")
    feature_code = "ticketing.management.templates"
    required_action = "edit_own"
    active_module = "ticketing"
    success_message = _("Template updated successfully.")
    formsets = {
        "fields": TicketTemplateFieldFormSet,
        "permissions": TicketTemplatePermissionFormSet,
        "events": TicketTemplateEventFormSet,
    }
    formset_prefixes = {
        "fields": "fields",
        "permissions": "permissions",
        "events": "events",
    }

    def get_form_kwargs(self):
        """Add request to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_queryset(self):
        """Filter by company."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketTemplate.objects.filter(company_id=company_id)

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Templates"), "url": reverse_lazy("ticketing:templates")},
            {"label": _("Edit"), "url": None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy("ticketing:templates")

    def get_form_title(self) -> str:
        """Return form title."""
        return _("Edit Template")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including formsets."""
        context = super().get_context_data(**kwargs)

        # Get categories and priorities for form
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by("name")
            context["priorities"] = models.TicketPriority.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by("priority_level")

        return context

    def process_formset(self, formset_name: str, formset) -> list:
        """Process formset before saving."""
        company_id = self.request.session.get("active_company_id")
        if company_id:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.company_id = company_id
                if hasattr(instance, "template") and instance.template:
                    if hasattr(instance, "template_code"):
                        instance.template_code = instance.template.template_code
                instance.save()
            return instances
        return None

    def form_valid(self, form):
        """Save template and all formsets."""
        # Save using parent's form_valid which handles multiple formsets
        return super().form_valid(form)


class TicketTemplateDetailView(BaseDetailView):
    """Detail view for viewing ticket templates (read-only)."""
    model = models.TicketTemplate
    template_name = "ticketing/template_detail.html"
    context_object_name = "template"
    feature_code = "ticketing.management.templates"
    required_action = "view_all"
    active_module = "ticketing"
    
    def get_queryset(self):
        """Filter by company and optimize queries."""
        company_id = self.request.session.get("active_company_id")
        if not company_id:
            return models.TicketTemplate.objects.none()
        queryset = models.TicketTemplate.objects.filter(company_id=company_id)
        queryset = queryset.select_related(
            'category',
            'subcategory',
            'default_priority',
            'created_by',
            'edited_by',
        ).prefetch_related(
            'fields',
            'permissions',
        )
        return queryset
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy("ticketing:templates")
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy("ticketing:template_edit", kwargs={"pk": self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, "is_locked"):
            return not bool(check_obj.is_locked)
        return True


class TicketTemplateDeleteView(BaseDeleteView):
    """View for deleting a ticket template."""

    model = models.TicketTemplate
    template_name = "shared/generic/generic_confirm_delete.html"
    success_url = reverse_lazy("ticketing:templates")
    feature_code = "ticketing.management.templates"
    required_action = "delete_own"
    active_module = "ticketing"
    success_message = _("Template deleted successfully.")

    def get_queryset(self):
        """Filter by company."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketTemplate.objects.filter(company_id=company_id)

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _("Delete Template")

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _("Are you sure you want to delete this template?")

    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        details = [
            {"label": _("Template Code"), "value": f"<code>{self.object.template_code}</code>"},
            {"label": _("Template Name"), "value": self.object.name},
        ]
        if self.object.description:
            details.append({"label": _("Description"), "value": self.object.description})
        return details

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["warning_message"] = _("Warning: This action cannot be undone. All associated fields, permissions, and events will also be deleted.")
        return context

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Templates"), "url": reverse_lazy("ticketing:templates")},
            {"label": _("Delete"), "url": None},
        ]

