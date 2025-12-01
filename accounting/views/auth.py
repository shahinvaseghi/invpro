"""
Authentication views for accounting module.
"""
from typing import Optional
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpRequest
from django.views.decorators.http import require_POST


@login_required
@require_POST
def set_active_fiscal_year(request: HttpRequest) -> HttpResponseRedirect:
    """
    Set the active fiscal year for the current user session.
    
    Expects POST parameter 'fiscal_year_id'.
    """
    fiscal_year_id: Optional[str] = request.POST.get('fiscal_year_id')
    active_company_id = request.session.get('active_company_id')
    
    if fiscal_year_id and active_company_id:
        try:
            fiscal_year_id_int: int = int(fiscal_year_id)
            
            # Verify fiscal year belongs to active company
            from accounting.models import FiscalYear
            fiscal_year = FiscalYear.objects.filter(
                pk=fiscal_year_id_int,
                company_id=active_company_id,
                is_enabled=1
            ).first()
            
            if fiscal_year:
                request.session['active_fiscal_year_id'] = fiscal_year_id_int
        except (ValueError, TypeError):
            pass
    
    # Redirect back to the referring page or home
    return HttpResponseRedirect(request.POST.get('next', '/'))

