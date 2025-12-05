"""
Master data views for inventory module.

This module contains CRUD views for:
- Item Types
- Item Categories
- Item Subcategories
- Items
- Warehouses
- Suppliers
- Supplier Categories
"""
import logging
from typing import Dict, Any, List
from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .base import InventoryBaseView, ItemUnitFormsetMixin
from .receipts import DocumentDeleteViewBase
from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    EditLockProtectedMixin,
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
    BaseDetailView,
)
from .. import models
from .. import forms

logger = logging.getLogger('inventory.views.master_data')


# ============================================================================
# Item Type Views
# ============================================================================

class ItemTypeListView(InventoryBaseView, ListView):
    """List view for item types."""
    model = models.ItemType
    template_name = 'inventory/item_types.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_types', 'created_by')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Item Types')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Types'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:itemtype_create')
        context['create_button_text'] = _('Create Item Type')
        context['table_headers'] = []  # Overridden in template
        context['show_actions'] = True
        context['feature_code'] = 'inventory.master.item_types'
        context['detail_url_name'] = 'inventory:itemtype_detail'
        context['edit_url_name'] = 'inventory:itemtype_edit'
        context['delete_url_name'] = 'inventory:itemtype_delete'
        context['empty_state_title'] = _('No Item Types Found')
        context['empty_state_message'] = _('Start by creating your first item type.')
        context['empty_state_icon'] = '🏷️'
        return context


class ItemTypeCreateView(InventoryBaseView, CreateView):
    """Create view for item types."""
    model = models.ItemType
    form_class = forms.ItemTypeForm
    template_name = 'inventory/itemtype_form.html'
    success_url = reverse_lazy('inventory:item_types')
    
    def form_valid(self, form):
        """Set company and created_by before saving."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Item Type created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic form template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Type')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('inventory:item_types')
        return context


class ItemTypeUpdateView(InventoryBaseView, BaseUpdateView):
    """Update view for item types."""
    model = models.ItemType
    form_class = forms.ItemTypeForm
    template_name = 'inventory/itemtype_form.html'
    success_url = reverse_lazy('inventory:item_types')
    feature_code = 'inventory.master.item_types'
    success_message = _('Item Type updated successfully.')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_types', 'created_by')
        return queryset
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Item Type')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:item_types')


class ItemTypeDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing item types (read-only)."""
    model = models.ItemType
    template_name = 'inventory/itemtype_detail.html'
    context_object_name = 'itemtype'
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_types', 'created_by')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('inventory:item_types')
        context['edit_url'] = reverse_lazy('inventory:itemtype_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        return context


class ItemTypeDeleteView(InventoryBaseView, DeleteView):
    """Delete view for item types."""
    model = models.ItemType
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_types')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_types', 'created_by')
        return queryset
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion with ProtectedError handling."""
        self.object = self.get_object()
        logger.info(f"Attempting to delete item type: {self.object}")
        logger.info(f"Item Type ID: {self.object.pk}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Item Type {self.object.pk} deleted successfully")
            messages.success(self.request, _('Item Type deleted successfully.'))
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            logger.error(f"ProtectedError when deleting item type {self.object.pk}: {e}")
            logger.error(f"Protected objects: {e.protected_objects}")
            
            # Model name mapping to Persian
            model_name_map = {
                'Item': _('کالا'),
                'Items': _('کالاها'),
                'BOMMaterial': _('ماده اولیه BOM'),
                'BOMMaterials': _('مواد اولیه BOM'),
            }
            
            # Extract model names from protected objects
            protected_models = set()
            protected_count = {}
            for obj in e.protected_objects:
                model_name = obj._meta.verbose_name
                # Use Persian name if available, otherwise use original
                persian_name = model_name_map.get(model_name, model_name)
                protected_models.add(persian_name)
                protected_count[persian_name] = protected_count.get(persian_name, 0) + 1
            
            # Create user-friendly error message
            error_parts = []
            for model_name, count in protected_count.items():
                error_parts.append(f"{count} {model_name}")
            
            error_message = _('Cannot delete this item type because it is used in {models}.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Item Type')
        context['confirmation_message'] = _('Are you sure you want to delete this item type?')
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.public_code},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Name (EN)'), 'value': self.object.name_en or '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:item_types')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Types'), 'url': reverse_lazy('inventory:item_types')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


# ============================================================================
# Item Category Views
# ============================================================================

class ItemCategoryListView(InventoryBaseView, ListView):
    """List view for item categories."""
    model = models.ItemCategory
    template_name = 'inventory/item_categories.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_categories', 'created_by')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Item Categories')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Categories'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:itemcategory_create')
        context['create_button_text'] = _('Create Item Category')
        context['table_headers'] = []  # Overridden in template
        context['show_actions'] = True
        context['feature_code'] = 'inventory.master.item_categories'
        context['detail_url_name'] = 'inventory:itemcategory_detail'
        context['edit_url_name'] = 'inventory:itemcategory_edit'
        context['delete_url_name'] = 'inventory:itemcategory_delete'
        context['empty_state_title'] = _('No Item Categories Found')
        context['empty_state_message'] = _('Start by creating your first item category.')
        context['empty_state_icon'] = '📦'
        return context


class ItemCategoryCreateView(InventoryBaseView, CreateView):
    """Create view for item categories."""
    model = models.ItemCategory
    form_class = forms.ItemCategoryForm
    template_name = 'inventory/itemcategory_form.html'
    success_url = reverse_lazy('inventory:item_categories')
    
    def form_valid(self, form):
        """Set company and created_by before saving."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Item Category created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic form template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Category')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Categories'), 'url': reverse_lazy('inventory:item_categories')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('inventory:item_categories')
        return context


