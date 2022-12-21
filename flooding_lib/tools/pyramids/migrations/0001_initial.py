# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import flooding_lib.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Animation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frames', models.IntegerField(default=0)),
                ('cols', models.IntegerField(default=0)),
                ('rows', models.IntegerField(default=0)),
                ('maxvalue', models.FloatField(null=True, blank=True)),
                ('geotransform', flooding_lib.fields.JSONField()),
                ('basedir', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Colormap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('matplotlib_name', models.CharField(unique=True, max_length=20)),
                ('description', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'ordering': ('description',),
            },
        ),
        migrations.CreateModel(
            name='Raster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', flooding_lib.fields.UUIDField(unique=True, editable=False, name=b'uuid', blank=True)),
            ],
        ),
    ]
