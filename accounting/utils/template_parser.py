"""
Template parser for variable substitution in automation expressions.
"""
import re
from typing import Any, Dict


class TemplateParser:
    """
    Parser for template strings with variable substitution.
    
    Supports syntax: {variable: variable_name}
    """
    
    VARIABLE_PATTERN = re.compile(r'\{variable:\s*(\w+)(?:\s*\|\s*default:\s*"([^"]+)")?\}')
    
    def parse(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Parse a template string and substitute variables.
        
        Args:
            template: Template string with {variable: var_name} syntax
            variables: Dictionary of variable values
        
        Returns:
            Parsed string with variables substituted
        """
        def replace_match(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else None
            
            value = variables.get(var_name)
            
            if value is None:
                return default_value if default_value else f"{{variable: {var_name}}}"
            
            return str(value)
        
        return self.VARIABLE_PATTERN.sub(replace_match, template)

