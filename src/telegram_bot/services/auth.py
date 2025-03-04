import aiohttp


async def login_user(email: str, password: str) -> bool:
    url = "http://127.0.0.1:8000/api/users/telegram-login/"
    data = {"email": email, "password": password}

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                return True
            return False
