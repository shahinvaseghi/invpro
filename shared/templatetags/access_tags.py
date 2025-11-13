"""Template helpers for access control."""

from __future__ import annotations

from django import template

from shared.utils.permissions import has_feature_permission

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
