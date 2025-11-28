"""
Management command to clear all stale edit locks.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.apps import apps


class Command(BaseCommand):
    help = 'Clear all stale edit locks (older than 5 minutes)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all edit locks (not just stale ones)',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=5,
            help='Timeout in minutes (default: 5)',
        )

    def handle(self, *args, **options):
        clear_all = options['all']
        timeout_minutes = options['timeout']
        
        if clear_all:
            timeout_threshold = timezone.now()
            self.stdout.write(self.style.WARNING('Clearing ALL edit locks...'))
        else:
            timeout_threshold = timezone.now() - timedelta(minutes=timeout_minutes)
            self.stdout.write(f'Clearing edit locks older than {timeout_minutes} minutes...')
        
        total_cleaned = 0
        
        # Get all installed apps and find models with EditableModel mixin
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                # Check if model has editing_by field (indicates EditableModel mixin)
                if hasattr(model, 'editing_by') and hasattr(model, 'editing_started_at'):
                    try:
                        if clear_all:
                            count = model.objects.filter(
                                editing_by__isnull=False
                            ).update(
                                editing_by=None,
                                editing_started_at=None,
                                editing_session_key=''
                            )
                        else:
                            count = model.objects.filter(
                                editing_by__isnull=False,
                                editing_started_at__isnull=False,
                                editing_started_at__lt=timeout_threshold
                            ).update(
                                editing_by=None,
                                editing_started_at=None,
                                editing_session_key=''
                            )
                        
                        if count > 0:
                            total_cleaned += count
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Cleared {count} edit locks from {model.__name__}'
                                )
                            )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error clearing locks for {model.__name__}: {e}'
                            )
                        )
        
        if total_cleaned > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nTotal: {total_cleaned} edit locks cleared.'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('No edit locks to clear.'))

