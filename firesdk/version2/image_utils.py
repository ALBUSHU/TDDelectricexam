import base64
#from flask import FileStorage
from werkzeug.datastructures import FileStorage
from config import SUPPORT_IMAGE_FORMATS, MAX_IMAGE_SIZE

def check_image_valid(file: FileStorage) -> bool:
    """校验单张图片格式、大小是否合法"""
    # 校验文件后缀
    if not file.filename or "." not in file.filename:
        return False
    suffix = file.filename.split(".")[-1].lower()
    if suffix not in SUPPORT_IMAGE_FORMATS:
        return False
    # 校验文件大小
    file.seek(0)
    if len(file.read()) > MAX_IMAGE_SIZE:
        return False
    file.seek(0)
    return True

def image_to_base64(file: FileStorage) -> str:
    """将本地图片转为火山方舟标准Base64格式"""
    try:
        file.seek(0)
        file_bytes = file.read()
        return base64.b64encode(file_bytes).decode("utf-8")
    except Exception:
        return ""