FROM python:3.10-alpine as web

WORKDIR /app

RUN apk add --no-cache libffi-dev libheif-dev libde265-dev
RUN apk add --no-cache build-base
RUN apk add exiftool
RUN pip3 install pyheif

RUN apk add zlib-dev jpeg-dev
RUN pip3 install Pillow

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000

CMD [ "flask", "run", "--host", "0.0.0.0" ]

FROM web as watchdog
RUN pip install --no-cache-dir watchdog
