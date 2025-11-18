# Generated migration to make consignment_receipt field optional
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_add_entered_price_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issueconsignmentline',
            name='consignment_receipt',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='issue_lines',
                to='inventory.receiptconsignment'
            ),
        ),
        migrations.AlterField(
            model_name='issueconsignmentline',
            name='consignment_receipt_code',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]

