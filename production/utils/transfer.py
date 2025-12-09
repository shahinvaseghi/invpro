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


def get_warehouse_inventory_balance(
    company_id: int,
    warehouse_id: int,
    item_id: int,
    as_of_date: Optional[date] = None
) -> Decimal:
    """
    Get inventory balance for an item in a warehouse.
    
    Args:
        company_id: Company ID
        warehouse_id: Warehouse ID
        item_id: Item ID
        as_of_date: Date for inventory calculation (optional)
        
    Returns:
        Current balance as Decimal, or Decimal('0') if error
    """
    from inventory.inventory_balance import calculate_item_balance
    
    try:
        balance_info = calculate_item_balance(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            as_of_date=as_of_date,
        )
        return Decimal(str(balance_info.get('current_balance', 0)))
    except Exception:
        return Decimal('0')


def select_source_warehouses_by_priority(
    company_id: int,
    item_id: int,
    source_warehouses_list: List[Dict],
    quantity_required: Decimal,
    as_of_date: Optional[date] = None
) -> Tuple[List[Tuple[Any, Decimal]], Optional[str]]:
    """
    Select source warehouses based on priority and inventory availability.
    This function implements the logic:
    - Step 2: If entire quantity is in one warehouse, return that warehouse
    - Step 3: If quantity is spread across multiple warehouses, return all needed warehouses
    
    Args:
        company_id: Company ID
        item_id: Item ID
        source_warehouses_list: List of warehouses with priorities
            Format: [{'warehouse_id': 1, 'warehouse_code': '001', 'priority': 1}, ...]
        quantity_required: Required quantity
        as_of_date: Date for inventory calculation (optional)
        
    Returns:
        Tuple of (list of (warehouse, quantity) tuples, error_message)
        If no warehouses found with sufficient inventory, returns ([], error_message)
    """
    from inventory.models import Warehouse
    
    if not source_warehouses_list:
        return [], _('No source warehouses configured for this item.')
    
    # Sort warehouses by priority (1, 2, 3...)
    sorted_warehouses = sorted(
        source_warehouses_list,
        key=lambda x: x.get('priority', 999)
    )
    
    selected_warehouses = []
    remaining_quantity = quantity_required
    
    # Step 2: Check if entire quantity is in one warehouse (by priority)
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
        current_balance = get_warehouse_inventory_balance(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            as_of_date=as_of_date,
        )
        
        # If this warehouse has enough for entire quantity, return it
        if current_balance >= quantity_required:
            return [(warehouse, quantity_required)], None
        
        # Step 3: If not enough in one warehouse, collect from multiple warehouses
        if current_balance > 0:
            quantity_from_this_warehouse = min(current_balance, remaining_quantity)
            selected_warehouses.append((warehouse, quantity_from_this_warehouse))
            remaining_quantity -= quantity_from_this_warehouse
            
            if remaining_quantity <= 0:
                # We have enough from multiple warehouses
                return selected_warehouses, None
    
    # Not enough inventory in all warehouses
    if selected_warehouses:
        # We found some inventory but not enough
        total_available = sum(qty for _, qty in selected_warehouses)
        warehouse_codes = [w.get('warehouse_code', 'Unknown') for w in sorted_warehouses]
        return [], _('Insufficient inventory in source warehouses: {warehouses}. Available: {available}, Required: {required}').format(
            warehouses=', '.join(warehouse_codes),
            available=total_available,
            required=quantity_required
        )
    else:
        warehouse_codes = [w.get('warehouse_code', 'Unknown') for w in sorted_warehouses]
        return [], _('Insufficient inventory in all source warehouses: {warehouses}').format(
            warehouses=', '.join(warehouse_codes)
        )


