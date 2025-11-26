# Generated manually to fix migration issue
# The 'notes' field should exist in ReceiptTemporary because it inherits from InventoryDocumentBase
# which includes the 'notes' field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0031_add_receipt_temporary_line'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipttemporary',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]

