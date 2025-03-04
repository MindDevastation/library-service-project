#!/bin/bash
echo 'Waiting for Django application...' &&
until cd /app; do sleep 1; done &&
echo 'Starting Celery Beat...' &&
celery -A library.celery beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
