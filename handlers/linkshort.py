import aiohttp
from handlers.database import db

async def get_shortlink(link):
    if not await db.check_shortner_exist():
        return False
    try:
        API_KEY,API_URL = await db.get_shortner_api_link()
        params = {'api': API_KEY, 'url': link}
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, params=params, raise_for_status=True) as response:
                data = await response.json()
                return data["shortenedUrl"]
    except Exception as e:
        print(e)
        return False