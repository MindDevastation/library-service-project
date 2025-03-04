#!/bin/bash
echo 'Waiting for Django application (server volume)...' &&
until cd /app; do sleep 1; done &&
echo 'Applying database migrations...' &&
until python manage.py makemigrations && python manage.py migrate && python manage.py migrate django_celery_beat; do
  echo 'Waiting for database...'; sleep 2;
done &&
echo 'Collecting static files...' &&
python manage.py collectstatic --noinput &&
echo 'Starting Django development server...' &&
python manage.py runserver 0.0.0.0:8000