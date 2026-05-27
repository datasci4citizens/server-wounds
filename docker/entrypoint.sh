#!/bin/bash

set -e

python citizens_project/manage.py migrate --noinput
python manage.py load_comorbidities --file docs/mapeamento_conceptID/comorbidities_cid.csv

# Automatically create the superuser if .env values are configured
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && "$DJANGO_SUPERUSER_USERNAME" != "admin" && \
     -n "$DJANGO_SUPERUSER_EMAIL" && "$DJANGO_SUPERUSER_EMAIL" != "admin@example.com" && \
     -n "$DJANGO_SUPERUSER_PASSWORD" && "$DJANGO_SUPERUSER_PASSWORD" != "admin" ]]; then

  echo "👤 Creating SuperUser..."
  python citizens_project/manage.py shell <<EOF


from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="$DJANGO_SUPERUSER_USERNAME").exists(): # user does not exist
  User.objects.create_superuser(
    username="$DJANGO_SUPERUSER_USERNAME",
    email="$DJANGO_SUPERUSER_EMAIL",
    password="$DJANGO_SUPERUSER_PASSWORD"
  )
  print("Superuser created successfully")

  print("Access at: http://0.0.0.0:8000/admin" )
else:
  print("Superuser already exists, continuing initialization...")
EOF
else
    echo "Superuser environment variables are not defined."
fi 

echo "Starting Django server..."

echo "Access the server at: http://localhost:8000"
python citizens_project/manage.py runserver 0.0.0.0:8000
