import os

# ==================== 火山方舟核心配置 ====================
# 优先环境变量，无则手动填写
ARK_ENDPOINT_URL = "https://ark.cn-beijing.volces.com/api/v3"
VISION_MODEL_ID = "doubao-seed-1-6-vision-250815"

# ==================== 本地Web服务配置 ====================
HOST = "0.0.0.0"
PORT = 8080
DEBUG = False

# ==================== 业务核心规则配置 ====================
# 模型单组最大图片数（服务内部分片阈值，硬性8张）
MAX_GROUP_IMAGES = 8
# 单张图片限制（遵循火山方舟官方规则）
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 单张最大10MB
SUPPORT_IMAGE_FORMATS = ["jpg", "jpeg", "png", "bmp", "webp"]