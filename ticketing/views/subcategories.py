"""
Views for ticket subcategories management.

Subcategories are actually TicketCategory instances with a parent_category set.
This module provides views specifically for managing subcategories.
"""
from typing import Dict, Any

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .. import models
from ..forms.categories import TicketCategoryForm, TicketCategoryPermissionFormSet
from .base import TicketingBaseView
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseListView,
    BaseFormsetCreateView,
    BaseFormsetUpdateView,
    BaseDetailView,
    BaseDeleteView,
    EditLockProtectedMixin,
)


class TicketSubcategoryListView(BaseListView):
    """List view for ticket subcategories (categories with parent)."""

    model = models.TicketCategory
    template_name = "ticketing/subcategories_list.html"
    context_object_name = "object_list"
    paginate_by = 50
    feature_code = "ticketing.management.subcategories"
    required_action = "view_all"
    active_module = "ticketing"
    default_order_by = ["parent_category__name", "sort_order", "public_code", "name"]

    def get_base_queryset(self):
        """Filter subcategories (categories with parent) by company."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketCategory.objects.filter(
            company_id=company_id, parent_category__isnull=False
        )

    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ["name", "name_en", "public_code"]

    def get_queryset(self):
        """Filter subcategories by company, search, and parent filter."""
        queryset = super().get_queryset()

        # Filter by parent category
        parent_id = self.request.GET.get("parent", "")
        if parent_id:
            queryset = queryset.filter(parent_category_id=parent_id)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)

        # Get all parent categories for filter
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["parent_categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, parent_category__isnull=True, is_enabled=1
            ).order_by("name")

        return context

    def get_page_title(self) -> str:
        """Return page title."""
        return _("Ticket Subcategories")

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Subcategories"), "url": None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy("ticketing:subcategory_create")

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _("Create Subcategory")

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return "ticketing:subcategory_detail"

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return "ticketing:subcategory_edit"

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return "ticketing:subcategory_delete"

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _("No Subcategories Found")

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _("Start by creating your first subcategory.")

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return "📂"


class TicketSubcategoryCreateView(BaseFormsetCreateView):
    """View for creating a new ticket subcategory."""

    model = models.TicketCategory
    form_class = TicketCategoryForm
    template_name = "ticketing/subcategory_form.html"
    success_url = reverse_lazy("ticketing:subcategories")
    feature_code = "ticketing.management.subcategories"
    required_action = "create"
    active_module = "ticketing"
    success_message = _("Subcategory created successfully.")
    formset_class = TicketCategoryPermissionFormSet
    formset_prefix = "permissions"

    def get_form_kwargs(self):
        """Add request to form kwargs."""
        kwargs = super().get_form_kwargs()
        form = TicketCategoryForm(**kwargs)
        form.request = self.request
        return kwargs

    def get_formset_kwargs(self) -> Dict[str, Any]:
        """Return kwargs for formset."""
        kwargs = super().get_formset_kwargs()
        if not kwargs.get("instance"):
            kwargs["instance"] = models.TicketCategory()
        return kwargs

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Subcategories"), "url": reverse_lazy("ticketing:subcategories")},
            {"label": _("Create"), "url": None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy("ticketing:subcategories")

    def get_form_title(self) -> str:
        """Return form title."""
        return _("Create Subcategory")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including permission formset."""
        context = super().get_context_data(**kwargs)

        # Set request on all forms in formset
        if "formset" in context:
            for form in context["formset"].forms:
                form.request = self.request

        # Get all parent categories for dropdown
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["parent_categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, parent_category__isnull=True, is_enabled=1
            ).order_by("name")

        return context

    def process_formset_instance(self, instance):
        """Process formset instance before saving."""
        company_id = self.request.session.get("active_company_id")
        if company_id:
            instance.company_id = company_id
        if instance.category:
            instance.category_code = instance.category.public_code
        return instance

    def form_valid(self, form):
        """Save subcategory and permissions."""
        # Ensure parent_category is set (subcategory requirement)
        if not form.instance.parent_category_id:
            form.add_error("parent_category", _("Subcategory must have a parent category."))
            return self.form_invalid(form)

        from django.db import transaction

        # Set company_id before saving
        company_id = self.request.session.get("active_company_id")
        if company_id:
            form.instance.company_id = company_id

        with transaction.atomic():
            # Save main object first
            self.object = form.save()

            # Get formset and set request on all forms
            formset = self.formset_class(
                self.request.POST, instance=self.object, prefix=self.formset_prefix
            )
            for perm_form in formset.forms:
                perm_form.request = self.request

            if formset.is_valid():
                # Process each instance before saving
                for permission in formset.save(commit=False):
                    self.process_formset_instance(permission)
                    permission.save()
                formset.save()
            else:
                # If formset is invalid, return form with errors
                return self.form_invalid(form)

        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())


