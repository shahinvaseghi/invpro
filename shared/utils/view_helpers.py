"""
View helper functions for common view operations.

These functions provide reusable utilities for views across all modules.
"""
from typing import List, Dict, Any, Optional, Tuple
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def get_breadcrumbs(module_name: str, items: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
    """
    Generate breadcrumbs list with module prefix.
    
    Args:
        module_name: Module name (e.g., 'inventory', 'production')
        items: List of dicts with 'label' and 'url' keys
        
    Returns:
        List of breadcrumb dicts with 'label' and 'url' keys
        
    Example:
        breadcrumbs = get_breadcrumbs('inventory', [
            {'label': _('Item Types'), 'url': reverse('inventory:item_types')},
            {'label': _('Create'), 'url': None},
        ])
    """
    breadcrumbs = [
        {'label': _('Dashboard'), 'url': reverse('ui:dashboard')},
    ]
    
    if items:
        breadcrumbs.extend(items)
    
    return breadcrumbs


def get_success_message(action: str, model_name: str) -> str:
    """
    Generate success message for common actions.
    
    Args:
        action: Action name ('created', 'updated', 'deleted')
        model_name: Model verbose name
        
    Returns:
        Translated success message
        
    Example:
        message = get_success_message('created', 'Item Type')
        # Returns: "Item Type created successfully."
    """
    action_messages = {
        'created': _('{model} created successfully.'),
        'updated': _('{model} updated successfully.'),
        'deleted': _('{model} deleted successfully.'),
    }
    
    message_template = action_messages.get(action, _('{model} {action} successfully.'))
    return message_template.format(model=model_name, action=action)


def validate_active_company(request: HttpRequest) -> Tuple[bool, Optional[str]]:
    """
    Validate that active company exists in session.
    
    Args:
        request: Django request object
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Example:
        is_valid, error = validate_active_company(request)
        if not is_valid:
            messages.error(request, error)
            return redirect('...')
    """
    company_id = request.session.get('active_company_id')
    if not company_id:
        return False, _('Please select a company first.')
    return True, None


def get_table_headers(fields: List[Any]) -> List[Dict[str, Any]]:
    """
    Generate table headers list from field definitions.
    
    Args:
        fields: List of field names or dicts with 'label' and 'field' keys
        
    Returns:
        List of header dicts with 'label' and 'field' keys
        
    Example:
        # Simple format
        headers = get_table_headers(['name', 'code', 'is_enabled'])
        
        # Custom format
        headers = get_table_headers([
            {'label': _('Name'), 'field': 'name'},
            {'label': _('Code'), 'field': 'public_code', 'type': 'code'},
        ])
    """
    headers = []
    
    for field in fields:
        if isinstance(field, str):
            # Simple string format - use field name as label
            headers.append({
                'label': field.replace('_', ' ').title(),
                'field': field,
            })
        elif isinstance(field, dict):
            # Dict format - use as is
            headers.append(field)
        else:
            # Unknown format - skip
            continue
    
    return headers


