FROM python:3.10-slim

WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt update && apt -y install --no-install-recommends \
  exiftool
  
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000

CMD [ "flask", "run", "--host", "0.0.0.0" ]