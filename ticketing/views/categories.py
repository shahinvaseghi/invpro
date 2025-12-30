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
from shared.views.base import (
    BaseListView,
    BaseFormsetCreateView,
    BaseFormsetUpdateView,
    BaseDetailView,
    BaseDeleteView,
    EditLockProtectedMixin,
)


class TicketCategoryListView(BaseListView):
    """List view for ticket categories."""

    model = models.TicketCategory
    template_name = "ticketing/categories_list.html"
    context_object_name = "object_list"
    paginate_by = 50
    feature_code = "ticketing.management.categories"
    required_action = "view_all"
    active_module = "ticketing"
    default_order_by = ["sort_order", "public_code", "name"]

    def get_base_queryset(self):
        """Filter categories by company."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketCategory.objects.filter(company_id=company_id)

    def get_search_fields(self) -> list:
        """Return list of fields to search in."""
        return ["name", "name_en", "public_code"]

    def get_queryset(self):
        """Filter categories by company, search, and parent filter."""
        queryset = super().get_queryset()

        # Filter by parent (main categories vs subcategories)
        parent_filter = self.request.GET.get("parent_filter", "")
        if parent_filter == "main":
            queryset = queryset.filter(parent_category__isnull=True)
        elif parent_filter == "sub":
            queryset = queryset.filter(parent_category__isnull=False)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        context["parent_filter_value"] = self.request.GET.get("parent_filter", "")
        return context

    def get_page_title(self) -> str:
        """Return page title."""
        return _("Ticket Categories")

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Categories"), "url": None},
        ]

    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy("ticketing:category_create")

    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _("Create Category")

    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return "ticketing:category_detail"

    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return "ticketing:category_edit"

    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return "ticketing:category_delete"

    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _("No Categories Found")

    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _("Start by creating your first category.")

    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return "📁"


class TicketCategoryCreateView(BaseFormsetCreateView):
    """View for creating a new ticket category."""

    model = models.TicketCategory
    form_class = TicketCategoryForm
    template_name = "ticketing/category_form.html"
    success_url = reverse_lazy("ticketing:categories")
    feature_code = "ticketing.management.categories"
    required_action = "create"
    active_module = "ticketing"
    success_message = _("Category created successfully.")
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
            {"label": _("Categories"), "url": reverse_lazy("ticketing:categories")},
            {"label": _("Create"), "url": None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy("ticketing:categories")

    def get_form_title(self) -> str:
        """Return form title."""
        return _("Create Category")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including permission formset."""
        context = super().get_context_data(**kwargs)

        # Set request on all forms in formset
        if "formset" in context:
            for form in context["formset"].forms:
                form.request = self.request

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
        """Save category and permissions."""
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


class TicketCategoryUpdateView(BaseFormsetUpdateView, EditLockProtectedMixin):
    """View for editing an existing ticket category."""

    model = models.TicketCategory
    form_class = TicketCategoryForm
    template_name = "ticketing/category_form.html"
    success_url = reverse_lazy("ticketing:categories")
    feature_code = "ticketing.management.categories"
    required_action = "edit_own"
    active_module = "ticketing"
    success_message = _("Category updated successfully.")
    formset_class = TicketCategoryPermissionFormSet
    formset_prefix = "permissions"

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

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Categories"), "url": reverse_lazy("ticketing:categories")},
            {"label": _("Edit"), "url": None},
        ]

    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy("ticketing:categories")

    def get_form_title(self) -> str:
        """Return form title."""
        return _("Edit Category")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data including permission formset."""
        context = super().get_context_data(**kwargs)

        # Set request on all forms in formset
        if "formset" in context:
            for form in context["formset"].forms:
                form.request = self.request

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
        """Save category and permissions."""
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


class TicketCategoryDetailView(BaseDetailView):
    """Detail view for viewing ticket categories (read-only)."""
    model = models.TicketCategory
    template_name = "shared/generic/generic_detail.html"
    context_object_name = "object"
    feature_code = "ticketing.management.categories"
    required_action = "view_all"
    active_module = "ticketing"
    
    def get_queryset(self):
        """Filter by company and optimize queries."""
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
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Ticket Category')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        category = self.object
        
        context['detail_title'] = self.get_page_title()
        context['info_banner'] = [
            {'label': _('Code'), 'value': category.public_code, 'type': 'code'},
            {'label': _('Status'), 'value': category.is_enabled, 'type': 'badge'},
        ]
        
        # Basic Information section
        basic_fields = [
            {'label': _('Name'), 'value': category.name},
        ]
        if category.name_en:
            basic_fields.append({'label': _('Name (EN)'), 'value': category.name_en})
        if category.parent_category:
            basic_fields.append({
                'label': _('Parent Category'),
                'value': category.parent_category.name,
            })
        if category.description:
            basic_fields.append({'label': _('Description'), 'value': category.description})
        
        detail_sections = [
            {
                'title': _('Basic Information'),
                'fields': basic_fields,
            },
        ]
        
        # Subcategories section
        if category.subcategories.exists():
            subcategories_text = ', '.join([subcat.name for subcat in category.subcategories.all()])
            detail_sections.append({
                'title': _('Subcategories'),
                'fields': [
                    {'label': _('Subcategories'), 'value': subcategories_text},
                ],
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy("ticketing:categories")
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy("ticketing:category_edit", kwargs={"pk": self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, "is_locked"):
            return not bool(check_obj.is_locked)
        return True


class TicketCategoryDeleteView(BaseDeleteView):
    """View for deleting a ticket category."""

    model = models.TicketCategory
    template_name = "shared/generic/generic_confirm_delete.html"
    success_url = reverse_lazy("ticketing:categories")
    feature_code = "ticketing.management.categories"
    required_action = "delete_own"
    active_module = "ticketing"
    success_message = _("Category deleted successfully.")

    def get_queryset(self):
        """Filter by company."""
        company_id = self.request.session.get("active_company_id")
        return models.TicketCategory.objects.filter(company_id=company_id)

    def get_delete_title(self) -> str:
        """Return delete title."""
        return _("Delete Category")

    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _("Are you sure you want to delete this category?")

    def get_object_details(self) -> list:
        """Return object details for confirmation."""
        details = [
            {"label": _("Name"), "value": self.object.name},
        ]
        if self.object.public_code:
            details.append({"label": _("Code"), "value": f"<code>{self.object.public_code}</code>"})
        if self.object.description:
            details.append({"label": _("Description"), "value": self.object.description})
        return details

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context data."""
        context = super().get_context_data(**kwargs)
        
        # Add warning message if category has subcategories
        if self.object.subcategories.exists():
            context["warning_message"] = _("This category has {count} subcategory(ies). They will also be deleted.").format(
                count=self.object.subcategories.count()
            )
        
        return context

    def get_breadcrumbs(self) -> list:
        """Return breadcrumbs list."""
        return [
            {"label": _("Ticket Management"), "url": None},
            {"label": _("Categories"), "url": reverse_lazy("ticketing:categories")},
            {"label": _("Delete"), "url": None},
        ]

