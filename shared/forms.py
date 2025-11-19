"""
Forms for shared module.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from .models import (
    AccessLevel,
    Company,
    CompanyUnit,
    ENABLED_FLAG_CHOICES,
    GroupProfile,
    UserCompanyAccess,
)

User = get_user_model()


class CompanyForm(forms.ModelForm):
    """Form for creating/editing companies."""
    
    class Meta:
        model = Company
        fields = [
            'public_code',
            'legal_name',
            'display_name',
            'display_name_en',
            'registration_number',
            'tax_id',
            'phone_number',
            'email',
            'website',
            'address',
            'city',
            'state',
            'country',
            'is_enabled',
        ]
        widgets = {
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
            'legal_name': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name': forms.TextInput(attrs={'class': 'form-control'}),
            'display_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'tax_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '3'}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'public_code': _('Code'),
            'legal_name': _('Legal Name'),
            'display_name': _('Display Name'),
            'display_name_en': _('Display Name (English)'),
            'registration_number': _('Registration Number'),
            'tax_id': _('Tax ID'),
            'phone_number': _('Phone'),
            'email': _('Email'),
            'website': _('Website'),
            'address': _('Address'),
            'city': _('City'),
            'state': _('State/Province'),
            'country': _('Country'),
            'is_enabled': _('Status'),
        }


class CompanyUnitForm(forms.ModelForm):
    """Form for creating/editing company units (organizational units)."""

    parent_unit = forms.ModelChoiceField(
        queryset=CompanyUnit.objects.none(),
        required=False,
        label=_('Parent Unit'),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = CompanyUnit
        fields = [
            'public_code',
            'name',
            'name_en',
            'parent_unit',
            'description',
            'notes',
            'is_enabled',
        ]
        widgets = {
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '5'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'public_code': 'کد',
            'name': 'نام واحد',
            'name_en': 'نام واحد (انگلیسی)',
            'parent_unit': 'واحد بالادست',
            'description': 'توضیح',
            'notes': 'یادداشت‌ها',
            'is_enabled': 'وضعیت',
        }

    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)

        queryset = CompanyUnit.objects.none()
        if self.company_id:
            queryset = CompanyUnit.objects.filter(company_id=self.company_id)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

        self.fields['parent_unit'].queryset = queryset
        self.fields['is_enabled'].choices = (
            (1, 'فعال'),
            (0, 'غیرفعال'),
        )

    def clean_parent_unit(self):
        parent = self.cleaned_data.get('parent_unit')
        if parent and self.company_id and parent.company_id != self.company_id:
            raise forms.ValidationError(_('Parent unit must belong to the same company.'))
        return parent


class UserBaseForm(forms.ModelForm):
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

    def _store_groups(self):
        if self._pending_groups is not None:
            self.instance.groups.set(self._pending_groups)

    def save(self, commit=True):
        # Store groups before calling super().save() to ensure they're available
        self._pending_groups = self.cleaned_data.get('groups')
        user = super().save(commit=commit)
        if commit:
            self._store_groups()
        return user

    def save_m2m(self):
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

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('The two password fields didn’t match.'))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            self.save_m2m()
        return user


class UserUpdateForm(UserBaseForm):
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

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        if new_password1 or new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError(_('The new passwords do not match.'))
        return cleaned_data

    def save(self, commit=True):
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


class GroupForm(forms.ModelForm):
    description = forms.CharField(
        label=_('Description'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
    )
    is_enabled = forms.ChoiceField(
        choices=ENABLED_FLAG_CHOICES,
        label=_('Status'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial=1,
    )
    access_levels = forms.ModelMultipleChoiceField(
        queryset=AccessLevel.objects.none(),
        required=False,
        label=_('Access Levels'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        help_text=_('Select one or more access levels for this group.'),
    )

    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Group Name'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = getattr(self.instance, 'profile', None)
        self.fields['access_levels'].queryset = AccessLevel.objects.filter(is_enabled=1).order_by('code')
        if self.profile:
            self.fields['description'].initial = self.profile.description
            self.fields['is_enabled'].initial = self.profile.is_enabled
            self.fields['access_levels'].initial = self.profile.access_levels.all()
        else:
            self.fields['is_enabled'].initial = 1

    def save(self, commit=True):
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

    def save_m2m(self):
        super().save_m2m()
        profile = getattr(self, '_post_save_profile', None)
        if profile:
            profile.save()
            profile.access_levels.set(self.cleaned_data.get('access_levels') or [])


class AccessLevelForm(forms.ModelForm):
    class Meta:
        model = AccessLevel
        fields = ['name', 'description', 'is_enabled', 'is_global']  # Removed 'code' - auto-generated
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
            'is_global': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Name'),
            'description': _('Description'),
            'is_enabled': _('Status'),
            'is_global': _('Global Role'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_enabled'].choices = ENABLED_FLAG_CHOICES
        self.fields['is_global'].choices = ENABLED_FLAG_CHOICES
        
        # Show code as read-only if editing existing instance
        if self.instance and self.instance.pk:
            self.fields['code'] = forms.CharField(
                label=_('Code'),
                required=False,
                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
                initial=self.instance.code,
                help_text=_('Auto-generated from name. Cannot be changed.')
            )


class UserCompanyAccessForm(forms.ModelForm):
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
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.filter(is_enabled=1).order_by('display_name')
        self.fields['access_level'].queryset = AccessLevel.objects.filter(is_enabled=1).order_by('code')
        self.fields['is_primary'].choices = ENABLED_FLAG_CHOICES
        self.fields['is_enabled'].choices = ENABLED_FLAG_CHOICES


class BaseUserCompanyAccessFormSet(BaseInlineFormSet):
    def clean(self):
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
