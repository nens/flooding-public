#!/bin/sh

echo "Note: This needs \"sudo apt-get install zip rsync\"."
echo "Note: must be in the \"flooding\" root directory."
echo "Deleting the old \"windows_build/\" subdirectory."
sleep 5

rm -rf windows_build/

mkdir -p windows_build/lib/var/log/
mkdir windows_build/lib/var/static/

touch windows_build/lib/var/log/django.log
touch windows_build/lib/var/log/django_tail.log

# These are all pure Python packages. We can copy them straight from Linux to Windows.

for pkg in flooding flooding_lib flooding_base flooding_presentation flooding_visualization lizard_worker django ampq pytz \
	raven treebeard pika appconf gislib \
        django_extensions django_nose
do
  rsync -r --verbose --exclude "*.pyc" --exclude "*.pyo" --exclude ".git" --exclude "settings/local.py" parts/omelette/${pkg}/ windows_build/lib/${pkg}/
done

for fil in six.py
do
  cp -R parts/omelette/${fil} windows_build/lib/${fil}
done

cp windows/*.cmd windows_build/

rm flooding-windows.zip
zip -r flooding-windows.zip windows_build -x \*.pyc \*.pyo .git local.py
