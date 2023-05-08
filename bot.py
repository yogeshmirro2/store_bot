# (c) @AbirHasan2005

import os
import secrets
import string
import asyncio
import traceback
from binascii import (
    Error
)
from pyrogram import (
    Client,
    enums,
    filters
)
from pyrogram.errors import (
    UserNotParticipant,
    FloodWait,
    QueryIdInvalid
)
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message
)
from configs import Config
from handlers.get_verify_min import get_diff_min
from handlers.multi_channel import get_db_channel_id,get_working_channel_string
from handlers.linkshort import get_shortlink
from handlers.database import db
from handlers.add_user_to_db import add_user_to_database
from handlers.send_file import media_forward,process_files
from handlers.helpers import b64_to_str, str_to_b64
from handlers.check_user_status import handle_user_status
from handlers.force_sub_handler import (
    handle_force_sub,
    get_invite_link
)
from handlers.broadcast_handlers import main_broadcast_handler
from handlers.save_media import (
    save_media_in_channel,
    save_batch_media_in_channel
)

MediaList = {}
BotCmdList = ["start","change_other_user_can_save_file","about","broadcast"
,"status","ban_user","unban_user",
"banned_users","clear_batch",
"change_db_channel","add_db_channel","delete_db_channel",
"add_update_channel","delete_update_channel","add_log_channel","delete_log_channel",
"change_forward_as_copy","change_broadcast_as_copy","change_verification","change_verify_days",
"delete_verify_days","change_use_pre_shorted_link","change_verify_key_link_list",
"delete_verify_key_link_list","change_shortner_api_link","delete_shortner_api_link",
"change_video_photo_send","delete_video_photo_send","change_add_details","delete_add_details",
"change_short_each_link","change_how_to_verify","delete_how_to_verify"]
Bot = Client(
    name=Config.BOT_USERNAME,
    in_memory=True,
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH
)


@Bot.on_message(filters.private)
async def _(bot: Client, cmd: Message):
    await handle_user_status(bot, cmd)


