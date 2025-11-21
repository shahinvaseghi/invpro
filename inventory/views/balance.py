"""
Inventory Balance views for inventory module.

This module contains views for:
- Inventory Balance Display
- Inventory Balance Details
- Inventory Balance API
"""
from typing import Dict, Any, Optional
from datetime import date
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from .base import InventoryBaseView
from .. import models
from .. import inventory_balance


class InventoryBalanceView(InventoryBaseView, TemplateView):
    """
    Display current inventory balances calculated from stocktaking baseline
    plus subsequent receipts and issues.
    """
    template_name = 'inventory/inventory_balance.html'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Calculate and return inventory balances."""
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        warehouse_id = self.request.GET.get('warehouse_id')
        item_type_id = self.request.GET.get('item_type_id')
        item_category_id = self.request.GET.get('item_category_id')
        as_of_date = self.request.GET.get('as_of_date')
        
        # Parse date (accepts both Gregorian YYYY-MM-DD and Jalali YYYY/MM/DD)
        if as_of_date:
            try:
                # Try Gregorian format first (YYYY-MM-DD)
                as_of_date = date.fromisoformat(as_of_date)
            except ValueError:
                try:
                    # Try Jalali format (YYYY/MM/DD)
                    from ..utils.jalali import jalali_to_gregorian
                    as_of_date = jalali_to_gregorian(as_of_date)
                except (ValueError, TypeError):
                    as_of_date = None
        
        # Get warehouse and filter options for UI
        company_id: Optional[int] = self.request.session.get('active_company_id')
        context['warehouses'] = models.Warehouse.objects.filter(
            company_id=company_id, is_enabled=1
        ).order_by('name')
        context['item_types'] = models.ItemType.objects.filter(
            company_id=company_id, is_enabled=1
        ).order_by('name')
        context['item_categories'] = models.ItemCategory.objects.filter(
            company_id=company_id, is_enabled=1
        ).order_by('name')
        
        # Selected filters
        context['selected_warehouse_id'] = warehouse_id
        context['selected_item_type_id'] = item_type_id
        context['selected_item_category_id'] = item_category_id
        context['as_of_date'] = as_of_date or date.today()
        
        # Calculate balances if warehouse is selected
        if warehouse_id:
            try:
                if not company_id:
                    company_id = self.request.user.usercompanyaccess_set.first().company_id if self.request.user.usercompanyaccess_set.exists() else 1
                
                balances = inventory_balance.calculate_warehouse_balances(
                    company_id=company_id,
                    warehouse_id=int(warehouse_id),
                    as_of_date=as_of_date,
                    item_type_id=int(item_type_id) if item_type_id else None,
                    item_category_id=int(item_category_id) if item_category_id else None,
                )
                context['balances'] = balances
                context['total_items'] = len(balances)
                context['total_balance_value'] = sum(b['current_balance'] for b in balances)
            except Exception as e:
                context['error'] = str(e)
                context['balances'] = []
        else:
            context['balances'] = []
        
        return context


class InventoryBalanceDetailsView(InventoryBaseView, TemplateView):
    """
    Display detailed transaction history (receipts and issues) for a specific item in a warehouse.
    Shows all movements from baseline date to as_of_date.
    """
    template_name = 'inventory/inventory_balance_details.html'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Get transaction history for item in warehouse."""
        context = super().get_context_data(**kwargs)
        
        item_id = kwargs.get('item_id')
        warehouse_id = kwargs.get('warehouse_id')
        as_of_date = self.request.GET.get('as_of_date')
        
        # Parse date
        if as_of_date:
            try:
                as_of_date = date.fromisoformat(as_of_date)
            except ValueError:
                try:
                    from ..utils.jalali import jalali_to_gregorian
                    as_of_date = jalali_to_gregorian(as_of_date)
                except (ValueError, TypeError):
                    as_of_date = None
        
        if not as_of_date:
            as_of_date = date.today()
        
        # Get company_id from session
        company_id: Optional[int] = self.request.session.get('active_company_id')
        if not company_id:
            company_id = self.request.user.usercompanyaccess_set.first().company_id if self.request.user.usercompanyaccess_set.exists() else 1
        
        # Get item and warehouse
        try:
            item = models.Item.objects.get(id=item_id, company_id=company_id)
            warehouse = models.Warehouse.objects.get(id=warehouse_id, company_id=company_id)
        except models.Item.DoesNotExist:
            context['error'] = _('Item not found')
            return context
        except models.Warehouse.DoesNotExist:
            context['error'] = _('Warehouse not found')
            return context
        
        # Get baseline
        baseline = inventory_balance.get_last_stocktaking_baseline(
            company_id, warehouse_id, item_id, as_of_date
        )
        baseline_date = baseline['baseline_date'] or date(1900, 1, 1)
        
        # Get all receipts (positive movements)
        receipts_perm = models.ReceiptPermanentLine.objects.filter(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            document__document_date__gt=baseline_date,
            document__document_date__lte=as_of_date,
            document__is_enabled=1,
        ).select_related('document', 'document__created_by').order_by('document__document_date', 'id')
        
        receipts_consignment = models.ReceiptConsignmentLine.objects.filter(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            document__document_date__gt=baseline_date,
            document__document_date__lte=as_of_date,
            document__is_enabled=1,
        ).select_related('document', 'document__created_by').order_by('document__document_date', 'id')
        
        # Get all issues (negative movements)
        issues_permanent = models.IssuePermanentLine.objects.filter(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            document__document_date__gt=baseline_date,
            document__document_date__lte=as_of_date,
            document__is_enabled=1,
        ).select_related('document', 'document__created_by').order_by('document__document_date', 'id')
        
        issues_consumption = models.IssueConsumptionLine.objects.filter(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            document__document_date__gt=baseline_date,
            document__document_date__lte=as_of_date,
            document__is_enabled=1,
        ).select_related('document', 'document__created_by').order_by('document__document_date', 'id')
        
        issues_consignment = models.IssueConsignmentLine.objects.filter(
            company_id=company_id,
            warehouse_id=warehouse_id,
            item_id=item_id,
            document__document_date__gt=baseline_date,
            document__document_date__lte=as_of_date,
            document__is_enabled=1,
        ).select_related('document', 'document__created_by').order_by('document__document_date', 'id')
        
        # Combine all transactions
        transactions = []
        
        # Add receipts
        for receipt in receipts_perm:
            transactions.append({
                'date': receipt.document.document_date,
                'type': 'receipt',
                'type_label': _('Permanent Receipt'),
                'document_code': receipt.document.document_code,
                'quantity': receipt.quantity,
                'unit': receipt.unit,
                'created_by': receipt.document.created_by.username if receipt.document.created_by else '—',
            })
        
        for receipt in receipts_consignment:
            transactions.append({
                'date': receipt.document.document_date,
                'type': 'receipt',
                'type_label': _('Consignment Receipt'),
                'document_code': receipt.document.document_code,
                'quantity': receipt.quantity,
                'unit': receipt.unit,
                'created_by': receipt.document.created_by.username if receipt.document.created_by else '—',
            })
        
        # Add issues
        for issue in issues_permanent:
            transactions.append({
                'date': issue.document.document_date,
                'type': 'issue',
                'type_label': _('Permanent Issue'),
                'document_code': issue.document.document_code,
                'quantity': issue.quantity,
                'unit': issue.unit,
                'created_by': issue.document.created_by.username if issue.document.created_by else '—',
            })
        
        for issue in issues_consumption:
            transactions.append({
                'date': issue.document.document_date,
                'type': 'issue',
                'type_label': _('Consumption Issue'),
                'document_code': issue.document.document_code,
                'quantity': issue.quantity,
                'unit': issue.unit,
                'created_by': issue.document.created_by.username if issue.document.created_by else '—',
            })
        
        for issue in issues_consignment:
            transactions.append({
                'date': issue.document.document_date,
                'type': 'issue',
                'type_label': _('Consignment Issue'),
                'document_code': issue.document.document_code,
                'quantity': issue.quantity,
                'unit': issue.unit,
                'created_by': issue.document.created_by.username if issue.document.created_by else '—',
            })
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'])
        
        # Calculate running balance
        running_balance = baseline['baseline_quantity']
        for transaction in transactions:
            if transaction['type'] == 'receipt':
                running_balance += transaction['quantity']
            else:
                running_balance -= transaction['quantity']
            transaction['running_balance'] = running_balance
        
        # Calculate current balance
        current_balance = baseline['baseline_quantity']
        if transactions:
            current_balance = transactions[-1]['running_balance']
        
        context.update({
            'item': item,
            'warehouse': warehouse,
            'baseline': baseline,
            'baseline_date': baseline_date,
            'as_of_date': as_of_date,
            'transactions': transactions,
            'total_receipts': sum(t['quantity'] for t in transactions if t['type'] == 'receipt'),
            'total_issues': sum(t['quantity'] for t in transactions if t['type'] == 'issue'),
            'current_balance': current_balance,
        })
        
        return context


class InventoryBalanceAPIView(InventoryBaseView, TemplateView):
    """
    JSON API endpoint for inventory balance calculation.
    """
    def get(self, request, *args, **kwargs) -> JsonResponse:
        """Return JSON response with inventory balance."""
        warehouse_id = request.GET.get('warehouse_id')
        item_id = request.GET.get('item_id')
        as_of_date = request.GET.get('as_of_date')
        
        if not warehouse_id or not item_id:
            return JsonResponse({'error': 'warehouse_id and item_id are required'}, status=400)
        
        # Parse date
        if as_of_date:
            try:
                as_of_date = date.fromisoformat(as_of_date)
            except ValueError:
                as_of_date = None
        
        try:
            # Get company from session
            company_id: Optional[int] = request.session.get('active_company_id')
            if not company_id:
                company_id = request.user.usercompanyaccess_set.first().company_id if request.user.usercompanyaccess_set.exists() else 1
            
            balance = inventory_balance.calculate_item_balance(
                company_id=company_id,
                warehouse_id=int(warehouse_id),
                item_id=int(item_id),
                as_of_date=as_of_date
            )
            
            return JsonResponse(balance)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

