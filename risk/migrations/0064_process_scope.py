# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-05 11:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0063_auto_20161203_0058'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='scope',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]