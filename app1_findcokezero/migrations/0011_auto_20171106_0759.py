# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-06 07:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app1_findcokezero', '0010_retailer_sodas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailer',
            name='sodas',
            field=models.ManyToManyField(blank=True, to='app1_findcokezero.Soda'),
        ),
    ]
