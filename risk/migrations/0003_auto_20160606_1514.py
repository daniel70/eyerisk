# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 15:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0002_auto_20160606_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selection',
            name='documents',
            field=models.ManyToManyField(blank=True, to='risk.Document'),
        ),
    ]