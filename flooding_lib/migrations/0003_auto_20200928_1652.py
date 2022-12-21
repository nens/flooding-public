# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flooding_lib', '0002_auto_20200925_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskexecutor',
            name='ipaddress',
            field=models.GenericIPAddressField(),
        ),
        migrations.AlterField(
            model_name='taskexecutor',
            name='tasktypes',
            field=models.ManyToManyField(to='flooding_lib.TaskType', blank=True),
        ),
    ]
