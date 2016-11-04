# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-02 15:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0042_auto_20161102_1513'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessEnablerAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('effect_on_frequency', models.CharField(choices=[('H', 'High'), ('M', 'Medium'), ('L', 'Low')], max_length=1, null=True)),
                ('effect_on_impact', models.CharField(choices=[('H', 'High'), ('M', 'Medium'), ('L', 'Low')], max_length=1, null=True)),
                ('essential_control', models.CharField(choices=[('Y', 'Y'), ('N', 'N')], max_length=1, null=True)),
                ('control_practice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.ControlPractice')),
                ('scenario_category_answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.ScenarioCategoryAnswer')),
            ],
        ),
        migrations.AlterField(
            model_name='scenariocategory',
            name='process_enabler',
            field=models.ManyToManyField(blank=True, related_name='process_enablers', to='risk.ControlPractice'),
        ),
    ]