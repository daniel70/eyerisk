# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-28 12:54
from __future__ import unicode_literals

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0076_auto_20171128_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='detection',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[(1, 'Slow'), (2, 'Moderate'), (3, 'Instant')], max_length=5),
        ),
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='duration',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[(1, 'Short'), (2, 'Moderate'), (3, 'Extended')], max_length=5),
        ),
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='time_lag',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, choices=[(1, 'Immediate'), (2, 'Delayed')], max_length=3),
        ),
    ]
