import base64
import imghdr
import io
from PIL import Image
from config import SUPPORT_IMAGE_FORMATS, MAX_IMAGE_SIZE

def validate_base64_image(b64_str: str) -> bool:
    """校验Base64图片是否合法（大小、格式）"""
    try:
        img_data = base64.b64decode(b64_str)
        if len(img_data) > MAX_IMAGE_SIZE:
            return False
        # 校验图片格式
        with io.BytesIO(img_data) as buf:
            img_format = imghdr.what(buf)
            if img_format is None:
                # 尝试用PIL打开
                try:
                    Image.open(io.BytesIO(img_data))
                except Exception:
                    return False
            else:
                if img_format not in SUPPORT_IMAGE_FORMATS:
                    return False
        return True
    except Exception:
        return False

def get_mime_type_from_base64(b64_str: str) -> str:
    """根据Base64数据推断MIME类型"""
    try:
        img_data = base64.b64decode(b64_str)
        with io.BytesIO(img_data) as buf:
            img_format = imghdr.what(buf)
            if img_format == 'jpeg':
                return 'image/jpeg'
            elif img_format == 'png':
                return 'image/png'
            elif img_format == 'bmp':
                return 'image/bmp'
            elif img_format == 'webp':
                return 'image/webp'
            else:
                return 'image/jpeg'
    except Exception:
        return 'image/jpeg'