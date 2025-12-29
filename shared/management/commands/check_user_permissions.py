"""
Management command to check user permissions.
Usage: python manage.py check_user_permissions <username> [company_id]
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from shared.models import UserCompanyAccess, AccessLevel
from shared.utils.permissions import get_user_feature_permissions

User = get_user_model()


class Command(BaseCommand):
    help = 'Check feature permissions for a specific user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to check permissions for')
        parser.add_argument(
            '--company-id',
            type=int,
            help='Company ID (optional, will use user\'s default company if not provided)',
        )

    def handle(self, *args, **options):
        username = options['username']
        company_id = options.get('company_id')

        try:
            user = User.objects.get(username__icontains=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" not found')
        except User.MultipleObjectsReturned:
            users = User.objects.filter(username__icontains=username)
            self.stdout.write(self.style.WARNING(f'Multiple users found matching "{username}":'))
            for u in users:
                self.stdout.write(f'  - {u.username} ({u.get_full_name()})')
            raise CommandError('Please use a more specific username')

        self.stdout.write(self.style.SUCCESS(f'\nChecking permissions for: {user.username} ({user.get_full_name()})'))
        self.stdout.write(f'Is superuser: {user.is_superuser}')
        
        if user.is_superuser:
            self.stdout.write(self.style.WARNING('User is superuser - has all permissions'))
            return

        # Get company access
        if company_id:
            company_access = UserCompanyAccess.objects.filter(
                user=user,
                company_id=company_id,
                is_enabled=1
            ).select_related('company', 'access_level').first()
            
            if not company_access:
                self.stdout.write(self.style.WARNING(f'\nUser does not have access to company ID {company_id}'))
                # Show available companies
                all_accesses = UserCompanyAccess.objects.filter(user=user, is_enabled=1).select_related('company')
                if all_accesses:
                    self.stdout.write('\nAvailable companies:')
                    for access in all_accesses:
                        self.stdout.write(f'  - {access.company.display_name} (ID: {access.company.id})')
                return
            
            company = company_access.company
        else:
            # Use default company
            if user.default_company:
                company = user.default_company
                company_id = company.id
                self.stdout.write(f'\nUsing default company: {company.display_name} (ID: {company_id})')
            else:
                # Get first available company
                company_access = UserCompanyAccess.objects.filter(
                    user=user,
                    is_enabled=1
                ).select_related('company').first()
                
                if not company_access:
                    self.stdout.write(self.style.ERROR('\nUser has no company access'))
                    return
                
                company = company_access.company
                company_id = company.id
                self.stdout.write(f'\nUsing first available company: {company.display_name} (ID: {company_id})')

        # Get access levels for this user and company
        company_accesses = UserCompanyAccess.objects.filter(
            user=user,
            company_id=company_id,
            is_enabled=1
        ).select_related('access_level')
        
        self.stdout.write(f'\nAccess Levels:')
        for access in company_accesses:
            if access.access_level and access.access_level.is_enabled == 1:
                self.stdout.write(f'  - {access.access_level.name} (Code: {access.access_level.code})')

        # Get feature permissions
        permissions = get_user_feature_permissions(user, company_id)
        
        # Check procurement-related permissions
        procurement_permissions = {
            'procurement.orders.list': 'Purchase Orders',
            'procurement.invoices.purchase': 'Purchase Invoices',
            'procurement.services.request': 'Service Requests',
            'procurement.invoices.service': 'Service Invoices',
            'procurement.buyers': 'Buyers',
            'procurement.dashboard': 'Dashboard',
        }
        
        self.stdout.write(self.style.SUCCESS('\n=== Procurement Permissions ==='))
        for perm_code, perm_label in procurement_permissions.items():
            perm_key = perm_code.replace('.', '__')
            perm_state = permissions.get(perm_key)
            
            if perm_state and perm_state.can_view:
                self.stdout.write(self.style.SUCCESS(f'✓ {perm_label} ({perm_code}):'))
                self.stdout.write(f'    View scope: {perm_state.view_scope}')
                if perm_state.actions:
                    actions_list = [k for k, v in perm_state.actions.items() if v]
                    if actions_list:
                        self.stdout.write(f'    Actions: {", ".join(actions_list)}')
            else:
                self.stdout.write(self.style.ERROR(f'✗ {perm_label} ({perm_code}): No permission'))

        # Show all permissions (optional, for debugging)
        self.stdout.write(self.style.SUCCESS('\n=== All Permissions ==='))
        procurement_features = [k for k in permissions.keys() if 'procurement' in k]
        for perm_key in sorted(procurement_features):
            perm_state = permissions[perm_key]
            perm_code = perm_key.replace('__', '.')
            if perm_state.can_view:
                self.stdout.write(f'{perm_code}: {perm_state.view_scope}')

