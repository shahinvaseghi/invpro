"""
Signal handlers for automation system.
These signals trigger automation processes when documents are created or updated.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from accounting.models.automation import AutomationProcess
from accounting.services.automation_executor import AutomationExecutor


@receiver(post_save, sender=None)
def trigger_automation_on_document_save(sender, instance, created, **kwargs):
    """
    Generic signal handler that checks if a saved document should trigger automation.
    
    This handler:
    1. Checks if the document model matches any active automation process
    2. Evaluates conditions for matching processes
    3. Executes automation if conditions are met
    
    Note: This is a generic handler. For better performance, you might want to
    register specific handlers for each document type.
    """
    # Skip if this is not a new document
    if not created:
        return
    
    # Skip if instance doesn't have company attribute (not a company-scoped model)
    if not hasattr(instance, 'company'):
        return
    
    # Get the model path (e.g., 'accounting.AccountingDocument')
    model_path = f"{sender._meta.app_label}.{sender._meta.model_name}"
    
    # Find active automation processes that match this model
    active_processes = AutomationProcess.objects.filter(
        trigger_model=model_path,
        is_active=True,
        company=instance.company
    )
    
    if not active_processes.exists():
        return
    
    # Execute automation for each matching process
    executor = AutomationExecutor()
    for process in active_processes:
        try:
            executor.execute_process(process, instance)
        except Exception as e:
            # Log error but don't break the document creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                f"Error executing automation process {process.id} for document {instance.id}: {str(e)}",
                exc_info=True
            )

