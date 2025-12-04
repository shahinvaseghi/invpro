# Generated migration for adding requires_qc field to ProcessOperation model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0033_add_document_type_and_operation_to_performance_record'),
    ]

    operations = [
        migrations.AddField(
            model_name='processoperation',
            name='requires_qc',
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text='Whether this operation requires QC inspection',
                verbose_name='Requires QC',
            ),
        ),
    ]

