Notes on Lizard Flooding, 2022-12-21
====================================

Documentation
-------------

Is mostly this README.

There are a few small documents in docs/; since they
were written the situation has simplified somewhat, as Flooding cannot
itself run Sobek simulations anymore, and there are no Windows servers
for running Sobek (or HISSSM) involved anymore.

Lizard Flooding (from now on: "Flooding") was developed from 2006 to
roughly 2014. After that the project was primarily in maintenance mode --
importing 3Di scenarios was added and fixes have been applied.

Backend
-------

Flooding is mostly a Python 2 / Django web application. It keeps
"scenarios" in a file structure on disk, and metadata about them in
(very convoluted) database tables.

Another included application is (a very early version of) "rasterserver",
which can store raster data as "pyramids" so they can be quickly visualized at
any zoom level; this is a Flask application.

The current version of Flooding is intended to run on two servers,
a "web server" and a "task server". The two communicate over a shared network drive
and over RabbitMQ for starting tasks. The raster server also runs on the webserver.

Flooding runs on Ubuntu 14.04 (the only instructions are further in
this file), using Python 2 and a build tool named "Buildout".

The included "bootstrap.py" installed Buildout -- when that still
worked. A config file (probably development.cfg) is symlinked to
"buildout.cfg". Then the "bin/buildout" command would run Buildout
(installing dependencies), and then "bin/django" would run the Django
interactive shell and "bin/gunicorn" was installed behind a proxying
Nginx webserver process.

