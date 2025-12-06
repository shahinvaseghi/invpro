"""
Rework Document views for production module.
Handles rework document creation for operations without performance documents
or operations with QC-rejected performance documents.
"""
from typing import Any, Dict, Optional, List
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Exists, OuterRef
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView
from django.views import View
from django import forms

from shared.mixins import FeaturePermissionRequiredMixin
from shared.views.base import (
    BaseDocumentListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDetailView,
    BaseDeleteView,
    EditLockProtectedMixin,
)
from shared.utils.permissions import get_user_feature_permissions, has_feature_permission
from inventory.utils.codes import generate_sequential_code
from production.models import (
    ReworkDocument,
    ProductOrder,
    ProcessOperation,
    PerformanceRecord,
    OperationQCStatus,
)


class ReworkDocumentListView(BaseDocumentListView):
    """List all rework documents for the active company."""
    model = ReworkDocument
    template_name = 'production/rework_document_list.html'
    context_object_name = 'object_list'
    paginate_by = 50
    feature_code = 'production.rework'
    required_action = 'view_own'
    active_module = 'production'
    default_status_filter = False
    default_order_by = ['-rework_date', 'rework_code']
    
    def get_select_related(self) -> List[str]:
        """Return list of fields to select_related."""
        return [
            'order',
            'order__finished_item',
            'operation',
            'original_performance',
            'approved_by',
        ]
    
    def get_queryset(self):
        """Filter rework documents by active company and permissions."""
        queryset = super().get_queryset()
        
        # Check if user has view_all permission
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            permissions = get_user_feature_permissions(self.request.user, active_company_id)
            if not has_feature_permission(permissions, 'production.rework', action='view_all'):
                # Only show own records
                queryset = queryset.filter(created_by=self.request.user)
        
        return queryset
    
    def get_page_title(self) -> str:
        """Return page title."""
        return _('Rework Documents')
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Rework'), 'url': None},
        ]
    
    def get_create_url(self):
        """Return create URL if user has permission."""
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            permissions = get_user_feature_permissions(self.request.user, active_company_id)
            if has_feature_permission(permissions, 'production.rework', action='create') or self.request.user.is_superuser:
                return reverse_lazy('production:rework_document_create')
        return None
    
    def get_create_button_text(self) -> str:
        """Return create button text."""
        return _('Create Rework Document +')
    
    def get_detail_url_name(self) -> Optional[str]:
        """Return detail URL name."""
        return 'production:rework_document_detail'
    
    def get_edit_url_name(self) -> Optional[str]:
        """Return edit URL name."""
        return 'production:rework_document_edit'
    
    def get_delete_url_name(self) -> Optional[str]:
        """Return delete URL name."""
        return 'production:rework_document_delete'
    
    def get_empty_state_title(self) -> str:
        """Return empty state title."""
        return _('No Rework Documents Found')
    
    def get_empty_state_message(self) -> str:
        """Return empty state message."""
        return _('Create your first rework document to get started.')
    
    def get_empty_state_icon(self) -> str:
        """Return empty state icon."""
        return '🔄'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for generic list template."""
        context = super().get_context_data(**kwargs)
        context['show_filters'] = False
        
        # Add user_feature_permissions for template
        active_company_id = self.request.session.get('active_company_id')
        if active_company_id:
            context['user_feature_permissions'] = get_user_feature_permissions(self.request.user, active_company_id)
        
        return context


class ReworkOrderSelectForm(forms.Form):
    """Form for selecting a production order in create view."""
    order = forms.ModelChoiceField(
        queryset=ProductOrder.objects.none(),
        label=_('Production Order'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_order_select'}),
    )


class ReworkDocumentCreateView(BaseCreateView):
    """
    Create a rework document.
    Shows order selection form, then two lists of operations after order is selected.
    """
    model = ReworkDocument
    template_name = 'production/rework_document_form.html'
    feature_code = 'production.rework'
    required_action = 'create'
    active_module = 'production'
    success_url = reverse_lazy('production:rework_document_list')
    success_message = _('Rework document created successfully.')
    fields = ['order', 'operation', 'original_performance', 'reason', 'notes', 'approved_by']
    
    def get_form(self, form_class=None):
        """Get form with company-scoped querysets."""
        form = super().get_form(form_class)
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if active_company_id:
            # Filter orders by company
            form.fields['order'].queryset = ProductOrder.objects.filter(
                company_id=active_company_id,
                process__isnull=False,
            ).select_related('finished_item', 'process')
            
            # Filter operations by company (will be filtered by selected order in JS)
            form.fields['operation'].queryset = ProcessOperation.objects.filter(
                company_id=active_company_id,
                is_enabled=1,
            ).select_related('process', 'work_line')
            
            # Filter performance records by company
            form.fields['original_performance'].queryset = PerformanceRecord.objects.filter(
                company_id=active_company_id,
                document_type=PerformanceRecord.DocumentType.OPERATIONAL,
            )
            
            # Filter approvers - users with approve permission
            from shared.models import AccessLevelPermission, UserCompanyAccess
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Get access levels that have approve permission for rework
            approve_access_level_ids = list(AccessLevelPermission.objects.filter(
                resource_code='production.rework',
                can_approve=1,
            ).values_list('access_level_id', flat=True))
            
            # Get users who have these access levels for the active company
            approver_user_ids = list(UserCompanyAccess.objects.filter(
                company_id=active_company_id,
                access_level_id__in=approve_access_level_ids,
            ).values_list('user_id', flat=True))
            
            if approver_user_ids:
                form.fields['approved_by'].queryset = User.objects.filter(
                    Q(id__in=approver_user_ids) | Q(is_superuser=True),
                ).order_by('username')
            else:
                form.fields['approved_by'].queryset = User.objects.filter(
                    is_superuser=True
                ).order_by('username')
        
        return form
    
    def get_initial(self):
        """Set initial values."""
        initial = super().get_initial()
        # Get order from GET parameter if available
        order_id = self.request.GET.get('order')
        if order_id:
            try:
                order = ProductOrder.objects.get(pk=order_id)
                initial['order'] = order
            except ProductOrder.DoesNotExist:
                pass
        return initial
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Rework'), 'url': reverse_lazy('production:rework_document_list')},
            {'label': _('Create'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:rework_document_list')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Create Rework Document')
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        context['form_id'] = 'rework-form'
        
        # Get selected order from form or GET
        selected_order = None
        if self.request.method == 'GET':
            order_id = self.request.GET.get('order')
            if order_id:
                try:
                    selected_order = ProductOrder.objects.get(
                        pk=order_id,
                        company_id=active_company_id,
                    )
                except ProductOrder.DoesNotExist:
                    pass
        elif self.request.method == 'POST' and hasattr(self, 'form') and self.form.is_valid():
            selected_order = self.form.cleaned_data.get('order')
        
        # Get operations lists if order is selected
        list1_operations = []
        list2_operations = []
        if selected_order:
            operations_data = self.get_operations_lists(selected_order)
            list1_operations = operations_data['list1_operations']
            list2_operations = operations_data['list2_operations']
        
        context['selected_order'] = selected_order
        context['list1_operations'] = list1_operations
        context['list2_operations'] = list2_operations
        
        return context
    
    def get_operations_lists(self, order):
        """Get two lists of operations for the selected order."""
        if not order or not order.process:
            return {
                'list1_operations': [],
                'list2_operations': [],
            }
        
        process_operations = order.process.operations.filter(
            company_id=order.company_id,
            is_enabled=1,
        ).select_related('process', 'work_line').order_by('sequence_order')
        
        # List 1: Operations without performance documents
        list1_operations = []
        for op in process_operations:
            has_performance = PerformanceRecord.objects.filter(
                company_id=order.company_id,
                order=order,
                operation=op,
                document_type=PerformanceRecord.DocumentType.OPERATIONAL,
            ).exists()
            
            if not has_performance:
                list1_operations.append(op)
        
        # List 2: Operations with QC-rejected performance documents
        list2_operations = []
        for op in process_operations:
            rejected_qc_status = OperationQCStatus.objects.filter(
                company_id=order.company_id,
                order=order,
                operation=op,
                qc_status=OperationQCStatus.QCStatus.REJECTED,
            ).select_related('performance').first()
            
            if rejected_qc_status:
                list2_operations.append({
                    'operation': op,
                    'qc_status': rejected_qc_status,
                    'performance': rejected_qc_status.performance,
                })
        
        return {
            'list1_operations': list1_operations,
            'list2_operations': list2_operations,
        }
    
    @transaction.atomic
    def form_valid(self, form):
        """Generate rework code and save."""
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if not active_company_id:
            form.add_error(None, _('No active company selected.'))
            return self.form_invalid(form)
        
        # Get operation from POST (from radio button selection)
        operation_id = self.request.POST.get('operation')
        if operation_id:
            try:
                operation = ProcessOperation.objects.get(
                    pk=operation_id,
                    company_id=active_company_id,
                )
                form.instance.operation = operation
                
                # If operation has a QC-rejected performance, set original_performance
                if not form.instance.original_performance:
                    rejected_qc_status = OperationQCStatus.objects.filter(
                        company_id=active_company_id,
                        order=form.instance.order,
                        operation=operation,
                        qc_status=OperationQCStatus.QCStatus.REJECTED,
                    ).select_related('performance').first()
                    
                    if rejected_qc_status:
                        form.instance.original_performance = rejected_qc_status.performance
            except ProcessOperation.DoesNotExist:
                form.add_error('operation', _('Selected operation does not exist.'))
                return self.form_invalid(form)
        else:
            form.add_error('operation', _('Please select an operation.'))
            return self.form_invalid(form)
        
        # Generate rework code
        if not form.instance.rework_code:
            rework_code = generate_sequential_code(
                ReworkDocument,
                company_id=active_company_id,
                width=8,
                prefix='RW',
            )
            form.instance.rework_code = rework_code
        
        form.instance.company_id = active_company_id
        form.instance.created_by = self.request.user
        
        messages.success(self.request, _('Rework document created successfully.'))
        return super().form_valid(form)


class ReworkDocumentDetailView(BaseDetailView):
    """View details of a rework document."""
    model = ReworkDocument
    template_name = 'production/rework_document_detail.html'
    context_object_name = 'object'
    feature_code = 'production.rework'
    required_action = 'view_own'
    active_module = 'production'
    
    def get_list_url(self):
        """Return list URL."""
        return reverse_lazy('production:rework_document_list')
    
    def get_edit_url(self):
        """Return edit URL."""
        return reverse_lazy('production:rework_document_edit', kwargs={'pk': self.object.pk})
    
    def can_edit_object(self, obj=None, feature_code=None) -> bool:
        """Check if object can be edited."""
        check_obj = obj if obj is not None else self.object
        if hasattr(check_obj, 'is_locked'):
            return not bool(check_obj.is_locked)
        return True


class ReworkDocumentUpdateView(BaseUpdateView, EditLockProtectedMixin):
    """Update an existing rework document."""
    model = ReworkDocument
    template_name = 'production/rework_document_form.html'
    success_url = reverse_lazy('production:rework_document_list')
    feature_code = 'production.rework'
    required_action = 'edit_own'
    active_module = 'production'
    success_message = _('Rework document updated successfully.')
    fields = ['order', 'operation', 'original_performance', 'reason', 'notes', 'approved_by']
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Rework'), 'url': reverse_lazy('production:rework_document_list')},
            {'label': _('Edit'), 'url': None},
        ]
    
    def get_cancel_url(self):
        """Return cancel URL."""
        return reverse_lazy('production:rework_document_list')
    
    def get_form_title(self) -> str:
        """Return form title."""
        return _('Edit Rework Document')
    
    def get_form(self, form_class=None):
        """Get form with company-scoped querysets."""
        form = super().get_form(form_class)
        active_company_id: Optional[int] = self.request.session.get('active_company_id')
        
        if active_company_id:
            # Filter orders by company
            form.fields['order'].queryset = ProductOrder.objects.filter(
                company_id=active_company_id,
                process__isnull=False,
            ).select_related('finished_item', 'process')
            
            # Filter operations by company
            form.fields['operation'].queryset = ProcessOperation.objects.filter(
                company_id=active_company_id,
                is_enabled=1,
            ).select_related('process', 'work_line')
            
            # Filter performance records by company
            form.fields['original_performance'].queryset = PerformanceRecord.objects.filter(
                company_id=active_company_id,
                document_type=PerformanceRecord.DocumentType.OPERATIONAL,
            )
            
            # Filter approvers - users with approve permission
            from shared.models import AccessLevelPermission, UserCompanyAccess
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Get access levels that have approve permission for rework
            approve_access_level_ids = list(AccessLevelPermission.objects.filter(
                resource_code='production.rework',
                can_approve=1,
            ).values_list('access_level_id', flat=True))
            
            # Get users who have these access levels for the active company
            approver_user_ids = list(UserCompanyAccess.objects.filter(
                company_id=active_company_id,
                access_level_id__in=approve_access_level_ids,
            ).values_list('user_id', flat=True))
            
            if approver_user_ids:
                form.fields['approved_by'].queryset = User.objects.filter(
                    Q(id__in=approver_user_ids) | Q(is_superuser=True),
                ).order_by('username')
            else:
                form.fields['approved_by'].queryset = User.objects.filter(
                    is_superuser=True
                ).order_by('username')
        
        return form
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add context for template."""
        context = super().get_context_data(**kwargs)
        context['form_id'] = 'rework-form'
        
        # Get operations lists if order is selected
        selected_order = self.object.order if self.object else None
        list1_operations = []
        list2_operations = []
        if selected_order:
            operations_data = self.get_operations_lists(selected_order)
            list1_operations = operations_data['list1_operations']
            list2_operations = operations_data['list2_operations']
        
        context['selected_order'] = selected_order
        context['list1_operations'] = list1_operations
        context['list2_operations'] = list2_operations
        
        return context
    
    def get_operations_lists(self, order):
        """Get two lists of operations for the selected order."""
        if not order or not order.process:
            return {
                'list1_operations': [],
                'list2_operations': [],
            }
        
        process_operations = order.process.operations.filter(
            company_id=order.company_id,
            is_enabled=1,
        ).select_related('process', 'work_line').order_by('sequence_order')
        
        # List 1: Operations without performance documents
        list1_operations = []
        for op in process_operations:
            has_performance = PerformanceRecord.objects.filter(
                company_id=order.company_id,
                order=order,
                operation=op,
                document_type=PerformanceRecord.DocumentType.OPERATIONAL,
            ).exists()
            
            if not has_performance:
                list1_operations.append(op)
        
        # List 2: Operations with QC-rejected performance documents
        list2_operations = []
        for op in process_operations:
            rejected_qc_status = OperationQCStatus.objects.filter(
                company_id=order.company_id,
                order=order,
                operation=op,
                qc_status=OperationQCStatus.QCStatus.REJECTED,
            ).select_related('performance').first()
            
            if rejected_qc_status:
                list2_operations.append({
                    'operation': op,
                    'qc_status': rejected_qc_status,
                    'performance': rejected_qc_status.performance,
                })
        
        return {
            'list1_operations': list1_operations,
            'list2_operations': list2_operations,
        }


