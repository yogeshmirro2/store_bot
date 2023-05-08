# (c) @AbirHasan2005

from configs import Config
from handlers.database import db
from pyrogram import Client
from pyrogram.types import Message


async def add_user_to_database(bot: Client, cmd: Message):
    if not await db.is_user_exist(cmd.from_user.id):
        await db.add_user(cmd.from_user.id)
        log_channel = await db.check_log_channel_id()
        if log_channel is not None:
            await bot.send_message(
                int(log_channel),
                f"#NEW_USER: \n\nNew User [{cmd.from_user.first_name}](tg://user?id={cmd.from_user.id}) started @{Config.BOT_USERNAME} !!"
            )
