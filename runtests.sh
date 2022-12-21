#!/bin/sh
rm -r htmlcov/
docker-compose run --rm web bin/coverage run bin/test
docker-compose run --rm web bin/coverage html
gnome-open htmlcov/index.html
