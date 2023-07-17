async def get_file_size(size:int):
    if size < 1024:
        file_size = f"[{size} B]"
    elif size < (1024**2):
        file_size = f"[{str(round(size/1024, 2))} KiB] "
    elif size < (1024**3):
        file_size = f"[{str(round(size/(1024**2), 2))} MiB] "
    elif size < (1024**4):
        file_size = f"[{str(round(size/(1024**3), 2))} GiB] "
    return file_size
