"""
Ticketing module models.

This module provides comprehensive ticket management with dynamic form builder capabilities.
All models follow the standard invproj architecture with multi-company support and auditing.
"""
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from shared.models import (
    ActivatableModel,
    CompanyScopedModel,
    ENABLED_FLAG_CHOICES,
    LockableModel,
    MetadataModel,
    NUMERIC_CODE_VALIDATOR,
    SortableModel,
    TimeStampedModel,
    User,
)

from .utils.codes import generate_sequential_code, generate_template_code, generate_ticket_code


# Base model for ticketing
class TicketingBaseModel(
    CompanyScopedModel,
    TimeStampedModel,
    ActivatableModel,
    MetadataModel,
):
    """Base model for all ticketing models."""

    class Meta:
        abstract = True


class TicketingSortableModel(TicketingBaseModel, SortableModel):
    """Base model for sortable ticketing models."""

    class Meta:
        abstract = True


# ============================================================================
# Master Data Models
# ============================================================================


class TicketCategory(TicketingSortableModel):
    """Category or subcategory for tickets with hierarchical support."""

    public_code = models.CharField(
        max_length=10,
        validators=[NUMERIC_CODE_VALIDATOR],
        verbose_name=_("Category Code"),
    )
    name = models.CharField(
        max_length=120,
        verbose_name=_("Name"),
    )
    name_en = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("Name (English)"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
    )
    parent_category = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
        verbose_name=_("Parent Category"),
    )

    class Meta:
        verbose_name = _("Ticket Category")
        verbose_name_plural = _("Ticket Categories")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="ticketing_category_company_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="ticketing_category_company_name_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["company", "is_enabled", "sort_order"],
                name="tkt_cat_comp_enabled_ord_idx",
            ),
        ]
        ordering = ("company", "sort_order", "public_code")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate public_code if not set."""
        if not self.public_code and self.company_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                field="public_code",
                width=10,
            )
        super().save(*args, **kwargs)


class TicketPriority(TicketingSortableModel):
    """Priority levels for tickets with SLA support."""

    public_code = models.CharField(
        max_length=10,
        validators=[NUMERIC_CODE_VALIDATOR],
        verbose_name=_("Priority Code"),
    )
    name = models.CharField(
        max_length=120,
        verbose_name=_("Name"),
    )
    name_en = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("Name (English)"),
    )
    priority_level = models.PositiveSmallIntegerField(
        default=3,
        verbose_name=_("Priority Level"),
        help_text=_("Numeric level (1=highest, 5=lowest) for sorting"),
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name=_("Color"),
        help_text=_("Hex color code for UI display (e.g., '#ff0000')"),
    )
    sla_hours = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("SLA Hours"),
        help_text=_("Service Level Agreement hours for response time"),
    )

    class Meta:
        verbose_name = _("Ticket Priority")
        verbose_name_plural = _("Ticket Priorities")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "public_code"),
                name="ticketing_priority_company_public_code_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "name"),
                name="ticketing_priority_company_name_unique",
            ),
            models.UniqueConstraint(
                fields=("company", "priority_level"),
                name="ticketing_priority_company_level_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["company", "priority_level"],
                name="tkt_priority_comp_level_idx",
            ),
        ]
        ordering = ("company", "priority_level", "sort_order")

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate public_code if not set."""
        if not self.public_code and self.company_id:
            self.public_code = generate_sequential_code(
                self.__class__,
                company_id=self.company_id,
                field="public_code",
                width=10,
            )
        super().save(*args, **kwargs)


# ============================================================================
# Permission Models
# ============================================================================


