"""
Condition evaluation service.
This service evaluates automation conditions against trigger documents.
"""
from typing import Any, Dict, List
from decimal import Decimal
from django.db.models import Q
from django.contrib.auth.models import User, Group

from accounting.models.automation import AutomationProcess, AutomationCondition, AutomationDocumentStep


class ConditionEvaluator:
    """
    Service for evaluating automation conditions.
    
    Supports:
    - Global filters (user, user_group, date, status)
    - Document-specific filters
    - Complex logical operators (AND/OR)
    - Hierarchy-based filters for tafsili accounts
    """
    
    def evaluate_conditions(
        self,
        process: AutomationProcess,
        trigger_document: Any
    ) -> bool:
        """
        Evaluate all conditions for a process against a trigger document.
        
        Args:
            process: The automation process
            trigger_document: The document to evaluate against
        
        Returns:
            True if all conditions are met, False otherwise
        """
        conditions = process.conditions.filter(is_active=True).order_by('sort_order')
        
        if not conditions.exists():
            # No conditions means always true
            return True
        
        # Evaluate conditions with logical operators
        result = None
        previous_operator = 'AND'  # Default to AND for first condition
        
        for condition in conditions:
            condition_result = self._evaluate_condition(condition, trigger_document)
            
            if result is None:
                # First condition
                result = condition_result
            else:
                # Combine with previous result using logical operator
                if previous_operator == 'AND':
                    result = result and condition_result
                elif previous_operator == 'OR':
                    result = result or condition_result
            
            previous_operator = condition.logical_operator
        
        return result if result is not None else True
    
    def _evaluate_condition(
        self,
        condition: AutomationCondition,
        trigger_document: Any
    ) -> bool:
        """
        Evaluate a single condition.
        
        Args:
            condition: The condition to evaluate
            trigger_document: The trigger document
        
        Returns:
            True if condition is met, False otherwise
        """
        if condition.filter_type == 'global':
            return self._evaluate_global_condition(condition, trigger_document)
        elif condition.filter_type == 'document_specific':
            return self._evaluate_document_specific_condition(condition, trigger_document)
        else:
            raise ValueError(f"Unknown filter type: {condition.filter_type}")
    
    def _evaluate_global_condition(
        self,
        condition: AutomationCondition,
        trigger_document: Any
    ) -> bool:
        """Evaluate a global condition."""
        if condition.filter_category == 'user':
            return self._evaluate_user_condition(condition, trigger_document)
        elif condition.filter_category == 'user_group':
            return self._evaluate_user_group_condition(condition, trigger_document)
        elif condition.filter_category == 'date':
            return self._evaluate_date_condition(condition, trigger_document)
        elif condition.filter_category == 'date_range':
            return self._evaluate_date_range_condition(condition, trigger_document)
        elif condition.filter_category == 'status':
            return self._evaluate_status_condition(condition, trigger_document)
        else:
            raise ValueError(f"Unknown global filter category: {condition.filter_category}")
    
    def _evaluate_user_condition(
        self,
        condition: AutomationCondition,
        trigger_document: Any
    ) -> bool:
        """Evaluate user-based condition."""
        created_by = getattr(trigger_document, 'created_by', None)
        if not created_by:
            return False
        
        if condition.operator == '==':
            user_ids = condition.value if isinstance(condition.value, list) else [condition.value]
            return created_by.id in user_ids
        else:
            raise ValueError(f"Unsupported operator for user condition: {condition.operator}")
    
    def _evaluate_user_group_condition(
        self,
        condition: AutomationCondition,
        trigger_document: Any
    ) -> bool:
        """Evaluate user group-based condition."""
        created_by = getattr(trigger_document, 'created_by', None)
        if not created_by:
            return False
        
        user_groups = created_by.groups.all()
        group_ids = condition.value if isinstance(condition.value, list) else [condition.value]
        
        if condition.operator == 'in':
            return user_groups.filter(id__in=group_ids).exists()
        else:
            raise ValueError(f"Unsupported operator for user_group condition: {condition.operator}")
    
    def _evaluate_date_condition(
        self,
        condition: AutomationCondition,
        trigger_document: Any
    ) -> bool:
        """Evaluate date-based condition."""
        # Try common date field names
        date_field = getattr(trigger_document, 'document_date', None) or \
                     getattr(trigger_document, 'date', None) or \
                     getattr(trigger_document, 'created_at', None)
        
        if not date_field:
            return False
        
        # Convert to date if datetime
        from datetime import date
        if hasattr(date_field, 'date'):
            date_field = date_field.date()
        
        condition_date = condition.value
        if isinstance(condition_date, str):
            from datetime import datetime
            condition_date = datetime.strptime(condition_date, '%Y-%m-%d').date()
        
        if condition.operator == '==':
            return date_field == condition_date
        elif condition.operator == '!=':
            return date_field != condition_date
        else:
            raise ValueError(f"Unsupported operator for date condition: {condition.operator}")
    
    def _evaluate_date_range_condition(
        self,
        condition: AutomationCondition,
        trigger_document: Any
    ) -> bool:
        """Evaluate date range condition."""
        # Try common date field names
        date_field = getattr(trigger_document, 'document_date', None) or \
                     getattr(trigger_document, 'date', None) or \
                     getattr(trigger_document, 'created_at', None)
        
        if not date_field:
            return False
        
        # Convert to date if datetime
        from datetime import date
        if hasattr(date_field, 'date'):
            date_field = date_field.date()
        
        if isinstance(condition.value, dict):
            start_date = condition.value.get('start')
            end_date = condition.value.get('end')
        elif isinstance(condition.value, list) and len(condition.value) == 2:
            start_date = condition.value[0]
            end_date = condition.value[1]
        else:
            raise ValueError("Date range condition value must be dict with 'start' and 'end' or list with 2 dates")
        
        # Convert strings to dates
        from datetime import datetime
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if condition.operator == 'between':
            return start_date <= date_field <= end_date
        elif condition.operator in ['>=', '<=']:
            if condition.operator == '>=':
                return date_field >= start_date
            else:
                return date_field <= end_date
        else:
            raise ValueError(f"Unsupported operator for date_range condition: {condition.operator}")
    
    def _evaluate_status_condition(
        self,
        condition: AutomationCondition,
        trigger_document: Any
    ) -> bool:
        """Evaluate status-based condition."""
        status = getattr(trigger_document, 'status', None)
        if status is None:
            return False
        
        if condition.operator == '==':
            return status == condition.value
        elif condition.operator == 'in':
            statuses = condition.value if isinstance(condition.value, list) else [condition.value]
            return status in statuses
        else:
            raise ValueError(f"Unsupported operator for status condition: {condition.operator}")
    
    def _evaluate_document_specific_condition(
        self,
        condition: AutomationCondition,
        trigger_document: Any
    ) -> bool:
        """Evaluate document-specific condition."""
        if not condition.field_name:
            raise ValueError("field_name is required for document-specific conditions")
        
        # Get field value from document
        field_value = getattr(trigger_document, condition.field_name, None)
        
        if field_value is None:
            # Check if operator allows None
            if condition.operator == 'is_null':
                return True
            elif condition.operator == 'is_not_null':
                return False
            else:
                return False
        
        # Handle hierarchy-based operators for tafsili accounts
        if condition.operator in ['hierarchy_level', 'hierarchy_parent', 'hierarchy_descendant']:
            return self._evaluate_hierarchy_condition(condition, field_value)
        
        # Handle standard operators
        condition_value = condition.value
        
        if condition.operator == '==':
            return field_value == condition_value
        elif condition.operator == '!=':
            return field_value != condition_value
        elif condition.operator == '>':
            return field_value > condition_value
        elif condition.operator == '<':
            return field_value < condition_value
        elif condition.operator == '>=':
            return field_value >= condition_value
        elif condition.operator == '<=':
            return field_value <= condition_value
        elif condition.operator == 'in':
            values = condition_value if isinstance(condition_value, list) else [condition_value]
            return field_value in values
        elif condition.operator == 'not_in':
            values = condition_value if isinstance(condition_value, list) else [condition_value]
            return field_value not in values
        elif condition.operator == 'contains':
            return str(condition_value) in str(field_value)
        elif condition.operator == 'starts_with':
            return str(field_value).startswith(str(condition_value))
        elif condition.operator == 'ends_with':
            return str(field_value).endswith(str(condition_value))
        elif condition.operator == 'is_null':
            return field_value is None
        elif condition.operator == 'is_not_null':
            return field_value is not None
        else:
            raise ValueError(f"Unsupported operator: {condition.operator}")
    
    def _evaluate_hierarchy_condition(
        self,
        condition: AutomationCondition,
        field_value: Any
    ) -> bool:
        """Evaluate hierarchy-based condition for tafsili accounts."""
        # This is a placeholder - actual implementation would need
        # to check the hierarchy structure
        # For now, we'll do a basic check
        
        if condition.operator == 'hierarchy_level':
            # Check if the tafsili account is at a specific hierarchy level
            level = condition.value
            if hasattr(field_value, 'hierarchy_level'):
                return field_value.hierarchy_level == level
            return False
        
        elif condition.operator == 'hierarchy_parent':
            # Check if the tafsili account is a child of a specific parent
            parent_id = condition.value
            if hasattr(field_value, 'parent_id'):
                return field_value.parent_id == parent_id
            return False
        
        elif condition.operator == 'hierarchy_descendant':
            # Check if the tafsili account is a descendant of a specific account
            ancestor_id = condition.value
            # This would require traversing the hierarchy tree
            # Placeholder implementation
            return False
        
        else:
            raise ValueError(f"Unsupported hierarchy operator: {condition.operator}")
    
    def evaluate_step_condition(
        self,
        step: AutomationDocumentStep,
        variables: Dict[str, Any]
    ) -> bool:
        """
        Evaluate execution condition for a document step.
        
        Args:
            step: The document step
            variables: Extracted variables
        
        Returns:
            True if step should execute, False otherwise
        """
        if not step.execution_condition:
            return True
        
        # This is a placeholder - actual implementation would need
        # to parse and evaluate the condition expression using variables
        # For now, we'll return True
        return True

