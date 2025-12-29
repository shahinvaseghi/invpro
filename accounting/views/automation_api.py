"""
API views for automation module.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _

from django.db.models import Q
from accounting.utils.automation_registry import get_document_by_id
from accounting.utils.document_filters import (
    get_filterable_fields_for_document,
    get_global_filter_categories,
)
from accounting.utils.document_field_groups import (
    get_field_groups_for_document,
)
from accounting.models import Account


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


@require_http_methods(["GET"])
def get_autocomplete_options(request, model_name):
    """
    API endpoint to get autocomplete options for foreign key fields.
    Supports: Account (SanadKol, Moin), TafsiliAccount
    """
    company_id = request.session.get('active_company_id')
    search_query = request.GET.get('q', '').strip()
    
    if not company_id:
        return JsonResponse({
            'success': False,
            'error': _('Company not selected'),
        }, status=400)
    
    results = []
    
    if model_name == 'accounting.Account':
        # Filter by account_level: 1=SanadKol, 2=Moin
        account_level = request.GET.get('account_level')
        queryset = Account.objects.filter(company_id=company_id, is_enabled=1)
        
        if account_level:
            try:
                level = int(account_level)
                queryset = queryset.filter(account_level=level)
            except ValueError:
                pass
        
        if search_query:
            queryset = queryset.filter(
                Q(account_name__icontains=search_query) |
                Q(account_code__icontains=search_query) |
                Q(account_name_en__icontains=search_query)
            )
        
        queryset = queryset.order_by('account_code')[:50]
        
        for account in queryset:
            results.append({
                'id': account.id,
                'text': f"{account.account_code} - {account.account_name}",
                'code': account.account_code,
                'name': account.account_name,
                'level': account.account_level,
            })
    
    elif model_name == 'accounting.TafsiliAccount' or model_name == 'accounting.Account':
        # Tafsili accounts are Account with account_level=3
        # But if account_level is provided, use it
        account_level = request.GET.get('account_level')
        queryset = Account.objects.filter(
            company_id=company_id,
            is_enabled=1,
        )
        
        # If account_level is provided, filter by it
        # Otherwise, if model is TafsiliAccount, default to level 3
        if account_level:
            try:
                level = int(account_level)
                queryset = queryset.filter(account_level=level)
            except ValueError:
                pass
        elif model_name == 'accounting.TafsiliAccount':
            queryset = queryset.filter(account_level=3)
        
        if search_query:
            queryset = queryset.filter(
                Q(account_name__icontains=search_query) |
                Q(account_code__icontains=search_query) |
                Q(account_name_en__icontains=search_query)
            )
        
        queryset = queryset.order_by('account_code')[:50]
        
        for account in queryset:
            results.append({
                'id': account.id,
                'text': f"{account.account_code} - {account.account_name}",
                'code': account.account_code,
                'name': account.account_name,
                'level': account.account_level,
            })
    
    else:
        return JsonResponse({
            'success': False,
            'error': _('Unsupported model'),
        }, status=400)
    
    return JsonResponse({
        'success': True,
        'results': results,
    })

