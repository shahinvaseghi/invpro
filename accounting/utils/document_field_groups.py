"""
Grouped field definitions for each document type.
This provides a better structure for displaying fields in UI with grouping.
"""
from django.utils.translation import gettext_lazy as _


# Grouped field definitions for better UI organization
DOCUMENT_FIELD_GROUPS = {
    'accounting.AccountingDocument': {
        'header_fields': {
            'label': _('فیلدهای هدر سند'),
            'fields': {
                'document_date': {
                    'field_type': 'date',
                    'label': _('تاریخ سند'),
                    'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
                    'ui_type': 'date_picker',
                },
                'document_number': {
                    'field_type': 'string',
                    'label': _('شماره سند'),
                    'operators': ['==', '!=', 'contains', 'starts_with', 'ends_with'],
                    'ui_type': 'text_input',
                },
                'status': {
                    'field_type': 'choice',
                    'label': _('وضعیت'),
                    'operators': ['==', '!=', 'in', 'not_in'],
                    'ui_type': 'select',
                },
            },
        },
        'line_fields': {
            'label': _('فیلدهای خطوط سند'),
            'fields': {
                'lines__tafsili': {
                    'field_type': 'foreign_key',
                    'model': 'accounting.TafsiliAccount',
                    'label': _('تفصیلی خط'),
                    'operators': ['==', 'in', 'hierarchy_level', 'hierarchy_parent'],
                    'ui_type': 'autocomplete',
                    'hierarchy_support': True,
                },
                'lines__cost_center': {
                    'field_type': 'foreign_key',
                    'model': 'accounting.CostCenter',
                    'label': _('مرکز هزینه خط'),
                    'operators': ['==', 'in', 'is_null', 'is_not_null'],
                    'ui_type': 'autocomplete',
                },
                'lines__amount': {
                    'field_type': 'number',
                    'label': _('مبلغ خط'),
                    'operators': ['==', '!=', '>', '<', '>=', '<='],
                    'ui_type': 'number_input',
                },
            },
        },
    },
    
    'sales.Invoice': {
        'header_fields': {
            'label': _('فیلدهای هدر فاکتور'),
            'fields': {
                'customer_tafsili': {
                    'field_type': 'foreign_key',
                    'model': 'accounting.TafsiliAccount',
                    'label': _('تفصیلی مشتری'),
                    'operators': ['==', 'in', 'hierarchy_level', 'hierarchy_parent', 'hierarchy_descendant'],
                    'ui_type': 'autocomplete',
                    'hierarchy_support': True,
                },
                'document_date': {
                    'field_type': 'date',
                    'label': _('تاریخ فاکتور'),
                    'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
                    'ui_type': 'date_picker',
                },
                'total_amount': {
                    'field_type': 'number',
                    'label': _('مبلغ کل فاکتور'),
                    'operators': ['==', '!=', '>', '<', '>=', '<='],
                    'ui_type': 'number_input',
                },
                'payment_type': {
                    'field_type': 'choice',
                    'label': _('نوع پرداخت'),
                    'operators': ['==', 'in'],
                    'ui_type': 'select',
                    'choices': ['cash', 'check', 'credit'],
                },
                'payment_status': {
                    'field_type': 'choice',
                    'label': _('وضعیت پرداخت'),
                    'operators': ['==', 'in'],
                    'ui_type': 'select',
                },
            },
        },
        'line_fields': {
            'label': _('فیلدهای خطوط فاکتور'),
            'fields': {
                'lines__product': {
                    'field_type': 'foreign_key',
                    'model': 'inventory.Product',
                    'label': _('کالا'),
                    'operators': ['==', 'in'],
                    'ui_type': 'autocomplete',
                },
                'lines__quantity': {
                    'field_type': 'number',
                    'label': _('تعداد'),
                    'operators': ['==', '!=', '>', '<', '>=', '<='],
                    'ui_type': 'number_input',
                },
                'lines__unit_price': {
                    'field_type': 'number',
                    'label': _('قیمت واحد'),
                    'operators': ['==', '!=', '>', '<', '>=', '<='],
                    'ui_type': 'number_input',
                },
                'lines__amount': {
                    'field_type': 'number',
                    'label': _('مبلغ خط'),
                    'operators': ['==', '!=', '>', '<', '>=', '<='],
                    'ui_type': 'number_input',
                },
            },
        },
    },
    
    'inventory.ReceiptPermanent': {
        'header_fields': {
            'label': _('فیلدهای هدر رسید'),
            'fields': {
                'supplier': {
                    'field_type': 'foreign_key',
                    'model': 'inventory.Supplier',
                    'label': _('تامین‌کننده'),
                    'operators': ['==', 'in'],
                    'ui_type': 'autocomplete',
                },
                'warehouse': {
                    'field_type': 'foreign_key',
                    'model': 'inventory.Warehouse',
                    'label': _('انبار'),
                    'operators': ['==', 'in'],
                    'ui_type': 'autocomplete',
                },
                'document_date': {
                    'field_type': 'date',
                    'label': _('تاریخ رسید'),
                    'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
                    'ui_type': 'date_picker',
                },
            },
        },
        'line_fields': {
            'label': _('فیلدهای خطوط رسید'),
            'fields': {
                'lines__product': {
                    'field_type': 'foreign_key',
                    'model': 'inventory.Product',
                    'label': _('کالا'),
                    'operators': ['==', 'in'],
                    'ui_type': 'autocomplete',
                },
                'lines__quantity': {
                    'field_type': 'number',
                    'label': _('تعداد'),
                    'operators': ['==', '!=', '>', '<', '>=', '<='],
                    'ui_type': 'number_input',
                },
            },
        },
    },
    
    'inventory.IssuePermanent': {
        'header_fields': {
            'label': _('فیلدهای هدر حواله'),
            'fields': {
                'source_warehouse': {
                    'field_type': 'foreign_key',
                    'model': 'inventory.Warehouse',
                    'label': _('انبار مبدأ'),
                    'operators': ['==', 'in'],
                    'ui_type': 'autocomplete',
                },
                'destination_warehouse': {
                    'field_type': 'foreign_key',
                    'model': 'inventory.Warehouse',
                    'label': _('انبار مقصد'),
                    'operators': ['==', 'in', 'is_null', 'is_not_null'],
                    'ui_type': 'autocomplete',
                },
                'cost_center': {
                    'field_type': 'foreign_key',
                    'model': 'accounting.CostCenter',
                    'label': _('مرکز هزینه'),
                    'operators': ['==', 'in', 'is_null', 'is_not_null'],
                    'ui_type': 'autocomplete',
                },
                'document_date': {
                    'field_type': 'date',
                    'label': _('تاریخ حواله'),
                    'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
                    'ui_type': 'date_picker',
                },
            },
        },
        'line_fields': {
            'label': _('فیلدهای خطوط حواله'),
            'fields': {
                'lines__product': {
                    'field_type': 'foreign_key',
                    'model': 'inventory.Product',
                    'label': _('کالا'),
                    'operators': ['==', 'in'],
                    'ui_type': 'autocomplete',
                },
                'lines__quantity': {
                    'field_type': 'number',
                    'label': _('تعداد'),
                    'operators': ['==', '!=', '>', '<', '>=', '<='],
                    'ui_type': 'number_input',
                },
            },
        },
    },
    
    'accounting.TreasuryReceive': {
        'header_fields': {
            'label': _('فیلدهای هدر دریافت'),
            'fields': {
                'cash_account': {
                    'field_type': 'foreign_key',
                    'model': 'accounting.Account',
                    'label': _('حساب نقدی/بانکی'),
                    'operators': ['==', 'in'],
                    'ui_type': 'autocomplete',
                },
                'party_account': {
                    'field_type': 'foreign_key',
                    'model': 'accounting.TafsiliAccount',
                    'label': _('طرف حساب'),
                    'operators': ['==', 'in', 'hierarchy_level', 'hierarchy_parent'],
                    'ui_type': 'autocomplete',
                    'hierarchy_support': True,
                },
                'amount': {
                    'field_type': 'number',
                    'label': _('مبلغ'),
                    'operators': ['==', '!=', '>', '<', '>=', '<='],
                    'ui_type': 'number_input',
                },
                'document_date': {
                    'field_type': 'date',
                    'label': _('تاریخ دریافت'),
                    'operators': ['==', '!=', '>', '<', '>=', '<=', 'between'],
                    'ui_type': 'date_picker',
                },
            },
        },
    },
}


def get_field_groups_for_document(document_model: str) -> dict:
    """
    Get grouped fields for a specific document model.
    
    Args:
        document_model: Full model path (e.g., 'sales.Invoice')
    
    Returns:
        Dictionary with field groups (header_fields, line_fields, etc.)
    """
    return DOCUMENT_FIELD_GROUPS.get(document_model, {})


def get_all_fields_for_document(document_model: str) -> dict:
    """
    Get all fields flattened from groups for a document.
    
    Args:
        document_model: Full model path
    
    Returns:
        Dictionary of all fields with their full path
    """
    groups = get_field_groups_for_document(document_model)
    all_fields = {}
    
    for group_name, group_data in groups.items():
        if 'fields' in group_data:
            for field_name, field_info in group_data['fields'].items():
                all_fields[field_name] = field_info
    
    return all_fields