class TicketCategoryPermission(TicketingBaseModel):
    """Permissions for users/groups to create/respond/close tickets in categories."""

    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name=_("Category"),
    )
    category_code = models.CharField(
        max_length=10,
        verbose_name=_("Category Code"),
        help_text=_("Cached category code"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ticket_category_permissions",
        verbose_name=_("User"),
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ticket_category_permissions",
        verbose_name=_("Group"),
    )
    can_create = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Can Create"),
    )
    can_respond = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Can Respond"),
    )
    can_close = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Can Close"),
    )

    class Meta:
        verbose_name = _("Category Permission")
        verbose_name_plural = _("Category Permissions")
        constraints = [
            models.UniqueConstraint(
                fields=("category", "user"),
                condition=models.Q(user__isnull=False),
                name="ticketing_category_permission_user_unique",
            ),
            models.UniqueConstraint(
                fields=("category", "group"),
                condition=models.Q(group__isnull=False),
                name="ticketing_category_permission_group_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["category", "can_create"],
                name="tkt_cat_perm_cat_create_idx",
            ),
            models.Index(
                fields=["category", "can_respond"],
                name="tkt_cat_perm_cat_resp_idx",
            ),
            models.Index(
                fields=["category", "can_close"],
                name="tkt_cat_perm_cat_close_idx",
            ),
            models.Index(
                fields=["user", "can_create"],
                name="tkt_cat_perm_user_create_idx",
            ),
            models.Index(
                fields=["user", "can_respond"],
                name="tkt_cat_perm_user_resp_idx",
            ),
            models.Index(
                fields=["user", "can_close"],
                name="tkt_cat_perm_user_close_idx",
            ),
            models.Index(
                fields=["group", "can_create"],
                name="tkt_cat_perm_grp_create_idx",
            ),
            models.Index(
                fields=["group", "can_respond"],
                name="tkt_cat_perm_grp_resp_idx",
            ),
            models.Index(
                fields=["group", "can_close"],
                name="tkt_cat_perm_grp_close_idx",
            ),
        ]

    def __str__(self) -> str:
        entity = self.user.username if self.user else (self.group.name if self.group else "Unknown")
        return f"{self.category.name} - {entity}"

    def save(self, *args, **kwargs):
        """Auto-populate category_code."""
        if self.category and not self.category_code:
            self.category_code = self.category.public_code
        super().save(*args, **kwargs)

    def clean(self):
        """Ensure either user or group is set, but not both."""
        from django.core.exceptions import ValidationError

        if not self.user and not self.group:
            raise ValidationError(_("Either user or group must be set."))
        if self.user and self.group:
            raise ValidationError(_("Cannot set both user and group."))


# ============================================================================
# Template Models
# ============================================================================


class TicketTemplate(TicketingSortableModel):
    """Template for creating tickets with dynamic fields."""

    template_code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_("Template Code"),
        help_text=_("Auto-generated template identifier (format: TMP-YYYYMMDD-XXXXXX)"),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Name"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="templates",
        verbose_name=_("Category"),
    )
    category_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Category Code"),
        help_text=_("Cached category code"),
    )
    default_priority = models.ForeignKey(
        TicketPriority,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="templates",
        verbose_name=_("Default Priority"),
    )
    default_priority_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Default Priority Code"),
        help_text=_("Cached default priority code"),
    )

    class Meta:
        verbose_name = _("Ticket Template")
        verbose_name_plural = _("Ticket Templates")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "template_code"),
                name="ticketing_template_company_code_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["company", "category", "is_enabled", "sort_order"],
                name="tkt_tmpl_comp_cat_enabled_idx",
            ),
        ]
        ordering = ("company", "sort_order", "template_code")

    def __str__(self) -> str:
        return f"{self.template_code} - {self.name}"

    def save(self, *args, **kwargs):
        """Auto-generate template_code if not set."""
        if not self.template_code:
            self.template_code = generate_template_code(self.company_id)
        if self.category and not self.category_code:
            self.category_code = self.category.public_code
        if self.default_priority and not self.default_priority_code:
            self.default_priority_code = self.default_priority.public_code
        super().save(*args, **kwargs)


