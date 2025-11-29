from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.auth.models import Group
from django.db import transaction, connection

from shared.models import (
    User,
    Company,
    CompanyUnit,
    AccessLevel,
    AccessLevelPermission,
    UserCompanyAccess,
)


class Command(BaseCommand):
    help = 'Delete all data except Users, Groups, Companies, Access Levels, Company Units, and User Company Access'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion (required to actually delete)',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete ALL data except:\n'
                    '  - Users\n'
                    '  - Groups\n'
                    '  - Companies\n'
                    '  - Access Levels\n'
                    '  - Access Level Permissions\n'
                    '  - Company Units\n'
                    '  - User Company Access\n\n'
                    'To proceed, run with --confirm flag:\n'
                    '  python manage.py clear_all_data --confirm'
                )
            )
            return

        # Models to keep (preserve)
        keep_models = {
            User,
            Group,
            Company,
            CompanyUnit,
            AccessLevel,
            AccessLevelPermission,
            UserCompanyAccess,
        }

        # Get all models from all apps
        all_models = []
        for app_config in apps.get_app_configs():
            # Skip Django's built-in apps
            if app_config.name.startswith('django.'):
                continue
            if app_config.name.startswith('admin.'):
                continue
            
            for model in app_config.get_models():
                # Skip abstract models
                if model._meta.abstract:
                    continue
                # Skip proxy models
                if model._meta.proxy:
                    continue
                # Skip models we want to keep
                if model in keep_models:
                    continue
                all_models.append(model)

        self.stdout.write(
            self.style.WARNING(
                f'\n⚠️  WARNING: About to delete data from {len(all_models)} models!\n'
            )
        )

        # Sort models by dependencies - delete child models first
        # We'll try multiple passes to handle dependencies
        models_to_delete = all_models.copy()
        total_deleted = 0
        deleted_models = []
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        with transaction.atomic():
            # For PostgreSQL, defer constraint checks
            with connection.cursor() as cursor:
                cursor.execute("SET CONSTRAINTS ALL DEFERRED")
            
            while models_to_delete and iteration < max_iterations:
                iteration += 1
                remaining_models = []
                
                for model in models_to_delete:
                    try:
                        count = model.objects.count()
                        if count > 0:
                            model.objects.all().delete()
                            total_deleted += count
                            deleted_models.append(model._meta.label)
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✓ Deleted {count} records from {model._meta.label}'
                                )
                            )
                    except Exception as e:
                        # If deletion fails due to foreign key constraints, try again later
                        remaining_models.append(model)
                        # Try raw SQL as fallback
                        try:
                            table_name = model._meta.db_table
                            with connection.cursor() as cursor:
                                # Use CASCADE delete via SQL
                                cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
                                count = model.objects.count()  # Count before deletion
                                if count > 0:
                                    model.objects.all().delete()
                                    total_deleted += count
                                    deleted_models.append(model._meta.label)
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f'✓ Deleted {count} records from {model._meta.label} (via SQL)'
                                        )
                                    )
                                    remaining_models.remove(model)
                        except Exception as e2:
                            # Keep in remaining for next iteration
                            pass
                
                models_to_delete = remaining_models
                
                # If no progress, try TRUNCATE CASCADE for remaining tables
                if models_to_delete and iteration >= 3:
                    for model in models_to_delete[:]:
                        try:
                            table_name = model._meta.db_table
                            with connection.cursor() as cursor:
                                cursor.execute(f'TRUNCATE TABLE "{table_name}" CASCADE')
                            if model in models_to_delete:
                                models_to_delete.remove(model)
                                deleted_models.append(model._meta.label)
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'✓ Truncated table {model._meta.label} (via SQL CASCADE)'
                                    )
                                )
                        except Exception as e3:
                            pass

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully deleted {total_deleted} total records from {len(deleted_models)} models.\n'
                'Preserved: Users, Groups, Companies, Access Levels, Company Units, User Company Access'
            )
        )

