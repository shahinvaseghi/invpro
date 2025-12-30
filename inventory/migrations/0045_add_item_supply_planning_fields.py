# Generated migration for adding supply type, planning type, lead time, and serial_in_qc fields to Item model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0044_link_existing_warehouse_transfers'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='serial_in_qc',
            field=models.PositiveSmallIntegerField(default=0, help_text='Serial tracking in QC'),
        ),
        migrations.AddField(
            model_name='item',
            name='supply_type',
            field=models.CharField(
                choices=[('buy', 'Purchasable'), ('make', 'Manufacturable')],
                default='buy',
                help_text='Supply type: Purchasable or Manufacturable',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='item',
            name='planning_type',
            field=models.CharField(
                choices=[
                    ('none', 'No Planning'),
                    ('mrp', 'MRP-based'),
                    ('reorder_point', 'Reorder Point-based'),
                ],
                default='none',
                help_text='Planning type: No Planning, MRP-based, or Reorder Point-based',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='item',
            name='lead_time',
            field=models.PositiveIntegerField(
                blank=True,
                help_text='Lead time in days',
                null=True,
            ),
        ),
    ]

