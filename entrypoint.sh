#!/usr/bin/env bash

set -e

cmd="$@"

DO_MIGRATION=${DO_MIGRATION:-n}

if [[ $DO_MIGRATION = y ]]; then
    python /app/manage.py migrate
fi

exec $cmd
