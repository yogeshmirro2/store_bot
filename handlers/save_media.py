# (c) @AbirHasan2005

import asyncio
from configs import Config
from pyrogram import Client,enums
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from handlers.database import db
from pyrogram.errors import FloodWait
from handlers.helpers import str_to_b64
from handlers.get_file_size import get_file_size
#from handlers.multi_channel import get_working_db_channel_id
from handlers.rm import rm_dir,rm_file

async def forward_to_channel(DB_CHANNEL, log_channel, bot: Client, message: Message, editable: Message):
    try:
        __SENT = await message.copy(int(DB_CHANNEL))
        return __SENT
    except FloodWait as sl:
        if sl.value > 45:
            await asyncio.sleep(sl.value)
            if log_channel is not None:
                await bot.send_message(
                    chat_id=int(log_channel),
                    text=f"#FloodWait:\nGot FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                        ]
                    )
                )
        return await forward_to_channel(bot, message, editable)


async def save_batch_media_in_channel(bot: Client, editable: Message, message_ids: list):
    try:
        DB_CHANNEL = await db.get_current_db_channel_id()
        log_channel = await db.check_log_channel_id()
        photo_send_channel = await db.check_video_photo_send()
        Channel_string = str(DB_CHANNEL).replace('-100','')
        each_short_link = await db.check_short_each_link()
    except Exception as e:
        await editable.edit(f"Something Went Wrong!\n\n**Error:** `{e}`")
        return
    try:
        media_thumb_id = ""
        message_ids_str = ""
        media_captions = []
        for message in (await bot.get_messages(chat_id=editable.chat.id, message_ids=message_ids)):
            sent_message = await forward_to_channel(DB_CHANNEL, log_channel, bot, message, editable)
            if sent_message is None:
                continue
            if sent_message.video or sent_message.audio or sent_message.document:
                media_captions.append(f"**👉  {sent_message.caption} {await get_file_size(sent_message)}**" if sent_message.caption else f"**👉 **")
                if not media_thumb_id:
                    try:
                        if sent_message.video:
                            media_thumb_id+=f"{sent_message.video.thumbs[0].file_id}"
                    except Exception as e:
                        print(e)
                        pass
            message_ids_str += f"{str(sent_message.id)} "
            await asyncio.sleep(2)
        try:
            SaveMessage = await bot.send_message(
                chat_id=int(DB_CHANNEL),
                text=f"#BaTCh_LInK|{message_ids_str}",
                disable_web_page_preview=True
            )
            # SaveMessage = await bot.send_message(
            #     chat_id=int(DB_CHANNEL),
            #     text=message_ids_str,
            #     disable_web_page_preview=True,
            #     reply_markup=InlineKeyboardMarkup([[
            #         InlineKeyboardButton("Delete Batch", callback_data="closeBatch")
            #     ]])
            # )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            SaveMessage = await bot.send_message(
                chat_id=int(DB_CHANNEL),
                text=f"#BaTCh_LInK|{message_ids_str}",
                disable_web_page_preview=True
            )
        
        share_link1 = f"https://t.me/{Config.BOT_USERNAME}?start=store_{Channel_string}_{str_to_b64(str(SaveMessage.id))}"
        if each_short_link:
            share_link = await get_shortlink(share_link)
            if not share_link:
                await editable.edit("**SHORT_EACH_LINK is enabled but there are no shortner available OR getting any error from shortner site.\nfor shortner site error check logs**")
                return
        else:
            share_link = share_link1
        
        try:
        
            await bot.send_message(
                chat_id=int(DB_CHANNEL),
                text=f"#BATCH_SAVE:\n\n[{editable.reply_to_message.from_user.first_name}](tg://user?id={editable.reply_to_message.from_user.id}) Got Batch Link!\n\nOpen Link - {share_link1}\n\nwithout shorted Link - {share_link1}",
                disable_web_page_preview=True
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await bot.send_message(
                chat_id=int(DB_CHANNEL),
                text=f"#BATCH_SAVE:\n\n[{editable.reply_to_message.from_user.first_name}](tg://user?id={editable.reply_to_message.from_user.id}) Got Batch Link!\n\nOpen Link - {share_link1}\n\nwithout shorted Link - {share_link1}",
                disable_web_page_preview=True
            )
            
        if not media_thumb_id and await db.get_default_thumb_status():
            media_thumb_id = await db.get_thumb_id()
            if media_thumb_id is None:
                await editable.reply_text("**set_default_thumb is enable but there is not thubmnail set by you.\nplz set a thumbnail first to get all media caption with thumbnail in photo_send_channel**")
        
        if media_thumb_id and photo_send_channel is not None:
            try:
                await editable.edit("**sending thumbnail with all Content caption to your VIDEO_PHOTO_SEND channel**")
                #thumb_path = await bot.download_media(media_thumb_id,f"{Config.DOWNLOAD_DIR}/{media_thumb_id}")
                thumb_path = await bot.download_media(media_thumb_id)
                add_detail = await db.get_add_detail()
                media_captions = sorted(media_captions)
                media_captions = "\n\n".join(media_captions)
                media_captions1=f"Here is the Permanent Link of your Content: <a href={share_link}>Download Link</a>\n\nJust Click on download to get your Content!\n\nyour Content name are:👇\n\n{media_captions}\n\n{add_detail}"
                if len(media_captions1)>1024:
                    await editable.edit("**media caption is too long (more than 1024 character)\nAdding only 1024 character caption to your media photo...**")
                    media_captions1 = media_captions1[0:1020]
                await bot.send_photo(int(photo_send_channel),thumb_path,media_captions1)
                await editable.edit("**thumbnail with media_captions has been sent to your VIDEO_PHOTO_SEND channel**")
                await rm_dir()
                await asyncio.sleep(2)
            except Exception as e:
                await editable.edit(f"{e}")
                return
                #await asyncio.sleep(4)
        
        try:
        
            if type(media_captions) is list:
                media_captions = sorted(media_captions)
                media_captions = "\n\n".join(media_captions)
            
        
        await editable.edit(
            f"Here is the Permanent Link of your Content: <a href={share_link}>Download Link</a>\n\n{media_captions}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Open Link", url=share_link)],[InlineKeyboardButton("without shorted Link", url=share_link1)]
                ]
            ),
            disable_web_page_preview=True
        )
        
        
    except Exception as err:
        await editable.edit(f"Something Went Wrong!\n\n**Error:** `{err}`")
        if log_channel is not None:
            await bot.send_message(
                chat_id=int(log_channel),
                text=f"#ERROR_TRACEBACK:\nGot Error from `{str(editable.chat.id)}` !!\n\n**Traceback:** `{err}`",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )

