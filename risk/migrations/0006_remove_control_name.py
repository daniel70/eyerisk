# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-10 12:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0005_control_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='control',
            name='name',
        ),
    ]
