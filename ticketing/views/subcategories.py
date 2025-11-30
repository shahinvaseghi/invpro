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
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .. import models
from ..forms.categories import TicketCategoryForm, TicketCategoryPermissionFormSet
from .base import TicketingBaseView
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin


class TicketSubcategoryListView(FeaturePermissionRequiredMixin, TicketingBaseView, ListView):
    """List view for ticket subcategories (categories with parent)."""

    model = models.TicketCategory
    template_name = "ticketing/subcategories_list.html"
    context_object_name = "object_list"
    paginate_by = 50
    feature_code = "ticketing.management.subcategories"
    required_action = "view_all"

    def get_queryset(self):
        """Filter subcategories (categories with parent) by company and search."""
        company_id = self.request.session.get("active_company_id")
        queryset = models.TicketCategory.objects.filter(
            company_id=company_id, parent_category__isnull=False
        )

        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(name_en__icontains=search)
                | Q(public_code__icontains=search)
            )

        # Filter by parent category
        parent_id = self.request.GET.get("parent", "")
        if parent_id:
            queryset = queryset.filter(parent_category_id=parent_id)

        return queryset.order_by("parent_category__name", "sort_order", "public_code", "name")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        if 'page_obj' in context and hasattr(context['page_obj'], 'object_list'):
            context['object_list'] = context['page_obj'].object_list
        elif 'object_list' in context and hasattr(context['object_list'], 'query'):
            context['object_list'] = list(context['object_list'])
        
        context["page_title"] = _("Ticket Subcategories")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Subcategories"), "url": None},
        ]
        context["create_url"] = reverse_lazy("ticketing:subcategory_create")
        context["create_button_text"] = _("Create Subcategory")
        context["show_filters"] = True
        context["search_placeholder"] = _("Search by name or code")
        context["clear_filter_url"] = reverse_lazy("ticketing:subcategories")
        context["show_actions"] = True
        context["edit_url_name"] = "ticketing:subcategory_edit"
        context["delete_url_name"] = "ticketing:subcategory_delete"
        context["empty_state_title"] = _("No Subcategories Found")
        context["empty_state_message"] = _("Start by creating your first subcategory.")
        context["empty_state_icon"] = "📂"

        # Get all parent categories for filter
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["parent_categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, parent_category__isnull=True, is_enabled=1
            ).order_by("name")

        return context


