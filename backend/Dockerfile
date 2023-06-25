FROM python:3.11-alpine as web

WORKDIR /app

RUN apk add --no-cache libffi-dev libheif-dev libde265-dev
RUN apk add exiftool

RUN apk add zlib-dev jpeg-dev

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 5000

CMD [ "flask", "run", "--host", "0.0.0.0" ]

FROM web as watchdog
RUN pip install --no-cache-dir watchdog

CMD ["flask", "run", "--host", "0.0.0.0", "--debug"]


FROM web as prod

RUN pip install --no-cache-dir waitress

CMD ["waitress-serve", "--call", "app:create_app"]