# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-28 13:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0077_auto_20171128_1254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='detection',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='duration',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='time_lag',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='timing',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]