# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('flooding_presentation', '0003_auto_20200925_1127'),
        ('flooding_lib', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='breach',
            options={'ordering': ['name'], 'verbose_name': 'Bres', 'verbose_name_plural': 'Bressen'},
        ),
        migrations.AlterModelOptions(
            name='cutofflocation',
            options={'verbose_name': 'Onderbrekingslocatie', 'verbose_name_plural': 'Onderbrekingslocaties'},
        ),
        migrations.AlterModelOptions(
            name='cutofflocationset',
            options={'verbose_name': 'Groep afsluitlocaties', 'verbose_name_plural': 'Afsluitlocatie groepen'},
        ),
        migrations.AlterModelOptions(
            name='cutofflocationsobekmodelsetting',
            options={'verbose_name': 'Afsluitlocatie sobek model instelling', 'verbose_name_plural': 'Afsluitlocatie sobek model instellingen'},
        ),
        migrations.AlterModelOptions(
            name='dike',
            options={'verbose_name': 'Dijk', 'verbose_name_plural': 'Dijken'},
        ),
        migrations.AlterModelOptions(
            name='externalwater',
            options={'verbose_name': 'Extern water', 'verbose_name_plural': 'Externe wateren'},
        ),
        migrations.AlterModelOptions(
            name='program',
            options={'verbose_name': 'Programma', 'verbose_name_plural': "Programma's"},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('friendlyname', 'name', 'owner'), 'verbose_name': 'Project', 'verbose_name_plural': 'Projecten'},
        ),
        migrations.AlterModelOptions(
            name='projectgrouppermission',
            options={'verbose_name': 'Projectgroeprecht', 'verbose_name_plural': 'Projectgroeprechten'},
        ),
        migrations.AlterModelOptions(
            name='region',
            options={'verbose_name': 'Regio', 'verbose_name_plural': "Regio's"},
        ),
        migrations.AlterModelOptions(
            name='regionset',
            options={'verbose_name': 'Regio set', 'verbose_name_plural': 'Regio sets'},
        ),
        migrations.AlterModelOptions(
            name='result',
            options={'verbose_name': 'Resultaat', 'verbose_name_plural': 'Resultaten'},
        ),
        migrations.AlterModelOptions(
            name='resulttype',
            options={'verbose_name': 'Resultaattype', 'verbose_name_plural': 'Resultaattypes'},
        ),
        migrations.AlterModelOptions(
            name='scenario',
            options={'ordering': ('name', 'owner'), 'verbose_name': 'Scenario', 'verbose_name_plural': "Scenario's"},
        ),
        migrations.AlterModelOptions(
            name='scenariobreach',
            options={'verbose_name': 'Scenario bres', 'verbose_name_plural': 'Scenario bressen'},
        ),
        migrations.AlterModelOptions(
            name='scenariocutofflocation',
            options={'verbose_name': 'Scenario afsluitlocatie', 'verbose_name_plural': 'Scenario afsluitlocaties'},
        ),
        migrations.AlterModelOptions(
            name='sobekmodel',
            options={'verbose_name': 'Sobekmodel', 'verbose_name_plural': 'Sobekmodellen'},
        ),
        migrations.AlterModelOptions(
            name='sobekversion',
            options={'verbose_name': 'Sobekversie', 'verbose_name_plural': 'Sobekversie'},
        ),
        migrations.AlterModelOptions(
            name='task',
            options={'get_latest_by': 'tstart', 'verbose_name': 'Taak', 'verbose_name_plural': 'Taken'},
        ),
        migrations.AlterModelOptions(
            name='taskexecutor',
            options={'verbose_name': 'Taakuitvoerder', 'verbose_name_plural': 'Taakuitvoerders'},
        ),
        migrations.AlterModelOptions(
            name='tasktype',
            options={'verbose_name': 'Taaktype', 'verbose_name_plural': 'Taaktypen'},
        ),
        migrations.AlterModelOptions(
            name='userpermission',
            options={'verbose_name': 'Gebruikersrecht', 'verbose_name_plural': 'Gebruikersrechten'},
        ),
        migrations.AlterModelOptions(
            name='waterlevel',
            options={'verbose_name': 'Waterniveau', 'verbose_name_plural': 'Waterniveaus'},
        ),
        migrations.AlterModelOptions(
            name='waterlevelset',
            options={'verbose_name': 'Waterniveau set', 'verbose_name_plural': 'Waterniveau sets'},
        ),
        migrations.AlterField(
            model_name='cutofflocation',
            name='type',
            field=models.IntegerField(choices=[(1, 'vergrendel'), (2, 'duiker'), (3, 'waterkering'), (4, 'bridge'), (5, 'onbekend'), (6, 'generieke_interne')]),
        ),
        migrations.AlterField(
            model_name='embankmentunit',
            name='type',
            field=models.IntegerField(choices=[(0, 'bestaand'), (1, 'nieuw')]),
        ),
        migrations.AlterField(
            model_name='externalwater',
            name='liztype',
            field=models.IntegerField(blank=True, null=True, choices=[(1, 'zee'), (2, b'estuarium'), (3, b'groot meer (incl. afgesloten zeearm)'), (4, b'grote rivier'), (5, b'scheepvaartkanaal'), (6, b'binnenmeer'), (7, b'regionale beek'), (8, b'regionale revier'), (9, b'boezemwater'), (10, b'polderwater')]),
        ),
        migrations.AlterField(
            model_name='externalwater',
            name='type',
            field=models.IntegerField(choices=[(1, 'zee'), (2, 'meer'), (3, 'kanaal'), (4, 'intern_meer'), (5, 'intern_kanaal'), (6, 'rivier'), (7, 'onbekend'), (8, 'lage_revier')]),
        ),
        migrations.AlterField(
            model_name='extrainfofield',
            name='header',
            field=models.IntegerField(default=20, choices=[(1, 'scenario'), (2, 'locatie'), (4, 'model'), (5, 'andere'), (6, 'bestanden'), (10, 'algemeen'), (20, 'metadata'), (30, 'bressen'), (40, 'externwater'), (70, 'geen')]),
        ),
        migrations.AlterField(
            model_name='measure',
            name='reference_adjustment',
            field=models.IntegerField(default=0, choices=[(0, 'onbekend'), (1, 'bestaand niveau'), (2, 'nieuw niveau')]),
        ),
        migrations.AlterField(
            model_name='projectcolormap',
            name='colormap',
            field=models.ForeignKey(to='pyramids.Colormap'),
        ),
        migrations.AlterField(
            model_name='projectgrouppermission',
            name='permission',
            field=models.IntegerField(choices=[(1, 'overzicht_scenario'), (2, 'toevoegen_scenario_nieuwe_simulatie'), (7, 'toevoegen_scenario_import'), (3, 'bewerken_scenario'), (4, 'goedkeuren_scenario'), (5, 'verwijderen_scenario'), (6, 'bewerken_scenario_eenvoudig')]),
        ),
        migrations.AlterField(
            model_name='result',
            name='animation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='pyramids.Animation', null=True),
        ),
        migrations.AlterField(
            model_name='result',
            name='raster',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='pyramids.Raster', null=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='Gearchiveerd'),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='archived_at',
            field=models.DateTimeField(null=True, verbose_name='Gearchiveerd op', blank=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='archived_by',
            field=models.ForeignKey(related_name='archived_by_user', verbose_name='Gearchiveerd door', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='calcpriority',
            field=models.IntegerField(default=20, choices=[(20, 'laag'), (30, 'middel'), (40, 'hoog')]),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='name',
            field=models.CharField(max_length=200, verbose_name='naam'),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='remarks',
            field=models.TextField(default=None, null=True, verbose_name='opmerkingen', blank=True),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='status_cache',
            field=models.IntegerField(default=None, null=True, choices=[(10, 'verwijderd'), (20, 'goedgekeurd'), (30, 'afgekeurd'), (40, 'berekend'), (50, 'fout'), (60, 'wacht'), (70, 'geen'), (80, 'gearchiveerd')]),
        ),
        migrations.AlterField(
            model_name='scenariobreach',
            name='methstartbreach',
            field=models.IntegerField(choices=[(1, 'op de top'), (2, 'op moment x'), (3, 'op kruising niveau x'), (4, 'onbekend/fout bij import')]),
        ),
        migrations.AlterField(
            model_name='sobekmodel',
            name='sobekmodeltype',
            field=models.IntegerField(choices=[(1, 'kanaal'), (2, 'overstroming')]),
        ),
        migrations.AlterField(
            model_name='userpermission',
            name='permission',
            field=models.IntegerField(choices=[(1, 'overzicht_scenario'), (2, 'toevoegen_scenario_nieuwe_simulatie'), (7, 'toevoegen_scenario_import'), (3, 'bewerken_scenario'), (4, 'goedkeuren_scenario'), (5, 'verwijderen_scenario'), (6, 'bewerken_scenario_eenvoudig')]),
        ),
        migrations.AlterField(
            model_name='waterlevelset',
            name='type',
            field=models.IntegerField(choices=[(1, 'onbekend'), (2, 'tij'), (3, 'bres')]),
        ),
        migrations.DeleteModel(
            name='Animation',
        ),
        migrations.DeleteModel(
            name='Colormap',
        ),
        migrations.DeleteModel(
            name='Raster',
        ),
    ]
