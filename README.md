# safe-config-service

The `safe-config-service` is a service that provides configuration information in the context of the Safe clients environment (eg.: list of available safe apps).

## Requirements

- `docker-compose` – https://docs.docker.com/compose/install/

## Setup

The service uses Gunicorn+Nginx as a connection proxy, Django as the main application layer and PostgreSQL as a relational database. All these services are provided with Docker images that can be started using the provided `docker-compose` (local setup of the services is out of scope for this document).


#### Configuration

The environment variables are set via the `.env` file. The configuration in `.env.example` is meant to be production ready for the most part. You can copy it and adjust it to your development needs (refer to the file for the explanation about each environment variable)

```
cp .env.example .env
```

#### Starting up the services

```
docker-compose up -d
```

This will start the Nginx proxy server, the `safe-config-service` and a postgres database. Nginx exposes the port `8080` to the host which is the port used to interact with the application.

Once you have the images up and running the service can be reached via `localhost:8080`.

#### Overriding the setup of each image

If you need to override the setup that is done for each image you can use `docker-compose.override.yml.example`. First copy it:

```
cp docker-compose.override.yml.example docker-compose.override.yml
```

By default, this example mounts a volume under `$DOCKER_WEB_VOLUME` (refer to the `.env` file) which can be used to develop and see the code changes without restarting the docker image.

## The `./run` script

The `./run` script is meant to be used as an utility to interact with the running image.

```
./run help

Tasks:
     1	ci:test
     2	cmd
     3	flake8
     4	help
     5	manage
     6	test

Extended help:
  Each task has comments for general usage
```

Example: if you want to issue a command to the image which is running the Django service from your host you can do the following:

```
./run manage <django-command>
```
