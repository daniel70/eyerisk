# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-21 23:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('compliance', '0003_auto_20160518_2325'),
    ]

    operations = [
        migrations.CreateModel(
            name='Selection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SelectionDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compliance.Document')),
                ('selection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compliance.Selection')),
            ],
        ),
        migrations.CreateModel(
            name='SelectionQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('decision', models.CharField(choices=[('A', 'Accept'), ('M', 'Mitigate'), ('T', 'Transfer')], default='A', max_length=1)),
                ('created', models.DateTimeField(auto_now=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compliance.Question')),
                ('selection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compliance.Selection')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='selectionquestion',
            unique_together=set([('selection', 'question')]),
        ),
        migrations.AlterUniqueTogether(
            name='selectiondocument',
            unique_together=set([('selection', 'document')]),
        ),
    ]
