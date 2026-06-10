import json
import logging
import time
from typing import List, Dict, Optional
from volcenginesdkarkruntime import Ark
from config import ARK_ENDPOINT_URL, VISION_MODEL_ID
from constants import MAIN_PROMPT, SUB_PROMPT
from image_utils import get_mime_type_from_base64

logger = logging.getLogger(__name__)

class ArkVisionClient:
    """火山方舟视觉模型客户端（单次调用）"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_id = VISION_MODEL_ID
        self.client = Ark(
            base_url=ARK_ENDPOINT_URL,
            api_key=self.api_key,
            timeout=180,
            max_retries=0
        )
        logger.info("火山方舟客户端实例化完成")

    def _build_image_content(self, b64_str: str, mime_type: str = "image/jpeg") -> dict:
        return {
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{b64_str}"}
        }

    def _clean_json_response(self, raw_text: str) -> str:
        raw_text = raw_text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return raw_text.strip()

    def _call_with_prompt(self, group_imgs: List[str], prompt: str, prompt_name: str) -> Optional[Dict]:
        content = []
        for b64 in group_imgs:
            mime = get_mime_type_from_base64(b64)
            content.append(self._build_image_content(b64, mime))
        content.append({"type": "text", "text": prompt})

        start_time = time.time()
        try:
            resp = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": content}],
                temperature=0.1
            )
            elapsed = time.time() - start_time
            logger.info(f"{prompt_name} 调用成功，耗时 {elapsed:.2f} 秒")
            raw_text = resp.choices[0].message.content.strip()
            cleaned = self._clean_json_response(raw_text)
            return json.loads(cleaned)
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"{prompt_name} 调用失败 (耗时 {elapsed:.2f} 秒): {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"响应状态码: {e.response.status_code}, 内容: {e.response.text}")
            return None

    def call_main(self, images: List[str]) -> Optional[Dict]:
        """调用主Prompt（提取基础信息 + 当前题目得分）"""
        return self._call_with_prompt(images, MAIN_PROMPT, "主Prompt")

    def call_sub(self, images: List[str]) -> Optional[Dict]:
        """调用辅Prompt（仅提取当前题目得分）"""
        return self._call_with_prompt(images, SUB_PROMPT, "辅Prompt")