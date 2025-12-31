"""
Trigger events configuration for automation system.
This defines when automation processes should be triggered for each document type.
"""
from django.utils.translation import gettext_lazy as _


# Configuration for trigger events for each document type
DOCUMENT_TRIGGER_EVENTS = {
    'accounting.AccountingDocument': {
        'events': [
            {
                'id': 'on_create',
                'label': _('هنگام ایجاد سند'),
                'description': _('بلافاصله پس از ایجاد سند'),
                'signal': 'post_save',
                'condition': {'created': True},
            },
            {
                'id': 'on_posted',
                'label': _('هنگام ثبت سند'),
                'description': _('وقتی سند از وضعیت DRAFT به POSTED تغییر می‌کند'),
                'signal': 'post_save',
                'condition': {'status': 'POSTED'},
            },
            {
                'id': 'on_locked',
                'label': _('هنگام قفل شدن سند'),
                'description': _('وقتی سند قفل می‌شود'),
                'signal': 'post_save',
                'condition': {'status': 'LOCKED'},
            },
        ],
        'default_event': 'on_posted',
    },
    
    'inventory.ReceiptPermanent': {
        'events': [
            {
                'id': 'on_create',
                'label': _('هنگام ایجاد رسید'),
                'description': _('بلافاصله پس از ایجاد رسید دائم'),
                'signal': 'post_save',
                'condition': {'created': True},
            },
        ],
        'default_event': 'on_create',
    },
    
    'inventory.ReceiptTemporary': {
        'events': [
            {
                'id': 'on_create',
                'label': _('هنگام ایجاد رسید موقت'),
                'description': _('بلافاصله پس از ایجاد رسید موقت'),
                'signal': 'post_save',
                'condition': {'created': True},
            },
            {
                'id': 'on_qc_approved',
                'label': _('هنگام تایید QC'),
                'description': _('وقتی رسید موقت توسط QC تایید می‌شود (status = APPROVED)'),
                'signal': 'post_save',
                'condition': {'status': 2},  # APPROVED status
            },
        ],
        'default_event': 'on_qc_approved',
    },
    
    'inventory.IssuePermanent': {
        'events': [
            {
                'id': 'on_create',
                'label': _('هنگام ایجاد حواله دائم'),
                'description': _('بلافاصله پس از ایجاد حواله دائم'),
                'signal': 'post_save',
                'condition': {'created': True},
            },
        ],
        'default_event': 'on_create',
    },
    
    'inventory.IssueConsumption': {
        'events': [
            {
                'id': 'on_create',
                'label': _('هنگام ایجاد حواله مصرف'),
                'description': _('بلافاصله پس از ایجاد حواله مصرف'),
                'signal': 'post_save',
                'condition': {'created': True},
            },
        ],
        'default_event': 'on_create',
    },
    
    'inventory.WarehouseTransfer': {
        'events': [
            {
                'id': 'on_create',
                'label': _('هنگام ایجاد انتقال انبار'),
                'description': _('بلافاصله پس از ایجاد انتقال انبار'),
                'signal': 'post_save',
                'condition': {'created': True},
            },
        ],
        'default_event': 'on_create',
    },
    
    # Add other document types as needed
    # 'sales.Invoice': { ... },
    # 'accounting.TreasuryReceive': { ... },
}


def get_trigger_events_for_document(document_model: str) -> list:
    """
    Get trigger events configuration for a specific document model.
    
    Args:
        document_model: Full model path (e.g., 'accounting.AccountingDocument')
    
    Returns:
        List of trigger event configurations
    """
    config = DOCUMENT_TRIGGER_EVENTS.get(document_model, {})
    return config.get('events', [])


def get_default_trigger_event(document_model: str) -> str:
    """
    Get default trigger event ID for a document model.
    
    Args:
        document_model: Full model path
    
    Returns:
        Default event ID or 'on_create' if not specified
    """
    config = DOCUMENT_TRIGGER_EVENTS.get(document_model, {})
    return config.get('default_event', 'on_create')

