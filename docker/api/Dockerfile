FROM python:3.10-slim

LABEL authors='{
  "Pastukhov Oleksii (Team Lead)": "oleksii.pastukhov.py@gmail.com",
  "Ruslan Yemets": "ruslanyemets@gmail.com",
  "Arsenii Aristov": "arseniyaristov07@gmail.com",
  "Mykyta Balabanov": "dogoberrr@gmail.com",
  "Taras Khomenko": "khomenkotaras1305@gmail.com",
  "Oleksandr Tsyhanok": "sashasmile1904@gmail.com"
}'


WORKDIR /app

COPY ../../requirements.txt /app/

RUN apt-get update && apt-get install -y dos2unix

RUN pip install --no-cache-dir -r requirements.txt

COPY ../.. /app/

EXPOSE 8000

RUN dos2unix /app/scripts/worker_start.sh
RUN dos2unix /app/scripts/celery_beat_start.sh
