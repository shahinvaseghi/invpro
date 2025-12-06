"""
Product Order CRUD views for production module.
"""
from decimal import Decimal
from typing import Any, Dict, Optional, List
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.views.generic import CreateView, UpdateView

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseListView,
    BaseDetailView,
    BaseDeleteView,
    BaseCreateView,
    BaseUpdateView,
    EditLockProtectedMixin,
)
from shared.views.base_additional import TransferRequestCreationMixin
from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
from production.forms import ProductOrderForm
from production.models import ProductOrder, TransferToLine, TransferToLineItem
from production.utils.transfer import generate_transfer_code


class ProductOrderListView(BaseListView):
    """List all product orders for the active company."""
    model = ProductOrder
    template_name = 'production/product_orders.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.product_orders'
    required_action = 'view_own'
    active_module = 'production'
    default_status_filter = False
    default_order_by = ['-order_date', 'order_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return ['finished_item', 'bom', 'process', 'approved_by']
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Product Orders')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Product Orders'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL."""
        return reverse_lazy('production:product_order_create')
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Product Order +')
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name."""
        return 'production:product_order_detail'
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name."""
        return 'production:product_order_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'production:product_order_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Product Orders Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Create your first product order to get started.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '📋'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['table_headers'] = []  # Overridden in template
        return context


class ProductOrderCreateView(TransferRequestCreationMixin, BaseCreateView):
    """Create a new product order."""
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'production/product_order_form.html'
    success_url = reverse_lazy('production:product_orders')
    feature_code = 'production.product_orders'
    required_action = 'create'
    active_module = 'production'
    success_message = _('Product order created successfully.')
    
    def get_form_kwargs(self) -> Dict[str, Any]:
        """Add company_id to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['company_id'] = self.request.session.get('active_company_id')
        return kwargs
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Product Orders'), 'url': reverse_lazy('production:product_orders')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:product_orders')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Product Order')
    
    def should_create_transfer_request(self, form) -> bool:
        """Check if transfer request should be created."""
        return form.cleaned_data.get('create_transfer_request', False) and form.cleaned_data.get('transfer_approved_by')
    
    def get_transfer_request_feature_code(self) -> str:
        """Return feature code for transfer request permission check."""
        return 'production.product_orders'
    
    def get_transfer_request_action(self) -> str:
        """Return action name for transfer request permission check."""
        return 'create_transfer_from_order'
    
    def get_transfer_request_kwargs(self, form) -> Dict[str, Any]:
        """Return kwargs for transfer request creation."""
        return {
            'approved_by': form.cleaned_data.get('transfer_approved_by'),
            'transfer_type': form.cleaned_data.get('transfer_type', 'full'),
            'selected_operations': form.cleaned_data.get('selected_operations', []),
        }
    
    def _create_transfer_request(
        self,
        order: ProductOrder,
        approved_by,
        company_id: int,
        transfer_type: str = 'full',
        selected_operations: list = None,
        **kwargs
    ) -> TransferToLine:
        """Helper method to create a transfer request from a product order."""
        if not order.bom:
            raise ValueError(_('Product order must have a BOM to create a transfer request.'))
        
        if selected_operations is None:
            selected_operations = []
        
        # Get extra items formset
        from production.forms import TransferToLineItemFormSet
        temp_transfer = TransferToLine()
        extra_items_formset = TransferToLineItemFormSet(
            self.request.POST,
            instance=temp_transfer,
            form_kwargs={'company_id': company_id},
            prefix='extra_items',
        )
        self.extra_items_formset = extra_items_formset
        
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
            transfer.transfer_code = generate_transfer_code(
                company_id=company_id,
                prefix='TR',
                width=8,
            )
            transfer.save(update_fields=['transfer_code'])
        
        # Collect materials to transfer based on transfer_type
        from inventory.models import ItemWarehouse
        from production.utils.transfer import get_operation_materials
        from production.models import ProcessOperation
        
        quantity_planned = order.quantity_planned
        materials_to_transfer = []  # List of (material_item, quantity, unit, scrap_allowance, source_warehouses_list)
        
        if transfer_type == 'full':
            # Transfer all BOM materials
            bom = order.bom
            bom_materials = bom.materials.filter(is_enabled=1).select_related('material_item')
            
            for bom_material in bom_materials:
                quantity_required = quantity_planned * bom_material.quantity_per_unit
                
                # Get source_warehouses from JSONField, or fallback to source_warehouse (backward compatibility)
                source_warehouses_list = bom_material.source_warehouses or []
                
                # If source_warehouses is empty but source_warehouse is set, use it for backward compatibility
                if not source_warehouses_list and bom_material.source_warehouse:
                    source_warehouses_list = [{
                        'warehouse_id': bom_material.source_warehouse.id,
                        'warehouse_code': bom_material.source_warehouse.public_code,
                        'priority': 1
                    }]
                
                materials_to_transfer.append((
                    bom_material.material_item,
                    quantity_required,
                    bom_material.unit,
                    bom_material.scrap_allowance,
                    source_warehouses_list,  # Include source_warehouses list from BOM
                ))
        
        elif transfer_type == 'operations' and selected_operations:
            # Transfer materials from selected operations
            operation_ids = [int(op_id) for op_id in selected_operations]
            operations = ProcessOperation.objects.filter(
                id__in=operation_ids,
                is_enabled=1,
            ).select_related('process')
            
            for operation in operations:
                operation_materials = get_operation_materials(operation, order)
                
                for op_material in operation_materials:
                    # Calculate quantity: quantity_planned × quantity_used (from ProcessOperationMaterial)
                    quantity_required = quantity_planned * op_material.quantity_used
                    
                    # Get scrap allowance and source_warehouses from BOM material if available
                    scrap_allowance = Decimal('0.00')
                    source_warehouses_list = []
                    if op_material.bom_material:
                        scrap_allowance = op_material.bom_material.scrap_allowance
                        source_warehouses_list = op_material.bom_material.source_warehouses or []
                        
                        # Backward compatibility: if source_warehouses is empty but source_warehouse is set
                        if not source_warehouses_list and op_material.bom_material.source_warehouse:
                            source_warehouses_list = [{
                                'warehouse_id': op_material.bom_material.source_warehouse.id,
                                'warehouse_code': op_material.bom_material.source_warehouse.public_code,
                                'priority': 1
                            }]
                    
                    materials_to_transfer.append((
                        op_material.material_item,
                        quantity_required,
                        op_material.unit,
                        scrap_allowance,
                        source_warehouses_list,  # Include source_warehouses list from BOM
                    ))
        
        # Create transfer items
        for material_item, quantity_required, unit, scrap_allowance, source_warehouses_list in materials_to_transfer:
            # Priority 1: Use first warehouse from source_warehouses list (sorted by priority)
            # Priority 2: Use first allowed warehouse from ItemWarehouse
            source_warehouse = None
            
            if source_warehouses_list and len(source_warehouses_list) > 0:
                # Sort by priority and get first warehouse (priority 1)
                sorted_warehouses = sorted(
                    source_warehouses_list,
                    key=lambda x: x.get('priority', 999)
                )
                
                if sorted_warehouses and sorted_warehouses[0].get('warehouse_id'):
                    from inventory.models import Warehouse
                    try:
                        source_warehouse = Warehouse.objects.get(
                            id=sorted_warehouses[0]['warehouse_id'],
                            company_id=company_id,
                            is_enabled=1,
                        )
                    except Warehouse.DoesNotExist:
                        pass
            
            if not source_warehouse:
                # Fallback: Get source warehouse from ItemWarehouse (first allowed warehouse)
                item_warehouse = ItemWarehouse.objects.filter(
                    item=material_item,
                    company_id=company_id,
                    is_enabled=1,
                ).select_related('warehouse').first()
                
                if not item_warehouse:
                    messages.warning(
                        self.request,
                        _('No allowed warehouse found for item {item_code}. Skipping this item.').format(
                            item_code=material_item.item_code
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
            
            # Create transfer item
            TransferToLineItem.objects.create(
                transfer=transfer,
                company_id=company_id,
                material_item=material_item,
                material_item_code=material_item.item_code,
                quantity_required=quantity_required,
                unit=unit,
                source_warehouse=source_warehouse,
                source_warehouse_code=source_warehouse.public_code,
                destination_work_center=destination_work_center,
                material_scrap_allowance=scrap_allowance,
                is_extra=0,  # From BOM or Operations
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
    
    @transaction.atomic
    def form_valid(self, form: ProductOrderForm) -> HttpResponseRedirect:
        """Auto-set company, created_by, finished_item, and bom_code."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if not active_company_id:
            messages.error(self.request, _('Please select a company first.'))
            return self.form_invalid(form)
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        
        # Auto-set finished_item and bom from Process
        if form.cleaned_data.get('process'):
            process = form.cleaned_data['process']
            form.instance.process = process
            form.instance.process_code = process.process_code
            form.instance.finished_item = process.finished_item
            form.instance.finished_item_code = process.finished_item.item_code
            if process.bom:
                form.instance.bom = process.bom
                form.instance.bom_code = process.bom.bom_code
        
        # Auto-generate order_code if not provided
        if not form.instance.order_code:
            from shared.utils.code_generation import generate_sequential_code
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
        self.object = form.save()
        
        # Use mixin's create_transfer_request_if_needed to handle transfer request creation
        transfer_request = self.create_transfer_request_if_needed(form, self.object)
        if transfer_request:
            messages.success(self.request, _('Product order and transfer request created successfully.'))
        else:
            messages.success(self.request, _('Product order created successfully.'))
        
        return HttpResponseRedirect(self.get_success_url())
    
    def _create_transfer_request(
        self,
        order: ProductOrder,
        approved_by,
        company_id: int,
        transfer_type: str = 'full',
        selected_operations: list = None,
    ) -> TransferToLine:
        """Helper method to create a transfer request from a product order."""
        if not order.bom:
            raise ValueError(_('Product order must have a BOM to create a transfer request.'))
        
        if selected_operations is None:
            selected_operations = []
        
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
            transfer.transfer_code = generate_transfer_code(
                company_id=company_id,
                prefix='TR',
                width=8,
            )
            transfer.save(update_fields=['transfer_code'])
        
        # Collect materials to transfer based on transfer_type
        from inventory.models import ItemWarehouse
        from production.utils.transfer import get_operation_materials
        from production.models import ProcessOperation
        
        quantity_planned = order.quantity_planned
        materials_to_transfer = []  # List of (material_item, quantity, unit, scrap_allowance, source_warehouses_list)
        
        if transfer_type == 'full':
            # Transfer all BOM materials
            bom = order.bom
            bom_materials = bom.materials.filter(is_enabled=1).select_related('material_item')
            
            for bom_material in bom_materials:
                quantity_required = quantity_planned * bom_material.quantity_per_unit
                
                # Get source_warehouses from JSONField, or fallback to source_warehouse (backward compatibility)
                source_warehouses_list = bom_material.source_warehouses or []
                
                # If source_warehouses is empty but source_warehouse is set, use it for backward compatibility
                if not source_warehouses_list and bom_material.source_warehouse:
                    source_warehouses_list = [{
                        'warehouse_id': bom_material.source_warehouse.id,
                        'warehouse_code': bom_material.source_warehouse.public_code,
                        'priority': 1
                    }]
                
                materials_to_transfer.append((
                    bom_material.material_item,
                    quantity_required,
                    bom_material.unit,
                    bom_material.scrap_allowance,
                    source_warehouses_list,  # Include source_warehouses list from BOM
                ))
        
        elif transfer_type == 'operations' and selected_operations:
            # Transfer materials from selected operations
            operation_ids = [int(op_id) for op_id in selected_operations]
            operations = ProcessOperation.objects.filter(
                id__in=operation_ids,
                is_enabled=1,
            ).select_related('process')
            
            for operation in operations:
                operation_materials = get_operation_materials(operation, order)
                
                for op_material in operation_materials:
                    # Calculate quantity: quantity_planned × quantity_used (from ProcessOperationMaterial)
                    quantity_required = quantity_planned * op_material.quantity_used
                    
                    # Get scrap allowance and source_warehouses from BOM material if available
                    scrap_allowance = Decimal('0.00')
                    source_warehouses_list = []
                    if op_material.bom_material:
                        scrap_allowance = op_material.bom_material.scrap_allowance
                        source_warehouses_list = op_material.bom_material.source_warehouses or []
                        
                        # Backward compatibility: if source_warehouses is empty but source_warehouse is set
                        if not source_warehouses_list and op_material.bom_material.source_warehouse:
                            source_warehouses_list = [{
                                'warehouse_id': op_material.bom_material.source_warehouse.id,
                                'warehouse_code': op_material.bom_material.source_warehouse.public_code,
                                'priority': 1
                            }]
                    
                    materials_to_transfer.append((
                        op_material.material_item,
                        quantity_required,
                        op_material.unit,
                        scrap_allowance,
                        source_warehouses_list,  # Include source_warehouses list from BOM
                    ))
        
        # Create transfer items
        for material_item, quantity_required, unit, scrap_allowance, source_warehouses_list in materials_to_transfer:
            # Priority 1: Use first warehouse from source_warehouses list (sorted by priority)
            # Priority 2: Use first allowed warehouse from ItemWarehouse
            source_warehouse = None
            
            if source_warehouses_list and len(source_warehouses_list) > 0:
                # Sort by priority and get first warehouse (priority 1)
                sorted_warehouses = sorted(
                    source_warehouses_list,
                    key=lambda x: x.get('priority', 999)
                )
                
                if sorted_warehouses and sorted_warehouses[0].get('warehouse_id'):
                    from inventory.models import Warehouse
                    try:
                        source_warehouse = Warehouse.objects.get(
                            id=sorted_warehouses[0]['warehouse_id'],
                            company_id=company_id,
                            is_enabled=1,
                        )
                    except Warehouse.DoesNotExist:
                        pass
            
            if not source_warehouse:
                # Fallback: Get source warehouse from ItemWarehouse (first allowed warehouse)
                item_warehouse = ItemWarehouse.objects.filter(
                    item=material_item,
                    company_id=company_id,
                    is_enabled=1,
                ).select_related('warehouse').first()
                
                if not item_warehouse:
                    messages.warning(
                        self.request,
                        _('No allowed warehouse found for item {item_code}. Skipping this item.').format(
                            item_code=material_item.item_code
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
            
            # Create transfer item
            TransferToLineItem.objects.create(
                transfer=transfer,
                company_id=company_id,
                material_item=material_item,
                material_item_code=material_item.item_code,
                quantity_required=quantity_required,
                unit=unit,
                source_warehouse=source_warehouse,
                source_warehouse_code=source_warehouse.public_code,
                destination_work_center=destination_work_center,
                material_scrap_allowance=scrap_allowance,
                is_extra=0,  # From BOM or Operations
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
        context['form_id'] = 'product-order-form'
        
        # Add formset for extra items (only if user has permission)
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        active_company_id = self.request.session.get('active_company_id')
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


class ProductOrderUpdateView(TransferRequestCreationMixin, BaseUpdateView, EditLockProtectedMixin):
    """Update an existing product order."""
    model = ProductOrder
    form_class = ProductOrderForm
    template_name = 'production/product_order_form.html'
    success_url = reverse_lazy('production:product_orders')
    feature_code = 'production.product_orders'
    required_action = 'edit_own'
    active_module = 'production'
    success_message = _('Product order updated successfully.')
    
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
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Product Orders'), 'url': reverse_lazy('production:product_orders')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:product_orders')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Product Order')
    
    def should_create_transfer_request(self, form) -> bool:
        """Check if transfer request should be created."""
        return form.cleaned_data.get('create_transfer_request', False) and form.cleaned_data.get('transfer_approved_by')
    
    def get_transfer_request_feature_code(self) -> str:
        """Return feature code for transfer request permission check."""
        return 'production.product_orders'
    
    def get_transfer_request_action(self) -> str:
        """Return action name for transfer request permission check."""
        return 'create_transfer_from_order'
    
    def get_transfer_request_kwargs(self, form) -> Dict[str, Any]:
        """Return kwargs for transfer request creation."""
        return {
            'approved_by': form.cleaned_data.get('transfer_approved_by'),
            'transfer_type': form.cleaned_data.get('transfer_type', 'full'),
            'selected_operations': form.cleaned_data.get('selected_operations', []),
        }
    
    def _create_transfer_request(
        self,
        order: ProductOrder,
        approved_by,
        company_id: int,
        transfer_type: str = 'full',
        selected_operations: list = None,
        **kwargs
    ) -> TransferToLine:
        """Helper method to create a transfer request from a product order."""
        if not order.bom:
            raise ValueError(_('Product order must have a BOM to create a transfer request.'))
        
        if selected_operations is None:
            selected_operations = []
        
        # Get extra items formset
        from production.forms import TransferToLineItemFormSet
        temp_transfer = TransferToLine()
        extra_items_formset = TransferToLineItemFormSet(
            self.request.POST,
            instance=temp_transfer,
            form_kwargs={'company_id': company_id},
            prefix='extra_items',
        )
        self.extra_items_formset = extra_items_formset
        
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
            transfer.transfer_code = generate_transfer_code(
                company_id=company_id,
                prefix='TR',
                width=8,
            )
            transfer.save(update_fields=['transfer_code'])
        
        # Collect materials to transfer based on transfer_type
        from inventory.models import ItemWarehouse
        from production.utils.transfer import get_operation_materials
        from production.models import ProcessOperation
        
        quantity_planned = order.quantity_planned
        materials_to_transfer = []  # List of (material_item, quantity, unit, scrap_allowance, source_warehouses_list)
        
        if transfer_type == 'full':
            # Transfer all BOM materials
            bom = order.bom
            bom_materials = bom.materials.filter(is_enabled=1).select_related('material_item')
            
            for bom_material in bom_materials:
                quantity_required = quantity_planned * bom_material.quantity_per_unit
                
                # Get source_warehouses from JSONField, or fallback to source_warehouse (backward compatibility)
                source_warehouses_list = bom_material.source_warehouses or []
                
                # If source_warehouses is empty but source_warehouse is set, use it for backward compatibility
                if not source_warehouses_list and bom_material.source_warehouse:
                    source_warehouses_list = [{
                        'warehouse_id': bom_material.source_warehouse.id,
                        'warehouse_code': bom_material.source_warehouse.public_code,
                        'priority': 1
                    }]
                
                materials_to_transfer.append((
                    bom_material.material_item,
                    quantity_required,
                    bom_material.unit,
                    bom_material.scrap_allowance,
                    source_warehouses_list,  # Include source_warehouses list from BOM
                ))
        
        elif transfer_type == 'operations' and selected_operations:
            # Transfer materials from selected operations
            operation_ids = [int(op_id) for op_id in selected_operations]
            operations = ProcessOperation.objects.filter(
                id__in=operation_ids,
                is_enabled=1,
            ).select_related('process')
            
            for operation in operations:
                operation_materials = get_operation_materials(operation, order)
                
                for op_material in operation_materials:
                    # Calculate quantity: quantity_planned × quantity_used (from ProcessOperationMaterial)
                    quantity_required = quantity_planned * op_material.quantity_used
                    
                    # Get scrap allowance and source_warehouses from BOM material if available
                    scrap_allowance = Decimal('0.00')
                    source_warehouses_list = []
                    if op_material.bom_material:
                        scrap_allowance = op_material.bom_material.scrap_allowance
                        source_warehouses_list = op_material.bom_material.source_warehouses or []
                        
                        # Backward compatibility: if source_warehouses is empty but source_warehouse is set
                        if not source_warehouses_list and op_material.bom_material.source_warehouse:
                            source_warehouses_list = [{
                                'warehouse_id': op_material.bom_material.source_warehouse.id,
                                'warehouse_code': op_material.bom_material.source_warehouse.public_code,
                                'priority': 1
                            }]
                    
                    materials_to_transfer.append((
                        op_material.material_item,
                        quantity_required,
                        op_material.unit,
                        scrap_allowance,
                        source_warehouses_list,  # Include source_warehouses list from BOM
                    ))
        
        # Create transfer items
        for material_item, quantity_required, unit, scrap_allowance, source_warehouses_list in materials_to_transfer:
            # Priority 1: Use first warehouse from source_warehouses list (sorted by priority)
            # Priority 2: Use first allowed warehouse from ItemWarehouse
            source_warehouse = None
            
            if source_warehouses_list and len(source_warehouses_list) > 0:
                # Sort by priority and get first warehouse (priority 1)
                sorted_warehouses = sorted(
                    source_warehouses_list,
                    key=lambda x: x.get('priority', 999)
                )
                
                if sorted_warehouses and sorted_warehouses[0].get('warehouse_id'):
                    from inventory.models import Warehouse
                    try:
                        source_warehouse = Warehouse.objects.get(
                            id=sorted_warehouses[0]['warehouse_id'],
                            company_id=company_id,
                            is_enabled=1,
                        )
                    except Warehouse.DoesNotExist:
                        pass
            
            if not source_warehouse:
                # Fallback: Get source warehouse from ItemWarehouse (first allowed warehouse)
                item_warehouse = ItemWarehouse.objects.filter(
                    item=material_item,
                    company_id=company_id,
                    is_enabled=1,
                ).select_related('warehouse').first()
                
                if not item_warehouse:
                    messages.warning(
                        self.request,
                        _('No allowed warehouse found for item {item_code}. Skipping this item.').format(
                            item_code=material_item.item_code
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
            
            # Create transfer item
            TransferToLineItem.objects.create(
                transfer=transfer,
                company_id=company_id,
                material_item=material_item,
                material_item_code=material_item.item_code,
                quantity_required=quantity_required,
                unit=unit,
                source_warehouse=source_warehouse,
                source_warehouse_code=source_warehouse.public_code,
                destination_work_center=destination_work_center,
                material_scrap_allowance=scrap_allowance,
                is_extra=0,  # From BOM or Operations
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
    
    @transaction.atomic
    def form_valid(self, form: ProductOrderForm) -> HttpResponseRedirect:
        """Auto-set edited_by and update related fields."""
        form.instance.edited_by = self.request.user
        
        # Update finished_item and bom from Process if Process changed
        if form.cleaned_data.get('process'):
            process = form.cleaned_data['process']
            form.instance.process = process
            form.instance.process_code = process.process_code
            form.instance.finished_item = process.finished_item
            form.instance.finished_item_code = process.finished_item.item_code
            if process.bom:
                form.instance.bom = process.bom
                form.instance.bom_code = process.bom.bom_code
        
        # Save product order first
        self.object = form.save()
        
        # Use mixin's create_transfer_request_if_needed to handle transfer request creation
        transfer_request = self.create_transfer_request_if_needed(form, self.object)
        if transfer_request:
            messages.success(self.request, _('Product order updated and transfer request created successfully.'))
        else:
            messages.success(self.request, _('Product order updated successfully.'))
        
        return HttpResponseRedirect(self.get_success_url())
    
    def _create_transfer_request(
        self,
        order: ProductOrder,
        approved_by,
        company_id: int,
        transfer_type: str = 'full',
        selected_operations: list = None,
    ) -> TransferToLine:
        """Helper method to create a transfer request from a product order."""
        if not order.bom:
            raise ValueError(_('Product order must have a BOM to create a transfer request.'))
        
        if selected_operations is None:
            selected_operations = []
        
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
            transfer.transfer_code = generate_transfer_code(
                company_id=company_id,
                prefix='TR',
                width=8,
            )
            transfer.save(update_fields=['transfer_code'])
        
        # Collect materials to transfer based on transfer_type
        from inventory.models import ItemWarehouse
        from production.utils.transfer import get_operation_materials
        from production.models import ProcessOperation
        
        quantity_planned = order.quantity_planned
        materials_to_transfer = []  # List of (material_item, quantity, unit, scrap_allowance, source_warehouses_list)
        
        if transfer_type == 'full':
            # Transfer all BOM materials
            bom = order.bom
            bom_materials = bom.materials.filter(is_enabled=1).select_related('material_item')
            
            for bom_material in bom_materials:
                quantity_required = quantity_planned * bom_material.quantity_per_unit
                
                # Get source_warehouses from JSONField, or fallback to source_warehouse (backward compatibility)
                source_warehouses_list = bom_material.source_warehouses or []
                
                # If source_warehouses is empty but source_warehouse is set, use it for backward compatibility
                if not source_warehouses_list and bom_material.source_warehouse:
                    source_warehouses_list = [{
                        'warehouse_id': bom_material.source_warehouse.id,
                        'warehouse_code': bom_material.source_warehouse.public_code,
                        'priority': 1
                    }]
                
                materials_to_transfer.append((
                    bom_material.material_item,
                    quantity_required,
                    bom_material.unit,
                    bom_material.scrap_allowance,
                    source_warehouses_list,  # Include source_warehouses list from BOM
                ))
        
        elif transfer_type == 'operations' and selected_operations:
            # Transfer materials from selected operations
            operation_ids = [int(op_id) for op_id in selected_operations]
            operations = ProcessOperation.objects.filter(
                id__in=operation_ids,
                is_enabled=1,
            ).select_related('process')
            
            for operation in operations:
                operation_materials = get_operation_materials(operation, order)
                
                for op_material in operation_materials:
                    # Calculate quantity: quantity_planned × quantity_used (from ProcessOperationMaterial)
                    quantity_required = quantity_planned * op_material.quantity_used
                    
                    # Get scrap allowance and source_warehouses from BOM material if available
                    scrap_allowance = Decimal('0.00')
                    source_warehouses_list = []
                    if op_material.bom_material:
                        scrap_allowance = op_material.bom_material.scrap_allowance
                        source_warehouses_list = op_material.bom_material.source_warehouses or []
                        
                        # Backward compatibility: if source_warehouses is empty but source_warehouse is set
                        if not source_warehouses_list and op_material.bom_material.source_warehouse:
                            source_warehouses_list = [{
                                'warehouse_id': op_material.bom_material.source_warehouse.id,
                                'warehouse_code': op_material.bom_material.source_warehouse.public_code,
                                'priority': 1
                            }]
                    
                    materials_to_transfer.append((
                        op_material.material_item,
                        quantity_required,
                        op_material.unit,
                        scrap_allowance,
                        source_warehouses_list,  # Include source_warehouses list from BOM
                    ))
        
        # Create transfer items
        for material_item, quantity_required, unit, scrap_allowance, source_warehouses_list in materials_to_transfer:
            # Priority 1: Use first warehouse from source_warehouses list (sorted by priority)
            # Priority 2: Use first allowed warehouse from ItemWarehouse
            source_warehouse = None
            
            if source_warehouses_list and len(source_warehouses_list) > 0:
                # Sort by priority and get first warehouse (priority 1)
                sorted_warehouses = sorted(
                    source_warehouses_list,
                    key=lambda x: x.get('priority', 999)
                )
                
                if sorted_warehouses and sorted_warehouses[0].get('warehouse_id'):
                    from inventory.models import Warehouse
                    try:
                        source_warehouse = Warehouse.objects.get(
                            id=sorted_warehouses[0]['warehouse_id'],
                            company_id=company_id,
                            is_enabled=1,
                        )
                    except Warehouse.DoesNotExist:
                        pass
            
            if not source_warehouse:
                # Fallback: Get source warehouse from ItemWarehouse (first allowed warehouse)
                item_warehouse = ItemWarehouse.objects.filter(
                    item=material_item,
                    company_id=company_id,
                    is_enabled=1,
                ).select_related('warehouse').first()
                
                if not item_warehouse:
                    messages.warning(
                        self.request,
                        _('No allowed warehouse found for item {item_code}. Skipping this item.').format(
                            item_code=material_item.item_code
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
            
            # Create transfer item
            TransferToLineItem.objects.create(
                transfer=transfer,
                company_id=company_id,
                material_item=material_item,
                material_item_code=material_item.item_code,
                quantity_required=quantity_required,
                unit=unit,
                source_warehouse=source_warehouse,
                source_warehouse_code=source_warehouse.public_code,
                destination_work_center=destination_work_center,
                material_scrap_allowance=scrap_allowance,
                is_extra=0,  # From BOM or Operations
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
        context['form_id'] = 'product-order-form'
        
        # Add formset for extra items (only if user has permission)
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        if self.object and self.object.company_id:
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


class ProductOrderDetailView(BaseDetailView):
    """Detail view for viewing product orders (read-only)."""
    model = ProductOrder
    template_name = 'shared/generic/generic_detail.html'
    context_object_name = 'object'
    feature_code = 'production.product_orders'
    required_action = 'view_own'
    active_module = 'production'
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'finished_item',
            'bom',
            'process',
            'approved_by',
            'created_by',
            'edited_by',
        )
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('View Product Order')
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add detail view context data."""
        context = super().get_context_data(**kwargs)
        order = self.object
        
        context['detail_title'] = self.get_page_title()
        context['info_banner'] = [
            {'label': _('Order Code'), 'value': order.order_code, 'type': 'code'},
            {'label': _('Order Date'), 'value': order.order_date},
            {'label': _('Status'), 'value': order.get_status_display()},
            {'label': _('Priority'), 'value': order.get_priority_display()},
        ]
        
        # Order Information section
        order_fields = [
            {
                'label': _('Finished Item'),
                'value': f"{order.finished_item.name} ({order.finished_item.item_code})",
            },
            {
                'label': _('Quantity Planned'),
                'value': f"{order.quantity_planned:.2f} {order.unit}",
            },
        ]
        if order.bom:
            order_fields.append({
                'label': _('BOM'),
                'value': f"{order.bom.bom_code} ({order.bom.version})",
            })
        if order.process:
            process_value = order.process.process_code
            if order.process.revision:
                process_value += f" ({_('Revision')}: {order.process.revision})"
            order_fields.append({
                'label': _('Process'),
                'value': process_value,
            })
        if order.due_date:
            order_fields.append({
                'label': _('Due Date'),
                'value': order.due_date,
            })
        if order.customer_reference:
            order_fields.append({
                'label': _('Customer Reference'),
                'value': order.customer_reference,
            })
        if order.approved_by:
            order_fields.append({
                'label': _('Approved By'),
                'value': order.approved_by.get_full_name() or order.approved_by.username,
            })
        
        detail_sections = [
            {
                'title': _('Order Information'),
                'fields': order_fields,
            },
        ]
        
        # Notes section
        if order.notes:
            detail_sections.append({
                'title': _('Notes'),
                'fields': [
                    {'label': _('Notes'), 'value': order.notes},
                ],
            })
        
        context['detail_sections'] = detail_sections
        return context
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('production:product_orders')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('production:product_order_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class ProductOrderDeleteView(BaseDeleteView):
    """Delete a product order."""
    model = ProductOrder
    success_url = reverse_lazy('production:product_orders')
    template_name = 'shared/generic/generic_confirm_delete.html'
    feature_code = 'production.product_orders'
    required_action = 'delete_own'
    active_module = 'production'
    success_message = _('Product order deleted successfully.')
    
    def get_queryset(self):
        """Filter by active company and optimize queries."""
        queryset = super().get_queryset()
        queryset = queryset.select_related('bom', 'finished_item')
        return queryset
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Product Order')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete this product order?')
    
    def get_object_details(self) -> List[Dict[str, str]]:
        """Return object details for confirmation."""
        details = [
            {'label': _('Order Code'), 'value': self.object.order_code},
        ]
        
        if self.object.bom:
            details.append({'label': _('BOM'), 'value': self.object.bom.bom_code})
        
        if self.object.finished_item:
            details.append({'label': _('Finished Item'), 'value': f"{self.object.finished_item.item_code} - {self.object.finished_item.name}"})
        
        details.extend([
            {'label': _('Quantity'), 'value': f"{self.object.quantity_planned} {self.object.unit}"},
            {'label': _('Status'), 'value': self.object.get_status_display()},
        ])
        
        return details
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Product Orders'), 'url': reverse_lazy('production:product_orders')},
            {'label': _('Delete'), 'url': None},
        ]

