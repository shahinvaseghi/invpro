# Generated manually for adding bom and approved_by fields to ProductOrder

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0018_change_process_approved_by_to_user'),
        ('shared', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productorder',
            name='bom',
            field=models.ForeignKey(
                help_text='Bill of Materials for this order',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='product_orders',
                to='production.bom',
                verbose_name='BOM',
                null=True,  # Allow null initially for existing records
                blank=True,
            ),
        ),
        migrations.AddField(
            model_name='productorder',
            name='approved_by',
            field=models.ForeignKey(
                blank=True,
                help_text='User who can approve this order',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='approved_product_orders',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Approver',
            ),
        ),
        migrations.AlterField(
            model_name='productorder',
            name='process',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='product_orders',
                to='production.process',
            ),
        ),
        migrations.AlterField(
            model_name='productorder',
            name='process_code',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]

