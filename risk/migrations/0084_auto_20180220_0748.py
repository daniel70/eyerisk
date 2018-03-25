# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-02-20 07:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0083_auto_20180215_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='type',
            field=models.CharField(choices=[('Q', 'Company'), ('P', 'Project'), ('C', 'Change')], max_length=1),
        ),
    ]