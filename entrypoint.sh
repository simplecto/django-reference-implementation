#!/usr/bin/env bash

set -e

cmd="$@"

uv run ./manage.py collectstatic --noinput
uv run ./manage.py migrate

exec uv run $cmd
