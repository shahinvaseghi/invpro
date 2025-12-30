"""Utility helpers for resolving user feature permissions."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping, Optional, Set

from django.contrib.auth import get_user_model
from django.db.models import Prefetch

from shared.models import AccessLevel, AccessLevelPermission, GroupProfile, UserCompanyAccess
from shared.permissions import FEATURE_PERMISSION_MAP


User = get_user_model()


@dataclass(frozen=True)
class FeaturePermissionState:
    """Represents the resolved permissions for a single feature."""

    view_scope: str
    can_view: bool
    actions: Mapping[str, bool]


def _feature_key(code: str) -> str:
    """Normalize feature code for template-friendly lookups."""

    return code.replace(".", "__")


def _collect_access_level_ids_for_user(user: User, company_id: Optional[int]) -> Set[int]:
    """Return all active access level IDs applicable to the user."""

    if not user.is_authenticated:
        return set()

    level_ids: Set[int] = set()

    # Company-scoped access levels
    if company_id is not None:
        company_accesses = (
            UserCompanyAccess.objects.filter(
                user=user,
                company_id=company_id,
                is_enabled=1,
            )
            .select_related("access_level")
        )
        for access in company_accesses:
            if access.access_level and access.access_level.is_enabled == 1:
                level_ids.add(access.access_level_id)

    # Group-derived access levels (mostly for global roles)
    user_groups = list(user.groups.all())
    if user_groups:
        group_profiles = (
            GroupProfile.objects.filter(group__in=user_groups, is_enabled=1)
            .prefetch_related(
                Prefetch(
                    "access_levels",
                    queryset=AccessLevel.objects.filter(is_enabled=1),
                )
            )
        )
        for profile in group_profiles:
            for level in profile.access_levels.all():
                if level.is_global == 1:
                    level_ids.add(level.id)

    return level_ids


def _resolve_feature_permissions(access_level_ids: Iterable[int]) -> Dict[str, FeaturePermissionState]:
    """Build a consolidated feature-permission mapping for given AccessLevels."""

    def _default_payload():
        return {
            "view_scope": "none",
            "can_view": False,
            "actions": defaultdict(bool),
        }

    feature_matrix: Dict[str, Dict[str, object]] = defaultdict(_default_payload)

    if not access_level_ids:
        return {}

    permissions = (
        AccessLevelPermission.objects.filter(access_level_id__in=set(access_level_ids))
        .select_related("access_level")
    )

    for perm in permissions:
        code = perm.resource_code
        data = feature_matrix[code]
        meta_actions = {}
        if isinstance(perm.metadata, dict):
            meta_actions = perm.metadata.get("actions", {}) or {}

        view_scope = meta_actions.get("view_scope")
        if not view_scope:
            # Fallback when metadata not populated (legacy records)
            if perm.can_view:
                view_scope = "all"
            else:
                view_scope = "none"

        # Promote scope priority: none < own < all
        current_scope = data["view_scope"]
        scope_rank = {"none": 0, "own": 1, "all": 2}
        if scope_rank.get(view_scope, 0) > scope_rank.get(current_scope, 0):
            data["view_scope"] = view_scope

        if view_scope != "none":
            data["can_view"] = True

        # Actions from metadata
        for action_code, enabled in meta_actions.items():
            if action_code in {"view_scope", "view_own", "view_all"}:
                continue
            if enabled:
                data["actions"][action_code] = True

        # Fallback to legacy boolean fields when metadata lacked certain entries
        legacy_action_map = {
            "create": perm.can_create,
            "edit_own": perm.can_edit,
            "delete_own": perm.can_delete,
            "approve": perm.can_approve,
        }
        for action_code, enabled in legacy_action_map.items():
            if enabled:
                data["actions"][action_code] = True

    # Ensure every known feature has an entry
    for feature in FEATURE_PERMISSION_MAP.values():
        feature_matrix.setdefault(feature.code, _default_payload())

    # Freeze structure with dataclass for clarity
    resolved: Dict[str, FeaturePermissionState] = {}
    for code, payload in feature_matrix.items():
        actions = dict(payload["actions"])
        resolved[_feature_key(code)] = FeaturePermissionState(
            view_scope=payload["view_scope"],
            can_view=payload["can_view"],
            actions=actions,
        )

    return resolved


def get_user_feature_permissions(user: User, company_id: Optional[int]) -> Dict[str, FeaturePermissionState]:
    """Public helper to resolve feature permissions for templates and views."""

    if not user.is_authenticated:
        return {}

    if user.is_superuser:
        # Superusers bypass checks – grant wildcard permissions for templates
        return {
            "__superuser__": FeaturePermissionState(
                view_scope="all",
                can_view=True,
                actions={"all": True},
            )
        }

    level_ids = _collect_access_level_ids_for_user(user, company_id)
    return _resolve_feature_permissions(level_ids)


def are_users_in_same_primary_group(user1: User, user2: User) -> bool:
    """
    Check if two users share at least one primary group.
    
    Args:
        user1: First user
        user2: Second user
        
    Returns:
        True if users share at least one primary group, False otherwise
    """
    if not user1 or not user2:
        return False
    
    # Get primary groups for both users
    user1_groups = set(user1.primary_groups.all().values_list('id', flat=True))
    user2_groups = set(user2.primary_groups.all().values_list('id', flat=True))
    
    # Check if there's any intersection
    return bool(user1_groups & user2_groups)


def has_feature_permission(
    permissions: Mapping[str, FeaturePermissionState],
    feature_code: str,
    action: str = "view",
    allow_own_scope: bool = True,
    current_user: Optional[User] = None,
    resource_owner: Optional[User] = None,
) -> bool:
    """
    Utility for validating a particular feature/action combination.
    
    Args:
        permissions: Resolved permissions mapping
        feature_code: Feature code to check
        action: Action to check (e.g., 'view_own', 'view_same_group')
        allow_own_scope: Whether to allow own scope fallback
        current_user: Current user (required for same_group checks)
        resource_owner: Owner of the resource (required for same_group checks)
    """

    if "__superuser__" in permissions:
        return True

    key = _feature_key(feature_code)
    state = permissions.get(key)
    if not state:
        return False

    if action == "view":
        if state.can_view:
            return True
        return False

    if action == "view_all":
        return state.view_scope == "all"

    if action == "view_own":
        return state.view_scope in {"own", "all"}
    
    # Check same_group actions
    if action in {"view_same_group", "edit_same_group", "delete_same_group", "lock_same_group", "unlock_same_group"}:
        # Check if user has the same_group permission
        action_value = state.actions.get(action)
        if not action_value:
            return False
        
        # If permission exists, check if users are in same primary group
        if current_user and resource_owner:
            if are_users_in_same_primary_group(current_user, resource_owner):
                return True
        
        return False

    action_value = state.actions.get(action)
    if action_value:
        return True

    # Some actions (like edit/delete) may rely on own scope
    if allow_own_scope and action in {"edit_own", "delete_own", "lock_own", "unlock_own"}:
        return state.view_scope in {"own", "all"}

    return False