class TicketTemplateField(TicketingBaseModel):
    """Dynamic field definition for ticket templates."""

    FIELD_TYPE_CHOICES = [
        ("short_text", _("Short Text")),
        ("long_text", _("Long Text")),
        ("radio", _("Radio Button")),
        ("dropdown", _("Dropdown")),
        ("file_upload", _("File Upload")),
        ("reference", _("Reference")),
        ("checkbox", _("Checkbox")),
        ("date", _("Date")),
        ("time", _("Time")),
        ("datetime", _("DateTime")),
        ("number", _("Number")),
        ("email", _("Email")),
        ("url", _("URL")),
        ("phone", _("Phone")),
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

    template = models.ForeignKey(
        TicketTemplate,
        on_delete=models.CASCADE,
        related_name="fields",
        verbose_name=_("Template"),
    )
    template_code = models.CharField(
        max_length=30,
        verbose_name=_("Template Code"),
        help_text=_("Cached template code"),
    )
    field_name = models.CharField(
        max_length=255,
        verbose_name=_("Field Name"),
        help_text=_("Field label/name for display"),
    )
    field_type = models.CharField(
        max_length=30,
        choices=FIELD_TYPE_CHOICES,
        verbose_name=_("Field Type"),
    )
    field_key = models.CharField(
        max_length=100,
        verbose_name=_("Field Key"),
        help_text=_("Unique identifier for the field within template (e.g., 'item_code', 'description')"),
    )
    is_required = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Is Required"),
    )
    default_value = models.TextField(
        blank=True,
        verbose_name=_("Default Value"),
    )
    field_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Field Order"),
        help_text=_("Display order (row position) in the form"),
    )
    help_text = models.TextField(
        blank=True,
        verbose_name=_("Help Text"),
    )
    validation_rules = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Validation Rules"),
        help_text=_("Validation rules (min/max length, regex patterns, etc.)"),
    )
    field_config = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Field Config"),
        help_text=_("Field-specific configuration (e.g., for reference fields: entity types, for file upload: allowed types, max size)"),
    )

    class Meta:
        verbose_name = _("Template Field")
        verbose_name_plural = _("Template Fields")
        constraints = [
            models.UniqueConstraint(
                fields=("template", "field_key"),
                name="ticketing_template_field_template_key_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["template", "field_order"],
                name="tkt_tmpl_field_order_idx",
            ),
        ]
        ordering = ("template", "field_order", "id")

    def __str__(self) -> str:
        return f"{self.template.name} - {self.field_name}"

    def save(self, *args, **kwargs):
        """Auto-populate template_code."""
        if self.template and not self.template_code:
            self.template_code = self.template.template_code
        super().save(*args, **kwargs)


class TicketTemplateFieldOption(TicketingBaseModel):
    """Options for radio, dropdown, or multi_select field types."""

    template_field = models.ForeignKey(
        TicketTemplateField,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name=_("Template Field"),
    )
    template = models.ForeignKey(
        TicketTemplate,
        on_delete=models.CASCADE,
        related_name="field_options",
        verbose_name=_("Template"),
        help_text=_("Cached template reference"),
    )
    option_value = models.CharField(
        max_length=255,
        verbose_name=_("Option Value"),
        help_text=_("Option value (stored value)"),
    )
    option_label = models.CharField(
        max_length=255,
        verbose_name=_("Option Label"),
        help_text=_("Option label (displayed text)"),
    )
    option_order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Option Order"),
        help_text=_("Display order in dropdown/radio list"),
    )
    is_default = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Is Default"),
        help_text=_("Whether this option is the default selection"),
    )

    class Meta:
        verbose_name = _("Template Field Option")
        verbose_name_plural = _("Template Field Options")
        constraints = [
            models.UniqueConstraint(
                fields=("template_field", "option_value"),
                name="ticketing_template_field_option_field_value_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["template_field", "option_order"],
                name="tkt_tmpl_field_opt_order_idx",
            ),
        ]
        ordering = ("template_field", "option_order", "id")

    def __str__(self) -> str:
        return f"{self.template_field.field_name} - {self.option_label}"

    def save(self, *args, **kwargs):
        """Auto-populate template reference."""
        if self.template_field and not self.template_id:
            self.template = self.template_field.template
        super().save(*args, **kwargs)