@Bot.on_message(filters.command("start") & filters.private)
async def start(bot: Client, cmd: Message):

    if cmd.from_user.id in Config.BANNED_USERS:
        await cmd.reply_text("Sorry, You are banned ⚠️.")
        return
    if await db.check_update_channel_id() is not None:
        back = await handle_force_sub(bot, cmd)
        if back == 400:
            return
    
    usr_cmd = cmd.text.split("_", 1)[-1]
    if usr_cmd == "/start":
        await add_user_to_database(bot, cmd)
        await cmd.reply_text(
            Config.HOME_TEXT.format(cmd.from_user.first_name, cmd.from_user.id),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    
                    [
                        InlineKeyboardButton("About Bot", callback_data="aboutbot"),
                        InlineKeyboardButton("About Dev", callback_data="aboutdevs")
                    ]
                ]
            )
        )
    else:
        key = cmd.text.split("_",1)[-1]
        check = (cmd.text.split("_",1)[0]).split()[-1]
        edits = await cmd.reply_text("**Please Wait...Checking Command Given by You**")
        try:
            if check == "verify":
                try:
                    if await db.get_verify_days() is not None and  await db.check_verification_status():
                        # if int(cmd.from_user.id) in Config.BOT_ADMINS:
                        #     await cmd.reply_text("**you are admin of this bot.\nyou not need any verification**")
                        #     return
                        await edits.edit("**Please Wait⚠️ Verifying You...**")
                        user_key = await db.get_verify_key(cmd.from_user.id)
                        day = await db.get_verify_days()
                        if key==user_key:
                            await db.update_verify_date(cmd.from_user.id)
                            await db.update_verify_key(cmd.from_user.id)
                            await edits.edit(f"**Verification Complete ️☑️\nyour verification valid till next {day} days")
                            return
                        else:
                            await edits.edit("**This verification link is not for you🚫\nPlease wait... untill generating new verification link for you**")
                            await db.update_verify_key(cmd.from_user.id)
                            usr_key = await db.get_verify_key()
                            if await db.use_pre_shorted_link_status() and await db.check_verify_list_exist():
                                verify_key_list,verify_link_list = await get_verify_key_link_list()
                                usr_link = verify_link_list[verify_key_list.index(usr_key)]
                                await edits.edit(f"**your new verification link is👇👇👇👇\n{usr_link}\nOnce you verify , your verification valid till next {day} days")
                                return
                            elif not await db.use_pre_shorted_link_status() and await db.check_verify_list_exist():
                                await edits.edit("**use_pre_shorted_link not enable.\nplease report bot owner🙏🙏🙏**")
                                return
                            elif not await db.check_verify_list_exist() and await db.use_pre_shorted_link_status():
                                await edits.edit("**there are no verify key or verify link exist.\n please report bot owner🙏🙏🙏**")
                                return
                            else:
                                usr_link_short = f"https://t.me/{Config.BOT_USERNAME}?start=verify_{usr_key}"
                                shorted_link = await get_shortlink(usr_link_short)
                                if shorted_link:
                                    await edits.edit(f"**your new verification link is👇👇👇👇\n{shorted_link}\nOnce you verify , your verification valid till next {day} days")
                                    return
                                else:
                                    await edits.edit("**there are no shortner availible.\nplease report bot owner🙏🙏🙏")
                                    return
                    elif not await db.check_verification_status():
                        await edits.edit("**Currently verification is off🚫\ncurrently you can use this bot like a free bird**")
                        return
                    elif await db.get_verify_days() is None and await db.check_verification_status():
                        await edits.edit("**verification is enabled but could't find verify days\nplz report bot owner**")
                        return
                except Exception as e:
                    edits.edit(f"**there are some problem during verification\n Error --- {e}\n{str(type(e))}\nplease forward this error to bot owner") 
                    return
            if (check != "verify") and ("storedb" in check):
                try:
                    db_channel = await get_db_channel_id(check)
                    if int(cmd.from_user.id) in Config.BOT_ADMINS:
                        await edits.delete()
                        await process_files(bot ,cmd ,db_channel)
                        return
                    else:
                        if await db.get_verify_days() is not None and await db.check_verification_status():
                            usr_verify_datetime_formate = await db.get_verify_date(cmd.from_user.id)
                            usr_min = await get_diff_min(usr_verify_datetime_formate)
                            day = await db.get_verify_days()
                            if usr_min<0:
                                await edits.edit("**your verification has expired.\nplease do verification again.\nplease wait... till next verification link will be generate....")
                                user_key = await db.get_verify_key(cmd.from_user.id)
                                if await db.use_pre_shorted_link_status() and await db.check_verify_list_exist():
                                    verify_key_list,verify_link_list = await get_verify_key_link_list()
                                    usr_link = verify_link_list[verify_key_list.index(usr_key)]
                                    await edits.edit(f"**your verification link is👇👇👇👇\n{usr_link}\nOnce you verify , your verification valid till next {day} days")
                                    return
                                elif not await db.check_verify_list_exist() and await db.use_pre_shorted_link_status():
                                    await edits.edit("**Error fetching your verification link becoz there are no verify key or verify link exist.\n please report bot owner🙏🙏🙏**")
                                    return
                                else:
                                    usr_link_short = f"https://t.me/{Config.BOT_USERNAME}?start=verify_{user_key}"
                                    shorted_link = await get_shortlink(usr_link_short)
                                    if shorted_link:
                                        await edits.edit(f"**your new verification link is👇👇👇👇\n{shorted_link}\nOnce you verify , your verification valid till next {day} days")
                                        return
                                    else:
                                        await edits.edit("**Error fetching your verification link becoz there are no shortner availible.\nplease report bot owner🙏🙏🙏")
                                        return
                            else:
                                await edits.delete()
                                await process_files(bot, cmd, db_channel)
                                return
                        
                        elif await db.get_verify_days() is None and await db.check_verification_status():
                            await edits.edit("**Error fetching your verification link becoz verification is enabled but can't find verify days.\nplease report bot owner🙏🙏🙏")
                        
                        else:
                            await edits.delete()
                            await process_files(bot, cmd, db_channel)
                            return
                        
                except Exception as e:
                    await edits.edit(f"**Error during sending file \n error -- {e}")
                    return
        except Exception as e:
            await edits.edit(f"**Error while indentify your commnd.\nError ----- {e}\n{str(type(e))}\nplease forward this error to bot owner")

