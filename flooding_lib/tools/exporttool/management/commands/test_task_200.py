from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from flooding_lib.tasks.calculate_export_maps import calculate_export_maps


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print 'Running ExportRun with id %s...' % args[0]
        calculate_export_maps(args[0])
