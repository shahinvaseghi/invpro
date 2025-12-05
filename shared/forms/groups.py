"""
Group forms for shared module.
"""
from typing import Optional

from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from shared.models import AccessLevel, GroupProfile, ENABLED_FLAG_CHOICES
from shared.forms.base import BaseModelForm


class GroupForm(BaseModelForm):
    """Form for creating/editing groups."""
    
    description = forms.CharField(
        label=_('Description'),
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
    )
    is_enabled = forms.ChoiceField(
        choices=ENABLED_FLAG_CHOICES,
        label=_('Status'),
        initial=1,
    )
    access_levels = forms.ModelMultipleChoiceField(
        queryset=AccessLevel.objects.none(),
        required=False,
        label=_('Access Levels'),
        widget=forms.CheckboxSelectMultiple(),
        help_text=_('Select one or more access levels for this group.'),
    )

    class Meta:
        model = Group
        fields = ['name']
        labels = {
            'name': _('Group Name'),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with profile data."""
        super().__init__(*args, **kwargs)
        self.profile: Optional[GroupProfile] = getattr(self.instance, 'profile', None)
        self.fields['access_levels'].queryset = AccessLevel.objects.filter(is_enabled=1).order_by('code')
        if self.profile:
            self.fields['description'].initial = self.profile.description
            self.fields['is_enabled'].initial = self.profile.is_enabled
            self.fields['access_levels'].initial = self.profile.access_levels.all()
        else:
            self.fields['is_enabled'].initial = 1

    def save(self, commit: bool = True):
        """Save group with profile."""
        group = super().save(commit=commit)
        profile = getattr(group, 'profile', None)
        if profile is None:
            profile = GroupProfile(group=group)
        profile.description = self.cleaned_data.get('description', '')
        profile.is_enabled = int(self.cleaned_data.get('is_enabled', 1) or 0)
        if commit:
            profile.save()
            profile.access_levels.set(self.cleaned_data.get('access_levels') or [])
        else:
            self._post_save_profile = profile
        return group

    def save_m2m(self) -> None:
        """Save many-to-many relationships (access levels)."""
        super().save_m2m()
        profile = getattr(self, '_post_save_profile', None)
        if profile:
            profile.save()
            profile.access_levels.set(self.cleaned_data.get('access_levels') or [])

