# Generated manually on 2025-12-02

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shared', '0014_add_editable_model_fields'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0007_add_income_expense_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('enabled_at', models.DateTimeField(blank=True, null=True)),
                ('disabled_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('company_code', models.CharField(blank=True, editable=False, max_length=8, validators=[django.core.validators.RegexValidator(message='Only numeric characters are allowed.', regex='^\\d+$')])),
                ('party_type', models.CharField(choices=[('customer', 'مشتری'), ('supplier', 'تأمین\u200cکننده'), ('employee', 'کارمند'), ('other', 'سایر')], help_text='Type of party', max_length=20)),
                ('party_code', models.CharField(blank=True, editable=False, help_text='Party code (auto-generated if not provided)', max_length=10, validators=[django.core.validators.RegexValidator(message='Only numeric characters are allowed.', regex='^\\d+$')])),
                ('party_name', models.CharField(help_text='Party name (Persian)', max_length=200)),
                ('party_name_en', models.CharField(blank=True, help_text='Party name (English)', max_length=200)),
                ('national_id', models.CharField(blank=True, help_text='National ID / Company Registration Number', max_length=20)),
                ('tax_id', models.CharField(blank=True, help_text='Tax ID', max_length=20)),
                ('address', models.TextField(blank=True, help_text='Address')),
                ('phone', models.CharField(blank=True, help_text='Phone number', max_length=50)),
                ('email', models.EmailField(blank=True, help_text='Email address', max_length=254)),
                ('contact_person', models.CharField(blank=True, help_text='Contact person name', max_length=200)),
                ('notes', models.TextField(blank=True, help_text='Additional notes')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='shared.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('disabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_disabled', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_edited', to=settings.AUTH_USER_MODEL)),
                ('enabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_enabled', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'طرف حساب',
                'verbose_name_plural': 'طرف حساب\u200cها',
                'ordering': ('company', 'party_type', 'sort_order', 'party_code'),
            },
        ),
        migrations.CreateModel(
            name='PartyAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('enabled_at', models.DateTimeField(blank=True, null=True)),
                ('disabled_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('sort_order', models.PositiveSmallIntegerField(default=0)),
                ('company_code', models.CharField(blank=True, editable=False, max_length=8, validators=[django.core.validators.RegexValidator(message='Only numeric characters are allowed.', regex='^\\d+$')])),
                ('account_code', models.CharField(blank=True, editable=False, help_text='Cached account code', max_length=30)),
                ('account_name', models.CharField(blank=True, editable=False, help_text='Cached account name', max_length=200)),
                ('is_primary', models.PositiveSmallIntegerField(default=0, help_text='Primary account for this party (1=Yes, 0=No)')),
                ('notes', models.TextField(blank=True, help_text='Additional notes about this account')),
                ('account', models.ForeignKey(help_text='Tafsili account for this party', limit_choices_to={'account_level': 3}, on_delete=django.db.models.deletion.PROTECT, related_name='party_accounts', to='accounting.account')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='shared.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('disabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_disabled', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_edited', to=settings.AUTH_USER_MODEL)),
                ('enabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_enabled', to=settings.AUTH_USER_MODEL)),
                ('party', models.ForeignKey(help_text='Party this account belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='accounting.party')),
            ],
            options={
                'verbose_name': 'حساب طرف حساب',
                'verbose_name_plural': 'حساب\u200cهای طرف حساب',
                'ordering': ('company', 'party', '-is_primary', 'account_code'),
            },
        ),
        migrations.AddConstraint(
            model_name='party',
            constraint=models.UniqueConstraint(fields=('company', 'party_code'), name='accounting_party_code_unique'),
        ),
        migrations.AddConstraint(
            model_name='party',
            constraint=models.UniqueConstraint(fields=('company', 'party_name'), name='accounting_party_name_unique'),
        ),
        migrations.AddConstraint(
            model_name='partyaccount',
            constraint=models.UniqueConstraint(fields=('company', 'party', 'account'), name='accounting_party_account_unique'),
        ),
    ]

