"""
Forms for ticket category management.
"""
from typing import Optional, Any

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from shared.models import ENABLED_FLAG_CHOICES

from ..models import (
    TicketCategory,
    TicketCategoryPermission,
)
from .base import TicketingBaseForm

User = get_user_model()


class TicketCategoryForm(TicketingBaseForm):
    """Form for creating and editing ticket categories."""

    class Meta:
        model = TicketCategory
        fields = [
            "public_code",
            "name",
            "name_en",
            "description",
            "parent_category",
            "is_enabled",
            "sort_order",
        ]
        widgets = {
            "public_code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "name_en": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "parent_category": forms.Select(attrs={"class": "form-control"}),
            "is_enabled": forms.Select(attrs={"class": "form-control"}),
            "sort_order": forms.NumberInput(attrs={"class": "form-control"}),
        }
        labels = {
            "public_code": _("Category Code"),
            "name": _("Name"),
            "name_en": _("Name (English)"),
            "description": _("Description"),
            "parent_category": _("Parent Category"),
            "is_enabled": _("Status"),
            "sort_order": _("Sort Order"),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with filtered querysets."""
        super().__init__(*args, **kwargs)
        company_id = None
        if hasattr(self, "request") and self.request:
            company_id = self.request.session.get("active_company_id")

        if company_id:
            # Filter parent categories by company and exclude self
            parent_qs = TicketCategory.objects.filter(company_id=company_id, is_enabled=1)
            if self.instance and self.instance.pk:
                parent_qs = parent_qs.exclude(pk=self.instance.pk)
            self.fields["parent_category"].queryset = parent_qs

        self.fields["is_enabled"].choices = ENABLED_FLAG_CHOICES
        self.fields["parent_category"].required = False

        # Make public_code read-only if editing
        if self.instance and self.instance.pk:
            self.fields["public_code"].widget.attrs["readonly"] = True
            self.fields["public_code"].widget.attrs["style"] = "background-color: #f3f4f6;"


class TicketCategoryPermissionForm(forms.ModelForm):
    """Form for category permission entries."""

    class Meta:
        model = TicketCategoryPermission
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
            "can_create": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "can_respond": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "can_close": forms.CheckboxInput(attrs={"class": "form-check-input"}),
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
        company_id = None
        if hasattr(self, "request") and self.request:
            company_id = self.request.session.get("active_company_id")

        # Filter users and groups by company if available
        # TODO: Filter users by company access
        self.fields["user"].queryset = User.objects.filter(is_active=True).order_by("username")
        self.fields["group"].queryset = Group.objects.all().order_by("name")
        self.fields["user"].required = False
        self.fields["group"].required = False
        self.fields["is_enabled"].choices = ENABLED_FLAG_CHOICES

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


class BaseTicketCategoryPermissionFormSet(BaseInlineFormSet):
    """Base formset for category permissions with validation."""

    def clean(self):
        """Validate that each row has either user or group, not both."""
        super().clean()
        for form in self.forms:
            if form.cleaned_data.get("DELETE"):
                continue
            user = form.cleaned_data.get("user")
            group = form.cleaned_data.get("group")

            if not user and not group:
                raise forms.ValidationError(
                    _("Each permission entry must have either a user or a group.")
                )


TicketCategoryPermissionFormSet = inlineformset_factory(
    TicketCategory,
    TicketCategoryPermission,
    form=TicketCategoryPermissionForm,
    formset=BaseTicketCategoryPermissionFormSet,
    fk_name="category",
    extra=1,
    can_delete=True,
)

