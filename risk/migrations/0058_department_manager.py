# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-18 14:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0057_auto_20161118_1423'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='manager',
            field=models.CharField(default='', max_length=50),
            preserve_default=False,
        ),
    ]