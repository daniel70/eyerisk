# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-02 15:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0043_auto_20161102_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='processenableranswer',
            name='effect_on_frequency',
            field=models.CharField(blank=True, choices=[('H', 'High'), ('M', 'Medium'), ('L', 'Low')], default='', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='processenableranswer',
            name='effect_on_impact',
            field=models.CharField(blank=True, choices=[('H', 'High'), ('M', 'Medium'), ('L', 'Low')], default='', max_length=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='processenableranswer',
            name='essential_control',
            field=models.CharField(blank=True, choices=[('Y', 'Y'), ('N', 'N')], default='', max_length=1),
            preserve_default=False,
        ),
    ]
