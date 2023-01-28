from config import file_save_path
from uuid import uuid4
from fastapi import UploadFile
from os import path
import aiofiles

async def save_file(file: UploadFile):
    file_uuid = uuid4().hex
    _, extension = path.splitext(file.filename)
    file_name = f'{file_uuid}{extension}'
    file_path = path.abspath(f"{file_save_path}/{file_name}")
    async with aiofiles.open(file_path, mode='wb') as buffer:
        content = await file.read()
        await buffer.write(content)
    return file_name
