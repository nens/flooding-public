# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flooding_presentation', '0002_presentationtype_default_colormap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='presentationlayer',
            name='source_application',
            field=models.IntegerField(default=1, choices=[(1, 'Geen'), (2, 'Flooding')]),
        ),
        migrations.AlterField(
            model_name='presentationtype',
            name='default_colormap',
            field=models.ForeignKey(blank=True, to='pyramids.Colormap', null=True),
        ),
    ]
