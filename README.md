# Heic wallpaper

Originally only for heic wallpapers, but now it supports all image formats.

## Installation

```bash
cd backend
pip install -r requirements.txt

cd ../frontend
npm ci
cp .sample.env .env
echo "Fill in the information in the .env file"

cd ../
docker compose up redis minio -d
```
## Usage
Run the project with the following commands:

```bash
cd backend
BROKER_URL=redis://localhost:6379 flask run --host 0.0.0.0 --debug
```

For the worker:
```bash
BROKER_URL=redis://localhost:6379 celery -A backend.worker.image_processor worker -l info --autoscale=4,1 
```

And for the frontend
```bash
cd frontend
npm run start
```