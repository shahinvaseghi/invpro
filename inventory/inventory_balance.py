"""
Inventory balance calculation utilities.

This module provides functions to calculate current inventory balances
based on the last stocktaking record and subsequent locked documents.
"""

from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Optional
from django.db.models import Sum, Q, F
from django.utils import timezone

from . import models


def get_last_stocktaking_baseline(
    company_id: int,
    warehouse_id: int,
    item_id: int,
    as_of_date: Optional[date] = None
) -> Dict:
    """
    Get the baseline balance from the last approved stocktaking record.
    
    Returns:
        dict with 'baseline_date', 'baseline_quantity', 'stocktaking_record_id'
        If no stocktaking found, returns baseline_quantity=0 and baseline_date=None
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()
    
    # First, try to find approved StocktakingRecord (this is the proper baseline)
    latest_record = models.StocktakingRecord.objects.filter(
        company_id=company_id,
        document_date__lte=as_of_date,
        approval_status='approved',
        is_locked=1,
        is_enabled=1,
    ).order_by('-document_date', '-id').first()
    
    if latest_record:
        # Use the record date as baseline, but start from beginning of time for movements
        # This ensures all receipts/issues before and after baseline_date are included
        # Deficit/surplus documents will be included as movements after baseline_date
        return {
            'baseline_date': date(1900, 1, 1),  # Start from beginning to include all movements
            'baseline_quantity': Decimal('0'),
            'stocktaking_record_id': latest_record.id,
            'stocktaking_record_code': latest_record.document_code,
            'stocktaking_record_date': latest_record.document_date,  # Keep original date for reference
        }
    
    # If no StocktakingRecord found, return None for baseline_date
    # Deficit/surplus documents will be included as movements, but only if there's a StocktakingRecord
    # Without a StocktakingRecord, there's no proper baseline
    return {
        'baseline_date': None,
        'baseline_quantity': Decimal('0'),
        'stocktaking_record_id': None,
    }


def calculate_movements_after_baseline(
    company_id: int,
    warehouse_id: int,
    item_id: int,
    baseline_date: Optional[date],
    as_of_date: Optional[date] = None
) -> Dict:
    """
    Calculate all inventory movements (receipts and issues) after baseline date.
    
    Returns:
        dict with 'receipts_total', 'issues_total', 'adjustments_net'
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()
    
    # Ensure as_of_date is a date object
    if not isinstance(as_of_date, date):
        try:
            if isinstance(as_of_date, str):
                as_of_date = date.fromisoformat(as_of_date)
            else:
                as_of_date = timezone.now().date()
        except (ValueError, TypeError):
            as_of_date = timezone.now().date()
    
    # If no baseline, start from beginning of time
    if baseline_date is None:
        baseline_date = date(1900, 1, 1)
    
    # Ensure baseline_date is a date object
    if not isinstance(baseline_date, date):
        try:
            if isinstance(baseline_date, str):
                baseline_date = date.fromisoformat(baseline_date)
            else:
                baseline_date = date(1900, 1, 1)
        except (ValueError, TypeError):
            baseline_date = date(1900, 1, 1)
    
    # Calculate receipts (positive movements) from line items
    receipts_perm = models.ReceiptPermanentLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document__document_date__gte=baseline_date,
        document__document_date__lte=as_of_date,
        document__is_enabled=1,
    ).aggregate(total=Sum('quantity'))
    
    receipts_consignment = models.ReceiptConsignmentLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document__document_date__gte=baseline_date,
        document__document_date__lte=as_of_date,
        document__is_enabled=1,
    ).aggregate(total=Sum('quantity'))
    
    surplus = models.StocktakingSurplusLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document__document_date__gte=baseline_date,
        document__document_date__lte=as_of_date,
        document__is_locked=1,
        document__is_enabled=1,
    ).aggregate(total=Sum('quantity_adjusted'))
    
    receipts_total = (
        (receipts_perm['total'] or Decimal('0')) + 
        (receipts_consignment['total'] or Decimal('0')) + 
        (surplus['total'] or Decimal('0'))
    )
    
    # Calculate issues (negative movements) from line items
    issues_permanent = models.IssuePermanentLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document__document_date__gte=baseline_date,
        document__document_date__lte=as_of_date,
        document__is_enabled=1,
    ).aggregate(total=Sum('quantity'))
    
    issues_consumption = models.IssueConsumptionLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document__document_date__gte=baseline_date,
        document__document_date__lte=as_of_date,
        document__is_enabled=1,
    ).aggregate(total=Sum('quantity'))
    
    issues_consignment = models.IssueConsignmentLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document__document_date__gte=baseline_date,
        document__document_date__lte=as_of_date,
        document__is_enabled=1,
    ).aggregate(total=Sum('quantity'))
    
    deficit = models.StocktakingDeficitLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document__document_date__gte=baseline_date,
        document__document_date__lte=as_of_date,
        document__is_locked=1,
        document__is_enabled=1,
    ).aggregate(total=Sum('quantity_adjusted'))
    
    issues_total = (
        (issues_permanent['total'] or Decimal('0')) +
        (issues_consumption['total'] or Decimal('0')) +
        (issues_consignment['total'] or Decimal('0')) +
        (deficit['total'] or Decimal('0'))
    )
    
    return {
        'receipts_total': receipts_total,
        'issues_total': issues_total,
        'surplus_total': surplus['total'] or Decimal('0'),
        'deficit_total': deficit['total'] or Decimal('0'),
    }


