from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('shared', '0006_person_company_units'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_enabled', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Enabled')], default=1)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('group', models.OneToOneField(on_delete=models.CASCADE, related_name='profile', to='auth.group')),
            ],
            options={
                'verbose_name': 'Group Profile',
                'verbose_name_plural': 'Group Profiles',
            },
        ),
        migrations.AddField(
            model_name='groupprofile',
            name='access_levels',
            field=models.ManyToManyField(blank=True, related_name='groups', to='shared.accesslevel'),
        ),
    ]