class ItemCategoryUpdateView(InventoryBaseView, BaseUpdateView):
    """Update view for item categories."""
    model = models.ItemCategory
    form_class = forms.ItemCategoryForm
    template_name = 'inventory/itemcategory_form.html'
    success_url = reverse_lazy('inventory:item_categories')
    feature_code = 'inventory.master.item_categories'
    success_message = _('Item Category updated successfully.')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_categories', 'created_by')
        return queryset
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Item Category')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Categories'), 'url': reverse_lazy('inventory:item_categories')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:item_categories')


class ItemCategoryDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing item categories (read-only)."""
    model = models.ItemCategory
    template_name = 'inventory/itemcategory_detail.html'
    context_object_name = 'itemcategory'
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_categories', 'created_by')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('inventory:item_categories')
        context['edit_url'] = reverse_lazy('inventory:itemcategory_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        return context


class ItemCategoryDeleteView(InventoryBaseView, DeleteView):
    """Delete view for item categories."""
    model = models.ItemCategory
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_categories')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_categories', 'created_by')
        return queryset
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion with ProtectedError handling."""
        self.object = self.get_object()
        logger.info(f"Attempting to delete item category: {self.object}")
        logger.info(f"Item Category ID: {self.object.pk}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Item Category {self.object.pk} deleted successfully")
            messages.success(self.request, _('Item Category deleted successfully.'))
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            logger.error(f"ProtectedError when deleting item category {self.object.pk}: {e}")
            logger.error(f"Protected objects: {e.protected_objects}")
            
            # Model name mapping
            model_name_map = {
                'Item': _('Item'),
                'Items': _('Items'),
                'Item Subcategory': _('Item Subcategory'),
                'Item Subcategories': _('Item Subcategories'),
            }
            
            # Extract model names from protected objects
            protected_models = set()
            protected_count = {}
            for obj in e.protected_objects:
                model_name = obj._meta.verbose_name
                persian_name = model_name_map.get(model_name, model_name)
                protected_models.add(persian_name)
                protected_count[persian_name] = protected_count.get(persian_name, 0) + 1
            
            # Create user-friendly error message
            error_parts = []
            for model_name, count in protected_count.items():
                error_parts.append(f"{count} {model_name}")
            
            error_message = _('Cannot delete this item category because it is used in {models}.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Item Category')
        context['confirmation_message'] = _('Are you sure you want to delete this item category?')
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.public_code},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Name (EN)'), 'value': self.object.name_en or '-'},
            {'label': _('Item Type'), 'value': self.object.item_type.name if self.object.item_type else '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:item_categories')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Categories'), 'url': reverse_lazy('inventory:item_categories')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


# ============================================================================
# Item Subcategory Views
# ============================================================================

class ItemSubcategoryListView(InventoryBaseView, ListView):
    """List view for item subcategories."""
    model = models.ItemSubcategory
    template_name = 'inventory/item_subcategories.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_subcategories', 'created_by')
        queryset = queryset.select_related('category')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Item Subcategories')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Subcategories'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:itemsubcategory_create')
        context['create_button_text'] = _('Create Item Subcategory')
        context['table_headers'] = []  # Overridden in template
        context['show_actions'] = True
        context['feature_code'] = 'inventory.master.item_subcategories'
        context['detail_url_name'] = 'inventory:itemsubcategory_detail'
        context['edit_url_name'] = 'inventory:itemsubcategory_edit'
        context['delete_url_name'] = 'inventory:itemsubcategory_delete'
        context['empty_state_title'] = _('No Item Subcategories Found')
        context['empty_state_message'] = _('Start by creating your first item subcategory.')
        context['empty_state_icon'] = '📋'
        return context


