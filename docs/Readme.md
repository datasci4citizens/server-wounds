# Data Science for Citizens
# Server Application Software for Wounds App

## Project Structure

* [citizens_project](../citizens_project) - Main Django project
	* [citizens_project/app_cicatrizando](../citizens_project/app_cicatrizando) - Main API application
	* [citizens_project/citizens_project](../citizens_project/citizens_project) - Project settings
* [docker](../docker) - Docker/Compose files
* [requirements.txt](../requirements.txt) - Python dependencies
* [.env.model](../.env.model) - Environment variables template

## Setup
### 1. Docker Compose and .env

Copy the template from [docker/docker-compose-model.yml](../docker/docker-compose-model.yml) to docker-compose.yml and edit the required fields.

Copy the template from [env.model](../.env.model) to .env and edit the required fields.


### 2. Build Docker

```bash

docker compose -f docker/docker-compose.yml --env-file ./.env up --build # Linux users may need sudo
``` 

## Running the Application


### 1. Start the database and server with Python

```bash
# from the root directory

python quickstart.py
```
The server will be available at http://localhost:8000

## Main Endpoints

The endpoints are available under [/api/](../citizens_project/app_cicatrizando/urls.py):

* `POST /api/auth/login/google/`
* `GET /api/auth/me/`

## Create an Admin User

### Update the following values in .env:

- DJANGO_SUPERUSER_USERNAME
- DJANGO_SUPERUSER_EMAIL
- DJANGO_SUPERUSER_PASSWORD

## Stack

* **Backend**: [Django](https://www.djangoproject.com/)
* **API**: [Django REST Framework](https://www.django-rest-framework.org/)
* **Database**: [PostgreSQL](https://www.postgresql.org/)
* **Auth**: [JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
* **Docs**: [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/)
* **Containerization**: [Docker](https://www.docker.com/)
