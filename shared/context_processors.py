"""
Context processors for shared module.

Provides company-related context to all templates.
"""

def active_company(request):
    """
    Add active company information to template context.
    
    Returns:
        dict: Context with active_company and user_companies
    """
    context = {
        'active_company': None,
        'user_companies': [],
        'user_feature_permissions': {},
    }
    
    if request.user.is_authenticated:
        # Get active company from session
        active_company_id = request.session.get('active_company_id')
        
        # Get all companies user has access to
        from shared.models import UserCompanyAccess
        user_accesses = UserCompanyAccess.objects.filter(
            user=request.user,
            is_enabled=1
        ).select_related('company')
        
        context['user_companies'] = [access.company for access in user_accesses]
        
        # Set active company
        if active_company_id:
            try:
                context['active_company'] = next(
                    (c for c in context['user_companies'] if c.id == active_company_id),
                    None
                )
            except StopIteration:
                pass
        
        # If no active company set, use default company or first available
        if not context['active_company'] and context['user_companies']:
            # Try to use user's default company first
            if hasattr(request.user, 'default_company') and request.user.default_company:
                default_company = request.user.default_company
                # Check if user has access to default company
                if default_company in context['user_companies']:
                    context['active_company'] = default_company
            
            # If default company not set or not accessible, use first available
            if not context['active_company']:
                context['active_company'] = context['user_companies'][0]
            
            request.session['active_company_id'] = context['active_company'].id

        from shared.utils.permissions import get_user_feature_permissions

        company_id = context['active_company'].id if context['active_company'] else None
        context['user_feature_permissions'] = get_user_feature_permissions(request.user, company_id)
        
        # Calculate notifications
        context['notifications'] = []
        context['notification_count'] = 0
        
        if company_id:
            from production.models import Person
            from inventory import models as inventory_models
            from django.utils import timezone
            
            notifications = []
            
            # 1. Requests awaiting approval (user is approver)
            pending_purchase_approvals = inventory_models.PurchaseRequest.objects.filter(
                company_id=company_id,
                status=inventory_models.PurchaseRequest.Status.DRAFT,
                approver=request.user,
                is_enabled=1
            ).count()
            
            if pending_purchase_approvals > 0:
                notifications.append({
                    'type': 'approval_pending',
                    'message': f'{pending_purchase_approvals} درخواست خرید در انتظار تایید',
                    'url': 'inventory:purchase_requests',
                    'count': pending_purchase_approvals,
                })
            
            pending_warehouse_approvals = inventory_models.WarehouseRequest.objects.filter(
                company_id=company_id,
                request_status='draft',
                approver=request.user,
                is_enabled=1
            ).count()
            
            if pending_warehouse_approvals > 0:
                notifications.append({
                    'type': 'approval_pending',
                    'message': f'{pending_warehouse_approvals} درخواست انبار در انتظار تایید',
                    'url': 'inventory:warehouse_requests',
                    'count': pending_warehouse_approvals,
                })
            
            pending_stocktaking_approvals = inventory_models.StocktakingRecord.objects.filter(
                company_id=company_id,
                approval_status='pending',
                approver=request.user,
                is_locked=0,
                is_enabled=1
            ).count()
            
            if pending_stocktaking_approvals > 0:
                notifications.append({
                    'type': 'approval_pending',
                    'message': f'{pending_stocktaking_approvals} سند شمارش در انتظار تایید',
                    'url': 'inventory:stocktaking_records',
                    'count': pending_stocktaking_approvals,
                })
            
            # 2. User's requests that were approved (recently - last 7 days)
            # Get current person for requested_by/requester lookup
            current_person = Person.objects.filter(
                user=request.user,
                company_id=company_id,
                is_enabled=1
            ).first()
            
            if current_person:
                week_ago = timezone.now() - timezone.timedelta(days=7)
                
                approved_purchase_requests = inventory_models.PurchaseRequest.objects.filter(
                    company_id=company_id,
                    requested_by=current_person,
                    status=inventory_models.PurchaseRequest.Status.APPROVED,
                    approved_at__gte=week_ago,
                    is_enabled=1
                ).count()
                
                if approved_purchase_requests > 0:
                    notifications.append({
                        'type': 'approved',
                        'message': f'{approved_purchase_requests} درخواست خرید شما تایید شد',
                        'url': 'inventory:purchase_requests',
                        'count': approved_purchase_requests,
                    })
                
                approved_warehouse_requests = inventory_models.WarehouseRequest.objects.filter(
                    company_id=company_id,
                    requester=current_person,
                    request_status='approved',
                    approved_at__gte=week_ago,
                    is_enabled=1
                ).count()
                
                if approved_warehouse_requests > 0:
                    notifications.append({
                        'type': 'approved',
                        'message': f'{approved_warehouse_requests} درخواست انبار شما تایید شد',
                        'url': 'inventory:warehouse_requests',
                        'count': approved_warehouse_requests,
                    })
            
            context['notifications'] = notifications
            context['notification_count'] = sum(n['count'] for n in notifications)

    return context

