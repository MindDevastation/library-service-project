FROM python:3.10-slim

LABEL authors='{
  "Pastukhov Oleksii (Team Lead)": "oleksii.pastukhov.py@gmail.com",
  "Ruslan Yemets": "ruslanyemets@gmail.com",
  "Arsenii Aristov": "arseniyaristov07@gmail.com",
  "Mykyta Balabanov": "",
  "Taras Khomenko": "khomenkotaras1305@gmail.com",
  "Oleksandr Tsyhanok": "sashasmile1904@gmail.com"
}'

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ../../requirements.txt /app/

RUN apt-get update && apt-get install -y dos2unix

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN dos2unix /app/scripts/bot_start.sh
