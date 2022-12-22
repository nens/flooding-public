# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

import os
import glob
import zipfile

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError


class Command(BaseCommand):
    args = '<path>'
    help = """Walks the directories starting at <path>, test zip-files,
    print info of corrupted zip-files."""

    def handle(self, *args, **options):
        if not args:
            raise CommandError("No path given.")
        path = args[0]
        if not os.path.exists(path) or not os.path.isdir(path):
            raise CommandError("'{0}' is not an existing directory.".
                               format(path))
        self.walk_zips(path)

    def test_zips(self, zippathes, out):
        count = 0
        for zippath in zippathes:
            try:
                result = ''
                with zipfile.ZipFile(zippath) as zip:
                    result = zip.testzip()
                if result:
                    count += 1
                    out.write('First corrupted file "%s" in zip: "%s\n"' % (
                        result, zippath))
            except:
                count += 1
                out.write("Corrupted zip: '%s'\n" % zippath)
        return count

    def walk_zips(self, path):
        if os.path.isdir(path):
            walk = os.walk(path)
        out = open('/tmp/resultaten_check_zips.txt', 'wb')
        out.write("Start on path: %s.\n" % path)
        print("Start test.")
        count = 0
        count_corrupted = 0
        for root, dirs, files in walk:
            for dir in dirs:
                path_patern = os.path.join(root, dir, '*.zip'.encode('UTF-8'))
                zips = glob.glob(os.path.join(path_patern))
                count += len(zips)
                count_corrupted += self.test_zips(zips, out)
        out.write("End test, total: %d, corrupted: %d\n" % (
                count, count_corrupted))
        out.close()
        print("End test, total: %d, corrupted: %d" % (
                count, count_corrupted))
        print("Result is written to /tmp/resultaten_check_zips.txt")
