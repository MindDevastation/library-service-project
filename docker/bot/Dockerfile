FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ../../requirements.txt /app/

RUN apt-get update && apt-get install -y dos2unix

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN dos2unix /app/scripts/bot_start.sh