@Bot.on_message(filters.incoming & ~filters.command(BotCmdList))
async def main(bot: Client, message: Message):

    if message.chat.type == enums.ChatType.PRIVATE:

        await add_user_to_database(bot, message)

        if await db.check_update_channel_id() is not None:
            back = await handle_force_sub(bot, message)
            if back == 400:
                return

        if message.from_user.id in Config.BANNED_USERS:
            await message.reply_text("Sorry, You are banned!\n\nContact [Support Group](https://t.me/JoinOT)",
                                     disable_web_page_preview=True)
            return

        if not Config.OTHER_USERS_CAN_SAVE_FILE and message.from_user.id not in Config.BOT_ADMINS:
            return

        await message.reply_text(
            text="**Choose an option from below:**",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Save in Batch", callback_data="addToBatchTrue")],
                [InlineKeyboardButton("Get Sharable Link", callback_data="addToBatchFalse")]
            ]),
            quote=True,
            disable_web_page_preview=True
        )
    elif message.chat.type == enums.ChatType.CHANNEL:
        log_channel = await db.check_log_channel_id()
        updates_channel = await db.check_update_channel_id()
        each_short_link = await db.check_short_each_link()
        total_db_channel_list = await db.get_total_db_channel_list()
        if updates_channel is None:
            updates_channel = 673889
        db_channel = await db.get_current_db_channel_id()
        db_channel_string = await get_working_channel_string()
        if (message.chat.id == int(log_channel)) or (message.chat.id in total_db_channel_list) or (message.chat.id == int(updates_channel)) or message.forward_from_chat or message.forward_from:
            return
        elif int(message.chat.id) in Config.BANNED_CHAT_IDS:
            await bot.leave_chat(message.chat.id)
            return
        else:
            pass

        try:
            forwarded_msg = await message.copy(db_channel)
            file_er_id = str(forwarded_msg.id)
            share_link1 = f"https://t.me/{Config.BOT_USERNAME}?start={db_channel_string}_{str_to_b64(file_er_id)}"
            if each_short_link:
                share_link = await get_shortlink(share_link)
                if not share_link:
                    await message.reply_text("**SHORT_EACH_LINK is enabled but there are no shortner available OR getting any error from shortner site.\nfor shortner site error check logs**")
                    return
            else:
                share_link = share_link1
            CH_edit = await bot.edit_message_reply_markup(message.chat.id, message.id,
                                                          reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                              "Get Sharable Link", url=share_link)]]))
            if message.chat.username:
                await forwarded_msg.reply_text(
                    f"#CHANNEL_BUTTON:\n\n[{message.chat.title}](https://t.me/{message.chat.username}/{CH_edit.id}) Channel's Broadcasted File's Button Added!")
            else:
                private_ch = str(message.chat.id)[4:]
                await forwarded_msg.reply_text(
                    f"#CHANNEL_BUTTON:\n\n[{message.chat.title}](https://t.me/c/{private_ch}/{CH_edit.id}) Channel's Broadcasted File's Button Added!")
        except FloodWait as sl:
            await asyncio.sleep(sl.value)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text=f"#FloodWait:\nGot FloodWait of `{str(sl.value)}s` from `{str(message.chat.id)}` !!",
                disable_web_page_preview=True
            )
        except Exception as err:
            await bot.leave_chat(message.chat.id)
            await bot.send_message(
                chat_id=int(Config.LOG_CHANNEL),
                text=f"#ERROR_TRACEBACK:\nGot Error from `{str(message.chat.id)}` !!\n\n**Traceback:** `{err}`",
                disable_web_page_preview=True
            )


@Bot.on_message(filters.private & filters.command("broadcast") & filters.user(Config.BOT_OWNER) & filters.reply)
async def broadcast_handler_open(_, m: Message):
    await main_broadcast_handler(m, db)