def select_source_warehouse_by_priority(
    company_id: int,
    item_id: int,
    source_warehouses_list: List[Dict],
    quantity_required: Decimal,
    as_of_date: Optional[date] = None
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Select source warehouse based on priority and inventory availability.
    DEPRECATED: Use select_source_warehouses_by_priority instead for multi-warehouse support.
    
    This function is kept for backward compatibility but only returns the first warehouse
    that has sufficient inventory.
    """
    warehouses, error_msg = select_source_warehouses_by_priority(
        company_id=company_id,
        item_id=item_id,
        source_warehouses_list=source_warehouses_list,
        quantity_required=quantity_required,
        as_of_date=as_of_date,
    )
    
    if error_msg:
        return None, error_msg
    
    if warehouses:
        # Return first warehouse (for backward compatibility)
        return warehouses[0][0], None
    
    return None, _('No warehouse found with sufficient inventory.')


def process_item_with_substitutes(
    company_id: int,
    main_item_id: int,
    main_item_code: str,
    quantity_required: Decimal,
    unit: str,
    source_warehouses_list: List[Dict],
    destination_warehouse: Any,
    as_of_date: Optional[date],
    bom_material_id: Optional[int] = None
) -> Tuple[List[Dict], Optional[str]]:
    """
    Process an item with substitute logic (Steps 1-5).
    
    Returns:
        Tuple of (list of transfer line data dicts, error_message)
    """
    from production.models import BOMMaterial, BOMMaterialAlternative
    
    transfer_lines_data = []
    
    # Step 1: Check main item and source warehouses by priority
    warehouses_with_quantities, error_msg = select_source_warehouses_by_priority(
        company_id=company_id,
        item_id=main_item_id,
        source_warehouses_list=source_warehouses_list,
        quantity_required=quantity_required,
        as_of_date=as_of_date,
    )
    
    if not error_msg and warehouses_with_quantities:
        # Steps 2 & 3: We have enough inventory (single or multiple warehouses)
        total_available = sum(qty for _, qty in warehouses_with_quantities)
        if total_available >= quantity_required:
            # Create lines for each warehouse
            remaining_qty = quantity_required
            for warehouse, available_qty in warehouses_with_quantities:
                if remaining_qty <= 0:
                    break
                qty_to_use = min(available_qty, remaining_qty)
                transfer_lines_data.append({
                    'item_id': main_item_id,
                    'item_code': main_item_code,
                    'source_warehouse': warehouse,
                    'destination_warehouse': destination_warehouse,
                    'quantity': qty_to_use,
                    'unit': unit,
                })
                remaining_qty -= qty_to_use
            return transfer_lines_data, None
    
    # Step 4 & 5: Not enough inventory, check substitutes
    if not bom_material_id:
        # No BOM material, can't check alternatives
        return [], error_msg or _('Insufficient inventory for item {item_code}').format(
            item_code=main_item_code
        )
    
    # Get BOM material alternatives
    bom_material = BOMMaterial.objects.filter(id=bom_material_id).first()
    if not bom_material:
        return [], error_msg or _('BOM material not found')
    
    alternatives = BOMMaterialAlternative.objects.filter(
        bom_material=bom_material,
        is_enabled=1,
    ).select_related('alternative_item').order_by('priority')
    
    if not alternatives.exists():
        return [], error_msg or _('No substitute items configured for item {item_code}').format(
            item_code=main_item_code
        )
    
    # Calculate how much we got from main item
    main_item_available = sum(qty for _, qty in warehouses_with_quantities) if warehouses_with_quantities else Decimal('0')
    remaining_quantity = quantity_required - main_item_available
    
    # Step 4 & 5: Not enough inventory, check substitutes
    # First, separate alternatives by combination flag
    combinable_alternatives = []
    non_combinable_alternatives = []
    
    for alternative in alternatives:
        if alternative.is_combinable == 1:
            combinable_alternatives.append(alternative)
        else:
            non_combinable_alternatives.append(alternative)
    
    # Step 5: Check combinable alternatives FIRST (if main item doesn't have enough)
    # According to logic: ابتدا باید کالاهایی که تیک ترکیب دارند بررسی شوند
    if main_item_available < quantity_required:
        # Try combinable alternatives first
        if combinable_alternatives:
            # If main item has some inventory, try combination
            if main_item_available > 0:
                for alternative in combinable_alternatives:
                    # Add main item lines first
                    main_lines = []
                    main_remaining = main_item_available
                    for warehouse, available_qty in warehouses_with_quantities:
                        if main_remaining <= 0:
                            break
                        qty_to_use = min(available_qty, main_remaining)
                        main_lines.append({
                            'item_id': main_item_id,
                            'item_code': main_item_code,
                            'source_warehouse': warehouse,
                            'destination_warehouse': destination_warehouse,
                            'quantity': qty_to_use,
                            'unit': unit,
                        })
                        main_remaining -= qty_to_use
                    
                    # Check if alternative can cover the remainder
                    alt_warehouses, alt_error = select_source_warehouses_by_priority(
                        company_id=company_id,
                        item_id=alternative.alternative_item_id,
                        source_warehouses_list=alternative.source_warehouses or [],
                        quantity_required=remaining_quantity,
                        as_of_date=as_of_date,
                    )
                    
                    if not alt_error and alt_warehouses:
                        alt_total = sum(qty for _, qty in alt_warehouses)
                        if alt_total >= remaining_quantity:
                            # We have a solution: main item + alternative
                            transfer_lines_data.extend(main_lines)
                            alt_remaining = remaining_quantity
                            for warehouse, available_qty in alt_warehouses:
                                if alt_remaining <= 0:
                                    break
                                qty_to_use = min(available_qty, alt_remaining)
                                transfer_lines_data.append({
                                    'item_id': alternative.alternative_item_id,
                                    'item_code': alternative.alternative_item_code,
                                    'source_warehouse': warehouse,
                                    'destination_warehouse': destination_warehouse,
                                    'quantity': qty_to_use,
                                    'unit': alternative.unit,
                                })
                                alt_remaining -= qty_to_use
                            return transfer_lines_data, None
            else:
                # Main item has NO inventory, use combinable alternative for full quantity
                for alternative in combinable_alternatives:
                    alt_warehouses, alt_error = select_source_warehouses_by_priority(
                        company_id=company_id,
                        item_id=alternative.alternative_item_id,
                        source_warehouses_list=alternative.source_warehouses or [],
                        quantity_required=quantity_required,
                        as_of_date=as_of_date,
                    )
                    
                    if not alt_error and alt_warehouses:
                        alt_total = sum(qty for _, qty in alt_warehouses)
                        if alt_total >= quantity_required:
                            # Use alternative for full quantity
                            alt_remaining = quantity_required
                            for warehouse, available_qty in alt_warehouses:
                                if alt_remaining <= 0:
                                    break
                                qty_to_use = min(available_qty, alt_remaining)
                                transfer_lines_data.append({
                                    'item_id': alternative.alternative_item_id,
                                    'item_code': alternative.alternative_item_code,
                                    'source_warehouse': warehouse,
                                    'destination_warehouse': destination_warehouse,
                                    'quantity': qty_to_use,
                                    'unit': alternative.unit,
                                })
                                alt_remaining -= qty_to_use
                            return transfer_lines_data, None
        
        # Step 4: If combinable alternatives didn't work, check non-combinable alternatives
        # According to logic: اگر با ترکیب اصلی و جایگزین نشد، بعد برود سراغ کالاهای جایگزین
        for alternative in non_combinable_alternatives:
            # For each alternative, apply same logic (Steps 1 & 2)
            alt_warehouses, alt_error = select_source_warehouses_by_priority(
                company_id=company_id,
                item_id=alternative.alternative_item_id,
                source_warehouses_list=alternative.source_warehouses or [],
                quantity_required=quantity_required,  # Full quantity required
                as_of_date=as_of_date,
            )
            
            if not alt_error and alt_warehouses:
                alt_total = sum(qty for _, qty in alt_warehouses)
                if alt_total >= quantity_required:
                    # Use this alternative for full quantity
                    alt_remaining = quantity_required
                    for warehouse, available_qty in alt_warehouses:
                        if alt_remaining <= 0:
                            break
                        qty_to_use = min(available_qty, alt_remaining)
                        transfer_lines_data.append({
                            'item_id': alternative.alternative_item_id,
                            'item_code': alternative.alternative_item_code,
                            'source_warehouse': warehouse,
                            'destination_warehouse': destination_warehouse,
                            'quantity': qty_to_use,
                            'unit': alternative.unit,
                        })
                        alt_remaining -= qty_to_use
                    return transfer_lines_data, None
    
    # No solution found
    return transfer_lines_data, error_msg or _('Insufficient inventory for item {item_code} and its substitutes').format(
        item_code=main_item_code
    )


@transaction.atomic
def create_warehouse_transfer_for_transfer_to_line(
    transfer: TransferToLine,
    user
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Create a warehouse transfer issue document for a transfer to line request.
    
    This function implements the complete 5-step logic:
    1. Check main item and source warehouses by priority
    2. If entire quantity is in one warehouse, issue from that warehouse
    3. If quantity is spread across multiple warehouses, issue from those warehouses
    4. If not available and combination flag is off, check substitute items
    5. If combination flag is on, use main item + substitute combination
    
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
        Item,
    )
    from inventory.forms.base import generate_document_code
    from production.models import BOMMaterial
    
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
        bom_material_id = None
        
        if not item.is_extra:
            # For BOM items, get source_warehouses from BOM material
            bom_material = BOMMaterial.objects.filter(
                bom=transfer.order.bom,
                material_item=item.material_item,
                is_enabled=1,
            ).first()
            
            if bom_material:
                bom_material_id = bom_material.id
                source_warehouses_list = bom_material.source_warehouses or []
                
                # Backward compatibility
                if not source_warehouses_list and bom_material.source_warehouse:
                    source_warehouses_list = [{
                        'warehouse_id': bom_material.source_warehouse.id,
                        'warehouse_code': bom_material.source_warehouse.public_code,
                        'priority': 1
                    }]
        else:
            # For extra items, use the source_warehouse from the item itself
            if item.source_warehouse:
                source_warehouses_list = [{
                    'warehouse_id': item.source_warehouse.id,
                    'warehouse_code': item.source_warehouse.public_code,
                    'priority': 1
                }]
            else:
                errors.append(
                    _('Item {item_code}: No source warehouse specified for extra item.').format(
                        item_code=item.material_item_code
                    )
                )
                continue
        
        # If no source warehouses configured, try ItemWarehouse
        if not source_warehouses_list:
            item_warehouse = ItemWarehouse.objects.filter(
                item=item.material_item,
                company_id=transfer.company_id,
                is_enabled=1,
            ).select_related('warehouse').first()
            
            if item_warehouse:
                source_warehouses_list = [{
                    'warehouse_id': item_warehouse.warehouse.id,
                    'warehouse_code': item_warehouse.warehouse.public_code,
                    'priority': 1
                }]
            else:
                errors.append(
                    _('Item {item_code}: No source warehouse found. Please configure ItemWarehouse or BOM source_warehouses.').format(
                        item_code=item.material_item_code
                    )
                )
                continue
        
        # Process item with substitute logic
        item_lines, error_msg = process_item_with_substitutes(
            company_id=transfer.company_id,
            main_item_id=item.material_item_id,
            main_item_code=item.material_item_code,
            quantity_required=item.quantity_required,
            unit=item.unit,
            source_warehouses_list=source_warehouses_list,
            destination_warehouse=destination_warehouse,
            as_of_date=transfer.transfer_date,
            bom_material_id=bom_material_id if not item.is_extra else None,
        )
        
        if error_msg:
            errors.append(
                _('Item {item_code}: {error}').format(
                    item_code=item.material_item_code,
                    error=error_msg
                )
            )
            continue
        
        # Convert item_ids to Item objects
        for line_data in item_lines:
            try:
                item_obj = Item.objects.get(id=line_data['item_id'])
                transfer_lines_data.append({
                    'item': item_obj,
                    'item_code': line_data['item_code'],
                    'source_warehouse': line_data['source_warehouse'],
                    'destination_warehouse': line_data['destination_warehouse'],
                    'quantity': line_data['quantity'],
                    'unit': line_data['unit'],
                })
            except Item.DoesNotExist:
                errors.append(
                    _('Item {item_code}: Item not found.').format(
                        item_code=line_data['item_code']
                    )
                )
    
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

