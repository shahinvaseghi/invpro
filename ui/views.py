from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView

from inventory import models as inventory_models


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "ui/dashboard.html"
    login_url = reverse_lazy("admin:login")
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get active company
        company_id = self.request.session.get('active_company_id')
        if not company_id:
            return context
        
        # Calculate statistics
        stats = self._calculate_stats(company_id)
        context.update(stats)
        
        return context
    
    def _calculate_stats(self, company_id):
        """Calculate dashboard statistics for the active company."""
        today = timezone.now().date()
        
        # Inventory Master Data
        total_items = inventory_models.Item.objects.filter(
            company_id=company_id,
            is_enabled=1
        ).count()
        
        total_warehouses = inventory_models.Warehouse.objects.filter(
            company_id=company_id,
            is_enabled=1
        ).count()
        
        total_suppliers = inventory_models.Supplier.objects.filter(
            company_id=company_id,
            is_enabled=1
        ).count()
        
        # Receipts
        temp_receipts_pending = inventory_models.ReceiptTemporary.objects.filter(
            company_id=company_id,
            status=inventory_models.ReceiptTemporary.Status.DRAFT,
            is_enabled=1
        ).count()
        
        temp_receipts_qc_pending = inventory_models.ReceiptTemporary.objects.filter(
            company_id=company_id,
            status=inventory_models.ReceiptTemporary.Status.AWAITING_INSPECTION,
            is_enabled=1
        ).count()
        
        permanent_receipts_today = inventory_models.ReceiptPermanent.objects.filter(
            company_id=company_id,
            document_date=today,
            is_enabled=1
        ).count()
        
        total_permanent_receipts = inventory_models.ReceiptPermanent.objects.filter(
            company_id=company_id,
            is_enabled=1
        ).count()
        
        # Issues
        permanent_issues_today = inventory_models.IssuePermanent.objects.filter(
            company_id=company_id,
            document_date=today,
            is_enabled=1
        ).count()
        
        consumption_issues_today = inventory_models.IssueConsumption.objects.filter(
            company_id=company_id,
            document_date=today,
            is_enabled=1
        ).count()
        
        total_permanent_issues = inventory_models.IssuePermanent.objects.filter(
            company_id=company_id,
            is_enabled=1
        ).count()
        
        # Requests
        pending_purchase_requests = inventory_models.PurchaseRequest.objects.filter(
            company_id=company_id,
            status=inventory_models.PurchaseRequest.Status.DRAFT,
            is_enabled=1
        ).count()
        
        pending_warehouse_requests = inventory_models.WarehouseRequest.objects.filter(
            company_id=company_id,
            request_status='draft',
            is_enabled=1
        ).count()
        
        # Stocktaking
        deficit_records = inventory_models.StocktakingDeficit.objects.filter(
            company_id=company_id,
            is_locked=0,
            is_enabled=1
        ).count()
        
        surplus_records = inventory_models.StocktakingSurplus.objects.filter(
            company_id=company_id,
            is_locked=0,
            is_enabled=1
        ).count()
        
        # Recent activity (last 7 days)
        week_ago = today - timezone.timedelta(days=7)
        recent_receipts = inventory_models.ReceiptPermanent.objects.filter(
            company_id=company_id,
            document_date__gte=week_ago,
            is_enabled=1
        ).count()
        
        recent_issues = inventory_models.IssuePermanent.objects.filter(
            company_id=company_id,
            document_date__gte=week_ago,
            is_enabled=1
        ).count()
        
        return {
            'stats': {
                'total_items': total_items,
                'total_warehouses': total_warehouses,
                'total_suppliers': total_suppliers,
                'temp_receipts_pending': temp_receipts_pending,
                'temp_receipts_qc_pending': temp_receipts_qc_pending,
                'permanent_receipts_today': permanent_receipts_today,
                'total_permanent_receipts': total_permanent_receipts,
                'permanent_issues_today': permanent_issues_today,
                'consumption_issues_today': consumption_issues_today,
                'total_permanent_issues': total_permanent_issues,
                'pending_purchase_requests': pending_purchase_requests,
                'pending_warehouse_requests': pending_warehouse_requests,
                'deficit_records': deficit_records,
                'surplus_records': surplus_records,
                'recent_receipts': recent_receipts,
                'recent_issues': recent_issues,
            }
        }
