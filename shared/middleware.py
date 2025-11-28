"""
Middleware for shared module.
"""
from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.apps import apps


class EditLockCleanupMiddleware:
    """
    Middleware to clean up stale edit locks.
    
    This middleware runs on every request and clears edit locks
    that are older than 5 minutes (stale locks).
    """
    timeout_minutes = 5
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Clean up stale edit locks periodically
        # Use a simple time-based approach to avoid running on every request
        import time
        current_time = time.time()
        
        # Check if we need to run cleanup (every 60 seconds)
        if not hasattr(self, '_last_cleanup_time'):
            self._last_cleanup_time = 0
        
        if current_time - self._last_cleanup_time > 60:  # Run every 60 seconds
            self._cleanup_stale_locks()
            self._last_cleanup_time = current_time
        
        response = self.get_response(request)
        return response
    
    def _cleanup_stale_locks(self):
        """Clean up edit locks older than timeout."""
        timeout_threshold = timezone.now() - timedelta(minutes=self.timeout_minutes)
        
        # Get all installed apps and find models with EditableModel mixin
        from django.apps import apps
        
        cleaned_count = 0
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                # Check if model has editing_by field (indicates EditableModel mixin)
                if hasattr(model, 'editing_by') and hasattr(model, 'editing_started_at'):
                    try:
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
                            cleaned_count += count
                    except Exception:
                        # Ignore errors (model might not have these fields yet, or table doesn't exist)
                        pass
        
        if cleaned_count > 0:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Cleaned up {cleaned_count} stale edit locks")

