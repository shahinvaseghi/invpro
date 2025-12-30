"""
Registry for documents that can be automated.
This registry defines all documents that can trigger automation processes.
"""
from django.utils.translation import gettext_lazy as _


# Registry of all automatable documents
AUTOMATABLE_DOCUMENTS = [
    # Accounting Documents
    {
        'id': 'accounting_document',
        'label': _('سند حسابداری'),
        'module': 'accounting',
        'document_type': 'AccountingDocument',
        'model': 'accounting.AccountingDocument',
        'category': _('حسابداری'),
    },
    
    # Sales Documents
    {
        'id': 'sales_invoice',
        'label': _('فاکتور فروش'),
        'module': 'sales',
        'document_type': 'Invoice',
        'model': 'sales.Invoice',
        'category': _('فروش'),
    },
    
    # Inventory Documents
    {
        'id': 'inventory_receipt_permanent',
        'label': _('رسید دائم'),
        'module': 'inventory',
        'document_type': 'ReceiptPermanent',
        'model': 'inventory.ReceiptPermanent',
        'category': _('انبار'),
    },
    {
        'id': 'inventory_receipt_temporary',
        'label': _('رسید موقت'),
        'module': 'inventory',
        'document_type': 'ReceiptTemporary',
        'model': 'inventory.ReceiptTemporary',
        'category': _('انبار'),
    },
    {
        'id': 'inventory_issue_permanent',
        'label': _('حواله دائم'),
        'module': 'inventory',
        'document_type': 'IssuePermanent',
        'model': 'inventory.IssuePermanent',
        'category': _('انبار'),
    },
    {
        'id': 'inventory_issue_consumption',
        'label': _('حواله مصرف'),
        'module': 'inventory',
        'document_type': 'IssueConsumption',
        'model': 'inventory.IssueConsumption',
        'category': _('انبار'),
    },
    {
        'id': 'inventory_warehouse_transfer',
        'label': _('انتقال انبار'),
        'module': 'inventory',
        'document_type': 'WarehouseTransfer',
        'model': 'inventory.WarehouseTransfer',
        'category': _('انبار'),
    },
    
    # Treasury Documents
    {
        'id': 'treasury_receive',
        'label': _('دریافت خزانه'),
        'module': 'accounting',
        'document_type': 'TreasuryReceive',
        'model': 'accounting.TreasuryReceive',
        'category': _('خزانه'),
    },
    {
        'id': 'treasury_pay',
        'label': _('پرداخت خزانه'),
        'module': 'accounting',
        'document_type': 'TreasuryPay',
        'model': 'accounting.TreasuryPay',
        'category': _('خزانه'),
    },
    {
        'id': 'treasury_transfer',
        'label': _('انتقال خزانه'),
        'module': 'accounting',
        'document_type': 'TreasuryTransfer',
        'model': 'accounting.TreasuryTransfer',
        'category': _('خزانه'),
    },
    
    # Procurement Documents
    {
        'id': 'procurement_purchase_order',
        'label': _('سفارش خرید'),
        'module': 'procurement',
        'document_type': 'PurchaseOrder',
        'model': 'procurement.PurchaseOrder',
        'category': _('تدارکات'),
    },
    {
        'id': 'procurement_purchase_invoice',
        'label': _('فاکتور خرید'),
        'module': 'procurement',
        'document_type': 'PurchaseInvoice',
        'model': 'procurement.PurchaseInvoice',
        'category': _('تدارکات'),
    },
    
    # Production Documents
    {
        'id': 'production_order',
        'label': _('سفارش تولید'),
        'module': 'production',
        'document_type': 'ProductionOrder',
        'model': 'production.ProductionOrder',
        'category': _('تولید'),
    },
]


def get_automatable_documents():
    """Get list of all automatable documents grouped by category."""
    documents_by_category = {}
    for doc in AUTOMATABLE_DOCUMENTS:
        category = doc['category']
        if category not in documents_by_category:
            documents_by_category[category] = []
        documents_by_category[category].append(doc)
    return documents_by_category


def get_document_by_id(document_id):
    """Get document configuration by ID."""
    for doc in AUTOMATABLE_DOCUMENTS:
        if doc['id'] == document_id:
            return doc
    return None

