# Data Science for Citizens
# Server Application Software for Wounds App

This project implements the server application for the Wounds App, a Django-based REST API serving the Cicatrizando wound monitoring application.

## Project Structure

* `citizens_project/` - Main Django project directory
  * `manage.py` - Django management script
  * `app_cicatrizando/` - Main application code for the wounds monitoring system
  * `citizens_project/` - Django project settings and configuration
* `docker/` - Docker configuration files and environment variables
* `tmp/` - Directory for media storage
* `requirements.txt` - Python dependencies

## Setup and Installation

### First Step: Starting Docker

The project includes a complete Docker setup for easy deployment:

```bash
# Clone the repository
git clone <repository-url>
cd server-wounds

# Create required directories if they don't exist
mkdir -p tmp/midia
mkdir wounds-db
mkdir wounds-impexp

#Remember to create a 'docker-compose' file based on the model that is available

# Start all services (database, migrations, and web server)
cd docker/dbms
docker compose up
```

The server will be available at http://localhost:8000

### Second Step: Initializing the server

```bash
cd server-wounds

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Change the root .env file with your credentials

# Run migrations
python citizens_project/manage.py migrate

# Run development server
python citizens_project/manage.py runserver
```

## Environment Variables

The application requires the following environment files:

### 1. Docker Environment File (`./docker/.env`)

This file contains database and Django configuration variables. Create a `docker/.env` file with:

```properties
SERVER_WOUNDS_DATABASE="POSTGRES"
SERVER_WOUNDS_DB_USER="api"
SERVER_WOUNDS_DB_PASSWORD="api"
SERVER_WOUNDS_DB_HOST="db" 
SERVER_WOUNDS_DB_PORT=5432
SERVER_WOUNDS_SECRET_KEY="your_secure_secret_key"
```

### 2. Local Development Environment File (`./.env`)

For local development, create a `.env` file:

```properties
SERVER_WOUNDS_DATABASE=POSTGRES
SERVER_WOUNDS_DB_USER=postgres
SERVER_WOUNDS_DB_PASSWORD=postgres
SERVER_WOUNDS_DB_HOST=localhost
SERVER_WOUNDS_DB_PORT=5432
SERVER_WOUNDS_SECRET_KEY=<"YOUR SECRET KEY">
GOOGLE_CLIENT_ID=<"GOOGLE_CLIENT_ID">
GOOGLE_CLIENT_SECRET=<"GOOGLE_CLIENT_SECRET">
```
This file contains Google OAuth2 credentials for authentication.

To obtain these credentials:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Create an OAuth 2.0 Client ID
5. Add your application's redirect URIs

## API Documentation

The API documentation is available at:
- Swagger UI: `/api/docs/swagger/`
- ReDoc: `/api/docs/redoc/`
- Schema: `/api/schema/`

## Creating an Admin User

To access the Django admin interface, you need to create a superuser:

```bash
# Create a superuser
python ./citizens_project/manage.py createsuperuser
```

Follow the prompts to:
- Insert Username
- Insert Email
- Insert Password

Once created, you can access the admin interface at http://localhost:8000/admin

## Technology Stack

- **Backend**: Django 5.2
- **API**: Django REST Framework 3.15.2
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework_simplejwt)
- **Documentation**: drf_spectacular
- **Containerization**: Docker & Docker Compose