class TicketTemplatePermission(TicketingBaseModel):
    """Permissions for users/groups to create/respond/close tickets using templates."""

    template = models.ForeignKey(
        TicketTemplate,
        on_delete=models.CASCADE,
        related_name="permissions",
        verbose_name=_("Template"),
    )
    template_code = models.CharField(
        max_length=30,
        verbose_name=_("Template Code"),
        help_text=_("Cached template code"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ticket_template_permissions",
        verbose_name=_("User"),
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ticket_template_permissions",
        verbose_name=_("Group"),
    )
    can_create = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Can Create"),
    )
    can_respond = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Can Respond"),
    )
    can_close = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Can Close"),
    )

    class Meta:
        verbose_name = _("Template Permission")
        verbose_name_plural = _("Template Permissions")
        constraints = [
            models.UniqueConstraint(
                fields=("template", "user"),
                condition=models.Q(user__isnull=False),
                name="ticketing_template_permission_user_unique",
            ),
            models.UniqueConstraint(
                fields=("template", "group"),
                condition=models.Q(group__isnull=False),
                name="ticketing_template_permission_group_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["template", "can_create"],
                name="tkt_tmpl_perm_tmpl_create_idx",
            ),
            models.Index(
                fields=["template", "can_respond"],
                name="tkt_tmpl_perm_tmpl_resp_idx",
            ),
            models.Index(
                fields=["template", "can_close"],
                name="tkt_tmpl_perm_tmpl_close_idx",
            ),
            models.Index(
                fields=["user", "can_create"],
                name="tkt_tmpl_perm_user_create_idx",
            ),
            models.Index(
                fields=["user", "can_respond"],
                name="tkt_tmpl_perm_user_resp_idx",
            ),
            models.Index(
                fields=["user", "can_close"],
                name="tkt_tmpl_perm_user_close_idx",
            ),
            models.Index(
                fields=["group", "can_create"],
                name="tkt_tmpl_perm_grp_create_idx",
            ),
            models.Index(
                fields=["group", "can_respond"],
                name="tkt_tmpl_perm_grp_resp_idx",
            ),
            models.Index(
                fields=["group", "can_close"],
                name="tkt_tmpl_perm_grp_close_idx",
            ),
        ]

    def __str__(self) -> str:
        entity = self.user.username if self.user else (self.group.name if self.group else "Unknown")
        return f"{self.template.name} - {entity}"

    def save(self, *args, **kwargs):
        """Auto-populate template_code."""
        if self.template and not self.template_code:
            self.template_code = self.template.template_code
        super().save(*args, **kwargs)

    def clean(self):
        """Ensure either user or group is set, but not both."""
        from django.core.exceptions import ValidationError

        if not self.user and not self.group:
            raise ValidationError(_("Either user or group must be set."))
        if self.user and self.group:
            raise ValidationError(_("Cannot set both user and group."))


# ============================================================================
# Ticket Models
# ============================================================================


