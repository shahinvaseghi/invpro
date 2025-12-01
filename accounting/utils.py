"""
Utility functions for accounting module.
"""
from django.db import models
from .models import FiscalYear

# Note: get_fiscal_year_from_date is now defined in accounting.models
# to avoid circular imports. Import it from there if needed.


def get_available_fiscal_years(company_id: int) -> models.QuerySet:
    """
    Get list of fiscal years that have documents (accounting, inventory, or sales).
    If no documents exist, return only the current fiscal year.
    
    Args:
        company_id: Company ID for multi-tenant filtering
    
    Returns:
        QuerySet of FiscalYear objects
    """
    from django.db.models import Q, Exists, OuterRef
    
    # Check for accounting documents
    from .models import AccountingDocument
    has_accounting_docs = Exists(
        AccountingDocument.objects.filter(
            company_id=company_id,
            fiscal_year_id=OuterRef('pk')
        )
    )
    
    # Check for inventory documents (receipts, issues, stocktaking)
    try:
        from inventory.models import (
            ReceiptTemporary, ReceiptPermanent, ReceiptConsignment,
            IssuePermanent, IssueConsumption, IssueConsignment,
            StocktakingRecord, PurchaseRequest, WarehouseRequest
        )
        
        has_inventory_docs = (
            Exists(ReceiptTemporary.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk'))) |
            Exists(ReceiptPermanent.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk'))) |
            Exists(ReceiptConsignment.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk'))) |
            Exists(IssuePermanent.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk'))) |
            Exists(IssueConsumption.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk'))) |
            Exists(IssueConsignment.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk'))) |
            Exists(StocktakingRecord.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk'))) |
            Exists(PurchaseRequest.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk'))) |
            Exists(WarehouseRequest.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk')))
        )
    except ImportError:
        has_inventory_docs = models.Q(pk__isnull=True)  # False condition
    
    # Check for sales documents
    try:
        from sales.models import Invoice, Order
        has_sales_docs = (
            Exists(Invoice.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk'))) |
            Exists(Order.objects.filter(company_id=company_id, fiscal_year_id=OuterRef('pk')))
        )
    except ImportError:
        has_sales_docs = models.Q(pk__isnull=True)  # False condition
    
    # Get fiscal years that have documents OR are current
    fiscal_years = FiscalYear.objects.filter(
        company_id=company_id,
        is_enabled=1
    ).filter(
        has_accounting_docs | has_inventory_docs | has_sales_docs | Q(is_current=1)
    ).distinct().order_by('-fiscal_year_code')
    
    return fiscal_years

