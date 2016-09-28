# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-18 08:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0011_auto_20160718_0841'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessEnabler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('freq_effect', models.CharField(choices=[('H', 'High'), ('M', 'Medium'), ('L', 'Low')], default='M', max_length=1)),
                ('impact_effect', models.CharField(choices=[('H', 'High'), ('M', 'Medium'), ('L', 'Low')], default='M', max_length=1)),
                ('is_essential_control', models.BooleanField(default=True)),
                ('process', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.ControlProcess')),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.Scenario')),
            ],
        ),
        migrations.AddField(
            model_name='scenario',
            name='process_enabler',
            field=models.ManyToManyField(through='risk.ProcessEnabler', to='risk.ControlProcess'),
        ),
    ]
