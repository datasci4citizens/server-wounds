# Data Science for Citizens
# Server Application Software for Wounds App

## Estrutura do projeto

* [citizens_project](../citizens_project) - Projeto Django principal
	* [citizens_project/manage.py](../citizens_project/manage.py) - Script de gerenciamento do Django
	* [citizens_project/app_cicatrizando](../citizens_project/app_cicatrizando) - App principal da API
	* [citizens_project/citizens_project](../citizens_project/citizens_project) - Configurações do projeto
* [docker](../docker) - Arquivos do Docker/Compose (apenas o banco)
* [requirements.txt](../requirements.txt) - Dependências Python
* [.env.model](../.env.model) - Modelo de variáveis de ambiente

## Setup

### 1. Crie o ambiente virtual

```bash

python -m venv .venv
```

### 2. ative o ambiente virtual

```bash
#linux
source .venv/bin/activate

#windows
./.venv/scripts/activate
```

### 3. baixe as dependencias

```bash
pip install -r requirements.txt
```

### 4. docker compose e .env

Copie o modelo em [docker/docker-compose-model.yml](../docker/docker-compose-model.yml) como docker-compose.yml, editando os campos necessarios.

Copie o modelo em [env.model](../.env.model) como .env, editando os campos necessarios.


### 5. rode o docker e as migrações


```bash

cd docker
docker compose up --build  # usuarios linux podem precisar de SUDO
``` 

## Execução


### 1. ative o ambiente virtual


```bash
#linux
source .venv/bin/activate
```

```sh
#windows
./.venv/scripts/activate
```

### 2. Inicie o Docker

```bash
cd docker
docker compose up -d
```

O servidor estará disponível em http://localhost:8000

## Endpoints principais

Os endpoints estão sob [/api/](../citizens_project/app_cicatrizando/urls.py):

* `POST /api/auth/login/google/`
* `GET /api/auth/me/`

## Criar usuário admin

```bash
# local

cd citizens_project
python manage.py createsuperuser

#docker
docker exec -it django-server python citizens_project/manage.py createsuperuser
```

Depois acesse http://localhost:8000/admin

## Stack

* **Backend**: [Django](https://www.djangoproject.com/)
* **API**: [Django REST Framework](https://www.django-rest-framework.org/)
* **Database**: [PostgreSQL](https://www.postgresql.org/)
* **Auth**: [JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
* **Docs**: [drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/)
* **Containerização**: [Docker](https://www.docker.com/)