class ItemSubcategoryCreateView(InventoryBaseView, CreateView):
    """Create view for item subcategories."""
    model = models.ItemSubcategory
    form_class = forms.ItemSubcategoryForm
    template_name = 'inventory/itemsubcategory_form.html'
    success_url = reverse_lazy('inventory:item_subcategories')
    
    def form_valid(self, form):
        """Set company and created_by before saving."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Item Subcategory created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic form template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Subcategory')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Subcategories'), 'url': reverse_lazy('inventory:item_subcategories')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('inventory:item_subcategories')
        return context


class ItemSubcategoryUpdateView(InventoryBaseView, BaseUpdateView):
    """Update view for item subcategories."""
    model = models.ItemSubcategory
    form_class = forms.ItemSubcategoryForm
    template_name = 'inventory/itemsubcategory_form.html'
    success_url = reverse_lazy('inventory:item_subcategories')
    feature_code = 'inventory.master.item_subcategories'
    success_message = _('Item Subcategory updated successfully.')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_subcategories', 'created_by')
        return queryset
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Item Subcategory')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Subcategories'), 'url': reverse_lazy('inventory:item_subcategories')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:item_subcategories')


class ItemSubcategoryDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing item subcategories (read-only)."""
    model = models.ItemSubcategory
    template_name = 'inventory/itemsubcategory_detail.html'
    context_object_name = 'itemsubcategory'
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_subcategories', 'created_by')
        queryset = queryset.select_related('category')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('inventory:item_subcategories')
        context['edit_url'] = reverse_lazy('inventory:itemsubcategory_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        return context


class ItemSubcategoryDeleteView(DocumentDeleteViewBase):
    """Delete view for item subcategories."""
    model = models.ItemSubcategory
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_subcategories')
    feature_code = 'inventory.master.item_subcategories'
    required_action = 'delete_own'
    allow_own_scope = True
    success_message = _('زیردسته کالا با موفقیت حذف شد.')
    
    def get_context_data(self, **kwargs):
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Item Subcategory')
        context['confirmation_message'] = _('Do you really want to delete this item subcategory?')
        context['object_details'] = [
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Category'), 'value': str(self.object.category) if self.object.category else '-'},
            {'label': _('Item Type'), 'value': str(self.object.item_type) if self.object.item_type else '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:item_subcategories')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Subcategories'), 'url': reverse_lazy('inventory:item_subcategories')},
            {'label': _('Delete'), 'url': None},
        ]
        return context
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion with ProtectedError handling."""
        self.object = self.get_object()
        logger.info(f"Attempting to delete item subcategory: {self.object}")
        logger.info(f"Item Subcategory ID: {self.object.pk}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Item Subcategory {self.object.pk} deleted successfully")
            messages.success(self.request, _('زیر دسته‌بندی کالا با موفقیت حذف شد.'))
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            logger.error(f"ProtectedError when deleting item subcategory {self.object.pk}: {e}")
            logger.error(f"Protected objects: {e.protected_objects}")
            
            # Model name mapping to Persian
            model_name_map = {
                'Item': _('کالا'),
                'Items': _('کالاها'),
            }
            
            # Extract model names from protected objects
            protected_models = set()
            protected_count = {}
            for obj in e.protected_objects:
                model_name = obj._meta.verbose_name
                # Use Persian name if available, otherwise use original
                persian_name = model_name_map.get(model_name, model_name)
                protected_models.add(persian_name)
                protected_count[persian_name] = protected_count.get(persian_name, 0) + 1
            
            # Create user-friendly error message
            error_parts = []
            for model_name, count in protected_count.items():
                error_parts.append(f"{count} {model_name}")
            
            error_message = _('نمی‌توان این زیر دسته‌بندی کالا را حذف کرد چون در ساختار {models} استفاده شده است.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())


# ============================================================================
# Item Views
# ============================================================================

class ItemListView(BaseListView):
    """List view for items."""
    model = models.Item
    template_name = 'inventory/items.html'
    feature_code = 'inventory.master.items'
    search_fields = ['item_code', 'name', 'name_en']
    filter_fields = ['is_enabled']
    default_status_filter = True
    default_order_by = ['-created_at', '-id']
    permission_field = 'created_by'
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['type', 'category', 'subcategory']
    
    def apply_custom_filters(self, queryset):
        """Apply custom filters for item type and category."""
        queryset = super().apply_custom_filters(queryset)
        
        # Filter by item type
        item_type_id = self.request.GET.get('type')
        if item_type_id:
            try:
                queryset = queryset.filter(type_id=int(item_type_id))
            except (ValueError, TypeError):
                pass
        
        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                queryset = queryset.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Items')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Items'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:item_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create New Item')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Search by code or name')
    
    def get_clear_filter_url(self):
        """Return clear filter URL."""
        return reverse_lazy('inventory:items')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:item_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:item_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'inventory:item_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Items Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first item.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📦'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add additional context variables."""
        context = super().get_context_data(**kwargs)
        from shared.utils.permissions import get_user_feature_permissions
        
        context['print_enabled'] = True
        
        # Add item types and categories for filter dropdown
        company_id = self.request.session.get('active_company_id')
        if company_id:
            context['item_types'] = models.ItemType.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('name')
            context['item_categories'] = models.ItemCategory.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('name')
        
        # Add user feature permissions for conditional rendering
        context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, company_id)
        
        return context


