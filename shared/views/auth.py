"""
Authentication views for shared module.
"""
from typing import Optional
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.views.decorators.http import require_POST


@login_required
@require_POST
def set_active_company(request: HttpRequest) -> HttpResponseRedirect:
    """
    Set the active company for the current user session.
    
    Expects POST parameter 'company_id'.
    """
    company_id: Optional[str] = request.POST.get('company_id')
    
    if company_id:
        try:
            company_id_int: int = int(company_id)
            
            # Verify user has access to this company
            from shared.models import UserCompanyAccess
            has_access: bool = UserCompanyAccess.objects.filter(
                user=request.user,
                company_id=company_id_int,
                is_enabled=1
            ).exists()
            
            if has_access:
                request.session['active_company_id'] = company_id_int
        except (ValueError, TypeError):
            pass
    
    # Redirect back to the referring page or home
    return HttpResponseRedirect(request.POST.get('next', '/'))


def custom_login(request: HttpRequest):
    """
    Custom login view with beautiful UI.
    """
    if request.user.is_authenticated:
        return redirect('ui:dashboard')
    
    current_lang: str = get_language()
    
    if request.method == 'POST':
        username: Optional[str] = request.POST.get('username')
        password: Optional[str] = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            next_url: str = request.POST.get('next') or request.GET.get('next') or 'ui:dashboard'
            return redirect(next_url)
        else:
            return render(request, 'login.html', {
                'form': {'errors': True},
                'next': request.POST.get('next', ''),
                'LANGUAGE_CODE': current_lang
            })
    
    return render(request, 'login.html', {
        'next': request.GET.get('next', ''),
        'LANGUAGE_CODE': current_lang
    })


@login_required
@require_POST
def mark_notification_read(request: HttpRequest) -> HttpResponseRedirect:
    """
    Mark a notification as read in the session.
    
    Expects POST parameter 'notification_key'.
    """
    notification_key: Optional[str] = request.POST.get('notification_key')
    
    if notification_key:
        # Get read notifications from session
        read_notifications = request.session.get('read_notifications', set())
        if not isinstance(read_notifications, set):
            read_notifications = set(read_notifications)
        
        # Add this notification to read list
        read_notifications.add(notification_key)
        request.session['read_notifications'] = list(read_notifications)
        request.session.modified = True
    
    # Redirect back to the referring page or home
    return HttpResponseRedirect(request.POST.get('next', '/'))

