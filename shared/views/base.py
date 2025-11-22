"""
Base mixins and helper classes for shared views.
"""
from collections import defaultdict
from typing import Optional, Any, Dict, Set
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from shared.forms import UserCompanyAccessFormSet

User = get_user_model()


class UserAccessFormsetMixin:
    """Helper mixin to manage UserCompanyAccess formsets."""

    def get_access_formset(self, form: Optional[Any] = None) -> UserCompanyAccessFormSet:
        """Get or create UserCompanyAccess formset for a user."""
        instance = None
        if form is not None:
            instance = form.instance
        elif hasattr(self, 'object'):
            instance = self.object
        if instance is None:
            instance = User()
        return UserCompanyAccessFormSet(
            self.request.POST if self.request.method == 'POST' else None,
            instance=instance,
        )


class AccessLevelPermissionMixin:
    """Mixin to handle access level permissions management."""
    template_name = 'shared/access_level_form.html'

    action_labels: Dict[str, str] = {}

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize action labels."""
        super().__init__(*args, **kwargs)
        from django.utils.translation import gettext_lazy as _
        from shared.permissions import PermissionAction
        
        self.action_labels = {
            PermissionAction.VIEW_OWN.value: _('View own records'),
            PermissionAction.VIEW_ALL.value: _('View all records'),
            PermissionAction.CREATE.value: _('Create'),
            PermissionAction.EDIT_OWN.value: _('Edit own records'),
            PermissionAction.EDIT_OTHER.value: _('Edit others records'),
            PermissionAction.DELETE_OWN.value: _('Delete own records'),
            PermissionAction.DELETE_OTHER.value: _('Delete others records'),
            PermissionAction.LOCK_OWN.value: _('Lock own documents'),
            PermissionAction.LOCK_OTHER.value: _('Lock others documents'),
            PermissionAction.UNLOCK_OWN.value: _('Unlock own documents'),
            PermissionAction.UNLOCK_OTHER.value: _('Unlock others documents'),
            PermissionAction.APPROVE.value: _('Approve'),
            PermissionAction.REJECT.value: _('Reject'),
            PermissionAction.CANCEL.value: _('Cancel'),
            PermissionAction.CREATE_TRANSFER_FROM_ORDER.value: _('Create Transfer from Order'),
            PermissionAction.CREATE_RECEIPT.value: _('Create Receipt'),
        }

    def _feature_key(self, code: str) -> str:
        """Convert feature code to HTML-safe key."""
        return code.replace('.', '__')

    def _prepare_feature_context(self, instance: Optional[Any] = None) -> list:
        """Prepare feature permissions context for template."""
        from django.utils.translation import gettext_lazy as _
        from shared.permissions import FEATURE_PERMISSION_MAP, PermissionAction
        
        existing: Dict[str, Dict[str, Any]] = {}
        if instance and instance.pk:
            for perm in instance.permissions.all():
                meta_actions: Dict[str, Any] = {}
                if isinstance(perm.metadata, dict):
                    meta_actions = perm.metadata.get('actions', {})
                existing[perm.resource_code] = {
                    'view_scope': meta_actions.get(
                        'view_scope',
                        'all' if meta_actions.get(PermissionAction.VIEW_ALL.value) else (
                            'own' if meta_actions.get(PermissionAction.VIEW_OWN.value) else ('all' if perm.can_view else 'none')
                        ),
                    ),
                    'checked': {
                        action: bool(meta_actions.get(action)) for action in meta_actions
                    },
                    'fallback_can_create': bool(perm.can_create),
                    'fallback_can_edit': bool(perm.can_edit),
                    'fallback_can_delete': bool(perm.can_delete),
                    'fallback_can_approve': bool(perm.can_approve),
                }
        features: list = []
        for feature in FEATURE_PERMISSION_MAP.values():
            code: str = feature.code
            key: str = self._feature_key(code)
            feature_state: Dict[str, Any] = existing.get(code, {})
            view_scope: str = feature_state.get('view_scope', 'none')
            checked_actions: Dict[str, bool] = feature_state.get('checked', {})
            data_actions: list = []
            for action in feature.actions:
                if action in {PermissionAction.VIEW_OWN, PermissionAction.VIEW_ALL}:
                    continue
                checked: bool = checked_actions.get(action.value, False)
                if not feature_state and action == PermissionAction.CREATE:
                    checked = feature_state.get('fallback_can_create', False)
                if not feature_state and action == PermissionAction.EDIT_OWN:
                    checked = feature_state.get('fallback_can_edit', False)
                if not feature_state and action == PermissionAction.DELETE_OWN:
                    checked = feature_state.get('fallback_can_delete', False)
                if not feature_state and action == PermissionAction.APPROVE:
                    checked = feature_state.get('fallback_can_approve', False)
                data_actions.append(
                    {
                        'code': action.value,
                        'label': self.action_labels[action.value],
                        'checked': checked,
                    }
                )
            # Extract module from feature code (e.g., "production.product_orders" -> "production")
            module_code = code.split('.')[0] if '.' in code else 'shared'
            
            features.append(
                {
                    'code': code,
                    'html_id': key,
                    'label': feature.label,
                    'module_code': module_code,
                    'view_supported': PermissionAction.VIEW_OWN in feature.actions or PermissionAction.VIEW_ALL in feature.actions,
                    'view_scope': view_scope,
                    'actions': data_actions,
                }
            )
        
        # Group features by module
        grouped_features = defaultdict(list)
        for feature in features:
            grouped_features[feature['module_code']].append(feature)
        
        # Convert to list of dicts with module info
        module_list = []
        module_labels = {
            'shared': _('Shared'),
            'production': _('Production'),
            'inventory': _('Inventory'),
            'qc': _('Quality Control'),
        }
        
        for module_code, module_features in sorted(grouped_features.items()):
            module_list.append({
                'code': module_code,
                'label': module_labels.get(module_code, module_code.title()),
                'features': module_features,
            })
        
        return module_list

    def _save_permissions(self, form: Any) -> None:
        """Save permissions from form POST data."""
        from shared.permissions import FEATURE_PERMISSION_MAP, PermissionAction
        
        active_codes: Set[str] = set()
        for feature in FEATURE_PERMISSION_MAP.values():
            code: str = feature.code
            html_key: str = self._feature_key(code)
            view_scope: str = self.request.POST.get(f'perm-{html_key}-view', 'none')
            selected_actions: list = []
            for action in feature.actions:
                if action in {PermissionAction.VIEW_OWN, PermissionAction.VIEW_ALL}:
                    continue
                if self.request.POST.get(f'perm-{html_key}-{action.value}') == 'on':
                    selected_actions.append(action)

            if view_scope == 'none' and not selected_actions:
                # Remove existing permission if it exists
                self.object.permissions.filter(resource_code=code).delete()
                continue

            perm, _created = self.object.permissions.get_or_create(
                resource_code=code,
                defaults={
                    'module_code': code.split('.')[0],
                    'resource_type': 'menu',
                },
            )
            perm.module_code = code.split('.')[0]
            perm.resource_type = 'menu'
            perm.can_view = 1 if view_scope != 'none' else 0
            perm.can_create = 1 if PermissionAction.CREATE in selected_actions else 0
            perm.can_edit = 1 if PermissionAction.EDIT_OWN in selected_actions else 0
            perm.can_delete = 1 if PermissionAction.DELETE_OWN in selected_actions else 0
            perm.can_approve = 1 if PermissionAction.APPROVE in selected_actions else 0

            metadata_actions: Dict[str, Any] = {
                'view_scope': view_scope,
                PermissionAction.VIEW_OWN.value: view_scope in {'own', 'all'},
                PermissionAction.VIEW_ALL.value: view_scope == 'all',
            }
            for action in feature.actions:
                if action in {PermissionAction.VIEW_OWN, PermissionAction.VIEW_ALL}:
                    continue
                metadata_actions[action.value] = action in selected_actions
            perm.metadata = {'actions': metadata_actions}
            perm.save()
            active_codes.add(code)

        # Remove stale permissions not present anymore
        self.object.permissions.exclude(resource_code__in=active_codes).delete()