@Bot.on_message(filters.private & filters.command("status") & filters.user(Config.BOT_OWNER))
async def sts(_, m: Message):
    total_users = await db.total_users_count()
    await m.reply_text(
        text=f"**Total Users in DB:** `{total_users}`",
        quote=True
    )


@Bot.on_message(filters.private & filters.command("ban_user") & filters.user(Config.BOT_OWNER))
async def ban(c: Client, m: Message):
    
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to ban any user from the bot.\n\n"
            f"Usage:\n\n"
            f"`/ban_user user_id ban_duration ban_reason`\n\n"
            f"Eg: `/ban_user 1234567 28 You misused me.`\n"
            f"This will ban user with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} days for the reason {ban_reason}."
        try:
            await c.send_message(
                user_id,
                f"You are banned to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n"
                f"**Message from the admin**"
            )
            ban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            ban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"

        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(
            ban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


@Bot.on_message(filters.private & filters.command("unban_user") & filters.user(Config.BOT_OWNER))
async def unban(c: Client, m: Message):

    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to unban any user.\n\n"
            f"Usage:\n\n`/unban_user user_id`\n\n"
            f"Eg: `/unban_user 1234567`\n"
            f"This will unban user with id `1234567`.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        unban_log_text = f"Unbanning user {user_id}"
        try:
            await c.send_message(
                user_id,
                f"Your ban was lifted!"
            )
            unban_log_text += '\n\nUser notified successfully!'
        except:
            traceback.print_exc()
            unban_log_text += f"\n\nUser notification failed! \n\n`{traceback.format_exc()}`"
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(
            unban_log_text,
            quote=True
        )
    except:
        traceback.print_exc()
        await m.reply_text(
            f"Error occurred! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True
        )


@Bot.on_message(filters.private & filters.command("banned_users") & filters.user(Config.BOT_OWNER))
async def _banned_users(_, m: Message):
    
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ''

    async for banned_user in all_banned_users:
        user_id = banned_user['id']
        ban_duration = banned_user['ban_status']['ban_duration']
        banned_on = banned_user['ban_status']['banned_on']
        ban_reason = banned_user['ban_status']['ban_reason']
        banned_usr_count += 1
        text += f"> **user_id**: `{user_id}`, **Ban Duration**: `{ban_duration}`, " \
                f"**Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
    reply_text = f"Total banned user(s): `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open('banned-users.txt', 'w') as f:
            f.write(reply_text)
        await m.reply_document('banned-users.txt', True)
        os.remove('banned-users.txt')
        return
    await m.reply_text(reply_text, True)


@Bot.on_message(filters.private & filters.command("clear_batch"))
async def clear_user_batch(bot: Client, m: Message):
    MediaList[f"{str(m.from_user.id)}"] = []
    await m.reply_text("Cleared your batch files successfully!")

@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_db_channel"))
async def change_db_channel(c :Client, m: Message):
    btn=[]
    DB_CHANNELS = await db.get_total_db_channel_list()
    c_db_ch = await db.get_current_db_channel_id()
    for i in DB_CHANNELS:
        btn.append([InlineKeyboardButton(f"{i}", callback_data=f"db_channel_{i}")])
    await m.reply_text(
        text=f"**your current db_channel is --- {c_db_ch}\n choose below one which you want to add as db_channel👇👇👇",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True,
        disable_web_page_preview=True
    )
    return

@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("add_db_channel"))
async def add_db_channel(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        return await m.reply_text("**reply any channel id to add in DB_CHANNEL list**")
        
    try:
        channel_id = int(m.reply_to_message.text)
        await db.add_db_channels_id(channel_id)
        await m.reply_text("**Successfully added in DB_CHANNEL list**")
        return
    except ValueError:
        await m.reply_text("don't send me text\nsend me only channel id in intiger like --- -1007725455")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("delete_db_channel"))
async def delete_db_channel(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        return await m.reply_text("**reply any channel id to delete from DB_CHANNEL list**")
        
    try:
        channel_id = int(m.reply_to_message.text)
        delt = await db.delete_db_channel_id(channel_id)
        if delt:
            await m.reply_text("**Successfully deleted from  DB_CHANNEL list**")
        if not delt:
            await m.reply_text("**this channel id not in DB_CHANNEL list**")
    except ValueError:
        await m.reply_text("don't send me text\nsend me only channel id in intiger like --- -1007725455")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("add_update_channel"))
