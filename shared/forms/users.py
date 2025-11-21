"""
User and UserCompanyAccess forms for shared module.
"""
from typing import Optional, List

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from shared.models import Company, AccessLevel, UserCompanyAccess, ENABLED_FLAG_CHOICES

User = get_user_model()


class UserBaseForm(forms.ModelForm):
    """Base form for user creation and update."""
    
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        required=False,
        label=_('Groups'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text=_('Assign the user to one or more groups.'),
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'first_name_en',
            'last_name_en',
            'phone_number',
            'mobile_number',
            'is_active',
            'is_staff',
            'is_superuser',
            'default_company',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'default_company': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': _('Username'),
            'email': _('Email'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'first_name_en': _('First Name (English)'),
            'last_name_en': _('Last Name (English)'),
            'phone_number': _('Phone'),
            'mobile_number': _('Mobile'),
            'is_active': _('Active'),
            'is_staff': _('Staff User'),
            'is_superuser': _('Superuser'),
            'default_company': _('Default Company'),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with groups queryset."""
        super().__init__(*args, **kwargs)
        self._pending_groups = None
        self.fields['default_company'].queryset = Company.objects.filter(is_enabled=1)
        self.fields['default_company'].required = False
        self.fields['groups'].queryset = Group.objects.order_by('name')
        if self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.all()

        self.fields['is_active'] = forms.BooleanField(
            required=False,
            initial=getattr(self.instance, 'is_active', True),
            label=_('Active'),
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        )
        self.fields['is_staff'] = forms.BooleanField(
            required=False,
            initial=getattr(self.instance, 'is_staff', False),
            label=_('Staff User'),
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        )
        self.fields['is_superuser'] = forms.BooleanField(
            required=False,
            initial=getattr(self.instance, 'is_superuser', False),
            label=_('Superuser'),
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        )

    def _store_groups(self) -> None:
        """Store groups to user instance."""
        if self._pending_groups is not None:
            self.instance.groups.set(self._pending_groups)

    def save(self, commit: bool = True):
        """Save user with groups."""
        # Store groups before calling super().save() to ensure they're available
        self._pending_groups = self.cleaned_data.get('groups')
        user = super().save(commit=commit)
        if commit:
            self._store_groups()
        return user

    def save_m2m(self) -> None:
        """Save many-to-many relationships (groups)."""
        # Store groups BEFORE calling super().save_m2m() which may clear them
        # Use _pending_groups if set, otherwise fall back to cleaned_data
        groups_to_set = None
        if hasattr(self, '_pending_groups') and self._pending_groups is not None:
            # Convert QuerySet to list of IDs to avoid stale queryset issues
            groups_to_set = list(self._pending_groups.values_list('id', flat=True))
        elif hasattr(self, 'cleaned_data') and 'groups' in self.cleaned_data:
            # Convert QuerySet to list of IDs
            groups_to_set = list(self.cleaned_data['groups'].values_list('id', flat=True))
        
        # Don't call super().save_m2m() because it will try to save 'groups' field
        # which is not in the form's Meta.fields, and may clear existing groups
        # Instead, set groups directly
        if groups_to_set is not None:
            self.instance.groups.set(groups_to_set)


class UserCreateForm(UserBaseForm):
    """Form for creating new users."""
    
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label=_('Password confirmation'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text=_('Enter the same password as before, for verification.'),
    )

    class Meta(UserBaseForm.Meta):
        fields = UserBaseForm.Meta.fields

    def clean(self) -> dict:
        """Validate password match."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('The two password fields did not match.'))
        return cleaned_data

    def save(self, commit: bool = True):
        """Save user with password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserUpdateForm(UserBaseForm):
    """Form for updating existing users."""
    
    new_password1 = forms.CharField(
        label=_('New password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
    )
    new_password2 = forms.CharField(
        label=_('Confirm new password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
    )

    class Meta(UserBaseForm.Meta):
        fields = UserBaseForm.Meta.fields

    def clean(self) -> dict:
        """Validate new password match."""
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 or new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(_('The new passwords do not match.'))
        return cleaned_data

    def save(self, commit: bool = True):
        """Save user with optional password change."""
        # Ensure _pending_groups is set before calling super().save()
        if not hasattr(self, '_pending_groups') or self._pending_groups is None:
            self._pending_groups = self.cleaned_data.get('groups')
        
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password1')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
            # Save groups directly after user is saved
            if hasattr(self, '_pending_groups') and self._pending_groups is not None:
                groups_to_set = list(self._pending_groups.values_list('id', flat=True))
                user.groups.set(groups_to_set)
            # Call save_m2m for any other M2M fields
            self.save_m2m()
        else:
            # Even if commit=False, we need to ensure _pending_groups is set
            # so save_m2m() can use it later
            if not hasattr(self, '_pending_groups') or self._pending_groups is None:
                self._pending_groups = self.cleaned_data.get('groups')
        return user


class UserCompanyAccessForm(forms.ModelForm):
    """Form for user company access."""
    
    class Meta:
        model = UserCompanyAccess
        fields = ['company', 'access_level', 'is_primary', 'is_enabled']
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'access_level': forms.Select(attrs={'class': 'form-control'}),
            'is_primary': forms.Select(attrs={'class': 'form-control'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'company': _('Company'),
            'access_level': _('Access Level'),
            'is_primary': _('Primary'),
            'is_enabled': _('Status'),
        }

    def __init__(self, *args, **kwargs):
        """Initialize form with filtered querysets."""
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(is_enabled=1).order_by('display_name')
        self.fields['access_level'].queryset = AccessLevel.objects.filter(is_enabled=1).order_by('code')
        self.fields['is_primary'].choices = ENABLED_FLAG_CHOICES
        self.fields['is_enabled'].choices = ENABLED_FLAG_CHOICES


class BaseUserCompanyAccessFormSet(BaseInlineFormSet):
    """Base formset for user company access with validation."""
    
    def clean(self) -> None:
        """Validate that only one primary company is selected."""
        super().clean()
        primary_count = 0
        for form in self.forms:
            if form.cleaned_data.get('DELETE'):
                continue
            if not form.cleaned_data.get('company'):
                continue
            if form.cleaned_data.get('is_primary') == 1:
                primary_count += 1
        if primary_count > 1:
            raise forms.ValidationError(_('Only one primary company may be selected per user.'))


UserCompanyAccessFormSet = inlineformset_factory(
    User,
    UserCompanyAccess,
    form=UserCompanyAccessForm,
    formset=BaseUserCompanyAccessFormSet,
    fk_name='user',
    extra=1,
    can_delete=True,
)

