#!/bin/sh
set -e

python manage.py collectstatic --noinput
python manage.py migrate
