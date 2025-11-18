"""Mixins shared across applications."""

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from shared.utils.permissions import (
    FeaturePermissionState,
    get_user_feature_permissions,
    has_feature_permission,
)


class FeaturePermissionRequiredMixin(LoginRequiredMixin):
    """Mixin that validates feature-level access before dispatching a view."""

    feature_code: str | None = None
    required_action: str = "view"
    allow_superuser: bool = True
    allow_own_scope: bool = True

    def get_feature_code(self) -> str | None:
        return self.feature_code

    def get_required_action(self) -> str:
        return self.required_action

    def _resolve_permissions(self) -> dict[str, FeaturePermissionState]:
        request = self.request
        company_id = request.session.get("active_company_id")
        return get_user_feature_permissions(request.user, company_id)

    def has_feature_permission(self) -> bool:
        feature_code = self.get_feature_code()
        if not feature_code:
            # Nothing to validate
            return True

        if self.allow_superuser and self.request.user.is_superuser:
            return True

        permissions = self._resolve_permissions()
        return has_feature_permission(
            permissions,
            feature_code,
            action=self.get_required_action(),
            allow_own_scope=self.allow_own_scope,
        )

    def dispatch(self, request, *args, **kwargs):
        if not self.has_feature_permission():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
