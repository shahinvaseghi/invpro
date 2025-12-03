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
from shared.views.base import EditLockProtectedMixin


class TicketTemplateListView(FeaturePermissionRequiredMixin, TicketingBaseView, ListView):
    """List view for ticket templates."""

    model = models.TicketTemplate
    template_name = "ticketing/templates_list.html"
    context_object_name = "object_list"
    paginate_by = 50
    feature_code = "ticketing.management.templates"
    required_action = "view_all"

    def get_queryset(self):
        """Filter templates by company and search."""
        company_id = self.request.session.get("active_company_id")
        
        # Filter by company
        if company_id:
            queryset = models.TicketTemplate.objects.filter(company_id=company_id)
        else:
            queryset = models.TicketTemplate.objects.none()

        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(template_code__icontains=search)
                | Q(description__icontains=search)
            )

        # Filter by category
        category_id = self.request.GET.get("category", "")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.order_by("sort_order", "template_code", "name")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        if 'page_obj' in context and hasattr(context['page_obj'], 'object_list'):
            context['object_list'] = context['page_obj'].object_list
        elif 'object_list' in context and hasattr(context['object_list'], 'query'):
            context['object_list'] = list(context['object_list'])
        
        context["page_title"] = _("Ticket Templates")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Templates"), "url": None},
        ]
        context["create_url"] = reverse_lazy("ticketing:template_create")
        context["create_button_text"] = _("Create Template")
        context["show_filters"] = True
        context["search_placeholder"] = _("Search by name or code")
        context["clear_filter_url"] = reverse_lazy("ticketing:templates")
        context["show_actions"] = True
        context["feature_code"] = "ticketing.management.templates"
        context["detail_url_name"] = "ticketing:template_detail"
        context["edit_url_name"] = "ticketing:template_edit"
        context["delete_url_name"] = "ticketing:template_delete"
        context["empty_state_title"] = _("No Templates Found")
        context["empty_state_message"] = _("Start by creating your first template.")
        context["empty_state_icon"] = "📋"

        # Get all categories for filter
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by("name")

        return context


class TicketTemplateCreateView(FeaturePermissionRequiredMixin, TicketingBaseView, CreateView):
    """View for creating a new ticket template."""

    model = models.TicketTemplate
    form_class = TicketTemplateForm
    template_name = "ticketing/template_form.html"
    success_url = reverse_lazy("ticketing:templates")
    feature_code = "ticketing.management.templates"
    required_action = "create"

    def get_form_kwargs(self):
        """Add request to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including formsets."""
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Create Template")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Templates"), "url": reverse_lazy("ticketing:templates")},
            {"label": _("Create"), "url": None},
        ]
        context["cancel_url"] = reverse_lazy("ticketing:templates")

        # Create formsets for new template
        if self.request.method == "POST":
            field_formset = TicketTemplateFieldFormSet(self.request.POST, instance=self.object or models.TicketTemplate())
            permission_formset = TicketTemplatePermissionFormSet(
                self.request.POST, instance=self.object or models.TicketTemplate()
            )
            event_formset = TicketTemplateEventFormSet(
                self.request.POST, instance=self.object or models.TicketTemplate()
            )
        else:
            field_formset = TicketTemplateFieldFormSet(instance=self.object or models.TicketTemplate())
            permission_formset = TicketTemplatePermissionFormSet(instance=self.object or models.TicketTemplate())
            event_formset = TicketTemplateEventFormSet(instance=self.object or models.TicketTemplate())

        context["field_formset"] = field_formset
        context["permission_formset"] = permission_formset
        context["event_formset"] = event_formset

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

    @transaction.atomic
    def form_valid(self, form):
        """Save template and all formsets."""
        # Set company_id before saving
        company_id = self.request.session.get("active_company_id")
        if company_id:
            form.instance.company_id = company_id

        response = super().form_valid(form)

        # Save field formset
        field_formset = TicketTemplateFieldFormSet(self.request.POST, instance=self.object)
        if field_formset.is_valid():
            fields = field_formset.save(commit=False)
            for field in fields:
                field.company_id = company_id
                if field.template:
                    field.template_code = field.template.template_code
                field.save()
            field_formset.save()
        else:
            # If field formset is invalid, return form with errors
            return self.form_invalid(form)

        # Save permission formset
        permission_formset = TicketTemplatePermissionFormSet(
            self.request.POST, instance=self.object
        )
        if permission_formset.is_valid():
            permissions = permission_formset.save(commit=False)
            for permission in permissions:
                permission.company_id = company_id
                if permission.template:
                    permission.template_code = permission.template.template_code
                permission.save()
            permission_formset.save()
        else:
            # If permission formset is invalid, return form with errors
            return self.form_invalid(form)

        # Save event formset
        event_formset = TicketTemplateEventFormSet(
            self.request.POST, instance=self.object
        )
        if event_formset.is_valid():
            events = event_formset.save(commit=False)
            for event in events:
                event.company_id = company_id
                if event.template:
                    event.template_code = event.template.template_code
                event.save()
            event_formset.save()
        else:
            # If event formset is invalid, return form with errors
            return self.form_invalid(form)

        messages.success(self.request, _("Template created successfully."))
        return response


class TicketTemplateUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, TicketingBaseView, UpdateView):
    """View for editing an existing ticket template."""

    model = models.TicketTemplate
    form_class = TicketTemplateForm
    template_name = "ticketing/template_form.html"
    success_url = reverse_lazy("ticketing:templates")
    feature_code = "ticketing.management.templates"
    required_action = "edit_own"

    def get_form_kwargs(self):
        """Add request to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_queryset(self):
        """Filter by company."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketTemplate.objects.filter(company_id=company_id)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including formsets."""
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Edit Template")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Templates"), "url": reverse_lazy("ticketing:templates")},
            {"label": _("Edit"), "url": None},
        ]
        context["cancel_url"] = reverse_lazy("ticketing:templates")

        # Create formsets for existing template
        if self.request.method == "POST":
            field_formset = TicketTemplateFieldFormSet(self.request.POST, instance=self.object)
            permission_formset = TicketTemplatePermissionFormSet(
                self.request.POST, instance=self.object
            )
            event_formset = TicketTemplateEventFormSet(
                self.request.POST, instance=self.object
            )
        else:
            field_formset = TicketTemplateFieldFormSet(instance=self.object)
            permission_formset = TicketTemplatePermissionFormSet(instance=self.object)
            event_formset = TicketTemplateEventFormSet(instance=self.object)

        context["field_formset"] = field_formset
        context["permission_formset"] = permission_formset
        context["event_formset"] = event_formset

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

    @transaction.atomic
    def form_valid(self, form):
        """Save template and all formsets."""
        response = super().form_valid(form)

        company_id = self.request.session.get("active_company_id")

        # Save field formset
        field_formset = TicketTemplateFieldFormSet(self.request.POST, instance=self.object)
        
        if field_formset.is_valid():
            fields = field_formset.save(commit=False)
            for field in fields:
                field.company_id = company_id
                if field.template:
                    field.template_code = field.template.template_code
                field.save()
            field_formset.save()
        else:
            # If field formset is invalid, return form with errors
            return self.form_invalid(form)

        # Save permission formset
        permission_formset = TicketTemplatePermissionFormSet(
            self.request.POST, instance=self.object
        )
        if permission_formset.is_valid():
            permissions = permission_formset.save(commit=False)
            for permission in permissions:
                permission.company_id = company_id
                if permission.template:
                    permission.template_code = permission.template.template_code
                permission.save()
            permission_formset.save()
        else:
            # If permission formset is invalid, return form with errors
            return self.form_invalid(form)

        # Save event formset
        event_formset = TicketTemplateEventFormSet(
            self.request.POST, instance=self.object
        )
        if event_formset.is_valid():
            events = event_formset.save(commit=False)
            for event in events:
                event.company_id = company_id
                if event.template:
                    event.template_code = event.template.template_code
                event.save()
            event_formset.save()
        else:
            # If event formset is invalid, return form with errors
            return self.form_invalid(form)

        messages.success(self.request, _("Template updated successfully."))
        return response


class TicketTemplateDetailView(FeaturePermissionRequiredMixin, TicketingBaseView, DetailView):
    """Detail view for viewing ticket templates (read-only)."""
    model = models.TicketTemplate
    template_name = "ticketing/template_detail.html"
    context_object_name = "template"
    feature_code = "ticketing.management.templates"
    required_action = "view_all"
    
    def get_queryset(self):
        """Filter by company."""
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
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("View Template")
        context["list_url"] = reverse_lazy("ticketing:templates")
        context["edit_url"] = reverse_lazy("ticketing:template_edit", kwargs={"pk": self.object.pk})
        context["can_edit"] = not getattr(self.object, "is_locked", 0) if hasattr(self.object, "is_locked") else True
        context["feature_code"] = "ticketing.management.templates"
        return context


class TicketTemplateDeleteView(FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView):
    """View for deleting a ticket template."""

    model = models.TicketTemplate
    template_name = "shared/generic/generic_confirm_delete.html"
    success_url = reverse_lazy("ticketing:templates")
    feature_code = "ticketing.management.templates"
    required_action = "delete_own"

    def get_queryset(self):
        """Filter by company."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketTemplate.objects.filter(company_id=company_id)

    def delete(self, request, *args, **kwargs):
        """Delete template and show success message."""
        messages.success(self.request, _("Template deleted successfully."))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["delete_title"] = _("Delete Template")
        context["confirmation_message"] = _("Are you sure you want to delete this template?")
        context["object_details"] = [
            {"label": _("Template Code"), "value": f"<code>{self.object.template_code}</code>"},
            {"label": _("Template Name"), "value": self.object.name},
        ]
        if self.object.description:
            context["object_details"].append({"label": _("Description"), "value": self.object.description})
        
        context["warning_message"] = _("Warning: This action cannot be undone. All associated fields, permissions, and events will also be deleted.")
        context["cancel_url"] = reverse_lazy("ticketing:templates")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Templates"), "url": reverse_lazy("ticketing:templates")},
            {"label": _("Delete"), "url": None},
        ]
        return context

