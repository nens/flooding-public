Een 3di scenario op de site zetten, aantekeningen
-------------------------------------------------

Benodigdheden:
- Een resultaat uit 3di (.nc file)
- Een aangemaakt scenario

De NetCDF file moet op de fileserver geplaatst worden, op dezelfde
manier als dat de Flooding site zelf een 3di resultaat erop zet.

Voorbeeld is scenario 13331. De resultaatdirectory van dat scenario is
//p-flod-fs-00-d1.external-nens.local/flod-share/Flooding/resultaten/Wippolder/13331/

Om dat uit te vinden kun je naar de flooding-productieserver gaan als
Buildout, 'bin/django shell' doen, en dan:

    >>> from flooding_lib.models import Scenario
    >>> Scenario.objects.get(pk=13331).get_abs_destdir()

Maak binnen de directory een subdirectory aan met de naam 'threedi'.

De NetCDF moet als naam 'subgrid_map.nc' hebben, en die file moet
ingepakt worden in 'subgrid_map.zip' in die threedi subdirectory.

Er moet nu een 'ThreediModel' aangemaakt worden. Dit gaat het handigst
in de admin interface. Het maakt niet uit wat je invult bij 'Scenarip
zip filename' en 'Mdu filename', die zijn alleen van belang als de
site 3di gaat aanroepen, deze tekst gaat over de situatie dat dat door
een adviseur al met de hand gedaan is. Vul dus alleen een zinnige naam
in en iets als 'hebben we niet' bij de rest. In mijn geval heeft het
nieuwe ThreediModel id 20.

Nu moeten we een 'ThreediCalculation' hebben. Die is lastig aan te
maken in de admin interface, omdat er 13000+ scenario's in een
pulldown menu staan. Misschien heeft die van jou wel een handige naam,
anders moet het even via bin/django shell. Status moet netcdf_created
(flooding_lib.models.ThreediCalculation.STATUS_NETCDF_CREATED) zijn.

Nu kan de PGN generation taak draaien. We moeten daarvoor zorgen dat
er een Lizard-Worker workflow template is met alleen die taak en
taak 185. Die is er al, workflow template 5 (met id 9...). Het
scenario moet dat workflow template krijgen. Kan via de admin interface.

Nu hoeft de taak alleen nog maar gestart te worden. Ga naar
http://flooding.lizard.net/scenarios_processing/
