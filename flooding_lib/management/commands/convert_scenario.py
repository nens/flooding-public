import glob
import mock
import os
import sys
import traceback
import time

from django.db.transaction import commit_on_success
from django.conf import settings
from django.core.management.base import BaseCommand

from flooding_presentation.models import PresentationType
from flooding_lib import models
from flooding_lib.tasks import pyramid_generation
from flooding_lib.tasks import presentationlayer_generation


def scenarios():
    # All ROR scenarios
    ROR = models.Project.objects.get(pk=99)

    for scenario in ROR.all_scenarios():
        yield scenario


def is_converted(scenario):
    return scenario.presentationlayer.filter(
        presentationtype__geo_type=PresentationType.GEO_TYPE_PYRAMID).exists()


class Log(object):
    def __init__(self):
        self.log = open("logfile.txt", "w")

    def message(self, message, *args, **kwargs):
        localtime = time.localtime()
        timestring = time.strftime("%d/%m %H:%M:%S", localtime)

        self.log.write(
            "{time} {message}\n".format(
                time=timestring, message=message.format(*args, **kwargs)))
        self.log.flush()


def convert_scenario(scenario):
    try:
        pyramid_generation.sobek(scenario.id, settings.TMP_DIR)
        pyramid_generation.his_ssm(scenario.id, settings.TMP_DIR)

        #presentationlayer_generation.perform_presentation_generation(
        #    scenario.id, None)

        # Remove old animation PNGs of the presentation layer
        # A copy is still available in the results dir, if needed
        pngdir = os.path.join(
            settings.EXTERNAL_PRESENTATION_MOUNTED_DIR,
            'flooding', 'scenario', str(scenario.id), 'fls')
        pngdir = pngdir.replace('\\', '/')
        files = glob.glob(
            os.path.join(pngdir, "*.png")) + glob.glob(
            os.path.join(pngdir, "*.pgw")) + glob.glob(
                '/tmp/*.aux.xml') + glob.glob(
                '/tmp/*.tif')

        for f in files:
            os.remove(f)

        print("1: Converted successfully.")
    except Exception as e:
        print("0: {} stopped due to an exception: {}".format(scenario.id, e))
        _, _, tb = sys.exc_info()
        traceback.print_tb(tb, 10)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if len(args) != 1:
            print "Usage: convert_scenario <scenario_id>"
            print ("Returns a status string, the first character is "
                   "0 or 1 indicating success.")
            return

        scenario_id = args[0]
        scenario = models.Scenario.objects.get(pk=scenario_id)

        convert_scenario(scenario)
