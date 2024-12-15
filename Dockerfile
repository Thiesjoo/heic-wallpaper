FROM python:3.11-alpine as backend

WORKDIR /app

RUN apk add --no-cache libffi-dev libheif-dev libde265-dev gcc musl-dev zlib-dev jpeg-dev curl
RUN curl -sSL https://install.python-poetry.org | python -u - --version 1.8.5

COPY djangobackend/poetry.lock .
COPY djangobackend/pyproject.toml .

RUN /root/.local/bin/poetry install

COPY djangobackend .

EXPOSE 5000
CMD ["/root/.local/bin/poetry", "run", "python", "manage.py", "runserver", "5000"]

FROM backend as celery
CMD ["/root/.local/bin/poetry", "run", "celery", "-A", "djangobackend", "worker", "-l", "info", "--beat"]

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
CMD ["/root/.local/bin/poetry", "run", "gunicorn", "djangobackend.wsgi", "-b", ":5000"]