class ItemSerialListView(BaseListView):
    """List view for item serials."""
    model = models.ItemSerial
    template_name = 'inventory/item_serials.html'
    context_object_name = 'serials'
    feature_code = 'inventory.master.item_serials'
    paginate_by = 100
    default_order_by = ['-created_at', '-id']
    permission_field = ''  # Skip permission filtering (ItemSerial is read-only)
    default_status_filter = False  # Custom status filter
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['item', 'receipt_document', 'current_warehouse']
    
    def apply_custom_filters(self, queryset):
        """Apply custom filters for receipt_code, item_code, serial_code, and status."""
        queryset = super().apply_custom_filters(queryset)
        
        receipt_code = (self.request.GET.get('receipt_code') or '').strip()
        item_code = (self.request.GET.get('item_code') or '').strip()
        serial_code = (self.request.GET.get('serial_code') or '').strip()
        status = (self.request.GET.get('status') or '').strip()
        
        if receipt_code:
            queryset = queryset.filter(receipt_document_code__icontains=receipt_code)
        if item_code:
            queryset = queryset.filter(item__item_code__icontains=item_code)
        if serial_code:
            queryset = queryset.filter(serial_code__icontains=serial_code)
        if status:
            queryset = queryset.filter(current_status=status)
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Item Serials')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Item Serials'), 'url': None},
        ]
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Search by receipt code, item code, or serial code')
    
    def get_clear_filter_url(self):
        """Return clear filter URL."""
        return reverse_lazy('inventory:item_serials')
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Item Serials Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('No item serials found matching your criteria.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '🔢'
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add additional context variables."""
        context = super().get_context_data(**kwargs)
        
        # ItemSerial is read-only, no view/edit buttons needed
        context['show_actions'] = False
        
        # Add filter values to context for template
        context['receipt_code'] = (self.request.GET.get('receipt_code') or '').strip()
        context['item_code'] = (self.request.GET.get('item_code') or '').strip()
        context['serial_code'] = (self.request.GET.get('serial_code') or '').strip()
        context['status'] = (self.request.GET.get('status') or '').strip()
        context['status_choices'] = models.ItemSerial.Status.choices
        context['has_filters'] = any([
            context['receipt_code'],
            context['item_code'],
            context['serial_code'],
            context['status'],
        ])
        
        return context


class ItemCreateView(ItemUnitFormsetMixin, BaseCreateView):
    """Create view for items with unit formset."""
    model = models.Item
    form_class = forms.ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:items')
    feature_code = 'inventory.master.items'
    required_action = 'create'
    success_message = _('کالا با موفقیت ایجاد شد.')
    
    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        company_id = self.request.session.get('active_company_id')
        if company_id:
            kwargs['company_id'] = company_id
        return kwargs
    
    def form_valid(self, form):
        """Save item and unit formset."""
        from django.http import HttpResponseRedirect
        
        company_id = self.request.session.get('active_company_id')
        
        # company_id and created_by are set by AutoSetFieldsMixin
        form.instance.edited_by = self.request.user
        
        # Build formset with instance=None for new items
        # Use a temporary instance to build the formset
        temp_instance = models.Item(company_id=company_id)
        units_formset = self.build_unit_formset(data=self.request.POST, instance=temp_instance, company_id=company_id)
        
        # Check if there are any forms with data in POST
        has_forms_with_data = False
        prefix = units_formset.prefix or 'units'
        total_forms = int(self.request.POST.get(f'{prefix}-TOTAL_FORMS', 0))
        
        for i in range(total_forms):
            # Check if any visible field has data
            visible_fields = ['from_quantity', 'from_unit', 'to_quantity', 'to_unit', 'description', 'notes']
            for field in visible_fields:
                field_name = f'{prefix}-{i}-{field}'
                if self.request.POST.get(field_name):
                    has_forms_with_data = True
                    break
            if has_forms_with_data:
                break
        
        # Validate formset only if there are forms with data
        if has_forms_with_data:
            formset_valid = units_formset.is_valid()
            
            if not formset_valid:
                return self.render_to_response(
                    self.get_context_data(form=form, units_formset=units_formset)
                )
        
        # Explicitly set checkbox values BEFORE saving form
        # IntegerCheckboxField should handle this, but we ensure values are set correctly
        checkbox_fields = ['is_sellable', 'has_lot_tracking', 'requires_temporary_receipt', 'serial_in_qc', 'is_enabled']
        for field_name in checkbox_fields:
            # First try to get from cleaned_data (processed by IntegerCheckboxField)
            value = form.cleaned_data.get(field_name)
            if value is None:
                # If not in cleaned_data, check POST directly
                # IntegerCheckboxInput returns '1' when checked, field not in POST when unchecked
                if field_name in self.request.POST:
                    post_value = self.request.POST.get(field_name)
                    if post_value in ('1', 'on', 1):
                        value = 1
                    else:
                        value = 0
                else:
                    value = 0
            else:
                # Ensure value is 0 or 1
                try:
                    value = 1 if int(value) == 1 else 0
                except (ValueError, TypeError):
                    value = 0
            # Set value directly on instance before save
            setattr(form.instance, field_name, value)
        
        # Save the item (now with correct checkbox values)
        self.object = form.save()
        
        # Now rebuild formset with the saved instance and save units
        if has_forms_with_data:
            units_formset = self.build_unit_formset(data=self.request.POST, instance=self.object, company_id=company_id)
            if units_formset.is_valid():
                self._save_unit_formset(units_formset)
        
        ordered = self._get_ordered_warehouses(form)
        self._sync_item_warehouses(self.object, ordered, self.request.user)
        
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add unit formset to context."""
        context = super().get_context_data(**kwargs)
        company_id = self.request.session.get('active_company_id')
        
        # Build unit formset for new items
        if 'units_formset' not in context:
            temp_instance = models.Item(company_id=company_id) if company_id else models.Item()
            context['units_formset'] = self.build_unit_formset(instance=temp_instance, company_id=company_id)
        
        return context
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Items'), 'url': reverse_lazy('inventory:items')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create New Item')
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:items')


