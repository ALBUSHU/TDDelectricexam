import json
import logging
import time
from typing import List, Dict, Optional
from volcenginesdkarkruntime import Ark
from config import ARK_API_KEY, VISION_MODEL_ID, MAX_GROUP_IMAGES, ARK_ENDPOINT_URL
from constants import MAIN_PROMPT, SUB_PROMPT

logger = logging.getLogger(__name__)

class ArkVisionClient:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.init_client()
        return cls._instance

    def init_client(self):
        try:
            # 增加超时到 180 秒（3 分钟），足够处理大图片
            self.client = Ark(
                base_url=ARK_ENDPOINT_URL,
                api_key=ARK_API_KEY,
                timeout=180,
                max_retries=0   # 关闭自动重试，避免重复计费
            )
            self.model_id = VISION_MODEL_ID
            logger.info("火山方舟客户端初始化完成 (timeout=180s, retries=0)")
        except Exception as e:
            logger.error(f"客户端初始化失败: {str(e)}")
            raise RuntimeError("火山方舟客户端初始化异常")

    def split_images_group(self, img_base64_list: List[str]) -> List[List[str]]:
        groups = []
        # 确保每组总 Base64 大小不超过 50 MB（安全余量）
        current_group = []
        current_size = 0
        max_group_bytes = 50 * 1024 * 1024  # 50 MB
        for b64 in img_base64_list:
            b64_size = len(b64)
            if current_group and current_size + b64_size > max_group_bytes:
                groups.append(current_group)
                current_group = []
                current_size = 0
            current_group.append(b64)
            current_size += b64_size
        if current_group:
            groups.append(current_group)

        # 如果仍然超出最大图片数限制，强制截断（但应该不会发生）
        final_groups = []
        for g in groups:
            if len(g) > MAX_GROUP_IMAGES:
                # 拆分成多组
                for i in range(0, len(g), MAX_GROUP_IMAGES):
                    final_groups.append(g[i:i+MAX_GROUP_IMAGES])
            else:
                final_groups.append(g)
        logger.info(f"图片动态分片完成，总分片数：{len(final_groups)}")
        return final_groups

    def _build_image_content(self, b64_str: str, mime_type: str = "image/jpeg") -> dict:
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{b64_str}"
            }
        }

    def _clean_json_response(self, raw_text: str) -> str:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return raw_text.strip()

    def _call_with_prompt(self, group_imgs: List[str], prompt: str, prompt_type: str) -> Optional[Dict]:
        content = []
        for b64 in group_imgs:
            content.append(self._build_image_content(b64))
        content.append({"type": "text", "text": prompt})

        start_time = time.time()
        try:
            resp = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": content}],
                temperature=0.1
            )
            elapsed = time.time() - start_time
            logger.info(f"{prompt_type} 调用成功，耗时 {elapsed:.2f} 秒")
            raw_text = resp.choices[0].message.content.strip()
            cleaned = self._clean_json_response(raw_text)
            return json.loads(cleaned)
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{prompt_type} 调用失败 (耗时 {elapsed:.2f} 秒): {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"响应状态码: {e.response.status_code}, 内容: {e.response.text}")
            return None

    def _call_main_prompt(self, group_imgs: List[str]) -> Optional[Dict]:
        return self._call_with_prompt(group_imgs, MAIN_PROMPT, "主Prompt")

    def _call_sub_prompt(self, group_imgs: List[str]) -> Optional[Dict]:
        return self._call_with_prompt(group_imgs, SUB_PROMPT, "辅Prompt")

    def batch_extract(self, all_img_base64: List[str]) -> Optional[Dict]:
        if not all_img_base64:
            logger.warning("图片列表为空")
            return None

        total_start = time.time()
        # 预估总大小日志
        total_bytes = sum(len(b64) for b64 in all_img_base64)
        logger.info(f"收到 {len(all_img_base64)} 张图片，Base64 总大小约 {total_bytes/(1024*1024):.1f} MB")

        img_groups = self.split_images_group(all_img_base64)
        total_scores = []
        base_info = {}

        for idx, group in enumerate(img_groups):
            logger.info(f"开始处理第 {idx+1} 组图片（{len(group)}张）")
            if idx == 0:
                group_result = self._call_main_prompt(group)
                if not group_result:
                    return None
                base_info = group_result.get("base_info", {})
                current_scores = group_result.get("current_item_scores", [])
                total_scores.extend(current_scores)
            else:
                group_result = self._call_sub_prompt(group)
                if not group_result:
                    return None
                current_scores = group_result.get("current_item_scores", [])
                total_scores.extend(current_scores)

        total_elapsed = time.time() - total_start
        logger.info(f"所有分片处理完成，总耗时 {total_elapsed:.2f} 秒，共提取 {len(total_scores)} 个题目得分")
        return {
            "base_info": base_info,
            "all_item_scores": total_scores
        }

ark_client = ArkVisionClient()