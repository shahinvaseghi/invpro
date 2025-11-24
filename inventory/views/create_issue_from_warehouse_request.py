"""
Views for selecting quantity from Warehouse Request before creating Issue documents.

This module contains intermediate views that allow users to review warehouse request
and adjust quantity before creating the issue document.
Since Warehouse Request is single-line, this is simpler than purchase request flow.
"""
from typing import Dict, Any
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from decimal import Decimal, InvalidOperation

from .base import InventoryBaseView
from shared.mixins import FeaturePermissionRequiredMixin
from .. import models


class CreateIssueFromWarehouseRequestView(FeaturePermissionRequiredMixin, InventoryBaseView, TemplateView):
    """Base view for selecting quantity from warehouse request to create issue."""
    issue_type = None  # 'permanent', 'consumption', 'consignment'
    template_name = 'inventory/create_issue_from_warehouse_request.html'
    required_action = 'create_issue_from_warehouse_request'
    
    def get_warehouse_request(self, pk: int):
        """Get warehouse request and check permissions."""
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            from django.http import Http404
            raise Http404(_('شرکت فعال مشخص نشده است.'))
        
        warehouse_request = get_object_or_404(
            models.WarehouseRequest,
            pk=pk,
            company_id=company_id,
            request_status='approved',
            is_enabled=1
        )
        return warehouse_request
    
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Display form to review warehouse request and adjust quantity."""
        context = super().get_context_data(**kwargs)
        warehouse_request = self.get_warehouse_request(kwargs['pk'])
        
        context['warehouse_request'] = warehouse_request
        context['issue_type'] = self.issue_type
        
        issue_type_names = {
            'permanent': _('حواله دائم'),
            'consumption': _('حواله مصرف'),
            'consignment': _('حواله امانی'),
        }
        context['issue_type_name'] = issue_type_names.get(self.issue_type, '')
        
        # Calculate remaining quantity (if already issued, subtract)
        remaining_quantity = warehouse_request.quantity_requested
        if warehouse_request.quantity_issued:
            remaining_quantity = warehouse_request.quantity_requested - warehouse_request.quantity_issued
        
        context['remaining_quantity'] = remaining_quantity
        context['default_quantity'] = remaining_quantity
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Process selected quantity and redirect to issue creation."""
        import logging
        logger = logging.getLogger('inventory.views.create_issue_from_warehouse_request')
        logger.info("=" * 80)
        logger.info(f"POST request received for CreateIssueFromWarehouseRequestView (issue_type={self.issue_type})")
        logger.info(f"URL kwargs: {kwargs}")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        
        warehouse_request = self.get_warehouse_request(kwargs['pk'])
        logger.info(f"Warehouse request found: {warehouse_request.request_code} (pk={warehouse_request.pk})")
        
        # Get quantity from form
        quantity_key = 'quantity'
        quantity_value = request.POST.get(quantity_key, '0')
        logger.info(f"Quantity from form: {quantity_value}")
        
        try:
            quantity = Decimal(str(quantity_value))
            logger.info(f"Parsed quantity: {quantity}")
            
            # Calculate remaining quantity
            remaining_quantity = warehouse_request.quantity_requested
            if warehouse_request.quantity_issued:
                remaining_quantity = warehouse_request.quantity_requested - warehouse_request.quantity_issued
            
            logger.info(f"Remaining quantity: {remaining_quantity}")
            
            if quantity <= 0:
                logger.warning("Quantity is zero or negative")
                messages.error(request, _('مقدار باید بیشتر از صفر باشد.'))
                return self.get(request, *args, **kwargs)
            
            if quantity > remaining_quantity:
                logger.warning(f"Quantity {quantity} > remaining {remaining_quantity}, adjusting")
                quantity = remaining_quantity
                messages.warning(request, _('مقدار بیشتر از مقدار باقیمانده بود و به مقدار باقیمانده تنظیم شد.'))
            
            # Get optional notes
            notes = request.POST.get('notes', '').strip()
            
            # Store warehouse request data in session for issue creation
            session_key = f'warehouse_request_{warehouse_request.pk}_issue_{self.issue_type}_data'
            session_data = {
                'warehouse_request_id': warehouse_request.pk,
                'quantity': str(quantity),
                'notes': notes,
            }
            logger.info(f"Storing in session with key: {session_key}")
            logger.info(f"Session data to store: {session_data}")
            request.session[session_key] = session_data
            logger.info(f"Session data stored successfully. Session keys: {list(request.session.keys())}")
            
            # Redirect to issue creation
            if self.issue_type == 'permanent':
                return HttpResponseRedirect(reverse('inventory:issue_permanent_create_from_warehouse_request', kwargs={'pk': warehouse_request.pk}))
            elif self.issue_type == 'consumption':
                return HttpResponseRedirect(reverse('inventory:issue_consumption_create_from_warehouse_request', kwargs={'pk': warehouse_request.pk}))
            elif self.issue_type == 'consignment':
                return HttpResponseRedirect(reverse('inventory:issue_consignment_create_from_warehouse_request', kwargs={'pk': warehouse_request.pk}))
            
            return HttpResponseRedirect(reverse('inventory:warehouse_requests'))
            
        except (ValueError, InvalidOperation) as e:
            logger.error(f"Error parsing quantity: {e}")
            messages.error(request, _('مقدار وارد شده معتبر نیست.'))
            return self.get(request, *args, **kwargs)


class CreatePermanentIssueFromWarehouseRequestView(CreateIssueFromWarehouseRequestView):
    """View to select quantity from warehouse request for permanent issue."""
    issue_type = 'permanent'
    feature_code = 'inventory.issues.permanent'


class CreateConsumptionIssueFromWarehouseRequestView(CreateIssueFromWarehouseRequestView):
    """View to select quantity from warehouse request for consumption issue."""
    issue_type = 'consumption'
    feature_code = 'inventory.issues.consumption'


class CreateConsignmentIssueFromWarehouseRequestView(CreateIssueFromWarehouseRequestView):
    """View to select quantity from warehouse request for consignment issue."""
    issue_type = 'consignment'
    feature_code = 'inventory.issues.consignment'

