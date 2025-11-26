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
        
        # Get active company from context processor first (it handles default selection)
        active_company = context.get('active_company')
        company_id = None
        
        if active_company:
            company_id = active_company.id
            # Ensure it's saved in session
            current_session_company_id = self.request.session.get('active_company_id')
            if current_session_company_id != company_id:
                self.request.session['active_company_id'] = company_id
                self.request.session.modified = True
        else:
            # If context processor didn't set it, try to get from session
            company_id = self.request.session.get('active_company_id')
            
            # If still no company_id, try to get user's companies and set first one
            if not company_id and self.request.user.is_authenticated:
                from shared.models import UserCompanyAccess
                user_accesses = UserCompanyAccess.objects.filter(
                    user=self.request.user,
                    is_enabled=1
                ).select_related('company')
                
                if user_accesses.exists():
                    # Try to use user's default company first
                    if hasattr(self.request.user, 'default_company') and self.request.user.default_company:
                        default_company = self.request.user.default_company
                        if user_accesses.filter(company=self.request.user.default_company).exists():
                            company_id = default_company.id
                            active_company = default_company
                    
                    # If no default, use first available
                    if not company_id:
                        first_access = user_accesses.first()
                        if first_access:
                            company_id = first_access.company.id
                            active_company = first_access.company
                    
                    # Save to session
                    if company_id:
                        self.request.session['active_company_id'] = company_id
                        self.request.session.modified = True
                        context['active_company'] = active_company
        
        if not company_id:
            # No company available, return empty stats
            context['stats'] = {
                'total_items': 0,
                'total_warehouses': 0,
                'total_suppliers': 0,
                'temp_receipts_pending': 0,
                'temp_receipts_qc_pending': 0,
                'permanent_receipts_today': 0,
                'total_permanent_receipts': 0,
                'permanent_issues_today': 0,
                'consumption_issues_today': 0,
                'total_permanent_issues': 0,
                'pending_purchase_requests': 0,
                'pending_warehouse_requests': 0,
                'total_pending_requests': 0,
                'deficit_records': 0,
                'surplus_records': 0,
                'total_stocktaking_records': 0,
                'pending_purchase_approvals': 0,
                'pending_warehouse_approvals': 0,
                'pending_stocktaking_approvals': 0,
                'total_pending_approvals': 0,
                'recent_receipts': 0,
                'recent_issues': 0,
            }
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
        
        # Pending Approvals
        # Purchase requests awaiting approval (draft with approver assigned)
        pending_purchase_approvals = inventory_models.PurchaseRequest.objects.filter(
            company_id=company_id,
            status=inventory_models.PurchaseRequest.Status.DRAFT,
            approver__isnull=False,
            is_enabled=1
        ).count()
        
        # Warehouse requests awaiting approval (draft with approver assigned)
        pending_warehouse_approvals = inventory_models.WarehouseRequest.objects.filter(
            company_id=company_id,
            request_status='draft',
            approver__isnull=False,
            is_enabled=1
        ).count()
        
        # Stocktaking records awaiting approval (records module)
        pending_stocktaking_approvals = inventory_models.StocktakingRecord.objects.filter(
            company_id=company_id,
            approval_status='pending',
            approver__isnull=False,
            is_locked=0,
            is_enabled=1
        ).count()
        
        total_pending_approvals = (
            pending_purchase_approvals +
            pending_warehouse_approvals +
            pending_stocktaking_approvals
        )
        
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
                'total_pending_requests': pending_purchase_requests + pending_warehouse_requests,
                'deficit_records': deficit_records,
                'surplus_records': surplus_records,
                'total_stocktaking_records': deficit_records + surplus_records,
                'pending_purchase_approvals': pending_purchase_approvals,
                'pending_warehouse_approvals': pending_warehouse_approvals,
                'pending_stocktaking_approvals': pending_stocktaking_approvals,
                'total_pending_approvals': total_pending_approvals,
                'recent_receipts': recent_receipts,
                'recent_issues': recent_issues,
            }
        }
