"""
Product Order CRUD views for production module.
"""
from decimal import Decimal
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import EditLockProtectedMixin
from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
from inventory.utils.codes import generate_sequential_code
from production.forms import ProductOrderForm
from production.models import ProductOrder, TransferToLine, TransferToLineItem


class ProductOrderListView(FeaturePermissionRequiredMixin, ListView):
    """List all product orders for the active company."""
    model = ProductOrder
    template_name = 'production/product_orders.html'
    context_object_name = 'product_orders'
    paginate_by = 50
    feature_code = 'production.product_orders'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter product orders by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return ProductOrder.objects.none()
        
        queryset = ProductOrder.objects.filter(
            company_id=active_company_id
        ).select_related(
            'finished_item',
            'bom',
            'process',
            'approved_by',
        ).order_by('-order_date', 'order_code')
        
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('Product Orders')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Product Orders'), 'url': None},
        ]
        context['create_url'] = reverse_lazy('production:product_order_create')
        context['create_button_text'] = _('Create Product Order +')
        context['table_headers'] = []  # Overridden in template
        context['show_actions'] = True
        context['edit_url_name'] = 'production:product_order_edit'
        context['delete_url_name'] = 'production:product_order_delete'
        context['empty_state_title'] = _('No Product Orders Found')
        context['empty_state_message'] = _('Create your first product order to get started.')
        context['empty_state_icon'] = '📋'
        return context


