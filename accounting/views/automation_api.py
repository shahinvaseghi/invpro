"""
API views for automation module.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _

from accounting.utils.automation_registry import get_document_by_id
from accounting.utils.document_filters import (
    get_filterable_fields_for_document,
    get_global_filter_categories,
)
from accounting.utils.document_field_groups import (
    get_field_groups_for_document,
)


@require_http_methods(["GET"])
def get_document_info(request, document_id):
    """
    API endpoint to get document information by ID.
    Returns JSON with module, document_type, and model.
    """
    doc = get_document_by_id(document_id)
    
    if not doc:
        return JsonResponse({
            'success': False,
            'error': _('Document not found'),
        }, status=404)
    
    return JsonResponse({
        'success': True,
        'module': doc['module'],
        'document_type': doc['document_type'],
        'model': doc['model'],
        'label': str(doc['label']),
    })


@require_http_methods(["GET"])
def get_filterable_fields(request, document_id):
    """
    API endpoint to get filterable fields for a document.
    Returns JSON with global filters and document-specific fields.
    """
    doc = get_document_by_id(document_id)
    
    if not doc:
        return JsonResponse({
            'success': False,
            'error': _('Document not found'),
        }, status=404)
    
    document_model = doc['model']
    
    # Get grouped fields for better UI organization
    field_groups = get_field_groups_for_document(document_model)
    
    # Also get flat fields for backward compatibility
    document_fields = get_filterable_fields_for_document(document_model)
    global_filters = get_global_filter_categories()
    
    # Convert grouped fields to serializable format
    groups_data = {}
    for group_name, group_data in field_groups.items():
        groups_data[group_name] = {
            'label': str(group_data.get('label', group_name)),
            'fields': {},
        }
        if 'fields' in group_data:
            for field_name, field_info in group_data['fields'].items():
                groups_data[group_name]['fields'][field_name] = {
                    'field_type': field_info.get('field_type'),
                    'label': str(field_info.get('label', field_name)),
                    'operators': field_info.get('operators', []),
                    'model': field_info.get('model'),
                    'ui_type': field_info.get('ui_type', 'text_input'),
                    'hierarchy_support': field_info.get('hierarchy_support', False),
                    'choices': field_info.get('choices'),
                }
    
    # Convert flat fields to serializable format (for backward compatibility)
    fields_data = {}
    for field_name, field_info in document_fields.items():
        fields_data[field_name] = {
            'field_type': field_info.get('field_type'),
            'label': str(field_info.get('label', field_name)),
            'operators': field_info.get('operators', []),
            'model': field_info.get('model'),
            'hierarchy_support': field_info.get('hierarchy_support', False),
        }
    
    global_data = {}
    for cat_name, cat_info in global_filters.items():
        global_data[cat_name] = {
            'label': str(cat_info.get('label', cat_name)),
            'field_type': cat_info.get('field_type'),
            'operators': cat_info.get('operators', []),
            'model': cat_info.get('model'),
        }
    
    return JsonResponse({
        'success': True,
        'field_groups': groups_data,  # New grouped structure
        'document_fields': fields_data,  # Flat structure for backward compatibility
        'global_filters': global_data,
    })

