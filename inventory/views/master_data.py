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
from typing import Dict, Any
from django.contrib import messages
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .base import InventoryBaseView, ItemUnitFormsetMixin
from shared.mixins import FeaturePermissionRequiredMixin
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
    context_object_name = 'item_types'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_types', 'created_by')
        return queryset


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
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Type')
        return context


class ItemTypeUpdateView(InventoryBaseView, UpdateView):
    """Update view for item types."""
    model = models.ItemType
    form_class = forms.ItemTypeForm
    template_name = 'inventory/itemtype_form.html'
    success_url = reverse_lazy('inventory:item_types')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_types', 'created_by')
        return queryset
    
    def form_valid(self, form):
        """Set edited_by before saving."""
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Item Type updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Item Type')
        return context


class ItemTypeDeleteView(InventoryBaseView, DeleteView):
    """Delete view for item types."""
    model = models.ItemType
    template_name = 'inventory/itemtype_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_types')
    
    def get_context_data(self, **kwargs):
        """Add model verbose name to context."""
        context = super().get_context_data(**kwargs)
        context['model_verbose_name'] = _('نوع کالا')
        return context
    
    def form_valid(self, form):
        """Handle deletion with ProtectedError handling."""
        logger.info(f"Attempting to delete item type: {self.object}")
        logger.info(f"Item Type ID: {self.object.pk}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Item Type {self.object.pk} deleted successfully")
            messages.success(self.request, _('نوع کالا با موفقیت حذف شد.'))
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
            
            error_message = _('نمی‌توان این نوع کالا را حذف کرد چون در ساختار {models} استفاده شده است.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())


# ============================================================================
# Item Category Views
# ============================================================================

class ItemCategoryListView(InventoryBaseView, ListView):
    """List view for item categories."""
    model = models.ItemCategory
    template_name = 'inventory/item_categories.html'
    context_object_name = 'item_categories'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_categories', 'created_by')
        return queryset


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
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Category')
        return context


class ItemCategoryUpdateView(InventoryBaseView, UpdateView):
    """Update view for item categories."""
    model = models.ItemCategory
    form_class = forms.ItemCategoryForm
    template_name = 'inventory/itemcategory_form.html'
    success_url = reverse_lazy('inventory:item_categories')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_categories', 'created_by')
        return queryset
    
    def form_valid(self, form):
        """Set edited_by before saving."""
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Item Category updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Item Category')
        return context


class ItemCategoryDeleteView(InventoryBaseView, DeleteView):
    """Delete view for item categories."""
    model = models.ItemCategory
    template_name = 'inventory/itemcategory_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_categories')
    
    def get_context_data(self, **kwargs):
        """Add model verbose name to context."""
        context = super().get_context_data(**kwargs)
        context['model_verbose_name'] = _('دسته‌بندی کالا')
        return context
    
    def form_valid(self, form):
        """Handle deletion with ProtectedError handling."""
        logger.info(f"Attempting to delete item category: {self.object}")
        logger.info(f"Item Category ID: {self.object.pk}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Item Category {self.object.pk} deleted successfully")
            messages.success(self.request, _('دسته‌بندی کالا با موفقیت حذف شد.'))
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            logger.error(f"ProtectedError when deleting item category {self.object.pk}: {e}")
            logger.error(f"Protected objects: {e.protected_objects}")
            
            # Model name mapping to Persian
            model_name_map = {
                'Item': _('کالا'),
                'Items': _('کالاها'),
                'Item Subcategory': _('زیر دسته‌بندی کالا'),
                'Item Subcategories': _('زیر دسته‌بندی‌های کالا'),
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
            
            error_message = _('نمی‌توان این دسته‌بندی کالا را حذف کرد چون در ساختار {models} استفاده شده است.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())


# ============================================================================
# Item Subcategory Views
# ============================================================================

class ItemSubcategoryListView(InventoryBaseView, ListView):
    """List view for item subcategories."""
    model = models.ItemSubcategory
    template_name = 'inventory/item_subcategories.html'
    context_object_name = 'item_subcategories'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_subcategories', 'created_by')
        return queryset


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
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Item Subcategory')
        return context


class ItemSubcategoryUpdateView(InventoryBaseView, UpdateView):
    """Update view for item subcategories."""
    model = models.ItemSubcategory
    form_class = forms.ItemSubcategoryForm
    template_name = 'inventory/itemsubcategory_form.html'
    success_url = reverse_lazy('inventory:item_subcategories')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.item_subcategories', 'created_by')
        return queryset
    
    def form_valid(self, form):
        """Set edited_by before saving."""
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Item Subcategory updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Item Subcategory')
        return context


class ItemSubcategoryDeleteView(InventoryBaseView, DeleteView):
    """Delete view for item subcategories."""
    model = models.ItemSubcategory
    template_name = 'inventory/itemsubcategory_confirm_delete.html'
    success_url = reverse_lazy('inventory:item_subcategories')
    
    def get_context_data(self, **kwargs):
        """Add model verbose name to context."""
        context = super().get_context_data(**kwargs)
        context['model_verbose_name'] = _('زیر دسته‌بندی کالا')
        return context
    
    def form_valid(self, form):
        """Handle deletion with ProtectedError handling."""
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

class ItemListView(InventoryBaseView, ListView):
    """List view for items."""
    model = models.Item
    template_name = 'inventory/items.html'
    context_object_name = 'items'
    paginate_by = 50
    
    def get_queryset(self):
        """Return items with filters and search, ordered by newest first."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('type', 'category', 'subcategory')
        
        # Filter by user permissions (own vs all)
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.items', 'created_by')
        
        # Search by item code or name (Persian or English)
        search = (self.request.GET.get('search') or '').strip()
        if search:
            queryset = queryset.filter(
                Q(item_code__icontains=search) |
                Q(name__icontains=search) |
                Q(name_en__icontains=search)
            )
        
        # Filter by item type
        item_type_id = self.request.GET.get('type')
        if item_type_id:
            queryset = queryset.filter(type_id=item_type_id)
        
        # Filter by category
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by status (is_enabled)
        status = self.request.GET.get('status')
        if status == '1':
            queryset = queryset.filter(is_enabled=1)
        elif status == '0':
            queryset = queryset.filter(is_enabled=0)
        
        # Order by created_at descending (newest first), then by id descending as fallback
        return queryset.order_by('-created_at', '-id')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add filter context for template."""
        context = super().get_context_data(**kwargs)
        company_id = self.request.session.get('active_company_id')
        
        # Add item types for filter dropdown
        if company_id:
            context['item_types'] = models.ItemType.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('name')
            context['item_categories'] = models.ItemCategory.objects.filter(
                company_id=company_id,
                is_enabled=1,
            ).order_by('name')
        
        return context


class ItemSerialListView(FeaturePermissionRequiredMixin, InventoryBaseView, ListView):
    """List view for item serials."""
    feature_code = 'inventory.master.item_serials'
    model = models.ItemSerial
    template_name = 'inventory/item_serials.html'
    context_object_name = 'serials'
    paginate_by = 100

    def get_queryset(self):
        """Filter and search serials."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('item', 'receipt_document', 'current_warehouse')
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

        return queryset.order_by('-created_at', '-id')

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add search filters to context."""
        context = super().get_context_data(**kwargs)
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


class ItemCreateView(ItemUnitFormsetMixin, InventoryBaseView, CreateView):
    """Create view for items with unit formset."""
    model = models.Item
    form_class = forms.ItemForm
    template_name = 'inventory/item_form.html'
    success_url = reverse_lazy('inventory:items')
    
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
        
        form.instance.company_id = company_id
        form.instance.created_by = self.request.user
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
        checkbox_fields = ['is_sellable', 'has_lot_tracking', 'requires_temporary_receipt', 'is_enabled']
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
        
        messages.success(self.request, _('کالا با موفقیت ایجاد شد.'))
        return HttpResponseRedirect(self.get_success_url())
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add unit formset to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('تعریف کالای جدید')
        return context


class ItemUpdateView(ItemUnitFormsetMixin, InventoryBaseView, UpdateView):
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
        checkbox_fields = ['is_sellable', 'has_lot_tracking', 'requires_temporary_receipt', 'is_enabled']
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
        context['form_title'] = _('ویرایش کالا')
        return context


class ItemDeleteView(InventoryBaseView, DeleteView):
    """Delete view for items."""
    model = models.Item
    template_name = 'inventory/item_confirm_delete.html'
    success_url = reverse_lazy('inventory:items')
    
    def get_context_data(self, **kwargs):
        """Add model verbose name to context."""
        context = super().get_context_data(**kwargs)
        context['model_verbose_name'] = self.model._meta.verbose_name
        return context
    
    def form_valid(self, form):
        """Handle deletion with ProtectedError handling."""
        logger.info(f"Attempting to delete item: {self.object}")
        logger.info(f"Item ID: {self.object.pk}, Code: {self.object.full_item_code or self.object.item_code}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Item {self.object.pk} deleted successfully")
            messages.success(self.request, _('کالا با موفقیت حذف شد.'))
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
            
            error_message = _('نمی‌توان این کالا را حذف کرد چون در {models} استفاده شده است.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())


# ============================================================================
# Warehouse Views
# ============================================================================

class WarehouseListView(InventoryBaseView, ListView):
    """List view for warehouses."""
    model = models.Warehouse
    template_name = 'inventory/warehouses.html'
    context_object_name = 'warehouses'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.warehouses', 'created_by')
        return queryset


class WarehouseCreateView(InventoryBaseView, CreateView):
    """Create view for warehouses."""
    model = models.Warehouse
    form_class = forms.WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouses')
    
    def form_valid(self, form):
        """Set company and created_by before saving."""
        form.instance.company_id = self.request.session.get('active_company_id')
        form.instance.created_by = self.request.user
        messages.success(self.request, _('Warehouse created successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Warehouse')
        return context


class WarehouseUpdateView(InventoryBaseView, UpdateView):
    """Update view for warehouses."""
    model = models.Warehouse
    form_class = forms.WarehouseForm
    template_name = 'inventory/warehouse_form.html'
    success_url = reverse_lazy('inventory:warehouses')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.master.warehouses', 'created_by')
        return queryset
    
    def form_valid(self, form):
        """Set edited_by before saving."""
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('Warehouse updated successfully.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Warehouse')
        return context


class WarehouseDeleteView(InventoryBaseView, DeleteView):
    """Delete view for warehouses."""
    model = models.Warehouse
    template_name = 'inventory/warehouse_confirm_delete.html'
    success_url = reverse_lazy('inventory:warehouses')
    
    def get_context_data(self, **kwargs):
        """Add model verbose name to context."""
        context = super().get_context_data(**kwargs)
        context['model_verbose_name'] = self.model._meta.verbose_name
        return context
    
    def form_valid(self, form):
        """Handle deletion with ProtectedError handling."""
        logger.info(f"Attempting to delete warehouse: {self.object}")
        logger.info(f"Warehouse ID: {self.object.pk}, Code: {self.object.public_code}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Warehouse {self.object.pk} deleted successfully")
            messages.success(self.request, _('انبار با موفقیت حذف شد.'))
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            logger.error(f"ProtectedError when deleting warehouse {self.object.pk}: {e}")
            logger.error(f"Protected objects: {e.protected_objects}")
            
            # Model name mapping to Persian
            model_name_map = {
                'Consumption Issue Line': _('خط مصرف'),
                'Permanent Receipt Line': _('خط رسید دائم'),
                'Consumption Issue Lines': _('خطوط مصرف'),
                'Permanent Receipt Lines': _('خطوط رسید دائم'),
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
            
            error_message = _('نمی‌توان این انبار را حذف کرد چون در {models} استفاده شده است.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())


# ============================================================================
# Supplier Category Views
# ============================================================================

class SupplierCategoryListView(InventoryBaseView, ListView):
    """List view for supplier categories."""
    model = models.SupplierCategory
    template_name = 'inventory/supplier_categories.html'
    context_object_name = 'supplier_categories'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.categories', 'created_by')
        return queryset


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
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ایجاد دسته‌بندی تأمین‌کننده')
        return context


class SupplierCategoryUpdateView(InventoryBaseView, UpdateView):
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
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ویرایش دسته‌بندی تأمین‌کننده')
        return context


class SupplierCategoryDeleteView(InventoryBaseView, DeleteView):
    """Delete view for supplier categories."""
    model = models.SupplierCategory
    template_name = 'inventory/suppliercategory_confirm_delete.html'
    success_url = reverse_lazy('inventory:supplier_categories')
    
    def delete(self, request, *args, **kwargs):
        """Show success message after deletion."""
        messages.success(self.request, _('دسته‌بندی تأمین‌کننده حذف شد.'))
        return super().delete(request, *args, **kwargs)


# ============================================================================
# Supplier Views
# ============================================================================

class SupplierListView(InventoryBaseView, ListView):
    """List view for suppliers."""
    model = models.Supplier
    template_name = 'inventory/suppliers.html'
    context_object_name = 'suppliers'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.list', 'created_by')
        return queryset


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
        messages.success(self.request, _('تأمین‌کننده با موفقیت ایجاد شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ایجاد تأمین‌کننده')
        return context


class SupplierUpdateView(InventoryBaseView, UpdateView):
    """Update view for suppliers."""
    model = models.Supplier
    form_class = forms.SupplierForm
    template_name = 'inventory/supplier_form.html'
    success_url = reverse_lazy('inventory:suppliers')
    
    def get_queryset(self):
        """Filter queryset by user permissions."""
        queryset = super().get_queryset()
        queryset = self.filter_queryset_by_permissions(queryset, 'inventory.suppliers.list', 'created_by')
        return queryset
    
    def form_valid(self, form):
        """Set edited_by before saving."""
        form.instance.edited_by = self.request.user
        messages.success(self.request, _('تأمین‌کننده با موفقیت ویرایش شد.'))
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('ویرایش تأمین‌کننده')
        return context


class SupplierDeleteView(InventoryBaseView, DeleteView):
    """Delete view for suppliers."""
    model = models.Supplier
    template_name = 'inventory/supplier_confirm_delete.html'
    success_url = reverse_lazy('inventory:suppliers')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_verbose_name'] = self.model._meta.verbose_name
        return context
    
    def form_valid(self, form):
        """Handle deletion with ProtectedError handling."""
        logger.info(f"Attempting to delete supplier: {self.object}")
        logger.info(f"Supplier ID: {self.object.pk}, Code: {self.object.public_code}, Name: {self.object.name}")
        
        try:
            self.object.delete()
            logger.info(f"Supplier {self.object.pk} deleted successfully")
            messages.success(self.request, _('تأمین‌کننده با موفقیت حذف شد.'))
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())
        except ProtectedError as e:
            logger.error(f"ProtectedError when deleting supplier {self.object.pk}: {e}")
            logger.error(f"Protected objects: {e.protected_objects}")
            
            # Model name mapping to Persian
            model_name_map = {
                'Consignment Receipt Line': _('خط رسید امانی'),
                'Receipt Consignment Line': _('خط رسید امانی'),
                'Consignment Receipt Lines': _('خطوط رسید امانی'),
                'Receipt Consignment Lines': _('خطوط رسید امانی'),
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
            
            error_message = _('نمی‌توان این تأمین‌کننده را حذف کرد چون در {models} استفاده شده است.').format(
                models=', '.join(error_parts)
            )
            
            messages.error(self.request, error_message)
            logger.error(f"Error message shown to user: {error_message}")
            
            # Redirect to list page with error message
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(self.get_success_url())

