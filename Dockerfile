FROM python:3.11-slim

# python
ENV PYTHONUNBUFFERED=1

ENV PYTHONUSERBASE=/python-deps
ENV PATH="${PATH}:${PYTHONUSERBASE}/bin"

WORKDIR /app
COPY requirements.txt ./

RUN set ex \
    && buildDeps=" \
        automake \
        build-essential  \
        gcc \
        libc-dev \
        libssl-dev \
        libtool  \
        pkg-config  \
		" \
    && apt-get update \
    && apt-get install -y --no-install-recommends $buildDeps tini \
    && pip3 install -U --no-cache-dir wheel setuptools pip \
    && pip3 install --no-cache-dir --user -r requirements.txt \
    && apt-get purge -y --auto-remove $buildDeps \
    && rm -rf /var/lib/apt/lists/* \
    && chmod +x /usr/bin/tini

COPY . .
RUN DEFAULT_FILE_STORAGE=django.core.files.storage.FileSystemStorage python src/manage.py collectstatic --noinput
ENTRYPOINT ["/usr/bin/tini", "--", "./docker-entrypoint.sh"]
