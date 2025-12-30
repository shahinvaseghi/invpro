"""Template helpers for access control."""

from __future__ import annotations

from django import template

from shared.utils.permissions import (
    get_user_feature_permissions,
    has_feature_permission,
    are_users_in_same_primary_group,
)

register = template.Library()


@register.filter
def feature_allowed(user_permissions, args: str) -> bool:
    """Filter usage: {{ user_feature_permissions|feature_allowed:"feature_code[:action]" }}."""

    if not user_permissions:
        return False

    if not args:
        return False

    if ':' in args:
        feature_code, action = args.split(':', 1)
    else:
        feature_code, action = args, 'view'

    return has_feature_permission(user_permissions, feature_code, action=action)


@register.simple_tag(takes_context=True)
def can_view_object(context, obj, feature_code: str = "") -> bool:
    """
    Check if current user can view a specific object.
    
    Usage:
        {% can_view_object object "inventory.receipts.temporary" as can_view %}
        {% if can_view %}...{% endif %}
    """
    request = context.get('request')
    if not request or not request.user:
        return False
    
    if request.user.is_superuser:
        return True
    
    # If no feature_code provided, allow view (backward compatibility)
    if not feature_code:
        return True
    
    company_id = request.session.get('active_company_id')
    permissions = get_user_feature_permissions(request.user, company_id)
    
    # Get resource owner
    resource_owner = None
    if hasattr(obj, 'created_by'):
        resource_owner = obj.created_by
    elif hasattr(obj, 'owner'):
        resource_owner = obj.owner
    elif hasattr(obj, 'user'):
        resource_owner = obj.user
    
    # Check view permissions
    can_view_all = has_feature_permission(
        permissions, feature_code, 'view_all', allow_own_scope=False,
        current_user=request.user, resource_owner=resource_owner
    )
    if can_view_all:
        return True
    
    # Check if user is owner
    is_owner = resource_owner == request.user if resource_owner else False
    if is_owner:
        can_view_own = has_feature_permission(
            permissions, feature_code, 'view_own', allow_own_scope=True,
            current_user=request.user, resource_owner=resource_owner
        )
        if can_view_own:
            return True
    
    # Check same group permission
    if resource_owner:
        can_view_same_group = has_feature_permission(
            permissions, feature_code, 'view_same_group', allow_own_scope=False,
            current_user=request.user, resource_owner=resource_owner
        )
        if can_view_same_group and are_users_in_same_primary_group(request.user, resource_owner):
            return True
    
    return False


@register.simple_tag(takes_context=True)
def can_edit_object(context, obj, feature_code: str = "") -> bool:
    """
    Check if current user can edit a specific object.
    Also checks if object is locked.
    
    Usage:
        {% can_edit_object object "inventory.receipts.temporary" as can_edit %}
        {% if can_edit %}...{% endif %}
    """
    # Check if object is locked
    if getattr(obj, 'is_locked', 0):
        return False
    
    request = context.get('request')
    if not request or not request.user:
        return False
    
    if request.user.is_superuser:
        return True
    
    # If no feature_code provided, allow edit (backward compatibility)
    if not feature_code:
        return True
    
    company_id = request.session.get('active_company_id')
    permissions = get_user_feature_permissions(request.user, company_id)
    
    # Get resource owner
    resource_owner = None
    if hasattr(obj, 'created_by'):
        resource_owner = obj.created_by
    elif hasattr(obj, 'owner'):
        resource_owner = obj.owner
    elif hasattr(obj, 'user'):
        resource_owner = obj.user
    
    # Check edit permissions
    can_edit_other = has_feature_permission(
        permissions, feature_code, 'edit_other', allow_own_scope=False,
        current_user=request.user, resource_owner=resource_owner
    )
    if can_edit_other:
        return True
    
    # Check if user is owner
    is_owner = resource_owner == request.user if resource_owner else False
    if is_owner:
        can_edit_own = has_feature_permission(
            permissions, feature_code, 'edit_own', allow_own_scope=True,
            current_user=request.user, resource_owner=resource_owner
        )
        if can_edit_own:
            return True
    
    # Check same group permission
    if resource_owner:
        can_edit_same_group = has_feature_permission(
            permissions, feature_code, 'edit_same_group', allow_own_scope=False,
            current_user=request.user, resource_owner=resource_owner
        )
        if can_edit_same_group and are_users_in_same_primary_group(request.user, resource_owner):
            return True
    
    return False
