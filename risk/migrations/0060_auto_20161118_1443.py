# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-18 14:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0059_process'),
    ]

    operations = [
        migrations.AlterField(
            model_name='process',
            name='name',
            field=models.CharField(max_length=80),
        ),
    ]
