FROM python:3.12.7-slim

# python
ENV PYTHONUNBUFFERED=1
ENV PYTHONUSERBASE=/python-deps
ENV PATH="${PATH}:${PYTHONUSERBASE}/bin"

ARG VERSION
ARG BUILD_NUMBER
ENV APPLICATION_VERSION=${VERSION} \
    APPLICATION_BUILD_NUMBER=${BUILD_NUMBER}

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
    && apt-get install -y --no-install-recommends $buildDeps \
    && pip3 install -U --no-cache-dir wheel setuptools pip \
    && pip3 install --no-cache-dir --user -r requirements.txt \
    && apt-get purge -y --auto-remove $buildDeps \
    && rm -rf /var/lib/apt/lists/*

# Group 'python' (GID 999) and user 'python' (uid 999) are created
RUN groupadd -g 999 python && \
    useradd -u 999 -r -g python python && \
    # App folder and '/nginx' mount point are created with the new user as owner
    mkdir -p /nginx && chown -R python:python /nginx .
COPY --chown=python:python src/ src
COPY --chown=python:python static/ static
COPY --chown=python:python docker-entrypoint.sh .

# Container is ran by the new user
# UID:GID is used as Kubernetes requires numeric IDs: https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.28/#securitycontext-v1-core
USER 999:999

RUN DEFAULT_FILE_STORAGE=django.core.files.storage.FileSystemStorage python src/manage.py collectstatic --noinput
ENTRYPOINT ["./docker-entrypoint.sh"]
