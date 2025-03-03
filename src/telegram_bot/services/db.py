# telegram_bot/services/db.py

import databases

DATABASE_URL = "postgresql://library_owner:npg_TDW9uodJm3jI@ep-jolly-hat-a9vxn1fq-pooler.gwc.azure.neon.tech/library?sslmode=require"

# Создаем объект для подключения к базе данных
database = databases.Database(DATABASE_URL)


# Функция подключения
async def connect_db():
    await database.connect()


# Функция отключения
async def disconnect_db():
    await database.disconnect()
