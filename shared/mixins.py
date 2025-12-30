"""Mixins shared across applications."""

from __future__ import annotations

from typing import Optional
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet, Q
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

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

    def get_resource_owner(self):
        """
        Get the owner of the resource being accessed.
        Override this method in views that have an object with a created_by or owner field.
        """
        if hasattr(self, 'object') and self.object:
            # Try common owner field names
            if hasattr(self.object, 'created_by'):
                return self.object.created_by
            if hasattr(self.object, 'owner'):
                return self.object.owner
            if hasattr(self.object, 'user'):
                return self.object.user
        return None

    def has_feature_permission(self) -> bool:
        feature_code = self.get_feature_code()
        if not feature_code:
            # Nothing to validate
            return True

        if self.allow_superuser and self.request.user.is_superuser:
            return True

        permissions = self._resolve_permissions()
        resource_owner = self.get_resource_owner()
        
        return has_feature_permission(
            permissions,
            feature_code,
            action=self.get_required_action(),
            allow_own_scope=self.allow_own_scope,
            current_user=self.request.user,
            resource_owner=resource_owner,
        )

    def dispatch(self, request, *args, **kwargs):
        if not self.has_feature_permission():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class PermissionFilterMixin:
    """
    Mixin for filtering queryset by permissions.
    
    This mixin provides a method to filter queryset based on user permissions
    (view_all, view_own, view_same_group).
    
    Usage:
        class MyListView(PermissionFilterMixin, ListView):
            feature_code = 'inventory.items'
            permission_field = 'created_by'
            
            def get_queryset(self):
                queryset = super().get_queryset()
                return self.filter_queryset_by_permissions(
                    queryset,
                    self.feature_code,
                    self.permission_field
                )
    """
    
    def filter_queryset_by_permissions(
        self,
        queryset: QuerySet,
        feature_code: str,
        owner_field: str = 'created_by'
    ) -> QuerySet:
        """
        Filter queryset based on user permissions.
        
        Args:
            queryset: Django queryset to filter
            feature_code: Feature code for permission check
            owner_field: Field name that identifies the owner (default: 'created_by')
            
        Returns:
            Filtered queryset
        """
        if self.request.user.is_superuser:
            return queryset
        
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return queryset.none()
        
        permissions = get_user_feature_permissions(self.request.user, company_id)
        
        # Check if user has view_all permission
        if has_feature_permission(
            permissions,
            feature_code,
            action='view_all',
            current_user=self.request.user,
        ):
            return queryset
        
        # Check if user has view_own permission
        if has_feature_permission(
            permissions,
            feature_code,
            action='view_own',
            current_user=self.request.user,
        ):
            return queryset.filter(**{owner_field: self.request.user})
        
        # Check if user has view_same_group permission
        if has_feature_permission(
            permissions,
            feature_code,
            action='view_same_group',
            current_user=self.request.user,
        ):
            # Get user's groups
            user_groups = self.request.user.groups.all()
            if user_groups:
                # Filter by objects created by users in same groups
                from django.contrib.auth import get_user_model
                User = get_user_model()
                users_in_groups = User.objects.filter(groups__in=user_groups).distinct()
                return queryset.filter(**{f"{owner_field}__in": users_in_groups})
        
        # No permission - return empty queryset
        return queryset.none()


class CompanyScopedViewMixin:
    """
    Mixin for views that filter by active company.
    
    This mixin automatically filters queryset by active_company_id and
    adds active_module to context.
    
    Usage:
        class MyListView(CompanyScopedViewMixin, ListView):
            active_module = 'inventory'
    """
    
    active_module: Optional[str] = None
    
    def get_queryset(self):
        """Filter queryset by active company."""
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        
        if company_id and hasattr(queryset.model, 'company_id'):
            queryset = queryset.filter(company_id=company_id)
        elif company_id and hasattr(queryset.model, 'company'):
            queryset = queryset.filter(company_id=company_id)
        elif company_id is None and hasattr(queryset.model, 'company_id'):
            # No company selected and model requires company
            return queryset.none()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add active_module to context."""
        context = super().get_context_data(**kwargs)
        if self.active_module:
            context['active_module'] = self.active_module
        return context


class AutoSetFieldsMixin:
    """
    Mixin for automatically setting company_id, created_by, and edited_by fields.
    
    This mixin automatically sets these fields in form_valid() method.
    
    Usage:
        class MyCreateView(AutoSetFieldsMixin, CreateView):
            auto_set_company = True
            auto_set_created_by = True
    """
    
    auto_set_company: bool = True
    auto_set_created_by: bool = True
    auto_set_edited_by: bool = True
    require_active_company: bool = True
    
    def form_valid(self, form):
        """Set company_id, created_by, and edited_by before saving."""
        # Validate active company if required
        if self.require_active_company:
            company_id = self.request.session.get('active_company_id')
            if not company_id:
                messages.error(
                    self.request,
                    _('Please select a company first.')
                )
                return self.form_invalid(form)
        
        # Set company_id
        if self.auto_set_company:
            company_id = self.request.session.get('active_company_id')
            if company_id and hasattr(form.instance, 'company_id'):
                form.instance.company_id = company_id
            elif company_id and hasattr(form.instance, 'company'):
                form.instance.company_id = company_id
        
        # Set created_by (for CreateView)
        if self.auto_set_created_by and hasattr(form.instance, 'created_by'):
            if not form.instance.pk:  # Only for new objects
                form.instance.created_by = self.request.user
        
        # Set edited_by (for UpdateView)
        if self.auto_set_edited_by and hasattr(form.instance, 'edited_by'):
            if form.instance.pk:  # Only for existing objects
                form.instance.edited_by = self.request.user
        
        return super().form_valid(form)


class SuccessMessageMixin:
    """
    Mixin for displaying success messages.
    
    This mixin automatically displays success messages after form submission
    or deletion.
    
    Usage:
        class MyCreateView(SuccessMessageMixin, CreateView):
            success_message = _('Item created successfully.')
    """
    
    success_message: Optional[str] = None
    
    def form_valid(self, form):
        """Display success message after form submission."""
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response
    
    def delete(self, request, *args, **kwargs):
        """Display success message after deletion."""
        response = super().delete(request, *args, **kwargs)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response
