# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lizard_worker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflowtemplate',
            name='code',
            field=models.IntegerField(unique=True),
        ),
    ]