class ItemUpdateView(EditLockProtectedMixin, ItemUnitFormsetMixin, InventoryBaseView, UpdateView):
    """Update view for items with unit formset."""
    model = models.Item
    form_class = forms.ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:items')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.items', 'created_by')
        return queryset
    
    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        instance = kwargs.get('instance')
        company_id = instance.company_id if instance else self.request.session.get('active_company_id')
        kwargs['company_id'] = company_id
        return kwargs
    
    def form_valid(self, form):
        """Save item and unit formset."""
        from django.http import HttpResponseRedirect
        
        company_id = form.instance.company_id
        units_formset = self.build_unit_formset(data=self.request.POST, instance=form.instance)
        if not units_formset.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, units_formset=units_formset)
            )
        form.instance.edited_by = self.request.user
        
        # Explicitly update checkbox values BEFORE saving form
        # IntegerCheckboxField should handle this, but we ensure values are set correctly
        checkbox_fields = ['is_sellable', 'has_lot_tracking', 'requires_temporary_receipt', 'serial_in_qc', 'is_enabled']
        for field_name in checkbox_fields:
            # First try to get from cleaned_data (processed by IntegerCheckboxField)
            value = form.cleaned_data.get(field_name)
            if value is None:
                # If not in cleaned_data, check POST directly
                # IntegerCheckboxInput returns '1' when checked, field not in POST when unchecked
                if field_name in self.request.POST:
                    post_value = self.request.POST.get(field_name)
                    if post_value in ('1', 'on', 1):
                        value = 1
                    else:
                        value = 0
                else:
                    value = 0
            else:
                # Ensure value is 0 or 1
                try:
                    value = 1 if int(value) == 1 else 0
                except (ValueError, TypeError):
                    value = 0
            # Set value directly on instance before save
            setattr(form.instance, field_name, value)
        
        # Save form (now with correct checkbox values)
        self.object = form.save()
        units_formset.instance = self.object
        self._save_unit_formset(units_formset)
        ordered = self._get_ordered_warehouses(form)
        self._sync_item_warehouses(self.object, ordered, self.request.user)
        messages.success(self.request, _('اطلاعات کالا با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add unit formset to context."""
        context = super().get_context_data(**kwargs)
        
        # Build unit formset for existing items
        if 'units_formset' not in context:
            context['units_formset'] = self.build_unit_formset(instance=self.object)
        
        context['form_title'] = _('Edit Item')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Items'), 'url': reverse_lazy('inventory:items')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('inventory:items')
        return context


class ItemDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing items (read-only)."""
    model = models.Item
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.items', 'created_by')
        queryset = queryset.select_related('type', 'category', 'subcategory').prefetch_related('warehouses__warehouse', 'units')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('inventory:items')
        context['edit_url'] = reverse_lazy('inventory:item_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        return context


class ItemDeleteView(InventoryBaseView, DeleteView):
    """Delete view for items."""
    model = models.Item
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:items')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.items', 'created_by')
        queryset = queryset.select_related('type', 'category', 'subcategory')
        return queryset
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion with ProtectedError handling."""
        self.object = self.get_object()
        logger.info(f"Attempting to delete item: {self.object}")
        logger.info(f"Item ID: {self.object.pk}, Code: {self.object.full_item_code or self.object.item_code}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Item {self.object.pk} deleted successfully")
            messages.success(self.request, _('Item deleted successfully.'))
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            logger.error(f"ProtectedError when deleting item {self.object.pk}: {e}")
            logger.error(f"Protected objects: {e.protected_objects}")
            
            # Extract model names from protected objects
            protected_models = set()
            protected_count = {}
            for obj in e.protected_objects:
                model_name = obj._meta.verbose_name
                protected_models.add(model_name)
                protected_count[model_name] = protected_count.get(model_name, 0) + 1
            
            # Create user-friendly error message
            error_parts = []
            for model_name, count in protected_count.items():
                error_parts.append(f"{count} {model_name}")
            
            error_message = _('Cannot delete this item because it is used in {models}.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Item')
        context['confirmation_message'] = _('Are you sure you want to delete this item?')
        context['object_details'] = [
            {'label': _('Item Code'), 'value': self.object.item_code},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Name (EN)'), 'value': self.object.name_en or '-'},
            {'label': _('Type'), 'value': self.object.type.name if self.object.type else '-'},
            {'label': _('Category'), 'value': self.object.category.name if self.object.category else '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:items')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Items'), 'url': reverse_lazy('inventory:items')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


# ============================================================================
# Warehouse Views
# ============================================================================


class WarehouseListView(BaseListView):
    """List view for warehouses."""
    model = models.Warehouse
    template_name = 'inventory/warehouses.html'
    feature_code = 'inventory.master.warehouses'
    search_fields = ['public_code', 'name', 'name_en']
    filter_fields = ['is_enabled']
    default_status_filter = True
    default_order_by = ['sort_order', 'public_code']
    permission_field = 'created_by'
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Warehouses')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Warehouses'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('inventory:warehouse_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Warehouse')
    
    def get_search_placeholder(self) -> str:
        """Return search placeholder."""
        return _('Search by code or name')
    
    def get_clear_filter_url(self):
        """Return clear filter URL."""
        return reverse_lazy('inventory:warehouses')
    
    def get_detail_url_name(self) -> str:
        """Return detail URL name."""
        return 'inventory:warehouse_detail'
    
    def get_edit_url_name(self) -> str:
        """Return edit URL name."""
        return 'inventory:warehouse_edit'
    
    def get_delete_url_name(self) -> str:
        """Return delete URL name."""
        return 'inventory:warehouse_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Warehouses Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Start by creating your first warehouse.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '🏬'


class WarehouseCreateView(BaseCreateView):
    """Create view for warehouses."""
    model = models.Warehouse
    form_class = forms.WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouses')
    feature_code = 'inventory.master.warehouses'
    required_action = 'create'
    success_message = _('Warehouse created successfully.')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Warehouses'), 'url': reverse_lazy('inventory:warehouses')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Warehouse')
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:warehouses')


class WarehouseUpdateView(InventoryBaseView, BaseUpdateView):
    """Update view for warehouses."""
    model = models.Warehouse
    form_class = forms.WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouses')
    feature_code = 'inventory.master.warehouses'
    success_message = _('Warehouse updated successfully.')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.warehouses', 'created_by')
        return queryset
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Warehouse')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Warehouses'), 'url': reverse_lazy('inventory:warehouses')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:warehouses')


class WarehouseDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing warehouses (read-only)."""
    model = models.Warehouse
    template_name = 'inventory/warehouse_detail.html'
    context_object_name = 'warehouse'
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.warehouses', 'created_by')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('inventory:warehouses')
        context['edit_url'] = reverse_lazy('inventory:warehouse_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        return context


class WarehouseDeleteView(InventoryBaseView, DeleteView):
    """Delete view for warehouses."""
    model = models.Warehouse
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:warehouses')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.warehouses', 'created_by')
        return queryset
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion with ProtectedError handling."""
        self.object = self.get_object()
        logger.info(f"Attempting to delete warehouse: {self.object}")
        logger.info(f"Warehouse ID: {self.object.pk}, Code: {self.object.public_code}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Warehouse {self.object.pk} deleted successfully")
            messages.success(self.request, _('Warehouse deleted successfully.'))
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            logger.error(f"ProtectedError when deleting warehouse {self.object.pk}: {e}")
            logger.error(f"Protected objects: {e.protected_objects}")
            
            # Model name mapping
            model_name_map = {
                'Consumption Issue Line': _('Consumption Issue Line'),
                'Permanent Receipt Line': _('Permanent Receipt Line'),
                'Consumption Issue Lines': _('Consumption Issue Lines'),
                'Permanent Receipt Lines': _('Permanent Receipt Lines'),
            }
            
            # Extract model names from protected objects
            protected_models = set()
            protected_count = {}
            for obj in e.protected_objects:
                model_name = obj._meta.verbose_name
                persian_name = model_name_map.get(model_name, model_name)
                protected_models.add(persian_name)
                protected_count[persian_name] = protected_count.get(persian_name, 0) + 1
            
            # Create user-friendly error message
            error_parts = []
            for model_name, count in protected_count.items():
                error_parts.append(f"{count} {model_name}")
            
            error_message = _('Cannot delete this warehouse because it is used in {models}.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Warehouse')
        context['confirmation_message'] = _('Are you sure you want to delete this warehouse?')
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.public_code},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('Name (EN)'), 'value': self.object.name_en or '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:warehouses')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Warehouses'), 'url': reverse_lazy('inventory:warehouses')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


