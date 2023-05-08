# (c) @AbirHasan2005

import os


class Config(object):
    API_ID = int(os.environ.get("API_ID",18860540))
    API_HASH = os.environ.get("API_HASH","22dd2ad1706199438ab3474e85c9afab")
    BOT_TOKEN = os.environ.get("BOT_TOKEN","6252647993:AAFVnqF_YcyPCksB2gUBL0K4BFek71HvxlY")
    BOT_USERNAME = os.environ.get("BOT_USERNAME","DC4_01Robot")
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "./downloads")
    DB_CHANNELS = list(int(x) for x in os.environ.get("DB_CHANNELS","-1001949245822").split())# multiple channel id must be separated by space
    LOG_CHANNEL = os.environ.get("LOG_CHANNEL","-1001949245822")
    UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL",None)
    BOT_OWNER = int(os.environ.get("BOT_OWNER","5360919559"))
    BOT_ADMINS = list(int(x) for x in os.environ.get("BOT_ADMINS","12 34").split())
    BOT_ADMINS.append(BOT_OWNER)
    OTHER_USERS_CAN_SAVE_FILE = os.environ.get("OTHER_USERS_CAN_SAVE_FILE",False)
    DATABASE_URL = os.environ.get("DATABASE_URL","mongodb+srv://ankur560s:ankur560@cluster00.nlwm8ya.mongodb.net/?retryWrites=true&w=majority")
    BANNED_USERS = set(int(x) for x in os.environ.get("BANNED_USERS", "1234567890").split())
    FORWARD_AS_COPY = os.environ.get("FORWARD_AS_COPY", True)
    BROADCAST_AS_COPY = os.environ.get("BROADCAST_AS_COPY", False)
    BANNED_CHAT_IDS = list(set(int(x) for x in os.environ.get("BANNED_CHAT_IDS", "-100136269 -100195497").split()))
    VERIFY_KEY = os.environ.get("VERIFY_KEY","").split()#multiple VERIFY_KEY separated by space.if VERIFICATION and USE_PRESHORTED_LINK is True then VERIFY_LINK and VERIFY_KEY must be fill.which VERIFY_LINK & VERIFY_KEY related to each other must be same index in both VERIFY_LINK and VERIFY_KEY var like --- "hhjdjdj" this key is ralated to https://www.shorted_link.com then if "hhjdjdj" key is at index 1 then https://www.shorted_link.com must also be at index 1 
    VERIFY_LINK = os.environ.get("VERIFY_LINK","").split()#multiple VERIFY_LINK separated by space.https://t.me/(your bot username without @)?start=verify_(your key which you fill in VERIFY_KEY Var)  ---- this is example of verify link,short this verify link by link shortner and get shorted link this shorted link fill here VERIFY_LINK var.for one verify key one shorted link.verify key and related shorted link must be at same index in their respective var as mention above in VERIFY_KEY
    VERIFICATION = os.environ.get("VERIFICATION",False)
    VERIFY_DAYS = os.environ.get("VERIFY_DAYS",None)
    USE_PRESHORTED_LINK = os.environ.get("USE_PRESHORTED_LINK",False)
    HOW_TO_VERIFY = os.environ.get("HOW_TO_VERIFY","")#if you want give a short instruction to user that how they can complete their VERIFICATION then add here that text
    SHORTNER_API_LINK = os.environ.get("SHORTNER_API_LINK",None)#if VERIFICATION os True and USE_PRESHORTED_LINK is not true then SHORTNER_API and SHORTNER_API_LINK var must be fill
    SHORTNER_API = os.environ.get("SHORTNER_API",None)
    VIDEO_PHOTO_SEND = os.environ.get("VIDEO_PHOTO_SEND",None)#if you want to extarct video thumbnail with caption and bot share link then fill channel id
    ADD_DETAILS = os.environ.get("ADD_DETAILS","")#if you want add some extra text in bottom of VIDEO_PHOTO_SEND then add here that text
    SHORT_EACH_LINK = os.environ.get("SHORT_EACH_LINK",False)#if you want to short each share link with link shortner then set it True and fill both SHORTNER_API_LINK,SHORTNER_API var
    ABOUT_BOT_TEXT = f"""
This is Permanent Files Store Bot!
Send me any file I will save it in my Database. Also works for channel. Add me to channel as Admin with Edit Permission, I will add Save Uploaded File in Channel & add Sharable Button Link.

🤖 **My Name:** [Files Store Bot](https://t.me/{BOT_USERNAME})

📝 **Language:** [Python3](https://www.python.org)

📚 **Library:** [Pyrogram](https://docs.pyrogram.org)

"""
    ABOUT_DEV_TEXT = f"""
🧑🏻‍💻 Developer is Unknown🚫😂
"""
    HOME_TEXT = """
Hi, [{}](tg://user?id={})\n\nThis is Permanent **File Store Bot**.

Send me any file I will give you a permanent Sharable Link.
"""
