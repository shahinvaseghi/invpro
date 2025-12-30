"""
Template tags for view-related operations.

These tags provide utilities for breadcrumbs, table headers, permissions, and actions.
"""
from django import template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from typing import List, Dict, Any, Optional

register = template.Library()


@register.simple_tag
def get_breadcrumbs(module_name: str, items: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
    """
    Generate breadcrumbs list with module prefix.
    
    Usage:
        {% get_breadcrumbs 'inventory' breadcrumb_items as breadcrumbs %}
        {% for crumb in breadcrumbs %}
            <a href="{{ crumb.url }}">{{ crumb.label }}</a>
        {% endfor %}
    
    Args:
        module_name: Module name (e.g., 'inventory', 'production')
        items: List of dicts with 'label' and 'url' keys
        
    Returns:
        List of breadcrumb dicts with 'label' and 'url' keys
    """
    from shared.utils.view_helpers import get_breadcrumbs as get_breadcrumbs_helper
    return get_breadcrumbs_helper(module_name, items)


@register.simple_tag
def get_table_headers(fields: List[Any]) -> List[Dict[str, Any]]:
    """
    Generate table headers list from field definitions.
    
    Usage:
        {% get_table_headers table_fields as headers %}
        {% for header in headers %}
            <th>{{ header.label }}</th>
        {% endfor %}
    
    Args:
        fields: List of field names or dicts with 'label' and 'field' keys
        
    Returns:
        List of header dicts with 'label' and 'field' keys
    """
    from shared.utils.view_helpers import get_table_headers as get_table_headers_helper
    return get_table_headers_helper(fields)


@register.simple_tag(takes_context=True)
def can_action(context, object, action: str, feature_code: str = '') -> bool:
    """
    Check if user can perform action on object.
    
    Usage:
        {% can_action object 'edit' feature_code as can_edit %}
        {% if can_edit %}
            <a href="...">Edit</a>
        {% endif %}
    
    Args:
        object: Model instance
        action: Action name ('view', 'edit', 'delete', etc.)
        feature_code: Feature code for permission check
        
    Returns:
        Boolean indicating if action is allowed
    """
    request = context.get('request')
    if not request or not request.user:
        return False
    
    user = request.user
    
    # Superuser can do everything
    if user.is_superuser:
        return True
    
    # Check if object has get_available_actions method
    if hasattr(object, 'get_available_actions'):
        available_actions = object.get_available_actions(request.user)
        return action in available_actions
    
    # Use feature permission system if feature_code is provided
    if feature_code:
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        
        # Get user permissions
        company_id = request.session.get('active_company_id')
        permissions = get_user_feature_permissions(user, company_id)
        
        # Map action names to permission actions
        action_map = {
            'view': 'view_own',
            'edit': 'edit_own',
            'delete': 'delete_own',
            'add': 'create',
        }
        
        permission_action = action_map.get(action.lower())
        if permission_action:
            # Get resource owner if available
            resource_owner = None
            if hasattr(object, 'created_by'):
                resource_owner = object.created_by
            elif hasattr(object, 'owner'):
                resource_owner = object.owner
            elif hasattr(object, 'user'):
                resource_owner = object.user
            
            return has_feature_permission(
                permissions,
                feature_code,
                permission_action,
                allow_own_scope=True,
                current_user=user,
                resource_owner=resource_owner,
            )
    
    # Fallback: check Django permissions
    if hasattr(object, '_meta'):
        app_label = object._meta.app_label
        model_name = object._meta.model_name
        
        permission_map = {
            'view': f'{app_label}.view_{model_name}',
            'edit': f'{app_label}.change_{model_name}',
            'delete': f'{app_label}.delete_{model_name}',
            'add': f'{app_label}.add_{model_name}',
        }
        
        permission = permission_map.get(action.lower())
        if permission:
            return user.has_perm(permission)
    
    return False


@register.simple_tag(takes_context=True)
def get_object_actions(context, object, feature_code: str = '') -> List[Dict[str, Any]]:
    """
    Get available actions for object.
    
    Usage:
        {% get_object_actions object feature_code as actions %}
        {% for action in actions %}
            <a href="{{ action.url }}">{{ action.label }}</a>
        {% endfor %}
    
    Args:
        object: Model instance
        feature_code: Feature code for permission check
        
    Returns:
        List of action dicts with 'name', 'label', 'url', 'class' keys
    """
    request = context.get('request')
    if not request or not request.user:
        return []
    
    user = request.user
    actions = []
    
    # Check if object has get_available_actions method
    if hasattr(object, 'get_available_actions'):
        available_action_names = object.get_available_actions(request.user)
        
        # Build action URLs
        action_urls = {
            'view': ('detail', 'view'),
            'edit': ('update', 'change', 'edit'),
            'delete': ('delete', 'remove'),
        }
        
        for action_name in available_action_names:
            action_info = {
                'name': action_name,
                'label': action_name.title(),
                'url': None,
                'class': f'btn-action-{action_name}',
            }
            
            # Try to find URL name
            if hasattr(object, '_meta'):
                app_label = object._meta.app_label
                model_name = object._meta.model_name
                
                # Try common URL patterns
                url_patterns = [
                    f'{app_label}:{model_name}_{action_name}',
                    f'{app_label}:{action_name}_{model_name}',
                    f'{app_label}:{model_name}-{action_name}',
                ]
                
                for url_name in url_patterns:
                    try:
                        action_info['url'] = reverse(url_name, args=[object.pk])
                        break
                    except:
                        continue
            
            actions.append(action_info)
        
        return actions
    
    # Default actions based on permissions
    default_actions = [
        ('view', _('View'), 'detail', 'view'),
        ('edit', _('Edit'), 'update', 'change'),
        ('delete', _('Delete'), 'delete', 'delete'),
    ]
    
    for action_name, label, url_suffix, perm_suffix in default_actions:
        # Check permission
        can_do = can_action(context, object, action_name, feature_code)
        if not can_do:
            continue
        
        # Build URL
        url = None
        if hasattr(object, '_meta'):
            app_label = object._meta.app_label
            model_name = object._meta.model_name
            
            url_patterns = [
                f'{app_label}:{model_name}_{url_suffix}',
                f'{app_label}:{url_suffix}_{model_name}',
                f'{app_label}:{model_name}-{url_suffix}',
            ]
            
            for url_name in url_patterns:
                try:
                    url = reverse(url_name, args=[object.pk])
                    break
                except:
                    continue
        
        if url:
            actions.append({
                'name': action_name,
                'label': str(label),
                'url': url,
                'class': f'btn-action-{action_name}',
            })
    
    return actions


@register.filter
def get_item(dictionary: Dict, key: str) -> Any:
    """
    Get item from dictionary by key.
    
    Usage:
        {{ stats_labels|get_item:'total' }}
    
    Args:
        dictionary: Dictionary to get item from
        key: Key to look up
        
    Returns:
        Value from dictionary or None
    """
    if not isinstance(dictionary, dict):
        return None
    return dictionary.get(key)

