#!/bin/bash
echo 'Waiting for Django application (server volume)...' &&
until cd /app; do sleep 1; done &&
echo 'Starting Celery worker...' &&
celery -A library.celery worker --loglevel=INFO
