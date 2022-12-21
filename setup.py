from setuptools import setup
import monkeypatch_setuptools


version = '1.97.dev0'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('TODO.txt').read(),
    open('CREDITS.txt').read(),
    open('CHANGES.txt').read(),
    ])

install_requires = [
    'Django == 1.9.13',
    'Flask',

    # Celery
    'celery < 5',
    'django-celery-results',
#    'django-celery',
    'django-appconf',
    'django_compressor >= 1.1',
    'django-debug-toolbar',
    'django-excel-response',
    'django-markdown-deux',
    'django-treebeard',
    'factory-boy',
    'mock',
    'flask',
    'gdal',
    'gunicorn',
    'iso8601',
    # mapnik deliberately not here, buildout / syseggrecipe don't work
    'matplotlib',
    'nens',
    'netcdf4',
    'numpy',
    'pika',
    'psycopg2',
    'pyproj',
    'raven',
    'scipy',
    'Pillow',  # For gislib, nens
    'setuptools',  # For gislib
    'supervisor',
    'xlrd',
    'xlwt',
    'networkx',  # For nens
    'shapely',  # For nens
    ],

tests_require = [
    'ipython',
    'ipdb',
]

setup(name='flooding',
      version=version,
      description="The Flooding website.",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Bastiaan Roos',
      author_email='ops@nelen-schuurmans.nl',
      url='',
      license='GPL',
      packages=[
          # We put everything in here, Flooding used to have lots of different packages
          # but that made it hard to upgrade the whole.
          'flooding',
          'flooding_lib',
          'flooding_presentation',
          'flooding_visualization',
          'flooding_base',
          'raster_server',
          'lizard_worker',
          'gislib',
          'nens',
      ],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points={
          'console_scripts': [
              'runflask=raster_server.server:run',
          ]},
      )