class ProductOrderCreateView(FeaturePermissionRequiredMixin, CreateView):
    """Create a new product order."""
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'production/product_order_form.html'
    success_url = reverse_lazy('production:product_orders')
    feature_code = 'production.product_orders'
    required_action = 'create'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    @transaction.atomic
    def form_valid(self, form: ProductOrderForm) -> HttpResponseRedirect:
        """Auto-set company, created_by, finished_item, and bom_code."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        
        # Auto-set finished_item from BOM
        if form.cleaned_data.get('bom'):
            form.instance.finished_item = form.cleaned_data['bom'].finished_item
            form.instance.finished_item_code = form.cleaned_data['bom'].finished_item.item_code
            form.instance.bom_code = form.cleaned_data['bom'].bom_code
        
        # Auto-generate order_code if not provided
        if not form.instance.order_code:
            form.instance.order_code = generate_sequential_code(
                ProductOrder,
                company_id=active_company_id,
                field='order_code',
                width=10,
            )
        
        # Set unit from finished_item if available
        if form.instance.finished_item and not form.instance.unit:
            form.instance.unit = form.instance.finished_item.primary_unit or 'pcs'
        
        # Save product order first
        response = super().form_valid(form)
        
        # Check if user wants to create transfer request and has permission
        create_transfer_request = form.cleaned_data.get('create_transfer_request', False)
        transfer_approved_by = form.cleaned_data.get('transfer_approved_by')
        
        if create_transfer_request and transfer_approved_by:
            # Check permission
            permissions = get_user_feature_permissions(self.request.user, active_company_id)
            has_permission = has_feature_permission(
                permissions,
                'production.product_orders',
                action='create_transfer_from_order',
            )
            
            if has_permission:
                try:
                    # Get extra items formset from context
                    from production.forms import TransferToLineItemFormSet
                    temp_transfer = TransferToLine()
                    extra_items_formset = TransferToLineItemFormSet(
                        self.request.POST,
                        instance=temp_transfer,
                        form_kwargs={'company_id': active_company_id},
                        prefix='extra_items',
                    )
                    self.extra_items_formset = extra_items_formset
                    
                    self._create_transfer_request(
                        order=self.object,
                        approved_by=transfer_approved_by,
                        company_id=active_company_id,
                    )
                    messages.success(self.request, _('Product order and transfer request created successfully.'))
                except Exception as e:
                    messages.warning(
                        self.request,
                        _('Product order created, but transfer request creation failed: {error}').format(error=str(e))
                    )
            else:
                messages.warning(
                    self.request,
                    _('Product order created, but you do not have permission to create transfer requests.')
                )
        else:
            messages.success(self.request, _('Product order created successfully.'))
        
        return response
    
    def _create_transfer_request(
        self,
        order: ProductOrder,
        approved_by,
        company_id: int,
    ) -> TransferToLine:
        """Helper method to create a transfer request from a product order."""
        if not order.bom:
            raise ValueError(_('Product order must have a BOM to create a transfer request.'))
        
        # Create transfer request
        transfer = TransferToLine.objects.create(
            company_id=company_id,
            order=order,
            order_code=order.order_code,
            transfer_date=timezone.now().date(),
            status=TransferToLine.Status.PENDING_APPROVAL,
            approved_by=approved_by,
            created_by=self.request.user,
        )
        
        # Generate transfer code
        if not transfer.transfer_code:
            transfer.transfer_code = generate_sequential_code(
                TransferToLine,
                company_id=company_id,
                field='transfer_code',
                prefix='TR',
                width=8,
            )
            transfer.save(update_fields=['transfer_code'])
        
        # Create items from BOM
        bom = order.bom
        quantity_planned = order.quantity_planned
        
        bom_materials = bom.materials.all().select_related('material_item')
        
        for bom_material in bom_materials:
            # Calculate required quantity: quantity_planned × quantity_per_unit
            quantity_required = quantity_planned * bom_material.quantity_per_unit
            
            # Get source warehouse from ItemWarehouse (first allowed warehouse)
            from inventory.models import ItemWarehouse
            item_warehouse = ItemWarehouse.objects.filter(
                item=bom_material.material_item,
                company_id=company_id,
                is_enabled=1,
            ).select_related('warehouse').first()
            
            if not item_warehouse:
                messages.warning(
                    self.request,
                    _('No allowed warehouse found for item {item_code}. Skipping this item.').format(
                        item_code=bom_material.material_item.item_code
                    )
                )
                continue
            
            source_warehouse = item_warehouse.warehouse
            
            # Get destination work center from order's process if available
            destination_work_center = None
            if order.process:
                # Get first work line from process
                work_lines = order.process.work_lines.filter(is_enabled=1).first()
                if work_lines:
                    # Note: WorkLine doesn't have work_center, so we'll leave it None for now
                    pass
            
            # Create transfer item from BOM
            TransferToLineItem.objects.create(
                transfer=transfer,
                company_id=company_id,
                material_item=bom_material.material_item,
                material_item_code=bom_material.material_item.item_code,
                quantity_required=quantity_required,
                unit=bom_material.unit,
                source_warehouse=source_warehouse,
                source_warehouse_code=source_warehouse.public_code,
                destination_work_center=destination_work_center,
                material_scrap_allowance=bom_material.scrap_allowance,
                is_extra=0,  # From BOM
                created_by=self.request.user,
            )
        
        # Save extra items from formset
        if hasattr(self, 'extra_items_formset') and self.extra_items_formset:
            self.extra_items_formset.instance = transfer
            if self.extra_items_formset.is_valid():
                for item_form in self.extra_items_formset:
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                        item = item_form.save(commit=False)
                        item.transfer = transfer
                        item.company_id = company_id
                        item.is_extra = 1  # Mark as extra request
                        item.created_by = self.request.user
                        item.save()
        
        return transfer
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Create Product Order')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Product Orders'), 'url': reverse_lazy('production:product_orders')},
            {'label': _('Create'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:product_orders')
        context['form_id'] = 'product-order-form'
        
        # Add formset for extra items (only if user has permission)
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        if active_company_id:
            permissions = get_user_feature_permissions(self.request.user, active_company_id)
            has_permission = has_feature_permission(
                permissions,
                'production.product_orders',
                action='create_transfer_from_order',
            )
            if has_permission or self.request.user.is_superuser:
                from production.forms import TransferToLineItemFormSet
                # Create a temporary TransferToLine instance for the formset
                # This won't be saved, it's just for the formset structure
                temp_transfer = TransferToLine()
                if self.request.POST:
                    context['extra_items_formset'] = TransferToLineItemFormSet(
                        self.request.POST,
                        instance=temp_transfer,
                        form_kwargs={'company_id': active_company_id},
                        prefix='extra_items',
                    )
                else:
                    context['extra_items_formset'] = TransferToLineItemFormSet(
                        instance=temp_transfer,
                        form_kwargs={'company_id': active_company_id},
                        prefix='extra_items',
                    )
        
        return context


class ProductOrderUpdateView(EditLockProtectedMixin, FeaturePermissionRequiredMixin, UpdateView):
    """Update an existing product order."""
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'production/product_order_form.html'
    success_url = reverse_lazy('production:product_orders')
    feature_code = 'production.product_orders'
    required_action = 'edit_own'
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.object.company_id
        return kwargs
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return ProductOrder.objects.none()
        return ProductOrder.objects.filter(company_id=active_company_id)
    
    @transaction.atomic
    def form_valid(self, form: ProductOrderForm) -> HttpResponseRedirect:
        """Auto-set edited_by and update related fields."""
        form.instance.edited_by = self.request.user
        
        # Update finished_item and bom_code if BOM changed
        if form.cleaned_data.get('bom'):
            form.instance.finished_item = form.cleaned_data['bom'].finished_item
            form.instance.finished_item_code = form.cleaned_data['bom'].finished_item.item_code
            form.instance.bom_code = form.cleaned_data['bom'].bom_code
        
        # Save product order first
        response = super().form_valid(form)
        
        # Check if user wants to create transfer request and has permission
        create_transfer_request = form.cleaned_data.get('create_transfer_request', False)
        transfer_approved_by = form.cleaned_data.get('transfer_approved_by')
        
        if create_transfer_request and transfer_approved_by:
            # Check permission
            permissions = get_user_feature_permissions(self.request.user, self.object.company_id)
            has_permission = has_feature_permission(
                permissions,
                'production.product_orders',
                action='create_transfer_from_order',
            )
            
            if has_permission:
                try:
                    # Get extra items formset from context
                    from production.forms import TransferToLineItemFormSet
                    temp_transfer = TransferToLine()
                    extra_items_formset = TransferToLineItemFormSet(
                        self.request.POST,
                        instance=temp_transfer,
                        form_kwargs={'company_id': self.object.company_id},
                        prefix='extra_items',
                    )
                    self.extra_items_formset = extra_items_formset
                    
                    self._create_transfer_request(
                        order=self.object,
                        approved_by=transfer_approved_by,
                        company_id=self.object.company_id,
                    )
                    messages.success(self.request, _('Product order updated and transfer request created successfully.'))
                except Exception as e:
                    messages.warning(
                        self.request,
                        _('Product order updated, but transfer request creation failed: {error}').format(error=str(e))
                    )
            else:
                messages.warning(
                    self.request,
                    _('Product order updated, but you do not have permission to create transfer requests.')
                )
        else:
            messages.success(self.request, _('Product order updated successfully.'))
        
        return response
    
    def _create_transfer_request(
        self,
        order: ProductOrder,
        approved_by,
        company_id: int,
    ) -> TransferToLine:
        """Helper method to create a transfer request from a product order."""
        if not order.bom:
            raise ValueError(_('Product order must have a BOM to create a transfer request.'))
        
        # Create transfer request
        transfer = TransferToLine.objects.create(
            company_id=company_id,
            order=order,
            order_code=order.order_code,
            transfer_date=timezone.now().date(),
            status=TransferToLine.Status.PENDING_APPROVAL,
            approved_by=approved_by,
            created_by=self.request.user,
        )
        
        # Generate transfer code
        if not transfer.transfer_code:
            transfer.transfer_code = generate_sequential_code(
                TransferToLine,
                company_id=company_id,
                field='transfer_code',
                prefix='TR',
                width=8,
            )
            transfer.save(update_fields=['transfer_code'])
        
        # Create items from BOM
        bom = order.bom
        quantity_planned = order.quantity_planned
        
        bom_materials = bom.materials.all().select_related('material_item')
        
        for bom_material in bom_materials:
            # Calculate required quantity: quantity_planned × quantity_per_unit
            quantity_required = quantity_planned * bom_material.quantity_per_unit
            
            # Get source warehouse from ItemWarehouse (first allowed warehouse)
            from inventory.models import ItemWarehouse
            item_warehouse = ItemWarehouse.objects.filter(
                item=bom_material.material_item,
                company_id=company_id,
                is_enabled=1,
            ).select_related('warehouse').first()
            
            if not item_warehouse:
                messages.warning(
                    self.request,
                    _('No allowed warehouse found for item {item_code}. Skipping this item.').format(
                        item_code=bom_material.material_item.item_code
                    )
                )
                continue
            
            source_warehouse = item_warehouse.warehouse
            
            # Get destination work center from order's process if available
            destination_work_center = None
            if order.process:
                # Get first work line from process
                work_lines = order.process.work_lines.filter(is_enabled=1).first()
                if work_lines:
                    # Note: WorkLine doesn't have work_center, so we'll leave it None for now
                    pass
            
            # Create transfer item from BOM
            TransferToLineItem.objects.create(
                transfer=transfer,
                company_id=company_id,
                material_item=bom_material.material_item,
                material_item_code=bom_material.material_item.item_code,
                quantity_required=quantity_required,
                unit=bom_material.unit,
                source_warehouse=source_warehouse,
                source_warehouse_code=source_warehouse.public_code,
                destination_work_center=destination_work_center,
                material_scrap_allowance=bom_material.scrap_allowance,
                is_extra=0,  # From BOM
                created_by=self.request.user,
            )
        
        # Save extra items from formset
        if hasattr(self, 'extra_items_formset') and self.extra_items_formset:
            self.extra_items_formset.instance = transfer
            if self.extra_items_formset.is_valid():
                for item_form in self.extra_items_formset:
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                        item = item_form.save(commit=False)
                        item.transfer = transfer
                        item.company_id = company_id
                        item.is_extra = 1  # Mark as extra request
                        item.created_by = self.request.user
                        item.save()
        
        return transfer
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and form title to context."""
        context = super().get_context_data(**kwargs)
        context['form_title'] = _('Edit Product Order')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Product Orders'), 'url': reverse_lazy('production:product_orders')},
            {'label': _('Edit'), 'url': None},
        ]
        context['cancel_url'] = reverse_lazy('production:product_orders')
        context['form_id'] = 'product-order-form'
        
        # Add formset for extra items (only if user has permission)
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        if self.object and self.object.company_id:
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, self.object.company_id)
            permissions = get_user_feature_permissions(self.request.user, self.object.company_id)
            has_permission = has_feature_permission(
                permissions,
                'production.product_orders',
                action='create_transfer_from_order',
            )
            if has_permission or self.request.user.is_superuser:
                from production.forms import TransferToLineItemFormSet
                # Create a temporary TransferToLine instance for the formset
                temp_transfer = TransferToLine()
                if self.request.POST:
                    context['extra_items_formset'] = TransferToLineItemFormSet(
                        self.request.POST,
                        instance=temp_transfer,
                        form_kwargs={'company_id': self.object.company_id},
                        prefix='extra_items',
                    )
                else:
                    context['extra_items_formset'] = TransferToLineItemFormSet(
                        instance=temp_transfer,
                        form_kwargs={'company_id': self.object.company_id},
                        prefix='extra_items',
                    )
        
        return context


