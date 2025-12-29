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
    document_fields = get_filterable_fields_for_document(document_model)
    global_filters = get_global_filter_categories()
    
    # Convert to serializable format
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
        'document_fields': fields_data,
        'global_filters': global_data,
    })

