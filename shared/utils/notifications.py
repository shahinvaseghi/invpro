"""
Helper functions for notification management.
"""
from typing import Optional, Dict, Any
from django.utils import timezone
from django.db import models
from shared.models import Notification, Company


def get_or_create_notification(
    user,
    company: Optional[Company],
    notification_type: str,
    notification_key: str,
    message: str,
    url_name: str,
    count: int = 1,
) -> Notification:
    """
    Get or create a notification in the database.
    
    Args:
        user: User who should receive the notification
        company: Company context for the notification
        notification_type: Type of notification (e.g., 'approval_pending', 'approved')
        notification_key: Unique key for this notification
        message: Notification message text
        url_name: Django URL name to redirect to
        count: Number of items in this notification
    
    Returns:
        Notification instance
    """
    notification, created = Notification.objects.get_or_create(
        notification_key=notification_key,
        defaults={
            'user': user,
            'company': company,
            'notification_type': notification_type,
            'message': message,
            'url_name': url_name,
            'count': count,
            'is_read': 0,
            'created_by': user,
        }
    )
    
    # Update notification if it already exists and count/message changed
    if not created:
        if notification.message != message or notification.count != count:
            notification.message = message
            notification.count = count
            notification.edited_by = user
            notification.edited_at = timezone.now()
            notification.save(update_fields=['message', 'count', 'edited_by', 'edited_at'])
    
    return notification


def get_unread_notifications(user, company_id: Optional[int]) -> list:
    """
    Get unread notifications for a user in a company context.
    
    Args:
        user: User to get notifications for
        company_id: Company ID to filter notifications
    
    Returns:
        List of notification dicts for template context
    """
    queryset = Notification.objects.filter(
        user=user,
        is_read=0,
    ).order_by('-created_at')
    
    if company_id:
        queryset = queryset.filter(company_id=company_id)
    
    notifications = []
    for notification in queryset:
        notifications.append({
            'type': notification.notification_type,
            'key': notification.notification_key,
            'message': notification.message,
            'url': notification.url_name,
            'count': notification.count,
            'id': notification.id,
        })
    
    return notifications


def get_unread_notification_count(user, company_id: Optional[int]) -> int:
    """
    Get count of unread notifications for a user in a company context.
    
    Args:
        user: User to count notifications for
        company_id: Company ID to filter notifications
    
    Returns:
        Count of unread notifications
    """
    queryset = Notification.objects.filter(
        user=user,
        is_read=0,
    )
    
    if company_id:
        queryset = queryset.filter(company_id=company_id)
    
    from django.db.models import Sum
    result = queryset.aggregate(total_count=Sum('count'))
    return result['total_count'] or 0


def get_recent_notifications(user, company_id: Optional[int], limit: int = 10) -> list:
    """
    Get recent notifications (both read and unread) for a user in a company context.
    
    Args:
        user: User to get notifications for
        company_id: Company ID to filter notifications
        limit: Maximum number of notifications to return (default: 10)
    
    Returns:
        List of notification dicts for template context
    """
    queryset = Notification.objects.filter(
        user=user,
    )
    
    if company_id:
        queryset = queryset.filter(company_id=company_id)
    
    queryset = queryset.order_by('-created_at')[:limit]
    
    notifications = []
    for notification in queryset:
        notifications.append({
            'type': notification.notification_type,
            'key': notification.notification_key,
            'message': notification.message,
            'url': notification.url_name,
            'count': notification.count,
            'id': notification.id,
            'is_read': notification.is_read,
        })
    
    return notifications

