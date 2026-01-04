"""
Management command برای خالی کردن دیتابیس از گروه‌ها، حساب‌های کل و معین

استفاده:
    python manage.py clear_account_tree --company-id=1
    python manage.py clear_account_tree --company-id=1 --force  # حذف همه حتی با تفصیلی
    python manage.py clear_account_tree --all  # حذف از همه شرکت‌ها
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from accounting.models.accounts import AccountGroup, Account
from accounting.models.accounts import TafsiliSubAccountRelation, SubAccountGLAccountRelation
from shared.models import Company


class Command(BaseCommand):
    help = 'خالی کردن دیتابیس از گروه‌ها، حساب‌های کل و معین'

    def add_arguments(self, parser):
        parser.add_argument(
            '--company-id',
            type=int,
            help='شناسه شرکت (اگر مشخص نشود، از همه شرکت‌ها حذف می‌شود)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='حذف از همه شرکت‌ها',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='حذف همه حساب‌ها حتی آنهایی که تفصیلی دارند (خطرناک!)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='نمایش تعداد حساب‌هایی که حذف می‌شوند بدون حذف واقعی',
        )

    def handle(self, *args, **options):
        company_id = options.get('company_id')
        all_companies = options.get('all', False)
        force = options.get('force', False)
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('*** حالت DRY RUN - هیچ تغییری اعمال نمی‌شود ***\n'))

        # تعیین شرکت‌ها
        if company_id:
            try:
                company = Company.objects.get(pk=company_id)
                companies = [company]
            except Company.DoesNotExist:
                raise CommandError(f'شرکت با شناسه {company_id} یافت نشد')
        elif all_companies:
            companies = list(Company.objects.all())
        else:
            raise CommandError('لطفاً --company-id یا --all را مشخص کنید')

        if not companies:
            raise CommandError('هیچ شرکتی یافت نشد')

        total_groups = 0
        total_gl_accounts = 0
        total_sub_accounts = 0
        total_protected_gl = 0
        total_protected_sub = 0

        for company in companies:
            self.stdout.write(f'\nشرکت: {company.display_name} (ID: {company.id})')
            self.stdout.write('=' * 50)

            with transaction.atomic():
                # شمارش و حذف حساب‌های معین
                sub_accounts = Account.objects.filter(
                    company_id=company.id,
                    account_level=2
                )
                
                protected_sub = 0
                deletable_sub = 0
                
                for sub_account in sub_accounts:
                    has_tafsili = TafsiliSubAccountRelation.objects.filter(
                        company_id=company.id,
                        sub_account=sub_account,
                        is_enabled=1
                    ).exists()
                    
                    if has_tafsili and not force:
                        protected_sub += 1
                    else:
                        deletable_sub += 1
                        if not dry_run:
                            sub_account.delete()
                
                total_sub_accounts += deletable_sub
                total_protected_sub += protected_sub
                
                self.stdout.write(f'  حساب‌های معین: {deletable_sub} حذف شد، {protected_sub} محافظت شده')

                # شمارش و حذف حساب‌های کل
                gl_accounts = Account.objects.filter(
                    company_id=company.id,
                    account_level=1
                )
                
                protected_gl = 0
                deletable_gl = 0
                
                for gl_account in gl_accounts:
                    has_children = gl_account.child_accounts.filter(is_enabled=1).exists()
                    
                    if has_children and not force:
                        protected_gl += 1
                    else:
                        deletable_gl += 1
                        if not dry_run:
                            gl_account.delete()
                
                total_gl_accounts += deletable_gl
                total_protected_gl += protected_gl
                
                self.stdout.write(f'  حساب‌های کل: {deletable_gl} حذف شد، {protected_gl} محافظت شده')

                # حذف گروه‌ها
                groups = AccountGroup.objects.filter(company_id=company.id)
                groups_count = groups.count()
                total_groups += groups_count
                
                if not dry_run:
                    groups.delete()
                
                self.stdout.write(f'  گروه‌ها: {groups_count} حذف شد')

        # خلاصه
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS('\nخلاصه:'))
        self.stdout.write(f'  گروه‌ها: {total_groups}')
        self.stdout.write(f'  حساب‌های کل: {total_gl_accounts} (محافظت شده: {total_protected_gl})')
        self.stdout.write(f'  حساب‌های معین: {total_sub_accounts} (محافظت شده: {total_protected_sub})')
        
        if total_protected_gl > 0 or total_protected_sub > 0:
            self.stdout.write(self.style.WARNING(
                f'\nتوجه: {total_protected_gl + total_protected_sub} حساب محافظت شده حذف نشدند.'
            ))
            self.stdout.write(self.style.WARNING(
                'برای حذف همه حساب‌ها (حتی با تفصیلی) از --force استفاده کنید.'
            ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n*** این یک DRY RUN بود - هیچ تغییری اعمال نشد ***'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ عملیات با موفقیت انجام شد'))

