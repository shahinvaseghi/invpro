# Generated manually for adding ProcessOperation and ProcessOperationMaterial models

from decimal import Decimal
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0028_move_workline_to_production'),
        ('production', '0021_performancerecord_performancerecordperson_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessOperation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('enabled_at', models.DateTimeField(blank=True, null=True)),
                ('disabled_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('company_code', models.CharField(blank=True, editable=False, max_length=8, validators=[django.core.validators.RegexValidator(message='Only numeric characters are allowed.', regex='^\\d+$')])),
                ('name', models.CharField(blank=True, help_text='Name of the operation', max_length=255)),
                ('description', models.CharField(blank=True, help_text='Description of the operation', max_length=500)),
                ('sequence_order', models.PositiveSmallIntegerField(default=1, help_text='Execution order (can be same for parallel operations)')),
                ('labor_minutes_per_unit', models.DecimalField(decimal_places=6, help_text='Labor minutes required per unit', max_digits=18, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('machine_minutes_per_unit', models.DecimalField(decimal_places=6, default=Decimal('0'), help_text='Machine minutes required per unit', max_digits=18, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('notes', models.TextField(blank=True, help_text='Additional notes for this operation')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='shared.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('disabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_disabled', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_edited', to=settings.AUTH_USER_MODEL)),
                ('enabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_enabled', to=settings.AUTH_USER_MODEL)),
                ('process', models.ForeignKey(help_text='Production process this operation belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='operations', to='production.process')),
            ],
            options={
                'verbose_name': 'Process Operation',
                'verbose_name_plural': 'Process Operations',
                'ordering': ('company', 'process', 'sequence_order', 'id'),
            },
        ),
        migrations.CreateModel(
            name='ProcessOperationMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('enabled_at', models.DateTimeField(blank=True, null=True)),
                ('disabled_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('company_code', models.CharField(blank=True, editable=False, max_length=8, validators=[django.core.validators.RegexValidator(message='Only numeric characters are allowed.', regex='^\\d+$')])),
                ('material_item_code', models.CharField(help_text='Material item code (cached)', max_length=16, validators=[django.core.validators.RegexValidator(message='Only numeric characters are allowed.', regex='^\\d+$')])),
                ('quantity_used', models.DecimalField(decimal_places=6, help_text='Quantity used in this operation', max_digits=18, validators=[django.core.validators.MinValueValidator(Decimal('0'))])),
                ('unit', models.CharField(help_text='Unit of measurement (cached from BOM material)', max_length=50)),
                ('bom_material', models.ForeignKey(help_text='BOM material being used', on_delete=django.db.models.deletion.PROTECT, related_name='operation_usages', to='production.bommaterial')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='shared.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('disabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_disabled', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_edited', to=settings.AUTH_USER_MODEL)),
                ('enabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_enabled', to=settings.AUTH_USER_MODEL)),
                ('material_item', models.ForeignKey(help_text='Material item (cached from BOM material)', on_delete=django.db.models.deletion.PROTECT, related_name='operation_materials', to='inventory.item')),
                ('operation', models.ForeignKey(help_text='Production operation', on_delete=django.db.models.deletion.CASCADE, related_name='operation_materials', to='production.processoperation')),
            ],
            options={
                'verbose_name': 'Process Operation Material',
                'verbose_name_plural': 'Process Operation Materials',
                'ordering': ('operation', 'id'),
            },
        ),
        migrations.AddIndex(
            model_name='processoperation',
            index=models.Index(fields=['process', 'sequence_order'], name='production__process_sequence_idx'),
        ),
        migrations.AddConstraint(
            model_name='processoperationmaterial',
            constraint=models.UniqueConstraint(fields=('operation', 'bom_material'), name='production_operation_material_unique'),
        ),
    ]

