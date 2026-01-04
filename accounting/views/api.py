"""
API views for accounting module - AJAX endpoints for filtering accounts.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from accounting.models.accounts import Account, AccountGroup, SubAccountGLAccountRelation


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


@login_required
@require_http_methods(["GET"])
def filter_sub_accounts_by_gl(request):
    """
    Filter sub accounts based on selected GL account (reverse direction).
    
    GET params:
        - gl_id: ID of selected GL account
        - company_id: Company ID (from session)
    
    Returns JSON list of sub accounts related to the GL account.
    """
    gl_id = request.GET.get('gl_id')
    company_id = request.session.get('active_company_id')
    
    if not gl_id or not company_id:
        return JsonResponse({'error': _('Missing required parameters')}, status=400)
    
    try:
        gl_account = Account.objects.get(
            pk=gl_id,
            company_id=company_id,
            account_level=1,
            is_enabled=1
        )
        
        # Get sub accounts related to this GL account
        relations = SubAccountGLAccountRelation.objects.filter(
            company_id=company_id,
            gl_account=gl_account,
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
        return JsonResponse({'error': _('GL account not found')}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def filter_tafsili_accounts_by_sub(request):
    """
    Filter tafsili accounts based on selected sub account (reverse direction).
    
    GET params:
        - sub_id: ID of selected sub account
        - company_id: Company ID (from session)
    
    Returns JSON list of tafsili accounts related to the sub account.
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
        
        # Get tafsili accounts related to this sub account
        relations = TafsiliSubAccountRelation.objects.filter(
            company_id=company_id,
            sub_account=sub_account,
            is_enabled=1
        ).select_related('tafsili_account')
        
        tafsili_accounts = []
        for relation in relations:
            tafsili_account = relation.tafsili_account
            if tafsili_account.is_enabled:
                tafsili_accounts.append({
                    'id': tafsili_account.pk,
                    'code': tafsili_account.account_code,
                    'name': tafsili_account.account_name,
                })
        
        return JsonResponse({'tafsili_accounts': tafsili_accounts})
    
    except Account.DoesNotExist:
        return JsonResponse({'error': _('Sub account not found')}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def toggle_document_lock(request):
    """
    Toggle lock status of an accounting document.
    
    POST params:
        - document_id: ID of document to lock/unlock
    
    Returns JSON with success status and new lock state.
    """
    from accounting.models.documents import AccountingDocument
    
    document_id = request.POST.get('document_id')
    company_id = request.session.get('active_company_id')
    
    if not document_id or not company_id:
        return JsonResponse({'error': _('Missing required parameters')}, status=400)
    
    try:
        document = AccountingDocument.objects.get(
            pk=document_id,
            company_id=company_id
        )
        
        if document.is_locked:
            document.unlock(request.user)
            is_locked = False
            message = _('Document unlocked successfully')
        else:
            document.lock(request.user)
            is_locked = True
            message = _('Document locked successfully')
        
        return JsonResponse({
            'success': True,
            'is_locked': is_locked,
            'message': str(message)
        })
    
    except AccountingDocument.DoesNotExist:
        return JsonResponse({'error': _('Document not found')}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def import_account_tree(request):
    """
    فراخوانی درختچه حساب‌ها از فایل معیار
    
    POST params:
        - update_existing: (optional) اگر True باشد، حساب‌های موجود را update می‌کند (default: True)
        - skip_protected: (optional) اگر True باشد، حساب‌هایی که تفصیلی دارند را skip می‌کند (default: True)
    
    Returns JSON with success status and statistics.
    """
    from shared.mixins import FeaturePermissionRequiredMixin
    from accounting.services.account_tree_importer import AccountTreeImporter
    import json
    
    company_id = request.session.get('active_company_id')
    
    if not company_id:
        return JsonResponse({
            'success': False,
            'message': _('لطفاً ابتدا یک شرکت را انتخاب کنید')
        }, status=400)
    
    # بررسی مجوز
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': _('لطفاً ابتدا وارد سیستم شوید')
        }, status=403)
    
    # دریافت پارامترهای اختیاری
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        update_existing = data.get('update_existing', 'true').lower() == 'true'
        skip_protected = data.get('skip_protected', 'true').lower() == 'true'
    except:
        update_existing = True
        skip_protected = True
    
    try:
        importer = AccountTreeImporter(
            company_id=company_id,
            update_existing=update_existing,
            skip_protected=skip_protected
        )
        stats = importer.import_account_tree()
        
        total_created = (
            stats['groups_created'] +
            stats['gl_accounts_created'] +
            stats['sub_accounts_created']
        )
        
        total_updated = (
            stats.get('groups_updated', 0) +
            stats.get('gl_accounts_updated', 0) +
            stats.get('sub_accounts_updated', 0)
        )
        
        total_protected = (
            stats.get('gl_accounts_protected', 0) +
            stats.get('sub_accounts_protected', 0)
        )
        
        if total_created > 0 or total_updated > 0:
            message = _('درختچه حساب‌ها با موفقیت فراخوانی شد')
            if total_protected > 0:
                message += f' ({total_protected} حساب محافظت شده نادیده گرفته شد)'
        elif total_protected > 0:
            message = _('همه حساب‌ها قبلاً ایجاد شده‌اند یا محافظت شده‌اند')
        else:
            message = _('همه حساب‌ها قبلاً ایجاد شده‌اند')
        
        if stats.get('errors'):
            message += f' ({len(stats["errors"])} خطا)'
        
        return JsonResponse({
            'success': True,
            'message': str(message),
            'stats': stats
        })
    
    except FileNotFoundError as e:
        return JsonResponse({
            'success': False,
            'message': _('فایل معیار یافت نشد')
        }, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': _('خطا در فراخوانی درختچه حساب‌ها: {}').format(str(e))
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_account_tree(request):
    """
    دریافت ساختار درختی حساب‌ها برای نمایش tree view
    
    Returns JSON with tree structure:
    {
        'success': True,
        'tree': [
            {
                'code': '1',
                'name': 'دارایی های جاری',
                'gl_accounts': [
                    {
                        'id': 1,
                        'code': '11',
                        'name': 'موجودی نقدی',
                        'sub_accounts': [
                            {
                                'id': 2,
                                'code': '1101',
                                'name': 'صندوق',
                                'tafsili_accounts': [...]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """
    company_id = request.session.get('active_company_id')
    
    if not company_id:
        return JsonResponse({
            'success': False,
            'message': _('لطفاً ابتدا یک شرکت را انتخاب کنید')
        }, status=400)
    
    try:
        # دریافت گروه‌ها
        groups = AccountGroup.objects.filter(
            company_id=company_id,
            is_enabled=1
        ).order_by('group_code')
        
        tree = []
        
        for group in groups:
            # دریافت حساب‌های کل این گروه
            gl_accounts = Account.objects.filter(
                company_id=company_id,
                account_level=1,
                account_group=group,
                is_enabled=1
            ).order_by('account_code')
            
            gl_accounts_data = []
            for gl in gl_accounts:
                # دریافت معین‌های این حساب کل
                sub_accounts = Account.objects.filter(
                    company_id=company_id,
                    account_level=2,
                    parent_account=gl,
                    is_enabled=1
                ).order_by('account_code')
                
                sub_accounts_data = []
                for sub in sub_accounts:
                    # دریافت تفصیلی‌های این معین
                    tafsili_accounts = Account.objects.filter(
                        company_id=company_id,
                        account_level=3,
                        parent_account=sub,
                        is_enabled=1
                    ).order_by('account_code')
                    
                    tafsili_data = [
                        {
                            'id': t.id,
                            'code': t.account_code,
                            'name': t.account_name,
                        }
                        for t in tafsili_accounts
                    ]
                    
                    sub_accounts_data.append({
                        'id': sub.id,
                        'code': sub.account_code,
                        'name': sub.account_name,
                        'tafsili_accounts': tafsili_data,
                    })
                
                gl_accounts_data.append({
                    'id': gl.id,
                    'code': gl.account_code,
                    'name': gl.account_name,
                    'sub_accounts': sub_accounts_data,
                })
            
            tree.append({
                'code': group.group_code,
                'name': group.group_name,
                'gl_accounts': gl_accounts_data,
            })
        
        return JsonResponse({
            'success': True,
            'tree': tree
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': _('خطا در دریافت درختچه حساب‌ها: {}').format(str(e))
        }, status=500)


@require_http_methods(["GET"])
def get_gl_account_info(request):
    """
    Get GL account information for a selected sub account.

    GET params:
        - sub_account_id: ID of selected sub account
        - company_id: Company ID (from session or parameter)

    Returns JSON with GL account info:
    {
        'gl_account': {
            'id': 1,
            'code': '11',
            'name': 'موجودی نقدی'
        }
    }
    """
    sub_account_id = request.GET.get('sub_account_id')
    company_id = request.GET.get('company_id') or request.session.get('active_company_id')

    if not sub_account_id:
        return JsonResponse({'error': _('Missing sub_account_id parameter')}, status=400)

    if not company_id:
        # Try to get default company
        try:
            from shared.models import Company
            company = Company.objects.filter(is_enabled=1).first()
            if company:
                company_id = company.id
            else:
                return JsonResponse({'error': _('No active company found')}, status=400)
        except:
            return JsonResponse({'error': _('Company lookup failed')}, status=400)

    try:
        sub_account = Account.objects.get(
            pk=sub_account_id,
            company_id=company_id,
            account_level=2,
            is_enabled=1
        )

        # Get GL account through parent_account relationship
        if sub_account.parent_account and sub_account.parent_account.account_level == 1:
            gl_account = sub_account.parent_account
            return JsonResponse({
                'gl_account': {
                    'id': gl_account.pk,
                    'code': gl_account.account_code,
                    'name': gl_account.account_name,
                }
            })
        else:
            return JsonResponse({'gl_account': None})

    except Account.DoesNotExist:
        return JsonResponse({'error': _('Sub account not found')}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def get_allowed_tafsili_accounts(request):
    """
    Get allowed tafsili accounts for each level based on selected sub account.

    GET params:
        - sub_account_id: ID of selected sub account
        - company_id: Company ID (from session)

    Returns JSON with allowed tafsili accounts for each level:
    {
        'level_1': [
            {'type_name': 'نام بانک', 'accounts': [...]},
            {'type_name': 'نوع ارز', 'accounts': [...]}
        ],
        'level_2': [...],
        'level_3': [...]
    }
    """
    sub_account_id = request.GET.get('sub_account_id')
    company_id = request.session.get('active_company_id')

    if not sub_account_id or not company_id:
        return JsonResponse({'error': _('Missing required parameters')}, status=400)

    try:
        sub_account = Account.objects.get(
            pk=sub_account_id,
            company_id=company_id,
            account_level=2,
            is_enabled=1
        )

        # Load chart of accounts to get tafsili configuration for this sub account
        import json
        import os
        from django.conf import settings

        chart_path = os.path.join(settings.BASE_DIR, 'accounting', 'data', 'chart_of_accounts.json')
        with open(chart_path, 'r', encoding='utf-8') as f:
            chart_data = json.load(f)

        # Find the sub account configuration in chart
        sub_config = None
        for group in chart_data['groups']:
            for gl_account in group['gl_accounts']:
                for sub in gl_account['sub_accounts']:
                    if str(sub['code']) == str(sub_account.account_code):
                        sub_config = sub
                        break
                if sub_config:
                    break
            if sub_config:
                break

        if not sub_config or 'tafsili_levels' not in sub_config:
            # If no tafsili configuration, return empty result
            return JsonResponse({
                'level_1': [],
                'level_2': [],
                'level_3': []
            })

        result = {'level_1': [], 'level_2': [], 'level_3': []}

        # Process each level
        for level_config in sub_config['tafsili_levels']:
            level_num = level_config['level']
            level_key = f'level_{level_num}'

            for type_config in level_config['types']:
                type_name = type_config['type_name']

                # Get all accounts for this type
                allowed_codes = [acc['code'] for acc in type_config['accounts']]
                accounts = Account.objects.filter(
                    company_id=company_id,
                    account_level=3,
                    account_code__in=allowed_codes,
                    is_enabled=1
                ).order_by('account_code')

                accounts_data = [
                    {
                        'id': acc.pk,
                        'code': acc.account_code,
                        'name': acc.account_name
                    }
                    for acc in accounts
                ]

                result[level_key].append({
                    'type_name': type_name,
                    'accounts': accounts_data
                })

        return JsonResponse(result)

    except Account.DoesNotExist:
        return JsonResponse({'error': _('Sub account not found')}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