class Ticket(TicketingBaseModel, LockableModel):
    """Main ticket entity."""

    STATUS_CHOICES = [
        ("open", _("Open")),
        ("in_progress", _("In Progress")),
        ("assigned", _("Assigned")),
        ("pending", _("Pending")),
        ("resolved", _("Resolved")),
        ("closed", _("Closed")),
        ("cancelled", _("Cancelled")),
    ]

    ticket_code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_("Ticket Code"),
        help_text=_("Auto-generated ticket identifier (format: TKT-YYYYMMDD-XXXXXX)"),
    )
    template = models.ForeignKey(
        TicketTemplate,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name=_("Template"),
    )
    template_code = models.CharField(
        max_length=30,
        verbose_name=_("Template Code"),
        help_text=_("Cached template code"),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
        verbose_name=_("Category"),
    )
    category_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Category Code"),
        help_text=_("Cached category code"),
    )
    priority = models.ForeignKey(
        TicketPriority,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
        verbose_name=_("Priority"),
    )
    priority_code = models.CharField(
        max_length=10,
        blank=True,
        verbose_name=_("Priority Code"),
        help_text=_("Cached priority code"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        verbose_name=_("Status"),
    )
    reported_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="reported_tickets",
        verbose_name=_("Reported By"),
    )
    reported_by_username = models.CharField(
        max_length=150,
        verbose_name=_("Reported By Username"),
        help_text=_("Cached reporter username"),
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
        verbose_name=_("Assigned To"),
    )
    assigned_to_username = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("Assigned To Username"),
        help_text=_("Cached assignee username"),
    )
    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Assigned At"),
    )
    opened_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Opened At"),
    )
    first_response_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("First Response At"),
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Resolved At"),
    )
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_tickets",
        verbose_name=_("Resolved By"),
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Closed At"),
    )
    closed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="closed_tickets",
        verbose_name=_("Closed By"),
    )
    resolution_notes = models.TextField(
        blank=True,
        verbose_name=_("Resolution Notes"),
    )
    related_entity_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Related Entity Type"),
        help_text=_("Type of related entity (e.g., 'inventory.item', 'production.order')"),
    )
    related_entity_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Related Entity ID"),
    )
    related_entity_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Related Entity Code"),
    )
    attachments = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Attachments"),
        help_text=_("Array of file attachments with metadata"),
    )

    class Meta:
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
        constraints = [
            models.UniqueConstraint(
                fields=("company", "ticket_code"),
                name="ticketing_ticket_company_code_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["company", "status", "created_at"],
                name="tkt_comp_status_created_idx",
            ),
            models.Index(
                fields=["company", "assigned_to", "status"],
                name="tkt_comp_assign_status_idx",
            ),
            models.Index(
                fields=["company", "category", "status"],
                name="tkt_comp_cat_status_idx",
            ),
            models.Index(
                fields=["company", "template", "status"],
                name="tkt_comp_tmpl_status_idx",
            ),
            models.Index(
                fields=["company", "priority", "status"],
                name="tkt_comp_pri_status_idx",
            ),
            models.Index(
                fields=["related_entity_type", "related_entity_id"],
                name="tkt_related_entity_idx",
            ),
        ]
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.ticket_code} - {self.title}"

    def save(self, *args, **kwargs):
        """Auto-generate ticket_code and populate cached fields."""
        if not self.ticket_code:
            self.ticket_code = generate_ticket_code(self.company_id)
        if self.template and not self.template_code:
            self.template_code = self.template.template_code
        if self.category and not self.category_code:
            self.category_code = self.category.public_code
        if self.priority and not self.priority_code:
            self.priority_code = self.priority.public_code
        if self.reported_by and not self.reported_by_username:
            self.reported_by_username = self.reported_by.username
        if self.assigned_to and not self.assigned_to_username:
            self.assigned_to_username = self.assigned_to.username
        super().save(*args, **kwargs)


