"""
Base views and mixins for accounting module.
"""
from typing import Optional, Dict, Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View


class AccountingBaseView(LoginRequiredMixin):
    """Base view with common context for accounting module."""
    login_url = '/admin/login/'
    
    def get_queryset(self):
        """Filter queryset by active company."""
        queryset = super().get_queryset()
        company_id = self.request.session.get('active_company_id')
        if company_id and (hasattr(queryset.model, 'company') or hasattr(queryset.model, 'company_id')):
            queryset = queryset.filter(company_id=company_id)
        return queryset
    
    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add common context data."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'accounting'
        return context
    
    def filter_queryset_by_permissions(self, queryset, feature_code: str, owner_field: str = 'created_by'):
        """
        Filter queryset based on user permissions.
        
        Args:
            queryset: The queryset to filter
            feature_code: Feature code for permission checking (e.g., 'accounting.fiscal_years')
            owner_field: Field name that contains the owner/creator (default: 'created_by')
        
        Returns:
            Filtered queryset
        """
        # Superuser can see all records
        if self.request.user.is_superuser:
            return queryset
        
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        
        # Check view scope
        can_view_all = has_feature_permission(permissions, feature_code, 'view_all', allow_own_scope=False)
        can_view_own = has_feature_permission(permissions, feature_code, 'view_own', allow_own_scope=True)
        
        # If user can view all, return queryset as is
        if can_view_all:
            return queryset
        
        # If user can only view own records, filter by owner
        if can_view_own:
            # Check if model has the owner field
            if hasattr(queryset.model, owner_field):
                return queryset.filter(**{owner_field: self.request.user})
        
        # If user has no view permission, return empty queryset
        return queryset.none()

