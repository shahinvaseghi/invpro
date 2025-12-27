# Generated manually for converting TafsiliHierarchy to TafsiliLevel

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounting', '0018_fiscalmemoryconfig_encryption_type_and_more'),
    ]

    operations = [
        # Remove old fields from TafsiliHierarchy
        migrations.RemoveField(
            model_name='tafsilihierarchy',
            name='level',
        ),
        migrations.RemoveField(
            model_name='tafsilihierarchy',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='tafsilihierarchy',
            name='tafsili_account',
        ),
        # Change verbose names
        migrations.AlterModelOptions(
            name='tafsilihierarchy',
            options={
                'ordering': ('company', 'sort_order', 'code'),
                'verbose_name': 'سطح تفضیلی',
                'verbose_name_plural': 'سطوح تفضیلی',
            },
        ),
        # Update help text for code and name fields
        migrations.AlterField(
            model_name='tafsilihierarchy',
            name='code',
            field=models.CharField(
                help_text='کد سطح تفضیلی (یکتا در شرکت)',
                max_length=50,
                validators=[django.core.validators.RegexValidator(message='Only numeric characters are allowed.', regex='^\\d+$')]
            ),
        ),
        migrations.AlterField(
            model_name='tafsilihierarchy',
            name='name',
            field=models.CharField(help_text='نام سطح تفضیلی', max_length=200),
        ),
        migrations.AlterField(
            model_name='tafsilihierarchy',
            name='name_en',
            field=models.CharField(blank=True, help_text='نام سطح تفضیلی (انگلیسی)', max_length=200),
        ),
        # Create TafsiliLevelSubAccountRelation model
        migrations.CreateModel(
            name='TafsiliLevelSubAccountRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('edited_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('enabled_at', models.DateTimeField(blank=True, null=True)),
                ('disabled_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('company_code', models.CharField(blank=True, editable=False, max_length=8, validators=[django.core.validators.RegexValidator(message='Only numeric characters are allowed.', regex='^\\d+$')])),
                ('is_primary', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=0, help_text='حساب معین اصلی (برای نمایش پیش‌فرض)')),
                ('notes', models.TextField(blank=True, help_text='یادداشت‌های اضافی')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)ss', to='shared.company')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('disabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_disabled', to=settings.AUTH_USER_MODEL)),
                ('edited_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_edited', to=settings.AUTH_USER_MODEL)),
                ('enabled_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_enabled', to=settings.AUTH_USER_MODEL)),
                ('sub_account', models.ForeignKey(help_text='حساب معین', limit_choices_to={'account_level': 2}, on_delete=django.db.models.deletion.CASCADE, related_name='tafsili_level_relations', to='accounting.account')),
                ('tafsili_level', models.ForeignKey(help_text='سطح تفضیلی', on_delete=django.db.models.deletion.CASCADE, related_name='sub_account_relations', to='accounting.tafsilihierarchy')),
            ],
            options={
                'verbose_name': 'رابطه سطح تفضیلی-معین',
                'verbose_name_plural': 'روابط سطح تفضیلی-معین',
                'ordering': ('company', 'tafsili_level', '-is_primary', 'sub_account'),
            },
        ),
        migrations.AddConstraint(
            model_name='tafsililevelsubaccountrelation',
            constraint=models.UniqueConstraint(fields=('company', 'tafsili_level', 'sub_account'), name='accounting_tafsili_level_sub_relation_unique'),
        ),
    ]

