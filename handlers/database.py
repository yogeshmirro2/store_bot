# (c) @AbirHasan2005
import secrets
import string
import datetime
import motor.motor_asyncio
from configs import Config
import datetime

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.fcol = self.db.database_channel
    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat(),
            verify_key=secrets.choice(Config.VERIFY_KEY) if Config.VERIFY_KEY else ''.join(secrets.choice(string.ascii_letters + string.digits)for i in range(7)),
            verify_date=str(datetime.datetime.today()-datetime.timedelta(days=int(Config.VERIFY_DAYS))) if Config.VERIFY_DAYS else str(datetime.datetime.today()-datetime.timedelta(days=2)),
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason=''
            )
        )
    async def add_bot_db(self):
        bot_db_dict=dict(
            BOT_DB = "BOT_SETTINGS",
            CURRENT_DB_CHANNEL=int(Config.DB_CHANNELS[0]),
            TOTAL_DB_CHANNEL_LIST = Config.DB_CHANNELS,
            UPDATES_CHANNEL = Config.UPDATES_CHANNEL,
            LOG_CHANNEL = Config.LOG_CHANNEL,
            FORWARD_AS_COPY = Config.FORWARD_AS_COPY,
            BROADCAST_AS_COPY = Config.BROADCAST_AS_COPY,
            VERIFICATION = Config.VERIFICATION,
            VERIFY_DAYS = Config.VERIFY_DAYS,
            USE_PRESHORTED_LINK = Config.USE_PRESHORTED_LINK,
            VERIFY_KEY = Config.VERIFY_KEY,
            VERIFY_LINK = Config.VERIFY_LINK,
            SHORTNER_API = Config.SHORTNER_API,
            SHORTNER_API_LINK = Config.SHORTNER_API_LINK,
            VIDEO_PHOTO_SEND = Config.VIDEO_PHOTO_SEND,
            ADD_DETAILS = Config.ADD_DETAILS,
            SHORT_EACH_LINK = Config.SHORT_EACH_LINK,
            HOW_TO_VERIFY = Config.HOW_TO_VERIFY,
            OTHER_USERS_CAN_SAVE_FILE = Config.OTHER_USERS_CAN_SAVE_FILE
        )
        await self.fcol.insert_one(bot_db_dict)

    async def get_total_db_channel_list(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        channels_list = bot_dict.get("TOTAL_DB_CHANNEL_LIST")
        return channels_list

    async def add_db_channels_id(self,channel_id):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        channels_list = bot_dict.get("TOTAL_DB_CHANNEL_LIST")
        channels_list.append(int(channel_id))
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'TOTAL_DB_CHANNEL_LIST': channels_list}})


    async def check_bot_setting_exist(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        return True if bot_dict else False


    async def get_current_db_channel_id(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        return bot_dict.get("CURRENT_DB_CHANNEL")

    async def update_current_db_channel(self,channel_id):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"}, {'$set': {'CURRENT_DB_CHANNEL': int(channel_id)}})


    async def delete_db_channel_id(self,channel_id):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        channels_list = bot_dict.get("TOTAL_DB_CHANNEL_LIST")
        if int(channel_id) in channels_list:
            channels_list.remove(int(channel_id))
            await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'TOTAL_DB_CHANNEL_LIST': channels_list}})
            return True
        else:
            return False

    async def add_update_channel_id(self,channel_id):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'UPDATES_CHANNEL': int(channel_id)}})


    async def check_update_channel_id(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        channel_id = bot_dict.get("UPDATES_CHANNEL")
        return channel_id



    async def delete_update_channel_id(self):
        check = await db.check_update_channel_id()
        if check is not None:
            await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'UPDATES_CHANNEL': None}})
            return True
        else:
            return False


    async def change_log_channel_id(self,channel_id):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'LOG_CHANNEL': channel_id}})

    async def check_log_channel_id(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        status = bot_dict.get("LOG_CHANNEL")
        return status

    async def delete_log_channel_id(self):
        checking = await db.check_log_channel_id()
        if checking is not None:
            await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'LOG_CHANNEL': None}})
            return True
        else:
            False

    async def change_other_user_can_save_file(self,bool_string):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'OTHER_USERS_CAN_SAVE_FILE': eval(bool_string)}})


    async def change_forward_as_copy(self,bool_string):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'FORWARD_AS_COPY': eval(bool_string)}})

    async def check_forward_as_copy_status(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        status = bot_dict.get("FORWARD_AS_COPY")
        return status


    async def change_broadcast_as_copy(self,bool_string):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'BROADCAST_AS_COPY': eval(bool_string)}})

    async def check_broadcast_as_copy_status(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        status = bot_dict.get("BROADCAST_AS_COPY")
        return status

    async def change_verification(self,bool_string):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'VERIFICATION': eval(bool_string)}})



    async def check_verification_status(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        verifaction_stats = bot_dict.get("VERIFICATION")
        return verifaction_stats

    async def get_verify_days(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        return bot_dict.get("VERIFY_DAYS")

    async def delete_verify_days(self):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'VERIFY_DAYS': None}})


    async def change_verify_days(self,day):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'VERIFY_DAYS': int(day)}})

    async def change_use_pre_shorted_link(self,bool_string):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'USE_PRESHORTED_LINK': eval(bool_string)}})

    async def use_pre_shorted_link_status(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        status = bot_dict.get(USE_PRESHORTED_LINK)
        return status

    async def change_verify_key_link(self,verify_key_string,verify_link_string):
        verify_key_list = verify_key_string.split()
        verify_link_list = verify_link_string.split()
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'VERIFY_LINK': verify_link_list}})
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'VERIFY_KEY': verify_key_list}})

    async def delete_verify_key_link(self):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'VERIFY_LINK': []}})
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'VERIFY_LINK': []}})

    async def get_verify_key_link_list(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        verify_key_list = bot_dict.get("VERIFY_KEY")
        verify_link_list = bot_dict.get("VERIFY_LINK")
        return verify_key_list,verify_link_list


    async def change_shortner_api_link(self,shortner_api_string,shortner_api_link_string):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'SHORTNER_API': shortner_api_string}})
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'SHORTNER_API_LINK': shortner_api_link_string}})

    async def check_shortner_exist(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        shortner_api = bot_dict.get("SHORTNER_API")
        shortner_api_link = bot_dict.get("SHORTNER_API_LINK")
        return True if shortner_api & shortner_api_link is not None else False

    async def get_shortner_api_link(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        shortner_api = bot_dict.get("SHORTNER_API")
        shortner_api_link = bot_dict.get("SHORTNER_API_LINK")
        return shortner_api,shortner_api_link

    async def delete_shortner_api_link(self):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'SHORTNER_API': None}})
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'SHORTNER_API_LINK': None}})

    async def change_video_photo_send(self,channel_id):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'VIDEO_PHOTO_SEND': int(channel_id)}})

    async def check_video_photo_send(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        status = bot_dict.get("VIDEO_PHOTO_SEND")
        return status


    async def delete_video_photo_send(self):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'VIDEO_PHOTO_SEND': None}})

    async def change_add_details(self,string):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'ADD_DETAILS': str(string)}})

    async def get_add_detail(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        detail = bot_dict.get("ADD_DETAILS")
        return detail

    async def delete_add_details(self):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'ADD_DETAILS': ""}})


    async def change_short_each_link(self,bool_string):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'SHORT_EACH_LINK': eval(bool_string)}})


    async def check_short_each_link(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        status = bot_dict.get("SHORT_EACH_LINK")
        return status

    async def get_how_to_verify(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        text = bot_dict.get("HOW_TO_VERIFY")
        return text

    async def change_how_to_verify(self,string):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'HOW_TO_VERIFY': string}})

    async def delete_how_to_verify(self):
        await self.fcol.update_one({"BOT_DB":"BOT_SETTINGS"},{'$set': {'HOW_TO_VERIFY': ""}})

    
    async def get_verify_date(self,id):
        user = await self.col.find_one({'id': int(id)})
        datetime_formate = user.get("verify_date")
        return datetime.datetime.strptime(datetime_formate, '%Y-%m-%d %H:%M:%S.%f')

    async def update_verify_date(self,id):
        user = await self.col.find_one({'id': int(id)})
        day = await get_verify_days()
        await self.col.update_one({'id': id}, {'$set': {'verify_date': str(datetime.datetime.today()+datetime.timedelta(days=int(day)))}})

    async def check_verify_list_exist(self):
        bot_dict = await self.fcol.find_one({"BOT_DB":"BOT_SETTINGS"})
        verify_key_list = bot_dict.get("VERIFY_KEY")
        verify_link_list = bot_dict.get("VERIFY_LINK")
        return True if len(verify_key_list) & len(verify_link_list)!=0 else False


    async def get_verify_key(self,id):
        user = await self.col.find_one({'id': int(id)})
        key = user.get("verify_key")
        if await db.check_verify_list_exist():
            verify_key_list,verify_link_list = await get_verify_key_link_list()
            if key not in verify_key_list:
                await update_verify_key(id)
                key = user.get("verify_key")
        return key

    async def update_verify_key(self,id):
        user = await self.col.find_one({'id': int(id)})
        if await db.check_verify_list_exist():
            verify_key_list,verify_link_list = await get_verify_key_link_list()
            key = secrets.choice(verify_key_list)
            await self.col.update_one({'id': id}, {'$set': {'verify_key': key}})
        else:
            key = ''.join(secrets.choice(string.ascii_letters + string.digits)for i in range(7))
            await self.col.update_one({'id': id}, {'$set': {'verify_key': key}})

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, user_id, ban_duration, ban_reason):
        ban_status = dict(
            is_banned=True,
            ban_duration=ban_duration,
            banned_on=datetime.date.today().isoformat(),
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason=''
        )
        user = await self.col.find_one({'id': int(id)})
        return user.get('ban_status', default)

    async def get_all_banned_users(self):
        banned_users = self.col.find({'ban_status.is_banned': True})
        return banned_users


db = Database(Config.DATABASE_URL, Config.BOT_USERNAME)