class ReworkDocumentDeleteView(BaseDeleteView):
    """Delete a rework document."""
    model = ReworkDocument
    template_name = 'shared/generic/generic_confirm_delete.html'
    success_url = reverse_lazy('production:rework_document_list')
    feature_code = 'production.rework'
    required_action = 'delete_own'
    active_module = 'production'
    success_message = _('Rework document deleted successfully.')
    
    def get_delete_title(self) -> str:
        """Return delete title."""
        return _('Delete Rework Document')
    
    def get_confirmation_message(self) -> str:
        """Return confirmation message."""
        return _('Are you sure you want to delete this rework document?')
    
    def get_object_details(self) -> List[Dict[str, str]]:
        """Return object details for confirmation."""
        from production.utils.jalali import gregorian_to_jalali
        
        details = [
            {'label': _('Rework Code'), 'value': f'<code>{self.object.rework_code}</code>'},
            {'label': _('Product Order'), 'value': self.object.order_code},
        ]
        
        if self.object.rework_date:
            try:
                jalali = gregorian_to_jalali(
                    self.object.rework_date.year,
                    self.object.rework_date.month,
                    self.object.rework_date.day
                )
                date_str = f"{jalali[0]}/{jalali[1]:02d}/{jalali[2]:02d}"
            except:
                date_str = str(self.object.rework_date)
            details.append({'label': _('Rework Date'), 'value': date_str})
        
        details.append({'label': _('Status'), 'value': self.object.get_status_display()})
        
        return details
    
    def get_breadcrumbs(self) -> List[Dict[str, Optional[str]]]:
        """Return breadcrumbs list."""
        return [
            {'label': _('Production'), 'url': None},
            {'label': _('Rework'), 'url': reverse_lazy('production:rework_document_list')},
            {'label': _('Delete'), 'url': None},
        ]


