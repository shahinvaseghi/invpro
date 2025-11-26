"""
Forms for ticket template management.
"""
from typing import Optional, Any, Dict

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from shared.models import ENABLED_FLAG_CHOICES

from ..models import (
    TicketTemplate,
    TicketTemplateField,
    TicketTemplateFieldOption,
    TicketTemplatePermission,
    TicketTemplateEvent,
    TicketTemplateFieldEvent,
    TicketCategory,
    TicketPriority,
)
from .base import TicketingBaseForm

User = get_user_model()


class TicketTemplateForm(TicketingBaseForm):
    """Form for creating and editing ticket templates."""

    class Meta:
        model = TicketTemplate
        fields = [
            "name",
            "description",
            "category",
            "default_priority",
            "is_enabled",
            "sort_order",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "default_priority": forms.Select(attrs={"class": "form-control"}),
            "is_enabled": forms.Select(attrs={"class": "form-control"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "name": _("Template Name"),
            "description": _("Description"),
            "category": _("Category"),
            "default_priority": _("Default Priority"),
            "is_enabled": _("Status"),
            "sort_order": _("Sort Order"),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with filtered querysets."""
        super().__init__(*args, **kwargs)
        company_id = None
        if self.request:
            company_id = self.request.session.get("active_company_id")

        if company_id:
            self.fields["category"].queryset = TicketCategory.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by("name")
            self.fields["default_priority"].queryset = TicketPriority.objects.filter(
                company_id=company_id, is_enabled=1
            ).order_by("priority_level")

        self.fields["is_enabled"].choices = ENABLED_FLAG_CHOICES
        self.fields["category"].required = False
        self.fields["default_priority"].required = False


class TicketTemplateFieldForm(forms.ModelForm):
    """Form for template field entries."""

    FIELD_TYPE_CHOICES = [
        ("short_text", _("Short Text")),
        ("long_text", _("Long Text")),
        ("radio", _("Radio Button")),
        ("dropdown", _("Dropdown")),
        ("checkbox", _("Checkbox")),
        ("number", _("Number")),
        ("date", _("Date")),
        ("time", _("Time")),
        ("datetime", _("DateTime")),
        ("email", _("Email")),
        ("url", _("URL")),
        ("phone", _("Phone")),
        ("file_upload", _("File Upload")),
        ("reference", _("Reference")),
        ("multi_select", _("Multi Select")),
        ("tags", _("Tags")),
        ("rich_text", _("Rich Text")),
        ("color", _("Color")),
        ("rating", _("Rating")),
        ("slider", _("Slider")),
        ("currency", _("Currency")),
        ("signature", _("Signature")),
        ("location", _("Location")),
        ("section", _("Section")),
        ("calculation", _("Calculation")),
    ]

    class Meta:
        model = TicketTemplateField
        fields = [
            "field_name",
            "field_type",
            "field_key",
            "is_required",
            "default_value",
            "field_order",
            "help_text",
            "validation_rules",
            "field_config",
            "is_enabled",
        ]
        widgets = {
            "field_name": forms.TextInput(attrs={"class": "form-control"}),
            "field_type": forms.Select(attrs={"class": "form-control"}),
            "field_key": forms.TextInput(attrs={"class": "form-control"}),
            "is_required": forms.Select(attrs={"class": "form-control"}),
            "default_value": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "field_order": forms.NumberInput(attrs={"class": "form-control"}),
            "help_text": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "validation_rules": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": '{"min_length": 5, "max_length": 100}'}),
            "field_config": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": '{"allowed_entity_types": ["inventory.item"]}'}),
            "is_enabled": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "field_name": _("Field Name"),
            "field_type": _("Field Type"),
            "field_key": _("Field Key"),
            "is_required": _("Required"),
            "default_value": _("Default Value"),
            "field_order": _("Order"),
            "help_text": _("Help Text"),
            "validation_rules": _("Validation Rules (JSON)"),
            "field_config": _("Field Configuration (JSON)"),
            "is_enabled": _("Status"),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with field type choices."""
        super().__init__(*args, **kwargs)
        self.fields["field_type"].choices = self.FIELD_TYPE_CHOICES
        self.fields["is_enabled"].choices = ENABLED_FLAG_CHOICES
        self.fields["is_required"].choices = ENABLED_FLAG_CHOICES
        
        # Convert field_config dict to JSON string for display in template
        # This is necessary because JSONField returns dict in Python but we need JSON string in template
        import json
        if self.instance and self.instance.pk and hasattr(self.instance, 'field_config'):
            field_config_value = self.instance.field_config
            if field_config_value:
                if isinstance(field_config_value, dict):
                    # Convert dict to JSON string
                    json_string = json.dumps(field_config_value, ensure_ascii=False)
                    # Override the widget's format_value to return JSON string
                    original_widget = self.fields["field_config"].widget
                    original_format_value = original_widget.format_value
                    
                    def format_json_value(value):
                        if isinstance(value, dict):
                            return json.dumps(value, ensure_ascii=False)
                        elif isinstance(value, str):
                            # Already a string, return as-is
                            return value
                        elif value is None:
                            return ""
                        else:
                            return original_format_value(value)
                    
                    original_widget.format_value = format_json_value


class TicketTemplateFieldOptionForm(forms.ModelForm):
    """Form for template field option entries."""

    class Meta:
        model = TicketTemplateFieldOption
        fields = [
            "option_value",
            "option_label",
            "option_order",
            "is_default",
            "is_enabled",
        ]
        widgets = {
            "option_value": forms.TextInput(attrs={"class": "form-control"}),
            "option_label": forms.TextInput(attrs={"class": "form-control"}),
            "option_order": forms.NumberInput(attrs={"class": "form-control"}),
            "is_default": forms.Select(attrs={"class": "form-control"}),
            "is_enabled": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "option_value": _("Option Value"),
            "option_label": _("Option Label"),
            "option_order": _("Order"),
            "is_default": _("Default"),
            "is_enabled": _("Status"),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form."""
        super().__init__(*args, **kwargs)
        self.fields["is_enabled"].choices = ENABLED_FLAG_CHOICES
        self.fields["is_default"].choices = ENABLED_FLAG_CHOICES


class TicketTemplateEventForm(forms.ModelForm):
    """Form for template event entries."""

    class Meta:
        model = TicketTemplateEvent
        fields = [
            "event_type",
            "event_order",
            "action_reference",
            "condition_rules",
            "is_enabled",
        ]
        widgets = {
            "event_type": forms.Select(attrs={"class": "form-control"}),
            "event_order": forms.NumberInput(attrs={"class": "form-control"}),
            "action_reference": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., users:show:gp=superuser"}),
            "condition_rules": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": '{"field_key": "priority", "operator": "equals", "value": "high"}'}),
            "is_enabled": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "event_type": _("Event Type"),
            "event_order": _("Order"),
            "action_reference": _("Action Reference"),
            "condition_rules": _("Condition Rules (JSON)"),
            "is_enabled": _("Status"),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form."""
        super().__init__(*args, **kwargs)
        self.fields["is_enabled"].choices = ENABLED_FLAG_CHOICES


class TicketTemplateFieldEventForm(forms.ModelForm):
    """Form for template field event entries."""

    class Meta:
        model = TicketTemplateFieldEvent
        fields = [
            "event_type",
            "event_order",
            "action_reference",
            "condition_rules",
            "is_enabled",
        ]
        widgets = {
            "event_type": forms.Select(attrs={"class": "form-control"}),
            "event_order": forms.NumberInput(attrs={"class": "form-control"}),
            "action_reference": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., users:show:gp=superuser"}),
            "condition_rules": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "is_enabled": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "event_type": _("Event Type"),
            "event_order": _("Order"),
            "action_reference": _("Action Reference"),
            "condition_rules": _("Condition Rules (JSON)"),
            "is_enabled": _("Status"),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form."""
        super().__init__(*args, **kwargs)
        self.fields["is_enabled"].choices = ENABLED_FLAG_CHOICES


class TicketTemplatePermissionForm(forms.ModelForm):
    """Form for template permission entries."""

    class Meta:
        model = TicketTemplatePermission
        fields = [
            "user",
            "group",
            "can_create",
            "can_respond",
            "can_close",
            "is_enabled",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "group": forms.Select(attrs={"class": "form-control"}),
            "can_create": forms.Select(attrs={"class": "form-control"}),
            "can_respond": forms.Select(attrs={"class": "form-control"}),
            "can_close": forms.Select(attrs={"class": "form-control"}),
            "is_enabled": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "user": _("User"),
            "group": _("Group"),
            "can_create": _("Can Create"),
            "can_respond": _("Can Respond"),
            "can_close": _("Can Close"),
            "is_enabled": _("Status"),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with filtered querysets."""
        super().__init__(*args, **kwargs)
        # TODO: Filter users by company access
        self.fields["user"].queryset = User.objects.filter(is_active=True).order_by("username")
        self.fields["group"].queryset = Group.objects.all().order_by("name")
        self.fields["user"].required = False
        self.fields["group"].required = False
        self.fields["is_enabled"].choices = ENABLED_FLAG_CHOICES
        self.fields["can_create"].choices = ENABLED_FLAG_CHOICES
        self.fields["can_respond"].choices = ENABLED_FLAG_CHOICES
        self.fields["can_close"].choices = ENABLED_FLAG_CHOICES

    def clean(self):
        """Ensure either user or group is set, but not both."""
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        group = cleaned_data.get("group")

        if not user and not group:
            raise forms.ValidationError(_("Either user or group must be set."))
        if user and group:
            raise forms.ValidationError(_("Cannot set both user and group."))

        return cleaned_data


# ============================================================================
# Formsets
# ============================================================================


class BaseTicketTemplateFieldFormSet(BaseInlineFormSet):
    """Base formset for template fields with validation."""

    def clean(self):
        """Validate field keys are unique within template."""
        super().clean()
        field_keys = []
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            field_key = form.cleaned_data.get("field_key")
            if field_key and field_key in field_keys:
                raise forms.ValidationError(
                    _("Field key '%(field_key)s' is duplicated. Field keys must be unique within a template.")
                    % {"field_key": field_key}
                )
            if field_key:
                field_keys.append(field_key)


class BaseTicketTemplateFieldOptionFormSet(BaseInlineFormSet):
    """Base formset for field options with validation."""

    def clean(self):
        """Validate option values are unique within field."""
        super().clean()
        option_values = []
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            option_value = form.cleaned_data.get("option_value")
            if option_value and option_value in option_values:
                raise forms.ValidationError(
                    _("Option value '%(option_value)s' is duplicated. Option values must be unique within a field.")
                    % {"option_value": option_value}
                )
            if option_value:
                option_values.append(option_value)


class BaseTicketTemplatePermissionFormSet(BaseInlineFormSet):
    """Base formset for template permissions with validation."""

    def clean(self):
        """Validate that each row has either user or group."""
        super().clean()
        for form in self.forms:
            # Skip forms marked for deletion
            if form.cleaned_data.get("DELETE"):
                continue
            
            # Skip completely empty forms (new forms with no data entered)
            # For new forms without instance, check if any data was entered
            if not form.instance.pk:
                # This is a new form - check if any field has been filled
                user = form.cleaned_data.get("user")
                group = form.cleaned_data.get("group")
                can_create = form.cleaned_data.get("can_create", 0)
                can_respond = form.cleaned_data.get("can_respond", 0)
                can_close = form.cleaned_data.get("can_close", 0)
                
                # If all fields are empty/default, skip validation (form will be ignored)
                if not user and not group and can_create == 0 and can_respond == 0 and can_close == 0:
                    continue
            
            # For existing instances or forms with data, validate
            user = form.cleaned_data.get("user")
            group = form.cleaned_data.get("group")
            
            if not user and not group:
                raise forms.ValidationError(
                    _("Each permission entry must have either a user or a group.")
                )


TicketTemplateFieldFormSet = inlineformset_factory(
    TicketTemplate,
    TicketTemplateField,
    form=TicketTemplateFieldForm,
    formset=BaseTicketTemplateFieldFormSet,
    fk_name="template",
    extra=1,
    can_delete=True,
)

TicketTemplateFieldOptionFormSet = inlineformset_factory(
    TicketTemplateField,
    TicketTemplateFieldOption,
    form=TicketTemplateFieldOptionForm,
    formset=BaseTicketTemplateFieldOptionFormSet,
    fk_name="template_field",
    extra=1,
    can_delete=True,
)

TicketTemplateEventFormSet = inlineformset_factory(
    TicketTemplate,
    TicketTemplateEvent,
    form=TicketTemplateEventForm,
    fk_name="template",
    extra=1,
    can_delete=True,
)

TicketTemplatePermissionFormSet = inlineformset_factory(
    TicketTemplate,
    TicketTemplatePermission,
    form=TicketTemplatePermissionForm,
    formset=BaseTicketTemplatePermissionFormSet,
    fk_name="template",
    extra=0,
    can_delete=True,
)

# Note: TemplateFieldEventFormSet will be created dynamically per field in views

