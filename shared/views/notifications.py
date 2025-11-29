"""
Notification views for shared module.
"""
from typing import Dict, Any
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.utils.translation import gettext_lazy as _
from shared.models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """List view for user notifications with read/unread filter."""
    model = Notification
    template_name = 'shared/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 50
    
    def get_queryset(self):
        """Filter notifications by user and read status."""
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        
        # Filter by company if active company is set
        company_id = self.request.session.get('active_company_id')
        if company_id:
            queryset = queryset.filter(company_id=company_id)
        
        # Filter by read status
        read_filter = self.request.GET.get('read', 'all')
        if read_filter == 'read':
            queryset = queryset.filter(is_read=1)
        elif read_filter == 'unread':
            queryset = queryset.filter(is_read=0)
        # 'all' shows everything
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        read_filter = self.request.GET.get('read', 'all')
        context['read_filter'] = read_filter
        
        # Get base queryset without read filter for counts
        base_queryset = super().get_queryset()
        base_queryset = base_queryset.filter(user=self.request.user)
        company_id = self.request.session.get('active_company_id')
        if company_id:
            base_queryset = base_queryset.filter(company_id=company_id)
        
        context['unread_count'] = base_queryset.filter(is_read=0).count()
        context['read_count'] = base_queryset.filter(is_read=1).count()
        return context

