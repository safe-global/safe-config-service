# safe-config-service

[![Coverage Status](https://coveralls.io/repos/github/gnosis/safe-config-service/badge.svg)](https://coveralls.io/github/gnosis/safe-config-service)

The `safe-config-service` is a service that provides configuration information in the context of the Safe clients environment (eg.: list of available safe apps and chain metadata).

## Requirements

- `docker-compose` – https://docs.docker.com/compose/install/
- Python 3.12.2

## Setup

In order to start the server application:

#### 1. Install the required Python dependencies. Eg.: With a python virtual environment:

```shell
python -m venv venv # creates a virtual environment venv in the local directory
source venv/bin/activate
pip install -r requirements-dev.txt
pip install setuptools
```

#### 2. Launch the Postgres database image

```shell
docker compose up -d db
```

#### 3. Execute pending database migrations

```shell
python src/manage.py migrate
```

#### 4. Create an admin user

The admin interface of the service will be available under `http://localhost:8000/admin` but you need to have an admin registered before you are able to access the panel.

To create an admin user:

```shell
python src/manage.py createsuperuser
```

#### 5. Launch the service:

```shell
python src/manage.py runserver
```

By default the service will be available under http://127.0.0.1:8000/

## Configuration

The service is already configured for development purposes however if you wish to deploy it in a production environment you should set some sensitive parameters such as: `POSTGRES_USER`
, `POSTGRES_PASSWORD`, `SECRET_KEY`.
`DEBUG` should be set to `false`.

We provide the `.dev.env` file which explains the role of each environment variable. You can set the configuration using this file and read it in terminal session where the application will be
executed.

## Testing

Pytest is used to run the available tests in the project. **Some of these tests validate the integration with the database
so having one running is required**. From the project root:

```shell
docker compose up -d db
pytest src
```

## Code Style Formatter and Linter

Code formatting and linting are enforced before every commit using `pre-commit`.

To manually trigger the checks, run:

```shell
pre-commit run --all-files
```
