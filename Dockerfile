FROM python:3.13-slim

# openssh-client + autossh: túnel hacia la RDS a través del bastion EC2
# gcc + libpq-dev: necesarios para compilar psycopg2 (no es psycopg2-binary)
# netcat-openbsd: usado por el entrypoint para esperar a que el túnel esté arriba
RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-client \
        autossh \
        netcat-openbsd \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh

# Evita que autossh se rinda si la primera conexión tarda en levantar
ENV AUTOSSH_GATETIME=0

ENTRYPOINT ["./docker-entrypoint.sh"]
