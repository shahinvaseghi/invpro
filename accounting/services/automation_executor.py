"""
Automation execution engine.
This service handles the execution of automation processes.
"""
from typing import Any, Dict, Optional
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError

from accounting.models.automation import (
    AutomationProcess,
    AutomationExecutionLog,
    AutomationDocumentStep,
    AutomationDocumentLine,
    AutomationDocumentApproval,
)
from accounting.services.variable_extractor import VariableExtractor
from accounting.services.condition_evaluator import ConditionEvaluator
from accounting.services.document_creator import DocumentCreator


class AutomationExecutor:
    """
    Main executor for automation processes.
    
    This class orchestrates the execution of automation processes:
    1. Evaluates conditions
    2. Extracts variables
    3. Creates documents according to steps
    4. Handles approvals
    """
    
    def __init__(self):
        self.variable_extractor = VariableExtractor()
        self.condition_evaluator = ConditionEvaluator()
        self.document_creator = DocumentCreator()
    
    def execute_process(
        self,
        process: AutomationProcess,
        trigger_document: Any,
        dry_run: bool = False
    ) -> Optional[AutomationExecutionLog]:
        """
        Execute an automation process for a trigger document.
        
        Args:
            process: The automation process to execute
            trigger_document: The document that triggered this process
            dry_run: If True, don't actually create documents, just return preview
        
        Returns:
            AutomationExecutionLog instance or None if dry_run
        """
        # Create execution log
        execution_log = AutomationExecutionLog.objects.create(
            process=process,
            trigger_document_id=trigger_document.id,
            trigger_document_type=f"{trigger_document._meta.app_label}.{trigger_document._meta.model_name}",
            status='in_progress',
            executed_at=timezone.now(),
            company=process.company,
            created_by=getattr(trigger_document, 'created_by', None),
        )
        
        try:
            # Step 1: Evaluate conditions
            conditions_met = self.condition_evaluator.evaluate_conditions(
                process,
                trigger_document
            )
            
            if not conditions_met:
                execution_log.status = 'cancelled'
                execution_log.completed_at = timezone.now()
                execution_log.error_message = "Conditions not met"
                execution_log.save()
                return execution_log
            
            # Step 2: Extract variables
            variables = self.variable_extractor.extract_variables(
                process,
                trigger_document
            )
            
            execution_log.execution_data = {
                'variables': variables,
                'conditions_evaluated': True,
            }
            execution_log.save()
            
            if dry_run:
                # Return preview without creating documents
                return execution_log
            
            # Step 3: Execute document steps
            created_documents = []
            steps = process.document_steps.filter(
                is_active=True
            ).order_by('step_number')
            
            for step in steps:
                # Check execution condition for this step
                if step.execution_condition:
                    step_condition_met = self.condition_evaluator.evaluate_step_condition(
                        step,
                        variables
                    )
                    if not step_condition_met:
                        continue
                
                # Check if we need to wait for previous approval
                if step.wait_for_previous_approval and created_documents:
                    # Check if previous document is approved
                    previous_step = steps.filter(
                        step_number__lt=step.step_number
                    ).order_by('-step_number').first()
                    
                    if previous_step:
                        previous_approval = AutomationDocumentApproval.objects.filter(
                            execution_log=execution_log,
                            step=previous_step,
                            status='approved'
                        ).first()
                        
                        if not previous_approval:
                            # Wait for approval
                            execution_log.status = 'pending'
                            execution_log.save()
                            return execution_log
                
                # Create document for this step
                try:
                    created_doc = self.document_creator.create_document(
                        step,
                        variables,
                        trigger_document,
                        execution_log
                    )
                    
                    if created_doc:
                        created_documents.append({
                            'step_id': step.id,
                            'step_number': step.step_number,
                            'document_type': step.document_type,
                            'document_id': created_doc.id,
                            'status': 'created',
                            'requires_approval': step.requires_approval,
                            'created_at': timezone.now().isoformat(),
                        })
                        
                        # Create approval record if needed
                        if step.requires_approval == 'manual':
                            AutomationDocumentApproval.objects.create(
                                execution_log=execution_log,
                                step=step,
                                document_id=created_doc.id,
                                document_type=step.document_type,
                                status='pending',
                                company=process.company,
                            )
                        elif step.requires_approval == 'auto':
                            # Auto-approve
                            AutomationDocumentApproval.objects.create(
                                execution_log=execution_log,
                                step=step,
                                document_id=created_doc.id,
                                document_type=step.document_type,
                                status='approved',
                                approved_by=getattr(trigger_document, 'created_by', None),
                                approved_at=timezone.now(),
                                company=process.company,
                            )
                
                except Exception as e:
                    # Log error but continue with next step
                    execution_log.error_message = f"Error in step {step.step_number}: {str(e)}"
                    execution_log.status = 'partial'
                    execution_log.save()
                    continue
            
            # Update execution log
            execution_log.created_documents = created_documents
            if execution_log.status == 'in_progress':
                execution_log.status = 'success' if created_documents else 'failed'
            execution_log.completed_at = timezone.now()
            execution_log.save()
            
            return execution_log
        
        except Exception as e:
            # Handle any unexpected errors
            execution_log.status = 'failed'
            execution_log.error_message = str(e)
            execution_log.completed_at = timezone.now()
            execution_log.save()
            raise

