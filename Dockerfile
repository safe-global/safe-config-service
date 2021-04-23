FROM python:3.9.4-alpine3.13 as python-base

# python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    CRYPTOGRAPHY_DONT_BUILD_RUST=1

ENV PYTHONUSERBASE=/python-deps

RUN set -ex \
    && apk add --no-cache --virtual .build-deps postgresql-dev build-base libffi-dev

# Install Python deps
COPY requirements.txt ./
RUN pip3 install --no-warn-script-location --user -r requirements.txt

# ------- development image -------

FROM python-base as development
ENV PATH="${PATH}:${PYTHONUSERBASE}/bin"

# venv already has runtime deps installed we get a quicker install
COPY requirements-dev.txt ./
RUN pip3 install --no-warn-script-location --user -r requirements-dev.txt

WORKDIR /app
COPY . .
