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
        
        from shared.utils.permissions import get_user_feature_permissions, has_feature_permission, are_users_in_same_primary_group
        from django.db.models import Q
        company_id = self.request.session.get('active_company_id')
        permissions = get_user_feature_permissions(self.request.user, company_id)
        
        # Check view scope
        can_view_all = has_feature_permission(permissions, feature_code, 'view_all', allow_own_scope=False)
        can_view_own = has_feature_permission(permissions, feature_code, 'view_own', allow_own_scope=True)
        can_view_same_group = has_feature_permission(permissions, feature_code, 'view_same_group', allow_own_scope=False)
        
        # If user can view all, return queryset as is
        if can_view_all:
            return queryset
        
        # Build filter conditions
        filter_conditions = Q()
        
        # If user can view own records, add own records to filter
        if can_view_own:
            if hasattr(queryset.model, owner_field):
                filter_conditions |= Q(**{owner_field: self.request.user})
        
        # If user can view same group records, add same group records to filter
        if can_view_same_group:
            if hasattr(queryset.model, owner_field):
                # Get current user's primary groups
                current_user_primary_groups = set(self.request.user.primary_groups.all().values_list('id', flat=True))
                
                if current_user_primary_groups:
                    # Get users who share at least one primary group with current user
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    same_group_users = User.objects.filter(
                        primary_groups__id__in=current_user_primary_groups
                    ).distinct()
                    
                    # Add same group records to filter
                    filter_conditions |= Q(**{f'{owner_field}__in': same_group_users})
        
        # If no permissions, return empty queryset
        if not filter_conditions:
            return queryset.none()
        
        # Apply filter
        return queryset.filter(filter_conditions).distinct()