class ReworkDocumentApproveView(FeaturePermissionRequiredMixin, View):
    """Approve a rework document."""
    feature_code = 'production.rework'
    required_action = 'approve'
    
    def post(self, request, pk: int):
        """Approve the rework document."""
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            return JsonResponse({'error': _('No active company selected.')}, status=400)
        
        rework_doc = get_object_or_404(
            ReworkDocument,
            pk=pk,
            company_id=active_company_id
        )
        
        # Check if already approved or rejected
        if rework_doc.status == ReworkDocument.Status.APPROVED:
            return JsonResponse({
                'error': _('This rework document has already been approved.')
            }, status=400)
        
        if rework_doc.status == ReworkDocument.Status.REJECTED:
            return JsonResponse({
                'error': _('This rework document has already been rejected.')
            }, status=400)
        
        # Check if user is the approver
        if rework_doc.approved_by != request.user:
            return JsonResponse({
                'error': _('You are not authorized to approve this rework document.')
            }, status=403)
        
        # Approve the document
        rework_doc.status = ReworkDocument.Status.APPROVED
        rework_doc.save()
        
        messages.success(request, _('Rework document approved successfully.'))
        return JsonResponse({
            'success': True,
            'message': _('Rework document approved successfully.')
        })


class ReworkDocumentRejectView(FeaturePermissionRequiredMixin, View):
    """Reject a rework document."""
    feature_code = 'production.rework'
    required_action = 'reject'
    
    def post(self, request, pk: int):
        """Reject the rework document."""
        active_company_id: Optional[int] = request.session.get('active_company_id')
        
        if not active_company_id:
            return JsonResponse({'error': _('No active company selected.')}, status=400)
        
        rework_doc = get_object_or_404(
            ReworkDocument,
            pk=pk,
            company_id=active_company_id
        )
        
        # Check if already approved or rejected
        if rework_doc.status == ReworkDocument.Status.APPROVED:
            return JsonResponse({
                'error': _('This rework document has already been approved.')
            }, status=400)
        
        if rework_doc.status == ReworkDocument.Status.REJECTED:
            return JsonResponse({
                'error': _('This rework document has already been rejected.')
            }, status=400)
        
        # Check if user is the approver
        if rework_doc.approved_by != request.user:
            return JsonResponse({
                'error': _('You are not authorized to reject this rework document.')
            }, status=403)
        
        # Reject the document
        rework_doc.status = ReworkDocument.Status.REJECTED
        rework_doc.save()
        
        messages.success(request, _('Rework document rejected successfully.'))
        return JsonResponse({
            'success': True,
            'message': _('Rework document rejected successfully.')
        })
