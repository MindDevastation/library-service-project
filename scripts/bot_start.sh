#!/bin/bash
echo 'Starting Telegram bot...' &&
until cd /app; do sleep 1; done &&
python telegram_bot/main.py
