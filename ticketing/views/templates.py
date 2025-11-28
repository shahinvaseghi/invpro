"""
Views for ticket template management.
"""
from typing import Dict, Any

from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

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
    context_object_name = "templates"
    paginate_by = 50
    feature_code = "ticketing.management.templates"
    required_action = "view_all"

    def get_queryset(self):
        """Filter templates by company and search."""
        company_id = self.request.session.get("active_company_id")
        
        # Debug: Log company_id and all templates
        print("=" * 80)
        print(f"🔵 [TEMPLATE_LIST] Company ID from session: {company_id}")
        print(f"🔵 [TEMPLATE_LIST] User: {self.request.user.username}")
        print(f"🔵 [TEMPLATE_LIST] Session keys: {list(self.request.session.keys())}")
        
        # Check all templates in database (for debugging)
        all_templates_in_db = models.TicketTemplate.objects.all()
        print(f"🔵 [TEMPLATE_LIST] Total templates in DB: {all_templates_in_db.count()}")
        for t in all_templates_in_db:
            print(f"🔵 [TEMPLATE_LIST]   - ID={t.pk}, Code={t.template_code}, Name={t.name}, Company={t.company_id}, Enabled={t.is_enabled}")
        
        # Filter by company
        if company_id:
            queryset = models.TicketTemplate.objects.filter(company_id=company_id)
            print(f"🔵 [TEMPLATE_LIST] Templates for company {company_id}: {queryset.count()}")
        else:
            print("🔵 [TEMPLATE_LIST] WARNING: No company_id in session!")
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

        final_queryset = queryset.order_by("sort_order", "template_code", "name")
        print(f"🔵 [TEMPLATE_LIST] Final queryset count: {final_queryset.count()}")
        print("=" * 80)
        
        return final_queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Ticket Templates")

        # Debug: Log context data
        print("=" * 80)
        print("🔵 [TEMPLATE_LIST_CONTEXT] Context keys:", list(context.keys()))
        print(f"🔵 [TEMPLATE_LIST_CONTEXT] 'templates' in context: {'templates' in context}")
        if 'templates' in context:
            templates_list = context['templates']
            print(f"🔵 [TEMPLATE_LIST_CONTEXT] Templates type: {type(templates_list)}")
            if hasattr(templates_list, '__len__'):
                print(f"🔵 [TEMPLATE_LIST_CONTEXT] Templates count: {len(templates_list)}")
                for idx, t in enumerate(templates_list):
                    print(f"🔵 [TEMPLATE_LIST_CONTEXT]   Template {idx}: {t.template_code} - {t.name}")
        print(f"🔵 [TEMPLATE_LIST_CONTEXT] is_paginated: {context.get('is_paginated', 'NOT IN CONTEXT')}")
        print(f"🔵 [TEMPLATE_LIST_CONTEXT] page_obj: {context.get('page_obj', 'NOT IN CONTEXT')}")
        print("=" * 80)

        # Get all categories for filter
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by("name")

        context["search_term"] = self.request.GET.get("search", "")
        context["selected_category"] = self.request.GET.get("category", "")
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
        context["page_title"] = _("Create Template")

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

        print("=" * 80)
        print("🟢 [TEMPLATE_CREATE] Saving new template...")
        print(f"🟢 [TEMPLATE_CREATE] Company ID from session: {company_id}")
        print(f"🟢 [TEMPLATE_CREATE] User: {self.request.user.username}")
        print(f"🟢 [TEMPLATE_CREATE] Template name: {form.instance.name}")
        print(f"🟢 [TEMPLATE_CREATE] Template code: {form.instance.template_code}")
        print(f"🟢 [TEMPLATE_CREATE] Is enabled: {form.instance.is_enabled}")
        print(f"🟢 [TEMPLATE_CREATE] Company ID on instance (before save): {form.instance.company_id}")

        response = super().form_valid(form)
        
        print(f"🟢 [TEMPLATE_CREATE] Template saved with ID: {self.object.pk}")
        print(f"🟢 [TEMPLATE_CREATE] Template code after save: {self.object.template_code}")
        print(f"🟢 [TEMPLATE_CREATE] Company ID on instance (after save): {self.object.company_id}")
        
        # Verify it's in database
        from_db = models.TicketTemplate.objects.filter(pk=self.object.pk).first()
        if from_db:
            print(f"🟢 [TEMPLATE_CREATE] Verified in DB: Code={from_db.template_code}, Company={from_db.company_id}, Enabled={from_db.is_enabled}")
        else:
            print("🟢 [TEMPLATE_CREATE] ERROR: Template not found in DB after save!")
        print("=" * 80)

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
        context["page_title"] = _("Edit Template")

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
            
            # Log field_config values for debugging
            print("=" * 80)
            print("🟣 [VIEW] Loading template for edit...")
            if self.object:
                print(f"🟣 [VIEW] Template ID: {self.object.pk}")
                fields = self.object.fields.all()
                for idx, field in enumerate(fields):
                    print(f"🟣 [VIEW] Field {idx}: field_key={field.field_key}, field_type={field.field_type}")
                    print(f"🟣 [VIEW] Field {idx} field_config type: {type(field.field_config)}")
                    print(f"🟣 [VIEW] Field {idx} field_config value: {field.field_config}")
                    import json
                    if isinstance(field.field_config, dict):
                        json_str = json.dumps(field.field_config, ensure_ascii=False)
                        print(f"🟣 [VIEW] Field {idx} field_config as JSON string: {json_str}")

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
        
        # Log field_config values from POST data
        print("=" * 80)
        print("🟣 [VIEW] Saving template fields...")
        for key, value in self.request.POST.items():
            if 'field_config' in key:
                print(f"🟣 [VIEW] POST field_config found: {key} = {value}")
        
        if field_formset.is_valid():
            fields = field_formset.save(commit=False)
            for idx, field in enumerate(fields):
                print(f"🟣 [VIEW] Field {idx}: field_key={field.field_key}, field_type={field.field_type}")
                print(f"🟣 [VIEW] Field {idx} field_config (before save): {field.field_config}")
                
                field.company_id = company_id
                if field.template:
                    field.template_code = field.template.template_code
                field.save()
                
                print(f"🟣 [VIEW] Field {idx} field_config (after save): {field.field_config}")
            field_formset.save()
        else:
            print("🟣 [VIEW] Field formset is INVALID!")
            print(f"🟣 [VIEW] Errors: {field_formset.errors}")
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


class TicketTemplateDeleteView(FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView):
    """View for deleting a ticket template."""

    model = models.TicketTemplate
    template_name = "ticketing/template_confirm_delete.html"
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
        context["page_title"] = _("Delete Template")
        return context

