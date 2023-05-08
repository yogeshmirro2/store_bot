# (c) @AbirHasan2005

import shutil
import aiofiles.os
from configs import Config


async def rm_dir(root: str = f"{Config.DOWNLOAD_DIR}"):
    """
    Delete a Folder.

    :param root: Pass DIR Path
    """

    try:
        shutil.rmtree(root)
        return True
    except Exception as e:
        print(e)
        return False

async def rm_file(file_path: str):
    """
    Delete a File.

    :param file_path: Pass File Path
    """
    try:
        await aiofiles.os.remove(file_path)
        return True
    except Exception as e:
        print(e)
        return False
        
