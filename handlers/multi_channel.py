from configs import Config
import asyncio
from handlers.database import db

async def db_channel_dict():
    db_channel_list = await db.get_total_db_channel_list()
    return {f"storedb{db_channel_list.index(i)}":str(i) for i in db_channel_list}

async def get_db_channel_id(channel_string):
    channel_dict = await db_channel_dict()
    return channel_dict.get(channel_string)

async def get_working_db_channel_id():
    return await db.get_current_db_channel_id()

async def get_working_channel_string():
    working_id = str(await db.get_current_db_channel_id())
    channel_dict = await db_channel_dict()
    print(channel_dict)
    for i in channel_dict:
        if channel_dict[i]==working_id:
            return i