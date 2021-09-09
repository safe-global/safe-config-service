FROM python:3.9-alpine as production

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
    && apk add --no-cache --virtual .build-deps \
    autoconf \
    automake \
    build-base \
    libffi-dev \
    libtool \
    postgresql-dev \
    tini \
    # Pillow dependencies
    freetype-dev \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev \
    openjpeg-dev \
    tcl-dev \
    tiff-dev \
    tk-dev \
    zlib-dev

WORKDIR /app
COPY . .
RUN pip3 install --no-warn-script-location --user -r requirements.txt

ENTRYPOINT ["/sbin/tini", "--", "./docker-entrypoint.sh"]

# ------- development image -------
FROM production as development

ENV PATH="${PATH}:${PYTHONUSERBASE}/bin"
RUN pip3 install --no-warn-script-location --user -r requirements-dev.txt
