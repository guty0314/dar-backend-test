#!/bin/sh
set -e

# ---------------------------------------------------------------
# Túnel SSH hacia la base de datos (accesible solo vía el bastion EC2).
# Se activa si están seteadas las variables TUNNEL_*; si no, arranca
# la API directo (útil para entornos donde la DB sí es alcanzable
# sin túnel, ej. desarrollo local).
# ---------------------------------------------------------------
if [ -n "$TUNNEL_SSH_HOST" ]; then
  echo "Preparando túnel SSH hacia ${TUNNEL_REMOTE_HOST}:${TUNNEL_REMOTE_PORT} vía ${TUNNEL_SSH_USER}@${TUNNEL_SSH_HOST}..."

  KEY_PATH="/tmp/bastion_key"
  cp "$TUNNEL_SSH_KEY_PATH" "$KEY_PATH"
  chmod 600 "$KEY_PATH"

  # Sin -f: así el proceso queda adjunto a este shell y cualquier error de
  # SSH (auth, timeout, host inalcanzable) se ve en los logs de Render en
  # vez de perderse en segundo plano.
  autossh -M 0 -N \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o BatchMode=yes \
    -o ConnectTimeout=10 \
    -o ServerAliveInterval=30 \
    -o ServerAliveCountMax=3 \
    -o ExitOnForwardFailure=yes \
    -i "$KEY_PATH" \
    -L "${TUNNEL_LOCAL_PORT}:${TUNNEL_REMOTE_HOST}:${TUNNEL_REMOTE_PORT}" \
    "${TUNNEL_SSH_USER}@${TUNNEL_SSH_HOST}" &

  echo "Esperando a que el túnel esté activo..."
  for i in $(seq 1 15); do
    if nc -z localhost "$TUNNEL_LOCAL_PORT" 2>/dev/null; then
      echo "Túnel SSH activo en el puerto ${TUNNEL_LOCAL_PORT}"
      break
    fi
    sleep 1
  done
fi

exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
