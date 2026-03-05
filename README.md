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
