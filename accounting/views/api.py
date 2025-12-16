"""
API views for accounting module - AJAX endpoints for filtering accounts.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from accounting.models.accounts import Account, TafsiliSubAccountRelation, SubAccountGLAccountRelation


@login_required
@require_http_methods(["GET"])
def filter_sub_accounts_by_tafsili(request):
    """
    Filter sub accounts based on selected tafsili account.
    
    GET params:
        - tafsili_id: ID of selected tafsili account
        - company_id: Company ID (from session)
    
    Returns JSON list of sub accounts related to the tafsili account.
    """
    tafsili_id = request.GET.get('tafsili_id')
    company_id = request.session.get('active_company_id')
    
    if not tafsili_id or not company_id:
        return JsonResponse({'error': _('Missing required parameters')}, status=400)
    
    try:
        tafsili_account = Account.objects.get(
            pk=tafsili_id,
            company_id=company_id,
            account_level=3,
            is_enabled=1
        )
        
        # Get sub accounts related to this tafsili account
        relations = TafsiliSubAccountRelation.objects.filter(
            company_id=company_id,
            tafsili_account=tafsili_account,
            is_enabled=1
        ).select_related('sub_account')
        
        sub_accounts = []
        for relation in relations:
            sub_account = relation.sub_account
            if sub_account.is_enabled:
                sub_accounts.append({
                    'id': sub_account.pk,
                    'code': sub_account.account_code,
                    'name': sub_account.account_name,
                })
        
        return JsonResponse({'sub_accounts': sub_accounts})
    
    except Account.DoesNotExist:
        return JsonResponse({'error': _('Tafsili account not found')}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def filter_gl_accounts_by_sub(request):
    """
    Filter GL accounts based on selected sub account.
    
    GET params:
        - sub_id: ID of selected sub account
        - company_id: Company ID (from session)
    
    Returns JSON list of GL accounts related to the sub account.
    """
    sub_id = request.GET.get('sub_id')
    company_id = request.session.get('active_company_id')
    
    if not sub_id or not company_id:
        return JsonResponse({'error': _('Missing required parameters')}, status=400)
    
    try:
        sub_account = Account.objects.get(
            pk=sub_id,
            company_id=company_id,
            account_level=2,
            is_enabled=1
        )
        
        # Get GL accounts related to this sub account
        relations = SubAccountGLAccountRelation.objects.filter(
            company_id=company_id,
            sub_account=sub_account,
            is_enabled=1
        ).select_related('gl_account')
        
        gl_accounts = []
        for relation in relations:
            gl_account = relation.gl_account
            if gl_account.is_enabled:
                gl_accounts.append({
                    'id': gl_account.pk,
                    'code': gl_account.account_code,
                    'name': gl_account.account_name,
                })
        
        return JsonResponse({'gl_accounts': gl_accounts})
    
    except Account.DoesNotExist:
        return JsonResponse({'error': _('Sub account not found')}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

