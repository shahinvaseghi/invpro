"""
Views for ticket category management.
"""
from typing import Dict, Any

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .. import models
from ..forms.categories import TicketCategoryForm, TicketCategoryPermissionFormSet
from .base import TicketingBaseView
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin


class TicketCategoryListView(FeaturePermissionRequiredMixin, TicketingBaseView, ListView):
    """List view for ticket categories."""

    model = models.TicketCategory
    template_name = "ticketing/categories_list.html"
    context_object_name = "object_list"
    paginate_by = 50
    feature_code = "ticketing.management.categories"
    required_action = "view_all"

    def get_queryset(self):
        """Filter categories by company and search."""
        company_id = self.request.session.get("active_company_id")
        queryset = models.TicketCategory.objects.filter(company_id=company_id)

        search = self.request.GET.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(name_en__icontains=search)
                | Q(public_code__icontains=search)
            )

        # Filter by parent (main categories vs subcategories)
        parent_filter = self.request.GET.get("parent_filter", "")
        if parent_filter == "main":
            queryset = queryset.filter(parent_category__isnull=True)
        elif parent_filter == "sub":
            queryset = queryset.filter(parent_category__isnull=False)

        return queryset.order_by("sort_order", "public_code", "name")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        if 'page_obj' in context and hasattr(context['page_obj'], 'object_list'):
            context['object_list'] = context['page_obj'].object_list
        elif 'object_list' in context and hasattr(context['object_list'], 'query'):
            context['object_list'] = list(context['object_list'])
        
        context["page_title"] = _("Ticket Categories")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Categories"), "url": None},
        ]
        context["create_url"] = reverse_lazy("ticketing:category_create")
        context["create_button_text"] = _("Create Category")
        context["show_filters"] = True
        context["parent_filter_value"] = self.request.GET.get("parent_filter", "")
        context["search_placeholder"] = _("Search by name or code")
        context["clear_filter_url"] = reverse_lazy("ticketing:categories")
        context["show_actions"] = True
        context["feature_code"] = "ticketing.management.categories"
        context["detail_url_name"] = "ticketing:category_detail"
        context["edit_url_name"] = "ticketing:category_edit"
        context["delete_url_name"] = "ticketing:category_delete"
        context["empty_state_title"] = _("No Categories Found")
        context["empty_state_message"] = _("Start by creating your first category.")
        context["empty_state_icon"] = "📁"
        return context


class TicketCategoryCreateView(FeaturePermissionRequiredMixin, TicketingBaseView, CreateView):
    """View for creating a new ticket category."""

    model = models.TicketCategory
    form_class = TicketCategoryForm
    template_name = "ticketing/category_form.html"
    success_url = reverse_lazy("ticketing:categories")
    feature_code = "ticketing.management.categories"
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
        context["form_title"] = _("Create Category")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Categories"), "url": reverse_lazy("ticketing:categories")},
            {"label": _("Create"), "url": None},
        ]
        context["cancel_url"] = reverse_lazy("ticketing:categories")

        # Create permission formset for new category
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
        return context

    def form_valid(self, form):
        """Save category and permissions."""
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

        messages.success(self.request, _("Category created successfully."))
        return response


class TicketCategoryUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, TicketingBaseView, UpdateView):
    """View for editing an existing ticket category."""

    model = models.TicketCategory
    form_class = TicketCategoryForm
    template_name = "ticketing/category_form.html"
    success_url = reverse_lazy("ticketing:categories")
    feature_code = "ticketing.management.categories"
    required_action = "edit_own"

    def get_form_kwargs(self):
        """Add request to form kwargs."""
        kwargs = super().get_form_kwargs()
        form = TicketCategoryForm(**kwargs)
        form.request = self.request
        return kwargs

    def get_queryset(self):
        """Filter by company."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketCategory.objects.filter(company_id=company_id)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including permission formset."""
        context = super().get_context_data(**kwargs)
        context["form_title"] = _("Edit Category")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Categories"), "url": reverse_lazy("ticketing:categories")},
            {"label": _("Edit"), "url": None},
        ]
        context["cancel_url"] = reverse_lazy("ticketing:categories")

        # Create permission formset for existing category
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
        return context

    def form_valid(self, form):
        """Save category and permissions."""
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

        messages.success(self.request, _("Category updated successfully."))
        return response


class TicketCategoryDetailView(FeaturePermissionRequiredMixin, TicketingBaseView, DetailView):
    """Detail view for viewing ticket categories (read-only)."""
    model = models.TicketCategory
    template_name = "ticketing/category_detail.html"
    context_object_name = "category"
    feature_code = "ticketing.management.categories"
    required_action = "view_all"
    
    def get_queryset(self):
        """Filter by company."""
        company_id = self.request.session.get("active_company_id")
        if not company_id:
            return models.TicketCategory.objects.none()
        queryset = models.TicketCategory.objects.filter(company_id=company_id)
        queryset = queryset.select_related(
            'parent_category',
            'created_by',
            'edited_by',
        ).prefetch_related('subcategories')
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for detail template."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("View Category")
        context["list_url"] = reverse_lazy("ticketing:categories")
        context["edit_url"] = reverse_lazy("ticketing:category_edit", kwargs={"pk": self.object.pk})
        context["can_edit"] = not getattr(self.object, "is_locked", 0) if hasattr(self.object, "is_locked") else True
        context["feature_code"] = "ticketing.management.categories"
        return context


class TicketCategoryDeleteView(FeaturePermissionRequiredMixin, TicketingBaseView, DeleteView):
    """View for deleting a ticket category."""

    model = models.TicketCategory
    template_name = "shared/generic/generic_confirm_delete.html"
    success_url = reverse_lazy("ticketing:categories")
    feature_code = "ticketing.management.categories"
    required_action = "delete_own"

    def get_queryset(self):
        """Filter by company."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketCategory.objects.filter(company_id=company_id)

    def delete(self, request, *args, **kwargs):
        """Delete category and show success message."""
        messages.success(self.request, _("Category deleted successfully."))
        return super().delete(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["delete_title"] = _("Delete Category")
        context["confirmation_message"] = _("Are you sure you want to delete this category?")
        context["object_details"] = [
            {"label": _("Name"), "value": self.object.name},
        ]
        if self.object.public_code:
            context["object_details"].append({"label": _("Code"), "value": f"<code>{self.object.public_code}</code>"})
        if self.object.description:
            context["object_details"].append({"label": _("Description"), "value": self.object.description})
        
        if self.object.subcategories.exists():
            context["warning_message"] = _("This category has {count} subcategory(ies). They will also be deleted.").format(
                count=self.object.subcategories.count()
            )
        
        context["cancel_url"] = reverse_lazy("ticketing:categories")
        context["breadcrumbs"] = [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Categories"), "url": reverse_lazy("ticketing:categories")},
            {"label": _("Delete"), "url": None},
        ]
        return context

