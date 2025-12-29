"""
Registry for filterable fields of each document type.
This defines which fields can be used for filtering conditions.
"""
from django.utils.translation import gettext_lazy as _


# Registry of filterable fields for each document type
DOCUMENT_FILTERABLE_FIELDS = {
    'accounting.AccountingDocument': {
        'document_date': {
            'field_type': 'date',
            'label': _('تاریخ سند'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
        'document_number': {
            'field_type': 'string',
            'label': _('شماره سند'),
            'operators': ['==', '!=', 'contains', 'starts_with', 'ends_with'],
        },
        'status': {
            'field_type': 'choice',
            'label': _('وضعیت'),
            'operators': ['==', '!=', 'in', 'not_in'],
        },
    },
    
    'sales.Invoice': {
        'customer_tafsili': {
            'field_type': 'foreign_key',
            'model': 'accounting.TafsiliAccount',
            'label': _('تفصیلی مشتری'),
            'operators': ['==', 'in', 'hierarchy_level', 'hierarchy_parent', 'hierarchy_descendant'],
            'hierarchy_support': True,
        },
        'total_amount': {
            'field_type': 'number',
            'label': _('مبلغ کل'),
            'operators': ['==', '!=', '>', '<', '>=', '<='],
        },
        'payment_type': {
            'field_type': 'choice',
            'label': _('نوع پرداخت'),
            'operators': ['==', 'in'],
        },
        'payment_status': {
            'field_type': 'choice',
            'label': _('وضعیت پرداخت'),
            'operators': ['==', 'in'],
        },
        'document_date': {
            'field_type': 'date',
            'label': _('Document Date'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
    },
    
    'inventory.ReceiptPermanent': {
        'supplier': {
            'field_type': 'foreign_key',
            'model': 'inventory.Supplier',
            'label': _('تامین‌کننده'),
            'operators': ['==', 'in'],
        },
        'warehouse': {
            'field_type': 'foreign_key',
            'model': 'inventory.Warehouse',
            'label': _('انبار'),
            'operators': ['==', 'in'],
        },
        'document_date': {
            'field_type': 'date',
            'label': _('تاریخ سند'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
    },
    
    'inventory.ReceiptTemporary': {
        'supplier': {
            'field_type': 'foreign_key',
            'model': 'inventory.Supplier',
            'label': _('تامین‌کننده'),
            'operators': ['==', 'in'],
        },
        'warehouse': {
            'field_type': 'foreign_key',
            'model': 'inventory.Warehouse',
            'label': _('انبار'),
            'operators': ['==', 'in'],
        },
        'document_date': {
            'field_type': 'date',
            'label': _('تاریخ سند'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
    },
    
    'inventory.IssuePermanent': {
        'source_warehouse': {
            'field_type': 'foreign_key',
            'model': 'inventory.Warehouse',
            'label': _('انبار مبدأ'),
            'operators': ['==', 'in'],
        },
        'destination_warehouse': {
            'field_type': 'foreign_key',
            'model': 'inventory.Warehouse',
            'label': _('انبار مقصد'),
            'operators': ['==', 'in', 'is_null', 'is_not_null'],
        },
        'cost_center': {
            'field_type': 'foreign_key',
            'model': 'accounting.CostCenter',
            'label': _('مرکز هزینه'),
            'operators': ['==', 'in', 'is_null', 'is_not_null'],
        },
        'document_date': {
            'field_type': 'date',
            'label': _('تاریخ سند'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
    },
    
    'inventory.IssueConsumption': {
        'source_warehouse': {
            'field_type': 'foreign_key',
            'model': 'inventory.Warehouse',
            'label': _('انبار مبدأ'),
            'operators': ['==', 'in'],
        },
        'cost_center': {
            'field_type': 'foreign_key',
            'model': 'accounting.CostCenter',
            'label': _('مرکز هزینه'),
            'operators': ['==', 'in', 'is_null', 'is_not_null'],
        },
        'document_date': {
            'field_type': 'date',
            'label': _('تاریخ سند'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
    },
    
    'inventory.WarehouseTransfer': {
        'source_warehouse': {
            'field_type': 'foreign_key',
            'model': 'inventory.Warehouse',
            'label': _('انبار مبدأ'),
            'operators': ['==', 'in'],
        },
        'destination_warehouse': {
            'field_type': 'foreign_key',
            'model': 'inventory.Warehouse',
            'label': _('انبار مقصد'),
            'operators': ['==', 'in'],
        },
        'document_date': {
            'field_type': 'date',
            'label': _('تاریخ سند'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
    },
    
    'accounting.TreasuryReceive': {
        'cash_account': {
            'field_type': 'foreign_key',
            'model': 'accounting.Account',
            'label': _('حساب نقدی/بانکی'),
            'operators': ['==', 'in'],
        },
        'party_account': {
            'field_type': 'foreign_key',
            'model': 'accounting.TafsiliAccount',
            'label': _('طرف حساب'),
            'operators': ['==', 'in', 'hierarchy_level', 'hierarchy_parent'],
            'hierarchy_support': True,
        },
        'amount': {
            'field_type': 'number',
            'label': _('مبلغ'),
            'operators': ['==', '!=', '>', '<', '>=', '<='],
        },
        'document_date': {
            'field_type': 'date',
            'label': _('تاریخ سند'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
    },
    
    'accounting.TreasuryPay': {
        'cash_account': {
            'field_type': 'foreign_key',
            'model': 'accounting.Account',
            'label': _('حساب نقدی/بانکی'),
            'operators': ['==', 'in'],
        },
        'party_account': {
            'field_type': 'foreign_key',
            'model': 'accounting.TafsiliAccount',
            'label': _('طرف حساب'),
            'operators': ['==', 'in', 'hierarchy_level', 'hierarchy_parent'],
            'hierarchy_support': True,
        },
        'amount': {
            'field_type': 'number',
            'label': _('مبلغ'),
            'operators': ['==', '!=', '>', '<', '>=', '<='],
        },
        'document_date': {
            'field_type': 'date',
            'label': _('تاریخ سند'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
    },
    
    'accounting.TreasuryTransfer': {
        'source_account': {
            'field_type': 'foreign_key',
            'model': 'accounting.Account',
            'label': _('حساب مبدأ'),
            'operators': ['==', 'in'],
        },
        'destination_account': {
            'field_type': 'foreign_key',
            'model': 'accounting.Account',
            'label': _('حساب مقصد'),
            'operators': ['==', 'in'],
        },
        'amount': {
            'field_type': 'number',
            'label': _('مبلغ'),
            'operators': ['==', '!=', '>', '<', '>=', '<='],
        },
        'document_date': {
            'field_type': 'date',
            'label': _('تاریخ سند'),
            'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
        },
    },
}

# Global filter categories (available for all documents)
GLOBAL_FILTER_CATEGORIES = {
    'user': {
        'label': _('کاربر'),
        'field_type': 'foreign_key',
        'model': 'auth.User',
        'operators': ['==', 'in'],
    },
    'user_group': {
        'label': _('گروه کاربری'),
        'field_type': 'foreign_key',
        'model': 'auth.Group',
        'operators': ['in'],
    },
    'date': {
        'label': _('تاریخ'),
        'field_type': 'date',
        'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
    },
    'date_range': {
        'label': _('بازه تاریخی'),
        'field_type': 'date_range',
        'operators': ['between'],
    },
    'status': {
        'label': _('وضعیت'),
        'field_type': 'choice',
        'operators': ['==', '!=', 'in', 'not_in'],
    },
}


def get_filterable_fields_for_document(document_model: str) -> dict:
    """
    Get filterable fields for a specific document model.
    
    Args:
        document_model: Full model path (e.g., 'sales.Invoice')
    
    Returns:
        Dictionary of filterable fields
    """
    return DOCUMENT_FILTERABLE_FIELDS.get(document_model, {})


def get_global_filter_categories() -> dict:
    """Get global filter categories available for all documents."""
    return GLOBAL_FILTER_CATEGORIES


def get_field_info(document_model: str, field_name: str) -> dict:
    """
    Get information about a specific field.
    
    Args:
        document_model: Full model path
        field_name: Field name
    
    Returns:
        Field information dictionary or None
    """
    fields = get_filterable_fields_for_document(document_model)
    return fields.get(field_name)

