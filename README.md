# DSCC App

Production-ready Django deployment powered by Docker, PostgreSQL, Gunicorn, and Nginx.

## Prerequisites
- Docker Desktop or Docker Engine with Compose v2
- Copy the environment template at the repository root and update values (`DB_HOST=db`, `DB_PORT=5432` inside Docker).  
  Django automatically loads `.env` from the repo root (or `dscc_app/.env` for legacy setups).
  ```bash
  cp .env.example .env
  ```

## Build and Run
1. Build images and start the stack:
   ```bash
   docker compose up -d --build
   ```
2. Run database migrations (inside the container `manage.py` lives in `/app/dscc_app`, so no extra path prefix is required):
   ```bash
   docker compose exec web python manage.py migrate
   ```
3. Collect static assets into the shared volume (done after startup so the mounted volume has the latest build):
   ```bash
   docker compose exec web python manage.py collectstatic --noinput
   ```
4. (Optional) create a superuser:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
5. Visit http://localhost:8080 to access the application (proxied through Nginx).

## Services
- **web** – Django app running Gunicorn, mounting shared static/media volumes.
- **db** – PostgreSQL 15 with persistent volume `postgres_data`.
- **nginx** – Serves static/media assets and proxies application traffic to `web`.

## Useful Commands
- View logs: `docker compose logs -f web`
- Stop the stack: `docker compose down`
- Remove volumes (including database data): `docker compose down -v`

## Running Tests & Linting
- Local pytest (uses SQLite automatically): `USE_SQLITE_FOR_TESTS=1 pytest`
- Lint with flake8: `flake8`

## CI/CD Pipeline
GitHub Actions workflow `.github/workflows/deploy.yml` runs on every push to `main`:
1. Installs Python dependencies and runs `flake8` + `pytest`
2. Builds a Docker image tagged as `latest` and the commit SHA
3. Pushes both tags to Docker Hub
4. SSHes into the production server and invokes `scripts/deploy.sh`, which pulls the new image, restarts the Compose stack in detached mode (minimizing downtime), then runs migrations and `collectstatic`

### Required GitHub Secrets
- `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`
- `SSH_HOST`, `SSH_USERNAME`, `SSH_PRIVATE_KEY`

Optional: set `APP_DIR` on the server (or export before running the script) to override the default `~/DSCC_CW1_12122` deployment path.