class TicketFieldValue(TicketingBaseModel):
    """Field values for tickets (dynamic field data)."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="field_values",
        verbose_name=_("Ticket"),
    )
    ticket_code = models.CharField(
        max_length=30,
        verbose_name=_("Ticket Code"),
        help_text=_("Cached ticket code"),
    )
    template_field = models.ForeignKey(
        TicketTemplateField,
        on_delete=models.PROTECT,
        related_name="ticket_values",
        verbose_name=_("Template Field"),
    )
    template_field_key = models.CharField(
        max_length=100,
        verbose_name=_("Template Field Key"),
        help_text=_("Cached field key for quick lookup"),
    )
    field_value = models.TextField(
        blank=True,
        verbose_name=_("Field Value"),
        help_text=_("Field value (text representation, JSON for complex types)"),
    )
    field_value_json = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("Field Value JSON"),
        help_text=_("Structured field value (for reference fields, file uploads, etc.)"),
    )

    class Meta:
        verbose_name = _("Ticket Field Value")
        verbose_name_plural = _("Ticket Field Values")
        constraints = [
            models.UniqueConstraint(
                fields=("ticket", "template_field"),
                name="ticketing_ticket_field_value_ticket_field_unique",
            ),
        ]
        indexes = [
            models.Index(
                fields=["ticket"],
                name="tkt_field_val_ticket_idx",
            ),
            models.Index(
                fields=["template_field"],
                name="tkt_field_val_field_idx",
            ),
        ]
        ordering = ("ticket", "template_field__field_order")

    def __str__(self) -> str:
        return f"{self.ticket.ticket_code} - {self.template_field.field_name}"

    def save(self, *args, **kwargs):
        """Auto-populate cached fields."""
        if self.ticket and not self.ticket_code:
            self.ticket_code = self.ticket.ticket_code
        if self.template_field and not self.template_field_key:
            self.template_field_key = self.template_field.field_key
        super().save(*args, **kwargs)


class TicketComment(TicketingBaseModel):
    """Comments/notes for tickets."""

    COMMENT_TYPE_CHOICES = [
        ("comment", _("Comment")),
        ("internal_note", _("Internal Note")),
        ("status_change", _("Status Change")),
        ("assignment", _("Assignment")),
    ]

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("Ticket"),
    )
    ticket_code = models.CharField(
        max_length=30,
        verbose_name=_("Ticket Code"),
        help_text=_("Cached ticket code"),
    )
    comment_text = models.TextField(
        verbose_name=_("Comment Text"),
    )
    comment_type = models.CharField(
        max_length=20,
        choices=COMMENT_TYPE_CHOICES,
        default="comment",
        verbose_name=_("Comment Type"),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="ticket_comments",
        verbose_name=_("Author"),
    )
    author_username = models.CharField(
        max_length=150,
        verbose_name=_("Author Username"),
        help_text=_("Cached author username"),
    )
    is_internal = models.PositiveSmallIntegerField(
        choices=ENABLED_FLAG_CHOICES,
        default=0,
        verbose_name=_("Is Internal"),
        help_text=_("Internal note flag (visible only to staff)"),
    )
    attachments = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Attachments"),
        help_text=_("Array of file attachments with metadata"),
    )

    class Meta:
        verbose_name = _("Ticket Comment")
        verbose_name_plural = _("Ticket Comments")
        indexes = [
            models.Index(
                fields=["ticket", "created_at"],
                name="tkt_comment_ticket_created_idx",
            ),
        ]
        ordering = ("ticket", "created_at")

    def __str__(self) -> str:
        return f"{self.ticket.ticket_code} - {self.author_username} - {self.created_at}"

    def save(self, *args, **kwargs):
        """Auto-populate cached fields."""
        if self.ticket and not self.ticket_code:
            self.ticket_code = self.ticket.ticket_code
        if self.author and not self.author_username:
            self.author_username = self.author.username
        super().save(*args, **kwargs)


class TicketAttachment(TicketingBaseModel):
    """File attachments for tickets or comments."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="file_attachments",
        verbose_name=_("Ticket"),
    )
    comment = models.ForeignKey(
        TicketComment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="file_attachments",
        verbose_name=_("Comment"),
    )
    file_name = models.CharField(
        max_length=255,
        verbose_name=_("File Name"),
    )
    file_path = models.CharField(
        max_length=500,
        verbose_name=_("File Path"),
        help_text=_("Storage path relative to media root"),
    )
    file_size = models.BigIntegerField(
        verbose_name=_("File Size"),
        help_text=_("File size in bytes"),
    )
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("MIME Type"),
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="ticket_attachments",
        verbose_name=_("Uploaded By"),
    )
    uploaded_by_username = models.CharField(
        max_length=150,
        verbose_name=_("Uploaded By Username"),
        help_text=_("Cached uploader username"),
    )
    uploaded_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Uploaded At"),
    )

    class Meta:
        verbose_name = _("Ticket Attachment")
        verbose_name_plural = _("Ticket Attachments")
        indexes = [
            models.Index(
                fields=["ticket"],
                name="tkt_attachment_ticket_idx",
            ),
            models.Index(
                fields=["comment"],
                name="tkt_attachment_comment_idx",
            ),
        ]
        ordering = ("-uploaded_at",)

    def __str__(self) -> str:
        return f"{self.file_name}"

    def save(self, *args, **kwargs):
        """Auto-populate uploaded_by_username."""
        if self.uploaded_by and not self.uploaded_by_username:
            self.uploaded_by_username = self.uploaded_by.username
        super().save(*args, **kwargs)

    def clean(self):
        """Ensure either ticket or comment is set, but not both."""
        from django.core.exceptions import ValidationError

        if not self.ticket and not self.comment:
            raise ValidationError(_("Either ticket or comment must be set."))
        if self.ticket and self.comment:
            raise ValidationError(_("Cannot set both ticket and comment."))
