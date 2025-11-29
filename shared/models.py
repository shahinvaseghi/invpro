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

# Export NUMERIC_CODE_VALIDATOR and ENABLED_FLAG_CHOICES for use in other modules
__all__ = [
    "TimeStampedModel",
    "ActivatableModel",
    "MetadataModel",
    "SortableModel",
    "CompanyScopedModel",
    "LockableModel",
    "EditableModel",
    "User",
    "Company",
    "CompanyUnit",
    "AccessLevel",
    "AccessLevelPermission",
    "GroupProfile",
    "UserCompanyAccess",
    "SMTPServer",
    "SectionRegistry",
    "ActionRegistry",
    "Notification",
    "NUMERIC_CODE_VALIDATOR",
    "ENABLED_FLAG_CHOICES",
]


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


class EditableModel(models.Model):
    """
    Mixin to track which user is currently editing a record.
    Prevents concurrent editing by multiple users.
    """
    editing_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_editing",
        null=True,
        blank=True,
        help_text=_("User currently editing this record"),
    )
    editing_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When editing session started"),
    )
    editing_session_key = models.CharField(
        max_length=40,
        blank=True,
        help_text=_("Django session key of the editing user"),
    )

    class Meta:
        abstract = True

    def clear_edit_lock(self):
        """Clear the edit lock for this record."""
        self.editing_by = None
        self.editing_started_at = None
        self.editing_session_key = ''
        self.save(update_fields=['editing_by', 'editing_started_at', 'editing_session_key'])

    def is_being_edited_by(self, user=None, session_key=None):
        """
        Check if this record is being edited by someone else.
        
        Args:
            user: User object to check if they are the editor
            session_key: Session key to check if it matches
            
        Returns:
            bool: True if record is being edited by someone else (not by the given user/session)
        """
        # If no editor, record is not being edited
        if not self.editing_by:
            return False
        
        # If user provided and matches the editor, record is not being edited by someone else
        if user and self.editing_by_id == user.id:
            return False
        
        # If session_key provided and matches, record is not being edited by someone else
        # Only check session_key if it's not empty (empty session_key means new session)
        if session_key and session_key.strip() and self.editing_session_key == session_key:
            return False
        
        # Record is being edited by someone else
        return True


class LockableModel(EditableModel):
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


class User(AbstractUser, MetadataModel, EditableModel):
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


class Company(TimeStampedModel, ActivatableModel, MetadataModel, EditableModel):
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


class CompanyUnit(CompanyScopedModel, TimeStampedModel, ActivatableModel, MetadataModel, EditableModel):
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


class AccessLevel(TimeStampedModel, ActivatableModel, MetadataModel, EditableModel):
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


class AccessLevelPermission(TimeStampedModel, MetadataModel, EditableModel):
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


class GroupProfile(TimeStampedModel, ActivatableModel, MetadataModel, EditableModel):
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


