# Data Science for Citizens
# Server Application Software for Peleja App

This project embraces the server implementation of Peleja App.

## Directory Structure

* `install` - installation instructions of the PostgreSQL in docker plus the SQLModel and FastAPI libraries;
* `migrations` - migrations of the Postgres database;
* `model` - diagram of the data model;
* `src` - server source code in Python.

## Running the Main Server Application

Create virtual environment on root

~~~
python3 -m venv .venv
~~~

Go to install/dbms 

~~~
cd install/dbms
~~~

Run docker compose file

~~~
docker compose up
~~~

Go back to root and activate virtual environment

~~~
source .venv/bin/activate
~~~

Go to src

~~~
cd src
~~~

Run server

~~~
fastapi dev main.py
~~~