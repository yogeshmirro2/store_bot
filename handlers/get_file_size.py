from pyrogram.types import Message


async def get_file_size(msg:Message):
    if msg.video:
        size = msg.video.file_size
    elif msg.document:
        size = msg.document.file_size
    elif msg.audio:
        size = msg.audio.file_size
    else:
        size = None
    if size is not None:
        if size < 1024:
            file_size = f"[{size} B]"
        elif size < (1024**2):
            file_size = f"[{str(round(size/1024, 2))} KiB] "
        elif size < (1024**3):
            file_size = f"[{str(round(size/(1024**2), 2))} MiB] "
        elif size < (1024**4):
            file_size = f"[{str(round(size/(1024**3), 2))} GiB] "
    else:
        file_size = ""
    return file_size
