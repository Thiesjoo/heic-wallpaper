FROM python:3.11-alpine as web

WORKDIR /app


RUN apk add --no-cache libffi-dev libheif-dev libde265-dev
# RUN apk add --no-cache build-base gcc
RUN apk add exiftool

# COPY deps/ ./deps
# RUN pip3 install deps/pyheif
# RUN pip3 install pyheif

RUN apk add zlib-dev jpeg-dev
# RUN pip3 install Pillow

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000

CMD [ "flask", "run", "--host", "0.0.0.0" ]

FROM web as watchdog
RUN pip install --no-cache-dir watchdog

CMD ["flask", "run", "--host", "0.0.0.0", "--debug"]