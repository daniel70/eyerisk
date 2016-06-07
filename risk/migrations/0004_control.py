# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-07 14:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0003_auto_20160606_1514'),
    ]

    operations = [
        migrations.CreateModel(
            name='Control',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.IntegerField()),
                ('area', models.CharField(max_length=25)),
                ('domain', models.CharField(max_length=75)),
                ('process_id', models.CharField(max_length=15)),
                ('process', models.CharField(max_length=200)),
                ('practice_id', models.CharField(max_length=15)),
                ('practice_name', models.CharField(max_length=100)),
                ('activity', models.TextField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.Document')),
            ],
            options={
                'ordering': ['document', 'ordering'],
            },
        ),
    ]