class ProductOrderDeleteView(FeaturePermissionRequiredMixin, DeleteView):
    """Delete a product order."""
    model = ProductOrder
    success_url = reverse_lazy('production:product_orders')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'production.product_orders'
    required_action = 'delete_own'
    
    def get_queryset(self):
        """Filter by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            return ProductOrder.objects.none()
        return ProductOrder.objects.filter(company_id=active_company_id).select_related('bom', 'finished_item')
    
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Delete product order and show success message."""
        messages.success(self.request, _('Product order deleted successfully.'))
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic delete template."""
        context = super().get_context_data(**kwargs)
        context['delete_title'] = _('Delete Product Order')
        context['confirmation_message'] = _('Are you sure you want to delete this product order?')
        
        object_details = [
            {'label': _('Order Code'), 'value': self.object.order_code},
        ]
        
        if self.object.bom:
            object_details.append({'label': _('BOM'), 'value': self.object.bom.bom_code})
        
        if self.object.finished_item:
            object_details.append({'label': _('Finished Item'), 'value': f"{self.object.finished_item.item_code} - {self.object.finished_item.name}"})
        
        object_details.extend([
            {'label': _('Quantity'), 'value': f"{self.object.quantity_planned} {self.object.unit}"},
            {'label': _('Status'), 'value': self.object.get_status_display()},
        ])
        
        context['object_details'] = object_details
        context['cancel_url'] = reverse_lazy('production:product_orders')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('Product Orders'), 'url': reverse_lazy('production:product_orders')},
            {'label': _('Delete'), 'url': None},
        ]
        return context

