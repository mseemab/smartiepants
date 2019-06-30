# Generated by Django 2.2.1 on 2019-05-16 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smarttm_web', '0026_participation_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meeting_summary',
            name='meeting_date',
        ),
        migrations.AddField(
            model_name='meeting_summary',
            name='meeting',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='smarttm_web.Meeting'),
            preserve_default=False,
        ),
    ]
