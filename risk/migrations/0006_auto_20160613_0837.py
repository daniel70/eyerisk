# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-13 08:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0005_auto_20160613_0835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='control',
            name='practice_governance',
            field=models.TextField(blank=True),
        ),
    ]