async def add_update_channel(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        return await m.reply_text("**reply any channel id to add  or change UPDATES_CHANNEL**")
        
    try:
        channel_id = int(m.reply_to_message.text)
        await db.add_update_channel_id(int(channel_id))
        await m.reply_text("**Successfully added as UPDATES_CHANNEL**")
    except ValueError:
        await m.reply_text("don't send me text\nsend me only channel id in intiger like --- -1007725455")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")

@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("delete_update_channel"))
async def delete_update_channel(c :Client, m: Message):
    checking = await db.delete_update_channel_id()
    if checking:
        return await m.reply_text("**Successfully deleted  UPDATES_CHANNEL**")
    else:
        return await m.reply_text("**there are no UPDATES_CHANNEL**")

@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("add_log_channel"))
async def add_log_channel(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        return await m.reply_text("**reply any channel id to add  or change LOG_CHANNEL**")
        
    try:
        channel_id = int(m.reply_to_message.text)
        await db.change_log_channel_id(int(channel_id))
        await m.reply_text("**Successfully added as LOG_CHANNEL**")
    except ValueError:
        await message.reply_text("don't send me text\nsend me only channel id in intiger like --- -1007725455")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("delete_log_channel"))
async def delete_log_channel(c :Client, m: Message):
    checking = await db.delete_log_channel_id()
    if checking:
        return await m.reply_text("**Successfully deleted LOG_CHANNEL**")
    else:
        return await m.reply_text("**there are no LOG_CHANNEL**")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_forward_as_copy"))
async def change_forward_as_copy(c :Client, m: Message):
    results = await db.check_forward_as_copy_status()
    if results:
        result = "False"
    else:
        result = "True"
    btn=[[InlineKeyboardButton("click here", callback_data=f"forward_as_copy_{result}")]]
    await m.reply_text(
        text=f"**your current status for forward_as_copy_status is --- {str(results)}\n click below to change status👇👇👇",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True,
        disable_web_page_preview=True
    )


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_broadcast_as_copy"))
async def change_broadcast_as_copy(c :Client, m: Message):
    results = await db.check_broadcast_as_copy_status()
    if results:
        result = "False"
    else:
        result = "True"
    btn=[[InlineKeyboardButton("click here", callback_data=f"broadcast_as_copy_{result}")]]
    await m.reply_text(
        text=f"**your current status for broadcast_as_copy is --- {str(results)}\n click below to change status👇👇👇",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True,
        disable_web_page_preview=True
    )

@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_verification"))
async def change_verification(c :Client, m: Message):
    results = await db.check_verification_status()
    if results:
        result = "False"
    else:
        result = "True"
    btn=[[InlineKeyboardButton("click here", callback_data=f"verification_{result}")]]
    await m.reply_text(
        text=f"**your current status for verification is --- {str(results)}\n click below to change status👇👇👇",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True,
        disable_web_page_preview=True
    )

@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_verify_days"))
async def change_verify_days(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        days = await db.get_verify_days()
        return await m.reply_text(f"**reply any intiger to add  or change verify_days\n Your current verify_days is {days}**")
        
    try:
        days = int(m.reply_to_message.text)
        await db.change_verify_days(str(days))
        await m.reply_text("**Successfully change verify_days**")
    except ValueError:
        await m.reply_text("don't send me text\nsend me only  intiger like --- 6")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("delete_verify_days"))
async def delete_verify_days(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    try:
        await db.delete_verify_days()
        await m.reply_text("**Successfully deleted verify_days**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_use_pre_shorted_link"))
