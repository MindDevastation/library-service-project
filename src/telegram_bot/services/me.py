from telegram_bot.services.db import database


async def get_me(telegram_id):
    query = (
        f"SELECT "
        f"last_login, date_joined, first_name, last_name, email "
        f"FROM users_user "
        f"WHERE telegram_id = {telegram_id};"
    )
    rows = await database.fetch_all(query)

    if rows:
        user_data = rows[0]
        return {
            "last_login": user_data[0],
            "date_joined": user_data[1],
            "first_name": user_data[2],
            "last_name": user_data[3],
            "email": user_data[4],
        }
    else:
        return None
