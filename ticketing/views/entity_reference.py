"""
API views for Entity Reference System.
These views provide data for the three-level Entity Reference UI:
1. Sections (from SectionRegistry)
2. Actions (from ActionRegistry for selected section)
3. Parameters (from parameter_schema for selected action)
4. Parameter values (dynamic based on parameter type)
"""
import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from shared.models import SectionRegistry, ActionRegistry
from django.contrib.auth.models import Group as AuthGroup


@method_decorator(login_required, name='dispatch')
class EntityReferenceSectionsView(View):
    """
    Returns list of all enabled sections from SectionRegistry.
    Response format: [
        {"code": "010301", "nickname": "users", "name": "Users", "name_en": "Users"},
        ...
    ]
    """
    def get(self, request):
        sections = SectionRegistry.objects.filter(is_enabled=1).order_by('module_code', 'menu_number', 'submenu_number', 'sort_order')
        
        # User can choose to display either nickname OR code, not both
        # For now, we return both and let the frontend decide
        sections_data = []
        for section in sections:
            sections_data.append({
                'code': section.section_code,
                'nickname': section.nickname,
                'name': section.name,
                'name_en': section.name_en or section.name,
            })
        
        return JsonResponse({'sections': sections_data})


@method_decorator(login_required, name='dispatch')
class EntityReferenceActionsView(View):
    """
    Returns list of enabled actions for a given section.
    Query params:
        - section_code: Section code (e.g., "010301") or nickname (e.g., "users")
    
    Response format: [
        {
            "action_name": "show",
            "action_label": "مشاهده",
            "action_label_en": "View",
            "parameter_schema": {...}
        },
        ...
    ]
    """
    def get(self, request):
        section_identifier = request.GET.get('section_code') or request.GET.get('nickname')
        
        if not section_identifier:
            return JsonResponse({'error': 'section_code or nickname required'}, status=400)
        
        # Find section by code or nickname
        try:
            if section_identifier.isdigit():
                section = SectionRegistry.objects.get(section_code=section_identifier, is_enabled=1)
            else:
                section = SectionRegistry.objects.get(nickname=section_identifier, is_enabled=1)
        except SectionRegistry.DoesNotExist:
            return JsonResponse({'error': 'Section not found'}, status=404)
        
        actions = ActionRegistry.objects.filter(
            section=section,
            is_enabled=1
        ).order_by('sort_order', 'action_name')
        
        actions_data = []
        for action in actions:
            actions_data.append({
                'action_name': action.action_name,
                'action_label': action.action_label,
                'action_label_en': action.action_label_en or action.action_label,
                'parameter_schema': action.parameter_schema or {},
            })
        
        return JsonResponse({'actions': actions_data})


@method_decorator(login_required, name='dispatch')
class EntityReferenceParameterValuesView(View):
    """
    Returns possible values for a parameter based on its type.
    Query params:
        - parameter_name: Name of the parameter (e.g., "gp", "type", "id")
        - parameter_type: Type of parameter (e.g., "string", "integer", "enum")
        - parameter_enum: JSON array of enum values (if type is enum)
        - section_code: Section code (optional, for context-specific values)
        - action_name: Action name (optional, for context-specific values)
    
    Response format: [
        {"value": "value1", "label": "Label 1"},
        {"value": "value2", "label": "Label 2"},
        ...
    ]
    """
    def get(self, request):
        parameter_name = request.GET.get('parameter_name')
        parameter_type = request.GET.get('parameter_type', 'string')
        parameter_enum_str = request.GET.get('parameter_enum')
        section_code = request.GET.get('section_code')
        action_name = request.GET.get('action_name')
        
        if not parameter_name:
            return JsonResponse({'error': 'parameter_name required'}, status=400)
        
        values = []
        
        # Handle enum type
        if parameter_type == 'enum' and parameter_enum_str:
            try:
                enum_values = json.loads(parameter_enum_str)
                if isinstance(enum_values, list):
                    for val in enum_values:
                        values.append({
                            'value': str(val),
                            'label': str(val).title().replace('_', ' ')
                        })
            except (json.JSONDecodeError, TypeError):
                pass
        
        # Handle specific parameter names
        elif parameter_name == 'gp':  # Group parameter
            # Return list of groups
            groups = AuthGroup.objects.all().order_by('name')
            for group in groups:
                values.append({
                    'value': group.name,
                    'label': group.name
                })
        
        elif parameter_name == 'type':
            # Common type values based on section/action context
            if section_code and action_name:
                # Could be receipt types, issue types, etc.
                if 'receipt' in section_code.lower() or 'receipt' in (section_code or ''):
                    values = [
                        {'value': 'temporary', 'label': 'Temporary'},
                        {'value': 'permanent', 'label': 'Permanent'},
                        {'value': 'consignment', 'label': 'Consignment'},
                    ]
                elif 'issue' in section_code.lower() or 'issue' in (section_code or ''):
                    values = [
                        {'value': 'permanent', 'label': 'Permanent'},
                        {'value': 'consumption', 'label': 'Consumption'},
                        {'value': 'consignment', 'label': 'Consignment'},
                    ]
        
        # For id and code parameters, we might need to fetch from specific models
        # This would require more context, so for now return empty
        # The frontend can handle this by allowing manual input or making additional calls
        
        return JsonResponse({'values': values})

