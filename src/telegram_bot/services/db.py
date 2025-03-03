import os

import databases

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create an object to connect to the database
database = databases.Database(DATABASE_URL)


# Connection function
async def connect_db():
    if not database.is_connected:
        await database.connect()


# Switch-off function
async def disconnect_db():
    if database.is_connected:
        await database.disconnect()
