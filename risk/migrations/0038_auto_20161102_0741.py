# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-02 07:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0037_auto_20161101_1857'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenariocategoryanswer',
            name='name',
            field=models.CharField(default='defaultname', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='scenariocategoryanswer',
            unique_together=set([('name', 'company')]),
        ),
    ]
