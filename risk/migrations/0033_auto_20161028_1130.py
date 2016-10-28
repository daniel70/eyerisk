# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-28 11:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0032_auto_20161028_0730'),
    ]

    operations = [
        migrations.CreateModel(
            name='RiskTypeAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('risk_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.RiskType')),
            ],
        ),
        migrations.AlterField(
            model_name='scenariocategoryanswer',
            name='threat_type',
            field=models.CharField(blank=True, help_text='The nature of the event', max_length=100),
        ),
        migrations.AddField(
            model_name='risktypeanswer',
            name='scenario_category_answer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.ScenarioCategoryAnswer'),
        ),
        migrations.AddField(
            model_name='scenariocategoryanswer',
            name='risk_type_answer',
            field=models.ManyToManyField(through='risk.RiskTypeAnswer', to='risk.RiskType'),
        ),
    ]