# ============================================================================
# Supplier Category Views
# ============================================================================

class SupplierCategoryListView(InventoryBaseView, ListView):
    """List view for supplier categories."""
    model = models.SupplierCategory
    template_name = 'inventory/supplier_categories.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.categories', 'created_by')
        queryset = queryset.select_related('supplier', 'category')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Supplier Categories')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Supplier Categories'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:suppliercategory_create')
        context['create_button_text'] = _('Create Supplier Category')
        context['table_headers'] = []  # Overridden in template
        context['show_actions'] = True
        context['feature_code'] = 'inventory.suppliers.categories'
        context['detail_url_name'] = 'inventory:suppliercategory_detail'
        context['edit_url_name'] = 'inventory:suppliercategory_edit'
        context['delete_url_name'] = 'inventory:suppliercategory_delete'
        context['empty_state_title'] = _('No Supplier Categories Found')
        context['empty_state_message'] = _('Start by creating your first supplier category.')
        context['empty_state_icon'] = '🏷️'
        return context


class SupplierCategoryCreateView(InventoryBaseView, CreateView):
    """Create view for supplier categories."""
    model = models.SupplierCategory
    form_class = forms.SupplierCategoryForm
    template_name = 'inventory/suppliercategory_form.html'
    success_url = reverse_lazy('inventory:supplier_categories')

    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs

    def form_valid(self, form):
        """Set company and created_by before saving."""
        from django.http import HttpResponseRedirect
        
        company_id = self.request.session.get('active_company_id')
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        self.object = form.save()
        self._sync_supplier_links(form)
        messages.success(self.request, _('دسته‌بندی تأمین‌کننده با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def _sync_supplier_links(self, form):
        """Sync supplier subcategories and items."""
        supplier = self.object.supplier
        company = self.object.company
        category = self.object.category
        subcategories = list(form.cleaned_data.get('subcategories') or [])
        items = list(form.cleaned_data.get('items') or [])

        selected_sub_ids = {sub.id for sub in subcategories}
        models.SupplierSubcategory.objects.filter(
            supplier=supplier,
            company=company,
            subcategory__category=category,
        ).exclude(subcategory_id__in=selected_sub_ids).delete()
        for sub in subcategories:
            obj, created = models.SupplierSubcategory.objects.get_or_create(
                supplier=supplier,
                company=company,
                subcategory=sub,
                defaults={
                    'created_by': self.request.user,
                    'edited_by': self.request.user,
                },
            )
            if not created:
                obj.edited_by = self.request.user
                obj.save(update_fields=['edited_by'])

        selected_item_ids = {item.id for item in items}
        models.SupplierItem.objects.filter(
            supplier=supplier,
            company=company,
            item__category=category,
        ).exclude(item_id__in=selected_item_ids).delete()
        for item in items:
            obj, created = models.SupplierItem.objects.get_or_create(
                supplier=supplier,
                company=company,
                item=item,
                defaults={
                    'created_by': self.request.user,
                    'edited_by': self.request.user,
                },
            )
            if not created:
                obj.edited_by = self.request.user
                obj.save(update_fields=['edited_by'])

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic form template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Supplier Category')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Supplier Categories'), 'url': reverse_lazy('inventory:supplier_categories')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('inventory:supplier_categories')
        return context


class SupplierCategoryUpdateView(EditLockProtectedMixin, InventoryBaseView, UpdateView):
    """Update view for supplier categories."""
    model = models.SupplierCategory
    form_class = forms.SupplierCategoryForm
    template_name = 'inventory/suppliercategory_form.html'
    success_url = reverse_lazy('inventory:supplier_categories')

    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.categories', 'created_by')
        return queryset

    def get_form_kwargs(self):
        """Pass company_id to form."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs

    def form_valid(self, form):
        """Set edited_by before saving."""
        from django.http import HttpResponseRedirect
        
        form.instance.edited_by = self.request.user
        self.object = form.save()
        self._sync_supplier_links(form)
        messages.success(self.request, _('دسته‌بندی تأمین‌کننده با موفقیت ویرایش شد.'))
        return HttpResponseRedirect(self.get_success_url())

    def _sync_supplier_links(self, form):
        """Sync supplier subcategories and items."""
        supplier = self.object.supplier
        company = self.object.company
        category = self.object.category
        subcategories = list(form.cleaned_data.get('subcategories') or [])
        items = list(form.cleaned_data.get('items') or [])

        selected_sub_ids = {sub.id for sub in subcategories}
        models.SupplierSubcategory.objects.filter(
            supplier=supplier,
            company=company,
            subcategory__category=category,
        ).exclude(subcategory_id__in=selected_sub_ids).delete()
        for sub in subcategories:
            obj, created = models.SupplierSubcategory.objects.get_or_create(
                supplier=supplier,
                company=company,
                subcategory=sub,
                defaults={
                    'created_by': self.request.user,
                    'edited_by': self.request.user,
                },
            )
            if not created:
                obj.edited_by = self.request.user
                obj.save(update_fields=['edited_by'])

        selected_item_ids = {item.id for item in items}
        models.SupplierItem.objects.filter(
            supplier=supplier,
            company=company,
            item__category=category,
        ).exclude(item_id__in=selected_item_ids).delete()
        for item in items:
            obj, created = models.SupplierItem.objects.get_or_create(
                supplier=supplier,
                company=company,
                item=item,
                defaults={
                    'created_by': self.request.user,
                    'edited_by': self.request.user,
                },
            )
            if not created:
                obj.edited_by = self.request.user
                obj.save(update_fields=['edited_by'])

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic form template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Supplier Category')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Supplier Categories'), 'url': reverse_lazy('inventory:supplier_categories')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('inventory:supplier_categories')
        return context


class SupplierCategoryDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing supplier categories (read-only)."""
    model = models.SupplierCategory
    template_name = 'inventory/suppliercategory_detail.html'
    context_object_name = 'suppliercategory'
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.categories', 'created_by')
        queryset = queryset.select_related('supplier', 'category')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('inventory:supplier_categories')
        context['edit_url'] = reverse_lazy('inventory:suppliercategory_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        return context


class SupplierCategoryDeleteView(InventoryBaseView, DeleteView):
    """Delete view for supplier categories."""
    model = models.SupplierCategory
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_categories')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.categories', 'created_by')
        queryset = queryset.select_related('supplier', 'category')
        return queryset
    
    def delete(self, request, *args, **kwargs):
        """Show success message after deletion."""
        self.object = self.get_object()
        messages.success(self.request, _('Supplier category deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Supplier Category')
        context['confirmation_message'] = _('Are you sure you want to delete this supplier category?')
        context['object_details'] = [
            {'label': _('Supplier'), 'value': self.object.supplier.name if self.object.supplier else '-'},
            {'label': _('Category'), 'value': self.object.category.name if self.object.category else '-'},
            {'label': _('Is Primary'), 'value': _('Yes') if self.object.is_primary else _('No')},
        ]
        context['cancel_url'] = reverse_lazy('inventory:supplier_categories')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Supplier Categories'), 'url': reverse_lazy('inventory:supplier_categories')},
            {'label': _('Delete'), 'url': None},
        ]
        return context


# ============================================================================
# Supplier Views
# ============================================================================

class SupplierListView(InventoryBaseView, ListView):
    """List view for suppliers."""
    model = models.Supplier
    template_name = 'inventory/suppliers.html'
    context_object_name = 'object_list'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.list', 'created_by')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Suppliers')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Suppliers'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('inventory:supplier_create')
        context['create_button_text'] = _('Create Supplier')
        context['table_headers'] = []  # Overridden in template
        context['show_actions'] = True
        context['feature_code'] = 'inventory.suppliers.list'
        context['detail_url_name'] = 'inventory:supplier_detail'
        context['edit_url_name'] = 'inventory:supplier_edit'
        context['delete_url_name'] = 'inventory:supplier_delete'
        context['empty_state_title'] = _('No Suppliers Found')
        context['empty_state_message'] = _('Start by creating your first supplier.')
        context['empty_state_icon'] = '🏢'
        return context


