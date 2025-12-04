# Generated manually on 2025-12-04

from django.db import migrations, models
import django.db.models.deletion


def clear_destination_work_center(apps, schema_editor):
    """
    Clear destination_work_center field before changing it from WorkCenter to WorkLine.
    Since WorkCenter and WorkLine are different models, we cannot migrate the data directly.
    """
    TransferToLineItem = apps.get_model('production', 'TransferToLineItem')
    # Set all destination_work_center to None
    TransferToLineItem.objects.filter(destination_work_center__isnull=False).update(destination_work_center=None)


def reverse_clear_destination_work_center(apps, schema_editor):
    """
    Reverse migration - nothing to do as we cannot restore WorkCenter references.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0029_add_source_warehouses_jsonfield_to_bom_material'),
    ]

    operations = [
        # First, clear any existing data (WorkCenter references cannot be migrated to WorkLine)
        migrations.RunPython(
            clear_destination_work_center,
            reverse_clear_destination_work_center,
        ),
        # Then change the field to point to WorkLine
        migrations.AlterField(
            model_name='transfertolineitem',
            name='destination_work_center',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='transfer_items',
                to='production.workline',
                verbose_name='Destination Work Line',
                help_text='Work line where materials should be transferred (determines destination warehouse)',
            ),
        ),
    ]