async def change_use_pre_shorted_link(c :Client, m: Message):
    results = await db.use_pre_shorted_link_status()
    if results:
        result = "False"
    else:
        result = "True"
    btn=[[InlineKeyboardButton("click here", callback_data=f"use_pre_shorted_link_{result}")]]
    await m.reply_text(
        text=f"**your current status for use_pre_shorted_link is --- {str(results)}\n click below to change status👇👇👇",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True,
        disable_web_page_preview=True
    )


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_verify_key_link_list"))
async def change_verify_key_link_list(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        list1,list2 = await db.get_verify_key_link_list()
        return await m.reply_text(f"**reply any text which contain verify key and verify link.\nmultiple verify key and verify link separated by space and verify key and verify link must separated by colon(|)\nexample---- key1 key2 key3 key4|link1 link2 link3 link4\nYour current verify key and verify list  is ----\nVerify_Key --- {list1}\nVerify_Link --- {list2} **")
        
    try:
        key_string,link_string= m.reply_to_message.text.split("|")[0],message.reply_to_message.text.split("|")[1]
        await db.change_verify_key_link(key_string,link_string)
        await m.reply_text("**Successfully change verify_key_list and verify_link_list**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")

@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("delete_verify_key_link_list"))
async def delete_verify_key_link_list(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    try:
        await db.delete_verify_key_link()
        await m.reply_text("**Successfully deleted verify_key and verify_link list**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_shortner_api_link"))
