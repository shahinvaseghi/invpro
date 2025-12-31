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
    
    'inventory.ReceiptPermanent': {
        'header_fields': {
            'document_code': {
                'field_type': 'string',
                'label': _('کد رسید'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'document_code',
            },
            'document_date': {
                'field_type': 'date',
                'label': _('تاریخ رسید'),
                'data_type': 'date',
                'extractable': True,
                'field_path': 'document_date',
            },
            'notes': {
                'field_type': 'string',
                'label': _('یادداشت‌ها'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'notes',
            },
            'temporary_receipt': {
                'field_type': 'foreign_key',
                'model': 'inventory.ReceiptTemporary',
                'label': _('رسید موقت مرتبط'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'temporary_receipt',
                'related_fields': {
                    'document_code': {'label': _('کد رسید موقت'), 'data_type': 'string'},
                    'document_date': {'label': _('تاریخ رسید موقت'), 'data_type': 'date'},
                },
            },
            'purchase_request': {
                'field_type': 'foreign_key',
                'model': 'inventory.PurchaseRequest',
                'label': _('درخواست خرید مرتبط'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'purchase_request',
                'related_fields': {
                    'request_code': {'label': _('کد درخواست'), 'data_type': 'string'},
                },
            },
            'created_by': {
                'field_type': 'foreign_key',
                'model': 'auth.User',
                'label': _('کاربر ایجادکننده'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'created_by',
                'related_fields': {
                    'username': {'label': _('نام کاربری'), 'data_type': 'string'},
                    'first_name': {'label': _('نام'), 'data_type': 'string'},
                    'last_name': {'label': _('نام خانوادگی'), 'data_type': 'string'},
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
                },
            },
        },
        'line_fields': {
            'item': {
                'field_type': 'foreign_key',
                'model': 'inventory.Item',
                'label': _('کالا'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.item',
                'aggregatable': False,
                'related_fields': {
                    'item_code': {'label': _('کد کالا'), 'data_type': 'string'},
                    'name': {'label': _('نام کالا'), 'data_type': 'string'},
                },
            },
            'warehouse': {
                'field_type': 'foreign_key',
                'model': 'inventory.Warehouse',
                'label': _('انبار'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.warehouse',
                'aggregatable': False,
                'related_fields': {
                    'public_code': {'label': _('کد انبار'), 'data_type': 'string'},
                    'name': {'label': _('نام انبار'), 'data_type': 'string'},
                },
            },
            'supplier': {
                'field_type': 'foreign_key',
                'model': 'inventory.Supplier',
                'label': _('تامین‌کننده'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.supplier',
                'aggregatable': False,
                'related_fields': {
                    'public_code': {'label': _('کد تامین‌کننده'), 'data_type': 'string'},
                    'name': {'label': _('نام تامین‌کننده'), 'data_type': 'string'},
                },
            },
            'quantity': {
                'field_type': 'number',
                'label': _('مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregatable': True,
                'aggregation_types': ['sum', 'count', 'avg', 'max', 'min'],
            },
            'unit': {
                'field_type': 'string',
                'label': _('واحد'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'lines.unit',
                'aggregatable': False,
            },
            'line_notes': {
                'field_type': 'string',
                'label': _('یادداشت خط'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'lines.line_notes',
                'aggregatable': False,
            },
        },
        'aggregated_fields': {
            'total_quantity': {
                'field_type': 'aggregated',
                'label': _('مجموع مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregation_type': 'sum',
            },
            'total_lines_count': {
                'field_type': 'aggregated',
                'label': _('تعداد خطوط'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines',
                'aggregation_type': 'count',
            },
        },
    },
    
    'inventory.ReceiptTemporary': {
        'header_fields': {
            'document_code': {
                'field_type': 'string',
                'label': _('کد رسید موقت'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'document_code',
            },
            'document_date': {
                'field_type': 'date',
                'label': _('تاریخ رسید موقت'),
                'data_type': 'date',
                'extractable': True,
                'field_path': 'document_date',
            },
            'status': {
                'field_type': 'choice',
                'label': _('وضعیت رسید'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'status',
            },
            'supplier': {
                'field_type': 'foreign_key',
                'model': 'inventory.Supplier',
                'label': _('تامین‌کننده'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'supplier',
                'related_fields': {
                    'public_code': {'label': _('کد تامین‌کننده'), 'data_type': 'string'},
                    'name': {'label': _('نام تامین‌کننده'), 'data_type': 'string'},
                },
            },
            'qc_approved_by': {
                'field_type': 'foreign_key',
                'model': 'auth.User',
                'label': _('کاربر تاییدکننده QC'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'qc_approved_by',
                'related_fields': {
                    'username': {'label': _('نام کاربری'), 'data_type': 'string'},
                },
            },
            'qc_approved_at': {
                'field_type': 'datetime',
                'label': _('زمان تایید QC'),
                'data_type': 'datetime',
                'extractable': True,
                'field_path': 'qc_approved_at',
            },
            'created_by': {
                'field_type': 'foreign_key',
                'model': 'auth.User',
                'label': _('کاربر ایجادکننده'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'created_by',
                'related_fields': {
                    'username': {'label': _('نام کاربری'), 'data_type': 'string'},
                },
            },
        },
        'line_fields': {
            'item': {
                'field_type': 'foreign_key',
                'model': 'inventory.Item',
                'label': _('کالا'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.item',
                'aggregatable': False,
                'related_fields': {
                    'item_code': {'label': _('کد کالا'), 'data_type': 'string'},
                    'name': {'label': _('نام کالا'), 'data_type': 'string'},
                },
            },
            'warehouse': {
                'field_type': 'foreign_key',
                'model': 'inventory.Warehouse',
                'label': _('انبار'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.warehouse',
                'aggregatable': False,
            },
            'quantity': {
                'field_type': 'number',
                'label': _('مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregatable': True,
                'aggregation_types': ['sum', 'count', 'avg', 'max', 'min'],
            },
            'qc_approved_quantity': {
                'field_type': 'number',
                'label': _('مقدار تایید شده QC'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.qc_approved_quantity',
                'aggregatable': True,
                'aggregation_types': ['sum', 'count', 'avg', 'max', 'min'],
            },
            'is_qc_approved': {
                'field_type': 'boolean',
                'label': _('تایید شده توسط QC'),
                'data_type': 'boolean',
                'extractable': True,
                'field_path': 'lines.is_qc_approved',
                'aggregatable': False,
            },
        },
        'aggregated_fields': {
            'total_quantity': {
                'field_type': 'aggregated',
                'label': _('مجموع مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregation_type': 'sum',
            },
            'total_qc_approved_quantity': {
                'field_type': 'aggregated',
                'label': _('مجموع مقدار تایید شده QC'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.qc_approved_quantity',
                'aggregation_type': 'sum',
            },
        },
    },
    
    'inventory.IssuePermanent': {
        'header_fields': {
            'document_code': {
                'field_type': 'string',
                'label': _('کد حواله'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'document_code',
            },
            'document_date': {
                'field_type': 'date',
                'label': _('تاریخ حواله'),
                'data_type': 'date',
                'extractable': True,
                'field_path': 'document_date',
            },
            'department_unit': {
                'field_type': 'foreign_key',
                'model': 'shared.CompanyUnit',
                'label': _('واحد سازمانی'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'department_unit',
                'related_fields': {
                    'public_code': {'label': _('کد واحد'), 'data_type': 'string'},
                    'name': {'label': _('نام واحد'), 'data_type': 'string'},
                },
            },
            'warehouse_request': {
                'field_type': 'foreign_key',
                'model': 'inventory.WarehouseRequest',
                'label': _('درخواست انبار مرتبط'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'warehouse_request',
                'related_fields': {
                    'request_code': {'label': _('کد درخواست'), 'data_type': 'string'},
                },
            },
            'created_by': {
                'field_type': 'foreign_key',
                'model': 'auth.User',
                'label': _('کاربر ایجادکننده'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'created_by',
                'related_fields': {
                    'username': {'label': _('نام کاربری'), 'data_type': 'string'},
                },
            },
        },
        'line_fields': {
            'item': {
                'field_type': 'foreign_key',
                'model': 'inventory.Item',
                'label': _('کالا'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.item',
                'aggregatable': False,
                'related_fields': {
                    'item_code': {'label': _('کد کالا'), 'data_type': 'string'},
                    'name': {'label': _('نام کالا'), 'data_type': 'string'},
                },
            },
            'warehouse': {
                'field_type': 'foreign_key',
                'model': 'inventory.Warehouse',
                'label': _('انبار مبدأ'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.warehouse',
                'aggregatable': False,
            },
            'quantity': {
                'field_type': 'number',
                'label': _('مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregatable': True,
                'aggregation_types': ['sum', 'count', 'avg', 'max', 'min'],
            },
            'destination_type': {
                'field_type': 'string',
                'label': _('نوع مقصد'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'lines.destination_type',
                'aggregatable': False,
            },
            'destination_code': {
                'field_type': 'string',
                'label': _('کد مقصد'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'lines.destination_code',
                'aggregatable': False,
            },
        },
        'aggregated_fields': {
            'total_quantity': {
                'field_type': 'aggregated',
                'label': _('مجموع مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregation_type': 'sum',
            },
            'total_lines_count': {
                'field_type': 'aggregated',
                'label': _('تعداد خطوط'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines',
                'aggregation_type': 'count',
            },
        },
    },
    
    'inventory.IssueConsumption': {
        'header_fields': {
            'document_code': {
                'field_type': 'string',
                'label': _('کد حواله مصرف'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'document_code',
            },
            'document_date': {
                'field_type': 'date',
                'label': _('تاریخ حواله مصرف'),
                'data_type': 'date',
                'extractable': True,
                'field_path': 'document_date',
            },
            'department_unit': {
                'field_type': 'foreign_key',
                'model': 'shared.CompanyUnit',
                'label': _('واحد سازمانی'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'department_unit',
                'related_fields': {
                    'public_code': {'label': _('کد واحد'), 'data_type': 'string'},
                    'name': {'label': _('نام واحد'), 'data_type': 'string'},
                },
            },
            'created_by': {
                'field_type': 'foreign_key',
                'model': 'auth.User',
                'label': _('کاربر ایجادکننده'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'created_by',
                'related_fields': {
                    'username': {'label': _('نام کاربری'), 'data_type': 'string'},
                },
            },
        },
        'line_fields': {
            'item': {
                'field_type': 'foreign_key',
                'model': 'inventory.Item',
                'label': _('کالا'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.item',
                'aggregatable': False,
                'related_fields': {
                    'item_code': {'label': _('کد کالا'), 'data_type': 'string'},
                    'name': {'label': _('نام کالا'), 'data_type': 'string'},
                },
            },
            'warehouse': {
                'field_type': 'foreign_key',
                'model': 'inventory.Warehouse',
                'label': _('انبار مبدأ'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.warehouse',
                'aggregatable': False,
            },
            'quantity': {
                'field_type': 'number',
                'label': _('مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregatable': True,
                'aggregation_types': ['sum', 'count', 'avg', 'max', 'min'],
            },
            'consumption_type': {
                'field_type': 'string',
                'label': _('نوع مصرف'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'lines.consumption_type',
                'aggregatable': False,
            },
            'work_line': {
                'field_type': 'foreign_key',
                'model': 'production.WorkLine',
                'label': _('خط کار تولید'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.work_line',
                'aggregatable': False,
            },
        },
        'aggregated_fields': {
            'total_quantity': {
                'field_type': 'aggregated',
                'label': _('مجموع مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregation_type': 'sum',
            },
        },
    },
    
    'inventory.IssueWarehouseTransfer': {
        'header_fields': {
            'document_code': {
                'field_type': 'string',
                'label': _('کد انتقال انبار'),
                'data_type': 'string',
                'extractable': True,
                'field_path': 'document_code',
            },
            'document_date': {
                'field_type': 'date',
                'label': _('تاریخ انتقال'),
                'data_type': 'date',
                'extractable': True,
                'field_path': 'document_date',
            },
            'approver': {
                'field_type': 'foreign_key',
                'model': 'auth.User',
                'label': _('تاییدکننده'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'approver',
                'related_fields': {
                    'username': {'label': _('نام کاربری'), 'data_type': 'string'},
                },
            },
            'created_by': {
                'field_type': 'foreign_key',
                'model': 'auth.User',
                'label': _('کاربر ایجادکننده'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'created_by',
                'related_fields': {
                    'username': {'label': _('نام کاربری'), 'data_type': 'string'},
                },
            },
        },
        'line_fields': {
            'item': {
                'field_type': 'foreign_key',
                'model': 'inventory.Item',
                'label': _('کالا'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.item',
                'aggregatable': False,
                'related_fields': {
                    'item_code': {'label': _('کد کالا'), 'data_type': 'string'},
                    'name': {'label': _('نام کالا'), 'data_type': 'string'},
                },
            },
            'source_warehouse': {
                'field_type': 'foreign_key',
                'model': 'inventory.Warehouse',
                'label': _('انبار مبدأ'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.source_warehouse',
                'aggregatable': False,
                'related_fields': {
                    'public_code': {'label': _('کد انبار مبدأ'), 'data_type': 'string'},
                    'name': {'label': _('نام انبار مبدأ'), 'data_type': 'string'},
                },
            },
            'destination_warehouse': {
                'field_type': 'foreign_key',
                'model': 'inventory.Warehouse',
                'label': _('انبار مقصد'),
                'data_type': 'foreign_key',
                'extractable': True,
                'field_path': 'lines.destination_warehouse',
                'aggregatable': False,
                'related_fields': {
                    'public_code': {'label': _('کد انبار مقصد'), 'data_type': 'string'},
                    'name': {'label': _('نام انبار مقصد'), 'data_type': 'string'},
                },
            },
            'quantity': {
                'field_type': 'number',
                'label': _('مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregatable': True,
                'aggregation_types': ['sum', 'count', 'avg', 'max', 'min'],
            },
        },
        'aggregated_fields': {
            'total_quantity': {
                'field_type': 'aggregated',
                'label': _('مجموع مقدار'),
                'data_type': 'number',
                'extractable': True,
                'field_path': 'lines.quantity',
                'aggregation_type': 'sum',
            },
        },
    },
    
    # Add other document types here as needed
    # 'sales.Invoice': { ... },
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

