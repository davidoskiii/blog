#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Automate superuser creation (ignores duplicate errors if user exists)
python manage.py createsuperuser --noinput || true
