# Generated by Django 2.2.1 on 2019-06-30 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smarttm_web', '0031_auto_20190629_1910'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summary',
            name='last_two_meetings_att',
        ),
        migrations.AddField(
            model_name='summary',
            name='last_absents',
            field=models.IntegerField(default=0),
        ),
    ]
