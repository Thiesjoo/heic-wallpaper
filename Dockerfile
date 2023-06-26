FROM python:3.11-alpine as backend

WORKDIR /backend

RUN apk add --no-cache libffi-dev libheif-dev libde265-dev exiftool
RUN apk add zlib-dev jpeg-dev

COPY backend/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY backend .

EXPOSE 5000

CMD ["flask", "run", "--host", "0.0.0.0", "--debug"]


FROM backend as celery-watching
RUN pip install --no-cache-dir watchdog

WORKDIR /

CMD ["watchmedo", "auto-restart", "--directory", "/backend", "--pattern", \
    "*.py", "--recursive", "--", "celery", "-A", "backend.worker.image_processor", "worker", "-l", "info"]

FROM backend as celery
WORKDIR /
CMD ["celery", "-A", "backend.worker.image_processor", "worker", "-l", "info"]


#Build frontend
FROM node:16-alpine as frontend-base

WORKDIR /app

COPY frontend/package.json ./
COPY frontend/package-lock.json ./
RUN npm ci
COPY frontend .

FROM frontend-base as frontend
CMD ["npm", "run", "start"]

FROM frontend-base as frontend-prod
RUN npm run build

FROM backend as backend-prod

CMD mkdir -p /static
COPY --from=frontend-prod /app/dist /static

WORKDIR /
RUN pip install --no-cache-dir waitress

CMD ["waitress-serve","--host","0.0.0.0", "--port", "5000", "backend:app"]