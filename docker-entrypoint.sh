#!/bin/ash

set -euo pipefail

echo "==> $(date +%H:%M:%S) ==> Migrating Django models..."
python src/manage.py migrate --noinput

echo "==> $(date +%H:%M:%S) ==> Applying fixtures..."
python src/manage.py loaddata initial_default_apps.json

echo "==> $(date +%H:%M:%S) ==> Running Gunicorn..."
exec gunicorn -c /app/src/config/gunicorn.py config.wsgi -b 0.0.0.0:${GUNICORN_BIND_PORT} --chdir /app/src/
