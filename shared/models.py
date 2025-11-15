import re

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


NUMERIC_CODE_VALIDATOR = RegexValidator(
    regex=r"^\d+$",
    message=_("Only numeric characters are allowed."),
)

ENABLED_FLAG_CHOICES = (
    (0, _("Disabled")),
    (1, _("Enabled")),
)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
        null=True,
        blank=True,
    )
    edited_at = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_edited",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class ActivatableModel(models.Model):
    is_enabled = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=1,
    )
    enabled_at = models.DateTimeField(null=True, blank=True)
    enabled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_enabled",
        null=True,
        blank=True,
    )
    disabled_at = models.DateTimeField(null=True, blank=True)
    disabled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_disabled",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class MetadataModel(models.Model):
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        abstract = True


class SortableModel(models.Model):
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True


class LockableModel(models.Model):
    is_locked = models.PositiveSmallIntegerField(default=0)
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_locked",
        null=True,
        blank=True,
    )
    unlocked_at = models.DateTimeField(null=True, blank=True)
    unlocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_unlocked",
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True


class CompanyScopedModel(models.Model):
    company = models.ForeignKey(
        "shared.Company",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    company_code = models.CharField(
        max_length=8,
        validators=[NUMERIC_CODE_VALIDATOR],
        blank=True,
        editable=False,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.company and not self.company_code:
            self.company_code = self.company.public_code
        super().save(*args, **kwargs)


class User(AbstractUser, MetadataModel):
    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(max_length=30, blank=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    first_name_en = models.CharField(max_length=120, blank=True)
    last_name_en = models.CharField(max_length=120, blank=True)
    default_company = models.ForeignKey(
        'Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_users',
        help_text=_("Default company to use when user logs in")
    )

    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self) -> str:
        return self.get_full_name() or self.username


class Company(TimeStampedModel, ActivatableModel, MetadataModel):
    public_code = models.CharField(
        max_length=3,
        unique=True,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    legal_name = models.CharField(max_length=180, unique=True)
    display_name = models.CharField(max_length=180, unique=True)
    display_name_en = models.CharField(max_length=180, blank=True)
    registration_number = models.CharField(max_length=60, unique=True, null=True, blank=True)
    tax_id = models.CharField(max_length=60, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=3, blank=True)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        ordering = ("public_code",)

    def __str__(self) -> str:
        return self.display_name


class CompanyUnit(CompanyScopedModel, TimeStampedModel, ActivatableModel, MetadataModel):
    public_code = models.CharField(
        max_length=5,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    name = models.CharField(max_length=180)
    name_en = models.CharField(max_length=180, blank=True)
    unit_type = models.CharField(max_length=30)
    parent_unit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="child_units",
    )
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Company Unit")
        verbose_name_plural = _("Company Units")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="company_unit_company_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="company_unit_company_name_unique",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class AccessLevel(TimeStampedModel, ActivatableModel, MetadataModel):
    code = models.CharField(max_length=30, unique=True, blank=True, editable=False)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_global = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
    )

    class Meta:
        verbose_name = _("Access Level")
        verbose_name_plural = _("Access Levels")
        ordering = ("code",)

    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.code:
            # Generate code from name: convert to uppercase, replace spaces with underscores
            base_code = self.name.upper().strip()
            # Remove special characters, keep only alphanumeric and underscores
            base_code = ''.join(c if c.isalnum() or c == '_' else '_' for c in base_code)
            # Replace multiple underscores with single underscore
            base_code = re.sub(r'_+', '_', base_code)
            # Remove leading/trailing underscores
            base_code = base_code.strip('_')
            # Limit length to 25 chars (leaving room for sequence suffix)
            if len(base_code) > 25:
                base_code = base_code[:25].rstrip('_')
            
            # If empty after cleaning, use default
            if not base_code:
                base_code = "ACCESS_LEVEL"
            
            # Check if code exists, if yes add sequence
            candidate_code = base_code
            sequence = 1
            while AccessLevel.objects.filter(code=candidate_code).exclude(pk=self.pk).exists():
                suffix = f"_{sequence}"
                # Ensure total length doesn't exceed 30
                max_base_len = 30 - len(suffix)
                candidate_code = base_code[:max_base_len] + suffix
                sequence += 1
            
            self.code = candidate_code
        
        super().save(*args, **kwargs)


class AccessLevelPermission(TimeStampedModel, MetadataModel):
    access_level = models.ForeignKey(
        AccessLevel,
        on_delete=models.CASCADE,
        related_name="permissions",
    )
    module_code = models.CharField(max_length=30)
    resource_type = models.CharField(max_length=40)
    resource_code = models.CharField(max_length=60)
    can_view = models.PositiveSmallIntegerField(choices=ENABLED_FLAG_CHOICES, default=0)
    can_create = models.PositiveSmallIntegerField(choices=ENABLED_FLAG_CHOICES, default=0)
    can_edit = models.PositiveSmallIntegerField(choices=ENABLED_FLAG_CHOICES, default=0)
    can_delete = models.PositiveSmallIntegerField(choices=ENABLED_FLAG_CHOICES, default=0)
    can_approve = models.PositiveSmallIntegerField(choices=ENABLED_FLAG_CHOICES, default=0)

    class Meta:
        verbose_name = _("Access Level Permission")
        verbose_name_plural = _("Access Level Permissions")
        constraints = [
            models.UniqueConstraint(
                fields=("access_level", "module_code", "resource_code"),
                name="access_level_permission_unique_resource",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.access_level.code} · {self.module_code}:{self.resource_code}"


class GroupProfile(TimeStampedModel, ActivatableModel, MetadataModel):
    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    description = models.CharField(max_length=255, blank=True)
    access_levels = models.ManyToManyField(
        AccessLevel,
        related_name="groups",
        blank=True,
    )

    class Meta:
        verbose_name = _("Group Profile")
        verbose_name_plural = _("Group Profiles")

    def __str__(self) -> str:
        return self.group.name


class UserCompanyAccess(TimeStampedModel, ActivatableModel, MetadataModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_accesses",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="user_accesses",
    )
    access_level = models.ForeignKey(
        AccessLevel,
        on_delete=models.PROTECT,
        related_name="user_accesses",
    )
    is_primary = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
    )

    class Meta:
        verbose_name = _("User Company Access")
        verbose_name_plural = _("User Company Accesses")
        constraints = [
            models.UniqueConstraint(
                fields=("user", "company"),
                name="user_company_access_unique_pair",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user} @ {self.company}"


class Person(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    SortableModel,
    MetadataModel,
):
    public_code = models.CharField(
        max_length=8,
        validators=[NUMERIC_CODE_VALIDATOR],
    )
    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    first_name_en = models.CharField(max_length=120, blank=True)
    last_name_en = models.CharField(max_length=120, blank=True)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    personnel_code = models.CharField(max_length=30, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    mobile_number = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="person_profile",
        null=True,
        blank=True,
    )
    company_units = models.ManyToManyField(
        CompanyUnit,
        blank=True,
        related_name="people",
    )

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("People")
        ordering = ("company", "sort_order", "public_code")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="person_company_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "username"),
                name="person_company_username_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "first_name", "last_name"),
                name="person_company_name_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class PersonAssignment(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name="assignments",
    )
    work_center_id = models.BigIntegerField()
    work_center_type = models.CharField(max_length=30)
    is_primary = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
    )
    assignment_start = models.DateField(null=True, blank=True)
    assignment_end = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Person Assignment")
        verbose_name_plural = _("Person Assignments")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "person", "work_center_id", "work_center_type"),
                name="person_assignment_unique_scope",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.person} → {self.work_center_type}:{self.work_center_id}"
