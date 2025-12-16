# Generated manually for seeding initial Tafsili Types

from django.db import migrations
from django.utils.translation import gettext_lazy as _


def create_initial_tafsili_types(apps, schema_editor):
    """Create initial Tafsili Types for existing companies."""
    TafsiliType = apps.get_model('accounting', 'TafsiliType')
    Company = apps.get_model('shared', 'Company')
    
    initial_types = [
        {'public_code': '1', 'name': 'مشتری', 'name_en': 'Customer', 'sort_order': 1},
        {'public_code': '2', 'name': 'فروشنده', 'name_en': 'Supplier', 'sort_order': 2},
        {'public_code': '3', 'name': 'پرسنل', 'name_en': 'Employee', 'sort_order': 3},
        {'public_code': '4', 'name': 'پروژه', 'name_en': 'Project', 'sort_order': 4},
        {'public_code': '5', 'name': 'مرکز هزینه', 'name_en': 'Cost Center', 'sort_order': 5},
        {'public_code': '6', 'name': 'حساب بانکی', 'name_en': 'Bank Account', 'sort_order': 6},
        {'public_code': '7', 'name': 'چک', 'name_en': 'Check', 'sort_order': 7},
        {'public_code': '8', 'name': 'سایر', 'name_en': 'Other', 'sort_order': 8},
    ]
    
    # Create types for each existing company
    for company in Company.objects.all():
        for type_data in initial_types:
            # Check if type already exists for this company
            if not TafsiliType.objects.filter(
                company=company,
                public_code=type_data['public_code']
            ).exists():
                TafsiliType.objects.create(
                    company=company,
                    **type_data,
                    is_enabled=1
                )


def reverse_create_initial_tafsili_types(apps, schema_editor):
    """Remove initial Tafsili Types."""
    TafsiliType = apps.get_model('accounting', 'TafsiliType')
    
    # Remove only the initial types (by public_code)
    initial_codes = ['1', '2', '3', '4', '5', '6', '7', '8']
    TafsiliType.objects.filter(public_code__in=initial_codes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0015_add_tafsili_type_model'),
        ('shared', '0015_add_primary_groups_to_user'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_tafsili_types,
            reverse_create_initial_tafsili_types
        ),
    ]

