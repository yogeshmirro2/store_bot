# (c) @AbirHasan2005

import asyncio
from binascii import (
    Error
)
import re
from get_file_size import get_file_size,get_file_attr
from database import db
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from helpers import b64_to_str, str_to_b64

async def process_files(bot: Client, cmd: Message, db_id):
    try:
        try:
            file_id = int(b64_to_str(cmd.text.rsplit("_",1)[-1]))
        except (Error, UnicodeDecodeError):
            file_id = int(cmd.text.rsplit("_",1)[-1])
        GetMessage = await bot.get_messages(chat_id=int(db_id), message_ids=file_id)
        message_ids = []
        if "BaTCh_LInK" or "SiNGle_LInk" in GetMessage.text:
            message_ids = GetMessage.text.split("|")[1].split()
            _response_msg = await cmd.reply_text(
                text=f"**Total Files:** `{len(message_ids)}`",
                quote=True,
                disable_web_page_preview=True
            )
        else:
            response = await cmd.reply_text("**You Send Me Wrong Link🚫🚫🚫👎Or This link is Not in My Database\nPlz Send Me A Valid Link ☑️☑️ Or Report Bot Owner!**")
            return
            # message_ids.append(int(GetMessage.id))
            # _response_msg = await cmd.reply_text(
            #     text=f"**Total Files:** `{len(message_ids)}`",
            #     quote=True,
            #     disable_web_page_preview=True
            # )
        for i in range(len(message_ids)):
            await media_forward(bot, user_id=cmd.from_user.id, file_id=int(message_ids[i]), db_id=db_id)
    except Exception as err:
        await cmd.reply_text(f"Something went wrong!\n\n**Error:** `{err}`")




# async def reply_forward(message: Message, file_id: int):
#     try:
#         await message.reply_text(
#             f"**Here is Sharable Link of this file:**\n"
#             f"https://t.me/{Config.BOT_USERNAME}?start=AbirHasan2005_{str_to_b64(str(file_id))}\n\n"
#             f"__To Retrive the Stored File, just open the link!__",
#             disable_web_page_preview=True, quote=True)
#     except FloodWait as e:
#         await asyncio.sleep(e.value)
#         await reply_forward(message, file_id)


async def media_forward(bot: Client, user_id: int, file_id: int, db_id):
    try:
        return await bot.copy_message(chat_id=user_id, from_chat_id=int(db_id),
                                           message_id=file_id)
        # msg = await bot.get_messages(db_id,file_id)
        # if msg.empty or msg.service:
        #     return await bot.send_message(user_id,"**You Send Me Invalid Link or Message may not be exist in my Database\nPlz Send Me A Valid Link**")
        # msg_attr = await get_file_attr(msg)
        # if msg_attr is not None:
        #     media_size = await get_file_size(msg)
        #     if "GiB" in media_size:
        #         int_media_size = float(re.findall(r"[-+]?\d*\.\d+|\d+",media_size)[0])
        #         if int_media_size>1.99:
        #             media_file_id = msg_attr.file_id
        #             return await bot.send_cached_media(user_id,media_file_id,msg.caption)
            
        #         else:
        #             return await bot.copy_message(chat_id=user_id, from_chat_id=int(db_id),
        #                                   message_id=file_id)
        #     else:
        #         return await bot.copy_message(chat_id=user_id, from_chat_id=int(db_id),
        #                                   message_id=file_id)
        # else:
        #     return await bot.copy_message(chat_id=user_id, from_chat_id=int(db_id),
                         
        
        # if await db.check_forward_as_copy_status():
        #     return await bot.copy_message(chat_id=user_id, from_chat_id=int(db_id),
        #                                   message_id=file_id)
        # elif not await db.check_forward_as_copy_status():
        #     return await bot.forward_messages(chat_id=user_id, from_chat_id=int(db_id),
        #                                      message_ids=file_id)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return media_forward(bot, user_id, file_id, db_id)
    except Exception as e:
        return await bot.send_message(user_id,f"**Error During send file(file_id: {file_id}) \nError:`{e}`\nType: `{str(type(e)}`\nPlz Forward This Error To Bot Owner⚠️⚠️")

# async def send_media_and_reply(bot: Client, user_id: int, file_id: int):
#     sent_message = await media_forward(bot, user_id, file_id)
#     await reply_forward(message=sent_message, file_id=file_id)
#     await asyncio.sleep(2)
