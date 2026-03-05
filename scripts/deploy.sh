#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[%s] %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "$*"
}

APP_DIR="/home/azureuser/app"
log "Ensuring deploy directory ${APP_DIR} exists"
mkdir -p "${APP_DIR}"
cd "${APP_DIR}"

log "Authenticating to Docker Hub"
echo "${DOCKERHUB_TOKEN}" | docker login -u "${DOCKERHUB_USERNAME}" --password-stdin >/dev/null 2>&1

export IMAGE_NAME="${DOCKERHUB_USERNAME}/dscc_app"

log "Pulling latest images"
docker-compose pull

docker-compose down
log "Applying updated images without stopping the stack"
docker-compose up -d --remove-orphans

log "Applying database migrations"
docker-compose exec -T web python manage.py migrate --noinput

log "Collecting static files"
docker-compose exec -T web python manage.py collectstatic --noinput

log "Restarting nginx to pick up new static assets/config"
docker-compose restart nginx

log "Deployment completed successfully"
