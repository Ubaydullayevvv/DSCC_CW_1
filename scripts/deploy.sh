#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*"
}

APP_DIR="${APP_DIR:-$HOME/DSCC_CW1_12122}"
log "Starting deploy in ${APP_DIR}"
cd "${APP_DIR}"

log "Authenticating to Docker Hub"
echo "${DOCKERHUB_TOKEN}" | docker login -u "${DOCKERHUB_USERNAME}" --password-stdin >/dev/null 2>&1

log "Pulling updated images"
docker compose pull

# Compose recreates services in detached mode to keep downtime to a few seconds while containers restart.
log "Recreating containers with near-zero downtime"
docker compose down --remove-orphans
docker compose up -d --remove-orphans

log "Applying database migrations"
docker compose exec -T web python manage.py migrate --noinput

log "Collecting static files"
docker compose exec -T web python manage.py collectstatic --noinput

log "Deployment completed successfully"
