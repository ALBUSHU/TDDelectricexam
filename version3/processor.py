import logging
from typing import List, Dict, Optional
from model_client import ArkVisionClient
from config import MAX_GROUP_IMAGES

logger = logging.getLogger(__name__)

def split_images_by_size_and_count(b64_list: List[str]) -> List[List[str]]:
    """
    将图片Base64列表分组：
    1. 每组总Base64大小不超过 50MB（安全余量）
    2. 每组图片数不超过 MAX_GROUP_IMAGES
    """
    groups = []
    current_group = []
    current_size = 0
    max_group_bytes = 50 * 1024 * 1024  # 50 MB

    for b64 in b64_list:
        b64_size = len(b64)
        if current_group and current_size + b64_size > max_group_bytes:
            groups.append(current_group)
            current_group = []
            current_size = 0
        current_group.append(b64)
        current_size += b64_size
    if current_group:
        groups.append(current_group)

    # 二次拆分：确保每组不超过 MAX_GROUP_IMAGES 张
    final_groups = []
    for g in groups:
        if len(g) > MAX_GROUP_IMAGES:
            for i in range(0, len(g), MAX_GROUP_IMAGES):
                final_groups.append(g[i:i+MAX_GROUP_IMAGES])
        else:
            final_groups.append(g)
    logger.info(f"图片分组完成，总分片数: {len(final_groups)}")
    return final_groups

def process_images(api_key: str, images_base64: List[str]) -> Optional[Dict]:
    """
    主处理函数：
    - 分组
    - 第一组用主Prompt，后续组用辅Prompt
    - 合并结果返回
    """
    if not images_base64:
        logger.warning("图片列表为空")
        return None

    total_bytes = sum(len(b64) for b64 in images_base64)
    logger.info(f"收到 {len(images_base64)} 张图片，Base64总大小约 {total_bytes/(1024*1024):.1f} MB")

    groups = split_images_by_size_and_count(images_base64)

    client = ArkVisionClient(api_key=api_key)

    all_scores = []
    base_info = {}

    for idx, group in enumerate(groups):
        logger.info(f"处理第 {idx+1} 组，共 {len(group)} 张图片")
        if idx == 0:
            result = client.call_main(group)
            if not result:
                return None
            base_info = result.get("base_info", {})
            scores = result.get("current_item_scores", [])
        else:
            result = client.call_sub(group)
            if not result:
                return None
            scores = result.get("current_item_scores", [])
        all_scores.extend(scores)

    return {
        "base_info": base_info,
        "all_item_scores": all_scores
    }