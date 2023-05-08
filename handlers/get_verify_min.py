import datetime

async def get_diff_min(user_datetime):
    diff_sec = (user_datetime-datetime.datetime.today()).total_seconds()
    diff_min = diff_sec//60
    return diff_min