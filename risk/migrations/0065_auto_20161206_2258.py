# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-06 22:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0064_process_scope'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='department',
            unique_together=set([('company', 'name')]),
        ),
    ]
