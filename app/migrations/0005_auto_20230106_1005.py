# Generated by Django 3.2.16 on 2023-01-06 10:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20230106_0940'),
    ]

    operations = [
        migrations.AlterField(
            model_name='key',
            name='expired_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 5, 10, 5, 18, 445233)),
        ),
        migrations.AlterField(
            model_name='key',
            name='is_login',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='trns',
            name='pnr_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 2, 5, 10, 5, 18, 446124)),
        ),
    ]
