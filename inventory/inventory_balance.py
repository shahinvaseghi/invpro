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
    
    latest_surplus = models.StocktakingSurplus.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document_date__lte=as_of_date,
        is_locked=1,
        is_enabled=1,
    ).order_by('-document_date', '-id').first()
    
    latest_deficit = models.StocktakingDeficit.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document_date__lte=as_of_date,
        is_locked=1,
        is_enabled=1,
    ).order_by('-document_date', '-id').first()
    
    latest_date = None
    if latest_surplus and latest_deficit:
        latest_date = max(latest_surplus.document_date, latest_deficit.document_date)
    elif latest_surplus:
        latest_date = latest_surplus.document_date
    elif latest_deficit:
        latest_date = latest_deficit.document_date
    
    if not latest_date:
        return {
            'baseline_date': None,
            'baseline_quantity': Decimal('0'),
            'stocktaking_record_id': None,
        }
    
    # Get the surplus/deficit for this specific item and warehouse
    # from the documents referenced in the stocktaking record
    baseline_qty = Decimal('0')
    
    # Check surplus documents
    surplus_docs = models.StocktakingSurplus.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document_date__lte=latest_date,
        is_locked=1,
        is_enabled=1,
    ).aggregate(total=Sum('quantity_adjusted'))
    
    # Check deficit documents
    deficit_docs = models.StocktakingDeficit.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document_date__lte=latest_date,
        is_locked=1,
        is_enabled=1,
    ).aggregate(total=Sum('quantity_adjusted'))
    
    baseline_qty = (surplus_docs['total'] or Decimal('0')) - (deficit_docs['total'] or Decimal('0'))
    
    return {
        'baseline_date': latest_date,
        'baseline_quantity': baseline_qty,
        'stocktaking_record_id': None,
        'stocktaking_record_code': None,
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
    
    # If no baseline, start from beginning of time
    if baseline_date is None:
        baseline_date = date(1900, 1, 1)
    
    # Calculate receipts (positive movements)
    receipts = models.ReceiptPermanent.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document_date__gt=baseline_date,
        document_date__lte=as_of_date,
        is_locked=1,
        is_enabled=1,
    ).aggregate(total=Sum('quantity'))
    
    surplus = models.StocktakingSurplus.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document_date__gt=baseline_date,
        document_date__lte=as_of_date,
        is_locked=1,
        is_enabled=1,
    ).aggregate(total=Sum('quantity_adjusted'))
    
    receipts_total = (receipts['total'] or Decimal('0')) + (surplus['total'] or Decimal('0'))
    
    # Calculate issues (negative movements)
    issues_permanent = models.IssuePermanent.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document_date__gt=baseline_date,
        document_date__lte=as_of_date,
        is_locked=1,
        is_enabled=1,
    ).aggregate(total=Sum('quantity'))
    
    issues_consumption = models.IssueConsumption.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document_date__gt=baseline_date,
        document_date__lte=as_of_date,
        is_locked=1,
        is_enabled=1,
    ).aggregate(total=Sum('quantity'))
    
    deficit = models.StocktakingDeficit.objects.filter(
        company_id=company_id,
        warehouse_id=warehouse_id,
        item_id=item_id,
        document_date__gt=baseline_date,
        document_date__lte=as_of_date,
        is_locked=1,
        is_enabled=1,
    ).aggregate(total=Sum('quantity_adjusted'))
    
    issues_total = (
        (issues_permanent['total'] or Decimal('0')) +
        (issues_consumption['total'] or Decimal('0')) +
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
    # Get all items in this warehouse
    items_query = models.Item.objects.filter(
        company_id=company_id,
        is_enabled=1,
    )
    
    if item_type_id:
        items_query = items_query.filter(type_id=item_type_id)
    
    if item_category_id:
        items_query = items_query.filter(category_id=item_category_id)
    
    # Also filter by items that have warehouse assignment
    items_query = items_query.filter(
        warehouses__warehouse_id=warehouse_id,
        warehouses__is_enabled=1,
    ).distinct()
    
    balances = []
    for item in items_query:
        try:
            balance = calculate_item_balance(company_id, warehouse_id, item.id, as_of_date)
            # Only include items with non-zero balance or activity
            if balance['current_balance'] != 0 or balance['receipts_total'] > 0 or balance['issues_total'] > 0:
                balances.append(balance)
        except Exception as e:
            # Log error but continue with other items
            print(f"Error calculating balance for item {item.id}: {e}")
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

