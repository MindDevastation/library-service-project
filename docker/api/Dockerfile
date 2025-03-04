FROM python:3.10-slim

LABEL authors=""

WORKDIR /app

COPY ../../requirements.txt /app/

RUN apt-get update && apt-get install -y dos2unix

RUN pip install --no-cache-dir -r requirements.txt

COPY ../.. /app/

EXPOSE 8000

RUN #dos2unix /app/telegram_bot/main.py
RUN dos2unix /app/scripts/worker_start.sh
RUN dos2unix /app/scripts/celery_beat_start.sh

#CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
