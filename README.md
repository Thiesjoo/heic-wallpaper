# Heic wallpaper

Originally only for heic wallpapers, but now it supports all image formats.

## Installation

### Prerequisites
Make sure you have [uv](https://github.com/astral-sh/uv) and [Node.js](https://nodejs.org/) installed.

```bash
# Set up Django backend dependencies with uv
cd djangobackend
uv sync
cp .sample.env .env

# Set up frontend dependencies
cd ../frontend
npm install
cp .sample.env .env
echo "Fill in the information in the .env files"

# Start background services (PostgreSQL, Redis, MinIO)
cd ../
docker compose up -d
```

Setup minio:

```bash
docker compose exec minio bash
mc alias set local http://localhost:9000 minioadmin minioadmin
mc mb local/uploads
mc mb local/results
mc anonymous set download local/results
```


## Usage

### 1. Run the Django Backend
```bash
cd djangobackend
uv run python manage.py runserver
```

### 2. Run the Celery Worker
```bash
cd djangobackend
uv run celery -A djangobackend worker -l info --beat
```

### 3. Run the Frontend Dev Server
```bash
cd frontend
npm run start
```