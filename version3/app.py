import json
import logging
from flask import Flask, request
from config import MAX_IMAGE_SIZE
from constants import standard_response, CODE_SUCCESS, CODE_PARAM_ERROR, CODE_IMAGE_ERROR, CODE_SERVICE_ERROR
from image_utils import validate_base64_image
from processor import process_images

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@app.route("/api/extract", methods=["POST"])
def extract_info():
    """
    请求格式 JSON:
    {
        "api_key": "your-api-key",
        "images_base64": ["base64_str1", "base64_str2", ...]
    }
    返回结构化结果
    """
    if not request.is_json:
        return json.dumps(
            standard_response(CODE_PARAM_ERROR, "请求 Content-Type 必须为 application/json"),
            ensure_ascii=False
        ), 400

    data = request.get_json()
    if not data:
        return json.dumps(
            standard_response(CODE_PARAM_ERROR, "请求体不能为空"),
            ensure_ascii=False
        ), 400

    api_key = data.get("api_key", "").strip()
    images_base64 = data.get("images_base64", [])

    if not api_key:
        return json.dumps(
            standard_response(CODE_PARAM_ERROR, "缺少必填参数: api_key"),
            ensure_ascii=False
        ), 400

    if not images_base64 or not isinstance(images_base64, list):
        return json.dumps(
            standard_response(CODE_PARAM_ERROR, "参数 images_base64 必须为非空数组"),
            ensure_ascii=False
        ), 400

    # 校验每张图片
    valid_b64_list = []
    for idx, b64_str in enumerate(images_base64):
        if not isinstance(b64_str, str) or not b64_str:
            return json.dumps(
                standard_response(CODE_IMAGE_ERROR, f"第 {idx+1} 张图片的 Base64 字符串无效"),
                ensure_ascii=False
            ), 400
        if not validate_base64_image(b64_str):
            return json.dumps(
                standard_response(CODE_IMAGE_ERROR, f"第 {idx+1} 张图片不合法（格式或大小超出 {MAX_IMAGE_SIZE//(1024*1024)}MB）"),
                ensure_ascii=False
            ), 400
        valid_b64_list.append(b64_str)

    logger.info(f"接收并校验通过 {len(valid_b64_list)} 张图片")

    try:
        result = process_images(api_key, valid_b64_list)
        if not result:
            return json.dumps(
                standard_response(CODE_SERVICE_ERROR, "模型服务调用失败，请检查 api_key 或网络"),
                ensure_ascii=False
            ), 500
    except Exception as e:
        logger.error(f"处理异常: {e}", exc_info=True)
        return json.dumps(
            standard_response(CODE_SERVICE_ERROR, f"服务内部异常: {str(e)}"),
            ensure_ascii=False
        ), 500

    resp_data = {
        "total_image_count": len(valid_b64_list),
        "base_info": result["base_info"],
        "all_item_scores": result["all_item_scores"]
    }
    return json.dumps(
        standard_response(CODE_SUCCESS, "提取成功", resp_data),
        ensure_ascii=False
    ), 200

@app.route("/health", methods=["GET"])
def health_check():
    return json.dumps(
        standard_response(CODE_SUCCESS, "服务运行正常"),
        ensure_ascii=False
    ), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)