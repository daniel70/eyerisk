# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-14 13:52
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0009_auto_20160614_0811'),
    ]

    operations = [
        migrations.CreateModel(
            name='Impact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)])),
                ('descriptor', models.CharField(max_length=30, unique=True)),
                ('definition', models.TextField()),
            ],
            options={
                'ordering': ['rating'],
            },
        ),
        migrations.CreateModel(
            name='Likelyhood',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(0)])),
                ('descriptor', models.CharField(max_length=30, unique=True)),
                ('definition', models.TextField()),
            ],
            options={
                'ordering': ['rating'],
            },
        ),
        migrations.CreateModel(
            name='SelectionControl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(choices=[('A', 'Accept'), ('M', 'Mitigate'), ('T', 'Transfer'), ('O', 'Avoid')], default='A', max_length=1)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('control', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.Control')),
                ('selection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.Selection')),
            ],
        ),
        migrations.RemoveField(
            model_name='question',
            name='standard',
        ),
        migrations.AlterUniqueTogether(
            name='selectionquestion',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='selectionquestion',
            name='question',
        ),
        migrations.RemoveField(
            model_name='selectionquestion',
            name='selection',
        ),
        migrations.DeleteModel(
            name='Question',
        ),
        migrations.DeleteModel(
            name='SelectionQuestion',
        ),
        migrations.AlterUniqueTogether(
            name='selectioncontrol',
            unique_together=set([('selection', 'control')]),
        ),
    ]