All are started using Supervisor ( https://supervisord.org ), the
required config files are generated with Ansible templates in
ansible/templates/ , also for Nginx.

Unfortunately, because of much newer versions of things like Python,
Ubuntu, Setuptools and PyPI, *nothing in this process still works*. For
instance Python 2 cannot talk to PyPI anymore; Buildout wants to
install a Setuptools version that is incompatible with
Buildout. So Flooding cannot be built at the moment.

It also has several outdated dependencies (like Mapnik 2) that were
not updated to Python 3. At least Django was updated to 1.9.13, which
does work with that version.

In essence, Flooding is a Django application that can be ported to
modern versions of everything (and pip, etc); but because of the
above, there is a lot of work to do before even the dependencies can
be installed. There is no obvious "step by step" process with working
software along the way as far as I can see, everything has to be done
in one step.

Works with RabbitMQ version 2.8.7.

As database, it uses PostgreSQL with the PostGIS extension.

Frontend
--------

The frontend is written using the "Isomorphic Smartclient" framework (
https://smartclient.com ). Most recent changes were in the period 2012
to 2014, the Smartclient version is probably 7 or 8.

It is mostly located in the directory flooding_base/static/ .

More information about it is lost.

Deployment
----------

Ansible scripts for provisioning servers and deploying a new version
from Git are provided in the ansible/ directory, but they currently
don't work because of the above.

However, they're probably a good start to figure out what's needed.

The Buildout configuration in 'production.cfg' assumes that the network share
is called '/mnt/flod-share/'; it symlinks some directories from inside it.

Removed from repository
=======================

To make this repository public, the following secrets were removed:

- The Django SECRET_KEY setting in flooding/settings.py

- The FLOODING_SHARE setting should refer to an existing network mount
  (not sure if it is used)

- That same flooding share in etc/rasterserver.json.in.

- The list of maintainer names in ansible/provision.yml

- The list of hostnames in ansible/production_hosts and ansible/staging_hosts

- Our Mapbox background maps and access keys in flooding_base/static/scripts/shared/lib/NMainScreenManager.js

- A Google Maps key in flooding/fixtures/flooding_base_setting.json
  (although Google Maps is unused; a Mapbox background map was
  hardcoded)

Note that settings for HISSSM and SOBEK can be ignored because
Flooding does not support running those programs anymore.

These need to be set:

- The DATABASES setting should be overridden in a "localsettings.py" file

- RabbitMQ broker settings (and queues should be configured)


Configuration elsewhere
-----------------------

Some parts of the configuration are set in the database (the "Setting"
Django model, result types, many others). Some are set in RabbitMQ
variables.

A complete dump of the current database is not a part of this
repository. However, if you get to the point of needing one, we can
provide settings as part of transfering data. An empty database for
testing can be generated using Django migrations.

Some are set using the fixtures in
flooding/flooding_base_setting.json, but these appear to be *very*
outdated (consider the YEAR setting, with value "2008").

OLD README FROM HERE
====================

Install Packages Ubuntu 14.04
-----------------------------
    $ sudo apt-get install \
        python-dev \
        python-gdal \
        python-mapnik2 \
        python-pip \
        python-tk \
        tzdata \
        zip \


Provision staging webserver
---------------------------

Provision using ansible::

    $ ansible-playbook -kK -i ansible/staging_inventory ansible/provision.yml

Unfortunately, some juggling with pip install pip and apt install python-pip
was still necessary.


Deploy staging webserver
---------------------------

Deploy using ansible::

    $ ansible-playbook -i ansible/staging_inventory ansible/deploy.yml --extra-vars "checkout_name=<checkout_name>"

Unfortunately, since we're a public repo, passwords are not allowed and a
localstagingsettings.py needs to be manually installed.


Provision production webserver
------------------------------

Provision using ansible::

    $ ansible-playbook -kK -i ansible/production_inventory ansible/provision.yml

Unfortunately, some juggling with pip install pip and apt install python-pip
was still necessary.


Deploy production servers
-------------------------

Deploy using ansible::

    $ ansible-playbook -i ansible/production_inventory ansible/deploy.yml --extra-vars "checkout_name=<checkout_name>"

Unfortunately, since we're a public repo, passwords are not allowed and a
localproductionsettings.py needs to be manually installed.


Development installation
------------------------

For development, you can use a docker-compose setup::

    $ docker-compose build --build-arg uid=`id -u` --build-arg gid=`id -g` web
    $ docker-compose up --no-start  # to not become too attached
    $ docker-compose start db

This is a nice time to dump && locally restore the production database for
development use, see below for instructions. After that, run bash on a
container to complete the installation::

    $ docker-compose run --rm web bash
    (docker)$ ln -s development.cfg buildout.cfg
    (docker)$ buildout

As everything goes well, you can now leave the container and start everything
picking one of the folowing statements::

    $ docker-compose start   # everything in the background
    $ docker-compose up web  # only web docker in the foreground
    $ docker-compose up      # everything in the foreground

If you want the rabbitmq management interface on localhost:15672::

    $ docker-compose exec rabbit rabbitmq-plugins enable rabbitmq_management

The broker definitions for the development rmq container can be imported in the
management interface. Login with username `flooding` and password `flooding`
and upload the file `rmq_dev_defs.json`.

Note that not only do all the Queues need to exist (for each task
number, "logging" and "sort"), they also need to be duplicated as
Bindings under the 'router' Exchange!

Dump and locally restore the production database for development use
--------------------------------------------------------------------

Dump the production database (see local settings on the production server for
the variables)::

    $ pg_dump flooding \
        --format custom \
        --schema public \
        --file flooding_public.dump \
        --host <host>
        --username <username> \
        --password \


The docker build step prepares a postgis database. But if there is need
replace that one::

    $ dropdb flooding --username flooding --password
    $ createdb flooding --username flooding --password
    $ psql flooding \
        --username flooding \
        --password \
        --command 'create extension postgis'


Restore the production dump to the local database::

    $ pg_restore \
        --dbname=flooding \
        --username flooding \
        --password \
        flooding_public.dump


Workflows
------------------------
The next workflow_templates are created on migration:

DEFAULT_TEMPLATE_CODE = 1 (workflow for a scenario with sobek model)
IMPORTED_TEMPLATE_CODE = 2 (workflow for a scenario with unknown model via import)
THREEDI_TEMPLATE_CODE = 3 (workflow for scenario with 3di model)
MAP_EXPORT_TEMPLATE_CODE = 4 (workflow for map's export)

The range of template's code 0 - 50 area reserved for auto workflows.


Upload/download water en- and keringshapes
------------------------------------------

Create a symbolic link ``BUILDOUT_DIR/var/ror_export`` to the mounted directory
(see ``ROR_KERINGEN_PATH`` in ``settings.py``)::

    $ ln -s /mnt/flooding/Flooding/ror_keringen var


GISDATA
-------
Copy shape-files to ``BUILDOUT_DIR/var/gisdata`` from old-webserver.


EXCEL files
-----------
Copy excel-files to ``BUILDOUT_DIR/var/excel`` from old-webserver.


Setup mount to flod-share
-------------------------
Set ``cifspw``, mount in ``fstab``. Then create dir ``/mnt/flod-share``.

    $ sudo mkdir /mnt/flod-share-3par
    $ sudo chown buildout:buildout /mnt/flod-share-3par
    $ sudo mkdir /p-common-fs01.external-nens.local
    $ sudo chown buildout:buildout /p-common-fs01.external-nens.local
    $ ln -s /mnt/flod-share-3par flod-share
    $ ln -s /mnt/flod-share-3par/pyramids pyramids
    $ ln -s /mnt/flod-share-3par/ror_keringen ror_keringen
    $ ln -s /mnt/flod-share-3par/exportruns/export_runs_csvs export_run_results


Raster Server
-------------

We also use an instance of the "raster-server" to serve WMS layers for
grid data. The grid data is stored as gislib "pyramids".

To use gislib and raster-server in Flooding, both need to be checked out
as development packages, using the "flooding-branch" branch.

Running Buildout, a configuration file for the raster-server is
created as etc/rasterserver.json. It says that the rasters are served
from BUILDOUT_DIR/var/pyramids. It is possible to symlink
/mnt/flooding/Flooding/pyramids to that directory, or to copy a few
rasters from the mounted share to that directory, or to change the
etc/rasterserver.json.in input file to use something file (in that
case, don't commit it).

The command to run the raster-server in development is, in the
buildout directory:


    $> RASTER_SERVER_SETTINGS=etc/rasterserver.json bin/runflask

The server will run at 0.0.0.0:5000 and visiting it should show a
working demo page where the available layers can be shown (although
there might be way too many for the page to render if you are using
the full Flooding share).

The URL used to find the WMS server is set in the Django settings as
RASTER_SERVER_URL. developmentsettings.py sets it to
'http://127.0.0.1:5000/wms' by default, change it to whatever you need
in localsettings.py if you are using virtual machines or similar.


Windows (task-server)
--------------------------------

* Check out the ``windows`` subdirectory, and customize it if needed.
* Check out the ``objectenbeheer/settings/windows.py`` module, and customize it if needed.

* Run ``build_windows.sh`` from Linux to wrap everything in a nice zip.

* In Windows, download Python 2.7.x from http://www.python.org/download/.
* In Windows, download Psycopg2 from http://www.stickpeople.com/projects/python/win-psycopg/.

* Extract the zip in the configured place, e.g. ``D:\Programs\flooding``.

* In Windows, configure your ``PYTHONPATH`` environment variable to point to the absolute path of the ``flooding\lib`` subdirectory.
  If you don't know how to do this, read https://kb.wisc.edu/cae/page.php?id=24500.

* To tune local settings like the database connection, create or edit ``objectenbeheer\lib\flooding\localsettings.py``.


Cleanup groupimport and importscenario
--------------------------------------
Run periodically ``cleanup_groupimport_dirs`` and ``cleanup_importscenario_dirs``
management command of ``flooding-lib`` package to remove wrong/unregistered
import-files. The dirs locate in ``var/media/import/``


Symlinks on windows
-------------------------
To avoid the problem with symlink on windows put the file ``sitecustomize.py``
into site-packages directory of your Python installation. The file located in
windows dir ``{buildout:directory}/windows``


Gebiedsdekkende kaarten
-----------------------
The app based on exporttool, used some parts of exporttool and located
in ``flooding_lib/tools/gdmapstool``

The app requires ``gdmapstool.change_gdmap`` permission.
