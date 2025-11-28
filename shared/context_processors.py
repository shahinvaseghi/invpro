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
            
            # Save to session and mark as modified
            if context['active_company']:
                request.session['active_company_id'] = context['active_company'].id
                request.session.modified = True  # Ensure session is saved

        from shared.utils.permissions import get_user_feature_permissions

        company_id = context['active_company'].id if context['active_company'] else None
        context['user_feature_permissions'] = get_user_feature_permissions(request.user, company_id)
        
        # Calculate notifications
        context['notifications'] = []
        context['notification_count'] = 0
        
        if company_id:
            from inventory import models as inventory_models
            from django.utils import timezone
            from shared.utils.notifications import get_or_create_notification, get_unread_notifications, get_unread_notification_count
            
            company = context['active_company']
            
            # Get sent email notifications from session (to avoid duplicate emails)
            sent_email_notifications = request.session.get('sent_email_notifications', set())
            if not isinstance(sent_email_notifications, set):
                sent_email_notifications = set()
            
            # 1. Requests awaiting approval (user is approver)
            pending_purchase_approvals = inventory_models.PurchaseRequest.objects.filter(
                company_id=company_id,
                status=inventory_models.PurchaseRequest.Status.DRAFT,
                approver=request.user,
                is_enabled=1
            ).count()
            
            notification_key = f'approval_pending_purchase_{company_id}'
            if pending_purchase_approvals > 0:
                get_or_create_notification(
                    user=request.user,
                    company=company,
                    notification_type='approval_pending',
                    notification_key=notification_key,
                    message=f'{pending_purchase_approvals} درخواست خرید در انتظار تایید',
                    url_name='inventory:purchase_requests',
                    count=pending_purchase_approvals,
                )
                # Send email notification (only if not already sent)
                if notification_key not in sent_email_notifications:
                    try:
                        from shared.utils.email import send_notification_email
                        from django.urls import reverse
                        notification_url = request.build_absolute_uri(reverse('inventory:purchase_requests'))
                        if send_notification_email(
                            notification_type='approval_pending',
                            notification_message=f'{pending_purchase_approvals} درخواست خرید در انتظار تایید',
                            recipient_user=request.user,
                            notification_url=notification_url,
                            company_name=context['active_company'].display_name if context['active_company'] else None,
                        ):
                            sent_email_notifications.add(notification_key)
                            request.session['sent_email_notifications'] = list(sent_email_notifications)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error sending email notification: {e}", exc_info=True)
            
            pending_warehouse_approvals = inventory_models.WarehouseRequest.objects.filter(
                company_id=company_id,
                request_status='draft',
                approver=request.user,
                is_enabled=1
            ).count()
            
            notification_key = f'approval_pending_warehouse_{company_id}'
            if pending_warehouse_approvals > 0:
                get_or_create_notification(
                    user=request.user,
                    company=company,
                    notification_type='approval_pending',
                    notification_key=notification_key,
                    message=f'{pending_warehouse_approvals} درخواست انبار در انتظار تایید',
                    url_name='inventory:warehouse_requests',
                    count=pending_warehouse_approvals,
                )
                # Send email notification (only if not already sent)
                if notification_key not in sent_email_notifications:
                    try:
                        from shared.utils.email import send_notification_email
                        from django.urls import reverse
                        notification_url = request.build_absolute_uri(reverse('inventory:warehouse_requests'))
                        if send_notification_email(
                            notification_type='approval_pending',
                            notification_message=f'{pending_warehouse_approvals} درخواست انبار در انتظار تایید',
                            recipient_user=request.user,
                            notification_url=notification_url,
                            company_name=context['active_company'].display_name if context['active_company'] else None,
                        ):
                            sent_email_notifications.add(notification_key)
                            request.session['sent_email_notifications'] = list(sent_email_notifications)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error sending email notification: {e}", exc_info=True)
            
            pending_stocktaking_approvals = inventory_models.StocktakingRecord.objects.filter(
                company_id=company_id,
                approval_status='pending',
                approver=request.user,
                is_locked=0,
                is_enabled=1
            ).count()
            
            notification_key = f'approval_pending_stocktaking_{company_id}'
            if pending_stocktaking_approvals > 0:
                get_or_create_notification(
                    user=request.user,
                    company=company,
                    notification_type='approval_pending',
                    notification_key=notification_key,
                    message=f'{pending_stocktaking_approvals} سند شمارش در انتظار تایید',
                    url_name='inventory:stocktaking_records',
                    count=pending_stocktaking_approvals,
                )
                # Send email notification (only if not already sent)
                if notification_key not in sent_email_notifications:
                    try:
                        from shared.utils.email import send_notification_email
                        from django.urls import reverse
                        notification_url = request.build_absolute_uri(reverse('inventory:stocktaking_records'))
                        if send_notification_email(
                            notification_type='approval_pending',
                            notification_message=f'{pending_stocktaking_approvals} سند شمارش در انتظار تایید',
                            recipient_user=request.user,
                            notification_url=notification_url,
                            company_name=context['active_company'].display_name if context['active_company'] else None,
                        ):
                            sent_email_notifications.add(notification_key)
                            request.session['sent_email_notifications'] = list(sent_email_notifications)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error sending email notification: {e}", exc_info=True)
            
            # 2. User's requests that were approved (recently - last 7 days)
            week_ago = timezone.now() - timezone.timedelta(days=7)
            
            approved_purchase_requests = inventory_models.PurchaseRequest.objects.filter(
                company_id=company_id,
                requested_by=request.user,
                status=inventory_models.PurchaseRequest.Status.APPROVED,
                approved_at__gte=week_ago,
                is_enabled=1
            ).count()
            
            notification_key = f'approved_purchase_{company_id}'
            if approved_purchase_requests > 0:
                get_or_create_notification(
                    user=request.user,
                    company=company,
                    notification_type='approved',
                    notification_key=notification_key,
                    message=f'{approved_purchase_requests} درخواست خرید شما تایید شد',
                    url_name='inventory:purchase_requests',
                    count=approved_purchase_requests,
                )
                # Send email notification (only if not already sent)
                if notification_key not in sent_email_notifications:
                    try:
                        from shared.utils.email import send_notification_email
                        from django.urls import reverse
                        notification_url = request.build_absolute_uri(reverse('inventory:purchase_requests'))
                        if send_notification_email(
                            notification_type='approved',
                            notification_message=f'{approved_purchase_requests} درخواست خرید شما تایید شد',
                            recipient_user=request.user,
                            notification_url=notification_url,
                            company_name=context['active_company'].display_name if context['active_company'] else None,
                        ):
                            sent_email_notifications.add(notification_key)
                            request.session['sent_email_notifications'] = list(sent_email_notifications)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error sending email notification: {e}", exc_info=True)
            
            approved_warehouse_requests = inventory_models.WarehouseRequest.objects.filter(
                company_id=company_id,
                requester=request.user,
                request_status='approved',
                approved_at__gte=week_ago,
                is_enabled=1
            ).count()
            
            notification_key = f'approved_warehouse_{company_id}'
            if approved_warehouse_requests > 0:
                get_or_create_notification(
                    user=request.user,
                    company=company,
                    notification_type='approved',
                    notification_key=notification_key,
                    message=f'{approved_warehouse_requests} درخواست انبار شما تایید شد',
                    url_name='inventory:warehouse_requests',
                    count=approved_warehouse_requests,
                )
                # Send email notification (only if not already sent)
                if notification_key not in sent_email_notifications:
                    try:
                        from shared.utils.email import send_notification_email
                        from django.urls import reverse
                        notification_url = request.build_absolute_uri(reverse('inventory:warehouse_requests'))
                        if send_notification_email(
                            notification_type='approved',
                            notification_message=f'{approved_warehouse_requests} درخواست انبار شما تایید شد',
                            recipient_user=request.user,
                            notification_url=notification_url,
                            company_name=context['active_company'].display_name if context['active_company'] else None,
                        ):
                            sent_email_notifications.add(notification_key)
                            request.session['sent_email_notifications'] = list(sent_email_notifications)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Error sending email notification: {e}", exc_info=True)
            
            # Get recent notifications from database (both read and unread)
            from shared.utils.notifications import get_recent_notifications
            context['notifications'] = get_recent_notifications(request.user, company_id, limit=10)
            context['notification_count'] = get_unread_notification_count(request.user, company_id)

    return context

