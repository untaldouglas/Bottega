# Sandbox I3 Frappe — imagen de aplicación (no-root, base con digest aceptado)
# Base exacta autorizada por IMAGE-OS-GATE (no sustituir).
FROM docker.io/library/python:3.14.8-slim-trixie@sha256:9b629e83e1a517e01eaf7a36362563c0c7f620d3e4747f7dcf79564e290b7b48

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Dependencias de sistema: git (GitPython), toolchain + libmariadb (mysqlclient),
# cliente mariadb + redis-tools para operación.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        build-essential \
        pkg-config \
        default-libmysqlclient-dev \
        libmariadb-dev \
        mariadb-client \
        redis-tools \
        ca-certificates \
        curl \
        gnupg \
        file \
    && rm -rf /var/lib/apt/lists/*

# Node 24 + Yarn (tupla I3: Node 24, Yarn 1.22+).
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g yarn \
    && rm -rf /var/lib/apt/lists/*

# Usuario no-root (bench se niega a correr como root).
RUN useradd -m -u 1000 -s /bin/bash frappe

# Bench fijado (GPL-3.0-only, decisión PASS interno).
RUN pip install frappe-bench==5.31.1

USER frappe
WORKDIR /home/frappe

# Init bench con Frappe v16.53.0 (commit e8d41dd0061a32ee781caefe5d0b0d2bb7c15362).
# --skip-assets: la validación runtime no requiere build del desk; Node/Yarn quedan
# fuera del alcance de este sandbox (registrados en inventario de la tupla).
RUN bench init --frappe-branch v16.53.0 --skip-redis-config-generation --no-backups --skip-assets frappe-bench

# Configuración de runtime: db y redis apuntan a los servicios internos del sandbox.
COPY --chown=frappe:frappe common_site_config.json /home/frappe/frappe-bench/sites/common_site_config.json

ENV PATH="/home/frappe/frappe-bench/env/bin:${PATH}" \
    SITES_PATH="/home/frappe/frappe-bench/sites"
WORKDIR /home/frappe/frappe-bench

CMD ["gunicorn", "--chdir", "/home/frappe/frappe-bench/sites", "-b", "0.0.0.0:8000", "-w", "1", "-t", "120", "frappe.app:application"]
