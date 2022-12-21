# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('approvaltool', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='approvalobjecttype',
            name='type',
            field=models.IntegerField(unique=True, choices=[(1, 'Project'), (2, 'ROR'), (3, 'Landelijk gebruik')]),
        ),
        migrations.AlterField(
            model_name='approvalrule',
            name='permissionlevel',
            field=models.IntegerField(default=1, help_text='Toestemmingsniveau van de gebruiker voor het uitvoeren van deze taak'),
        ),
    ]