class SupplierCreateView(InventoryBaseView, CreateView):
    """Create view for suppliers."""
    model = models.Supplier
    form_class = forms.SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:suppliers')
    
    def form_valid(self, form):
        """Set company and created_by before saving."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Supplier created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic form template."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Supplier')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Suppliers'), 'url': reverse_lazy('inventory:suppliers')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('inventory:suppliers')
        return context


class SupplierUpdateView(InventoryBaseView, BaseUpdateView):
    """Update view for suppliers."""
    model = models.Supplier
    form_class = forms.SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:suppliers')
    feature_code = 'inventory.suppliers.list'
    success_message = _('Supplier updated successfully.')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.list', 'created_by')
        return queryset
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Supplier')
    
    def get_breadcrumbs(self) -> List[Dict[str, Any]]:
        """Return breadcrumbs."""
        return [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Suppliers'), 'url': reverse_lazy('inventory:suppliers')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('inventory:suppliers')


class SupplierDetailView(InventoryBaseView, DetailView):
    """Detail view for viewing suppliers (read-only)."""
    model = models.Supplier
    template_name = 'inventory/supplier_detail.html'
    context_object_name = 'supplier'
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.list', 'created_by')
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for detail view."""
        context = super().get_context_data(**kwargs)
        context['list_url'] = reverse_lazy('inventory:suppliers')
        context['edit_url'] = reverse_lazy('inventory:supplier_edit', kwargs={'pk': self.object.pk})
        context['can_edit'] = not getattr(self.object, 'is_locked', 0) if hasattr(self.object, 'is_locked') else True
        return context


