"""
QC Operations views for production module.
Handles QC approval/rejection for operations that require QC inspection.
"""
from typing import Any, Dict, Optional
from django.contrib import messages
from django.db.models import Q, Exists, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView
from django.views import View

from shared.mixins import FeaturePermissionRequiredMixin
from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
from production.models import (
    OperationQCStatus,
    ProductOrder,
    ProcessOperation,
    PerformanceRecord,
)


class QCOperationsListView(FeaturePermissionRequiredMixin, ListView):
    """
    List operations that require QC and have performance documents.
    Only shows operations where:
    - requires_qc = 1
    - Performance record exists for the operation
    """
    model = OperationQCStatus
    template_name = 'production/qc_operations_list.html'
    context_object_name = 'qc_operations'
    paginate_by = 50
    feature_code = 'production.qc_operations'
    required_action = 'view_own'
    
    def get_queryset(self):
        """Filter QC operations by active company."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            return OperationQCStatus.objects.none()
        
        # Get all operations that require QC and have performance documents
        # Show only pending QC operations (or all if needed for review)
        queryset = OperationQCStatus.objects.filter(
            company_id=active_company_id,
            operation__requires_qc=1,
            performance__isnull=False,
        ).select_related(
            'order',
            'order__finished_item',
            'operation',
            'operation__process',
            'performance',
            'qc_approved_by',
        ).order_by(
            'qc_status',  # PENDING first, then APPROVED, then REJECTED
            '-qc_status_date',
            '-created_at',
            'order',
            'operation'
        )
        
        # Check if user has view_all permission
        permissions = get_user_feature_permissions(self.request.user, active_company_id)
        if not has_feature_permission(permissions, 'production.qc_operations', action='view_all'):
            # Only show operations from orders created by user (if needed)
            # For now, show all pending operations that need QC review
            pass
        
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['page_title'] = _('QC Operations')
        context['breadcrumbs'] = [
            {'label': _('Production'), 'url': None},
            {'label': _('QC Operations'), 'url': None},
        ]
        
        # Add permission checks for approve/reject actions
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        if active_company_id:
            permissions = get_user_feature_permissions(self.request.user, active_company_id)
            context['can_approve'] = has_feature_permission(
                permissions, 'production.qc_operations', action='approve'
            ) or self.request.user.is_superuser
            context['can_reject'] = has_feature_permission(
                permissions, 'production.qc_operations', action='reject'
            ) or self.request.user.is_superuser
        
        return context


class QCOperationApproveView(FeaturePermissionRequiredMixin, View):
    """Approve QC for an operation."""
    feature_code = 'production.qc_operations'
    required_action = 'approve'
    
    def post(self, request, pk: int):
        """Approve QC for the operation."""
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            return JsonResponse({'error': _('No active company selected.')}, status=400)
        
        qc_status = get_object_or_404(
            OperationQCStatus,
            pk=pk,
            company_id=active_company_id
        )
        
        # Check if already approved or rejected
        if qc_status.qc_status == OperationQCStatus.QCStatus.APPROVED:
            return JsonResponse({
                'error': _('This operation has already been approved by QC.')
            }, status=400)
        
        if qc_status.qc_status == OperationQCStatus.QCStatus.REJECTED:
            return JsonResponse({
                'error': _('This operation has already been rejected by QC.')
            }, status=400)
        
        # Approve the operation
        qc_status.qc_status = OperationQCStatus.QCStatus.APPROVED
        qc_status.qc_approved_by = request.user
        qc_status.qc_status_date = timezone.now()
        qc_status.save()
        
        messages.success(request, _('Operation approved by QC successfully.'))
        return JsonResponse({
            'success': True,
            'message': _('Operation approved by QC successfully.')
        })


class QCOperationRejectView(FeaturePermissionRequiredMixin, View):
    """Reject QC for an operation."""
    feature_code = 'production.qc_operations'
    required_action = 'reject'
    
    def post(self, request, pk: int):
        """Reject QC for the operation."""
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            return JsonResponse({'error': _('No active company selected.')}, status=400)
        
        qc_status = get_object_or_404(
            OperationQCStatus,
            pk=pk,
            company_id=active_company_id
        )
        
        # Check if already approved or rejected
        if qc_status.qc_status == OperationQCStatus.QCStatus.APPROVED:
            return JsonResponse({
                'error': _('This operation has already been approved by QC.')
            }, status=400)
        
        if qc_status.qc_status == OperationQCStatus.QCStatus.REJECTED:
            return JsonResponse({
                'error': _('This operation has already been rejected by QC.')
            }, status=400)
        
        # Get rejection notes from request
        qc_notes = request.POST.get('qc_notes', '').strip()
        
        # Reject the operation
        qc_status.qc_status = OperationQCStatus.QCStatus.REJECTED
        qc_status.qc_approved_by = request.user
        qc_status.qc_status_date = timezone.now()
        if qc_notes:
            qc_status.qc_notes = qc_notes
        qc_status.save()
        
        messages.success(request, _('Operation rejected by QC successfully.'))
        return JsonResponse({
            'success': True,
            'message': _('Operation rejected by QC successfully.')
        })

