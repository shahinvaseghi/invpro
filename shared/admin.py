from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "default_company", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "first_name_en", "last_name_en")
    list_filter = ("is_staff", "is_superuser", "is_active", "default_company")
    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            _("Additional info"),
            {
                "fields": (
                    "first_name_en",
                    "last_name_en",
                    "phone_number",
                    "mobile_number",
                    "default_company",
                    "metadata",
                )
            },
        ),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        (
            _("Additional info"),
            {
                "fields": (
                    "first_name_en",
                    "last_name_en",
                    "phone_number",
                    "mobile_number",
                    "default_company",
                )
            },
        ),
    )


@admin.register(models.Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("public_code", "display_name", "is_enabled", "country")
    list_filter = ("is_enabled", "country")
    search_fields = ("public_code", "display_name", "legal_name", "tax_id")


@admin.register(models.CompanyUnit)
class CompanyUnitAdmin(admin.ModelAdmin):
    list_display = ("public_code", "name", "company")
    list_filter = ("company", "unit_type", "is_enabled")
    search_fields = ("public_code", "name", "company__display_name")


@admin.register(models.AccessLevel)
class AccessLevelAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_enabled", "is_global")
    list_filter = ("is_enabled", "is_global")
    search_fields = ("code", "name")


@admin.register(models.AccessLevelPermission)
class AccessLevelPermissionAdmin(admin.ModelAdmin):
    list_display = ("access_level", "module_code", "resource_code", "can_view", "can_create", "can_edit")
    list_filter = ("module_code", "resource_type")
    search_fields = ("module_code", "resource_code", "access_level__code")


@admin.register(models.UserCompanyAccess)
class UserCompanyAccessAdmin(admin.ModelAdmin):
    list_display = ("user", "company", "access_level", "is_primary", "is_enabled")
    list_filter = ("access_level", "is_primary", "is_enabled")
    search_fields = ("user__username", "company__display_name")


@admin.register(models.GroupProfile)
class GroupProfileAdmin(admin.ModelAdmin):
    list_display = ("group", "is_enabled")
    list_filter = ("is_enabled",)
    search_fields = ("group__name", "description")


