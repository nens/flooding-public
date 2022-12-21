# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('flooding_lib', '0002_auto_20200925_1127'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GDMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('creation_date', models.DateTimeField(null=True, verbose_name='Creation date', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Gebiedsdekkende map',
                'verbose_name_plural': 'Gebiedsdekkende maps',
            },
        ),
        migrations.CreateModel(
            name='GDMapProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('creation_date', models.DateTimeField(null=True, verbose_name='Creation date', blank=True)),
                ('owner', models.ForeignKey(verbose_name='Owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['creation_date'],
                'verbose_name': 'Gebiedsdekkende map project',
                'verbose_name_plural': 'Gebiedsdekkende map projects',
            },
        ),
        migrations.AddField(
            model_name='gdmap',
            name='gd_map_project',
            field=models.ForeignKey(verbose_name='GD map project', to='gdmapstool.GDMapProject'),
        ),
        migrations.AddField(
            model_name='gdmap',
            name='scenarios',
            field=models.ManyToManyField(to='flooding_lib.Scenario', null=True, blank=True),
        ),
    ]
