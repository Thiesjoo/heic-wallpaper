FROM python:3.11-alpine as backend

WORKDIR /backend

RUN apk add --no-cache libffi-dev libheif-dev libde265-dev gcc musl-dev
RUN apk add --no-cache zlib-dev jpeg-dev

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
FROM node:18-alpine as frontend-base

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

WORKDIR /
RUN pip install --no-cache-dir waitress

CMD ["waitress-serve","--host","0.0.0.0", "--port", "5000", "backend:app"]