def calculate_item_balance(
    company_id: int,
    warehouse_id: int,
    item_id: int,
    as_of_date: Optional[date] = None
) -> Dict:
    """
    Calculate the current inventory balance for a specific item in a warehouse.
    
    Args:
        company_id: Company ID
        warehouse_id: Warehouse ID
        item_id: Item ID
        as_of_date: Calculate balance as of this date (default: today)
    
    Returns:
        dict with complete balance information including:
        - company_code, warehouse_code, item_code, item_name
        - baseline_date, baseline_quantity
        - receipts_total, issues_total
        - current_balance
        - last_calculated_at
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()
    
    # Get item and warehouse details
    item = models.Item.objects.get(id=item_id)
    warehouse = models.Warehouse.objects.get(id=warehouse_id)
    
    # Get baseline from last stocktaking
    baseline = get_last_stocktaking_baseline(company_id, warehouse_id, item_id, as_of_date)
    
    # Calculate movements after baseline
    movements = calculate_movements_after_baseline(
        company_id,
        warehouse_id,
        item_id,
        baseline['baseline_date'],
        as_of_date
    )
    
    # Calculate current balance
    current_balance = (
        baseline['baseline_quantity'] +
        movements['receipts_total'] -
        movements['issues_total']
    )
    
    return {
        'company_id': company_id,
        'company_code': item.company_code,
        'warehouse_id': warehouse_id,
        'warehouse_code': warehouse.public_code,
        'warehouse_name': warehouse.name,
        'item_id': item_id,
        'item_code': item.item_code,
        'item_name': item.name,
        'baseline_date': baseline['baseline_date'],
        'baseline_quantity': float(baseline['baseline_quantity']),
        'stocktaking_record_id': baseline.get('stocktaking_record_id'),
        'stocktaking_record_code': baseline.get('stocktaking_record_code'),
        'receipts_total': float(movements['receipts_total']),
        'issues_total': float(movements['issues_total']),
        'surplus_total': float(movements['surplus_total']),
        'deficit_total': float(movements['deficit_total']),
        'current_balance': float(current_balance),
        'as_of_date': as_of_date.isoformat(),
        'last_calculated_at': timezone.now().isoformat(),
    }


def calculate_warehouse_balances(
    company_id: int,
    warehouse_id: int,
    as_of_date: Optional[date] = None,
    item_type_id: Optional[int] = None,
    item_category_id: Optional[int] = None,
) -> List[Dict]:
    """
    Calculate balances for all items in a warehouse.
    
    Args:
        company_id: Company ID
        warehouse_id: Warehouse ID
        as_of_date: Calculate balance as of this date (default: today)
        item_type_id: Filter by item type (optional)
        item_category_id: Filter by item category (optional)
    
    Returns:
        List of balance dictionaries (one per item)
    """
    if as_of_date is None:
        as_of_date = timezone.now().date()
    
    # Get all items that have activity in this warehouse (receipts, issues, or stocktaking)
    from django.db.models import Q
    
    # First, get items with warehouse assignment (traditional way)
    items_with_assignment = models.Item.objects.filter(
        company_id=company_id,
        is_enabled=1,
        warehouses__warehouse_id=warehouse_id,
        warehouses__is_enabled=1,
    ).values_list('id', flat=True)
    
    # Second, get items with actual transactions in this warehouse (only enabled documents)
    # Filter by as_of_date to only include items with activity up to that date
    items_with_receipts = models.ReceiptPermanentLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        document__is_enabled=1,
        document__document_date__lte=as_of_date,
    ).values_list('item_id', flat=True).distinct()
    
    items_with_consignment_receipts = models.ReceiptConsignmentLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        document__is_enabled=1,
        document__document_date__lte=as_of_date,
    ).values_list('item_id', flat=True).distinct()
    
    items_with_issues = models.IssuePermanentLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        document__is_enabled=1,
        document__document_date__lte=as_of_date,
    ).values_list('item_id', flat=True).distinct()
    
    items_with_consumption = models.IssueConsumptionLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        document__is_enabled=1,
        document__document_date__lte=as_of_date,
    ).values_list('item_id', flat=True).distinct()
    
    items_with_consignment_issues = models.IssueConsignmentLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        document__is_enabled=1,
        document__document_date__lte=as_of_date,
    ).values_list('item_id', flat=True).distinct()
    
    # Also check for items with stocktaking records (surplus/deficit)
    items_with_surplus = models.StocktakingSurplusLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        document__is_enabled=1,
        document__document_date__lte=as_of_date,
    ).values_list('item_id', flat=True).distinct()
    
    items_with_deficit = models.StocktakingDeficitLine.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        document__is_enabled=1,
        document__document_date__lte=as_of_date,
    ).values_list('item_id', flat=True).distinct()
    
    # Combine all item IDs
    all_item_ids = (
        set(items_with_assignment) | 
        set(items_with_receipts) | 
        set(items_with_consignment_receipts) | 
        set(items_with_issues) | 
        set(items_with_consumption) |
        set(items_with_consignment_issues) |
        set(items_with_surplus) |
        set(items_with_deficit)
    )
    
    # Build final query
    # Include items with transactions even if disabled (they have inventory activity)
    # But only include enabled items if they only have warehouse assignment
    items_with_transactions = (
        set(items_with_receipts) | 
        set(items_with_consignment_receipts) | 
        set(items_with_issues) | 
        set(items_with_consumption) |
        set(items_with_consignment_issues) |
        set(items_with_surplus) |
        set(items_with_deficit)
    )
    
    # For items with transactions, include them regardless of enabled status
    # For items only with assignment, require enabled=1
    items_query = models.Item.objects.filter(
        id__in=all_item_ids,
        company_id=company_id,
    ).filter(
        Q(id__in=items_with_transactions) | Q(is_enabled=1)
    )
    
    if item_type_id:
        items_query = items_query.filter(type_id=item_type_id)
    
    if item_category_id:
        items_query = items_query.filter(category_id=item_category_id)
    
    balances = []
    for item in items_query:
        try:
            balance = calculate_item_balance(company_id, warehouse_id, item.id, as_of_date)
            # Only include items with non-zero balance or activity
            if balance['current_balance'] != 0 or balance['receipts_total'] > 0 or balance['issues_total'] > 0:
                balances.append(balance)
        except Exception as e:
            # Log error with more details but continue with other items
            import traceback
            print(f"Error calculating balance for item {item.id} ({item.item_code}): {e}")
            print(f"Traceback: {traceback.format_exc()}")
            continue
    
    return balances


def get_low_stock_items(
    company_id: int,
    warehouse_id: Optional[int] = None,
    threshold_quantity: Decimal = Decimal('10'),
) -> List[Dict]:
    """
    Get items with balance below threshold (low stock alert).
    
    Args:
        company_id: Company ID
        warehouse_id: Warehouse ID (optional, all warehouses if None)
        threshold_quantity: Minimum quantity threshold
    
    Returns:
        List of items with low stock
    """
    # TODO: Implement low stock detection
    # This would require calculating balances and filtering
    pass

