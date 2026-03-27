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
### 1. .env

Copy the template from [env.model](../.env.model) to .env and edit the required fields.

### 2. Build Docker

```bash

# from root directory
docker compose -f docker/docker-compose.yml --env-file ./.env up --build # Linux users may need sudo
```

---

### It's recommended the use of a Venv (Virtual Environment) for debugging and testing outside of a docker:

### creating a venv:
from root directory
```bash
python -m venv .venv
```

starting up a venv
```bash
# linux
source ./.venv/bin/activate

#windows
./.venv/scripts/activate.ps1
```

once the venv is active for the first time:
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

to leave venv:
```bash
deactivate
```

## Running the Application


### 1. Start the database and server with the python script

```bash
# from the root directory

python quickstart.py
```

Read the quickstart scripts documentation at [quickstart.py](../quickstart.py) for additional options

The server will be available at http://localhost:8000




## Main Endpoints

The API routes are defined in:

- [citizens_project/citizens_project/urls.py](../citizens_project/citizens_project/urls.py)
- [citizens_project/app_cicatrizando/urls.py](../citizens_project/app_cicatrizando/urls.py)

Available endpoints:

- `POST /auth/login/firebase/` — Authenticate with Firebase and receive JWT tokens.

- `POST /auth/login/role/` — Select user role (`provider` or `patient`).

- `POST /auth/login/provider/` — Complete provider profile data.
- `POST /auth/login/patient/` — Complete patient profile data.
- `GET /auth/me/` — Validate token and return current authenticated user info.
- `GET /docs/` — Open interactive API documentation (Swagger UI).

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
