#!/bin/bash

set -e

python citizens_project/manage.py makemigrations > /dev/null

python citizens_project/manage.py migrate > /dev/null


# Criação automática do superusuário, caso as informações no .env tenham sido definidas
if [[ -n "$DJANGO_SUPERUSER_USERNAME" && "$DJANGO_SUPERUSER_USERNAME" != "admin" && \
     -n "$DJANGO_SUPERUSER_EMAIL" && "$DJANGO_SUPERUSER_EMAIL" != "admin@example.com" && \
     -n "$DJANGO_SUPERUSER_PASSWORD" && "$DJANGO_SUPERUSER_PASSWORD" != "admin" ]]; then

  echo "👤 Criando superusuário..."
  python citizens_project/manage.py shell <<EOF


from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username="$DJANGO_SUPERUSER_USERNAME").exists(): #user dont exist
  User.objects.create_superuser(
    username="$DJANGO_SUPERUSER_USERNAME",
    email="$DJANGO_SUPERUSER_EMAIL",
    password="$DJANGO_SUPERUSER_PASSWORD"
  )
  print("Usuario Criado com sucesso")

  print("Acesse em: http://0.0.0.0:8000/admin" )
else:
  print("Usuario já existente, continuando inicialização...")
EOF
else
    echo "Variaveis de superuser não definidas."
fi 

echo "iniciando servidor django..."

echo "acesse o servidor em: http://localhost:8000"
python citizens_project/manage.py runserver 0.0.0.0:8000