async def save_media_in_channel(bot: Client, editable: Message, message: Message):
    try:
        DB_CHANNEL = await db.get_current_db_channel_id()
        log_channel = await db.check_log_channel_id()
        photo_send_channel = await db.check_video_photo_send()
        Channel_string = str(DB_CHANNEL).replace('-100','')
        each_short_link = await db.check_short_each_link()
    except Exception as err:
        await editable.edit(f"Something Went Wrong!\n\n**Error:** `{err}`")
        return
    try:
        media_captions = ""
        thumb_id = ""
        forwarded_msg = await message.copy(int(DB_CHANNEL}))
        file_er_id = str(forwarded_msg.id)
        
        try:
            SaveMessage = await bot.send_message(
                chat_id=DB_CHANNEL,
                text=f"#SiNGle_LInk|{file_er_id}",
                disable_web_page_preview=True
            )
            # SaveMessage = await bot.send_message(
            #     chat_id=int(DB_CHANNEL),
            #     text=file_er_id,
            #     disable_web_page_preview=True,
            #     reply_markup=InlineKeyboardMarkup([[
            #         InlineKeyboardButton("Delete file", callback_data="closeBatch")
            #     ]])
            # )
        
        except FloodWait as e:
            await asyncio.sleep(e.value)
            SaveMessage = await bot.send_message(
                chat_id=int(DB_CHANNEL),
                text=f"#SiNGle_LInk|{file_er_id}",
                disable_web_page_preview=True
            )
        
        share_link1 = f"https://t.me/{Config.BOT_USERNAME}?start=store_{Channel_string}_{str_to_b64(file_er_id)}"
        if each_short_link:
            share_link = await get_shortlink(share_link)
            if not share_link:
                await editable.edit("**SHORT_EACH_LINK is enabled but there are no shortner available OR getting any error from shortner site.\nfor shortner site error check logs**")
                return
        else:
            share_link = share_link1
        
        try:
            await forwarded_msg.reply_text(
                f"#PRIVATE_FILE:\n\n[{message.from_user.first_name}](tg://user?id={message.from_user.id}) Got File Link!\n\nOpen Link - {share_link1}\n\nwithout shorted Link - {share_link1}",
                disable_web_page_preview=True)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await forwarded_msg.reply_text(
                f"#PRIVATE_FILE:\n\n[{message.from_user.first_name}](tg://user?id={message.from_user.id}) Got File Link!\n\nOpen Link - {share_link1}\n\nwithout shorted Link - {share_link1}",
                disable_web_page_preview=True)
            
        if forwarded_msg.video or forwarded_msg.audio or forwarded_msg.document:
            media_captions+=f"**👉 {forwarded_msg.caption} {await get_file_size(forwarded_msg)}**" if forwarded_msg.caption else f"**👉 **"
            if forwarded_msg.video:
                try:
                    thumb_id+=f"{forwarded_msg.video.thumbs[0].file_id}"
                except Exception as e:
                    print(e)
                    pass
            
            if not thumb_id and await db.get_default_thumb_status():
                thumb_id = await db.get_thumb_id()
                if thumb_id is None:
                    await editable.reply_text("**set_default_thumb is enable but there is not thubmnail set by you.\nplz set a thumbnail first to get all media caption with thumbnail in photo_send_channel**")
        
            
            if thumb_id and photo_send_channel is not None:
                await editable.edit("**sending thumbnail with all Content caption to your VIDEO_PHOTO_SEND channel**")
                try:
                    add_detail = await db.get_add_detail()
                    thumb_path = await bot.download_media(thumb_id)
                    media_captions1=f"Here is the Permanent Link of your Content: <a href={share_link}>Download Link</a>\n\nJust Click on download to get your Content!\n\nyour Content name are:👇\n\n{media_captions}\n\n{add_detail}"
                    if len(media_captions1)>1024:
                        await editable.edit("**media caption is too long (more than 1024 character)\nAdding only 1024 character caption to your media photo...**")
                        media_captions1 = media_captions1[0:1020]
                    await bot.send_photo(int(photo_send_channel),thumb_path,media_captions1)
                    await editable.edit("**thumbnail with media_captions has been sent to your VIDEO_PHOTO_SEND channel**")
                    await rm_dir()
                    await asyncio.sleep(2)
                except Exception as e:
                    await editable.edit(f"{e}")
                    print(e)
                    return
        
        
        await editable.edit(
            f"Here is the Permanent Link of your Content: <a href={share_link}>Download Link</a>\n\n{media_captions}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Open Link", url=share_link)],[InlineKeyboardButton("without shorted Link", url=share_link1)]
                ]
            ),
            disable_web_page_preview=True
        )
    
    except FloodWait as sl:
        if sl.value > 45:
            print(f"Sleep of {sl.value}s caused by FloodWait ...")
            await asyncio.sleep(sl.value)
            if await log_channel is not None:
                await bot.send_message(
                    chat_id=int(log_channel),
                    text="#FloodWait:\n"
                         f"Got FloodWait of `{str(sl.value)}s` from `{str(editable.chat.id)}` !!",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                        ]
                    )
                )
        await save_media_in_channel(bot, editable, message)
    except Exception as err:
        await editable.edit(f"Something Went Wrong!\n\n**Error:** `{err}`")
        if log_channel is not None:
            await bot.send_message(
                chat_id=int(log_channel),
                text="#ERROR_TRACEBACK:\n"
                     f"Got Error from `{str(editable.chat.id)}` !!\n\n"
                     f"**Traceback:** `{err}`",
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Ban User", callback_data=f"ban_user_{str(editable.chat.id)}")]
                    ]
                )
            )
