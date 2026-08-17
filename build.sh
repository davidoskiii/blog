#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py createsuperuser --noinput --username davide --email davide.mascherin9@gmail.com --password Davide070810? && python manage.py collectstatic --noinput