class SMTPServer(TimeStampedModel, ActivatableModel, MetadataModel, EditableModel):
    """
    SMTP Server configuration for sending email notifications.
    Global configuration (not company-scoped).
    """
    name = models.CharField(
        max_length=120,
        unique=True,
        verbose_name=_("Server Name"),
        help_text=_("A descriptive name for this SMTP server configuration"),
    )
    host = models.CharField(
        max_length=255,
        verbose_name=_("SMTP Host"),
        help_text=_("SMTP server hostname or IP address (e.g., smtp.gmail.com)"),
    )
    port = models.PositiveIntegerField(
        default=587,
        verbose_name=_("SMTP Port"),
        help_text=_("SMTP server port (usually 587 for TLS, 465 for SSL, 25 for plain)"),
    )
    use_tls = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=1,
        verbose_name=_("Use TLS"),
        help_text=_("Enable TLS encryption for SMTP connection"),
    )
    use_ssl = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Use SSL"),
        help_text=_("Enable SSL encryption for SMTP connection (usually for port 465)"),
    )
    username = models.CharField(
        max_length=255,
        verbose_name=_("Username"),
        help_text=_("SMTP authentication username (usually email address)"),
    )
    password = models.CharField(
        max_length=255,
        verbose_name=_("Password"),
        help_text=_("SMTP authentication password or app-specific password"),
    )
    from_email = models.EmailField(
        max_length=255,
        verbose_name=_("From Email"),
        help_text=_("Default sender email address"),
    )
    from_name = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("From Name"),
        help_text=_("Default sender name (optional)"),
    )
    timeout = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Connection Timeout"),
        help_text=_("Connection timeout in seconds"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Additional notes about this SMTP configuration"),
    )

    class Meta:
        verbose_name = _("SMTP Server")
        verbose_name_plural = _("SMTP Servers")
        ordering = ("name",)

    def __str__(self) -> str:
        return f"{self.name} ({self.host}:{self.port})"

    def get_connection_config(self) -> dict:
        """Get SMTP connection configuration dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'use_tls': bool(self.use_tls),
            'use_ssl': bool(self.use_ssl),
            'username': self.username,
            'password': self.password,
            'timeout': self.timeout,
        }


class SectionRegistry(TimeStampedModel, ActivatableModel, MetadataModel, SortableModel):
    """
    Central registry for all application sections/features.
    Each section has a unique 6-digit code (XXYYZZ format) and nickname.
    Used by the Entity Reference System for cross-module action execution.
    """
    SECTION_CODE_VALIDATOR = RegexValidator(
        regex=r"^\d{6}$",
        message=_("Section code must be exactly 6 digits."),
    )
    
    section_code = models.CharField(
        max_length=6,
        unique=True,
        validators=[SECTION_CODE_VALIDATOR],
        verbose_name=_("Section Code"),
        help_text=_("6-digit code in XXYYZZ format (module + menu + submenu)"),
    )
    nickname = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Nickname"),
        help_text=_("Unique identifier for this section (e.g., 'users', 'purchase_requests')"),
    )
    module_code = models.CharField(
        max_length=2,
        validators=[NUMERIC_CODE_VALIDATOR],
        verbose_name=_("Module Code"),
        help_text=_("2-digit module number (00=dashboard, 01=shared, 02=inventory, etc.)"),
    )
    menu_number = models.CharField(
        max_length=2,
        validators=[NUMERIC_CODE_VALIDATOR],
        verbose_name=_("Menu Number"),
        help_text=_("2-digit menu number within module"),
    )
    submenu_number = models.CharField(
        max_length=2,
        validators=[NUMERIC_CODE_VALIDATOR],
        null=True,
        blank=True,
        verbose_name=_("Submenu Number"),
        help_text=_("2-digit submenu number (NULL if no submenu)"),
    )
    name = models.CharField(
        max_length=180,
        verbose_name=_("Name"),
        help_text=_("Display name in local language"),
    )
    name_en = models.CharField(
        max_length=180,
        blank=True,
        verbose_name=_("Name (English)"),
        help_text=_("Display name in English"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
    )
    module = models.CharField(
        max_length=30,
        verbose_name=_("Module"),
        help_text=_("Module identifier (e.g., 'shared', 'inventory')"),
    )
    app_label = models.CharField(
        max_length=30,
        verbose_name=_("App Label"),
        help_text=_("Django app label (e.g., 'shared', 'inventory')"),
    )
    list_url_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("List URL Name"),
        help_text=_("Django URL name for list view (e.g., 'inventory:items')"),
    )
    detail_url_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Detail URL Name"),
        help_text=_("Django URL name for detail/edit view (e.g., 'inventory:item_edit')"),
    )
    activated_at = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Section Registry")
        verbose_name_plural = _("Section Registry")
        ordering = ("module_code", "menu_number", "submenu_number", "sort_order")
        indexes = [
            models.Index(fields=["section_code"], name="section_registry_code_idx"),
            models.Index(fields=["nickname"], name="section_registry_nickname_idx"),
            models.Index(fields=["module_code", "is_enabled", "sort_order"], name="section_registry_module_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.section_code} - {self.name}"


class ActionRegistry(TimeStampedModel, ActivatableModel, MetadataModel, SortableModel):
    """
    Registry of actions available for each section.
    Actions define what can be done in a section (e.g., show, approve, delete).
    Used by the Entity Reference System for dynamic action execution.
    """
    section = models.ForeignKey(
        SectionRegistry,
        on_delete=models.CASCADE,
        related_name="actions",
        verbose_name=_("Section"),
    )
    action_name = models.CharField(
        max_length=50,
        verbose_name=_("Action Name"),
        help_text=_("Action identifier (e.g., 'show', 'approve', 'delete')"),
    )
    action_label = models.CharField(
        max_length=180,
        verbose_name=_("Action Label"),
        help_text=_("Human-readable label for the action"),
    )
    action_label_en = models.CharField(
        max_length=180,
        blank=True,
        null=True,
        verbose_name=_("Action Label (English)"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
    )
    handler_function = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Handler Function"),
        help_text=_("Fully qualified path to handler (e.g., 'inventory.views.requests.PurchaseRequestApproveView')"),
    )
    url_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("URL Name"),
        help_text=_("Django URL name for this action (e.g., 'inventory:purchase_request_approve')"),
    )
    parameter_schema = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Parameter Schema"),
        help_text=_("JSON schema defining required/optional parameters"),
    )
    permission_required = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Permission Required"),
        help_text=_("Feature permission code required for this action"),
    )
    requires_confirmation = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Requires Confirmation"),
        help_text=_("Whether this action requires user confirmation"),
    )
    is_destructive = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Is Destructive"),
        help_text=_("Flag indicating if this is a destructive action"),
    )

    class Meta:
        verbose_name = _("Action Registry")
        verbose_name_plural = _("Action Registry")
        ordering = ("section", "sort_order", "action_name")
        constraints = [
            models.UniqueConstraint(
                fields=("section", "action_name"),
                name="action_registry_section_action_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["section", "is_enabled", "sort_order"], name="action_registry_section_idx"),
            models.Index(fields=["action_name"], name="action_registry_name_idx"),
            models.Index(fields=["url_name"], name="action_registry_url_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.section.section_code}:{self.action_name} - {self.action_label}"


class Notification(TimeStampedModel):
    """User notification model for storing notifications in database."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("User"),
    )
    company = models.ForeignKey(
        "Company",
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
        verbose_name=_("Company"),
    )
    notification_type = models.CharField(
        max_length=50,
        verbose_name=_("Notification Type"),
        help_text=_("Type of notification (e.g., 'approval_pending', 'approved')"),
    )
    notification_key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Notification Key"),
        help_text=_("Unique key for this notification (e.g., 'approval_pending_purchase_1')"),
    )
    message = models.TextField(
        verbose_name=_("Message"),
        help_text=_("Notification message text"),
    )
    url_name = models.CharField(
        max_length=100,
        verbose_name=_("URL Name"),
        help_text=_("Django URL name to redirect to"),
    )
    count = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Count"),
        help_text=_("Number of items in this notification"),
    )
    is_read = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Is Read"),
        help_text=_("Whether this notification has been read"),
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Read At"),
        help_text=_("When this notification was read"),
    )
    
    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "is_read", "created_at"], name="notification_user_read_idx"),
            models.Index(fields=["company", "is_read"], name="notification_company_read_idx"),
            models.Index(fields=["notification_key"], name="notification_key_idx"),
        ]
    
    def __str__(self) -> str:
        return f"{self.user.username} - {self.message} ({'Read' if self.is_read else 'Unread'})"
    
    def mark_as_read(self, user=None):
        """Mark this notification as read."""
        from django.utils import timezone
        self.is_read = 1
        self.read_at = timezone.now()
        if user:
            self.edited_by = user
        self.save(update_fields=['is_read', 'read_at', 'edited_by', 'edited_at'])
    
    def mark_as_unread(self, user=None):
        """Mark this notification as unread."""
        self.is_read = 0
        self.read_at = None
        if user:
            self.edited_by = user
        self.save(update_fields=['is_read', 'read_at', 'edited_by', 'edited_at'])

