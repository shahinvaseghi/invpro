"""
Utility functions for Transfer to Line requests.
"""
from typing import Set, List, Optional, Dict, Tuple, Any
from decimal import Decimal
from datetime import date
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from production.models import (
    TransferToLine,
    TransferToLineItem,
    ProductOrder,
    Process,
    ProcessOperation,
    ProcessOperationMaterial,
    BOMMaterial,
)


def generate_transfer_code(company_id: int, prefix: str = 'TR', width: int = 8) -> str:
    """
    Generate a sequential transfer code with prefix.
    
    This function should be called within a transaction to ensure atomicity
    when creating multiple transfers.
    
    Args:
        company_id: Company ID
        prefix: Prefix for the code (default: 'TR')
        width: Width of the numeric part (default: 8)
        
    Returns:
        Transfer code in format: prefix + zero-padded number (e.g., 'TR00000001')
    """
    # Get all transfer codes with the prefix for this company
    existing_codes = TransferToLine.objects.filter(
        company_id=company_id,
        transfer_code__startswith=prefix
    ).values_list('transfer_code', flat=True)
    
    # Extract numeric parts and find the maximum
    max_value = 0
    for code in existing_codes:
        if code.startswith(prefix):
            numeric_part = code[len(prefix):]
            if numeric_part.isdigit():
                max_value = max(max_value, int(numeric_part))
    
    # Generate next code
    next_value = max_value + 1
    numeric_code = str(next_value).zfill(width)
    
    # Ensure uniqueness (in case of race conditions or multiple calls in same transaction)
    full_code = prefix + numeric_code
    while TransferToLine.objects.filter(transfer_code=full_code).exists():
        next_value += 1
        numeric_code = str(next_value).zfill(width)
        full_code = prefix + numeric_code
    
    return full_code


def get_transferred_materials_for_order(
    order: ProductOrder,
    exclude_scrap_replacement: bool = True
) -> Set[int]:
    """
    Get set of material item IDs that have been transferred for this order.
    
    Args:
        order: ProductOrder instance
        exclude_scrap_replacement: If True, exclude transfers with is_scrap_replacement=1
        
    Returns:
        Set of material item IDs that have been transferred
    """
    transfers = TransferToLine.objects.filter(
        order=order,
        is_enabled=1,
    )
    
    if exclude_scrap_replacement:
        transfers = transfers.filter(is_scrap_replacement=0)
    
    transferred_item_ids = set()
    for transfer in transfers.select_related('order').prefetch_related('items'):
        for item in transfer.items.filter(is_enabled=1):
            transferred_item_ids.add(item.material_item_id)
    
    return transferred_item_ids


def get_transferred_operations_for_order(
    order: ProductOrder,
    exclude_scrap_replacement: bool = True
) -> Set[int]:
    """
    Get set of operation IDs that have been fully transferred for this order.
    
    An operation is considered transferred if all its materials have been transferred.
    
    Args:
        order: ProductOrder instance
        exclude_scrap_replacement: If True, exclude transfers with is_scrap_replacement=1
        
    Returns:
        Set of ProcessOperation IDs that have been fully transferred
    """
    if not order.process:
        return set()
    
    process = order.process
    operations = process.operations.filter(is_enabled=1).select_related('process')
    
    # Get all transferred materials for this order
    transferred_materials = get_transferred_materials_for_order(
        order,
        exclude_scrap_replacement=exclude_scrap_replacement
    )
    
    if not transferred_materials:
        return set()
    
    transferred_operations = set()
    
    for operation in operations:
        # Get all materials for this operation
        operation_materials = ProcessOperationMaterial.objects.filter(
            operation=operation,
            is_enabled=1,
        ).select_related('material_item', 'operation')
        
        # Check if all materials of this operation have been transferred
        all_transferred = True
        for op_material in operation_materials:
            if op_material.material_item_id not in transferred_materials:
                all_transferred = False
                break
        
        if all_transferred and operation_materials.exists():
            transferred_operations.add(operation.id)
    
    return transferred_operations


