import json
import logging
from flask import Flask, request
from config import REQUEST_TYPE_LIST
from constants import *
from image_utils import check_image_valid, image_to_base64
from model_client import ark_client
from constants import standard_response, CODE_SUCCESS, CODE_PARAM_ERROR, CODE_IMAGE_ERROR, CODE_SERVICE_ERROR

# 初始化Flask
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@app.route("/api/extract", methods=["POST"])
def extract_info():
    """
    核心对外接口
    请求方式：POST form-data
    参数：
      req_type: type1 / type2 （必填，仅标记用途）
      images: 本地图片文件（数量无限制）
    返回：统一结构化JSON
    """
    # 1. 解析基础参数
    req_type = request.form.get("req_type", "").strip()
    image_files = request.files.getlist("images")

    # 2. 基础参数校验
    if not req_type or not image_files:
        return json.dumps(
            standard_response(CODE_PARAM_ERROR, "参数缺失：req_type 和 images 为必填项"),
            ensure_ascii=False
        ), 400

    if req_type not in REQUEST_TYPE_LIST:
        return json.dumps(
            standard_response(CODE_PARAM_ERROR, f"请求类型仅支持：{REQUEST_TYPE_LIST}"),
            ensure_ascii=False
        ), 400

    # 3. 遍历校验单张图片 + 转Base64
    base64_list = []
    for file in image_files:
        if not check_image_valid(file):
            return json.dumps(
                standard_response(CODE_IMAGE_ERROR, f"图片 {file.filename} 格式/大小不合法"),
                ensure_ascii=False
            ), 400
        b64_str = image_to_base64(file)
        if not b64_str:
            return json.dumps(
                standard_response(CODE_IMAGE_ERROR, f"图片 {file.filename} 编码失败"),
                ensure_ascii=False
            ), 400
        base64_list.append(b64_str)

    logger.info(f"客户端上传图片总数：{len(base64_list)}")

    # 4. 调用模型批量提取（内部自动分片+多调用+合并）
    full_result = ark_client.batch_extract(base64_list)
    if not full_result:
        return json.dumps(
            standard_response(CODE_SERVICE_ERROR, "模型服务调用失败，请查看控制台日志"),
            ensure_ascii=False
        ), 500

    # 5. 组装最终对外返回数据
    resp_data = {
        "req_type": req_type,
        "total_image_count": len(image_files),
        "base_info": full_result["base_info"],
        "all_item_scores": full_result["all_item_scores"]
    }

    return json.dumps(
        standard_response(CODE_SUCCESS, "提取成功", resp_data),
        ensure_ascii=False
    ), 200

@app.route("/health", methods=["GET"])
def health_check():
    """健康检查接口"""
    return json.dumps(
        standard_response(CODE_SUCCESS, "服务运行正常"),
        ensure_ascii=False
    ), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)