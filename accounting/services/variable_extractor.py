"""
Variable extraction service.
This service extracts variables from trigger documents based on automation variable definitions.
"""
from typing import Any, Dict, List
from decimal import Decimal
from django.db.models import Sum, Count, Avg, Max, Min
from django.db.models.query import QuerySet

from accounting.models.automation import AutomationProcess, AutomationVariable


class VariableExtractor:
    """
    Service for extracting variables from trigger documents.
    
    Supports:
    - Direct field extraction
    - Related field extraction
    - Aggregated values (sum, count, avg, max, min)
    - Computed expressions
    """
    
    def extract_variables(
        self,
        process: AutomationProcess,
        trigger_document: Any
    ) -> Dict[str, Any]:
        """
        Extract all variables defined in the process from the trigger document.
        
        Args:
            process: The automation process
            trigger_document: The document that triggered the process
        
        Returns:
            Dictionary mapping variable names to their extracted values
        """
        variables = {}
        
        active_variables = process.variables.filter(is_active=True)
        
        for var in active_variables:
            try:
                value = self._extract_variable_value(var, trigger_document)
                variables[var.name] = value
            except Exception as e:
                # Use default value if extraction fails
                if var.default_value is not None:
                    variables[var.name] = var.default_value
                else:
                    # Re-raise if no default value
                    raise ValueError(f"Failed to extract variable {var.name}: {str(e)}")
        
        return variables
    
    def _extract_variable_value(
        self,
        variable: AutomationVariable,
        trigger_document: Any
    ) -> Any:
        """
        Extract a single variable value from the trigger document.
        
        Args:
            variable: The variable definition
            trigger_document: The trigger document
        
        Returns:
            The extracted value
        """
        if variable.source_type == 'field':
            return self._extract_field_value(variable, trigger_document)
        elif variable.source_type == 'related_field':
            return self._extract_related_field_value(variable, trigger_document)
        elif variable.source_type == 'aggregated':
            return self._extract_aggregated_value(variable, trigger_document)
        elif variable.source_type == 'computed':
            return self._extract_computed_value(variable, trigger_document)
        else:
            raise ValueError(f"Unknown source type: {variable.source_type}")
    
    def _extract_field_value(
        self,
        variable: AutomationVariable,
        trigger_document: Any
    ) -> Any:
        """Extract value from a direct field."""
        field_path = variable.field_path
        
        # Handle nested field paths (e.g., "customer.name")
        parts = field_path.split('.')
        value = trigger_document
        
        for part in parts:
            if value is None:
                return None
            value = getattr(value, part, None)
            
            # If it's a callable (like a property), call it
            if callable(value):
                value = value()
        
        return value
    
    def _extract_related_field_value(
        self,
        variable: AutomationVariable,
        trigger_document: Any
    ) -> Any:
        """Extract value from a related field (ForeignKey)."""
        field_path = variable.field_path
        
        # Get the related object first
        parts = field_path.split('.')
        related_obj = trigger_document
        
        for part in parts[:-1]:  # All parts except the last
            if related_obj is None:
                return None
            related_obj = getattr(related_obj, part, None)
        
        if related_obj is None:
            return None
        
        # Get the final field value
        final_field = parts[-1]
        value = getattr(related_obj, final_field, None)
        
        if callable(value):
            value = value()
        
        return value
    
    def _extract_aggregated_value(
        self,
        variable: AutomationVariable,
        trigger_document: Any
    ) -> Any:
        """Extract aggregated value from line items."""
        if variable.field_type != 'line_field':
            raise ValueError("Aggregated variables must be from line_field")
        
        # Get the lines (e.g., trigger_document.lines.all())
        field_path_parts = variable.field_path.split('.')
        lines_field = field_path_parts[0]  # e.g., 'lines'
        field_name = field_path_parts[1] if len(field_path_parts) > 1 else None
        
        lines = getattr(trigger_document, lines_field, None)
        
        if lines is None:
            return 0 if variable.aggregation_type in ['sum', 'count'] else None
        
        # If it's a manager, get queryset
        if hasattr(lines, 'all'):
            lines = lines.all()
        
        if not isinstance(lines, (list, QuerySet)):
            raise ValueError(f"Cannot aggregate from {type(lines)}")
        
        # Perform aggregation
        if variable.aggregation_type == 'sum':
            if field_name:
                return sum(getattr(line, field_name, 0) or 0 for line in lines)
            else:
                return len(lines)
        elif variable.aggregation_type == 'count':
            return len(lines)
        elif variable.aggregation_type == 'avg':
            if field_name:
                values = [getattr(line, field_name, 0) or 0 for line in lines]
                return sum(values) / len(values) if values else 0
            else:
                return 0
        elif variable.aggregation_type == 'max':
            if field_name:
                values = [getattr(line, field_name, None) for line in lines if getattr(line, field_name, None) is not None]
                return max(values) if values else None
            else:
                return None
        elif variable.aggregation_type == 'min':
            if field_name:
                values = [getattr(line, field_name, None) for line in lines if getattr(line, field_name, None) is not None]
                return min(values) if values else None
            else:
                return None
        else:
            raise ValueError(f"Unknown aggregation type: {variable.aggregation_type}")
    
    def _extract_computed_value(
        self,
        variable: AutomationVariable,
        trigger_document: Any
    ) -> Any:
        """Extract computed value using an expression."""
        # This is a placeholder - actual implementation would need
        # a safe expression evaluator
        # For now, we'll use a simple variable substitution
        
        expression = variable.computation_expression
        
        if not expression:
            raise ValueError("Computation expression is required for computed variables")
        
        # Simple variable substitution: {variable: var_name}
        # This is a basic implementation - a full implementation would
        # need a proper expression parser
        
        # For now, return the expression as-is
        # A proper implementation would parse and evaluate the expression
        return expression

