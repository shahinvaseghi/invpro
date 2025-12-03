# Generated manually
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0025_add_scrap_replacement_to_transfer'),
    ]

    operations = [
        migrations.AddField(
            model_name='processoperation',
            name='work_line',
            field=models.ForeignKey(
                blank=True,
                help_text='Work line where this operation is performed',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='process_operations',
                to='production.workline',
            ),
        ),
    ]

