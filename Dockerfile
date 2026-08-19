FROM python:3.11-slim as backend

WORKDIR /app

RUN apt update \
    && apt install --no-install-recommends -y libffi-dev libheif-dev libde265-dev gcc libjpeg-dev curl \
    && rm -r /var/cache/apt/* /var/lib/apt/*

# Install uv by copying it from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY djangobackend/pyproject.toml djangobackend/uv.lock ./

RUN uv sync --frozen

COPY djangobackend .

EXPOSE 5000
CMD ["uv", "run", "python", "manage.py", "runserver", "5000"]

FROM backend as celery
CMD ["uv", "run", "celery", "-A", "djangobackend", "worker", "-l", "info", "--beat"]

#Build frontend
FROM node:22-alpine as frontend-base

WORKDIR /app

COPY frontend/package.json ./
COPY frontend/package-lock.json ./
RUN npm ci
COPY frontend .

FROM frontend-base as frontend
CMD ["npm", "run", "start"]

FROM frontend as frontend-prod
ARG VITE_OIDC_AUTHORITY
ARG VITE_OIDC_CLIENT_ID
RUN env
RUN npm run build


FROM nginx:1.21-alpine as nginx-prod
COPY --from=frontend-prod /app/dist /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

FROM backend as backend-prod
CMD ["uv", "run", "gunicorn", "djangobackend.wsgi", "-b", ":5000"]
