# Generated by Django 2.2 on 2019-05-03 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smarttm_web', '0015_auto_20190503_1236'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='meeting_date',
            field=models.DateField(verbose_name='Meeting Date'),
        ),
    ]