class SupplierDeleteView(InventoryBaseView, DeleteView):
    """Delete view for suppliers."""
    model = models.Supplier
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('inventory:suppliers')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.list', 'created_by')
        return queryset
    
    def delete(self, request, *args, **kwargs):
        """Handle deletion with ProtectedError handling."""
        self.object = self.get_object()
        logger.info(f"Attempting to delete supplier: {self.object}")
        logger.info(f"Supplier ID: {self.object.pk}, Code: {self.object.public_code}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Supplier {self.object.pk} deleted successfully")
            messages.success(self.request, _('Supplier deleted successfully.'))
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            logger.error(f"ProtectedError when deleting supplier {self.object.pk}: {e}")
            logger.error(f"Protected objects: {e.protected_objects}")
            
            # Model name mapping
            model_name_map = {
                'Consignment Receipt Line': _('Consignment Receipt Line'),
                'Receipt Consignment Line': _('Receipt Consignment Line'),
                'Consignment Receipt Lines': _('Consignment Receipt Lines'),
                'Receipt Consignment Lines': _('Receipt Consignment Lines'),
            }
            
            # Extract model names from protected objects
            protected_models = set()
            protected_count = {}
            for obj in e.protected_objects:
                model_name = obj._meta.verbose_name
                persian_name = model_name_map.get(model_name, model_name)
                protected_models.add(persian_name)
                protected_count[persian_name] = protected_count.get(persian_name, 0) + 1
            
            # Create user-friendly error message
            error_parts = []
            for model_name, count in protected_count.items():
                error_parts.append(f"{count} {model_name}")
            
            error_message = _('Cannot delete this supplier because it is used in {models}.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Supplier')
        context['confirmation_message'] = _('Are you sure you want to delete this supplier?')
        context['object_details'] = [
            {'label': _('Code'), 'value': self.object.public_code},
            {'label': _('Name'), 'value': self.object.name},
            {'label': _('City'), 'value': self.object.city or '-'},
        ]
        context['cancel_url'] = reverse_lazy('inventory:suppliers')
        context['breadcrumbs'] = [
            {'label': _('Inventory'), 'url': None},
            {'label': _('Master Data'), 'url': None},
            {'label': _('Suppliers'), 'url': reverse_lazy('inventory:suppliers')},
            {'label': _('Delete'), 'url': None},
        ]
        return context

