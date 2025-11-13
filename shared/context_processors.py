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
    
    return context