def is_full_order_transferred(
    order: ProductOrder,
    exclude_scrap_replacement: bool = True
) -> bool:
    """
    Check if all BOM materials for this order have been transferred.
    
    Args:
        order: ProductOrder instance
        exclude_scrap_replacement: If True, exclude transfers with is_scrap_replacement=1
        
    Returns:
        True if all BOM materials have been transferred, False otherwise
    """
    if not order.bom:
        return False
    
    # Get all BOM materials
    bom_materials = order.bom.materials.filter(is_enabled=1)
    
    if not bom_materials.exists():
        return False
    
    # Get transferred materials
    transferred_materials = get_transferred_materials_for_order(
        order,
        exclude_scrap_replacement=exclude_scrap_replacement
    )
    
    # Check if all BOM materials have been transferred
    for bom_material in bom_materials:
        if bom_material.material_item_id not in transferred_materials:
            return False
    
    return True


def get_available_operations_for_order(
    order: ProductOrder,
    include_scrap_replacement: bool = False,
    scrap_replacement_mode: bool = False
) -> List[Dict]:
    """
    Get list of available operations for this order.
    
    Args:
        order: ProductOrder instance
        include_scrap_replacement: If True, allow operations that were transferred
                                   for scrap replacement (deprecated, use scrap_replacement_mode)
        scrap_replacement_mode: If True, return only operations that have been transferred.
                               If False, return only operations that have NOT been transferred.
        
    Returns:
        List of dictionaries with operation info:
        [
            {
                'id': operation.id,
                'name': operation.name,
                'sequence_order': operation.sequence_order,
                'description': operation.description,
            },
            ...
        ]
    """
    if not order.process:
        return []
    
    process = order.process
    all_operations = process.operations.filter(is_enabled=1).order_by(
        'sequence_order', 'id'
    )
    
    # Get transferred operations (excluding scrap replacements for normal mode)
    exclude_scrap_replacement = not include_scrap_replacement and not scrap_replacement_mode
    transferred_operations = get_transferred_operations_for_order(
        order,
        exclude_scrap_replacement=exclude_scrap_replacement
    )
    
    available_operations = []
    for operation in all_operations:
        if scrap_replacement_mode:
            # Scrap replacement mode: only return operations that HAVE been transferred
            if operation.id in transferred_operations:
                available_operations.append({
                    'id': operation.id,
                    'name': operation.name or f"Operation {operation.sequence_order}",
                    'sequence_order': operation.sequence_order,
                    'description': operation.description or '',
                })
        else:
            # Normal mode: only return operations that have NOT been transferred
            if operation.id not in transferred_operations:
                available_operations.append({
                    'id': operation.id,
                    'name': operation.name or f"Operation {operation.sequence_order}",
                    'sequence_order': operation.sequence_order,
                    'description': operation.description or '',
                })
    
    return available_operations


def get_operation_materials(
    operation: ProcessOperation,
    order: ProductOrder
) -> List[ProcessOperationMaterial]:
    """
    Get all materials for a specific operation.
    
    Args:
        operation: ProcessOperation instance
        order: ProductOrder instance (for quantity calculation)
        
    Returns:
        List of ProcessOperationMaterial instances
    """
    return ProcessOperationMaterial.objects.filter(
        operation=operation,
        is_enabled=1,
    ).select_related('material_item', 'bom_material').order_by('id')


