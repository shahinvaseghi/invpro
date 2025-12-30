"""
Context processors for accounting module.

Provides fiscal year-related context to all templates.
"""

def active_fiscal_year(request):
    """
    Add active fiscal year information to template context.
    
    Returns:
        dict: Context with active_fiscal_year and available_fiscal_years
    """
    context = {
        'active_fiscal_year': None,
        'available_fiscal_years': [],
    }
    
    if request.user.is_authenticated:
        active_company_id = request.session.get('active_company_id')
        
        if active_company_id:
            from accounting.models import FiscalYear
            from accounting.utils import get_available_fiscal_years
            
            # Get available fiscal years (those with documents or current)
            available_fiscal_years = get_available_fiscal_years(active_company_id)
            context['available_fiscal_years'] = list(available_fiscal_years)
            
            # Get active fiscal year from session
            active_fiscal_year_id = request.session.get('active_fiscal_year_id')
            
            if active_fiscal_year_id:
                try:
                    context['active_fiscal_year'] = FiscalYear.objects.get(
                        pk=active_fiscal_year_id,
                        company_id=active_company_id,
                        is_enabled=1
                    )
                except FiscalYear.DoesNotExist:
                    pass
            
            # If no active fiscal year set, use current fiscal year or first available
            if not context['active_fiscal_year']:
                # Try to use current fiscal year first
                current_fiscal_year = FiscalYear.objects.filter(
                    company_id=active_company_id,
                    is_current=1,
                    is_enabled=1
                ).first()
                
                if current_fiscal_year:
                    context['active_fiscal_year'] = current_fiscal_year
                elif context['available_fiscal_years']:
                    # Use first available fiscal year
                    context['active_fiscal_year'] = context['available_fiscal_years'][0]
                else:
                    # If no available fiscal years, try to get any enabled fiscal year
                    any_fiscal_year = FiscalYear.objects.filter(
                        company_id=active_company_id,
                        is_enabled=1
                    ).order_by('-fiscal_year_code').first()
                    if any_fiscal_year:
                        context['active_fiscal_year'] = any_fiscal_year
                    else:
                        # If no fiscal year exists at all, try to get or create a default current fiscal year
                        # This ensures the selector is always shown
                        from datetime import date
                        from jdatetime import datetime as jdatetime
                        
                        # Get current Jalali year
                        now = jdatetime.now()
                        current_jalali_year = now.year
                        
                        # Try to find or create a fiscal year for current year
                        default_fiscal_year = FiscalYear.objects.filter(
                            company_id=active_company_id,
                            fiscal_year_code=str(current_jalali_year),
                            is_enabled=1
                        ).first()
                        
                        if not default_fiscal_year:
                            # Create a default fiscal year if none exists
                            # Calculate start and end dates for current Jalali year
                            start_date = jdatetime(current_jalali_year, 1, 1).togregorian()
                            end_date = jdatetime(current_jalali_year, 12, 29).togregorian()
                            
                            default_fiscal_year = FiscalYear.objects.create(
                                company_id=active_company_id,
                                fiscal_year_code=str(current_jalali_year),
                                fiscal_year_name=f'سال مالی {current_jalali_year}',
                                start_date=start_date,
                                end_date=end_date,
                                is_current=1,
                                is_enabled=1
                            )
                        
                        context['active_fiscal_year'] = default_fiscal_year
                        # Add to available_fiscal_years if not already there
                        if default_fiscal_year not in context['available_fiscal_years']:
                            context['available_fiscal_years'] = [default_fiscal_year]
                
                # Save to session
                if context['active_fiscal_year']:
                    request.session['active_fiscal_year_id'] = context['active_fiscal_year'].id
                    request.session.modified = True
    
    return context

