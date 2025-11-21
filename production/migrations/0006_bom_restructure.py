# Generated manually for BOM restructure

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0005_person_processstep_machine_code_personassignment_and_more'),
        ('inventory', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Drop old BOMMaterial table
        migrations.DeleteModel(
            name='BOMMaterial',
        ),
        
        # Create new BOM model (Header)
        migrations.CreateModel(
            name='BOM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('bom_code', models.CharField(max_length=16, unique=True)),
                ('finished_item_code', models.CharField(max_length=16)),
                ('version', models.CharField(default='1.0', max_length=10)),
                ('is_active', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('effective_date', models.DateField(blank=True, null=True)),
                ('expiry_date', models.DateField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_bom_set', to='shared.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_bom_created_set', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_bom_edited_set', to=settings.AUTH_USER_MODEL)),
                ('finished_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='boms', to='inventory.item')),
            ],
            options={
                'verbose_name': 'BOM',
                'verbose_name_plural': 'BOMs',
                'ordering': ('company', 'finished_item', '-version'),
            },
        ),
        
        # Create new BOMMaterial model (Lines)
        migrations.CreateModel(
            name='BOMMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('material_item_code', models.CharField(max_length=16)),
                ('material_type', models.CharField(default='raw', max_length=30)),
                ('quantity_per_unit', models.DecimalField(decimal_places=6, max_digits=18)),
                ('unit', models.CharField(max_length=30)),
                ('scrap_allowance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('line_number', models.PositiveSmallIntegerField(default=1)),
                ('is_optional', models.PositiveSmallIntegerField(default=0)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('notes', models.TextField(blank=True)),
                ('bom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='production.bom')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='production_bommaterial_set', to='shared.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_bommaterial_created_set', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='production_bommaterial_edited_set', to=settings.AUTH_USER_MODEL)),
                ('material_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='material_in_boms', to='inventory.item')),
            ],
            options={
                'verbose_name': 'BOM Material',
                'verbose_name_plural': 'BOM Materials',
                'ordering': ('bom', 'line_number'),
            },
        ),
        
        # Add constraints
        migrations.AddConstraint(
            model_name='bom',
            constraint=models.UniqueConstraint(fields=('company', 'finished_item', 'version'), name='production_bom_unique_version'),
        ),
        migrations.AddConstraint(
            model_name='bommaterial',
            constraint=models.UniqueConstraint(fields=('bom', 'material_item'), name='production_bom_material_unique'),
        ),
        migrations.AddConstraint(
            model_name='bommaterial',
            constraint=models.UniqueConstraint(fields=('bom', 'line_number'), name='production_bom_material_line_unique'),
        ),
    ]