async def change_shortner_api_link(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        api,link = await db.get_shortner_api_link()
        return await m.reply_text(f"**reply any text which contain shortner_api and shortner_api_link.\nshortner_api and shortner_api_link must be separated by colon(|)\nexample---- shortner_api|shortner_api_link\n Your current shortner_api and shortner_api_link  is ----\nShortner_Api --- {api}\nShortner_Api_Link --- {link} **")
        
    try:
        api_string,link_string= m.reply_to_message.text.split("|")[0],message.reply_to_message.text.split("|")[1]
        await db.change_shortner_api_link(api_string,link_string)
        await m.reply_text("**Successfully change shortner_api and shortner_api_link**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("delete_shortner_api_link"))
async def delete_shortner_api_link(c :Client, m: Message):
    if not m.from_user:
        return await message.reply_text("I don't know about you sar :(")
    try:
        await db.delete_shortner_api_link()
        await m.reply_text("**Successfully deleted shortner_api and shortner_api_link**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_video_photo_send"))
async def change_video_photo_send(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        channel_id = await db.check_video_photo_send()
        return await m.reply_text(f"**reply any channel_id to add  or change video_photo_send\n Your current video_photo_send channel id is {channel_id}**")
        
    try:
        channel_id = int(m.reply_to_message.text)
        await db.change_video_photo_send(int(channel_id))
        await m.reply_text("**Successfully change video_photo_send channel id**")
    except ValueError:
        await m.reply_text("don't send me text\nsend me only channel_id like --- -100646678")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")

@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("delete_video_photo_send"))
async def delete_video_photo_send(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    try:
        await db.delete_video_photo_send()
        await m.reply_text("**Successfully deleted video_photo_send channel_id**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_add_details"))
async def change_add_details(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        detail = await db.get_add_detail()
        return await m.reply_text(f"**reply any text which you want as ADD_DETAILS.**")
        
    try:
        add_detail = m.reply_to_message.text
        await db.change_add_details(str(add_detail))
        await m.reply_text("**Successfully change add_detail data**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("delete_add_details"))
async def delete_add_details(c :Client, m: Message):
    if not m.from_user:
        return await message.reply_text("I don't know about you sar :(")
    try:
        await db.delete_add_details()
        await m.reply_text("**Successfully deleted add_detail data**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_short_each_link"))
async def change_short_each_link(c :Client, m: Message):
    results = await db.check_short_each_link()
    if results:
        result = "False"
    else:
        result = "True"
    btn=[[InlineKeyboardButton("click here", callback_data=f"check_short_each_link_{result}")]]
    await m.reply_text(
        text=f"**your current status for short_each_link is --- {str(results)}\n click below to change status👇👇👇",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True,
        disable_web_page_preview=True
    )


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_how_to_verify"))
async def change_how_to_verify(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    if not m.reply_to_message:
        detail = await db.get_how_to_verify()
        return await m.reply_text(f"**reply any text which you want as HOW_TO_VERIFY.\nyour current HOW_TO_VERIFY is --- {detail}**")
        
    try:
        add_detail = m.reply_to_message.text
        await db.change_how_to_verify(str(add_detail))
        await m.reply_text("**Successfully change HOW_TO_VERIFY data**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")

@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("delete_how_to_verify"))
async def delete_how_to_verify(c :Client, m: Message):
    if not m.from_user:
        return await m.reply_text("I don't know about you sar :(")
    try:
        await db.delete_how_to_verify()
        await m.reply_text("**Successfully deleted HOW_TO_VERIFY data**")
    except Exception as e:
        await m.reply_text(f"somthing went wrong \nerror ---- {str(type(e))} ")


@Bot.on_message(filters.private & filters.user(Config.BOT_OWNER) & filters.command("change_other_user_can_save_file"))
async def change_other_user_can_save_file(c :Client, m: Message):
    results = await db.change_other_user_can_save_file()
    if results:
        result = "False"
    else:
        result = "True"
    btn=[[InlineKeyboardButton("click here", callback_data=f"other_user_can_save_file_{result}")]]
    await m.reply_text(
        text=f"**your current status for other_user_can_save_file status is --- {str(results)}\n click below to change status👇👇👇",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True,
        disable_web_page_preview=True
    )




@Bot.on_callback_query()
async def button(bot: Client, cmd: CallbackQuery):

    cb_data = cmd.data

    if "broadcast_as_copy" in cb_data:
        bool_string = cb_data.rsplit("_",1)[-1]
        await db.change_broadcast_as_copy(bool_string)
        await cmd.message.edit(f"**Now your broadcast_as_copy is {bool_string}**")

    elif "other_user_can_save_file" in cb_data:
        bool_string = cb_data.rsplit("_",1)[-1]
        await db.change_other_user_can_save_file(bool_string)
        await cmd.message.edit(f"**Now your other_user_can_save_file is {bool_string}**")

    elif "check_short_each_link" in cb_data:
        bool_string = cb_data.rsplit("_",1)[-1]
        await db.change_short_each_link(bool_string)
        await cmd.message.edit(f"**Now your short_each_link is {bool_string}**")


    elif "use_pre_shorted_link" in cb_data:
        bool_string = cb_data.rsplit("_",1)[-1]
        await db.change_use_pre_shorted_link(bool_string)
        await cmd.message.edit(f"**Now your use_pre_shorted_link is {bool_string}**")


    elif "verification" in cb_data:
        bool_string = cb_data.rsplit("_",1)[-1]
        await db.change_verification(bool_string)
        await cmd.message.edit(f"**Now your verification is {bool_string}**")

    
    elif "forward_as_copy" in cb_data:
        bool_string = cb_data.rsplit("_",1)[-1]
        await db.change_forward_as_copy(bool_string)
        await cmd.message.edit(f"**Now your forward_as_copy_status is {bool_string}**")


    elif "db_channel" in cb_data:
        db_ch_id = cb_data.rsplit("_",1)[-1]
        await db.update_current_db_channel(db_ch_id)
        await cmd.message.edit(f"**db_channel has changed\nNow your db_channel is {db_ch_id}**")
    
    elif "aboutbot" in cb_data:
        await cmd.message.edit(
            Config.ABOUT_BOT_TEXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Source Codes of Bot",
                                             url="https://github.com/")
                    ],
                    [
                        InlineKeyboardButton("Go Home", callback_data="gotohome"),
                        InlineKeyboardButton("About Dev", callback_data="aboutdevs")
                    ]
                ]
            )
        )

    elif "aboutdevs" in cb_data:
        await cmd.message.edit(
            Config.ABOUT_DEV_TEXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Source Codes of Bot",
                                             url="https://github.com/")
                    ],
                    [
                        InlineKeyboardButton("About Bot", callback_data="aboutbot"),
                        InlineKeyboardButton("Go Home", callback_data="gotohome")
                    ]
                ]
            )
        )

    elif "gotohome" in cb_data:
        await cmd.message.edit(
            Config.HOME_TEXT.format(cmd.message.chat.first_name, cmd.message.chat.id),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Support Group", url="https://t.me/"),
                        InlineKeyboardButton("Bots Channel", url="https://t.me/")
                    ],
                    [
                        InlineKeyboardButton("About Bot", callback_data="aboutbot"),
                        InlineKeyboardButton("About Dev", callback_data="aboutdevs")
                    ]
                ]
            )
        )

    elif "refreshForceSub" in cb_data:
        if Config.UPDATES_CHANNEL:
            if Config.UPDATES_CHANNEL.startswith("-100"):
                channel_chat_id = int(Config.UPDATES_CHANNEL)
            else:
                channel_chat_id = Config.UPDATES_CHANNEL
            try:
                user = await bot.get_chat_member(channel_chat_id, cmd.message.chat.id)
                if user.status == "kicked":
                    await cmd.message.edit(
                        text="Sorry Sir, You are Banned to use me. Contact my Support.",
                        disable_web_page_preview=True
                    )
                    return
            except UserNotParticipant:
                invite_link = await get_invite_link(channel_chat_id)
                await cmd.message.edit(
                    text="**You Still Didn't Join ☹️, Please Join My Updates Channel to use this Bot!**\n\n"
                         "Due to Overload, Only Channel Subscribers can use the Bot!",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton("🤖 Join Updates Channel", url=invite_link.invite_link)
                            ],
                            [
                                InlineKeyboardButton("🔄 Refresh 🔄", callback_data="refreshmeh")
                            ]
                        ]
                    )
                )
                return
            except Exception:
                await cmd.message.edit(
                    text="Something went Wrong. Contact my Support.",
                    disable_web_page_preview=True
                )
                return
        await cmd.message.edit(
            text=Config.HOME_TEXT.format(cmd.message.chat.first_name, cmd.message.chat.id),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Support Group", url="https://t.me/"),
                        InlineKeyboardButton("Bots Channel", url="https://t.me/")
                    ],
                    [
                        InlineKeyboardButton("About Bot", callback_data="aboutbot"),
                        InlineKeyboardButton("About Dev", callback_data="aboutdevs")
                    ]
                ]
            )
        )

    elif cb_data.startswith("ban_user_"):
        user_id = cb_data.split("_", 2)[-1]
        if Config.UPDATES_CHANNEL is None:
            await cmd.answer("Sorry Sir, You didn't Set any Updates Channel!", show_alert=True)
            return
        if not int(cmd.from_user.id) == Config.BOT_OWNER:
            await cmd.answer("You are not allowed to do that!", show_alert=True)
            return
        try:
            await bot.kick_chat_member(chat_id=int(Config.UPDATES_CHANNEL), user_id=int(user_id))
            await cmd.answer("User Banned from Updates Channel!", show_alert=True)
        except Exception as e:
            await cmd.answer(f"Can't Ban Him!\n\nError: {e}", show_alert=True)

    elif "addToBatchTrue" in cb_data:
        if MediaList.get(f"{str(cmd.from_user.id)}", None) is None:
            MediaList[f"{str(cmd.from_user.id)}"] = []
        file_id = cmd.message.reply_to_message.id
        MediaList[f"{str(cmd.from_user.id)}"].append(file_id)
        await cmd.message.edit("File Saved in Batch!\n\n"
                               "Press below button to get batch link.",
                               reply_markup=InlineKeyboardMarkup([
                                   [InlineKeyboardButton("Get Batch Link", callback_data="getBatchLink")],
                                   [InlineKeyboardButton("Close Message", callback_data="closeMessage")]
                               ]))

    elif "addToBatchFalse" in cb_data:
        await save_media_in_channel(bot, editable=cmd.message, message=cmd.message.reply_to_message)

    elif "getBatchLink" in cb_data:
        message_ids = MediaList.get(f"{str(cmd.from_user.id)}", None)
        if message_ids is None:
            await cmd.answer("Batch List Empty!", show_alert=True)
            return
        await cmd.message.edit("Please wait, generating batch link ...")
        await save_batch_media_in_channel(bot=bot, editable=cmd.message, message_ids=message_ids)
        MediaList[f"{str(cmd.from_user.id)}"] = []

    elif "closeMessage" in cb_data:
        await cmd.message.delete(True)

    try:
        await cmd.answer()
    except QueryIdInvalid: pass


Bot.run()
