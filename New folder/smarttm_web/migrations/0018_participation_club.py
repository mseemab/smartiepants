# Generated by Django 2.2 on 2019-05-05 11:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smarttm_web', '0017_auto_20190503_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='participation',
            name='club',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='smarttm_web.Club'),
        ),
    ]
