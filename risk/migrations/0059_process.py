# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-18 14:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0058_department_manager'),
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('owner', models.CharField(max_length=50)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.Department')),
            ],
        ),
    ]
