# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-06 14:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SelectionQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.CharField(choices=[('A', 'Accept'), ('M', 'Mitigate'), ('T', 'Transfer'), ('O', 'Avoid')], default='A', max_length=1)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.Question')),
                ('selection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='risk.Selection')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='selectionquestion',
            unique_together=set([('selection', 'question')]),
        ),
    ]
