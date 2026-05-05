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

### 1. Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ (for local development)
- PostgreSQL client (for direct database access)

### 2. Configure Environment Variables

Copy the template from [.env.model](../.env.model) to `.env` in the root directory and edit the required fields.

```bash
cp .env.model .env
# Edit .env with your configuration
```

### 3. Virtual Environment (Optional - for local development)

Create and activate a virtual environment:

```bash
# Create venv
python -m venv .venv

# Activate venv
# Linux/macOS
source ./.venv/bin/activate

# Windows
./.venv/scripts/activate.ps1

# Install dependencies
pip install --upgrade pip && pip install -r requirements.txt

# Deactivate when done
deactivate
```

## Running the Application

The recommended way to run the application is using the provided quickstart script, which manages both the database and server:

```bash
# From the root directory
python quickstart.py
```

Read the quickstart scripts documentation at [quickstart.py](../quickstart.py) for additional options

The server will be available at http://localhost:8000 once running.



## Main Endpoints

The API routes are defined in:

- [citizens_project/citizens_project/urls.py](../citizens_project/citizens_project/urls.py) — Main project routes
- [citizens_project/app_cicatrizando/urls.py](../citizens_project/app_cicatrizando/urls.py) — Application-specific routes

### Authentication Endpoints

- `POST /auth/login/google/` — Authenticate with Google OAuth2 and receive JWT tokens
- `POST /auth/login/role/` — Select user role (`provider` or `patient`)
- `POST /auth/login/provider/` — Complete provider profile data
- `POST /auth/login/patient/` — Complete patient profile data
- `GET /auth/me/` — Validate token and return current authenticated user info

### Documentation

- `GET /docs/` — Interactive API documentation (Swagger UI)

## Create an Admin User

To create a superuser for accessing the Django admin panel, set these environment variables in `.env`:

- `DJANGO_SUPERUSER_USERNAME` — Username for the admin account
- `DJANGO_SUPERUSER_EMAIL` — Email for the admin account
- `DJANGO_SUPERUSER_PASSWORD` — Password for the admin account

These values will be used automatically when the application starts. The admin panel can be accessed at http://localhost:8000/admin/

## Stack

* **Backend Framework**: [Django](https://www.djangoproject.com/) — Web framework for Python
* **API**: [Django REST Framework](https://www.django-rest-framework.org/) — REST API toolkit
* **Database**: [PostgreSQL](https://www.postgresql.org/) — Relational database
* **Containerization**: [Docker](https://www.docker.com/) — Container platform
* **Authentication**: [Google OAuth2](https://developers.google.com/identity/protocols/oauth2) and [JWT tokens](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
* **Docs**: [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/)
