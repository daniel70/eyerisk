# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-28 07:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0031_scenariocategoryanswer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='threat_type',
            field=models.CharField(blank=True, choices=[(1, 'Malicious'), (2, 'Accidental'), (3, 'Error'), (4, 'Failure'), (5, 'Natural'), (6, 'External requirement')], help_text='The nature of the event', max_length=100),
        ),
    ]
