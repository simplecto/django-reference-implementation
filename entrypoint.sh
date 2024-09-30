#!/usr/bin/env bash

set -e

cmd="$@"

./manage.py collectstatic --noinput
./manage.py migrate

exec $cmd