def select_source_warehouse_by_priority(
    company_id: int,
    item_id: int,
    source_warehouses_list: List[Dict],
    quantity_required: Decimal,
    as_of_date: Optional[date] = None
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Select source warehouse based on priority and inventory availability.
    
    Args:
        company_id: Company ID
        item_id: Item ID
        source_warehouses_list: List of warehouses with priorities
            Format: [{'warehouse_id': 1, 'warehouse_code': '001', 'priority': 1}, ...]
        quantity_required: Required quantity
        as_of_date: Date for inventory calculation (optional)
        
    Returns:
        Tuple of (selected_warehouse, error_message)
        If no warehouse found with sufficient inventory, returns (None, error_message)
    """
    from inventory.models import Warehouse
    from inventory.inventory_balance import calculate_item_balance
    
    if not source_warehouses_list:
        return None, _('No source warehouses configured for this item.')
    
    # Sort warehouses by priority (1, 2, 3...)
    sorted_warehouses = sorted(
        source_warehouses_list,
        key=lambda x: x.get('priority', 999)
    )
    
    # Check each warehouse in priority order
    for warehouse_info in sorted_warehouses:
        warehouse_id = warehouse_info.get('warehouse_id')
        if not warehouse_id:
            continue
        
        try:
            warehouse = Warehouse.objects.get(
                id=warehouse_id,
                company_id=company_id,
                is_enabled=1,
            )
        except Warehouse.DoesNotExist:
            continue
        
        # Check inventory balance
        try:
            balance_info = calculate_item_balance(
                company_id=company_id,
                warehouse_id=warehouse_id,
                item_id=item_id,
                as_of_date=as_of_date,
            )
            current_balance = Decimal(str(balance_info.get('current_balance', 0)))
            
            if current_balance >= quantity_required:
                return warehouse, None
        except Exception:
            # If calculation fails, skip this warehouse
            continue
    
    # No warehouse found with sufficient inventory
    warehouse_codes = [w.get('warehouse_code', 'Unknown') for w in sorted_warehouses]
    return None, _('Insufficient inventory in all source warehouses: {warehouses}').format(
        warehouses=', '.join(warehouse_codes)
    )


@transaction.atomic
def create_warehouse_transfer_for_transfer_to_line(
    transfer: TransferToLine,
    user
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Create a warehouse transfer issue document for a transfer to line request.
    
    This function creates an IssueWarehouseTransfer document with lines for each
    item in the transfer request, selecting source warehouses based on priority
    and inventory availability.
    
    Args:
        transfer: TransferToLine instance
        user: User creating the transfer (for audit fields)
        
    Returns:
        Tuple of (created_transfer_document, error_message)
        If creation fails, returns (None, error_message)
    """
    from inventory.models import (
        IssueWarehouseTransfer,
        IssueWarehouseTransferLine,
        Warehouse,
        ItemWarehouse,
    )
    from inventory.inventory_balance import calculate_item_balance
    from inventory.forms.base import generate_document_code
    
    # Get all transfer items
    transfer_items = transfer.items.filter(is_enabled=1).select_related(
        'material_item',
        'source_warehouse',
        'destination_work_center',
    )
    
    if not transfer_items.exists():
        return None, _('Transfer request has no items.')
    
    # Collect line data with source warehouse selection
    transfer_lines_data = []
    errors = []
    
    for item in transfer_items:
        # Get destination warehouse from WorkLine
        if not item.destination_work_center or not item.destination_work_center.warehouse:
            errors.append(
                _('Item {item_code}: No destination warehouse specified (WorkLine has no warehouse).').format(
                    item_code=item.material_item_code
                )
            )
            continue
        
        destination_warehouse = item.destination_work_center.warehouse
        
        # Get source warehouses list from BOM material (if available)
        source_warehouses_list = []
        if not item.is_extra:
            # For BOM items, get source_warehouses from BOM material
            # We need to find the BOM material for this item
            from production.models import BOMMaterial
            bom_material = BOMMaterial.objects.filter(
                bom=transfer.order.bom,
                material_item=item.material_item,
                is_enabled=1,
            ).first()
            
            if bom_material:
                source_warehouses_list = bom_material.source_warehouses or []
                
                # Backward compatibility
                if not source_warehouses_list and bom_material.source_warehouse:
                    source_warehouses_list = [{
                        'warehouse_id': bom_material.source_warehouse.id,
                        'warehouse_code': bom_material.source_warehouse.public_code,
                        'priority': 1
                    }]
        
        # For extra items, use the source_warehouse from the item itself
        if item.is_extra:
            if item.source_warehouse:
                source_warehouse = item.source_warehouse
            else:
                errors.append(
                    _('Item {item_code}: No source warehouse specified for extra item.').format(
                        item_code=item.material_item_code
                    )
                )
                continue
        else:
            # For BOM items, select source warehouse based on priority and inventory
            if source_warehouses_list:
                source_warehouse, error_msg = select_source_warehouse_by_priority(
                    company_id=transfer.company_id,
                    item_id=item.material_item_id,
                    source_warehouses_list=source_warehouses_list,
                    quantity_required=item.quantity_required,
                    as_of_date=transfer.transfer_date,
                )
                
                if not source_warehouse:
                    errors.append(
                        _('Item {item_code}: {error}').format(
                            item_code=item.material_item_code,
                            error=error_msg
                        )
                    )
                    continue
            else:
                # Fallback: use source_warehouse from item
                if item.source_warehouse:
                    source_warehouse = item.source_warehouse
                else:
                    # Try to get from ItemWarehouse
                    item_warehouse = ItemWarehouse.objects.filter(
                        item=item.material_item,
                        company_id=transfer.company_id,
                        is_enabled=1,
                    ).select_related('warehouse').first()
                    
                    if not item_warehouse:
                        errors.append(
                            _('Item {item_code}: No source warehouse found. Please configure ItemWarehouse or BOM source_warehouses.').format(
                                item_code=item.material_item_code
                            )
                        )
                        continue
                    
                    source_warehouse = item_warehouse.warehouse
        
        # Check inventory for all items (source_warehouse is already selected)
        # Note: For BOM items with source_warehouses_list, inventory check is also done in select_source_warehouse_by_priority
        # But we check here again to ensure consistency and catch any edge cases
        try:
            balance_info = calculate_item_balance(
                company_id=transfer.company_id,
                warehouse_id=source_warehouse.id,
                item_id=item.material_item_id,
                as_of_date=transfer.transfer_date,
            )
            current_balance = Decimal(str(balance_info.get('current_balance', 0)))
            
            if current_balance < item.quantity_required:
                errors.append(
                    _('Item {item_code}: Insufficient inventory in warehouse {warehouse_code}. Available: {available}, Required: {required}').format(
                        item_code=item.material_item_code,
                        warehouse_code=source_warehouse.public_code,
                        available=current_balance,
                        required=item.quantity_required
                    )
                )
                continue
        except Exception as e:
            errors.append(
                _('Item {item_code}: Error checking inventory: {error}').format(
                    item_code=item.material_item_code,
                    error=str(e)
                )
            )
            continue
        
        # Add to transfer lines data
        transfer_lines_data.append({
            'item': item.material_item,
            'item_code': item.material_item_code,
            'source_warehouse': source_warehouse,
            'destination_warehouse': destination_warehouse,
            'quantity': item.quantity_required,
            'unit': item.unit,
        })
    
    # If there are errors, don't create the transfer
    if errors:
        return None, ' '.join(errors)
    
    if not transfer_lines_data:
        return None, _('No valid items found for warehouse transfer.')
    
    # Create warehouse transfer document
    warehouse_transfer = IssueWarehouseTransfer.objects.create(
        company_id=transfer.company_id,
        document_code=generate_document_code(
            IssueWarehouseTransfer,
            transfer.company_id,
            "WHT"
        ),
        document_date=transfer.transfer_date,
        created_by=user,
        edited_by=user,
        production_transfer=transfer,
        production_transfer_code=transfer.transfer_code,
    )
    
    # Create transfer lines
    for idx, line_data in enumerate(transfer_lines_data, start=1):
        IssueWarehouseTransferLine.objects.create(
            company_id=transfer.company_id,
            document=warehouse_transfer,
            item=line_data['item'],
            item_code=line_data['item_code'],
            source_warehouse=line_data['source_warehouse'],
            source_warehouse_code=line_data['source_warehouse'].public_code,
            destination_warehouse=line_data['destination_warehouse'],
            destination_warehouse_code=line_data['destination_warehouse'].public_code,
            warehouse=line_data['source_warehouse'],  # For compatibility with IssueLineBase
            warehouse_code=line_data['source_warehouse'].public_code,
            quantity=line_data['quantity'],
            unit=line_data['unit'],
            sort_order=idx,
            is_enabled=1,
        )
    
    return warehouse_transfer, None

