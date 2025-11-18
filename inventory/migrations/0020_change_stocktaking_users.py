# Generated migration to change confirmed_by and approver from Person to User
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_make_consignment_receipt_optional'),
        ('shared', '0001_initial'),
    ]

    operations = [
        # Remove old foreign keys
        migrations.RemoveField(
            model_name='stocktakingrecord',
            name='confirmed_by',
        ),
        migrations.RemoveField(
            model_name='stocktakingrecord',
            name='approver',
        ),
        # Add new foreign keys to User
        migrations.AddField(
            model_name='stocktakingrecord',
            name='confirmed_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='stocktaking_records_confirmed',
                to=settings.AUTH_USER_MODEL,
                null=True,  # Temporary, will be removed after data migration
            ),
        ),
        migrations.AddField(
            model_name='stocktakingrecord',
            name='approver',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='stocktaking_records_approved',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # Make confirmed_by not null after ensuring data is migrated
        migrations.AlterField(
            model_name='stocktakingrecord',
            name='confirmed_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='stocktaking_records_confirmed',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

