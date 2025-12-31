"""
Extractable fields configuration for automation system.
This defines which fields from each document type can be extracted as variables.
"""
from django.utils.translation import gettext_lazy as _


# Configuration for extractable fields from each document type
DOCUMENT_EXTRACTABLE_FIELDS = {
    'accounting.AccountingDocument': {
        'header_fields': {
            'document_date': {
                'field_type': 'date',
                'label': _('تاریخ سند'),
                'data_type': 'date',
                'extractable': True,
                'field_path': 'document_date',
            },
            'document_number': {
                'field_type': 'string',
                'label': _('شماره سند'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'document_number',
            },
            'description': {
                'field_type': 'string',
                'label': _('شرح سند'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'description',
            },
            'status': {
                'field_type': 'choice',
                'label': _('وضعیت سند'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'status',
            },
            'total_debit': {
                'field_type': 'number',
                'label': _('مجموع بدهکار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'total_debit',
            },
            'total_credit': {
                'field_type': 'number',
                'label': _('مجموع بستانکار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'total_credit',
            },
            'created_by': {
                'field_type': 'foreign_key',
                'model': 'auth.User',
                'label': _('کاربر صادرکننده'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'created_by',
                'related_fields': {
                    'username': {'label': _('نام کاربری'), 'data_type': 'string'},
                    'first_name': {'label': _('نام'), 'data_type': 'string'},
                    'last_name': {'label': _('نام خانوادگی'), 'data_type': 'string'},
                    'email': {'label': _('ایمیل'), 'data_type': 'string'},
                },
            },
            'fiscal_year': {
                'field_type': 'foreign_key',
                'model': 'accounting.FiscalYear',
                'label': _('سال مالی'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'fiscal_year',
                'related_fields': {
                    'fiscal_year_name': {'label': _('نام سال مالی'), 'data_type': 'string'},
                    'fiscal_year_code': {'label': _('کد سال مالی'), 'data_type': 'string'},
                },
            },
        },
        'line_fields': {
            'debit_account': {
                'field_type': 'foreign_key',
                'model': 'accounting.Account',
                'label': _('حساب بدهکار'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.gl_account',
                'aggregatable': False,
                'related_fields': {
                    'account_code': {'label': _('کد حساب'), 'data_type': 'string'},
                    'account_name': {'label': _('نام حساب'), 'data_type': 'string'},
                },
            },
            'debit_sub_account': {
                'field_type': 'foreign_key',
                'model': 'accounting.Account',
                'label': _('معین بدهکار'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.sub_account',
                'aggregatable': False,
                'related_fields': {
                    'account_code': {'label': _('کد معین'), 'data_type': 'string'},
                    'account_name': {'label': _('نام معین'), 'data_type': 'string'},
                },
            },
            'debit_tafsili': {
                'field_type': 'foreign_key',
                'model': 'accounting.Account',
                'label': _('تفصیلی بدهکار'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.tafsili_account',
                'aggregatable': False,
                'related_fields': {
                    'account_code': {'label': _('کد تفصیلی'), 'data_type': 'string'},
                    'account_name': {'label': _('نام تفصیلی'), 'data_type': 'string'},
                    'hierarchy_level': {'label': _('سطح تفصیلی'), 'data_type': 'number'},
                },
            },
            'debit_tafsili_hierarchy_level': {
                'field_type': 'number',
                'label': _('سطح تفصیلی بدهکار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.tafsili_account.hierarchy_level',
                'aggregatable': False,
            },
            'credit_account': {
                'field_type': 'foreign_key',
                'model': 'accounting.Account',
                'label': _('حساب بستانکار'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.gl_account',
                'aggregatable': False,
                'related_fields': {
                    'account_code': {'label': _('کد حساب'), 'data_type': 'string'},
                    'account_name': {'label': _('نام حساب'), 'data_type': 'string'},
                },
            },
            'credit_sub_account': {
                'field_type': 'foreign_key',
                'model': 'accounting.Account',
                'label': _('معین بستانکار'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.sub_account',
                'aggregatable': False,
                'related_fields': {
                    'account_code': {'label': _('کد معین'), 'data_type': 'string'},
                    'account_name': {'label': _('نام معین'), 'data_type': 'string'},
                },
            },
            'credit_tafsili': {
                'field_type': 'foreign_key',
                'model': 'accounting.Account',
                'label': _('تفصیلی بستانکار'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.tafsili_account',
                'aggregatable': False,
                'related_fields': {
                    'account_code': {'label': _('کد تفصیلی'), 'data_type': 'string'},
                    'account_name': {'label': _('نام تفصیلی'), 'data_type': 'string'},
                    'hierarchy_level': {'label': _('سطح تفصیلی'), 'data_type': 'number'},
                },
            },
            'credit_tafsili_hierarchy_level': {
                'field_type': 'number',
                'label': _('سطح تفصیلی بستانکار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.tafsili_account.hierarchy_level',
                'aggregatable': False,
            },
            'line_amount': {
                'field_type': 'number',
                'label': _('مبلغ خط'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.debit',
                'aggregatable': True,
                'aggregation_types': ['sum', 'count', 'avg', 'max', 'min'],
            },
            'line_credit_amount': {
                'field_type': 'number',
                'label': _('مبلغ بستانکار خط'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.credit',
                'aggregatable': True,
                'aggregation_types': ['sum', 'count', 'avg', 'max', 'min'],
            },
            'line_description': {
                'field_type': 'string',
                'label': _('توضیحات خط'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'lines.description',
                'aggregatable': False,
            },
            'line_number': {
                'field_type': 'number',
                'label': _('شماره خط'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.line_number',
                'aggregatable': False,
            },
        },
        'aggregated_fields': {
            'total_lines_amount': {
                'field_type': 'aggregated',
                'label': _('مجموع مبلغ تمام خطوط'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.debit',
                'aggregation_type': 'sum',
            },
            'total_lines_count': {
                'field_type': 'aggregated',
                'label': _('تعداد خطوط سند'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines',
                'aggregation_type': 'count',
            },
            'average_line_amount': {
                'field_type': 'aggregated',
                'label': _('میانگین مبلغ خطوط'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.debit',
                'aggregation_type': 'avg',
            },
            'max_line_amount': {
                'field_type': 'aggregated',
                'label': _('حداکثر مبلغ خط'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.debit',
                'aggregation_type': 'max',
            },
            'min_line_amount': {
                'field_type': 'aggregated',
                'label': _('حداقل مبلغ خط'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.debit',
                'aggregation_type': 'min',
            },
        },
    },
    
    # Add other document types here as needed
    # 'sales.Invoice': { ... },
    # 'inventory.ReceiptPermanent': { ... },
}


def get_extractable_fields_for_document(document_model: str) -> dict:
    """
    Get extractable fields configuration for a specific document model.
    
    Args:
        document_model: Full model path (e.g., 'accounting.AccountingDocument')
    
    Returns:
        Dictionary with extractable fields grouped by type (header_fields, line_fields, aggregated_fields)
    """
    return DOCUMENT_EXTRACTABLE_FIELDS.get(document_model, {})


def get_all_extractable_fields_flat(document_model: str) -> dict:
    """
    Get all extractable fields flattened (for easier iteration).
    
    Args:
        document_model: Full model path
    
    Returns:
        Dictionary of all extractable fields with their configuration
    """
    fields_config = get_extractable_fields_for_document(document_model)
    all_fields = {}
    
    for group_name, group_fields in fields_config.items():
        if isinstance(group_fields, dict):
            for field_name, field_config in group_fields.items():
                all_fields[field_name] = field_config
    
    return all_fields


def is_field_extractable(document_model: str, field_path: str) -> bool:
    """
    Check if a specific field path is extractable for a document.
    
    Args:
        document_model: Full model path
        field_path: Field path (e.g., 'document_date', 'lines.amount')
    
    Returns:
        True if field is extractable, False otherwise
    """
    fields_config = get_extractable_fields_for_document(document_model)
    
    # Check in all groups
    for group_fields in fields_config.values():
        if isinstance(group_fields, dict):
            for field_config in group_fields.values():
                if field_config.get('field_path') == field_path:
                    return field_config.get('extractable', False)
    
    return False

