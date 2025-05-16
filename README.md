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

### Option 1: Using Docker (Recommended)

The project includes a complete Docker setup for easy deployment:

```bash
# Clone the repository
git clone <repository-url>
cd server-wounds

# Create required directories if they don't exist
mkdir -p tmp/midia

# Start all services (database, migrations, and web server)
docker compose up
```

The server will be available at http://localhost:8000

### Option 2: Local Development

For local development without Docker:

```bash
# Clone the repository
git clone <repository-url>
cd server-wounds

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env.google and docker/.env files with necessary variables

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

### 2. Google API Credentials (`./.env.google`)

This file contains Google OAuth2 credentials for authentication. Create a `.env.google` file in the project root with:

```properties
GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

To obtain these credentials:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Create an OAuth 2.0 Client ID
5. Add your application's redirect URIs
6. Copy the Client ID and Client Secret to your `.env.google` file

### 3. Local Development Environment File (`./.env`)

For local development without Docker, create a `.env` file with modified database connection settings:

```properties
SERVER_WOUNDS_DATABASE="POSTGRES"
SERVER_WOUNDS_DB_USER="api"
SERVER_WOUNDS_DB_PASSWORD="api"
SERVER_WOUNDS_DB_HOST="localhost"
SERVER_WOUNDS_DB_PORT=5432
SERVER_WOUNDS_SECRET_KEY="your_secure_secret_key"
```

## API Documentation

The API documentation is available at:
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## Creating an Admin User

To access the Django admin interface, you need to create a superuser:

### Using Docker

```bash
# Access the server container shell
docker compose exec server sh

# Create a superuser
python ./citizens_project/manage.py createsuperuser
```

Follow the prompts to:
- Insert Username
- Insert Email
- Insert Password

Once created, you can access the admin interface at http://localhost:8000/admin

### Local Development

```bash
# Make sure your virtual environment is activated
source .venv/bin/activate

# Create a superuser
python citizens_project/manage.py createsuperuser
```

## Technology Stack

- **Backend**: Django 5.2
- **API**: Django REST Framework 3.15.2
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework_simplejwt)
- **Documentation**: drf_spectacular
- **Containerization**: Docker & Docker Compose