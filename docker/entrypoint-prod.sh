#!/bin/bash

set -e

cd /code/citizens_project

python manage.py migrate --noinput
python manage.py load_comorbidities

# Optionally create a superuser if credentials are provided and not defaults
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && "$DJANGO_SUPERUSER_USERNAME" != "admin" && \
      -n "$DJANGO_SUPERUSER_EMAIL" && "$DJANGO_SUPERUSER_EMAIL" != "admin@example.com" && \
      -n "$DJANGO_SUPERUSER_PASSWORD" && "$DJANGO_SUPERUSER_PASSWORD" != "admin" ]]; then
  python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="$DJANGO_SUPERUSER_USERNAME").exists():
    User.objects.create_superuser(
        username="$DJANGO_SUPERUSER_USERNAME",
        email="$DJANGO_SUPERUSER_EMAIL",
        password="$DJANGO_SUPERUSER_PASSWORD",
    )
    print("Superuser created")
else:
    print("Superuser already exists")
EOF
fi

exec gunicorn citizens_project.wsgi:application --bind 0.0.0.0:8000 --workers 2
