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

from .base import BaseCreateDocumentFromRequestView
from .. import models


class CreateIssueFromWarehouseRequestView(BaseCreateDocumentFromRequestView):
    """Base view for selecting quantity from warehouse request to create issue."""
    document_type = 'issue'
    request_model = models.WarehouseRequest
    is_multi_line = False
    template_name = 'inventory/create_issue_from_warehouse_request.html'
    required_action = 'create_issue_from_warehouse_request'
    
    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Display form to review warehouse request and adjust quantity."""
        context = super().get_context_data(**kwargs)
        # Add issue_type for backward compatibility with templates
        context['issue_type'] = self.document_subtype
        context['issue_type_name'] = context.get('issue_type_name', '')
        return context


class CreatePermanentIssueFromWarehouseRequestView(CreateIssueFromWarehouseRequestView):
    """View to select quantity from warehouse request for permanent issue."""
    document_subtype = 'permanent'
    feature_code = 'inventory.issues.permanent'


class CreateConsumptionIssueFromWarehouseRequestView(CreateIssueFromWarehouseRequestView):
    """View to select quantity from warehouse request for consumption issue."""
    document_subtype = 'consumption'
    feature_code = 'inventory.issues.consumption'


class CreateConsignmentIssueFromWarehouseRequestView(CreateIssueFromWarehouseRequestView):
    """View to select quantity from warehouse request for consignment issue."""
    document_subtype = 'consignment'
    feature_code = 'inventory.issues.consignment'

