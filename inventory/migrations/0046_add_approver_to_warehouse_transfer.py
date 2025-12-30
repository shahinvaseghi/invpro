# Generated migration to add approver field to IssueWarehouseTransfer

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0045_add_item_supply_planning_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='issuewarehousetransfer',
            name='approver',
            field=models.ForeignKey(
                blank=True,
                help_text='User who can approve this warehouse transfer',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='warehouse_transfers_to_approve',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Approver',
            ),
        ),
    ]

