FROM python:3.9.4-alpine3.13 as production

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
ENV PATH="${PATH}:${PYTHONUSERBASE}/bin"

RUN set -ex \
    && apk add --no-cache --virtual .build-deps postgresql-dev build-base libffi-dev

WORKDIR /app
COPY . .
RUN pip3 install --no-warn-script-location --user -r requirements.txt

# ------- development image -------
FROM production as development

ENV PATH="${PATH}:${PYTHONUSERBASE}/bin"
RUN pip3 install --no-warn-script-location --user -r requirements-dev.txt
