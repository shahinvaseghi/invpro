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
    Person,
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


class PersonForm(forms.ModelForm):
    """Form for creating/editing personnel."""
    
    use_personnel_code_as_username = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Use Personnel Code as Username'),
        help_text=_('If checked, username will be same as personnel code'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'use_personnel_code'})
    )
    
    class Meta:
        model = Person
        fields = [
            'public_code',
            'first_name',
            'last_name',
            'first_name_en',
            'last_name_en',
            'national_id',
            'personnel_code',
            'username',
            'phone_number',
            'mobile_number',
            'email',
            'description',
            'notes',
            'is_enabled',
            'company_units',
        ]
        widgets = {
            'public_code': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '8'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name_en': forms.TextInput(attrs={'class': 'form-control'}),
            'national_id': forms.TextInput(attrs={'class': 'form-control'}),
            'personnel_code': forms.TextInput(attrs={'class': 'form-control', 'id': 'personnel_code_field'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'username_field'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
            'company_units': forms.CheckboxSelectMultiple(
                attrs={'class': 'form-check-input'}
            ),
        }
        labels = {
            'public_code': _('Code'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'first_name_en': _('First Name (English)'),
            'last_name_en': _('Last Name (English)'),
            'national_id': _('National ID'),
            'personnel_code': _('Personnel Code'),
            'username': _('Username'),
            'phone_number': _('Phone'),
            'mobile_number': _('Mobile'),
            'email': _('Email'),
            'description': _('Description'),
            'notes': _('Notes'),
            'is_enabled': _('Status'),
            'company_units': _('Company Units'),
        }
    
    def __init__(self, *args, company_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.company_id = company_id or (self.instance.company_id if self.instance and self.instance.pk else None)

        if self.company_id:
            self.fields['company_units'].queryset = CompanyUnit.objects.filter(company_id=self.company_id, is_enabled=1)
            self.fields['company_units'].help_text = _('Select one or more organizational units.')
        else:
            self.fields['company_units'].queryset = CompanyUnit.objects.none()
            self.fields['company_units'].help_text = _('Please select a company first.')

        self.fields['company_units'].required = False

        # If editing and username equals personnel_code, check the box
        if self.instance.pk and self.instance.username == self.instance.personnel_code:
            self.fields['use_personnel_code_as_username'].initial = True
    
    def clean(self):
        cleaned_data = super().clean()
        use_personnel_code = cleaned_data.get('use_personnel_code_as_username')
        personnel_code = cleaned_data.get('personnel_code')
        username = cleaned_data.get('username')
        
        # If checkbox is checked, use personnel_code as username
        if use_personnel_code:
            if not personnel_code:
                raise forms.ValidationError(_('Personnel Code is required when using it as username.'))
            cleaned_data['username'] = personnel_code
        else:
            if not username:
                raise forms.ValidationError(_('Username is required when not using personnel code.'))
        
        # Ensure selected units belong to the same company
        if self.company_id:
            units = cleaned_data.get('company_units')
            if units and units.filter(~Q(company_id=self.company_id)).exists():
                raise forms.ValidationError(_('Selected units must belong to the active company.'))
        
        return cleaned_data


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
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
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
        self._pending_groups = self.cleaned_data.get('groups')
        user = super().save(commit=commit)
        if commit:
            self._store_groups()
        return user

    def save_m2m(self):
        super().save_m2m()
        self._store_groups()


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
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password1')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
            self.save_m2m()
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
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
    )
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        label=_('Members'),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        help_text=_('Select users who should belong to this group.'),
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
        self.fields['members'].queryset = User.objects.order_by('username')
        if self.profile:
            self.fields['description'].initial = self.profile.description
            self.fields['is_enabled'].initial = self.profile.is_enabled
            self.fields['access_levels'].initial = self.profile.access_levels.all()
        else:
            self.fields['is_enabled'].initial = 1
        if self.instance.pk:
            self.fields['members'].initial = self.instance.user_set.all()

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
            group.user_set.set(self.cleaned_data.get('members') or [])
        else:
            self._post_save_profile = profile
        return group

    def save_m2m(self):
        super().save_m2m()
        profile = getattr(self, '_post_save_profile', None)
        if profile:
            profile.save()
            profile.access_levels.set(self.cleaned_data.get('access_levels') or [])
            profile.group.user_set.set(self.cleaned_data.get('members') or [])


class AccessLevelForm(forms.ModelForm):
    class Meta:
        model = AccessLevel
        fields = ['code', 'name', 'description', 'is_enabled', 'is_global']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_enabled': forms.Select(attrs={'class': 'form-control'}),
            'is_global': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'code': _('Code'),
            'name': _('Name'),
            'description': _('Description'),
            'is_enabled': _('Status'),
            'is_global': _('Global Role'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_enabled'].choices = ENABLED_FLAG_CHOICES
        self.fields['is_global'].choices = ENABLED_FLAG_CHOICES


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
    extra=1,
    can_delete=True,
)