class TicketSubcategoryUpdateView(BaseFormsetUpdateView, EditLockProtectedMixin):
    """View for editing an existing ticket subcategory."""

    model = models.TicketCategory
    form_class = TicketCategoryForm
    template_name = "ticketing/subcategory_form.html"
    success_url = reverse_lazy("ticketing:subcategories")
    feature_code = "ticketing.management.subcategories"
    required_action = "edit_own"
    active_module = "ticketing"
    success_message = _("Subcategory updated successfully.")
    formset_class = TicketCategoryPermissionFormSet
    formset_prefix = "permissions"

    def get_form_kwargs(self):
        """Add request to form kwargs."""
        kwargs = super().get_form_kwargs()
        form = TicketCategoryForm(**kwargs)
        form.request = self.request
        return kwargs

    def get_queryset(self):
        """Filter by company and ensure it's a subcategory."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketCategory.objects.filter(
            company_id=company_id, parent_category__isnull=False
        )

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Subcategories"), "url": reverse_lazy("ticketing:subcategories")},
            {"label": _("Edit"), "url": None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy("ticketing:subcategories")

    def get_form_title(self) -> str:
        """Return form title."""
        return _("Edit Subcategory")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including permission formset."""
        context = super().get_context_data(**kwargs)

        # Set request on all forms in formset
        if "formset" in context:
            for form in context["formset"].forms:
                form.request = self.request

        # Get all parent categories for dropdown
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["parent_categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, parent_category__isnull=True, is_enabled=1
            ).order_by("name")

        return context

    def process_formset_instance(self, instance):
        """Process formset instance before saving."""
        company_id = self.request.session.get("active_company_id")
        if company_id:
            instance.company_id = company_id
        if instance.category:
            instance.category_code = instance.category.public_code
        return instance

    def form_valid(self, form):
        """Save subcategory and permissions."""
        # Ensure parent_category is set (subcategory requirement)
        if not form.instance.parent_category_id:
            form.add_error("parent_category", _("Subcategory must have a parent category."))
            return self.form_invalid(form)

        from django.db import transaction

        with transaction.atomic():
            # Save main object first
            self.object = form.save()

            # Get formset and set request on all forms
            formset = self.formset_class(
                self.request.POST, instance=self.object, prefix=self.formset_prefix
            )
            for perm_form in formset.forms:
                perm_form.request = self.request

            if formset.is_valid():
                # Process each instance before saving
                for permission in formset.save(commit=False):
                    self.process_formset_instance(permission)
                    permission.save()
                formset.save()
            else:
                # If formset is invalid, return form with errors
                return self.form_invalid(form)

        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(self.get_success_url())


class TicketSubcategoryDetailView(BaseDetailView):
    """Detail view for viewing ticket subcategories (read-only)."""
    model = models.TicketCategory
    template_name = "ticketing/subcategory_detail.html"
    context_object_name = "subcategory"
    feature_code = "ticketing.management.subcategories"
    required_action = "view_all"
    active_module = "ticketing"
    
    def get_queryset(self):
        """Filter by company and ensure it's a subcategory."""
        company_id = self.request.session.get("active_company_id")
        if not company_id:
            return models.TicketCategory.objects.none()
        queryset = models.TicketCategory.objects.filter(
            company_id=company_id, parent_category__isnull=False
        )
        queryset = queryset.select_related(
            'parent_category',
            'created_by',
            'edited_by',
        )
        return queryset
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy("ticketing:subcategories")
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy("ticketing:subcategory_edit", kwargs={"pk": self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, "is_locked"):
            return not bool(check_obj.is_locked)
        return True


class TicketSubcategoryDeleteView(BaseDeleteView):
    """View for deleting a ticket subcategory."""

    model = models.TicketCategory
    template_name = "shared/generic/generic_confirm_delete.html"
    success_url = reverse_lazy("ticketing:subcategories")
    feature_code = "ticketing.management.subcategories"
    required_action = "delete_own"
    active_module = "ticketing"
    success_message = _("Subcategory deleted successfully.")

    def get_queryset(self):
        """Filter by company and ensure it's a subcategory."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketCategory.objects.filter(
            company_id=company_id, parent_category__isnull=False
        )

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _("Delete Subcategory")

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _("Are you sure you want to delete this subcategory?")

    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        details = [
            {"label": _("Name"), "value": self.object.name},
        ]
        if self.object.public_code:
            details.append({"label": _("Code"), "value": f"<code>{self.object.public_code}</code>"})
        if self.object.description:
            details.append({"label": _("Description"), "value": self.object.description})
        if self.object.parent_category:
            details.append({"label": _("Parent Category"), "value": self.object.parent_category.name})
        return details

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Subcategories"), "url": reverse_lazy("ticketing:subcategories")},
            {"label": _("Delete"), "url": None},
        ]

