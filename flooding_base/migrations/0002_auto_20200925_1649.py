# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flooding_base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='configurations',
            field=models.ManyToManyField(to='flooding_base.Configuration', blank=True),
        ),
        migrations.AlterField(
            model_name='site',
            name='maps',
            field=models.ManyToManyField(to='flooding_base.Map', blank=True),
        ),
    ]
