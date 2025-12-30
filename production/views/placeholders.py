"""
Placeholder views for production module.

These views are placeholders for future features:
- Transfer to Line Requests (درخواست انتقال به پای کار)
- Performance Records (سند عملکرد)
- Tracking and Identification (شناسایی و ردیابی)
"""
from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView
from shared.mixins import FeaturePermissionRequiredMixin

from production.models import Machine  # Temporary placeholder model


class TransferToLineRequestListView(LoginRequiredMixin, ListView):
    """
    List all transfer to line requests.
    Placeholder view - full implementation pending.
    """
    model = Machine  # Temporary placeholder model
    template_name = 'production/transfer_requests.html'
    context_object_name = 'requests'
    paginate_by = 50
    
    def get_queryset(self):
        """Return empty queryset for now."""
        return Machine.objects.none()
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and page title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['page_title'] = _('Transfer to Line Requests')
        return context


class PerformanceRecordListView(LoginRequiredMixin, ListView):
    """
    List all performance records.
    Placeholder view - full implementation pending.
    """
    model = Machine  # Temporary placeholder model
    template_name = 'production/performance_records.html'
    context_object_name = 'records'
    paginate_by = 50
    
    def get_queryset(self):
        """Return empty queryset for now."""
        return Machine.objects.none()
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and page title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['page_title'] = _('Performance Records')
        return context


class TrackingIdentificationView(FeaturePermissionRequiredMixin, TemplateView):
    """
    Tracking and identification view.
    Placeholder view - full implementation pending.
    """
    template_name = 'production/tracking_identification.html'
    feature_code = 'production.tracking_identification'
    required_action = 'view_own'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add active module and page title to context."""
        context = super().get_context_data(**kwargs)
        context['active_module'] = 'production'
        context['page_title'] = _('شناسایی و ردیابی')
        return context

