import os

import databases
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

database = databases.Database(DATABASE_URL)


async def connect_db():
    if not database.is_connected:
        await database.connect()


async def disconnect_db():
    if database.is_connected:
        await database.disconnect()