class TicketSubcategoryCreateView(FeaturePermissionRequiredMixin, TicketingBaseView, CreateView):
    """View for creating a new ticket subcategory."""

    model = models.TicketCategory
    form_class = TicketCategoryForm
    template_name = "ticketing/subcategory_form.html"
    success_url = reverse_lazy("ticketing:subcategories")
    feature_code = "ticketing.management.subcategories"
    required_action = "create"

    def get_form_kwargs(self):
        """Add request to form kwargs."""
        kwargs = super().get_form_kwargs()
        form = TicketCategoryForm(**kwargs)
        form.request = self.request
        return kwargs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including permission formset."""
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Create Subcategory")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Subcategories"), "url": reverse_lazy("ticketing:subcategories")},
            {"label": _("Create"), "url": None},
        ]
        context["cancel_url"] = reverse_lazy("ticketing:subcategories")

        # Create permission formset for new subcategory
        if self.request.method == "POST":
            permission_formset = TicketCategoryPermissionFormSet(
                self.request.POST, instance=self.object or models.TicketCategory()
            )
        else:
            permission_formset = TicketCategoryPermissionFormSet(
                instance=self.object or models.TicketCategory()
            )

        # Set request on all forms in formset
        for form in permission_formset.forms:
            form.request = self.request

        context["permission_formset"] = permission_formset

        # Get all parent categories for dropdown
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["parent_categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, parent_category__isnull=True, is_enabled=1
            ).order_by("name")

        return context

    def form_valid(self, form):
        """Save subcategory and permissions."""
        # Ensure parent_category is set (subcategory requirement)
        if not form.instance.parent_category_id:
            form.add_error("parent_category", _("Subcategory must have a parent category."))
            return self.form_invalid(form)

        # Set company_id before saving
        company_id = self.request.session.get("active_company_id")
        if company_id:
            form.instance.company_id = company_id

        response = super().form_valid(form)

        # Save permission formset
        permission_formset = TicketCategoryPermissionFormSet(
            self.request.POST, instance=self.object
        )

        # Set request on all forms in formset
        for perm_form in permission_formset.forms:
            perm_form.request = self.request

        if permission_formset.is_valid():
            permission_formset.save()
            # Set company_id for all saved permissions
            for permission in permission_formset.save(commit=False):
                permission.company_id = company_id
                if permission.category:
                    permission.category_code = permission.category.public_code
                permission.save()
        else:
            # If formset is invalid, return form with errors
            return self.form_invalid(form)

        messages.success(self.request, _("Subcategory created successfully."))
        return response


class TicketSubcategoryUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, TicketingBaseView, UpdateView):
    """View for editing an existing ticket subcategory."""

    model = models.TicketCategory
    form_class = TicketCategoryForm
    template_name = "ticketing/subcategory_form.html"
    success_url = reverse_lazy("ticketing:subcategories")
    feature_code = "ticketing.management.subcategories"
    required_action = "edit_own"

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

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including permission formset."""
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Edit Subcategory")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Subcategories"), "url": reverse_lazy("ticketing:subcategories")},
            {"label": _("Edit"), "url": None},
        ]
        context["cancel_url"] = reverse_lazy("ticketing:subcategories")

        # Create permission formset for existing subcategory
        if self.request.method == "POST":
            permission_formset = TicketCategoryPermissionFormSet(
                self.request.POST, instance=self.object
            )
        else:
            permission_formset = TicketCategoryPermissionFormSet(instance=self.object)

        # Set request on all forms in formset
        for form in permission_formset.forms:
            form.request = self.request

        context["permission_formset"] = permission_formset

        # Get all parent categories for dropdown
        company_id = self.request.session.get("active_company_id")
        if company_id:
            context["parent_categories"] = models.TicketCategory.objects.filter(
                company_id=company_id, parent_category__isnull=True, is_enabled=1
            ).order_by("name")

        return context

    def form_valid(self, form):
        """Save subcategory and permissions."""
        # Ensure parent_category is set (subcategory requirement)
        if not form.instance.parent_category_id:
            form.add_error("parent_category", _("Subcategory must have a parent category."))
            return self.form_invalid(form)

        response = super().form_valid(form)

        # Save permission formset
        permission_formset = TicketCategoryPermissionFormSet(
            self.request.POST, instance=self.object
        )

        # Set request on all forms in formset
        for perm_form in permission_formset.forms:
            perm_form.request = self.request

        if permission_formset.is_valid():
            company_id = self.request.session.get("active_company_id")
            for permission in permission_formset.save(commit=False):
                permission.company_id = company_id
                if permission.category:
                    permission.category_code = permission.category.public_code
                permission.save()
            permission_formset.save()
        else:
            # If formset is invalid, return form with errors
            return self.form_invalid(form)

        messages.success(self.request, _("Subcategory updated successfully."))
        return response


class TicketSubcategoryDeleteView(FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView):
    """View for deleting a ticket subcategory."""

    model = models.TicketCategory
    template_name = "shared/generic/generic_confirm_delete.html"
    success_url = reverse_lazy("ticketing:subcategories")
    feature_code = "ticketing.management.subcategories"
    required_action = "delete_own"

    def get_queryset(self):
        """Filter by company and ensure it's a subcategory."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketCategory.objects.filter(
            company_id=company_id, parent_category__isnull=False
        )

    def delete(self, request, *args, **kwargs):
        """Delete subcategory and show success message."""
        messages.success(self.request, _("Subcategory deleted successfully."))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["delete_title"] = _("Delete Subcategory")
        context["confirmation_message"] = _("Are you sure you want to delete this subcategory?")
        context["object_details"] = [
            {"label": _("Name"), "value": self.object.name},
        ]
        if self.object.public_code:
            context["object_details"].append({"label": _("Code"), "value": f"<code>{self.object.public_code}</code>"})
        if self.object.description:
            context["object_details"].append({"label": _("Description"), "value": self.object.description})
        if self.object.parent_category:
            context["object_details"].append({"label": _("Parent Category"), "value": self.object.parent_category.name})
        
        context["cancel_url"] = reverse_lazy("ticketing:subcategories")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Subcategories"), "url": reverse_lazy("ticketing:subcategories")},
            {"label": _("Delete"), "url": None},
        ]
        return context

