"""
Utility functions for Transfer to Line requests.
"""
from typing import Set, List, Optional, Dict, Tuple
from decimal import Decimal

from production.models import (
    TransferToLine,
    TransferToLineItem,
    ProductOrder,
    Process,
    ProcessOperation,
    ProcessOperationMaterial,
    BOMMaterial,
)


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
    include_scrap_replacement: bool = False
) -> List[Dict]:
    """
    Get list of available operations that can still be transferred for this order.
    
    Args:
        order: ProductOrder instance
        include_scrap_replacement: If True, allow operations that were transferred
                                   for scrap replacement
        
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
    
    # Get transferred operations
    exclude_scrap_replacement = not include_scrap_replacement
    transferred_operations = get_transferred_operations_for_order(
        order,
        exclude_scrap_replacement=exclude_scrap_replacement
    )
    
    available_operations = []
    for operation in all_operations:
        # If include_scrap_replacement is False, exclude already transferred operations
        if not include_scrap_replacement and operation.id in transferred_operations:
            continue
        
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

