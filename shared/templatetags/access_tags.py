"""Template tags for access control helpers."""

from __future__ import annotations

from django import template

from shared.utils.permissions import has_feature_permission

register = template.Library()


@register.simple_tag
def feature_allowed(user_permissions, feature_code: str, action: str = "view") -> bool:
    """Return True when the feature/action is permitted for the current user."""

    if not user_permissions:
        return False
    return has_feature_permission(user_permissions, feature_code, action=action)
