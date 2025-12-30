# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('production', '0026_add_work_line_to_process_operation'),
    ]

    operations = [
        migrations.AddField(
            model_name='transfertoline',
            name='qc_approved_by',
            field=models.ForeignKey(
                blank=True,
                help_text='User who can approve QC for this transfer request (only for scrap replacement)',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='qc_approved_transfers',
                to=settings.AUTH_USER_MODEL,
                verbose_name='QC Approver',
            ),
        ),
        migrations.AddField(
            model_name='transfertoline',
            name='qc_status',
            field=models.CharField(
                choices=[
                    ('not_required', 'Not Required'),
                    ('pending_approval', 'Pending Approval'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ],
                default='not_required',
                help_text='Quality Control approval status for scrap replacement transfers',
                max_length=20,
                verbose_name='QC Status',
            ),
        ),
        migrations.AlterField(
            model_name='transfertoline',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending_approval', 'Pending Approval'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                    ('pending_qc_approval', 'Pending QC Approval'),
                ],
                default='pending_approval',
                max_length=20,
            ),
        ),
    ]

