# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-28 12:52
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0075_auto_20171128_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='timing',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[(1, 'Non-Critical'), (2, 'Critical')], max_length=3),
        ),
    ]
