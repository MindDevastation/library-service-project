import aiohttp

from telegram_bot.config import API_URL


async def login_user(email: str, password: str):
    url = f"{API_URL}/users/token/"
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json={"email": email, "password": password}
        ) as response:
            if response.status == 200:
                return (
                    await response.json()
                )  # Receive token { "access": "token", "refresh": "refresh_token" }
            return None


async def refresh_access_token(refresh_token: str):
    url = f"{API_URL}/users/token/refresh/"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"refresh": refresh_token}) as response:
            if response.status == 200:
                return await response.json()  # Получаем новый access токен
            return None


async def verify_access_token(access_token: str):
    url = f"{API_URL}/users/token/verify/"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"token": access_token}) as response:
            if response.status == 200:
                return True
            return False
